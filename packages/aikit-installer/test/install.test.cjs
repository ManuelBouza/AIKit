const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const cli = path.resolve(__dirname, '..', 'dist', 'cli.js');
const packageRoot = path.resolve(__dirname, '..');
const repositoryRoot = path.resolve(packageRoot, '..', '..');

function fixture(t) {
  const root = path.resolve(__dirname, '..', '..', '..', '.aikit', 'node-test');
  fs.mkdirSync(root, { recursive: true });
  const dir = fs.mkdtempSync(path.join(root, 'profile-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function run(home, ...args) {
  const result = spawnSync(process.execPath, [cli, 'install', '--codex-home', home, ...args], {
    encoding: 'utf8',
  });
  assert.ifError(result.error);
  return result;
}

function status(home) {
  return spawnSync(process.execPath, [cli, 'status', '--codex-home', home], { encoding: 'utf8' });
}

test('las plantillas empaquetadas coinciden con las fuentes canónicas', () => {
  for (const name of ['go.md', 'context7.md', 'investigacion.md', 'escritura.md', 'visualizacion.md']) {
    assert.deepEqual(fs.readFileSync(path.join(packageRoot, 'templates', name)),
      fs.readFileSync(path.join(repositoryRoot, 'config', 'codex', name)));
  }
});

test('status identifica versión aplicada y detecta divergencias sin escribir', (t) => {
  const home = fixture(t);
  const before = status(home);
  assert.equal(before.status, 0, before.stderr);
  assert.equal(JSON.parse(before.stdout).installedVersion, null);
  const installed = run(home);
  assert.equal(installed.status, 0, installed.stderr);
  const info = JSON.parse(installed.stdout);
  const file = path.join(home, 'AGENTS.md');
  const data = fs.readFileSync(file, 'utf8');
  assert.ok(data.includes(`<!-- AIKIT:VERSION:${info.version} -->`));
  const current = status(home);
  assert.equal(current.status, 0, current.stderr);
  assert.equal(JSON.parse(current.stdout).status, 'current');
  assert.equal(JSON.parse(current.stdout).installedVersion, info.version);
  assert.equal(fs.readFileSync(file, 'utf8'), data);
  const altered = data.replace('<!-- AIKIT:CONTEXT7:BEGIN -->', '<!-- AIKIT:CONTEXT7:BEGIN -->\nCambio local');
  fs.writeFileSync(file, altered);
  const different = status(home);
  assert.equal(different.status, 0, different.stderr);
  assert.equal(JSON.parse(different.stdout).status, 'different');
  assert.equal(fs.readFileSync(file, 'utf8'), altered);
});

test('vista previa, instalación y repetición conservan contenido y respaldo', (t) => {
  const home = fixture(t);
  const file = path.join(home, 'AGENTS.md');
  const original = Buffer.from('\ufeff# Preferencias personales\r\nTexto ajeno.\r\n');
  fs.writeFileSync(file, original);
  const preview = run(home, '--dry-run');
  assert.equal(preview.status, 0, preview.stderr);
  const plan = JSON.parse(preview.stdout);
  assert.equal(plan.status, 'preview');
  assert.equal(path.resolve(plan.path), file);
  assert.match(plan.after, /AIKIT:GO:BEGIN/);
  assert.match(plan.after, /AIKIT:CONTEXT7:BEGIN/);
  assert.match(plan.after, /AIKIT:INVESTIGACION:BEGIN/);
  assert.deepEqual(fs.readFileSync(file), original);

  const install = run(home);
  assert.equal(install.status, 0, install.stderr);
  const applied = JSON.parse(install.stdout);
  assert.equal(applied.status, 'changed');
  assert.ok(applied.version);
  assert.deepEqual(fs.readFileSync(applied.backup), original);
  const contents = fs.readFileSync(file);
  assert.ok(contents.subarray(0, original.length).equals(original));
  assert.match(contents.toString('utf8'), /AIKIT:GO:BEGIN/);
  assert.match(contents.toString('utf8'), /AIKIT:CONTEXT7:BEGIN/);
  assert.match(contents.toString('utf8'), /AIKIT:INVESTIGACION:BEGIN/);

  const repeat = run(home);
  assert.equal(repeat.status, 0, repeat.stderr);
  assert.equal(JSON.parse(repeat.stdout).status, 'unchanged');
  assert.deepEqual(fs.readFileSync(file), contents);
});

test('actualiza ambos bloques anteriores conservando el texto externo', (t) => {
  const home = fixture(t);
  const file = path.join(home, 'AGENTS.md');
  fs.writeFileSync(file, 'Antes\n<!-- AIKIT:GO:BEGIN -->\nantiguo go\n<!-- AIKIT:GO:END -->\nCentro\n<!-- AIKIT:CONTEXT7:BEGIN -->\nantiguo context7\n<!-- AIKIT:CONTEXT7:END -->\nDespués\n');
  const original = fs.readFileSync(file);
  const result = run(home);
  assert.equal(result.status, 0, result.stderr);
  const applied = JSON.parse(result.stdout);
  assert.equal(applied.status, 'changed');
  assert.deepEqual(fs.readFileSync(applied.backup), original);
  const text = fs.readFileSync(file, 'utf8');
  assert.match(text, /^Antes\n/);
  assert.match(text, /\nCentro\n/);
  assert.match(text, /\nDespués\n<!-- AIKIT:INVESTIGACION:BEGIN -->/);
  assert.doesNotMatch(text, /antiguo go|antiguo context7/);
  assert.match(text, /AIKIT:INVESTIGACION:BEGIN/);
});

test('rechaza bloques de investigación anidados sin modificar el destino', (t) => {
  const home = fixture(t);
  const file = path.join(home, 'AGENTS.md');
  const original = '<!-- AIKIT:INVESTIGACION:BEGIN -->\n<!-- AIKIT:GO:BEGIN -->\n<!-- AIKIT:INVESTIGACION:END -->\n<!-- AIKIT:GO:END -->\n';
  fs.writeFileSync(file, original);
  const result = run(home);
  assert.notEqual(result.status, 0);
  assert.equal(fs.readFileSync(file, 'utf8'), original);
});

test('crea perfil inexistente y registra que no había archivo previo', (t) => {
  const parent = fixture(t);
  const home = path.join(parent, 'nuevo');
  const result = run(home);
  assert.equal(result.status, 0, result.stderr);
  const applied = JSON.parse(result.stdout);
  assert.equal(applied.status, 'changed');
  assert.ok(fs.existsSync(applied.backup));
  assert.match(fs.readFileSync(path.join(home, 'AGENTS.md'), 'utf8'), /AIKIT:CONTEXT7:BEGIN/);
});

for (const [name, content, override] of [
  ['marcador incompleto', '<!-- AIKIT:GO:BEGIN -->\n sin cierre', null],
  ['marcador duplicado', '<!-- AIKIT:GO:BEGIN -->\na\n<!-- AIKIT:GO:END -->\n<!-- AIKIT:GO:BEGIN -->\nb\n<!-- AIKIT:GO:END -->', null],
  ['bloques solapados', '<!-- AIKIT:GO:BEGIN -->\n<!-- AIKIT:CONTEXT7:BEGIN -->\n<!-- AIKIT:GO:END -->\n<!-- AIKIT:CONTEXT7:END -->', null],
  ['override global', 'contenido ajeno', 'instrucción activa'],
]) {
  test(`rechaza ${name} sin modificar instrucciones`, (t) => {
    const home = fixture(t);
    const file = path.join(home, 'AGENTS.md');
    fs.writeFileSync(file, content);
    if (override !== null) fs.writeFileSync(path.join(home, 'AGENTS.override.md'), override);
    const before = fs.readFileSync(file);
    const result = run(home);
    assert.notEqual(result.status, 0);
    assert.deepEqual(fs.readFileSync(file), before);
  });
}

test('rechaza un AGENTS.md enlazado sin modificar el destino', (t) => {
  const parent = fixture(t);
  const home = path.join(parent, 'profile');
  fs.mkdirSync(home);
  const target = path.join(parent, 'target.md');
  fs.writeFileSync(target, 'contenido protegido');
  try {
    fs.symlinkSync(target, path.join(home, 'AGENTS.md'), 'file');
  } catch (error) {
    if (['EPERM', 'EACCES', 'ENOSYS'].includes(error.code)) return t.skip('No se pueden crear symlinks en este entorno');
    throw error;
  }
  const result = run(home);
  assert.notEqual(result.status, 0);
  assert.equal(fs.readFileSync(target, 'utf8'), 'contenido protegido');
});

function junction(t, target, link) {
  if (process.platform !== 'win32') {
    t.skip('Las junctions se prueban en Windows');
    return false;
  }
  try {
    fs.symlinkSync(target, link, 'junction');
    return true;
  } catch (error) {
    if (['EPERM', 'EACCES', 'ENOSYS'].includes(error.code)) {
      t.skip('No se pueden crear junctions en este entorno');
      return false;
    }
    throw error;
  }
}

test('rechaza un perfil situado en una junction real de Windows', (t) => {
  const parent = fixture(t);
  const target = path.join(parent, 'destino');
  const link = path.join(parent, 'junction');
  fs.mkdirSync(target);
  const file = path.join(target, 'AGENTS.md');
  fs.writeFileSync(file, 'instrucción protegida');
  if (!junction(t, target, link)) return;
  const result = run(link);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /junction|enlace/i);
  assert.equal(fs.readFileSync(file, 'utf8'), 'instrucción protegida');
  assert.equal(fs.existsSync(path.join(target, 'backups')), false);
});

test('rechaza una junction real en el directorio de respaldos', (t) => {
  const parent = fixture(t);
  const home = path.join(parent, 'perfil');
  const target = path.join(parent, 'respaldos-ajenos');
  fs.mkdirSync(home);
  fs.mkdirSync(target);
  const file = path.join(home, 'AGENTS.md');
  fs.writeFileSync(file, 'instrucción protegida');
  if (!junction(t, target, path.join(home, 'backups'))) return;
  const result = run(home);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /junction|enlace/i);
  assert.equal(fs.readFileSync(file, 'utf8'), 'instrucción protegida');
  assert.deepEqual(fs.readdirSync(target), []);
  assert.deepEqual(fs.readdirSync(home).sort(), ['AGENTS.md', 'backups']);
});

