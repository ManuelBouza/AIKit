const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');

const cli = path.resolve(__dirname, '../dist/cli.js');
function setup(t) {
  const root = path.resolve(__dirname, '../../../.aikit/node-test');
  fs.mkdirSync(root, { recursive: true });
  const dir = fs.mkdtempSync(path.join(root, 'scope-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}
function run(cwd, args, env = {}) {
  return spawnSync(process.execPath, [cli, ...args], { cwd, encoding: 'utf8', env: { ...process.env, ...env } });
}
function repo(dir) {
  const result = spawnSync('git', ['init', '--quiet', dir], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
}

test('proyecto desde subdirectorio conserva texto, respaldo no versionable e idempotencia', t => {
  const dir = setup(t);
  const project = path.join(dir, 'repo');
  repo(project);
  const nested = path.join(project, 'nested');
  fs.mkdirSync(nested);
  const target = path.join(project, 'AGENTS.md');
  fs.writeFileSync(target, 'instrucciones existentes\n');
  const env = { CODEX_HOME: path.join(dir, 'perfil') };
  const preview = run(nested, ['install', '--project', '--dry-run'], env);
  assert.equal(preview.status, 0, preview.stderr);
  assert.equal(JSON.parse(preview.stdout).path, target);
  assert.equal(fs.readFileSync(target, 'utf8'), 'instrucciones existentes\n');
  const install = run(nested, ['install', '--project'], env);
  assert.equal(install.status, 0, install.stderr);
  const info = JSON.parse(install.stdout);
  assert.equal(info.path, target);
  assert.equal(fs.readFileSync(info.backup, 'utf8'), 'instrucciones existentes\n');
  assert.ok(info.backup.startsWith(path.join(project, '.git', 'aikit-backups') + path.sep));
  assert.equal(fs.existsSync(env.CODEX_HOME), false);
  const repeat = run(nested, ['install', '--project'], env);
  assert.equal(repeat.status, 0, repeat.stderr);
  assert.equal(JSON.parse(repeat.stdout).status, 'unchanged');
  const git = spawnSync('git', ['status', '--porcelain', '--untracked-files=all'], { cwd: project, encoding: 'utf8' });
  assert.equal(git.status, 0, git.stderr);
  assert.doesNotMatch(git.stdout, /aikit-backups|original-replacefile/);
});

test('global usa CODEX_HOME sin tocar proyecto', t => {
  const dir = setup(t);
  const project = path.join(dir, 'repo');
  repo(project);
  const profile = path.join(dir, 'profile');
  const result = run(project, ['install', '--global'], { CODEX_HOME: profile });
  assert.equal(result.status, 0, result.stderr);
  assert.equal(JSON.parse(result.stdout).path, path.join(profile, 'AGENTS.md'));
  assert.equal(fs.existsSync(path.join(project, 'AGENTS.md')), false);
});

test('proyecto rechaza override, destino fuera de Git y ámbitos incompatibles', t => {
  const dir = setup(t);
  const project = path.join(dir, 'repo');
  repo(project);
  fs.writeFileSync(path.join(project, 'AGENTS.override.md'), 'override');
  const blocked = run(project, ['install', '--project']);
  assert.notEqual(blocked.status, 0);
  assert.equal(fs.existsSync(path.join(project, 'AGENTS.md')), false);
  const nonRepo = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-nonrepo-'));
  t.after(() => fs.rmSync(nonRepo, { recursive: true, force: true }));
  const outside = run(nonRepo, ['install', '--project']);
  assert.notEqual(outside.status, 0);
  assert.match(outside.stderr, /repositorio Git/);
  for (const args of [['install', '--global', '--project'], ['install', '--project', '--codex-home', dir], ['install']]) {
    assert.notEqual(run(project, args).status, 0);
  }
});
