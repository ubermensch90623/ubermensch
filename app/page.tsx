import { TopicForm } from "@/components/TopicForm";

export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center bg-stone-50 px-6 py-12">
      <div className="mb-12 max-w-2xl text-center">
        <h1 className="mb-4 text-5xl font-bold tracking-tight text-slate-900">
          Atlas
        </h1>
        <p className="text-xl text-slate-600">
          Type any topic — history, biology, physics, anything — and get an
          interactive, hand-drawn diagram. Click any element to explore deeper.
        </p>
      </div>
      <TopicForm />
    </main>
  );
}
