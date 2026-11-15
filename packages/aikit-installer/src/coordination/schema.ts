import { createHash } from 'node:crypto';

export const states = [
  'Preparada',
  'Esperando al usuario',
  'En curso',
  'Bloqueada',
  'Pausada',
  'Finalizada',
  'Cancelada',
] as const;
export type Current = { cycle: number; revision: number; state: string; updateId: string };
export type Notice = {
  schemaVersion: 1;
  projectId: string;
  taskId: string;
  cycle: number;
  senderChatId: string;
  updateId: string;
  revision: number;
  state: string;
  summary: string;
  references: string[];
  corrects: string | null;
};
export type Decision = 'aplicado' | 'antiguo' | 'pendiente';
export type Outcome = {
  decision: Decision;
  resultingCurrent: Current | null;
  operationId: string;
  recordedAt: string;
};
export type Receipt = Outcome & { updateId: string; notice: Notice; history: Outcome[] };
export type Incident = {
  incidentId: string;
  notice: Notice;
  conflictsWithUpdateId: string;
  conflictsWithTaskId?: string;
  reason: string;
  operationId: string;
  recordedAt: string;
};
export type Admin = {
  operationId: string;
  kind: 'crear-tarea';
  baseGeneration: null;
  proposedGeneration: number;
};
export type Task = {
  schemaVersion: 1;
  projectId: string;
  taskId: string;
  generation: number;
  assignedChatId: string;
  activeCycle: number;
  current: Current | null;
  receipts: Receipt[];
  incidents: Incident[];
  adminOperations: Admin[];
};
export type Project = {
  schemaVersion: 1;
  projectId: string;
  coordinatorChatId: string;
  ownerEpoch: number;
  generation: number;
  operations: {
    operationId: string;
    previousEpoch: null;
    newEpoch: number;
    previousCoordinator: null;
    newCoordinator: string;
  }[];
};
export type Query = {
  schemaVersion: 1;
  projectId: string;
  taskId: string;
  updateId: string;
  result: Decision | 'duplicado' | 'conflicto' | 'incierto';
  receipt: Receipt | null;
  incidentId: string | null;
  generation: number | null;
  reason: string | null;
};

