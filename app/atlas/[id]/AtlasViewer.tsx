"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import "@excalidraw/excalidraw/index.css";
import type { OrderedExcalidrawElement } from "@excalidraw/excalidraw/element/types";
import type {
  ExcalidrawImperativeAPI,
  PointerDownState,
  AppState,
} from "@excalidraw/excalidraw/types";
import { claudeToExcalidraw } from "@/lib/excalidraw-client";
import type { Atlas, AtlasNode, ElementCustomData } from "@/types/atlas";
import { BreadcrumbTrail } from "@/components/BreadcrumbTrail";
import { ShareBar } from "@/components/ShareBar";
import { LoadingOverlay } from "@/components/LoadingOverlay";

const Excalidraw = dynamic(
  () => import("@excalidraw/excalidraw").then((m) => m.Excalidraw),
  { ssr: false, loading: () => <CanvasFallback /> },
);

function CanvasFallback() {
  return (
    <div className="flex h-full w-full items-center justify-center bg-stone-50">
      <p className="text-slate-500">Loading canvas…</p>
    </div>
  );
}

interface AtlasViewerProps {
  atlas: Atlas;
}

export function AtlasViewer({ atlas: initialAtlas }: AtlasViewerProps) {
  const [atlas, setAtlas] = useState<Atlas>(initialAtlas);
  const [stack, setStack] = useState<string[]>([initialAtlas.rootNodeId]);
  const [expanding, setExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiRef = useRef<ExcalidrawImperativeAPI | null>(null);

  const currentNodeId = stack[stack.length - 1];
  const currentNode: AtlasNode = atlas.nodes[currentNodeId];

  const stackNodes = useMemo(
    () => stack.map((id) => atlas.nodes[id]).filter(Boolean),
    [stack, atlas.nodes],
  );

  const elements: OrderedExcalidrawElement[] = useMemo(
    () =>
      claudeToExcalidraw({
        title: currentNode.title,
        format: currentNode.format,
        summary: currentNode.summary,
        elements: currentNode.claudeElements,
      }),
    [currentNode],
  );

  useEffect(() => {
    const api = apiRef.current;
    if (!api) return;
    api.updateScene({ elements });
    api.scrollToContent(elements, {
      fitToContent: true,
      animate: true,
      duration: 400,
    });
  }, [elements]);

  const expand = useCallback(
    async (parentNodeId: string, parentElementId: string) => {
      if (expanding) return;
      setError(null);
      setExpanding(true);
      try {
        const res = await fetch(`/api/atlas/${atlas.id}/expand`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ parentNodeId, parentElementId }),
        });
        const data = (await res.json()) as {
          node?: AtlasNode;
          error?: string;
        };
        if (!res.ok || !data.node) {
          throw new Error(data.error ?? `HTTP ${res.status}`);
        }
        const child = data.node;
        setAtlas((prev) => ({
          ...prev,
          nodes: { ...prev.nodes, [child.id]: child },
        }));
        setStack((prev) => [...prev, child.id]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Expand failed");
      } finally {
        setExpanding(false);
      }
    },
    [atlas.id, expanding],
  );

  const handlePointerDown = useCallback(
    (
      _activeTool: AppState["activeTool"],
      pointerDownState: PointerDownState,
    ) => {
      const hit = pointerDownState.hit.element;
      if (!hit) return;
      const cd = hit.customData as ElementCustomData | undefined;
      if (!cd?.expandable) return;
      void expand(currentNodeId, cd.semanticId);
    },
    [expand, currentNodeId],
  );

  const handleBack = useCallback(() => {
    setStack((prev) => (prev.length > 1 ? prev.slice(0, -1) : prev));
  }, []);

  const handleJump = useCallback((depth: number) => {
    setStack((prev) => prev.slice(0, depth + 1));
  }, []);

  return (
    <div className="flex h-screen flex-col bg-stone-50">
      <header className="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 py-3">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="text-lg font-bold tracking-tight text-slate-900 hover:text-slate-700"
          >
            Atlas
          </Link>
          <span className="text-slate-300">/</span>
          <span className="text-sm text-slate-500">{atlas.topic}</span>
        </div>
        <ShareBar />
      </header>

      <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-2">
        <button
          type="button"
          onClick={handleBack}
          disabled={stack.length <= 1}
          className="rounded border border-slate-300 px-2 py-1 text-sm text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
          aria-label="Back"
        >
          ← Back
        </button>
        <BreadcrumbTrail stack={stackNodes} onJump={handleJump} />
        <span className="ml-auto text-xs text-slate-500">
          {currentNode.format} · {currentNode.claudeElements.length} elements
        </span>
      </div>

      {currentNode.summary && (
        <div className="border-b border-slate-200 bg-stone-100 px-4 py-2 text-sm text-slate-600">
          {currentNode.summary}
        </div>
      )}

      <div className="relative flex-1">
        <Excalidraw
          excalidrawAPI={(api) => {
            apiRef.current = api;
          }}
          initialData={{
            elements,
            appState: {
              viewBackgroundColor: "#fffaf0",
              zenModeEnabled: false,
              viewModeEnabled: true,
            },
            scrollToContent: true,
          }}
          viewModeEnabled
          onPointerDown={handlePointerDown}
          UIOptions={{
            canvasActions: {
              changeViewBackgroundColor: false,
              clearCanvas: false,
              export: false,
              loadScene: false,
              saveAsImage: false,
              saveToActiveFile: false,
              toggleTheme: false,
            },
            tools: { image: false },
          }}
        />
        {error && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-md bg-red-600 px-4 py-2 text-sm text-white shadow-lg">
            {error}
          </div>
        )}
        {expanding && (
          <LoadingOverlay
            message="Drilling deeper…"
            hint="Loading the next layer."
          />
        )}
      </div>
    </div>
  );
}
