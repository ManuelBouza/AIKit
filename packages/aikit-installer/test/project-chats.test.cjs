const assert = require('node:assert/strict');
const { spawn, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');

const cli = path.resolve(__dirname, '../dist/cli.js');
const first = '00000000-0000-4000-8000-000000000001';
const second = '00000000-0000-4000-8000-000000000002';
const entry = {
  id: first,
  project: 'Proyecto ficticio',
  responsibility: 'Revisar exportaciones',
  state: 'Disponible',
};

function fixture(t) {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-chats-'));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  return directory;
}

function run(root, command, options = [], { input, cwd, preload, succeeds = true, env } = {}) {
  const args = preload ? ['--import', preload, cli] : [cli];
  const result = spawnSync(
    process.execPath,
    [...args, 'project-chats', command, '--root', root, ...options],
    {
      input: input === undefined ? undefined : JSON.stringify(input),
      encoding: 'utf8',
      cwd,
      env,
    },
  );
  assert.equal(result.status === 0, succeeds, result.stderr || result.error?.message);
  return succeeds ? JSON.parse(result.stdout) : result.stderr;
}

function update(root, revision, input, options = [], context = {}) {
  return run(root, 'upsert', ['--expected-revision', String(revision), ...options], {
    ...context,
    input,
  });
}

test('consulta y vista previa sin escritura, alta idempotente y baja con instrucciones intactas', (t) => {
  const root = fixture(t);
  const instructions = path.join(root, 'AGENTS.md');
  const original = Buffer.from('\uFEFF# Instrucción ajena\r\nLínea final');
  fs.writeFileSync(instructions, original);
  assert.equal(run(root, 'status').status, 'disabled');
  const preview = run(root, 'enable', ['--dry-run']);
  assert.equal(preview.inventoryRoot, root);
  assert.equal(preview.before, original.toString('utf8'));
  assert.deepEqual(fs.readdirSync(root), ['AGENTS.md']);
  const enabled = run(root, 'enable');
  assert.equal(enabled.status, 'changed');
  assert.deepEqual(fs.readFileSync(enabled.backup), original);
  assert.equal(fs.readFileSync(instructions, 'utf8'), preview.after);
  assert.equal(run(root, 'enable').status, 'unchanged');
  assert.equal(run(root, 'status').status, 'enabled');
  update(root, 0, entry);
  assert.equal(run(root, 'disable', ['--dry-run']).after, original.toString('utf8'));
  assert.equal(run(root, 'disable').status, 'changed');
  assert.deepEqual(fs.readFileSync(instructions), original);
  assert.equal(run(root, 'list').records[0].id, first);

  run(root, 'enable');
  fs.appendFileSync(instructions, '# Nueva instrucción ajena\n');
  run(root, 'disable');
  assert.deepEqual(
    fs.readFileSync(instructions),
    Buffer.concat([original, Buffer.from('\r\n# Nueva instrucción ajena\n')]),
  );

  assert.match(run('.', 'enable', [], { succeeds: false }), /absoluta/u);
  if (process.platform === 'win32') {
    assert.match(run('\\ruta-relativa-a-unidad', 'enable', [], { succeeds: false }), /absoluta/u);
    assert.match(run('C:ruta-relativa', 'enable', [], { succeeds: false }), /absoluta/u);
  }
  assert.match(
    run(root, 'enable', [], { succeeds: false, env: { ...process.env, CODEX_HOME: root } }),
    /proyecto local/u,
  );
});

test('desactiva el bloque CRLF bajo override y rechaza marcadores cruzados con go', (t) => {
  const root = fixture(t);
  const instructions = path.join(root, 'AGENTS.md');
  const override = path.join(root, 'AGENTS.override.md');
  const foreign = '# Regla de proyecto\r\nRegla antes';
  const following = 'Regla después\r\n';
  fs.writeFileSync(instructions, foreign);
  run(root, 'enable');
  fs.appendFileSync(instructions, following);
  const earlier = fs.readFileSync(instructions, 'utf8');
  fs.writeFileSync(override, '# Override ajeno\r\n');
  assert.equal(run(root, 'status').status, 'shadowed');
  assert.match(run(root, 'enable', [], { succeeds: false }), /override/u);
  const preview = run(root, 'disable', ['--dry-run']);
  assert.equal(preview.after, foreign + '\r\n' + following);
  assert.equal(fs.readFileSync(instructions, 'utf8'), earlier);
  run(root, 'disable');
  assert.equal(fs.readFileSync(instructions, 'utf8'), preview.after);
  assert.equal(fs.readFileSync(override, 'utf8'), '# Override ajeno\r\n');
  const crossed = [
    '<!-- AIKIT:GO:BEGIN -->',
    '<!-- AIKIT:RESPONSABILIDAD-CHATS:BEGIN -->',
    '<!-- AIKIT:GO:END -->',
    '<!-- AIKIT:RESPONSABILIDAD-CHATS:END -->',
  ].join('\r\n');
  fs.writeFileSync(instructions, crossed);
  assert.match(run(root, 'disable', [], { succeeds: false }), /solapados/u);
  assert.equal(fs.readFileSync(instructions, 'utf8'), crossed);
});

function hook(root, source) {
  const preload = path.join(root, 'simular.mjs');
  fs.writeFileSync(
    preload,
    `
import fs from 'node:fs';
import { syncBuiltinESMExports } from 'node:module';
${source}
syncBuiltinESMExports();
`,
  );
  return { preload: require('node:url').pathToFileURL(preload).href };
}

test('bloquea un proyecto que coincide con la ruta real del perfil global', (t) => {
  const root = fixture(t);
  const alias = path.join(root, 'alias-de-perfil');
  const simulated = hook(
    root,
    `
const realpath = fs.realpathSync.native;
fs.realpathSync.native = (file, ...args) => {
  if (file === ${JSON.stringify(alias)}) return ${JSON.stringify(root)};
  return realpath(file, ...args);
};
`,
  );
  assert.match(
    run(root, 'enable', [], {
      ...simulated,
      env: { ...process.env, CODEX_HOME: alias },
      succeeds: false,
    }),
    /proyecto local/u,
  );
  assert.equal(fs.existsSync(path.join(root, 'AGENTS.md')), false);
});

test('status exige que todas las fichas sean legibles y válidas', (t) => {
  const root = fixture(t);
  run(root, 'enable');
  const { path: record } = update(root, 0, entry);
  const simulated = hook(
    root,
    `
const read = fs.readFileSync;
fs.readFileSync = (file, ...args) => {
  if (file === ${JSON.stringify(record)}) {
    throw Object.assign(new Error('Lectura de ficha denegada'), { code: 'EACCES' });
  }
  return read(file, ...args);
};
`,
  );
  const status = run(root, 'status', [], simulated);
  assert.equal(status.inventoryAccess, 'unverified');
  assert.match(status.inventoryError, /Lectura de ficha denegada/u);
  fs.writeFileSync(record, '{}');
  assert.equal(run(root, 'status').inventoryAccess, 'unverified');
});

test('una ficha sin permiso r+ conserva sus bytes y libera el bloqueo', (t) => {
  const root = fixture(t);
  const { path: record } = update(root, 0, entry);
  const bytes = fs.readFileSync(record);
  const simulated = hook(
    root,
    `
const open = fs.openSync;
fs.openSync = (file, flags, ...args) => {
  if (file === ${JSON.stringify(record)} && flags === 'r+') {
    throw Object.assign(new Error('Escritura de ficha denegada'), { code: 'EACCES' });
  }
  return open(file, flags, ...args);
};
`,
  );
  const error = update(root, 1, entry, [], { ...simulated, succeeds: false });
  assert.match(error, /Escritura de ficha denegada/u);
  assert.deepEqual(fs.readFileSync(record), bytes);
  assert.deepEqual(fs.readdirSync(path.dirname(record)), [path.basename(record)]);
});

test('se comprueba la revisión de nuevo una vez adquirido el bloqueo', (t) => {
  const root = fixture(t);
  const initial = update(root, 0, entry);
  const concurrent = JSON.stringify({ ...initial.record, revision: 2 });
  const simulated = hook(
    root,
    `
const open = fs.openSync;
fs.openSync = (file, flags, ...args) => {
  if (file === ${JSON.stringify(initial.path + '.lock')} && flags === 'wx') {
    fs.writeFileSync(${JSON.stringify(initial.path)}, ${JSON.stringify(concurrent)});
  }
  return open(file, flags, ...args);
};
`,
  );
  const error = update(root, 1, { ...entry, state: 'En curso' }, [], {
    ...simulated,
    succeeds: false,
  });
  assert.match(error, /Revisión obsoleta: esperada 1; actual 2/u);
  assert.equal(fs.readFileSync(initial.path, 'utf8'), concurrent);
});

test('la sustitución conserva el modo de la ficha frente a umask en POSIX', (t) => {
  if (process.platform === 'win32') return t.skip('El modo POSIX requiere otro sistema');
  const root = fixture(t);
  const { path: record } = update(root, 0, entry);
  fs.chmodSync(record, 0o640);
  update(root, 1, entry, [], hook(root, 'process.umask(0o077);'));
  assert.equal(fs.statSync(record).mode & 0o777, 0o640);
});

test('la sustitución conserva la ACL explícita de una ficha en Windows', (t) => {
  if (process.platform !== 'win32') return t.skip('La ACL requiere Windows');
  const root = fixture(t);
  const { path: record } = update(root, 0, entry);
  function acl(addRule) {
    const script = String.raw`$ErrorActionPreference = 'Stop'
$file = $env:AIKIT_TEST_RECORD
$acl = [IO.File]::GetAccessControl($file)
if ($env:AIKIT_TEST_SET_RULE -eq '1') {
  $sid = [Security.Principal.SecurityIdentifier]::new('S-1-5-19')
  $rule = [Security.AccessControl.FileSystemAccessRule]::new($sid, 'Read', 'Allow')
  $acl.AddAccessRule($rule)
  [IO.File]::SetAccessControl($file, $acl)
  $acl = [IO.File]::GetAccessControl($file)
}
[Console]::Out.Write($acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access))`;
    const result = spawnSync(
      'powershell.exe',
      [
        '-NoLogo',
        '-NoProfile',
        '-NonInteractive',
        '-EncodedCommand',
        Buffer.from(script, 'utf16le').toString('base64'),
      ],
      {
        env: {
          ...process.env,
          AIKIT_TEST_RECORD: record,
          AIKIT_TEST_SET_RULE: addRule ? '1' : '0',
        },
        encoding: 'utf8',
        timeout: 15000,
      },
    );
    assert.ifError(result.error);
    assert.equal(result.status, 0, result.stderr);
    return result.stdout;
  }
  const inherited = acl(false);
  const explicit = acl(true);
  if (explicit === inherited) return t.skip('El entorno no aplica cambios de ACL explícita');
  update(root, 1, { ...entry, state: 'En curso' });
  assert.equal(acl(false), explicit);
  assert.deepEqual(fs.readdirSync(path.dirname(record)), [path.basename(record)]);
});

test('un fallo de File.Replace conserva los bytes originales y el diagnóstico', (t) => {
  if (process.platform !== 'win32') return t.skip('File.Replace requiere Windows');
  const root = fixture(t);
  const { path: record } = update(root, 0, entry);
  const bytes = fs.readFileSync(record);
  const simulated = hook(
    root,
    `
const child = (await import('node:child_process')).default;
const spawn = child.spawnSync;
child.spawnSync = (file, args, options) => {
  if (options?.env?.AIKIT_REPLACE_DEST === ${JSON.stringify(record)}) {
    return { status: 1, stdout: '{"ok":false,"code":1175}' };
  }
  return spawn(file, args, options);
};
`,
  );
  const error = update(root, 1, entry, [], { ...simulated, succeeds: false });
  assert.match(error, /1175/u);
  assert.deepEqual(fs.readFileSync(record), bytes);
  assert.equal(fs.existsSync(record + '.lock'), true);
});

test('los cinco estados, ID estable, origen y títulos iguales de fichas distintas', (t) => {
  const root = fixture(t);
  const preview = update(root, 0, entry, ['--dry-run']);
  assert.equal(preview.status, 'preview');
  assert.equal(fs.existsSync(path.join(root, '.aikit')), false);
  const added = update(root, 0, entry).record;
  const fork = update(root, 0, { ...entry, id: second, originId: first }).record;
  assert.equal(added.title, fork.title);
  assert.equal(fork.originId, added.id);
  assert.equal(run(root, 'list').records.length, 2);
  let revision = fork.revision;
  for (const state of ['En curso', 'En espera', 'Pausado', 'Cerrado']) {
    const pause = state === 'En espera' || state === 'Pausado';
    const record = update(root, revision, {
      ...entry,
      id: second,
      responsibility: 'Validar un fork',
      state,
      ...(pause ? { reason: 'Falta una decisión', continuation: 'Recibir decisión' } : {}),
    }).record;
    assert.equal(record.revision, revision + 1);
    assert.equal(record.id, second);
    assert.equal(record.originId, first);
    assert.equal(record.title, `[${state}] Proyecto ficticio · Validar un fork`);
    assert.equal(record.state, state);
    assert.equal(new Date(record.updatedAt).toISOString(), record.updatedAt);
    revision = record.revision;
  }
});

test('valida los datos de ficha y rechaza revisión obsoleta sin sobrescribir', (t) => {
  const root = fixture(t);
  for (const input of [
    { ...entry, id: undefined },
    { ...entry, id: 'ID con espacios' },
    { ...entry, state: 'En espera' },
    { ...entry, state: 'Activo' },
    { ...entry, originId: first },
    { ...entry, conversation: 'contenido fuera de esquema' },
  ]) {
    update(root, 0, input, [], { succeeds: false });
  }
  assert.equal(run(root, 'list').records.length, 0);
  update(root, 0, entry);
  const change = { ...entry, state: 'En curso' };
  const applied = update(root, 1, change).record;
  assert.match(
    update(root, 1, { ...entry, state: 'Cerrado' }, [], { succeeds: false }),
    /Revisión obsoleta/u,
  );
  assert.deepEqual(run(root, 'list').records, [applied]);
});

function parallelUpdate(root, expected, input) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [
      cli,
      'project-chats',
      'upsert',
      '--root',
      root,
      '--expected-revision',
      String(expected),
    ]);
    let stderr = '';
    child.stderr.setEncoding('utf8').on('data', (data) => (stderr += data));
    child.stdout.resume();
    child.on('error', reject).on('close', (code) => resolve({ code, stderr }));
    child.stdin.end(JSON.stringify(input));
  });
}

