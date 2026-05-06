import Link from "next/link";

export default function AtlasNotFound() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-stone-50 px-6 py-12 text-center">
      <h1 className="mb-3 text-3xl font-bold text-slate-900">
        Atlas not found
      </h1>
      <p className="mb-6 max-w-md text-slate-600">
        This diagram doesn&apos;t exist or has been removed. The link may have
        a typo, or the atlas was created on a different machine.
      </p>
      <Link
        href="/"
        className="rounded-lg bg-slate-900 px-5 py-2.5 text-white transition hover:bg-slate-800"
      >
        Generate a new diagram
      </Link>
    </main>
  );
}
