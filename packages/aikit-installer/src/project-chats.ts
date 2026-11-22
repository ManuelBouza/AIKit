import * as fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  inventoryPath,
  listRecords,
  readInventoryDirectory,
  updateRecord,
} from './chat-inventory.js';
import { checkedPath, decoder, readOptional, writeInstructions } from './project-files.js';

export const CHAT_BLOCK = 'RESPONSABILIDAD-CHATS';
const begin = `<!-- AIKIT:${CHAT_BLOCK}:BEGIN -->`;
const end = `<!-- AIKIT:${CHAT_BLOCK}:END -->`;
const rootLine = 'Raíz de inventario (ruta JSON): ';
const usage = 'Uso: aikit project-chats <status|enable|disable|list|upsert> --root RAÍZ_ABSOLUTA';

function absoluteRoot(root: string): boolean {
  return process.platform === 'win32'
    ? /^(?:[a-z]:[\\/]|[\\/]{2}[^\\/]+[\\/][^\\/]+)/i.test(root)
    : path.isAbsolute(root);
}

function projectDirectory(root: string): string {
  if (!absoluteRoot(root)) throw new Error('Indique una raíz de proyecto absoluta');
  const directory = path.resolve(root);
  checkedPath(directory);
  if (!fs.statSync(directory).isDirectory()) throw new Error(`No es un directorio: ${directory}`);
  const canonical = fs.realpathSync(directory);
  for (const profile of [path.join(os.homedir(), '.codex'), process.env.CODEX_HOME]) {
    if (!profile) continue;
    const profilePath = path.resolve(profile);
    const locations = [profilePath];
    try {
      locations.push(fs.realpathSync.native(profilePath));
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
    }
    for (const location of locations) {
      const relative = path.relative(location, canonical);
      if (!relative || (!path.isAbsolute(relative) && !relative.split(path.sep).includes('..')))
        throw new Error('La responsabilidad única solo se configura en un proyecto local');
    }
  }
  return canonical;
}

function linkedCommonDirectory(root: string): string | null {
  const dotGit = path.join(root, '.git');
  checkedPath(dotGit);
  let metadata: fs.Stats;
  try {
    metadata = fs.statSync(dotGit);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw error;
  }
  if (!metadata.isFile()) return null;
  const gitDir = fs
    .readFileSync(dotGit, 'utf8')
    .trim()
    .match(/^gitdir: (.+)$/)?.[1];
  if (!gitDir) throw new Error(`No se pudo verificar .git en ${root}`);
  const commonDir = path.resolve(root, gitDir, 'commondir');
  checkedPath(commonDir);
  const contents = readOptional(commonDir)?.toString('utf8').trim();
  if (contents === undefined) return null;
  if (!contents) throw new Error(`No se pudo verificar commondir en ${root}`);
  return path.resolve(path.dirname(commonDir), contents);
}

function sharedDirectory(root: string): string {
  const directory = projectDirectory(root);
  if (linkedCommonDirectory(directory))
    throw new Error('Indique la raíz de inventario compartida, fuera del checkout del worktree');
  return directory;
}

function configuration(text: string) {
  const from = text.indexOf(begin);
  if (from === -1) return null;
  const to = text.indexOf(end, from) + end.length;
  const block = text.slice(from, to);
  const references = block.split('\n').filter((line) => line.startsWith(rootLine));
  const match = references[0]?.slice(rootLine.length).match(/^`(.+)`\.?\r?$/);
  if (references.length !== 1 || !match) throw new Error('Referencia del inventario inválida');
  const root: unknown = JSON.parse(match[1]);
  if (typeof root !== 'string' || !absoluteRoot(root))
    throw new Error('Referencia del inventario sin raíz absoluta');
  return { from, to, root };
}

function principalInventory(root: string, validateMarkers: (text: string) => void): string | null {
  let bytes: Buffer | null;
  try {
    const common = linkedCommonDirectory(root);
    if (!common || path.basename(common) !== '.git') return null;
    const target = path.join(path.dirname(common), 'AGENTS.md');
    checkedPath(common);
    if (!fs.statSync(common).isDirectory()) return null;
    checkedPath(target);
    bytes = readOptional(target);
  } catch (error) {
    if (['ENOENT', 'EACCES', 'EPERM'].includes((error as NodeJS.ErrnoException).code ?? ''))
      return null;
    throw error;
  }
  if (!bytes) return null;
  const text = decoder.decode(bytes);
  if (!text.includes(begin)) return null;
  validateMarkers(text);
  return configuration(text)?.root ?? null;
}

