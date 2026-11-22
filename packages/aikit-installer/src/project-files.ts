import * as fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import { TextDecoder } from 'node:util';
import { replaceWindows } from './windows-replace.js';

export const decoder = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });

export function checkedPath(target: string): void {
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

export function readOptional(file: string): Buffer | null {
  try {
    return fs.readFileSync(file);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw error;
  }
}

export function acquireLock(file: string, conflict: string): number {
  checkedPath(file);
  try {
    return fs.openSync(file, 'wx', 0o600);
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'EEXIST')
      throw new Error(conflict, { cause: error });
    throw error;
  }
}

export function writeInstructions(
  targetDirectory: string,
  backupBase: string,
  original: Buffer | null,
  originalStat: fs.Stats | null,
  replacement: Buffer,
  allowedOverride?: Buffer,
) {
  const target = path.join(targetDirectory, 'AGENTS.md');
  const override = path.join(targetDirectory, 'AGENTS.override.md');
  let windowsBackup: string | null = null;
  fs.mkdirSync(targetDirectory, { recursive: true });
  checkedPath(target);
  checkedPath(override);
  const temporary = path.join(targetDirectory, `.agents.md.tmp-${randomUUID()}`);
  const backupDir = path.join(backupBase, randomUUID());
  const backup = path.join(backupDir, original ? 'AGENTS.md' : 'STATE.txt');
  const lockPath = path.join(targetDirectory, '.aikit-instructions.lock');
  const nativeBackup = path.join(backupDir, 'original-replacefile.md');
  let preserveTemporary = false;
  const lock = acquireLock(
    lockPath,
    'Otra instalación de AIKit está activa o dejó un bloqueo pendiente',
  );
  try {
    fs.writeFileSync(temporary, replacement, { flag: 'wx', mode: 0o600 });
    // Windows chmod no preserva ACL; conservar únicamente bits POSIX donde sí aplican.
    if (originalStat && process.platform !== 'win32')
      fs.chmodSync(temporary, originalStat.mode & 0o777);
    checkedPath(backupDir);
    fs.mkdirSync(backupDir, { recursive: true });
    fs.writeFileSync(backup, original || 'AGENTS.md no existía originalmente.\n', {
      flag: 'wx',
      mode: 0o600,
    });
    checkedPath(target);
    checkedPath(override);
    const current = readOptional(target);
    const currentOverride = readOptional(override);
    if (
      (allowedOverride
        ? !currentOverride?.equals(allowedOverride)
        : (currentOverride?.length || 0) !== 0) ||
      !!current !== !!original ||
      (current && original && !current.equals(original))
    )
      throw new Error('Modificación concurrente detectada');
    if (originalStat) {
      const currentStat = fs.statSync(target);
      if (
        currentStat.dev !== originalStat.dev ||
        currentStat.ino !== originalStat.ino ||
        currentStat.mode !== originalStat.mode
      )
        throw new Error('Metadatos o identidad modificados durante la instalación');
    }
    if (original && process.platform === 'win32') {
      checkedPath(nativeBackup);
      // Al iniciar File.Replace, cualquier fallo puede dejar un estado parcial.
      preserveTemporary = true;
      const report = replaceWindows({
        destination: target,
        replacement: temporary,
        backup: nativeBackup,
      });
      if (report)
        throw new Error(
          `Falló la sustitución de Windows; conserve los archivos y examine el diagnóstico: ${JSON.stringify({ ...report, priorBackup: backup })}`,
        );
      windowsBackup = nativeBackup;
      preserveTemporary = false;
    } else {
      fs.renameSync(temporary, target);
    }
  } finally {
    try {
      if (!preserveTemporary) fs.rmSync(temporary, { force: true });
    } finally {
      fs.closeSync(lock);
      // Un resultado incierto exige inspección antes de cualquier reintento.
      if (!preserveTemporary) fs.unlinkSync(lockPath);
    }
  }
  return { backup, windowsBackup };
}
