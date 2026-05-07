import { TopicForm } from "@/components/TopicForm";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Home() {
  return (
    <main className="relative flex flex-1 flex-col items-center justify-center bg-stone-50 px-6 py-12 dark:bg-stone-950">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>
      <div className="mb-12 max-w-2xl text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl dark:text-stone-100">
          Atlas
        </h1>
        <p className="text-lg text-slate-600 sm:text-xl dark:text-stone-400">
          Type any topic — history, biology, physics, anything — and get an
          interactive, hand-drawn diagram. Click any element to explore deeper.
        </p>
      </div>
      <TopicForm />
    </main>
  );
}
