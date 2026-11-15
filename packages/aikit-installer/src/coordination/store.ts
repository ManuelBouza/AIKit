import * as fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { replaceWindows, type ReplaceRunner } from '../windows-replace.js';
import {
  canonical,
  document,
  ensure,
  markdown,
  notice,
  project,
  sha,
  strictJson,
  task,
  taskId,
  uuid,
  type Notice,
  type Project,
  type Query,
  type Task,
} from './schema.js';
import { decide } from './state.js';

type Kind = 'activar-proyecto' | 'crear-tarea' | 'aviso' | 'derivado';
class KnownRejection extends Error {}
type Manifest = {
  schemaVersion: 1;
  operationId: string;
  kind: Kind;
  projectId: string;
  taskId: string | null;
  coordinatorChatId: string;
  expectedOwnerEpoch: number | null;
  target: string;
  baseGeneration: number | null;
  proposedGeneration: number;
  baseSha256: string | null;
  proposedSha256: string;
  notice: Notice | null;
  reason: string;
  createdAt: string;
};
export type Phase =
  | 'operation-directory'
  | 'base'
  | 'proposal'
  | 'manifest'
  | 'ready'
  | 'temporary'
  | 'published'
  | 'verified'
  | 'completed';
export type Permissions = { inspect(file: string): string; verifyRoot(root: string): void };
export type StoreOptions = {
  root: string;
  projectId: string;
  coordinatorChatId: string;
  ownerEpoch: number;
  permissions?: Permissions;
  replaceRunner?: ReplaceRunner;
  platform?: NodeJS.Platform;
  fault?: (phase: Phase) => void;
};

function acl(file: string, verify = false): string {
  const systemRoot = process.env.SystemRoot;
  ensure(systemRoot && path.isAbsolute(systemRoot), 'SystemRoot no verificable');
  const script = `$ErrorActionPreference='Stop'
if ([IO.Directory]::Exists($env:AIKIT_ACL_PATH)) { $acl = [IO.Directory]::GetAccessControl($env:AIKIT_ACL_PATH) }
else { $acl = [IO.File]::GetAccessControl($env:AIKIT_ACL_PATH) }
if ($env:AIKIT_ACL_VERIFY -eq 'yes') {
  $allowed = @([Security.Principal.WindowsIdentity]::GetCurrent().User.Value, 'S-1-5-18', 'S-1-5-32-544')
  if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -notin $allowed) { throw 'Propietario no admitido' }
  $mask = [int]([Security.AccessControl.FileSystemRights]::Write -bor [Security.AccessControl.FileSystemRights]::Delete -bor [Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor [Security.AccessControl.FileSystemRights]::ChangePermissions -bor [Security.AccessControl.FileSystemRights]::TakeOwnership)
  $rules = $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])
  if ($rules.Count -eq 0) { throw 'DACL vacía o no verificable' }
  foreach ($rule in $rules) {
    if ($rule.AccessControlType -eq 'Allow' -and (([int]$rule.FileSystemRights -band $mask) -ne 0) -and $rule.IdentityReference.Value -notin $allowed) { throw 'Escritura por otro principal' }
  }
}
$sections = [Security.AccessControl.AccessControlSections]::Access -bor [Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group
$acl.GetSecurityDescriptorSddlForm($sections)`;
  const result = spawnSync(
    path.join(systemRoot, 'System32/WindowsPowerShell/v1.0/powershell.exe'),
    [
      '-NoProfile',
      '-NonInteractive',
      '-EncodedCommand',
      Buffer.from(script, 'utf16le').toString('base64'),
    ],
    {
      env: { ...process.env, AIKIT_ACL_PATH: file, AIKIT_ACL_VERIFY: verify ? 'yes' : 'no' },
      encoding: 'utf8',
      windowsHide: true,
      timeout: 15000,
    },
  );
  ensure(
    result.status === 0 && !result.error && result.stdout.trim(),
    'ACL no verificable: ' + (result.error?.message ?? result.stderr.trim()),
  );
  return result.stdout.trim();
}
export const nativePermissions: Permissions = {
  inspect(file) {
    return process.platform === 'win32' ? acl(file) : String(fs.statSync(file).mode & 0o777);
  },
  verifyRoot(root) {
    if (process.platform === 'win32') {
      const sddl = acl(root, true);
      ensure(sddl.includes('D:'), 'DACL no verificable');
    } else ensure((fs.statSync(root).mode & 0o077) === 0, 'Raíz debe tener permisos 0700');
  },
};

