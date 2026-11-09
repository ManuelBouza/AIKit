const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

test('un bloqueo previo impide escrituras y se conserva para inspección', (t) => {
  const base = path.resolve(__dirname, '../../../.aikit/node-test');
  fs.mkdirSync(base, { recursive: true });
  const home = fs.mkdtempSync(path.join(base, 'lock-'));
  t.after(() => fs.rmSync(home, { recursive: true, force: true }));
  const target = path.join(home, 'AGENTS.md');
  const lock = path.join(home, '.aikit-instructions.lock');
  fs.writeFileSync(target, 'instrucción existente\n');
  fs.writeFileSync(lock, 'bloqueo previo');
  const result = spawnSync(process.execPath, [path.resolve(__dirname, '../dist/cli.js'), 'install', '--codex-home', home], { encoding: 'utf8' });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /bloqueo/);
  assert.equal(fs.readFileSync(target, 'utf8'), 'instrucción existente\n');
  assert.equal(fs.readFileSync(lock, 'utf8'), 'bloqueo previo');
});
