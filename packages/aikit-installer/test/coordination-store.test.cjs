const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { randomUUID } = require('node:crypto');
const { spawnSync, spawn } = require('node:child_process');
const { once } = require('node:events');
const { syncBuiltinESMExports } = require('node:module');

test('referencias son texto literal y derivados exactos solo incluyen avisos aplicados', async (t) => {
  const f = await fixture(t);
  f.store.createTask('T-002', 'tarea', 'prueba');
  const refs = [
    '![imagen](https://example.test/pixel)',
    '[enlace](https://example.test/)',
    '<img src="https://example.test/x">',
    '`````',
    'línea\notra',
  ];
  f.store.apply(f.n(2, { references: refs }), 'aplicado');
  f.store.apply(f.n(1, { references: ['antiguo excluido'] }), 'antiguo');
  f.store.apply(f.n(3, { senderChatId: 'ajeno', references: ['pendiente excluido'] }), 'pendiente');
  f.store.apply(f.n(1, { taskId: 'T-002', references: ['segunda tarea'] }), 'aplicado');
  f.store.rebuildIndex();
  assert.equal(
    fs.readFileSync(path.join(f.root, 'coordinacion/INDICE.md'), 'utf8'),
    '# Tareas\n\n- [T-001](T-001/TAREA.md)\n- [T-002](T-002/TAREA.md)\n',
  );
  assert.equal(
    fs.readFileSync(path.join(f.root, 'coordinacion/T-001/ENTREGAS.md'), 'utf8'),
    '# Entregas\n\n``````json\n' + JSON.stringify(refs) + '\n``````\n',
  );
  assert.equal(
    fs.readFileSync(path.join(f.root, 'coordinacion/T-002/ENTREGAS.md'), 'utf8'),
    '# Entregas\n\n```json\n["segunda tarea"]\n```\n',
  );
});
test('rechazos conocidos liberan solo su bloqueo y permiten continuar', async (t) => {
  const f = await fixture(t);
  const lock = path.join(f.root, 'coordinacion/.control/escritura.lock');
  const operations = path.join(f.root, 'coordinacion/.control/operaciones');
  const before = fs.readdirSync(operations);
  assert.throws(() => f.store.createTask('T-001', 'otra', 'prueba'), /ya existente/);
  assert.equal(fs.existsSync(lock), false);
  assert.throws(() => f.store.apply(f.n(1, { taskId: 'T-999' }), 'prueba'), /no existente/);
  assert.equal(fs.existsSync(lock), false);
  assert.deepEqual(fs.readdirSync(operations), before);
  assert.equal(f.store.apply(f.n(), 'prueba').result, 'aplicado');
});
test('padres internos y lock deben superar política antes de mutar', async (t) => {
  for (const relative of [
    'coordinacion',
    'coordinacion/.control',
    'coordinacion/.control/operaciones',
    'coordinacion/.control/escritura.lock',
  ]) {
    const f = await fixture(t);
    const denied = path.join(f.root, relative);
    const file = path.join(f.root, 'coordinacion/T-001/TAREA.md');
    const before = fs.readFileSync(file);
    let checked = false;
    const store = new f.CoordinationStore({
      ...f.options,
      permissions: {
        inspect() {
          return 'acl-prueba';
        },
        verifyRoot(file) {
          if (file === denied) {
            checked = true;
            throw new Error('política insegura');
          }
        },
      },
    });
    assert.throws(() => store.apply(f.n(), 'prueba'), /política insegura/);
    assert.equal(checked, true);
    assert.deepEqual(fs.readFileSync(file), before);
    if (relative.endsWith('lock')) assert.ok(fs.existsSync(denied));
  }
});
test('modo POSIX incompatible se rechaza antes de rename y conserva bytes', async (t) => {
  const permissions = {
    verifyRoot() {},
    inspect(file) {
      return file.endsWith('.tmp') ? '384' : '256';
    },
  };
  const f = await fixture(t, { platform: 'linux', permissions });
  const file = path.join(f.root, 'coordinacion/T-001/TAREA.md');
  const before = fs.readFileSync(file);
  assert.throws(() => f.store.apply(f.n(), 'prueba'), /Modo POSIX incompatible antes de publicar/);
  assert.deepEqual(fs.readFileSync(file), before);
  assert.equal(f.store.query('T-001', randomUUID()).result, 'incierto');
});
test(
  'base POSIX real 0400 no se sustituye por temporal 0600',
  { skip: process.platform === 'win32' ? 'Requiere modos POSIX reales' : false },
  async (t) => {
    const { nativePermissions } = await import('../dist/coordination/store.js');
    const f = await fixture(t, { permissions: nativePermissions });
    const file = path.join(f.root, 'coordinacion/T-001/TAREA.md');
    fs.chmodSync(file, 0o400);
    const before = fs.readFileSync(file);
    assert.throws(
      () => f.store.apply(f.n(), 'prueba'),
      /Modo POSIX incompatible antes de publicar/,
    );
    assert.deepEqual(fs.readFileSync(file), before);
    assert.equal(fs.statSync(file).mode & 0o777, 0o400);
  },
);
test(
  'consulta ACL acota espera y timeout no permite crear datos',
  { skip: process.platform !== 'win32' },
  async (t) => {
    const { CoordinationStore } = await import('../dist/coordination/store.js');
    const cp = require('node:child_process');
    let received;
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-acl-timeout-'));
    t.after(() => fs.rmSync(root, { recursive: true, force: true }));
    const mock = t.mock.method(cp, 'spawnSync', (_exe, _args, options) => {
      received = options;
      return {
        status: null,
        error: Object.assign(new Error('timeout de ACL'), { code: 'ETIMEDOUT' }),
        stdout: '',
        stderr: '',
      };
    });
    syncBuiltinESMExports();
    try {
      assert.throws(
        () =>
          new CoordinationStore({
            root,
            projectId: randomUUID(),
            coordinatorChatId: 'prueba',
            ownerEpoch: 1,
          }),
        /ACL no verificable.*timeout/,
      );
      assert.equal(received.timeout, 15000);
      assert.deepEqual(fs.readdirSync(root), []);
    } finally {
      mock.mock.restore();
      syncBuiltinESMExports();
    }
  },
);
for (const redirected of ['root', 'subdirectory'])
  test(`rechaza ${redirected} con junction/enlace real y conserva destino externo`, async (t) => {
    const f = await fixture(t);
    const external = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-external-'));
    t.after(() => fs.rmSync(external, { recursive: true, force: true }));
    const sentinel = path.join(external, 'intacto.txt');
    fs.writeFileSync(sentinel, 'datos externos');
    const link =
      redirected === 'root'
        ? path.join(f.root, 'raiz-enlazada')
        : path.join(f.root, 'coordinacion/T-002');
    try {
      fs.symlinkSync(external, link, process.platform === 'win32' ? 'junction' : 'dir');
    } catch (error) {
      if (['EPERM', 'EACCES', 'ENOTSUP'].includes(error.code)) {
        t.skip(
          'El entorno no permite crear junction/enlace real; ejecutar esta prueba fuera del sandbox',
        );
        return;
      }
      throw error;
    }
    assert.equal(fs.lstatSync(link).isSymbolicLink(), true);
    if (redirected === 'root')
      assert.throws(
        () => new f.CoordinationStore({ ...f.options, root: link }),
        /Enlaces|redirigida/,
      );
    else assert.throws(() => f.store.createTask('T-003', 'otra', 'prueba'), /Enlaces|redirigida/);
    assert.deepEqual(fs.readdirSync(external), ['intacto.txt']);
    assert.equal(fs.readFileSync(sentinel, 'utf8'), 'datos externos');
    fs.unlinkSync(link);
  });

