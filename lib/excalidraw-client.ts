"use client";

import { convertToExcalidrawElements } from "@excalidraw/excalidraw";
import type { OrderedExcalidrawElement } from "@excalidraw/excalidraw/element/types";
import type { ClaudeNodeOutput } from "@/types/atlas";
import { claudeToSkeletons } from "./excalidraw";

export function claudeToExcalidraw(
  node: ClaudeNodeOutput,
): OrderedExcalidrawElement[] {
  const skeletons = claudeToSkeletons(node);
  return convertToExcalidrawElements(skeletons, { regenerateIds: false });
}
