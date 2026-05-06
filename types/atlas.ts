export type Format =
  | "history"
  | "biology"
  | "process"
  | "geography"
  | "concept";

export const FORMATS: readonly Format[] = [
  "history",
  "biology",
  "process",
  "geography",
  "concept",
] as const;

export type ClaudeElementKind =
  | "box"
  | "ellipse"
  | "arrow"
  | "text"
  | "region"
  | "icon";

export interface ClaudeElement {
  id: string;
  kind: ClaudeElementKind;
  label: string;
  x: number;
  y: number;
  w?: number;
  h?: number;
  from?: string;
  to?: string;
  expandable: boolean;
  childPrompt?: string;
}

export interface ClaudeNodeOutput {
  title: string;
  format: Format;
  summary: string;
  elements: ClaudeElement[];
}

export interface AtlasNode {
  id: string;
  atlasId: string;
  parentId: string | null;
  parentElementId: string | null;
  title: string;
  format: Format;
  summary: string;
  claudeElements: ClaudeElement[];
  createdAt: number;
}

export interface Atlas {
  id: string;
  rootNodeId: string;
  topic: string;
  createdAt: number;
  nodes: Record<string, AtlasNode>;
}

export interface ElementCustomData {
  semanticId: string;
  expandable: boolean;
  childPrompt?: string;
}