export function ensure(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}
export function uuid(value: unknown): asserts value is string {
  ensure(
    typeof value === 'string' &&
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(value),
    'UUID v4 inválido',
  );
}
export function taskId(value: unknown): asserts value is string {
  ensure(typeof value === 'string' && /^T-\d{3,}$/.test(value), 'ID de tarea inválido');
}
function positive(value: unknown) {
  ensure(
    typeof value === 'number' && Number.isSafeInteger(value) && value > 0,
    'Entero positivo inválido',
  );
}
function unicode(value: unknown): asserts value is string {
  ensure(
    typeof value === 'string' &&
      !/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value),
    'Unicode inválido',
  );
}
function str(value: unknown) {
  unicode(value);
  ensure(value.length > 0, 'Cadena vacía o inválida');
}
function date(value: unknown) {
  ensure(
    typeof value === 'string' &&
      /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(value) &&
      new Date(value).toISOString() === value,
    'Fecha inválida',
  );
}
function obj(
  value: unknown,
  keys: string[],
  optional: string[] = [],
): asserts value is Record<string, unknown> {
  ensure(value !== null && typeof value === 'object' && !Array.isArray(value), 'Objeto requerido');
  ensure(
    keys.every((k) => Object.hasOwn(value, k)) &&
      Object.keys(value).every((k) => keys.includes(k) || optional.includes(k)),
    'Campos incorrectos',
  );
}
function array(value: unknown): asserts value is unknown[] {
  ensure(Array.isArray(value), 'Array requerido');
}
function exactInteger(token: string) {
  const parts = /^-?(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(token)!;
  const digits = (parts[1] + (parts[2] ?? '')).replace(/^0+/, '');
  if (!digits) return;
  const significant = digits.replace(/0+$/, '');
  const scale =
    BigInt(parts[3] ?? '0') -
    BigInt(parts[2]?.length ?? 0) +
    BigInt(digits.length - significant.length);
  ensure(
    scale >= 0n && scale <= 16n && BigInt(significant.length) + scale <= 16n,
    'Número no entero exacto',
  );
  ensure(BigInt(significant) * 10n ** scale <= BigInt(Number.MAX_SAFE_INTEGER), 'Número no seguro');
}

/** Escáner previo: JSON.parse no detecta claves duplicadas ni números inexactos. */
export function strictJson(bytes: Uint8Array): unknown {
  const text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
  ensure(!text.startsWith('\uFEFF'), 'BOM no admitido');
  let i = 0;
  const ws = () => {
    while (/[\t\n\r ]/.test(text[i] ?? '') && i < text.length) i++;
  };
  const string = (): string => {
    const start = i++;
    while (i < text.length) {
      const c = text[i++];
      if (c === '\\') i++;
      else if (c === '"') {
        const value: unknown = JSON.parse(text.slice(start, i));
        ensure(
          typeof value === 'string' &&
            !/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value),
          'Unicode inválido',
        );
        return value;
      }
    }
    throw new Error('Cadena incompleta');
  };
  const value = (): void => {
    ws();
    if (text[i] === '{') {
      i++;
      ws();
      const keys = new Set<string>();
      if (text[i] !== '}') {
        for (;;) {
          ensure(text[i] === '"', 'Clave requerida');
          const key = string();
          ensure(!keys.has(key), 'Clave duplicada');
          keys.add(key);
          ws();
          ensure(text[i++] === ':', 'Separador requerido');
          value();
          ws();
          if (text[i] !== ',') break;
          i++;
          ws();
        }
      }
      ensure(text[i++] === '}', 'Objeto incompleto');
    } else if (text[i] === '[') {
      i++;
      ws();
      if (text[i] !== ']') {
        for (;;) {
          value();
          ws();
          if (text[i] !== ',') break;
          i++;
        }
      }
      ensure(text[i++] === ']', 'Array incompleto');
    } else if (text[i] === '"') string();
    else {
      const token = /^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(
        text.slice(i),
      )?.[0];
      ensure(token, 'Valor inválido');
      if (!['true', 'false', 'null'].includes(token)) exactInteger(token);
      i += token.length;
    }
  };
  value();
  ws();
  ensure(i === text.length, 'Contenido adicional');
  return JSON.parse(text) as unknown;
}
export function canonical(value: unknown): string {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object')
    return (
      '{' +
      Object.keys(value)
        .sort()
        .map((k) => JSON.stringify(k) + ':' + canonical((value as Record<string, unknown>)[k]))
        .join(',') +
      '}'
    );
  return JSON.stringify(value);
}
export function sha(bytes: Uint8Array): string {
  return createHash('sha256').update(bytes).digest('hex');
}
const prefix = '# AIKit coordinación v1\n\n```json\n';
export function markdown(value: unknown): Buffer {
  return Buffer.from(prefix + canonical(value) + '\n```\n');
}
export function document(bytes: Uint8Array): unknown {
  const text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
  ensure(text.startsWith(prefix) && text.endsWith('\n```\n'), 'Envoltura inválida');
  const body = text.slice(prefix.length, -5);
  ensure(!/[\r\n]/.test(body), 'JSON debe ocupar una línea');
  return strictJson(Buffer.from(body));
}
export function notice(value: unknown): Notice {
  obj(value, [
    'schemaVersion',
    'projectId',
    'taskId',
    'cycle',
    'senderChatId',
    'updateId',
    'revision',
    'state',
    'summary',
    'references',
    'corrects',
  ]);
  ensure(value.schemaVersion === 1, 'Versión inválida');
  uuid(value.projectId);
  taskId(value.taskId);
  positive(value.cycle);
  str(value.senderChatId);
  uuid(value.updateId);
  positive(value.revision);
  ensure(states.includes(value.state as (typeof states)[number]), 'Estado inválido');
  unicode(value.summary);
  array(value.references);
  value.references.forEach(unicode);
  if (value.corrects !== null) uuid(value.corrects);
  return value as Notice;
}
function current(value: unknown): asserts value is Current | null {
  if (value === null) return;
  obj(value, ['cycle', 'revision', 'state', 'updateId']);
  positive(value.cycle);
  positive(value.revision);
  uuid(value.updateId);
  ensure(states.includes(value.state as (typeof states)[number]), 'Estado inválido');
}
function outcome(value: Record<string, unknown>) {
  ensure(
    ['aplicado', 'antiguo', 'pendiente'].includes(String(value.decision)),
    'Decisión inválida',
  );
  current(value.resultingCurrent);
  uuid(value.operationId);
  date(value.recordedAt);
}
export function project(value: unknown, expected?: string): Project {
  obj(value, [
    'schemaVersion',
    'projectId',
    'coordinatorChatId',
    'ownerEpoch',
    'generation',
    'operations',
  ]);
  ensure(value.schemaVersion === 1, 'Versión inválida');
  uuid(value.projectId);
  if (expected) ensure(value.projectId === expected, 'Proyecto ajeno');
  str(value.coordinatorChatId);
  positive(value.ownerEpoch);
  positive(value.generation);
  ensure(value.ownerEpoch === 1 && value.generation === 1, 'Relevo no implementado');
  array(value.operations);
  ensure(value.operations.length === 1, 'Activación requerida');
  for (const op of value.operations) {
    obj(op, ['operationId', 'previousEpoch', 'newEpoch', 'previousCoordinator', 'newCoordinator']);
    uuid(op.operationId);
    ensure(
      op.previousEpoch === null &&
        op.previousCoordinator === null &&
        op.newEpoch === 1 &&
        op.newCoordinator === value.coordinatorChatId,
      'Activación inválida',
    );
  }
  return value as Project;
}
export function task(value: unknown, projectId: string, expectedTask: string): Task {
  obj(value, [
    'schemaVersion',
    'projectId',
    'taskId',
    'generation',
    'assignedChatId',
    'activeCycle',
    'current',
    'receipts',
    'incidents',
    'adminOperations',
  ]);
  ensure(
    value.schemaVersion === 1 && value.projectId === projectId && value.taskId === expectedTask,
    'Identidad inválida',
  );
  taskId(value.taskId);
  positive(value.generation);
  str(value.assignedChatId);
  ensure(value.activeCycle === 1, 'Ciclo no implementado');
  current(value.current);
  array(value.receipts);
  array(value.incidents);
  array(value.adminOperations);
  const ids = new Set<string>();
  for (const receipt of value.receipts) {
    obj(receipt, [
      'updateId',
      'notice',
      'decision',
      'resultingCurrent',
      'operationId',
      'recordedAt',
      'history',
    ]);
    uuid(receipt.updateId);
    const n = notice(receipt.notice);
    ensure(
      n.projectId === projectId &&
        n.taskId === expectedTask &&
        n.updateId === receipt.updateId &&
        !ids.has(n.updateId),
      'Recibo inconsistente',
    );
    ids.add(n.updateId);
    outcome(receipt);
    array(receipt.history);
    for (const h of receipt.history) {
      obj(h, ['decision', 'resultingCurrent', 'operationId', 'recordedAt']);
      outcome(h);
    }
    if (receipt.decision === 'aplicado')
      ensure(
        canonical(receipt.resultingCurrent) ===
          canonical({ cycle: n.cycle, revision: n.revision, state: n.state, updateId: n.updateId }),
        'Resultado aplicado inconsistente',
      );
  }
  const incidents = new Set<string>();
  for (const incident of value.incidents) {
    obj(
      incident,
      ['incidentId', 'notice', 'conflictsWithUpdateId', 'reason', 'operationId', 'recordedAt'],
      ['conflictsWithTaskId'],
    );
    uuid(incident.incidentId);
    ensure(!incidents.has(incident.incidentId), 'Incidente duplicado');
    incidents.add(incident.incidentId);
    const n = notice(incident.notice);
    ensure(n.projectId === projectId && n.taskId === expectedTask, 'Incidente ajeno');
    uuid(incident.conflictsWithUpdateId);
    if (incident.conflictsWithTaskId !== undefined) taskId(incident.conflictsWithTaskId);
    str(incident.reason);
    uuid(incident.operationId);
    date(incident.recordedAt);
  }
  ensure(value.adminOperations.length === 1, 'Creación requerida');
  for (const op of value.adminOperations) {
    obj(op, ['operationId', 'kind', 'baseGeneration', 'proposedGeneration']);
    uuid(op.operationId);
    ensure(
      op.kind === 'crear-tarea' && op.baseGeneration === null && op.proposedGeneration === 1,
      'Administración inválida',
    );
  }
  const typed = value as Task;
  let observed: Current | null = null;
  const operations = new Set<string>(typed.adminOperations.map((op) => op.operationId));
  for (const r of typed.receipts) {
    ensure(!operations.has(r.operationId), 'Operación repetida');
    operations.add(r.operationId);
    ensure(r.history.length === 0, 'Resolución de pendientes no implementada');
    const assigned =
      r.notice.senderChatId === typed.assignedChatId && r.notice.cycle === typed.activeCycle;
    if (r.decision === 'pendiente') ensure(!assigned, 'Pendiente sin desajuste de asignación');
    else {
      ensure(assigned, 'Recibo de procedencia ajena');
      if (r.decision === 'aplicado') {
        ensure(r.notice.revision > (observed?.revision ?? 0), 'Revisión aplicada no creciente');
        observed = r.resultingCurrent;
      } else
        ensure(observed && r.notice.revision < observed.revision, 'Antiguo sin revisión posterior');
    }
    ensure(
      canonical(r.resultingCurrent) === canonical(observed),
      'Resultado de recibo inconsistente',
    );
  }
  for (const i of typed.incidents) {
    ensure(!operations.has(i.operationId), 'Operación repetida');
    operations.add(i.operationId);
  }
  ensure(
    typed.generation === 1 + typed.receipts.length + typed.incidents.length,
    'Generación incoherente',
  );
  if (typed.current !== null)
    ensure(
      typed.receipts.some(
        (r) =>
          r.decision === 'aplicado' && canonical(r.resultingCurrent) === canonical(typed.current),
      ),
      'Current sin recibo aplicado',
    );
  const max = typed.receipts
    .filter((r) => r.decision === 'aplicado')
    .reduce((n, r) => Math.max(n, r.notice.revision), 0);
  ensure((typed.current?.revision ?? 0) === max, 'Regresión de revisión');
  return typed;
}
