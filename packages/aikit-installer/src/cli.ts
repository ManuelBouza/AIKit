#!/usr/bin/env node
import * as fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { checkedPath, decoder, readOptional, writeInstructions } from './project-files.js';
import { CHAT_BLOCK, runProjectChats } from './project-chats.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const metadata: unknown = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
if (
  !metadata ||
  typeof metadata !== 'object' ||
  !('version' in metadata) ||
  typeof metadata.version !== 'string'
) {
  throw new Error('package.json sin version válida');
}
const version = metadata.version;
if (
  !('aikitPreferences' in metadata) ||
  !metadata.aikitPreferences ||
  typeof metadata.aikitPreferences !== 'object' ||
  Array.isArray(metadata.aikitPreferences)
) {
  throw new Error('package.json sin preferencias AIKit válidas');
}
const preferences = new Map<string, boolean>();
for (const [id, enabled] of Object.entries(metadata.aikitPreferences)) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id) || typeof enabled !== 'boolean') {
    throw new Error(`Preferencia AIKit inválida: ${id}`);
  }
  preferences.set(id, enabled);
}
function count(text: string, marker: string): number {
  return text.split(marker).length - 1;
}

function validateCrossed(text: string): void {
  const markers = text.matchAll(/<!-- AIKIT:([A-Z0-9-]+):(BEGIN|END) -->/g);
  let open = null;
  const seen = new Set<string>();
  for (const marker of markers) {
    if (marker[1] !== CHAT_BLOCK && !preferences.has(marker[1].toLowerCase())) continue;
    if (marker[2] === 'BEGIN') {
      if (seen.has(marker[1])) throw new Error('Bloque AIKit duplicado');
      seen.add(marker[1]);
      if (open) throw new Error('Bloques AIKit solapados o anidados');
      open = marker[1];
    } else {
      if (open !== marker[1]) throw new Error('Bloques AIKit solapados o mal ordenados');
      open = null;
    }
  }
  if (open) throw new Error('Bloque AIKit sin cierre');
}

function merge(text: string, name: string, template: string): string {
  const begin = `<!-- AIKIT:${name}:BEGIN -->`;
  const end = `<!-- AIKIT:${name}:END -->`;
  for (const [label, value] of [
    ['plantilla', template],
    ['destino', text],
  ]) {
    const starts = count(value, begin),
      ends = count(value, end);
    if (
      starts > 1 ||
      ends > 1 ||
      starts !== ends ||
      (label === 'plantilla' && starts !== 1) ||
      (starts && value.indexOf(begin) > value.indexOf(end))
    ) {
      throw new Error(`Marcadores ${name} inválidos en ${label}`);
    }
  }
  let block = template.slice(template.indexOf(begin), template.indexOf(end) + end.length);
  if (name === 'GO') block = block.replace(begin, `${begin}\n<!-- AIKIT:VERSION:${version} -->`);
  if (text.includes(begin))
    return text.slice(0, text.indexOf(begin)) + block + text.slice(text.indexOf(end) + end.length);
  if (!text) return block;
  return text + (text.endsWith('\n') ? '' : '\n') + block + '\n';
}