test('selecciona preferencias por opción y conserva los bloques no seleccionados', (t) => {
  const home = fixture(t), file = path.join(home, 'AGENTS.md');
  const previous = '<!-- AIKIT:GO:BEGIN -->\nAnterior\n<!-- AIKIT:GO:END -->';
  fs.writeFileSync(file, `Propio\n${previous}\n`);
  const preview = run(home, '--escritura', '--visualizacion', '--dry-run');
  assert.equal(preview.status, 0, preview.stderr);
  const plan = JSON.parse(preview.stdout);
  assert.ok(plan.after.includes(previous));
  for (const name of ['ESCRITURA', 'VISUALIZACION']) assert.ok(plan.after.includes(`AIKIT:${name}:BEGIN`));
  for (const name of ['CONTEXT7', 'INVESTIGACION']) assert.ok(!plan.after.includes(`AIKIT:${name}:BEGIN`));
  const installed = run(home, '--escritura', '--visualizacion');
  assert.equal(installed.status, 0, installed.stderr);
  assert.equal(fs.readFileSync(file, 'utf8'), plan.after);
  assert.equal(JSON.parse(run(home, '--escritura', '--visualizacion').stdout).status, 'unchanged');
});

for (const [option, name] of [['--go', 'GO'], ['--context7', 'CONTEXT7'], ['--investigacion', 'INVESTIGACION'], ['--escritura', 'ESCRITURA'], ['--visualizacion', 'VISUALIZACION']]) {
  test(`selección independiente ${option}`, (t) => {
    const home = fixture(t);
    const result = run(home, option, '--dry-run');
    assert.equal(result.status, 0, result.stderr);
    const after = JSON.parse(result.stdout).after;
    for (const candidate of ['GO', 'CONTEXT7', 'INVESTIGACION', 'ESCRITURA', 'VISUALIZACION']) {
      assert.equal(after.includes(`AIKIT:${candidate}:BEGIN`), candidate === name);
    }
  });
}

