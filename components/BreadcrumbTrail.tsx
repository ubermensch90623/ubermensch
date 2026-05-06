"use client";

import type { AtlasNode } from "@/types/atlas";

interface BreadcrumbTrailProps {
  stack: AtlasNode[];
  onJump: (depth: number) => void;
}

export function BreadcrumbTrail({ stack, onJump }: BreadcrumbTrailProps) {
  return (
    <nav className="flex flex-wrap items-center gap-1 text-sm">
      {stack.map((node, i) => {
        const isLast = i === stack.length - 1;
        return (
          <span key={node.id} className="flex items-center gap-1">
            {i > 0 && <span className="text-slate-400">›</span>}
            {isLast ? (
              <span className="font-medium text-slate-900">{node.title}</span>
            ) : (
              <button
                type="button"
                onClick={() => onJump(i)}
                className="rounded px-1 text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              >
                {node.title}
              </button>
            )}
          </span>
        );
      })}
    </nav>
  );
}