test('escrituras concurrentes conservan altas distintas y rechazan una edición de la misma ficha', async (t) => {
  const root = fixture(t);
  const newWrites = await Promise.all([
    parallelUpdate(root, 0, entry),
    parallelUpdate(root, 0, { ...entry, id: second }),
  ]);
  assert.deepEqual(newWrites, [
    { code: 0, stderr: '' },
    { code: 0, stderr: '' },
  ]);
  const edits = await Promise.all([
    parallelUpdate(root, 1, { ...entry, state: 'En curso' }),
    parallelUpdate(root, 1, { ...entry, state: 'Cerrado' }),
  ]);
  assert.equal(edits.filter((result) => result.code === 0).length, 1);
  assert.match(edits.find((result) => result.code !== 0).stderr, /Revisión obsoleta|otra edición/u);
  assert.deepEqual(
    run(root, 'list')
      .records.map((record) => [record.id, record.revision])
      .sort(),
    [
      [first, 2],
      [second, 1],
    ],
  );
});

function git(cwd, ...args) {
  const result = spawnSync(
    'git',
    [
      '-c',
      'core.hooksPath=.sin-hooks-aikit',
      '-c',
      'user.name=AIKit Tests',
      '-c',
      'user.email=aikit@example.invalid',
      ...args,
    ],
    { cwd, encoding: 'utf8' },
  );
  assert.equal(result.status, 0, result.stderr || result.error?.message);
}

