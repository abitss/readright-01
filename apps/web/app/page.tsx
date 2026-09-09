import Link from "next/link";
import { ReadRightMark } from "@/components/brand/readright-mark";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-8 md:px-10">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-6xl flex-col">
        <header className="flex items-center justify-between">
          <ReadRightMark />
          <span className="rounded-full border border-[var(--rr-border)] bg-white px-3 py-1 text-xs font-medium text-[var(--rr-muted)]">
            Platform foundation
          </span>
        </header>

        <section className="grid flex-1 items-center gap-12 py-16 lg:grid-cols-[1.15fr_.85fr]">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full bg-[var(--rr-orange-soft)] px-3 py-1 text-sm font-semibold text-[var(--rr-orange-deep)]">
              Learning Intelligence Infrastructure
            </span>
            <h1 className="mt-6 max-w-3xl text-5xl font-semibold tracking-[-0.045em] text-[var(--rr-ink)] md:text-7xl">
              Understand the barrier. Take the next action. Verify learning.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-[var(--rr-muted)]">
              ReadRight turns learner evidence into a clear learning picture so teachers can decide what to do next without reducing a child to a score.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link className="rr-flame-button" href="/teacher">
                Open teacher workspace
              </Link>
              <Link className="rr-secondary-button" href="/child/assessment">
                Preview assessment player
              </Link>
            </div>
          </div>

          <div className="rr-brand-panel relative overflow-hidden p-8 md:p-10">
            <div className="rr-arc" aria-hidden="true" />
            <div className="relative z-10">
              <div className="rr-spark mb-8" aria-hidden="true">✦</div>
              <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[var(--rr-muted)]">The ReadRight loop</p>
              <div className="mt-6 space-y-4">
                {[
                  ["01", "Evidence"],
                  ["02", "Understanding"],
                  ["03", "Action"],
                  ["04", "Verification"],
                ].map(([number, label]) => (
                  <div key={label} className="flex items-center gap-4 border-b border-[var(--rr-border)] pb-4 last:border-0">
                    <span className="text-xs font-semibold text-[var(--rr-orange)]">{number}</span>
                    <span className="text-xl font-semibold tracking-tight">{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
