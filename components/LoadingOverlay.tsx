interface LoadingOverlayProps {
  message: string;
  hint?: string;
}

export function LoadingOverlay({ message, hint }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-3 rounded-lg bg-white px-8 py-6 shadow-xl dark:bg-stone-900">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-700 dark:border-stone-700 dark:border-t-stone-200" />
        <p className="text-base font-medium text-slate-800 dark:text-stone-100">
          {message}
        </p>
        {hint && (
          <p className="text-sm text-slate-500 dark:text-stone-400">{hint}</p>
        )}
      </div>
    </div>
  );
}
