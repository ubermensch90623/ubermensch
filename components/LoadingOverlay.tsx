interface LoadingOverlayProps {
  message: string;
  hint?: string;
}

export function LoadingOverlay({ message, hint }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-3 rounded-lg bg-white px-8 py-6 shadow-xl">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-700" />
        <p className="text-base font-medium text-slate-800">{message}</p>
        {hint && <p className="text-sm text-slate-500">{hint}</p>}
      </div>
    </div>
  );
}
