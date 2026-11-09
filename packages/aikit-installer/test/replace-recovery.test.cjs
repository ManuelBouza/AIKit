// Simulaciones de estados documentados; no se invoca ReplaceFileW ni el instalador.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '../../../.aikit/node-test');
const moduleUrl = pathToFileURL(path.resolve(__dirname, '../dist/replace-recovery.js')).href;

for (const [code, layout, expected] of [
  [1175, { destination: 'original', replacement: 'nuevo' }, 'expected-original-paths'],
  [1176, { destination: 'original', replacement: 'nuevo' }, 'expected-original-paths'],
  [1177, { backup: 'original', replacement: 'nuevo' }, 'expected-backup-path'],
]) {
  test(`diagnostica simulación ${code} y conserva todos los archivos`, async (t) => {
    fs.mkdirSync(root, { recursive: true });
    const dir = fs.mkdtempSync(path.join(root, 'recuperacion-'));
    t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
    const paths = Object.fromEntries(['destination', 'replacement', 'backup'].map(name => [name, path.join(dir, name)]));
    for (const [name, content] of Object.entries(layout)) fs.writeFileSync(paths[name], content);
    const before = fs.readdirSync(dir).sort().map(name => [name, fs.readFileSync(path.join(dir, name), 'utf8')]);
    const observations = Object.fromEntries(Object.entries(paths).map(([name, file]) => [name, { path: file, exists: fs.existsSync(file) }]));
    const { diagnoseReplaceFailure } = await import(moduleUrl);
    const report = diagnoseReplaceFailure({ code, ...observations });
    assert.equal(report.classification, expected);
    assert.equal(report.action, 'preserve-and-inspect');
    assert.deepEqual(report.paths, observations);
    assert.deepEqual(fs.readdirSync(dir).sort().map(name => [name, fs.readFileSync(path.join(dir, name), 'utf8')]), before);
  });
}

test('estado desconocido o inconsistente nunca se clasifica como recuperado', async () => {
  const { diagnoseReplaceFailure } = await import(moduleUrl);
  const destination = { path: 'destino', exists: 'unknown' };
  const replacement = { path: 'reemplazo', exists: true };
  const backup = { path: 'respaldo', exists: true };
  for (const code of [1175, 1176, 1177, null, 5]) {
    const report = diagnoseReplaceFailure({ code, destination, replacement, backup });
    assert.equal(report.classification, 'unverified');
    assert.equal(report.action, 'preserve-and-inspect');
    assert.deepEqual(report.paths, { destination, replacement, backup });
  }
});