function main(args: string[]): void {
  const command = args.shift();
  if (command === 'project-chats') {
    runProjectChats(args, validateCrossed);
    return;
  }
  if (command !== 'install' && command !== 'status')
    throw new Error('Uso: aikit <install|status|project-chats>');
  let targetDirectory = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
  let scope: 'global' | 'project' | undefined;
  let explicitCodexHome = false;
  let dry = false;
  const selected = new Set<string>();
  const removed = new Set<string>();
  while (args.length) {
    const arg = args.shift();
    if (arg === '--dry-run') dry = true;
    else if (arg?.startsWith('--') && preferences.has(arg.slice(2))) selected.add(arg.slice(2));
    else if (arg?.startsWith('--quitar-') && preferences.has(arg.slice(9)))
      removed.add(arg.slice(9));
    else if (arg === '--global' || arg === '--project') {
      if (scope) throw new Error('Indique un único ámbito: --global o --project');
      scope = arg === '--global' ? 'global' : 'project';
    } else if (arg === '--codex-home' && args.length && args[0]) {
      targetDirectory = args.shift()!;
      explicitCodexHome = true;
    } else throw new Error(`Opción inválida: ${arg}`);
  }
  for (const name of removed)
    if (selected.has(name))
      throw new Error(`No se puede activar y quitar ${name.toUpperCase()} a la vez`);
  if (scope === 'project' && explicitCodexHome)
    throw new Error('--codex-home solo es válido para el ámbito global');
  if (!scope && explicitCodexHome) scope = 'global'; // compatibilidad con perfiles ficticios y CLI anterior
  if (!scope) {
    if (!process.stdin.isTTY) throw new Error('Indique el ámbito mediante --global o --project');
    process.stderr.write('Ámbito de AIKit: global (g) o proyecto (p): ');
    const input = Buffer.alloc(64);
    const selection = input
      .subarray(0, fs.readSync(0, input, 0, input.length, null))
      .toString('utf8')
      .trim()
      .toLowerCase();
    if (selection !== 'g' && selection !== 'p')
      throw new Error('Ámbito no reconocido; no se modificó ningún archivo');
    scope = selection === 'g' ? 'global' : 'project';
  }
  let backupBase: string;
  if (scope === 'project') {
    const gitRoot = spawnSync('git', ['rev-parse', '--show-toplevel'], {
      encoding: 'utf8',
      windowsHide: true,
    });
    if (gitRoot.error || gitRoot.status !== 0 || !gitRoot.stdout.trim())
      throw new Error('El directorio actual no pertenece a un repositorio Git');
    targetDirectory = path.resolve(gitRoot.stdout.trim());
    const gitPath = spawnSync(
      'git',
      ['rev-parse', '--path-format=absolute', '--git-path', 'aikit-backups'],
      { cwd: targetDirectory, encoding: 'utf8', windowsHide: true },
    );
    if (gitPath.error || gitPath.status !== 0 || !gitPath.stdout.trim())
      throw new Error('No se pudo determinar la ubicación administrativa Git para respaldos');
    backupBase = path.resolve(gitPath.stdout.trim());
  } else {
    targetDirectory = path.resolve(targetDirectory);
    backupBase = path.join(targetDirectory, 'backups', 'aikit');
  }
  const target = path.join(targetDirectory, 'AGENTS.md');
  const override = path.join(targetDirectory, 'AGENTS.override.md');
  checkedPath(target);
  checkedPath(override);
  const overrideBytes = readOptional(override);
  if (overrideBytes?.length)
    throw new Error('AGENTS.override.md no vacío; no se modificó ningún archivo');
  const original = readOptional(target);
  const originalStat = original ? fs.statSync(target) : null;
  const before = original ? decoder.decode(original) : '';
  validateCrossed(before);
  let after = before;
  for (const [id, defaultEnabled] of preferences) {
    const name = id.toUpperCase();
    if (removed.has(id)) {
      const begin = `<!-- AIKIT:${name}:BEGIN -->`,
        end = `<!-- AIKIT:${name}:END -->`;
      const start = after.indexOf(begin);
      if (start !== -1)
        after = after.slice(0, start) + after.slice(after.indexOf(end, start) + end.length);
      continue;
    }
    if (selected.size || removed.size ? !selected.has(id) : !defaultEnabled) continue;
    after = merge(
      after,
      name,
      decoder.decode(fs.readFileSync(path.join(root, 'templates', `${id}.md`))),
    );
  }
  const replacement = Buffer.from(after, 'utf8');
  const changed = original ? !original.equals(replacement) : replacement.length > 0;
  if (command === 'status') {
    const match = before.match(/<!-- AIKIT:VERSION:([^\s]+) -->/g) || [];
    const withinGo =
      before.match(/<!-- AIKIT:GO:BEGIN -->[\s\S]*?<!-- AIKIT:GO:END -->/)?.[0] || '';
    const installed = withinGo.match(/<!-- AIKIT:VERSION:([^\s]+) -->/)?.[1] || null;
    console.log(
      JSON.stringify({
        status: changed ? 'different' : 'current',
        path: target,
        version,
        installedVersion: match.length === 1 ? installed : null,
      }),
    );
    return;
  }
  let backup: string | null = null;
  let windowsBackup: string | null = null;
  if (!dry && changed) {
    process.stderr.write(`Destino ${scope}: ${target}\n`);
    ({ backup, windowsBackup } = writeInstructions(
      targetDirectory,
      backupBase,
      original,
      originalStat,
      replacement,
    ));
  }
  console.log(
    JSON.stringify({
      status: dry ? 'preview' : changed ? 'changed' : 'unchanged',
      path: target,
      version,
      backup,
      windowsBackup,
      before: dry ? before : undefined,
      after: dry ? after : undefined,
    }),
  );
}

try {
  main(process.argv.slice(2));
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