function exists(file: string): boolean {
  try {
    fs.lstatSync(file);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return false;
    throw error;
  }
}
function equal(a: Buffer | null, b: Buffer | null): boolean {
  return a === null || b === null ? a === b : a.equals(b);
}
function object(value: unknown): Record<string, unknown> {
  ensure(
    value !== null && typeof value === 'object' && !Array.isArray(value),
    'Objeto de diario requerido',
  );
  return value as Record<string, unknown>;
}
function keys(value: Record<string, unknown>, expected: string[]) {
  ensure(
    Object.keys(value).length === expected.length && expected.every((k) => Object.hasOwn(value, k)),
    'Campos de diario inválidos',
  );
}
function integer(value: unknown) {
  ensure(
    typeof value === 'number' && Number.isSafeInteger(value) && value > 0,
    'Generación inválida',
  );
}
function hash(value: unknown) {
  ensure(typeof value === 'string' && /^[a-f0-9]{64}$/.test(value), 'Hash inválido');
}
function timestamp(value: unknown) {
  ensure(typeof value === 'string' && new Date(value).toISOString() === value, 'Fecha inválida');
}

/** Un store explícito; no infiere proyecto ni recupera bloqueos abandonados. */
export class CoordinationStore {
  readonly root: string;
  private readonly control: string;
  private readonly operations: string;
  private readonly lock: string;
  private readonly permissions: Permissions;
  constructor(private readonly options: StoreOptions) {
    ensure(Number(process.versions.node.split('.')[0]) >= 24, 'El auxiliar requiere Node 24');
    ensure(path.isAbsolute(options.root), 'Raíz absoluta requerida');
    uuid(options.projectId);
    ensure(options.coordinatorChatId.trim(), 'Coordinador requerido');
    ensure(options.ownerEpoch === 1, 'Relevo no implementado');
    this.root = path.resolve(options.root);
    this.check(this.root);
    ensure(fs.statSync(this.root).isDirectory(), 'Raíz debe existir');
    this.permissions = options.permissions ?? nativePermissions;
    this.permissions.verifyRoot(this.root);
    this.control = path.join(this.root, 'coordinacion', '.control');
    this.operations = path.join(this.control, 'operaciones');
    this.lock = path.join(this.control, 'escritura.lock');
  }
  private check(file: string) {
    const parsed = path.parse(file);
    let current = parsed.root;
    for (const part of file.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
      current = path.join(current, part);
      if (exists(current)) {
        const stat = fs.lstatSync(current);
        ensure(!stat.isSymbolicLink(), 'Enlaces o junctions no admitidos');
        const resolved = path.resolve(fs.realpathSync.native(current));
        ensure(
          process.platform === 'win32'
            ? resolved.toLowerCase() === path.resolve(current).toLowerCase()
            : resolved === path.resolve(current),
          'Ruta redirigida',
        );
      }
    }
  }
  private inside(relative: string): string {
    const absolute = path.resolve(this.root, relative);
    ensure(absolute.startsWith(this.root + path.sep), 'Escape de raíz');
    this.check(absolute);
    return absolute;
  }
  private mkdir(file: string) {
    this.check(file);
    fs.mkdirSync(file, { recursive: true, mode: 0o700 });
    this.check(file);
    this.permissions.verifyRoot(file);
  }
  private read(file: string): Buffer | null {
    this.check(file);
    return exists(file) ? fs.readFileSync(file) : null;
  }
  private syncDirectory(directory: string) {
    if (process.platform === 'win32' || this.options.platform === 'win32') return;
    const fd = fs.openSync(directory, 'r');
    try {
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
  }
  private write(file: string, bytes: Buffer) {
    this.check(file);
    const fd = fs.openSync(file, 'wx', 0o600);
    try {
      fs.writeFileSync(fd, bytes);
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    ensure(this.read(file)?.equals(bytes), 'Escritura no verificable');
    this.syncDirectory(path.dirname(file));
  }
  private json(file: string, value: unknown) {
    this.write(file, Buffer.from(canonical(value) + '\n'));
  }
  private phase(phase: Phase) {
    this.options.fault?.(phase);
  }
  private authority(activation = false): Project | null {
    this.permissions.verifyRoot(this.root);
    const bytes = this.read(this.inside('coordinacion/PROYECTO.md'));
    if (activation) {
      ensure(bytes === null, 'Proyecto ya existente');
      return null;
    }
    ensure(bytes, 'Proyecto no activado');
    const p = project(document(bytes), this.options.projectId);
    ensure(
      p.coordinatorChatId === this.options.coordinatorChatId &&
        p.ownerEpoch === this.options.ownerEpoch,
      'Autoridad o epoch no vigente',
    );
    return p;
  }
  private locked<T>(action: () => T): T {
    this.permissions.verifyRoot(this.root);
    this.mkdir(path.join(this.root, 'coordinacion'));
    this.mkdir(this.control);
    this.mkdir(this.operations);
    this.check(this.lock);
    const token = randomUUID();
    let fd: number;
    try {
      fd = fs.openSync(this.lock, 'wx', 0o600);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'EEXIST')
        throw new Error('Bloqueo ocupado o incierto; requiere supervisión', { cause: error });
      throw error;
    }
    // Un fallo, incluso mientras se escribe el propietario, conserva la exclusión.
    try {
      fs.writeFileSync(
        fd,
        canonical({
          token,
          pid: process.pid,
          host: os.hostname(),
          coordinatorChatId: this.options.coordinatorChatId,
          ownerEpoch: this.options.ownerEpoch,
        }),
      );
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    this.permissions.verifyRoot(this.lock);
    this.permissions.verifyRoot(this.control);
    this.permissions.verifyRoot(path.join(this.root, 'coordinacion'));
    let result: T;
    try {
      result = action();
    } catch (error) {
      // Solo estos rechazos explícitos ocurren después de recuperar sin incertidumbre
      // y antes de preparar una nueva operación. Los demás errores conservan el lock.
      if (error instanceof KnownRejection) this.release(token);
      throw error;
    }
    this.release(token);
    return result;
  }
  private release(token: string) {
    this.check(this.lock);
    this.permissions.verifyRoot(this.lock);
    const owner = object(strictJson(fs.readFileSync(this.lock)));
    ensure(owner.token === token, 'Bloqueo ya no pertenece al escritor');
    fs.unlinkSync(this.lock);
    this.syncDirectory(this.control);
  }
  private tasks(): Task[] {
    const directory = this.inside('coordinacion');
    if (!exists(directory)) return [];
    const result: Task[] = [];
    const ids = new Set<string>();
    for (const entry of fs.readdirSync(directory).sort()) {
      if (!entry.startsWith('T-')) continue;
      taskId(entry);
      const bytes = this.read(this.inside(`coordinacion/${entry}/TAREA.md`));
      ensure(bytes, 'Tarea incompleta');
      const t = task(document(bytes), this.options.projectId, entry);
      for (const receipt of t.receipts) {
        ensure(!ids.has(receipt.updateId), 'ID repetido entre tareas');
        ids.add(receipt.updateId);
      }
      result.push(t);
    }
    return result;
  }
  private validateTarget(bytes: Buffer, m: Manifest): Project | Task | { generation: number } {
    if (m.kind === 'derivado') {
      const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
      ensure(
        text.startsWith(m.taskId === null ? '# Tareas\n\n' : '# Entregas\n\n'),
        'Derivado inválido',
      );
      return {
        generation:
          sha(bytes) === m.proposedSha256 ? m.proposedGeneration : (m.baseGeneration ?? 1),
      };
    }
    return m.taskId === null
      ? project(document(bytes), m.projectId)
      : task(document(bytes), m.projectId, m.taskId);
  }
  private manifest(value: unknown): Manifest {
    const m = object(value);
    keys(m, [
      'schemaVersion',
      'operationId',
      'kind',
      'projectId',
      'taskId',
      'coordinatorChatId',
      'expectedOwnerEpoch',
      'target',
      'baseGeneration',
      'proposedGeneration',
      'baseSha256',
      'proposedSha256',
      'notice',
      'reason',
      'createdAt',
    ]);
    ensure(m.schemaVersion === 1, 'Versión de diario inválida');
    uuid(m.operationId);
    uuid(m.projectId);
    ensure(
      m.projectId === this.options.projectId &&
        m.coordinatorChatId === this.options.coordinatorChatId,
      'Diario ajeno',
    );
    ensure(
      ['activar-proyecto', 'crear-tarea', 'aviso', 'derivado'].includes(String(m.kind)),
      'Operación no implementada',
    );
    if (m.taskId !== null) taskId(m.taskId);
    const target =
      m.kind === 'derivado'
        ? m.taskId === null
          ? 'coordinacion/INDICE.md'
          : `coordinacion/${String(m.taskId)}/ENTREGAS.md`
        : m.taskId === null
          ? 'coordinacion/PROYECTO.md'
          : `coordinacion/${String(m.taskId)}/TAREA.md`;
    ensure(m.target === target, 'Destino de diario inválido');
    integer(m.proposedGeneration);
    if (m.baseGeneration !== null) integer(m.baseGeneration);
    if (m.baseSha256 !== null) hash(m.baseSha256);
    hash(m.proposedSha256);
    timestamp(m.createdAt);
    ensure(typeof m.reason === 'string' && m.reason.length > 0, 'Motivo requerido');
    if (m.kind === 'activar-proyecto')
      ensure(
        m.taskId === null &&
          m.expectedOwnerEpoch === null &&
          m.baseGeneration === null &&
          m.baseSha256 === null &&
          m.proposedGeneration === 1 &&
          m.notice === null,
        'Activación inválida',
      );
    else if (m.kind === 'derivado') {
      ensure(
        m.expectedOwnerEpoch === this.options.ownerEpoch &&
          m.notice === null &&
          (m.baseGeneration === null
            ? m.baseSha256 === null && m.proposedGeneration === 1
            : m.baseSha256 !== null && m.proposedGeneration === Number(m.baseGeneration) + 1),
        'Derivado inválido',
      );
    } else {
      ensure(
        m.taskId !== null && m.expectedOwnerEpoch === this.options.ownerEpoch,
        'Epoch inválido',
      );
      if (m.kind === 'crear-tarea')
        ensure(
          m.notice === null &&
            m.baseGeneration === null &&
            m.baseSha256 === null &&
            m.proposedGeneration === 1,
          'Creación inválida',
        );
      else {
        const n = notice(m.notice);
        ensure(
          n.projectId === m.projectId &&
            n.taskId === m.taskId &&
            typeof m.baseGeneration === 'number' &&
            m.proposedGeneration === m.baseGeneration + 1 &&
            m.baseSha256 !== null,
          'Aviso de diario inválido',
        );
      }
    }
    return m as Manifest;
  }
  private evidence(bytes: Buffer, m: Manifest): boolean {
    const value = this.validateTarget(bytes, m);
    if (value.generation < m.proposedGeneration) return false;
    if ('receipts' in value) {
      if (m.kind === 'crear-tarea')
        return value.adminOperations.some(
          (op) =>
            op.operationId === m.operationId &&
            op.baseGeneration === m.baseGeneration &&
            op.proposedGeneration === m.proposedGeneration,
        );
      return (
        value.receipts.some(
          (r) => r.operationId === m.operationId && canonical(r.notice) === canonical(m.notice),
        ) ||
        value.incidents.some(
          (i) => i.operationId === m.operationId && canonical(i.notice) === canonical(m.notice),
        )
      );
    }
    return (
      m.kind === 'activar-proyecto' &&
      'operations' in value &&
      value.operations.some(
        (op) =>
          op.operationId === m.operationId &&
          op.newEpoch === 1 &&
          op.newCoordinator === m.coordinatorChatId,
      )
    );
  }
  private publish(m: Manifest, dir: string, proposal: Buffer, base: Buffer | null) {
    this.authority(m.kind === 'activar-proyecto');
    const destination = this.inside(m.target);
    ensure(equal(this.read(destination), base), 'La base cambió');
    this.mkdir(path.dirname(destination));
    const temp = destination + '.' + m.operationId + '.tmp';
    ensure(!exists(temp), 'Temporal existente: inspección necesaria');
    this.write(temp, proposal);
    this.phase('temporary');
    this.permissions.verifyRoot(temp);
    if (base !== null) this.permissions.verifyRoot(destination);
    const before = this.savedPermissions(dir, m);
    if (before !== null)
      ensure(this.permissions.inspect(destination) === before, 'Permisos de base modificados');
    if (before !== null && (this.options.platform ?? process.platform) !== 'win32')
      ensure(
        this.permissions.inspect(temp) === before,
        'Modo POSIX incompatible antes de publicar',
      );
    this.permissions.verifyRoot(this.root);
    ensure(equal(this.read(destination), base), 'Base modificada durante preparación');
    if (base !== null && (this.options.platform ?? process.platform) === 'win32') {
      const report = replaceWindows(
        { destination, replacement: temp, backup: path.join(dir, 'respaldo.md') },
        this.options.replaceRunner,
      );
      ensure(report === null, 'Sustitución incierta: conservar y supervisar');
      ensure(
        this.read(path.join(dir, 'respaldo.md'))?.equals(base),
        'Respaldo Windows no verificable',
      );
    } else fs.renameSync(temp, destination);
    this.phase('published');
    if (before !== null)
      ensure(this.permissions.inspect(destination) === before, 'Permisos no preservados');
    this.syncDirectory(path.dirname(destination));
    ensure(this.read(destination)?.equals(proposal), 'Publicación no verificable');
    this.validateTarget(proposal, m);
    this.phase('verified');
    this.complete(dir, m);
    this.phase('completed');
  }
  private complete(dir: string, m: Manifest) {
    const file = path.join(dir, 'completada.json');
    const expected = {
      schemaVersion: 1,
      operationId: m.operationId,
      proposedSha256: m.proposedSha256,
    };
    if (exists(file)) {
      const bytes = this.read(file);
      ensure(bytes, 'Marcador ausente');
      const c = object(strictJson(bytes));
      keys(c, [...Object.keys(expected), 'verifiedAt']);
      ensure(
        Object.entries(expected).every(([k, v]) => c[k] === v),
        'Marcador completado inválido',
      );
      timestamp(c.verifiedAt);
    } else this.json(file, { ...expected, verifiedAt: new Date().toISOString() });
  }
  private savedPermissions(dir: string, m: Manifest): string | null {
    const bytes = this.read(path.join(dir, 'permisos.json'));
    ensure(bytes, 'Evidencia de permisos ausente');
    const value = object(strictJson(bytes));
    keys(value, ['schemaVersion', 'operationId', 'basePermissions']);
    ensure(
      value.schemaVersion === 1 &&
        value.operationId === m.operationId &&
        (m.baseSha256 === null
          ? value.basePermissions === null
          : typeof value.basePermissions === 'string' && value.basePermissions.length > 0),
      'Evidencia de permisos inválida',
    );
    return value.basePermissions as string | null;
  }
  private transaction(
    kind: Kind,
    target: string,
    value: Project | Task,
    operationId: string,
    reason: string,
    n: Notice | null,
  ): void {
    const destination = this.inside(target);
    const base = this.read(destination);
    const proposal = markdown(value);
    const m: Manifest = {
      schemaVersion: 1,
      operationId,
      kind,
      projectId: this.options.projectId,
      taskId: 'taskId' in value ? value.taskId : null,
      coordinatorChatId: this.options.coordinatorChatId,
      expectedOwnerEpoch: kind === 'activar-proyecto' ? null : this.options.ownerEpoch,
      target,
      baseGeneration:
        base === null
          ? null
          : this.validateTarget(base, {
              taskId: 'taskId' in value ? value.taskId : null,
              projectId: this.options.projectId,
            } as Manifest).generation,
      proposedGeneration: value.generation,
      baseSha256: base === null ? null : sha(base),
      proposedSha256: sha(proposal),
      notice: n,
      reason,
      createdAt: new Date().toISOString(),
    };
    this.prepare(m, base, proposal);
  }
  private prepare(m: Manifest, base: Buffer | null, proposal: Buffer) {
    const operationId = m.operationId;
    this.manifest(m);
    this.validateTarget(proposal, m);
    ensure(
      m.kind === 'derivado' || this.evidence(proposal, m),
      'Propuesta no acredita la operación',
    );
    const dir = path.join(this.operations, operationId);
    fs.mkdirSync(dir, { mode: 0o700 });
    this.permissions.verifyRoot(dir);
    this.phase('operation-directory');
    this.json(path.join(dir, 'permisos.json'), {
      schemaVersion: 1,
      operationId,
      basePermissions: base === null ? null : this.permissions.inspect(this.inside(m.target)),
    });
    if (base !== null) this.write(path.join(dir, 'base.md'), base);
    else this.json(path.join(dir, 'ausencia.json'), { schemaVersion: 1, absent: true });
    this.phase('base');
    this.write(path.join(dir, 'propuesta.md'), proposal);
    this.phase('proposal');
    const bytes = Buffer.from(canonical(m) + '\n');
    this.write(path.join(dir, 'operacion.json'), bytes);
    this.phase('manifest');
    this.json(path.join(dir, 'lista.json'), {
      schemaVersion: 1,
      operationId,
      manifestSha256: sha(bytes),
    });
    this.phase('ready');
    this.publish(m, dir, proposal, base);
  }
  private recoverLocked() {
    for (const id of fs.readdirSync(this.operations).sort()) {
      uuid(id);
      const dir = this.inside(`coordinacion/.control/operaciones/${id}`);
      this.check(dir);
      this.permissions.verifyRoot(dir);
      const manifestBytes = this.read(path.join(dir, 'operacion.json'));
      const readyBytes = this.read(path.join(dir, 'lista.json'));
      ensure(
        manifestBytes && readyBytes,
        'Operación sin preparación completa: requiere inspección',
      );
      const m = this.manifest(strictJson(manifestBytes));
      ensure(m.operationId === id, 'Operación en carpeta ajena');
      const ready = object(strictJson(readyBytes));
      keys(ready, ['schemaVersion', 'operationId', 'manifestSha256']);
      ensure(
        ready.schemaVersion === 1 &&
          ready.operationId === id &&
          ready.manifestSha256 === sha(manifestBytes),
        'Lista inválida',
      );
      const proposal = this.read(path.join(dir, 'propuesta.md'));
      ensure(proposal && sha(proposal) === m.proposedSha256, 'Propuesta inválida');
      const proposed = this.validateTarget(proposal, m);
      ensure(proposed.generation === m.proposedGeneration, 'Generación propuesta inválida');
      ensure(
        m.kind === 'derivado' || this.evidence(proposal, m),
        'Propuesta sin evidencia de operación',
      );
      const base = this.read(path.join(dir, 'base.md'));
      if (m.baseSha256 === null) {
        ensure(base === null, 'Base inesperada');
        const absenceBytes = this.read(path.join(dir, 'ausencia.json'));
        ensure(absenceBytes, 'Ausencia no acreditada');
        const absence = object(strictJson(absenceBytes));
        keys(absence, ['schemaVersion', 'absent']);
        ensure(absence.schemaVersion === 1 && absence.absent === true, 'Ausencia inválida');
      } else {
        ensure(base && sha(base) === m.baseSha256, 'Base inválida');
        ensure(
          this.validateTarget(base, m).generation === m.baseGeneration,
          'Generación base inválida',
        );
      }
      const completed = exists(path.join(dir, 'completada.json'));
      const basePermissions = this.savedPermissions(dir, m);
      if (completed) this.complete(dir, m);
      // Los derivados confirmados son descartables; nunca acreditan un acuse.
      // Su ausencia se repara solo al solicitar explícitamente rebuildIndex().
      if (m.kind === 'derivado' && completed) continue;
      const current = this.read(this.inside(m.target));
      if (equal(current, proposal) || (current && this.evidence(current, m))) {
        this.authority();
        const destination = this.inside(m.target);
        this.permissions.verifyRoot(destination);
        if (basePermissions !== null)
          ensure(
            this.permissions.inspect(destination) === basePermissions,
            'Recuperación con permisos no preservados',
          );
        this.complete(dir, m);
        continue;
      }
      ensure(!completed, 'Operación completada sin canónico acreditado');
      ensure(equal(current, base), 'Canónico ambiguo: no restaurar versión anterior');
      this.publish(m, dir, proposal, base);
    }
  }
  activate(reason: string): void {
    ensure(reason.trim(), 'Motivo requerido');
    this.locked(() => {
      this.recoverLocked();
      this.authority(true);
      const operationId = randomUUID();
      const p: Project = {
        schemaVersion: 1,
        projectId: this.options.projectId,
        coordinatorChatId: this.options.coordinatorChatId,
        ownerEpoch: 1,
        generation: 1,
        operations: [
          {
            operationId,
            previousEpoch: null,
            newEpoch: 1,
            previousCoordinator: null,
            newCoordinator: this.options.coordinatorChatId,
          },
        ],
      };
      this.transaction(
        'activar-proyecto',
        'coordinacion/PROYECTO.md',
        p,
        operationId,
        reason,
        null,
      );
    });
  }
  createTask(id: string, assignedChatId: string, reason: string): void {
    taskId(id);
    ensure(assignedChatId.trim() && reason.trim(), 'Asignación y motivo requeridos');
    this.authority();
    this.tasks();
    this.locked(() => {
      this.recoverLocked();
      this.authority();
      this.tasks();
      if (exists(this.inside(`coordinacion/${id}`))) throw new KnownRejection('Tarea ya existente');
      const operationId = randomUUID();
      const t: Task = {
        schemaVersion: 1,
        projectId: this.options.projectId,
        taskId: id,
        generation: 1,
        assignedChatId,
        activeCycle: 1,
        current: null,
        receipts: [],
        incidents: [],
        adminOperations: [
          { operationId, kind: 'crear-tarea', baseGeneration: null, proposedGeneration: 1 },
        ],
      };
      this.transaction('crear-tarea', `coordinacion/${id}/TAREA.md`, t, operationId, reason, null);
    });
  }
  apply(input: unknown, reason: string): Query {
    const n = notice(input);
    ensure(n.projectId === this.options.projectId && reason.trim(), 'Aviso ajeno o motivo vacío');
    // Rechazos de entrada/canónico no crean un bloqueo ni un diario.
    this.authority();
    this.tasks();
    return this.locked(() => {
      this.recoverLocked();
      this.authority();
      const all = this.tasks();
      const source = all.find((t) => t.taskId === n.taskId);
      if (!source) throw new KnownRejection('Tarea no existente');
      const operationId = randomUUID();
      const result = decide(source, n, all, operationId, new Date().toISOString());
      if (result.changed)
        this.transaction(
          'aviso',
          `coordinacion/${n.taskId}/TAREA.md`,
          result.task,
          operationId,
          reason,
          n,
        );
      return result.query;
    });
  }
  recover(): void {
    this.locked(() => {
      this.recoverLocked();
      this.authority();
    });
  }
  query(id: string, updateId: string): Query {
    taskId(id);
    uuid(updateId);
    const response: Query = {
      schemaVersion: 1,
      projectId: this.options.projectId,
      taskId: id,
      updateId,
      result: 'incierto',
      receipt: null,
      incidentId: null,
      generation: null,
      reason: 'Acuse no acreditado',
    };
    try {
      this.authority();
      const all = this.tasks();
      const t = all.find((t) => t.taskId === id);
      ensure(t, 'Tarea ausente');
      const receipt = t.receipts.find((r) => r.updateId === updateId);
      if (receipt)
        return {
          ...response,
          result: receipt.decision,
          receipt,
          generation: t.generation,
          reason: null,
        };
      const incident = t.incidents.find((i) => i.notice.updateId === updateId);
      if (incident)
        return {
          ...response,
          result: 'conflicto',
          incidentId: incident.incidentId,
          generation: t.generation,
          reason: incident.reason,
        };
      return response;
    } catch (error) {
      return { ...response, reason: error instanceof Error ? error.message : 'Documento inválido' };
    }
  }
  /** Índice reconstruible: ningún dato de este archivo participa en decisiones. */
  rebuildIndex(): void {
    this.locked(() => {
      this.recoverLocked();
      this.authority();
      const all = this.tasks();
      const publications = [
        {
          relative: 'coordinacion/INDICE.md',
          bytes: Buffer.from(
            '# Tareas\n\n' + all.map((t) => `- [${t.taskId}](${t.taskId}/TAREA.md)\n`).join(''),
          ),
        },
        ...all.map((t) => ({
          relative: `coordinacion/${t.taskId}/ENTREGAS.md`,
          bytes: Buffer.from(
            '# Entregas\n\n' +
              t.receipts
                .filter((r) => r.decision === 'aplicado')
                .map((r) => {
                  const json = JSON.stringify(r.notice.references);
                  const fence = '`'.repeat(
                    Math.max(3, ...[...json.matchAll(/`+/g)].map((m) => m[0].length + 1)),
                  );
                  return `${fence}json\n${json}\n${fence}\n`;
                })
                .join(''),
          ),
        })),
      ];
      for (const item of publications) {
        const base = this.read(this.inside(item.relative));
        if (equal(base, item.bytes)) continue;
        let baseGeneration: number | null = null;
        if (base) {
          baseGeneration = 1;
          for (const id of fs.readdirSync(this.operations)) {
            const previous = this.manifest(
              strictJson(fs.readFileSync(path.join(this.operations, id, 'operacion.json'))),
            );
            if (previous.kind === 'derivado' && previous.target === item.relative)
              baseGeneration = Math.max(baseGeneration, previous.proposedGeneration);
          }
        }
        const match = /^coordinacion\/(T-\d{3,})\/ENTREGAS.md$/.exec(item.relative);
        const m: Manifest = {
          schemaVersion: 1,
          operationId: randomUUID(),
          kind: 'derivado',
          projectId: this.options.projectId,
          taskId: match?.[1] ?? null,
          coordinatorChatId: this.options.coordinatorChatId,
          expectedOwnerEpoch: this.options.ownerEpoch,
          target: item.relative,
          baseGeneration,
          proposedGeneration: (baseGeneration ?? 0) + 1,
          baseSha256: base ? sha(base) : null,
          proposedSha256: sha(item.bytes),
          notice: null,
          reason: 'Reconstrucción explícita de índice derivado',
          createdAt: new Date().toISOString(),
        };
        this.prepare(m, base, item.bytes);
      }
    });
  }
}
