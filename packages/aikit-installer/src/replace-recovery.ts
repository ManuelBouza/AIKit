/** Diagnóstico conservador tras un fallo de ReplaceFileW; no modifica archivos. */
export type ObservedPath = { path: string; exists: boolean | 'unknown' };

export interface ReplaceFailure {
  code: number | null;
  destination: ObservedPath;
  replacement: ObservedPath;
  backup: ObservedPath;
}

export interface RecoveryReport {
  code: number | null;
  classification: 'expected-original-paths' | 'expected-backup-path' | 'unverified';
  paths: { destination: ObservedPath; replacement: ObservedPath; backup: ObservedPath };
  action: 'preserve-and-inspect';
}

/** Las clasificaciones solo describen una distribución de rutas, no prueban contenido ni autoría. */
export function diagnoseReplaceFailure(failure: ReplaceFailure): RecoveryReport {
  const { code, destination, replacement, backup } = failure;
  let classification: RecoveryReport['classification'] = 'unverified';
  if ((code === 1175 || code === 1176) && destination.exists === true && replacement.exists === true && backup.exists === false) {
    classification = 'expected-original-paths';
  } else if (code === 1177 && destination.exists === false && replacement.exists === true && backup.exists === true) {
    classification = 'expected-backup-path';
  }
  return { code, classification, paths: { destination, replacement, backup }, action: 'preserve-and-inspect' };
}
