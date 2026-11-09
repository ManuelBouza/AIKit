const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const { pathToFileURL } = require('node:url');

const cli = path.resolve(__dirname, '../dist/cli.js');
function profile(t) {
  const root = path.resolve(__dirname, '../../../.aikit/node-test');
  fs.mkdirSync(root, { recursive: true });
  const home = fs.mkdtempSync(path.join(root, 'perfil-á & '));
  t.after(() => fs.rmSync(home, { recursive: true, force: true }));
  return home;
}

for (const [code, destinationPresent, backupPresent, expected] of [
  [1175, true, false, 'expected-original-paths'],
  [1176, true, false, 'expected-original-paths'],
  [1177, false, true, 'expected-backup-path'],
  [1177, true, false, 'unverified'],
]) {
  test(`diagnóstico integrado simula fallo ${code} y conserva las rutas`, async (t) => {
    const home = profile(t);
    const paths = { destination: path.join(home, 'AGENTS.md'), replacement: path.join(home, 'temporal'), backup: path.join(home, 'respaldo') };
    if (destinationPresent) fs.writeFileSync(paths.destination, 'original');
    if (backupPresent) fs.writeFileSync(paths.backup, 'original');
    fs.writeFileSync(paths.replacement, 'nuevo');
    const before = fs.readdirSync(home).sort().map(file => [file, fs.readFileSync(path.join(home, file), 'utf8')]);
    const { replaceWindows } = await import(pathToFileURL(path.resolve(__dirname, '../dist/windows-replace.js')).href);
    let calls = 0;
    const report = replaceWindows(paths, received => { calls++; assert.deepEqual(received, paths); return { ok: false, code }; });
    assert.equal(calls, 1);
    assert.equal(report.classification, expected);
    assert.equal(report.action, 'preserve-and-inspect');
    assert.deepEqual(report.paths, {
      destination: { path: paths.destination, exists: destinationPresent },
      replacement: { path: paths.replacement, exists: true },
      backup: { path: paths.backup, exists: backupPresent },
    });
    assert.deepEqual(fs.readdirSync(home).sort().map(file => [file, fs.readFileSync(path.join(home, file), 'utf8')]), before);
  });
}

test('un fallo no verificable no borra ni reintenta', async (t) => {
  const home = profile(t);
  const paths = { destination: path.join(home, 'AGENTS.md'), replacement: path.join(home, 'temporal'), backup: path.join(home, 'respaldo') };
  fs.writeFileSync(paths.destination, 'original');
  fs.writeFileSync(paths.replacement, 'nuevo');
  const { replaceWindows } = await import(pathToFileURL(path.resolve(__dirname, '../dist/windows-replace.js')).href);
  let calls = 0;
  const report = replaceWindows(paths, () => { calls++; throw new Error('fallo ficticio'); });
  assert.equal(calls, 1);
  assert.equal(report.code, null);
  assert.equal(report.classification, 'unverified');
  assert.equal(fs.readFileSync(paths.destination, 'utf8'), 'original');
  assert.equal(fs.readFileSync(paths.replacement, 'utf8'), 'nuevo');
});

function acl(home, addRule = false) {
  const script = String.raw`$ErrorActionPreference = 'Stop'
$file = Join-Path $env:AIKIT_TEST_HOME 'AGENTS.md'
if ($env:AIKIT_TEST_ADD_RULE -eq '1') {
  $acl = [IO.File]::GetAccessControl($file)
  $user = [Security.Principal.WindowsIdentity]::GetCurrent().User
  $rule = [Security.AccessControl.FileSystemAccessRule]::new($user, 'Read', 'Allow')
  $acl.AddAccessRule($rule)
  [IO.File]::SetAccessControl($file, $acl)
}
$sections = [Security.AccessControl.AccessControlSections]::Access -bor [Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group
[Console]::Out.Write([IO.File]::GetAccessControl($file).GetSecurityDescriptorSddlForm($sections))`;
  const encoded = Buffer.from(script, 'utf16le').toString('base64');
  const result = spawnSync('powershell.exe', ['-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], {
    env: { ...process.env, AIKIT_TEST_HOME: home, AIKIT_TEST_ADD_RULE: addRule ? '1' : '0' }, encoding: 'utf8', timeout: 30000,
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

for (const explicit of [false, true]) {
  test(`instalador conserva ACL ${explicit ? 'explícita' : 'heredada'} en ruta Unicode y respalda contenido`, (t) => {
    if (process.platform !== 'win32') return t.skip('Requiere Windows');
    const home = profile(t);
    const target = path.join(home, 'AGENTS.md');
    const before = Buffer.from('# Preferencias personales\r\nContenido previo.\r\n');
    fs.writeFileSync(target, before);
    const originalAcl = acl(home, explicit);
    const result = spawnSync(process.execPath, [cli, 'install', '--codex-home', home], { encoding: 'utf8', timeout: 30000 });
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    const output = JSON.parse(result.stdout);
    assert.equal(output.status, 'changed');
    assert.deepEqual(fs.readFileSync(output.backup), before);
    assert.equal(acl(home), originalAcl);
    assert.match(fs.readFileSync(target, 'utf8'), /AIKIT:GO:BEGIN/);
  });
}
