"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { LoadingOverlay } from "./LoadingOverlay";

const EXAMPLES = [
  "How a CPU executes an instruction",
  "Photosynthesis",
  "프랑스 혁명",
  "Animal cell anatomy",
];

export function TopicForm() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(value: string) {
    const trimmed = value.trim();
    if (trimmed.length < 3 || trimmed.length > 200) {
      setError("Topic must be 3–200 characters.");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const res = await fetch("/api/atlas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: trimmed }),
      });
      const data = (await res.json()) as { id?: string; error?: string };
      if (!res.ok || !data.id) {
        throw new Error(data.error ?? `HTTP ${res.status}`);
      }
      router.push(`/atlas/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setSubmitting(false);
    }
  }

  return (
    <>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void submit(topic);
        }}
        className="flex w-full max-w-xl flex-col gap-3"
      >
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter any topic..."
          disabled={submitting}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-lg shadow-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200 disabled:opacity-50"
          autoFocus
        />
        <button
          type="submit"
          disabled={submitting || topic.trim().length < 3}
          className="rounded-lg bg-slate-900 px-6 py-3 text-lg font-medium text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Generate diagram
        </button>
        {error && <p className="text-sm text-red-600">{error}</p>}
      </form>

      <div className="mt-6 flex w-full max-w-xl flex-wrap gap-2">
        <span className="text-sm text-slate-500">Try:</span>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            type="button"
            disabled={submitting}
            onClick={() => {
              setTopic(ex);
              void submit(ex);
            }}
            className="rounded-full border border-slate-300 bg-white px-3 py-1 text-sm text-slate-700 transition hover:border-slate-500 hover:bg-slate-50 disabled:opacity-50"
          >
            {ex}
          </button>
        ))}
      </div>

      {submitting && (
        <LoadingOverlay
          message="Drawing your diagram…"
          hint="This usually takes 5–10 seconds."
        />
      )}
    </>
  );
}