async function fixture(t, extra = {}) {
  const { CoordinationStore } = await import('../dist/coordination/store.js');
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-coordination-'));
  fs.chmodSync(root, 0o700);
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  // Adaptador controlado: comprueba el protocolo, sin acreditar ACL reales de Windows.
  const permissions = {
    verifyRoot() {},
    inspect() {
      return 'acl-prueba';
    },
  };
  const options = {
    root,
    projectId: randomUUID(),
    coordinatorChatId: 'coordinador',
    ownerEpoch: 1,
    permissions,
    ...extra,
  };
  const store = new CoordinationStore(options);
  store.activate('prueba');
  store.createTask('T-001', 'tarea', 'prueba');
  const n = (revision = 1, patch = {}) => ({
    schemaVersion: 1,
    projectId: options.projectId,
    taskId: 'T-001',
    cycle: 1,
    senderChatId: 'tarea',
    updateId: randomUUID(),
    revision,
    state: 'En curso',
    summary: 'Prueba',
    references: ['referencia'],
    corrects: null,
    ...patch,
  });
  return { store, options, root, n, CoordinationStore };
}
function unlock(root) {
  const lock = path.join(root, 'coordinacion/.control/escritura.lock');
  fs.renameSync(lock, lock + '.supervisado-' + randomUUID());
}
test('aplicado, duplicado, antiguo, pendiente y conflicto conservan original tras reapertura', async (t) => {
  const f = await fixture(t);
  const a = f.n(3);
  assert.equal(f.store.apply(a, 'prueba').result, 'aplicado');
  assert.equal(f.store.apply(a, 'prueba').result, 'duplicado');
  assert.equal(f.store.apply(f.n(1), 'prueba').result, 'antiguo');
  assert.equal(f.store.apply(f.n(5, { senderChatId: 'ajeno' }), 'prueba').result, 'pendiente');
  assert.equal(f.store.apply(f.n(5, { cycle: 2 }), 'prueba').result, 'pendiente');
  assert.equal(f.store.apply({ ...a, summary: 'contradicción' }, 'prueba').result, 'conflicto');
  assert.equal(f.store.apply(f.n(3), 'prueba').result, 'conflicto');
  const reopened = new f.CoordinationStore(f.options);
  assert.equal(reopened.query('T-001', a.updateId).receipt.notice.summary, 'Prueba');
  assert.equal(reopened.query('T-001', randomUUID()).result, 'incierto');
  f.store.rebuildIndex();
  fs.unlinkSync(path.join(f.root, 'coordinacion/INDICE.md'));
  assert.equal(reopened.query('T-001', a.updateId).result, 'aplicado');
  f.store.rebuildIndex();
});
test('colisión entre tareas produce incidente sin otro recibo', async (t) => {
  const f = await fixture(t);
  f.store.createTask('T-002', 'otra', 'prueba');
  const n = f.n();
  f.store.apply(n, 'prueba');
  const result = f.store.apply({ ...n, taskId: 'T-002', senderChatId: 'otra' }, 'prueba');
  assert.equal(result.result, 'conflicto');
  assert.equal(result.receipt, null);
  assert.equal(f.store.query('T-001', n.updateId).result, 'aplicado');
});
for (const phase of [
  'operation-directory',
  'base',
  'proposal',
  'manifest',
  'ready',
  'temporary',
  'published',
  'verified',
  'completed',
]) {
  test(`interrupción en ${phase} preserva evidencia y bloqueo`, async (t) => {
    const f = await fixture(t);
    const n = f.n();
    const broken = new f.CoordinationStore({
      ...f.options,
      fault(p) {
        if (p === phase) throw new Error('interrupción');
      },
    });
    assert.throws(() => broken.apply(n, 'prueba'), /interrupción/);
    assert.ok(fs.existsSync(path.join(f.root, 'coordinacion/.control/escritura.lock')));
    assert.throws(() => f.store.apply(n, 'prueba'), /Bloqueo/);
    unlock(f.root);
    if (['operation-directory', 'base', 'proposal', 'manifest', 'temporary'].includes(phase)) {
      assert.throws(() => f.store.recover());
      assert.ok(fs.existsSync(path.join(f.root, 'coordinacion/.control/escritura.lock')));
    } else {
      f.store.recover();
      assert.equal(f.store.query('T-001', n.updateId).result, 'aplicado');
      assert.equal(f.store.apply(n, 'prueba').result, 'duplicado');
    }
  });
}
test('bloqueo vacío, documento inválido y epoch ajeno no se aceptan', async (t) => {
  const f = await fixture(t);
  const lock = path.join(f.root, 'coordinacion/.control/escritura.lock');
  fs.writeFileSync(lock, '');
  assert.throws(() => f.store.apply(f.n(), 'prueba'), /Bloqueo/);
  fs.unlinkSync(lock);
  const file = path.join(f.root, 'coordinacion/T-001/TAREA.md');
  const original = fs.readFileSync(file);
  fs.writeFileSync(file, 'inválido');
  const response = f.store.query('T-001', randomUUID());
  assert.equal(response.result, 'incierto');
  assert.equal(response.receipt, null);
  assert.throws(() => f.store.apply(f.n(), 'prueba'));
  assert.equal(fs.readFileSync(file, 'utf8'), 'inválido');
  fs.writeFileSync(file, original);
  assert.throws(() => new f.CoordinationStore({ ...f.options, ownerEpoch: 2 }));
  assert.throws(() => new f.CoordinationStore({ ...f.options, root: 'relative' }));
});
test('fallo de sustitución conserva diario sin reintento ni restauración', async (t) => {
  const f = await fixture(t);
  let calls = 0;
  const store = new f.CoordinationStore({
    ...f.options,
    platform: 'win32',
    replaceRunner() {
      calls++;
      return { ok: false, code: 1177 };
    },
  });
  const n = f.n();
  assert.throws(() => store.apply(n, 'prueba'), /Sustitución incierta/);
  assert.equal(calls, 1);
  assert.equal(f.store.query('T-001', n.updateId).result, 'incierto');
});
test('segundo proceso no adquiere bloqueo existente', async (t) => {
  const f = await fixture(t);
  const lock = path.join(f.root, 'coordinacion/.control/escritura.lock');
  fs.writeFileSync(lock, '');
  const url = require('node:url').pathToFileURL(
    path.resolve(__dirname, '../dist/coordination/store.js'),
  ).href;
  const code = `import {CoordinationStore} from ${JSON.stringify(url)}; const options=JSON.parse(process.env.TEST_OPTIONS); options.permissions={verifyRoot(){},inspect(){return 'test'}}; try {new CoordinationStore(options).createTask('T-002','otra','prueba');process.exitCode=2;}catch(e){if(!e.message.includes('Bloqueo'))throw e;console.log('bloqueado');}`;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', code], {
    env: { ...process.env, TEST_OPTIONS: JSON.stringify({ ...f.options, permissions: undefined }) },
    encoding: 'utf8',
    timeout: 15000,
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /bloqueado/);
  assert.equal(fs.readFileSync(lock, 'utf8'), '');
});
test(
  'dos escritores de procesos reales compiten y solo uno publica',
  { timeout: 40000 },
  async (t) => {
    const f = await fixture(t);
    const url = require('node:url').pathToFileURL(
      path.resolve(__dirname, '../dist/coordination/store.js'),
    ).href;
    const n = f.n();
    const code = `import fs from 'node:fs'; import {CoordinationStore} from ${JSON.stringify(url)}; const options=JSON.parse(process.env.TEST_OPTIONS); options.permissions={verifyRoot(){},inspect(){return 'test'}}; options.fault=(phase)=>{if(phase==='temporary'){console.log('holding');fs.readSync(0,Buffer.alloc(1),0,1,null);}}; const result=new CoordinationStore(options).apply(JSON.parse(process.env.TEST_NOTICE),'prueba');console.log(result.result);`;
    const child = spawn(process.execPath, ['--input-type=module', '-e', code], {
      env: {
        ...process.env,
        TEST_OPTIONS: JSON.stringify({ ...f.options, permissions: undefined }),
        TEST_NOTICE: JSON.stringify(n),
      },
      stdio: ['pipe', 'pipe', 'pipe'],
      timeout: 30000,
    });
    t.after(() => child.kill());
    const finished = once(child, 'exit');
    let output = '';
    let errors = '';
    child.stderr.on('data', (chunk) => {
      errors += chunk;
    });
    await new Promise((resolve, reject) => {
      child.once('error', reject);
      child.once('exit', () =>
        reject(new Error('Escritor salió antes de adquirir bloqueo: ' + errors)),
      );
      child.stdout.on('data', (chunk) => {
        output += chunk;
        if (output.includes('holding')) resolve();
      });
    });
    assert.throws(() => f.store.apply(f.n(2), 'segundo escritor'), /Bloqueo/);
    child.stdin.write('x');
    const [status] = await finished;
    assert.equal(status, 0, errors);
    assert.match(output, /aplicado/);
    assert.equal(f.store.query('T-001', n.updateId).result, 'aplicado');
  },
);
test('versión posterior acredita operación previa sin completada; no restaura base', async (t) => {
  const f = await fixture(t);
  const n = f.n();
  f.store.apply(n, 'primera');
  const operations = path.join(f.root, 'coordinacion/.control/operaciones');
  const directory = fs
    .readdirSync(operations)
    .find(
      (id) =>
        JSON.parse(fs.readFileSync(path.join(operations, id, 'operacion.json'))).notice
          ?.updateId === n.updateId,
    );
  const later = f.n(2);
  f.store.apply(later, 'segunda');
  fs.unlinkSync(path.join(operations, directory, 'completada.json'));
  const before = fs.readFileSync(path.join(f.root, 'coordinacion/T-001/TAREA.md'));
  f.store.recover();
  assert.deepEqual(fs.readFileSync(path.join(f.root, 'coordinacion/T-001/TAREA.md')), before);
  assert.equal(f.store.query('T-001', later.updateId).result, 'aplicado');
});
test('marcador parcial conserva incertidumbre y no reconstruye canónico ausente', async (t) => {
  const f = await fixture(t);
  const n = f.n();
  f.store.apply(n, 'prueba');
  const operations = path.join(f.root, 'coordinacion/.control/operaciones');
  const directory = fs
    .readdirSync(operations)
    .find(
      (id) =>
        JSON.parse(fs.readFileSync(path.join(operations, id, 'operacion.json'))).notice
          ?.updateId === n.updateId,
    );
  fs.writeFileSync(path.join(operations, directory, 'completada.json'), '{');
  assert.throws(() => f.store.recover());
  unlock(f.root);
  fs.unlinkSync(path.join(f.root, 'coordinacion/T-001/TAREA.md'));
  assert.throws(() => f.store.recover());
  assert.equal(f.store.query('T-001', n.updateId).result, 'incierto');
});
test('política de permisos incierta detiene antes de sustituir', async (t) => {
  const f = await fixture(t);
  const n = f.n();
  const before = fs.readFileSync(path.join(f.root, 'coordinacion/T-001/TAREA.md'));
  let calls = 0;
  const store = new f.CoordinationStore({
    ...f.options,
    permissions: {
      inspect() {
        return 'test';
      },
      verifyRoot(file) {
        if (file.endsWith('.tmp')) throw new Error('permiso incierto');
      },
    },
    replaceRunner() {
      calls++;
      return { ok: true };
    },
  });
  assert.throws(() => store.apply(n, 'prueba'), /permiso incierto/);
  assert.equal(calls, 0);
  assert.deepEqual(fs.readFileSync(path.join(f.root, 'coordinacion/T-001/TAREA.md')), before);
});
test(
  'demo nativo verifica ACL y sustitución reales en carpeta privada vacía',
  { timeout: 180000 },
  async (t) => {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'aikit-native-demo-'));
    t.after(() => fs.rmSync(root, { recursive: true, force: true }));
    fs.chmodSync(root, 0o700);
    if (process.platform === 'win32') {
      const script = `$ErrorActionPreference='Stop'; $acl=[IO.Directory]::GetAccessControl($env:TEST_ROOT); $acl.SetAccessRuleProtection($true,$false); foreach($rule in @($acl.GetAccessRules($true,$true,[Security.Principal.SecurityIdentifier]))){$acl.RemoveAccessRuleSpecific($rule)}; $sid=[Security.Principal.WindowsIdentity]::GetCurrent().User; $rule=[Security.AccessControl.FileSystemAccessRule]::new($sid,'FullControl','ContainerInherit,ObjectInherit','None','Allow'); $acl.AddAccessRule($rule); [IO.Directory]::SetAccessControl($env:TEST_ROOT,$acl)`;
      const setup = spawnSync(
        path.join(process.env.SystemRoot, 'System32/WindowsPowerShell/v1.0/powershell.exe'),
        [
          '-NoProfile',
          '-NonInteractive',
          '-EncodedCommand',
          Buffer.from(script, 'utf16le').toString('base64'),
        ],
        {
          env: { ...process.env, TEST_ROOT: root },
          encoding: 'utf8',
          windowsHide: true,
          timeout: 15000,
        },
      );
      assert.equal(setup.status, 0, setup.stderr);
    }
    const result = spawnSync(
      process.execPath,
      [path.resolve(__dirname, '../dist/coordination-demo.js'), root],
      { encoding: 'utf8', timeout: 150000 },
    );
    if (
      process.platform === 'win32' &&
      process.env.AIKIT_REQUIRE_NATIVE_ACL !== 'yes' &&
      result.status === 1 &&
      result.stderr.includes('ACL no verificable:') &&
      result.stderr.includes('Escritura por otro principal')
    ) {
      assert.deepEqual(
        fs.readdirSync(root),
        [],
        'El rechazo de ACL debe ocurrir antes de crear datos',
      );
      t.skip(
        'La ACL del sandbox añade otro principal: rechazo seguro comprobado; ruta positiva requiere ejecución nativa sin sandbox',
      );
      return;
    }
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(result.stdout).result, 'aplicado');
    const before = fs.readFileSync(path.join(root, 'coordinacion/T-001/TAREA.md'));
    const retry = spawnSync(
      process.execPath,
      [path.resolve(__dirname, '../dist/coordination-demo.js'), root],
      { encoding: 'utf8', timeout: 15000 },
    );
    assert.equal(retry.status, 1);
    assert.deepEqual(fs.readFileSync(path.join(root, 'coordinacion/T-001/TAREA.md')), before);
  },
);
test('recibos duplicados, current fabricado y generación incoherente no acreditan acuse', async (t) => {
  const f = await fixture(t);
  const s = await import('../dist/coordination/schema.js');
  const n = f.n();
  f.store.apply(n, 'prueba');
  const file = path.join(f.root, 'coordinacion/T-001/TAREA.md');
  const original = fs.readFileSync(file);
  const source = s.document(original);
  for (const patch of [
    { receipts: [...source.receipts, ...source.receipts] },
    { current: { ...source.current, updateId: randomUUID() } },
    { generation: 999 },
    { assignedChatId: 'otra' },
    { extra: true },
  ]) {
    fs.writeFileSync(file, s.markdown({ ...source, ...patch }));
    const before = fs.readFileSync(file);
    assert.equal(f.store.query('T-001', n.updateId).result, 'incierto');
    assert.throws(() => f.store.apply(f.n(2), 'prueba'));
    assert.deepEqual(fs.readFileSync(file), before);
    assert.equal(fs.existsSync(path.join(f.root, 'coordinacion/.control/escritura.lock')), false);
  }
  fs.writeFileSync(file, original);
});
test('recuperación no confirma permisos alterados después de publicar', async (t) => {
  const f = await fixture(t);
  let permissions = 'original';
  const n = f.n();
  const options = {
    ...f.options,
    permissions: {
      verifyRoot() {},
      inspect() {
        return permissions;
      },
    },
  };
  const store = new f.CoordinationStore({
    ...options,
    fault(phase) {
      if (phase === 'published') {
        permissions = 'cambiado';
        throw new Error('interrupción');
      }
    },
  });
  assert.throws(() => store.apply(n, 'prueba'), /interrupción/);
  unlock(f.root);
  assert.throws(() => new f.CoordinationStore(options).recover(), /permisos no preservados/);
});
test('derivados fallidos conservan acuse confirmado y diario recuperable', async (t) => {
  const f = await fixture(t);
  const n = f.n();
  f.store.apply(n, 'prueba');
  const broken = new f.CoordinationStore({
    ...f.options,
    fault(phase) {
      if (phase === 'ready') throw new Error('índice pendiente');
    },
  });
  assert.throws(() => broken.rebuildIndex(), /índice pendiente/);
  assert.equal(f.store.query('T-001', n.updateId).result, 'aplicado');
  unlock(f.root);
  f.store.recover();
  f.store.rebuildIndex();
  assert.ok(fs.existsSync(path.join(f.root, 'coordinacion/INDICE.md')));
});