function instructions(root: string): string {
  const quoted = JSON.stringify(root).replace(
    /[`<>\p{Zl}\p{Zp}]/gu,
    (character) => '\\u' + character.charCodeAt(0).toString(16).padStart(4, '0'),
  );
  return `${begin}
## Responsabilidad única del chat

${rootLine}\`${quoted}\`.

Conserva una sola responsabilidad por chat. Consulta el inventario de esta raíz
con el flujo «Responsabilidad única de los chats» de aikit-setup. Usa siempre
la misma raíz, incluso desde un worktree. Identifica los chats por su ID
nativo completo. Si no puedes verificar tu ID, deja el alta pendiente.

Atiende aquí las solicitudes que cubra tu responsabilidad. Para las demás,
recomienda el chat vigente que corresponda por su título e ID. Indica dudas
si hay varias coincidencias o si la consulta no está disponible. Si ningún
chat cubre la solicitud, recomienda un chat nuevo cuando baste un resumen o
un fork cuando sea necesario el historial. Conserva el encargo de este chat.
Crear o bifurcar requiere autorización específica. Si falta la acción nativa
o el acceso a la raíz de inventario, ofrece un traslado manual.

Registra los cambios por ID y sincroniza el título con la acción nativa, si
está disponible. Informa cualquier título pendiente de sincronizar y usa la
ficha como referencia de estado.
${end}`;
}

function inventoryAccess(root: string | null) {
  if (!root) return {};
  const directory = inventoryPath(root);
  try {
    sharedDirectory(root);
    const names = readInventoryDirectory(directory);
    if (names) listRecords(directory, names);
    return {
      inventoryPath: directory,
      inventoryAccess: names ? 'readable' : 'absent',
    };
  } catch (error) {
    return {
      inventoryPath: directory,
      inventoryAccess: 'unverified',
      inventoryError: error instanceof Error ? error.message : String(error),
    };
  }
}

export function runProjectChats(args: string[], validateMarkers: (text: string) => void): void {
  const command = args.shift();
  if (!['status', 'enable', 'disable', 'list', 'upsert'].some((item) => item === command))
    throw new Error(usage);
  const options = new Map<string, string>();
  const permitted = new Set(['--root']);
  if (command === 'enable') permitted.add('--inventory-root');
  if (command === 'upsert') permitted.add('--expected-revision');
  if (command === 'enable' || command === 'disable' || command === 'upsert')
    permitted.add('--dry-run');
  while (args.length) {
    const name = args.shift()!;
    if (!permitted.has(name) || options.has(name)) throw new Error(`Opción inválida: ${name}`);
    const value = name === '--dry-run' ? 'true' : args.shift();
    if (!value || value.startsWith('--')) throw new Error(`Falta valor para ${name}`);
    options.set(name, value);
  }
  const root = projectDirectory(options.get('--root') ?? '');
  const dry = options.has('--dry-run');
  if (command === 'list' || command === 'upsert') {
    const directory = inventoryPath(sharedDirectory(root));
    if (command === 'list') {
      console.log(
        JSON.stringify({ root, inventoryPath: directory, records: listRecords(directory) }),
      );
      return;
    }
    const revision = options.get('--expected-revision') ?? '';
    const expected = Number(revision);
    if (!/^\d+$/.test(revision) || !Number.isSafeInteger(expected + 1))
      throw new Error('Indique la revisión esperada completa (0 para un alta)');
    const result = updateRecord(directory, expected, dry);
    console.log(JSON.stringify({ status: dry ? 'preview' : 'changed', root, ...result }));
    return;
  }

  const target = path.join(root, 'AGENTS.md');
  const override = path.join(root, 'AGENTS.override.md');
  checkedPath(target);
  checkedPath(override);
  const overrideBytes = readOptional(override);
  const shadowed = !!overrideBytes?.length;
  const original = readOptional(target);
  const before = original ? decoder.decode(original) : '';
  validateMarkers(before);
  const config = configuration(before);
  const reference = config?.root ?? null;
  if (command === 'status') {
    console.log(
      JSON.stringify({
        status: shadowed ? 'shadowed' : config ? 'enabled' : 'disabled',
        path: target,
        root,
        inventoryRoot: reference,
        ...inventoryAccess(reference),
      }),
    );
    return;
  }
  if (shadowed && command === 'enable')
    throw new Error('AGENTS.override.md no vacío; no se modificó ningún archivo');

  let after = before;
  let inventoryRoot = reference;
  if (command === 'enable') {
    const explicit = options.get('--inventory-root');
    inventoryRoot = sharedDirectory(explicit ?? reference ?? root);
    if (reference && path.relative(reference, inventoryRoot))
      throw new Error('La regla local ya apunta a otra raíz compartida');
    const principal = principalInventory(root, validateMarkers);
    if (principal && path.relative(sharedDirectory(principal), inventoryRoot))
      throw new Error('Use la raíz de inventario configurada en el checkout principal');
    listRecords(inventoryPath(inventoryRoot));
    const eol = before.includes('\r\n') || before.endsWith('\r') ? '\r\n' : '\n';
    const block = instructions(inventoryRoot).replaceAll('\n', eol);
    after = config
      ? before.slice(0, config.from) + block + before.slice(config.to)
      : before + (before ? eol : '') + block + eol;
  } else if (config) {
    const prefix = before.slice(0, config.from);
    const suffix = before.slice(config.to);
    const leadingEol = prefix.match(/\r?\n$/)?.[0] ?? '';
    const trailingEol = suffix.match(/^\r?\n/)?.[0] ?? '';
    const above = prefix.slice(0, prefix.length - leadingEol.length);
    const below = suffix.slice(trailingEol.length);
    const separator =
      above && below && !above.endsWith('\n') && !/^\r?\n/.test(below)
        ? leadingEol || trailingEol
        : '';
    after = above + separator + below;
  }
  const changed = before !== after;
  const backupBase = path.join(root, '.aikit', 'instruction-backups');
  const backups =
    !dry && changed
      ? writeInstructions(
          root,
          backupBase,
          original,
          original ? fs.statSync(target) : null,
          Buffer.from(after),
          command === 'disable' ? (overrideBytes ?? undefined) : undefined,
        )
      : {};
  console.log(
    JSON.stringify({
      status: dry ? 'preview' : changed ? 'changed' : 'unchanged',
      path: target,
      root,
      inventoryRoot,
      ...inventoryAccess(inventoryRoot),
      ...backups,
      backupBase: dry ? backupBase : undefined,
      before: dry ? before : undefined,
      after: dry ? after : undefined,
    }),
  );
}
