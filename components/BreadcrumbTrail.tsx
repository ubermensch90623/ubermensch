"use client";

import type { AtlasNode } from "@/types/atlas";

interface BreadcrumbTrailProps {
  stack: AtlasNode[];
  onJump: (depth: number) => void;
}

export function BreadcrumbTrail({ stack, onJump }: BreadcrumbTrailProps) {
  const collapsed = stack.length > 3;
  const visible = collapsed
    ? [stack[0], stack[stack.length - 2], stack[stack.length - 1]]
    : stack;

  return (
    <nav className="flex flex-wrap items-center gap-1 text-sm">
      {visible.map((node, i) => {
        const realIndex = collapsed
          ? i === 0
            ? 0
            : i === 1
              ? stack.length - 2
              : stack.length - 1
          : i;
        const isLast = realIndex === stack.length - 1;
        const showEllipsis = collapsed && i === 1 && stack.length > 3;
        return (
          <span key={node.id} className="flex items-center gap-1">
            {i > 0 && (
              <span className="text-slate-400 dark:text-stone-600">›</span>
            )}
            {showEllipsis && (
              <>
                <span className="text-slate-400 dark:text-stone-600">…</span>
                <span className="text-slate-400 dark:text-stone-600">›</span>
              </>
            )}
            {isLast ? (
              <span className="max-w-[14rem] truncate font-medium text-slate-900 dark:text-stone-100">
                {node.title}
              </span>
            ) : (
              <button
                type="button"
                onClick={() => onJump(realIndex)}
                className="max-w-[10rem] truncate rounded px-1 text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 dark:text-stone-400 dark:hover:bg-stone-800 dark:hover:text-stone-200"
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
