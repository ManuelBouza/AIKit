const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

// Estas pruebas ejercitan File.Replace directamente, no el instalador.
function runScenario(t, script) {
  if (process.platform !== 'win32') return t.skip('Requiere Windows y PowerShell');
  const root = path.resolve(__dirname, '../../../.aikit/node-test');
  fs.mkdirSync(root, { recursive: true });
  const directory = fs.mkdtempSync(path.join(root, 'reemplazo-á-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  // EncodedCommand evita que las rutas o los contenidos se interpreten como código.
  const command = Buffer.from(`$ErrorActionPreference = 'Stop'\n${script}`, 'utf16le').toString('base64');
  const result = spawnSync('powershell.exe', ['-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', command], {
    env: { ...process.env, AIKIT_TEST_DIRECTORY: directory, AIKIT_TEST_NODE: process.execPath, AIKIT_TEST_CLI: path.resolve(__dirname, '../dist/cli.js') }, encoding: 'utf8', timeout: 30000,
  });
  if (result.error && result.error.code === 'ENOENT') return t.skip('Windows PowerShell no está disponible');
  assert.ifError(result.error);
  assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
}

const setup = String.raw`
$target = Join-Path $env:AIKIT_TEST_DIRECTORY 'AGENTS.md'
$replacement = Join-Path $env:AIKIT_TEST_DIRECTORY 'sustitución.tmp'
$backup = Join-Path $env:AIKIT_TEST_DIRECTORY 'respaldo.md'
[IO.File]::WriteAllText($target, 'anterior')
[IO.File]::WriteAllText($replacement, 'nuevo')
`;

for (const explicit of [false, true]) {
  test(`File.Replace conserva ACL ${explicit ? 'con regla explícita' : 'heredada'} y respaldo en ruta Unicode`, (t) => {
    runScenario(t, `${setup}
${explicit ? String.raw`
$acl = [IO.File]::GetAccessControl($target)
$user = [Security.Principal.WindowsIdentity]::GetCurrent().User
$rule = [Security.AccessControl.FileSystemAccessRule]::new($user, 'Read', 'Allow')
$acl.AddAccessRule($rule)
[IO.File]::SetAccessControl($target, $acl)
` : ''}
$sections = [Security.AccessControl.AccessControlSections]::Access -bor [Security.AccessControl.AccessControlSections]::Owner -bor [Security.AccessControl.AccessControlSections]::Group
$before = [IO.File]::GetAccessControl($target).GetSecurityDescriptorSddlForm($sections)
[IO.File]::Replace($replacement, $target, $backup, $false)
$after = [IO.File]::GetAccessControl($target).GetSecurityDescriptorSddlForm($sections)
if ($before -ne $after) { throw 'Cambió el descriptor de seguridad' }
if ([IO.File]::ReadAllText($target) -ne 'nuevo') { throw 'Contenido inesperado' }
if ([IO.File]::ReadAllText($backup) -ne 'anterior') { throw 'Respaldo inesperado' }
if (Test-Path -LiteralPath $replacement) { throw 'El reemplazo no fue consumido' }
`);
  });
}

test('File.Replace con destino bloqueado falla y conserva ambos archivos', (t) => {
  runScenario(t, `${setup}
$stream = [IO.File]::Open($target, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
$failed = $false
try {
  try { [IO.File]::Replace($replacement, $target, $backup, $false) }
  catch [System.IO.IOException] { $failed = $true }
} finally { $stream.Dispose() }
if (-not $failed) { throw 'Se esperaba fallo por bloqueo' }
if ([IO.File]::ReadAllText($target) -ne 'anterior') { throw 'Original modificado' }
if ([IO.File]::ReadAllText($replacement) -ne 'nuevo') { throw 'Reemplazo modificado' }
if (Test-Path -LiteralPath $backup) { throw 'Respaldo inesperado' }
`);
});

test('instalador conserva bloqueo y temporal cuando destino está bloqueado', (t) => {
  runScenario(t, String.raw`
$target = Join-Path $env:AIKIT_TEST_DIRECTORY 'AGENTS.md'
[IO.File]::WriteAllText($target, 'original')
$stream = [IO.File]::Open($target, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
try {
  $ErrorActionPreference = 'Continue'
  $result = & $env:AIKIT_TEST_NODE $env:AIKIT_TEST_CLI install --codex-home $env:AIKIT_TEST_DIRECTORY 2>&1
  $code = $LASTEXITCODE
  $ErrorActionPreference = 'Stop'
} finally { $stream.Dispose() }
if ($code -eq 0) { throw 'Se esperaba fallo de sustitución' }
if ([IO.File]::ReadAllText($target) -ne 'original') { throw 'Original modificado' }
if (-not (Test-Path -LiteralPath (Join-Path $env:AIKIT_TEST_DIRECTORY '.aikit-instructions.lock'))) { throw 'Bloqueo no conservado' }
$temp = @(Get-ChildItem -LiteralPath $env:AIKIT_TEST_DIRECTORY -Force -Filter '.agents.md.tmp-*')
if ($temp.Count -ne 1) { throw 'Temporal no conservado' }
if (($result | Out-String) -notmatch 'diagnóstico') { throw 'Falta diagnóstico' }
`);
});