test('worktree real consulta y actualiza la raíz explícita incluso con permisos limitados simulados', (t) => {
  const directory = fixture(t);
  const root = path.join(directory, 'principal');
  const worktree = path.join(directory, 'lateral');
  fs.mkdirSync(root);
  git(root, 'init', '-q');
  git(root, 'commit', '-qm', 'Base ficticia', '--allow-empty');
  git(root, 'worktree', 'add', '-q', '--detach', worktree, 'HEAD');
  const unrelated = path.join(directory, 'independiente');
  fs.mkdirSync(unrelated);
  assert.equal(
    run(worktree, 'enable', ['--inventory-root', unrelated, '--dry-run']).inventoryRoot,
    unrelated,
  );
  run(root, 'enable');
  assert.match(
    run(worktree, 'enable', ['--inventory-root', unrelated], { succeeds: false }),
    /inventario configurada en el checkout principal/u,
  );
  assert.equal(fs.existsSync(path.join(worktree, 'AGENTS.md')), false);
  assert.deepEqual(fs.readdirSync(unrelated), []);
  assert.match(run(worktree, 'enable', [], { succeeds: false }), /raíz de inventario compartida/u);
  run(worktree, 'enable', ['--inventory-root', root], { cwd: worktree });
  assert.equal(run(worktree, 'status', [], { cwd: root }).inventoryRoot, root);
  update(root, 0, entry, [], { cwd: worktree });
  assert.equal(run(root, 'list', [], { cwd: root }).records[0].id, first);
  update(root, 1, { ...entry, state: 'En curso' }, [], { cwd: root });
  assert.equal(run(root, 'list', [], { cwd: worktree }).records[0].state, 'En curso');
  const preload = path.join(directory, 'simular-permiso.mjs');
  fs.writeFileSync(
    preload,
    `
import fs from 'node:fs';
import path from 'node:path';
import { syncBuiltinESMExports } from 'node:module';
const inventory = ${JSON.stringify(path.join(root, '.aikit', 'chats'))};
const denied = () => Object.assign(new Error('EACCES simulado para inventario'), { code: 'EACCES' });
const readdir = fs.readdirSync;
fs.readdirSync = (file, ...args) => {
  if (path.normalize(file) === inventory && process.env.AIKIT_TEST_DENY_READ) throw denied();
  return readdir(file, ...args);
};
const open = fs.openSync;
fs.openSync = (file, flags, ...args) => {
  if (typeof file === 'string' && path.dirname(file) === inventory && flags === 'wx') throw denied();
  return open(file, flags, ...args);
};
syncBuiltinESMExports();
`,
  );
  const limited = { cwd: worktree, preload: require('node:url').pathToFileURL(preload).href };
  assert.equal(run(worktree, 'status', [], limited).inventoryAccess, 'readable');
  assert.equal(run(root, 'list', [], limited).records[0].revision, 2);
  assert.match(update(root, 2, entry, [], { ...limited, succeeds: false }), /EACCES simulado/u);
  const denied = { ...limited, env: { ...process.env, AIKIT_TEST_DENY_READ: '1' } };
  assert.equal(run(worktree, 'status', [], denied).inventoryAccess, 'unverified');
  assert.match(run(root, 'list', [], { ...denied, succeeds: false }), /EACCES simulado/u);
  assert.equal(run(root, 'list').records[0].revision, 2);
  assert.equal(fs.existsSync(path.join(worktree, '.aikit', 'chats')), false);
});
