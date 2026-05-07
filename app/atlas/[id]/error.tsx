"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function AtlasError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[atlas viewer error]", error);
  }, [error]);

  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-stone-50 px-6 py-12 text-center dark:bg-stone-950">
      <h1 className="mb-3 text-3xl font-bold text-slate-900 dark:text-stone-100">
        Something broke
      </h1>
      <p className="mb-6 max-w-md text-slate-600 dark:text-stone-400">
        The viewer hit an unexpected error: {error.message}
      </p>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={reset}
          className="rounded-lg bg-slate-900 px-5 py-2.5 text-white transition hover:bg-slate-800 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-200"
        >
          Try again
        </button>
        <Link
          href="/"
          className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-slate-800 transition hover:bg-slate-50 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200 dark:hover:bg-stone-800"
        >
          Home
        </Link>
      </div>
    </main>
  );
}
