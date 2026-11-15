import * as fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { CoordinationStore } from './coordination/store.js';

/** Solo inicializa una carpeta existente y completamente vacía elegida explícitamente. */
export function demo(root: string) {
  if (
    !path.isAbsolute(root) ||
    !fs.statSync(root).isDirectory() ||
    fs.readdirSync(root).length !== 0
  )
    throw new Error('El demo requiere una carpeta absoluta, existente y vacía');
  const projectId = randomUUID();
  const updateId = randomUUID();
  const options = { root, projectId, coordinatorChatId: 'demo-coordinador', ownerEpoch: 1 };
  const store = new CoordinationStore(options);
  store.activate('Demostración ficticia autorizada');
  store.createTask('T-001', 'demo-tarea', 'Asignación fija del demo');
  store.apply(
    {
      schemaVersion: 1,
      projectId,
      taskId: 'T-001',
      cycle: 1,
      senderChatId: 'demo-tarea',
      updateId,
      revision: 1,
      state: 'Finalizada',
      summary: 'Demostración local completada',
      references: ['evidencia ficticia'],
      corrects: null,
    },
    'Aviso ficticio del demo',
  );
  store.rebuildIndex();
  return new CoordinationStore(options).query('T-001', updateId);
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  try {
    if (process.argv.length !== 3)
      throw new Error('Uso: node dist/coordination-demo.js <carpeta-absoluta-vacía>');
    console.log(JSON.stringify(demo(process.argv[2]), null, 2));
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
