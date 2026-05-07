"use client";

import { useState } from "react";
import type { OrderedExcalidrawElement } from "@excalidraw/excalidraw/element/types";

interface ExportMenuProps {
  elements: OrderedExcalidrawElement[];
  filename: string;
  isDark: boolean;
}

export function ExportMenu({ elements, filename, isDark }: ExportMenuProps) {
  const [busy, setBusy] = useState<"png" | "svg" | null>(null);

  async function downloadPng() {
    setBusy("png");
    try {
      const { exportToBlob } = await import("@excalidraw/excalidraw");
      const blob = await exportToBlob({
        elements,
        appState: {
          exportBackground: true,
          viewBackgroundColor: isDark ? "#1c1917" : "#fffaf0",
          theme: isDark ? "dark" : "light",
        },
        files: null,
        mimeType: "image/png",
      });
      triggerDownload(blob, `${filename}.png`);
    } finally {
      setBusy(null);
    }
  }

  async function downloadSvg() {
    setBusy("svg");
    try {
      const { exportToSvg } = await import("@excalidraw/excalidraw");
      const svg = await exportToSvg({
        elements,
        appState: {
          exportBackground: true,
          viewBackgroundColor: isDark ? "#1c1917" : "#fffaf0",
          theme: isDark ? "dark" : "light",
        },
        files: null,
      });
      const xml = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([xml], { type: "image/svg+xml" });
      triggerDownload(blob, `${filename}.svg`);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        onClick={downloadPng}
        disabled={busy !== null || elements.length === 0}
        className="rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-700 transition hover:border-slate-500 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:border-stone-500 dark:hover:bg-stone-800"
      >
        {busy === "png" ? "…" : "PNG"}
      </button>
      <button
        type="button"
        onClick={downloadSvg}
        disabled={busy !== null || elements.length === 0}
        className="rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-700 transition hover:border-slate-500 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:border-stone-500 dark:hover:bg-stone-800"
      >
        {busy === "svg" ? "…" : "SVG"}
      </button>
    </div>
  );
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
