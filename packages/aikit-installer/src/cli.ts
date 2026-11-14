#!/usr/bin/env node
import * as fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { TextDecoder } from 'node:util';
import { spawnSync } from 'node:child_process';
import { replaceWindows } from './windows-replace.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const version = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8')).version;
const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });

function checkedPath(target: string): void {
  let current = path.resolve(target);
  for (;;) {
    try {
      const info = fs.lstatSync(current);
      if (info.isSymbolicLink()) throw new Error(`Enlace o junction no permitido: ${current}`);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error;
    }
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
}

function readOptional(file: string): Buffer | null {
  try { return fs.readFileSync(file); } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw error;
  }
}

function count(text: string, marker: string): number { return text.split(marker).length - 1; }

function validateCrossed(text: string): void {
  const markers = [...text.matchAll(/<!-- AIKIT:(GO|CONTEXT7|INVESTIGACION|ESCRITURA|VISUALIZACION):(BEGIN|END) -->/g)];
  let open = null;
  const seen = new Set<string>();
  for (const marker of markers) {
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
  for (const [label, value] of [['plantilla', template], ['destino', text]]) {
    const starts = count(value, begin), ends = count(value, end);
    if (starts > 1 || ends > 1 || starts !== ends || (label === 'plantilla' && starts !== 1) || (starts && value.indexOf(begin) > value.indexOf(end))) {
      throw new Error(`Marcadores ${name} inválidos en ${label}`);
    }
  }
  let block = template.slice(template.indexOf(begin), template.indexOf(end) + end.length);
  if (name === 'GO') block = block.replace(begin, `${begin}\n<!-- AIKIT:VERSION:${version} -->`);
  if (text.includes(begin)) return text.slice(0, text.indexOf(begin)) + block + text.slice(text.indexOf(end) + end.length);
  if (!text) return block;
  return text + (text.endsWith('\n') ? '' : '\n') + block + '\n';
}

function main(args: string[]): void {
  const command = args.shift();
  if (command !== 'install' && command !== 'status') throw new Error('Uso: aikit <install|status> [--codex-home RUTA] [--dry-run]');
  let targetDirectory = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
  let scope: 'global' | 'project' | undefined;
  let explicitCodexHome = false;
  let dry = false;
  const selected = new Set<string>();
  const removed = new Set<string>();
  const optionNames: Record<string, string> = { '--go': 'GO', '--context7': 'CONTEXT7', '--investigacion': 'INVESTIGACION', '--escritura': 'ESCRITURA', '--visualizacion': 'VISUALIZACION' };
  while (args.length) {
    const arg = args.shift();
    if (arg === '--dry-run') dry = true;
    else if (arg && optionNames[arg]) selected.add(optionNames[arg]);
    else if (arg?.startsWith('--quitar-') && optionNames[`--${arg.slice(9)}`]) removed.add(optionNames[`--${arg.slice(9)}`]);
    else if (arg === '--global' || arg === '--project') {
      if (scope) throw new Error('Indique un único ámbito: --global o --project');
      scope = arg === '--global' ? 'global' : 'project';
    }
    else if (arg === '--codex-home' && args.length && args[0]) { targetDirectory = args.shift()!; explicitCodexHome = true; }
    else throw new Error(`Opción inválida: ${arg}`);
  }
  for (const name of removed) if (selected.has(name)) throw new Error(`No se puede activar y quitar ${name} a la vez`);
  if (scope === 'project' && explicitCodexHome) throw new Error('--codex-home solo es válido para el ámbito global');
  if (!scope && explicitCodexHome) scope = 'global'; // compatibilidad con perfiles ficticios y CLI anterior
  if (!scope) {
    if (!process.stdin.isTTY) throw new Error('Indique el ámbito mediante --global o --project');
    process.stderr.write('Ámbito de AIKit: global (g) o proyecto (p): ');
    const input = Buffer.alloc(64);
    const selection = input.subarray(0, fs.readSync(0, input, 0, input.length, null)).toString('utf8').trim().toLowerCase();
    if (selection !== 'g' && selection !== 'p') throw new Error('Ámbito no reconocido; no se modificó ningún archivo');
    scope = selection === 'g' ? 'global' : 'project';
  }
  let backupBase: string;
  if (scope === 'project') {
    const gitRoot = spawnSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8', windowsHide: true });
    if (gitRoot.error || gitRoot.status !== 0 || !gitRoot.stdout.trim()) throw new Error('El directorio actual no pertenece a un repositorio Git');
    targetDirectory = path.resolve(gitRoot.stdout.trim());
    const gitPath = spawnSync('git', ['rev-parse', '--path-format=absolute', '--git-path', 'aikit-backups'], { cwd: targetDirectory, encoding: 'utf8', windowsHide: true });
    if (gitPath.error || gitPath.status !== 0 || !gitPath.stdout.trim()) throw new Error('No se pudo determinar la ubicación administrativa Git para respaldos');
    backupBase = path.resolve(gitPath.stdout.trim());
  } else {
    targetDirectory = path.resolve(targetDirectory);
    backupBase = path.join(targetDirectory, 'backups', 'aikit');
  }
  const target = path.join(targetDirectory, 'AGENTS.md');
  const override = path.join(targetDirectory, 'AGENTS.override.md');
  checkedPath(target); checkedPath(override);
  const overrideBytes = readOptional(override);
  if (overrideBytes?.length) throw new Error('AGENTS.override.md no vacío; no se modificó ningún archivo');
  const original = readOptional(target);
  const originalStat = original ? fs.statSync(target) : null;
  const before = original ? decoder.decode(original) : '';
  validateCrossed(before);
  let after = before;
  const blocks = [['GO', 'go.md'], ['CONTEXT7', 'context7.md'], ['INVESTIGACION', 'investigacion.md'], ['ESCRITURA', 'escritura.md'], ['VISUALIZACION', 'visualizacion.md']];
  for (const [name, filename] of blocks) {
    if (removed.has(name)) {
      const begin = `<!-- AIKIT:${name}:BEGIN -->`, end = `<!-- AIKIT:${name}:END -->`;
      const start = after.indexOf(begin);
      if (start !== -1) after = after.slice(0, start) + after.slice(after.indexOf(end, start) + end.length);
      continue;
    }
    if ((selected.size || removed.size) ? !selected.has(name) : ['ESCRITURA', 'VISUALIZACION'].includes(name)) continue;
    after = merge(after, name, decoder.decode(fs.readFileSync(path.join(root, 'templates', filename))));
  }
  const replacement = Buffer.from(after, 'utf8');
  const changed = original ? !original.equals(replacement) : replacement.length > 0;
  if (command === 'status') {
    const match = before.match(/<!-- AIKIT:VERSION:([^\s]+) -->/g) || [];
    const withinGo = before.match(/<!-- AIKIT:GO:BEGIN -->[\s\S]*?<!-- AIKIT:GO:END -->/)?.[0] || '';
    const installed = withinGo.match(/<!-- AIKIT:VERSION:([^\s]+) -->/)?.[1] || null;
    console.log(JSON.stringify({status: changed ? 'different' : 'current', path: target, version, installedVersion: match.length === 1 ? installed : null}));
    return;
  }
  let backup: string | null = null;
  let windowsBackup: string | null = null;
  if (!dry && changed) {
    process.stderr.write(`Destino ${scope}: ${target}\n`);
    fs.mkdirSync(targetDirectory, { recursive: true });
    checkedPath(target); checkedPath(override);
    const temporary = path.join(targetDirectory, `.agents.md.tmp-${randomUUID()}`);
    const backupDir = path.join(backupBase, randomUUID());
    const lockPath = path.join(targetDirectory, '.aikit-instructions.lock');
    const nativeBackup = path.join(backupDir, 'original-replacefile.md');
    let preserveTemporary = false;
    checkedPath(lockPath);
    let lock: number;
    try {
      lock = fs.openSync(lockPath, 'wx', 0o600);
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'EEXIST') throw new Error('Otra instalación de AIKit está activa o dejó un bloqueo pendiente');
      throw error;
    }
    try {
      fs.writeFileSync(temporary, replacement, { flag: 'wx', mode: 0o600 });
      // Windows chmod no preserva ACL; conservar únicamente bits POSIX donde sí aplican.
      if (originalStat && process.platform !== 'win32') fs.chmodSync(temporary, originalStat.mode & 0o777);
      checkedPath(backupDir);
      fs.mkdirSync(backupDir, { recursive: true });
      backup = path.join(backupDir, original ? 'AGENTS.md' : 'STATE.txt');
      fs.writeFileSync(backup, original || 'AGENTS.md no existía originalmente.\n', { flag: 'wx', mode: 0o600 });
      checkedPath(target); checkedPath(override);
      const current = readOptional(target);
      const currentOverride = readOptional(override);
      if ((currentOverride?.length || 0) !== 0 || (!!current !== !!original) || (current && original && !current.equals(original))) throw new Error('Modificación concurrente detectada');
      if (originalStat) {
        const currentStat = fs.statSync(target);
        if (currentStat.dev !== originalStat.dev || currentStat.ino !== originalStat.ino || currentStat.mode !== originalStat.mode) throw new Error('Metadatos o identidad modificados durante la instalación');
      }
      if (original && process.platform === 'win32') {
        checkedPath(nativeBackup);
        // Al iniciar File.Replace, cualquier fallo puede dejar un estado parcial.
        preserveTemporary = true;
        const report = replaceWindows({ destination: target, replacement: temporary, backup: nativeBackup });
        if (report) throw new Error(`Falló la sustitución de Windows; conserve los archivos y examine el diagnóstico: ${JSON.stringify({ ...report, priorBackup: backup })}`);
        windowsBackup = nativeBackup;
        preserveTemporary = false;
      } else {
        fs.renameSync(temporary, target);
      }
    } finally {
      try {
        if (!preserveTemporary) try { fs.unlinkSync(temporary); } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; }
      } finally {
        fs.closeSync(lock);
        // Un resultado incierto exige inspección antes de cualquier reintento.
        if (!preserveTemporary) fs.unlinkSync(lockPath);
      }
    }
  }
  console.log(JSON.stringify({ status: dry ? 'preview' : changed ? 'changed' : 'unchanged', path: target, version, backup, windowsBackup, before: dry ? before : undefined, after: dry ? after : undefined }));
}

try { main(process.argv.slice(2)); } catch (error) { console.error(error instanceof Error ? error.message : String(error)); process.exitCode = 1; }
