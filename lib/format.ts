import type { ClaudeElement, ClaudeNodeOutput } from "@/types/atlas";

const CANVAS_CENTER = { x: 500, y: 500 };
const PROCESS_X_MIN = 100;
const PROCESS_X_MAX = 900;
const PROCESS_Y = 500;
const CONCEPT_RADIUS = 320;
const HISTORY_BASELINE_Y = 850;

export function applyLayoutTemplate(
  node: ClaudeNodeOutput,
): ClaudeNodeOutput {
  switch (node.format) {
    case "process":
      return applyProcessLayout(node);
    case "concept":
      return applyConceptLayout(node);
    case "history":
      return applyHistoryLayout(node);
    case "biology":
      return applyBiologyLayout(node);
    case "geography":
      return applyGeographyLayout(node);
    default:
      return node;
  }
}

function applyProcessLayout(node: ClaudeNodeOutput): ClaudeNodeOutput {
  const stepIds = new Set<string>();
  const inDegree = new Map<string, number>();
  const outEdges = new Map<string, string[]>();

  for (const el of node.elements) {
    if (el.kind !== "arrow" || !el.from || !el.to) continue;
    stepIds.add(el.from);
    stepIds.add(el.to);
    if (!inDegree.has(el.from)) inDegree.set(el.from, 0);
    inDegree.set(el.to, (inDegree.get(el.to) ?? 0) + 1);
    outEdges.set(el.from, [...(outEdges.get(el.from) ?? []), el.to]);
  }

  if (stepIds.size < 2) return node;

  const localInDegree = new Map(inDegree);
  const queue: string[] = [];
  for (const [id, deg] of localInDegree) {
    if (deg === 0) queue.push(id);
  }

  const order: string[] = [];
  while (queue.length > 0) {
    const id = queue.shift() as string;
    order.push(id);
    for (const next of outEdges.get(id) ?? []) {
      const d = (localInDegree.get(next) ?? 0) - 1;
      localInDegree.set(next, d);
      if (d === 0) queue.push(next);
    }
  }

  if (order.length !== stepIds.size) return node;

  const idToX = new Map<string, number>();
  if (order.length === 1) {
    idToX.set(order[0], CANVAS_CENTER.x);
  } else {
    const spacing = (PROCESS_X_MAX - PROCESS_X_MIN) / (order.length - 1);
    order.forEach((id, i) => {
      idToX.set(id, PROCESS_X_MIN + i * spacing);
    });
  }

  const elements: ClaudeElement[] = node.elements.map((el) => {
    if (el.kind === "arrow") return el;
    const x = idToX.get(el.id);
    if (x === undefined) return el;
    return { ...el, x, y: PROCESS_Y };
  });

  return { ...node, elements };
}

function applyConceptLayout(node: ClaudeNodeOutput): ClaudeNodeOutput {
  const shapes = node.elements.filter((e) => e.kind !== "arrow");
  if (shapes.length < 2) return node;

  let central = shapes[0];
  let centralArea = areaOf(shapes[0]);
  for (const s of shapes) {
    const a = areaOf(s);
    if (a > centralArea) {
      central = s;
      centralArea = a;
    }
  }

  const satellites = shapes.filter((s) => s.id !== central.id);
  const angleStep = (2 * Math.PI) / satellites.length;
  const positions = new Map<string, { x: number; y: number }>();
  positions.set(central.id, { ...CANVAS_CENTER });
  satellites.forEach((s, i) => {
    const angle = i * angleStep - Math.PI / 2;
    positions.set(s.id, {
      x: Math.round(CANVAS_CENTER.x + CONCEPT_RADIUS * Math.cos(angle)),
      y: Math.round(CANVAS_CENTER.y + CONCEPT_RADIUS * Math.sin(angle)),
    });
  });

  const elements: ClaudeElement[] = node.elements.map((el) => {
    if (el.kind === "arrow") return el;
    const p = positions.get(el.id);
    return p ? { ...el, x: p.x, y: p.y } : el;
  });

  return { ...node, elements };
}

