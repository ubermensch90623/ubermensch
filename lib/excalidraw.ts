import type { ExcalidrawElementSkeleton } from "@excalidraw/excalidraw/data/transform";
import type {
  ClaudeElement,
  ClaudeElementKind,
  ClaudeNodeOutput,
  ElementCustomData,
  Format,
} from "@/types/atlas";

const SCALE = 1.4;
const PADDING = 50;
const ROUGHNESS = 2;
const ROUNDNESS_ADAPTIVE = { type: 3 } as const;

const FORMAT_STROKE: Record<Format, string> = {
  history: "#7c4a1f",
  biology: "#0f766e",
  process: "#1e40af",
  geography: "#a3441b",
  concept: "#7c3aed",
};

const FORMAT_REGION_BG: Record<Format, string> = {
  history: "#f4ecd8",
  biology: "#ecfdf5",
  process: "#eff6ff",
  geography: "#fef3c7",
  concept: "#faf5ff",
};

function defaultDims(kind: ClaudeElementKind): { w: number; h: number } {
  switch (kind) {
    case "box":
      return { w: 140, h: 70 };
    case "ellipse":
      return { w: 120, h: 120 };
    case "region":
      return { w: 280, h: 180 };
    case "icon":
      return { w: 50, h: 50 };
    case "text":
    case "arrow":
      return { w: 0, h: 0 };
  }
}

function toCustomData(el: ClaudeElement): ElementCustomData {
  return {
    semanticId: el.id,
    expandable: el.expandable,
    childPrompt: el.childPrompt,
  };
}

export function claudeToSkeletons(
  node: ClaudeNodeOutput,
): ExcalidrawElementSkeleton[] {
  const stroke = FORMAT_STROKE[node.format];
  const regionBg = FORMAT_REGION_BG[node.format];

  const skeletons: ExcalidrawElementSkeleton[] = [];
  const shapeIds = new Set<string>();

  for (const el of node.elements) {
    if (el.kind === "arrow") continue;
    const skel = buildShape(el, stroke, regionBg);
    if (skel) {
      skeletons.push(skel);
      shapeIds.add(el.id);
    }
  }

  for (const el of node.elements) {
    if (el.kind !== "arrow") continue;
    const arrow = buildArrow(el, stroke, shapeIds);
    if (arrow) skeletons.push(arrow);
  }

  return skeletons;
}

function buildShape(
  el: ClaudeElement,
  stroke: string,
  regionBg: string,
): ExcalidrawElementSkeleton | null {
  const { w: dw, h: dh } = defaultDims(el.kind);
  const w = el.w ?? dw;
  const h = el.h ?? dh;
  const x = (el.x - w / 2) * SCALE + PADDING;
  const y = (el.y - h / 2) * SCALE + PADDING;
  const customData = toCustomData(el);

  const baseProps = {
    id: el.id,
    x,
    y,
    width: w * SCALE,
    height: h * SCALE,
    strokeColor: stroke,
    roughness: ROUGHNESS,
    roundness: ROUNDNESS_ADAPTIVE,
    customData,
  } as const;

  switch (el.kind) {
    case "box":
      return {
        type: "rectangle",
        ...baseProps,
        ...(el.label ? { label: { text: el.label, fontSize: 16 } } : {}),
      };
    case "ellipse":
      return {
        type: "ellipse",
        ...baseProps,
        ...(el.label ? { label: { text: el.label, fontSize: 16 } } : {}),
      };
    case "region":
      return {
        type: "rectangle",
        ...baseProps,
        backgroundColor: regionBg,
        fillStyle: "hachure",
        ...(el.label ? { label: { text: el.label, fontSize: 18 } } : {}),
      };
    case "icon":
      return {
        type: "ellipse",
        ...baseProps,
        strokeWidth: 2,
      };
    case "text":
      return {
        type: "text",
        text: el.label,
        x,
        y,
        fontSize: 18,
        strokeColor: stroke,
        id: el.id,
        customData,
      };
    case "arrow":
      return null;
  }
}

function buildArrow(
  el: ClaudeElement,
  stroke: string,
  shapeIds: Set<string>,
): ExcalidrawElementSkeleton | null {
  if (!el.from || !el.to) return null;
  if (!shapeIds.has(el.from) || !shapeIds.has(el.to)) return null;
  return {
    type: "arrow",
    x: 0,
    y: 0,
    strokeColor: stroke,
    roughness: ROUGHNESS,
    start: { id: el.from },
    end: { id: el.to },
    customData: toCustomData(el),
  };
}
