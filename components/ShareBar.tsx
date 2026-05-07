"use client";

import { useState } from "react";

export function ShareBar() {
  const [copied, setCopied] = useState(false);

  async function copy() {
    if (typeof window === "undefined") return;
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore
    }
  }

  return (
    <button
      type="button"
      onClick={copy}
      className="rounded-md border border-slate-300 bg-white px-2.5 py-1.5 text-sm text-slate-700 transition hover:border-slate-500 hover:bg-slate-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:border-stone-500 dark:hover:bg-stone-800"
    >
      {copied ? "Copied!" : "Copy URL"}
    </button>
  );
}