function applyHistoryLayout(node: ClaudeNodeOutput): ClaudeNodeOutput {
  const stepIds = new Set<string>();
  const inDegree = new Map<string, number>();
  const outEdges = new Map<string, string[]>();

  for (const el of node.elements) {
    if (el.kind !== "arrow" || !el.from || !el.to) continue;
    stepIds.add(el.from);
    stepIds.add(el.to);
    if (!inDegree.has(el.from)) inDegree.set(el.from, 0);
    inDegree.set(el.to, (inDegree.get(el.to) ?? 0) + 1);
    outEdges.set(el.from, [...(outEdges.get(el.from) ?? []), el.to]);
  }

  if (stepIds.size < 2) return node;

  const localInDegree = new Map(inDegree);
  const queue: string[] = [];
  for (const [id, deg] of localInDegree) {
    if (deg === 0) queue.push(id);
  }

  const order: string[] = [];
  while (queue.length > 0) {
    const id = queue.shift() as string;
    order.push(id);
    for (const next of outEdges.get(id) ?? []) {
      const d = (localInDegree.get(next) ?? 0) - 1;
      localInDegree.set(next, d);
      if (d === 0) queue.push(next);
    }
  }

  if (order.length !== stepIds.size) return node;

  const idToX = new Map<string, number>();
  if (order.length === 1) {
    idToX.set(order[0], CANVAS_CENTER.x);
  } else {
    const spacing = (PROCESS_X_MAX - PROCESS_X_MIN) / (order.length - 1);
    order.forEach((id, i) => {
      idToX.set(id, PROCESS_X_MIN + i * spacing);
    });
  }

  const elements: ClaudeElement[] = node.elements.map((el) => {
    if (el.kind === "arrow") return el;
    const x = idToX.get(el.id);
    if (x === undefined) return el;
    return { ...el, x, y: HISTORY_BASELINE_Y };
  });

  return { ...node, elements };
}

function applyBiologyLayout(node: ClaudeNodeOutput): ClaudeNodeOutput {
  const shapes = node.elements.filter((e) => e.kind !== "arrow");
  if (shapes.length < 2) return node;

  let central = shapes[0];
  let centralArea = areaOf(shapes[0]);
  for (const s of shapes) {
    const a = areaOf(s);
    if (a > centralArea) {
      central = s;
      centralArea = a;
    }
  }

  if (central.x === CANVAS_CENTER.x && central.y === CANVAS_CENTER.y) {
    return node;
  }

  const dx = CANVAS_CENTER.x - central.x;
  const dy = CANVAS_CENTER.y - central.y;
  const elements: ClaudeElement[] = node.elements.map((el) => {
    if (el.kind === "arrow") return el;
    if (el.id === central.id) {
      return { ...el, x: CANVAS_CENTER.x, y: CANVAS_CENTER.y };
    }
    const newX = clamp(el.x + dx * 0.5, 50, 950);
    const newY = clamp(el.y + dy * 0.5, 50, 950);
    return { ...el, x: newX, y: newY };
  });

  return { ...node, elements };
}

function applyGeographyLayout(node: ClaudeNodeOutput): ClaudeNodeOutput {
  const regions: ClaudeElement[] = [];
  const others: ClaudeElement[] = [];
  for (const el of node.elements) {
    if (el.kind === "region") regions.push(el);
    else others.push(el);
  }
  if (regions.length === 0) return node;
  return { ...node, elements: [...regions, ...others] };
}

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

function areaOf(el: ClaudeElement): number {
  const w = el.w ?? defaultDim(el.kind, "w");
  const h = el.h ?? defaultDim(el.kind, "h");
  return w * h;
}

function defaultDim(kind: ClaudeElement["kind"], axis: "w" | "h"): number {
  switch (kind) {
    case "box":
      return axis === "w" ? 140 : 70;
    case "ellipse":
      return 120;
    case "region":
      return axis === "w" ? 280 : 180;
    case "icon":
      return 50;
    case "text":
    case "arrow":
      return 0;
  }
}
