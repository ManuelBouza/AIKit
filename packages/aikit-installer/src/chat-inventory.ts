import * as fs from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { acquireLock, checkedPath, decoder, readOptional } from './project-files.js';
import { replaceWindows } from './windows-replace.js';

const states = ['Disponible', 'En curso', 'En espera', 'Pausado', 'Cerrado'] as const;
const entryKeys = [
  'id',
  'project',
  'responsibility',
  'state',
  'originId',
  'reason',
  'continuation',
];

type Entry = {
  id: string;
  project: string;
  responsibility: string;
  state: (typeof states)[number];
  originId?: string;
  reason?: string;
  continuation?: string;
};

type Record = Entry & { title: string; updatedAt: string; revision: number };

export function inventoryPath(root: string): string {
  return path.join(root, '.aikit', 'chats');
}

export function readInventoryDirectory(directory: string): string[] | null {
  checkedPath(directory);
  try {
    return fs.readdirSync(directory);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw error;
  }
}

function recordName(id: string): string {
  const hash = createHash('sha256').update(id, 'utf8').digest('hex');
  return `${hash}.json`;
}

function object(value: unknown, keys: string[]): asserts value is { [key: string]: unknown } {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw new Error('Se esperaba un objeto JSON de ficha');
  if (Object.keys(value).some((key) => !keys.includes(key)))
    throw new Error('La ficha contiene campos ajenos al inventario');
}

function line(value: unknown, field: string): string {
  if (
    typeof value !== 'string' ||
    !value.trim() ||
    value !== value.trim() ||
    /[\p{C}\p{Zl}\p{Zp}]/u.test(value)
  )
    throw new Error(`Campo de una línea inválido: ${field}`);
  return value;
}

function nativeId(value: unknown, field: string): string {
  const id = line(value, field);
  if (/\s/u.test(id)) throw new Error(`ID nativo completo inválido: ${field}`);
  return id;
}

function parseEntry(value: { [key: string]: unknown }): Entry {
  const id = nativeId(value.id, 'id');
  const project = line(value.project, 'project');
  const responsibility = line(value.responsibility, 'responsibility');
  const state = states.find((state) => state === value.state);
  if (!state) throw new Error('Estado de chat inválido');
  const entry: Entry = { id, project, responsibility, state };
  if (value.originId !== undefined) {
    entry.originId = nativeId(value.originId, 'originId');
    if (entry.originId === id) throw new Error('Un fork requiere un ID distinto del origen');
  }
  if (state === 'Pausado' || state === 'En espera') {
    entry.reason = line(value.reason, 'reason');
    entry.continuation = line(value.continuation, 'continuation');
  } else if (value.reason !== undefined || value.continuation !== undefined) {
    throw new Error('El motivo y la continuación solo corresponden a espera o pausa');
  }
  return entry;
}

function title(entry: Entry): string {
  return `[${entry.state}] ${entry.project} · ${entry.responsibility}`;
}

function readRecord(file: string): Record | null {
  checkedPath(file);
  const bytes = readOptional(file);
  if (!bytes) return null;
  const value: unknown = JSON.parse(decoder.decode(bytes));
  object(value, [...entryKeys, 'title', 'updatedAt', 'revision']);
  const entry = parseEntry(value);
  if (path.basename(file) !== recordName(entry.id))
    throw new Error(`La identidad de la ficha no corresponde a su ruta: ${file}`);
  const { updatedAt, revision } = value;
  if (
    value.title !== title(entry) ||
    typeof updatedAt !== 'string' ||
    !Number.isFinite(Date.parse(updatedAt)) ||
    new Date(updatedAt).toISOString() !== updatedAt ||
    typeof revision !== 'number' ||
    !Number.isSafeInteger(revision) ||
    revision < 1
  )
    throw new Error(`Metadatos inválidos en la ficha: ${file}`);
  return { ...entry, title: value.title, updatedAt, revision };
}

export function listRecords(
  directory: string,
  names = readInventoryDirectory(directory) ?? [],
): Record[] {
  const records: Record[] = [];
  for (const name of names.sort()) {
    if (!/^[a-f0-9]{64}\.json$/.test(name)) continue;
    const record = readRecord(path.join(directory, name));
    if (!record) throw new Error(`La ficha cambió durante la consulta: ${name}`);
    records.push(record);
  }
  return records;
}

function planUpdate(file: string, entry: Entry, expected: number): Record {
  const current = readRecord(file);
  if (current && current.id !== entry.id)
    throw new Error('El ID solicitado no coincide con la ficha existente');
  if ((current?.revision ?? 0) !== expected)
    throw new Error(
      `Revisión obsoleta: esperada ${expected}; actual ${current?.revision ?? 0}. Vuelva a consultar el inventario.`,
    );
  if (current?.originId && entry.originId && current.originId !== entry.originId)
    throw new Error('El ID de origen de un fork es estable');
  const originId = entry.originId ?? current?.originId;
  return {
    ...entry,
    ...(originId === undefined ? {} : { originId }),
    title: title(entry),
    updatedAt: new Date().toISOString(),
    revision: expected + 1,
  };
}

export function updateRecord(directory: string, expected: number, dry: boolean) {
  const value: unknown = JSON.parse(decoder.decode(fs.readFileSync(0)));
  object(value, entryKeys);
  const entry = parseEntry(value);
  const file = path.join(directory, recordName(entry.id));
  const proposal = planUpdate(file, entry, expected);
  if (dry) return { path: file, record: proposal };

  checkedPath(directory);
  fs.mkdirSync(directory, { recursive: true, mode: 0o700 });
  const lockFile = `${file}.lock`;
  const lock = acquireLock(lockFile, 'Hay otra edición de esta ficha o un bloqueo pendiente');
  const temporary = path.join(directory, `.ficha-${randomUUID()}.tmp`);
  const backup = `${temporary}.bak`;
  let preserve = false;
  try {
    const record = planUpdate(file, entry, expected);
    let mode = 0o600;
    if (expected !== 0) {
      // Una sustitución del directorio no acredita permiso de escritura sobre la ficha.
      const current = fs.openSync(file, 'r+');
      try {
        mode = fs.fstatSync(current).mode & 0o777;
      } finally {
        fs.closeSync(current);
      }
    }
    fs.writeFileSync(temporary, JSON.stringify(record, null, 2) + '\n', { flag: 'wx', mode });
    checkedPath(file);
    if (expected !== 0 && process.platform === 'win32') {
      checkedPath(backup);
      // File.Replace conserva la ACL y puede dejar los bytes previos en el respaldo.
      preserve = true;
      const report = replaceWindows({ destination: file, replacement: temporary, backup });
      if (report)
        throw new Error(
          `Falló la sustitución de la ficha; conserve los archivos y examine el diagnóstico: ${JSON.stringify(report)}`,
        );
      preserve = false;
    } else {
      if (expected !== 0) fs.chmodSync(temporary, mode);
      fs.renameSync(temporary, file);
    }
    return { path: file, record };
  } finally {
    try {
      if (!preserve) {
        fs.rmSync(temporary, { force: true });
        fs.rmSync(backup, { force: true });
      }
    } finally {
      fs.closeSync(lock);
      if (!preserve) fs.unlinkSync(lockFile);
    }
  }
}
