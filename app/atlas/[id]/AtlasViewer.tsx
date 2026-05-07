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
import { useTheme } from "@/lib/use-theme";
import type { Atlas, AtlasNode, ElementCustomData } from "@/types/atlas";
import { BreadcrumbTrail } from "@/components/BreadcrumbTrail";
import { ShareBar } from "@/components/ShareBar";
import { LoadingOverlay } from "@/components/LoadingOverlay";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ExportMenu } from "@/components/ExportMenu";

const Excalidraw = dynamic(
  () => import("@excalidraw/excalidraw").then((m) => m.Excalidraw),
  { ssr: false, loading: () => <CanvasFallback /> },
);

function CanvasFallback() {
  return (
    <div className="flex h-full w-full items-center justify-center bg-stone-50 dark:bg-stone-900">
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
  const { theme } = useTheme();
  const isDark = theme === "dark";

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
    api.updateScene({
      elements,
      appState: {
        viewBackgroundColor: isDark ? "#1c1917" : "#fffaf0",
        theme: isDark ? "dark" : "light",
      },
    });
    api.scrollToContent(elements, {
      fitToContent: true,
      animate: true,
      duration: 400,
    });
  }, [elements, isDark]);

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

  const filename = useMemo(
    () =>
      `atlas-${currentNode.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "diagram"}`,
    [currentNode.title],
  );

  return (
    <div className="flex h-screen flex-col bg-stone-50 dark:bg-stone-950">
      <header className="flex items-center justify-between gap-2 border-b border-slate-200 bg-white px-3 py-3 sm:gap-4 sm:px-4 dark:border-stone-800 dark:bg-stone-900">
        <div className="flex min-w-0 items-center gap-2 sm:gap-3">
          <Link
            href="/"
            className="text-lg font-bold tracking-tight text-slate-900 hover:text-slate-700 dark:text-stone-100 dark:hover:text-stone-300"
          >
            Atlas
          </Link>
          <span className="hidden text-slate-300 sm:inline dark:text-stone-700">/</span>
          <span className="hidden truncate text-sm text-slate-500 sm:inline dark:text-stone-400">
            {atlas.topic}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
          <ExportMenu elements={elements} filename={filename} isDark={isDark} />
          <ThemeToggle />
          <ShareBar />
        </div>
      </header>

      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 bg-white px-3 py-2 sm:gap-3 sm:px-4 dark:border-stone-800 dark:bg-stone-900">
        <button
          type="button"
          onClick={handleBack}
          disabled={stack.length <= 1}
          className="rounded border border-slate-300 px-2 py-1 text-sm text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-stone-700 dark:text-stone-300 dark:hover:bg-stone-800"
          aria-label="Back"
        >
          ← Back
        </button>
        <BreadcrumbTrail stack={stackNodes} onJump={handleJump} />
        <span className="ml-auto hidden text-xs text-slate-500 sm:block dark:text-stone-500">
          {currentNode.format} · {currentNode.claudeElements.length} elements
        </span>
      </div>

      {currentNode.summary && (
        <div className="border-b border-slate-200 bg-stone-100 px-3 py-2 text-sm text-slate-600 sm:px-4 dark:border-stone-800 dark:bg-stone-900/50 dark:text-stone-400">
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
              viewBackgroundColor: isDark ? "#1c1917" : "#fffaf0",
              zenModeEnabled: false,
              viewModeEnabled: true,
              theme: isDark ? "dark" : "light",
            },
            scrollToContent: true,
          }}
          theme={isDark ? "dark" : "light"}
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