for (const content of [
  '<!-- AIKIT:ESCRITURA:BEGIN -->\na\n<!-- AIKIT:ESCRITURA:END -->\n<!-- AIKIT:ESCRITURA:BEGIN -->\nb\n<!-- AIKIT:ESCRITURA:END -->',
  '<!-- AIKIT:VISUALIZACION:BEGIN -->\n<!-- AIKIT:GO:BEGIN -->\n<!-- AIKIT:VISUALIZACION:END -->\n<!-- AIKIT:GO:END -->',
  '<!-- AIKIT:VISUALIZACION:END -->',
]) {
  test('rechaza marcadores de preferencias inválidos', (t) => {
    const home = fixture(t), file = path.join(home, 'AGENTS.md');
    fs.writeFileSync(file, content);
    assert.notEqual(run(home).status, 0);
    assert.equal(fs.readFileSync(file, 'utf8'), content);
    assert.equal(fs.existsSync(path.join(home, 'backups')), false);
  });
}

test('instala opciones en un proyecto ficticio', (t) => {
  const project = fixture(t);
  const init = spawnSync('git', ['init', '-q', project], { encoding: 'utf8' });
  assert.equal(init.status, 0, init.stderr);
  const invoke = (...args) => spawnSync(process.execPath, [cli, 'install', '--project', ...args], { cwd: project, encoding: 'utf8' });
  const preview = invoke('--escritura', '--visualizacion', '--dry-run');
  assert.equal(preview.status, 0, preview.stderr);
  assert.equal(fs.existsSync(path.join(project, 'AGENTS.md')), false);
  const result = invoke('--escritura', '--visualizacion');
  assert.equal(result.status, 0, result.stderr);
  const contents = fs.readFileSync(path.join(project, 'AGENTS.md'), 'utf8');
  assert.match(contents, /AIKIT:ESCRITURA:BEGIN/);
  assert.match(contents, /AIKIT:VISUALIZACION:BEGIN/);
  assert.equal(JSON.parse(invoke('--escritura', '--visualizacion').stdout).status, 'unchanged');
});


