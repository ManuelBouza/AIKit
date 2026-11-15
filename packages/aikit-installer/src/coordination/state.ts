import { canonical, type Notice, type Query, type Task } from './schema.js';

export function decide(
  source: Task,
  incoming: Notice,
  allTasks: Task[],
  operationId: string,
  recordedAt: string,
): { task: Task; query: Query; changed: boolean } {
  const next = structuredClone(source);
  const query: Query = {
    schemaVersion: 1,
    projectId: source.projectId,
    taskId: source.taskId,
    updateId: incoming.updateId,
    result: 'incierto',
    receipt: null,
    incidentId: null,
    generation: source.generation,
    reason: null,
  };
  const receiptTask = allTasks.find((t) =>
    t.receipts.some((r) => r.updateId === incoming.updateId),
  );
  const originalReceipt = receiptTask?.receipts.find((r) => r.updateId === incoming.updateId);
  const existingTask =
    receiptTask ??
    allTasks.find((t) => t.incidents.some((i) => i.notice.updateId === incoming.updateId));
  const existing =
    originalReceipt ??
    existingTask?.incidents.find((i) => i.notice.updateId === incoming.updateId)?.notice;
  if (
    originalReceipt &&
    existingTask?.taskId === source.taskId &&
    canonical(originalReceipt.notice) === canonical(incoming)
  )
    return {
      task: source,
      query: { ...query, result: 'duplicado', receipt: originalReceipt },
      changed: false,
    };
  const incompatible = [
    ...source.receipts.map((r) => r.notice),
    ...source.incidents.map((i) => i.notice),
  ].find(
    (n) =>
      n.senderChatId === incoming.senderChatId &&
      n.cycle === incoming.cycle &&
      n.revision === incoming.revision &&
      canonical(n) !== canonical(incoming),
  );
  if (existing || incompatible) {
    const conflict = existing ?? incompatible!;
    const prior = source.incidents.find((i) => canonical(i.notice) === canonical(incoming));
    if (prior)
      return {
        task: source,
        query: {
          ...query,
          result: 'conflicto',
          incidentId: prior.incidentId,
          reason: prior.reason,
        },
        changed: false,
      };
    const incident = {
      incidentId: operationId,
      notice: incoming,
      conflictsWithUpdateId: conflict.updateId,
      reason: existing ? 'ID utilizado con otro contenido o tarea' : 'Revisión incompatible',
      operationId,
      recordedAt,
      ...(existingTask && existingTask.taskId !== source.taskId
        ? { conflictsWithTaskId: existingTask.taskId }
        : {}),
    };
    next.incidents.push(incident);
    next.generation++;
    return {
      task: next,
      query: {
        ...query,
        result: 'conflicto',
        incidentId: incident.incidentId,
        reason: incident.reason,
        generation: next.generation,
      },
      changed: true,
    };
  }
  const decision =
    incoming.cycle !== source.activeCycle || incoming.senderChatId !== source.assignedChatId
      ? 'pendiente'
      : source.current && incoming.revision < source.current.revision
        ? 'antiguo'
        : 'aplicado';
  if (decision === 'aplicado')
    next.current = {
      cycle: incoming.cycle,
      revision: incoming.revision,
      state: incoming.state,
      updateId: incoming.updateId,
    };
  const receipt = {
    updateId: incoming.updateId,
    notice: incoming,
    decision,
    resultingCurrent: structuredClone(next.current),
    operationId,
    recordedAt,
    history: [],
  } as const;
  next.receipts.push({ ...receipt, history: [] });
  next.generation++;
  return {
    task: next,
    query: {
      ...query,
      result: decision,
      receipt: { ...receipt, history: [] },
      generation: next.generation,
    },
    changed: true,
  };
}
