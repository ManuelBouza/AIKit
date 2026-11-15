const { test } = require('node:test');
const assert = require('node:assert/strict');
const { randomUUID } = require('node:crypto');
const load = () => import('../dist/coordination/schema.js');
test('parser estricto rechaza duplicados anidados, BOM, Unicode, números y envolturas', async () => {
  const s = await load();
  for (const input of [
    '{"a":1,"a":2}',
    '{"a":[{"x":1,"\\u0078":2}]}',
    '{"a":9007199254740993}',
    '{"a":1.5}',
    '{"a":1.0000000000000001}',
    '{"a":1e-999}',
    '{"a":9007199254740991.1}',
    '{"a":-1.0000000000000001}',
    '"\\ud800"',
    '"\\udc00"',
    '\ufeff{}',
    '{} x',
    '[1,]',
    '{"x":1,}',
  ])
    assert.throws(() => s.strictJson(Buffer.from(input)), input);
  assert.throws(() => s.strictJson(Buffer.from([0xff])));
  for (const [literal, expected] of [
    ['1.0', 1],
    ['100e-2', 1],
    ['1e2', 100],
    ['9007199254740991', Number.MAX_SAFE_INTEGER],
    ['0e-999', 0],
  ])
    assert.equal(s.strictJson(Buffer.from(literal)), expected);
  assert.deepEqual(s.strictJson(Buffer.from('{"a":"😀","b":[true,null]}')), {
    a: '😀',
    b: [true, null],
  });
  const b = s.markdown({ b: 2, a: 1 });
  assert.deepEqual(s.document(b), { a: 1, b: 2 });
  assert.throws(() => s.document(Buffer.concat([b, Buffer.from('extra')])));
  assert.equal(s.canonical({ z: [{ b: 1, a: ' x ' }], a: 2 }), '{"a":2,"z":[{"a":" x ","b":1}]}');
});
test('avisos rechazan campos desconocidos, rutas hostiles y estados inválidos', async () => {
  const s = await load();
  const n = {
    schemaVersion: 1,
    projectId: randomUUID(),
    taskId: 'T-001',
    cycle: 1,
    senderChatId: 'tarea',
    updateId: randomUUID(),
    revision: 1,
    state: 'En curso',
    summary: '',
    references: [],
    corrects: null,
  };
  assert.deepEqual(s.notice(n), n);
  for (const patch of [
    { extra: 1 },
    { taskId: '../T-001' },
    { revision: 0 },
    { revision: Infinity },
    { cycle: 2.3 },
    { state: 'otro' },
    { senderChatId: '' },
    { schemaVersion: 2 },
    { corrects: 'xxx' },
  ])
    assert.throws(() => s.notice({ ...n, ...patch }));
});
