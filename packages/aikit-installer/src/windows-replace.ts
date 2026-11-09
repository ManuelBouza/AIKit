import * as fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { diagnoseReplaceFailure, type ObservedPath, type RecoveryReport } from './replace-recovery.js';

// Script constante: las rutas son datos en el entorno, nunca código PowerShell.
const script = `$ErrorActionPreference = 'Stop'
try {
  [IO.File]::Replace($env:AIKIT_REPLACE_TEMP, $env:AIKIT_REPLACE_DEST, $env:AIKIT_REPLACE_BACKUP, $false)
  @{ ok = $true } | ConvertTo-Json -Compress
} catch {
  $exception = $_.Exception.GetBaseException()
  $hresult = [long]$exception.HResult -band 0xffffffffL
  $code = $null
  if (($hresult -band 0xffff0000L) -eq 0x80070000L) { $code = $hresult -band 0xffffL }
  @{ ok = $false; code = $code } | ConvertTo-Json -Compress
  exit 1
}`;

export type ReplacePaths = { destination: string; replacement: string; backup: string };
export type ReplaceOutcome = { ok: true } | { ok: false; code: number | null };
export type ReplaceRunner = (paths: ReplacePaths) => ReplaceOutcome;

export const runWindowsReplace: ReplaceRunner = (paths) => {
  const systemRoot = process.env.SystemRoot;
  if (!systemRoot || !path.isAbsolute(systemRoot)) return { ok: false, code: null };
  const executable = path.join(systemRoot, 'System32', 'WindowsPowerShell', 'v1.0', 'powershell.exe');
  const encoded = Buffer.from(script, 'utf16le').toString('base64');
  const result = spawnSync(executable, ['-NoLogo', '-NoProfile', '-NonInteractive', '-EncodedCommand', encoded], {
    env: { ...process.env, AIKIT_REPLACE_TEMP: paths.replacement, AIKIT_REPLACE_DEST: paths.destination, AIKIT_REPLACE_BACKUP: paths.backup },
    encoding: 'utf8', windowsHide: true,
  });
  if (result.error || result.signal || result.status === null) return { ok: false, code: null };
  try {
    const output: unknown = JSON.parse(result.stdout.trim());
    if (!output || typeof output !== 'object' || !('ok' in output)) return { ok: false, code: null };
    if (result.status === 0 && output.ok === true) return { ok: true };
    if (result.status !== 0 && output.ok === false && 'code' in output && (output.code === null || (typeof output.code === 'number' && Number.isInteger(output.code) && output.code >= 0 && output.code <= 65535))) {
      return { ok: false, code: output.code as number | null };
    }
  } catch { /* Salida no verificable: preservar y diagnosticar. */ }
  return { ok: false, code: null };
};

function observe(file: string): ObservedPath {
  try { fs.lstatSync(file); return { path: file, exists: true }; }
  catch (error) { return { path: file, exists: (error as NodeJS.ErrnoException).code === 'ENOENT' ? false : 'unknown' }; }
}

/** Nunca restaura, borra ni reintenta; informa el estado observado. */
export function replaceWindows(paths: ReplacePaths, runner: ReplaceRunner = runWindowsReplace): RecoveryReport | null {
  let outcome: ReplaceOutcome;
  try { outcome = runner(paths); } catch { outcome = { ok: false, code: null }; }
  if (outcome.ok) return null;
  return diagnoseReplaceFailure({ code: outcome.code, destination: observe(paths.destination), replacement: observe(paths.replacement), backup: observe(paths.backup) });
}
