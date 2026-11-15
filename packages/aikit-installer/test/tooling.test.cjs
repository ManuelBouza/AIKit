// Ejercita el consumidor real de minimatch en el parser, no solo su importación.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { parser } = require('typescript-eslint');

test('projectService admite un archivo oculto mediante allowDefaultProject', (t) => {
  const root = path.resolve(__dirname, '../../../.aikit/node-test');
  fs.mkdirSync(root, { recursive: true });
  const dir = fs.mkdtempSync(path.join(root, 'parser-'));
  t.after(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });
  fs.writeFileSync(
    path.join(dir, 'tsconfig.json'),
    JSON.stringify({ compilerOptions: { strict: true }, include: ['included.ts'] }),
  );
  fs.writeFileSync(path.join(dir, 'included.ts'), 'export {};\n');
  const result = parser.parseForESLint('const value: number = 1;', {
    filePath: path.join(dir, '.probe.ts'),
    tsconfigRootDir: dir,
    projectService: { allowDefaultProject: ['*.ts'] },
    loc: true,
    range: true,
  });
  assert.ok(result.services.program);
  assert.ok(result.services.program.getSourceFile(path.join(dir, '.probe.ts')));
});
