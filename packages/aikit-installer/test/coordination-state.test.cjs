const { test } = require('node:test');
const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const projectId = randomUUID();
const makeTask = (taskId = 'T-001') => ({
  schemaVersion: 1,
  projectId,
  taskId,
  generation: 1,
  assignedChatId: 'asignado',
  activeCycle: 1,
  current: null,
  receipts: [],
  incidents: [],
  adminOperations: [
    { operationId: randomUUID(), kind: 'crear-tarea', baseGeneration: null, proposedGeneration: 1 },
  ],
});
const notice = (patch = {}) => ({
  schemaVersion: 1,
  projectId,
  taskId: 'T-001',
  cycle: 1,
  senderChatId: 'asignado',
  updateId: randomUUID(),
  revision: 1,
  state: 'En curso',
  summary: 'original',
  references: [],
  corrects: null,
  ...patch,
});
async function engine() {
  const { decide } = await import('../dist/coordination/state.js');
  return (t, n, all = [t]) => decide(t, n, all, randomUUID(), '2026-11-15T00:00:00.000Z');
}
test('revisión pendiente contradictoria conserva primer aviso y registra incidente', async () => {
  const apply = await engine();
  const original = notice({ senderChatId: 'ajeno' });
  const first = apply(makeTask(), original).task;
  const result = apply(first, { ...original, updateId: randomUUID(), summary: 'otra declaración' });
  assert.equal(result.query.result, 'conflicto');
  assert.deepEqual(result.task.receipts[0].notice, original);
  assert.equal(result.task.receipts.length, 1);
  assert.equal(result.task.current, null);
  assert.equal(result.task.incidents.length, 1);
});
test('ID presente solo en incidente no reaparece cambiado ni se aplica en otra tarea', async () => {
  const apply = await engine();
  let t = apply(makeTask(), notice()).task;
  const conflicted = notice();
  t = apply(t, conflicted).task;
  assert.equal(
    t.receipts.some((r) => r.updateId === conflicted.updateId),
    false,
  );
  assert.equal(apply(t, { ...conflicted, revision: 2 }).query.result, 'conflicto');
  const other = makeTask('T-002');
  const result = apply(other, { ...conflicted, taskId: 'T-002', revision: 2 }, [t, other]);
  assert.equal(result.query.result, 'conflicto');
  assert.equal(result.task.current, null);
  assert.equal(result.task.receipts.length, 0);
  assert.equal(result.task.incidents[0].conflictsWithTaskId, 'T-001');
});
test('recibo original tiene prioridad global sobre copias de su ID en incidentes', async () => {
  const apply = await engine();
  const n = notice();
  const first = apply(makeTask(), n).task;
  const other = makeTask('T-002');
  const second = apply(other, { ...n, taskId: 'T-002' }, [first, other]).task;
  const result = apply(first, n, [second, first]);
  assert.equal(result.query.result, 'duplicado');
  assert.deepEqual(result.query.receipt.notice, n);
  assert.equal(result.changed, false);
});