test('permite elegir preferencias diferentes por ámbito', (t) => {
  const home = fixture(t), project = fixture(t);
  assert.equal(spawnSync('git', ['init', '-q', project]).status, 0);
  const global = run(home, '--go');
  assert.equal(global.status, 0, global.stderr);
  const local = spawnSync(process.execPath, [cli, 'install', '--project', '--escritura'], { cwd: project, encoding: 'utf8' });
  assert.equal(local.status, 0, local.stderr);
  const globalText = fs.readFileSync(path.join(home, 'AGENTS.md'), 'utf8');
  const projectText = fs.readFileSync(path.join(project, 'AGENTS.md'), 'utf8');
  assert.match(globalText, /AIKIT:GO:BEGIN/);
  assert.doesNotMatch(globalText, /AIKIT:ESCRITURA:BEGIN/);
  assert.match(projectText, /AIKIT:ESCRITURA:BEGIN/);
  assert.doesNotMatch(projectText, /AIKIT:GO:BEGIN/);
});

test('sin selección conserva las tres preferencias históricas', (t) => {
  const home = fixture(t);
  const preview = run(home, '--dry-run');
  assert.equal(preview.status, 0, preview.stderr);
  const after = JSON.parse(preview.stdout).after;
  for (const name of ['GO', 'CONTEXT7', 'INVESTIGACION']) assert.match(after, new RegExp(`AIKIT:${name}:BEGIN`));
  for (const name of ['ESCRITURA', 'VISUALIZACION']) assert.doesNotMatch(after, new RegExp(`AIKIT:${name}:BEGIN`));
});
