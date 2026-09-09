import Link from "next/link";
import { BookOpen, CheckCircle2, CircleHelp, ClipboardCheck, Home, Search, Sparkles, Users } from "lucide-react";
import { ReadRightMark } from "@/components/brand/readright-mark";

const nav = [
  ["Today", Home],
  ["Learners", Users],
  ["Assess", Search],
  ["Teach", BookOpen],
  ["Verify", ClipboardCheck],
];

export default function TeacherPage() {
  return (
    <main className="min-h-screen bg-[var(--rr-background)] md:grid md:grid-cols-[240px_1fr]">
      <aside className="hidden min-h-screen border-r border-[var(--rr-border)] bg-white p-5 md:flex md:flex-col">
        <ReadRightMark />
        <nav className="mt-10 space-y-1">
          {nav.map(([label, Icon], index) => (
            <div
              key={String(label)}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${index === 0 ? "bg-[var(--rr-orange-soft)] text-[var(--rr-ink)]" : "text-[var(--rr-muted)]"}`}
            >
              <Icon size={18} strokeWidth={1.8} />
              {label as string}
            </div>
          ))}
        </nav>
        <div className="mt-auto rounded-2xl border border-[var(--rr-border)] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--rr-muted)]">Pilot principle</p>
          <p className="mt-2 text-sm leading-6">AI assists. Evidence decides.</p>
        </div>
      </aside>

      <section className="px-5 py-6 md:px-10 md:py-8">
        <header className="flex items-center justify-between md:hidden">
          <ReadRightMark compact />
          <span className="text-sm font-medium">Teacher</span>
        </header>

        <div className="mx-auto max-w-6xl">
          <div className="mt-8 flex flex-col gap-4 md:mt-0 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm font-semibold text-[var(--rr-orange-deep)]">Today</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em] md:text-4xl">What needs your attention</h1>
              <p className="mt-2 text-[var(--rr-muted)]">A calm view of the next best teacher actions.</p>
            </div>
            <Link href="/child/assessment" className="rr-flame-button self-start">Start assessment</Link>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <Metric icon={Sparkles} value="4" label="Need action" />
            <Metric icon={ClipboardCheck} value="3" label="Need verification" />
            <Metric icon={CircleHelp} value="2" label="Need evidence" />
          </div>

          <section className="mt-10">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Priority learners</h2>
              <span className="text-sm text-[var(--rr-muted)]">Teacher-first view</span>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-2">
              <LearnerCard
                name="Aarav"
                why="Phoneme blending"
                evidence="Strong evidence"
                action="8-minute blending routine"
              />
              <LearnerCard
                name="Meera"
                why="More evidence needed"
                evidence="Current evidence is mixed"
                action="Run a 3-minute focused probe"
              />
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function Metric({ icon: Icon, value, label }: { icon: typeof Sparkles; value: string; label: string }) {
  return (
    <div className="rr-card flex items-center gap-4 p-5">
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-[var(--rr-orange-soft)] text-[var(--rr-orange)]">
        <Icon size={19} strokeWidth={1.8} />
      </div>
      <div>
        <div className="text-2xl font-semibold tracking-[-0.04em]">{value}</div>
        <div className="text-sm text-[var(--rr-muted)]">{label}</div>
      </div>
    </div>
  );
}

function LearnerCard({ name, why, evidence, action }: { name: string; why: string; evidence: string; action: string }) {
  return (
    <article className="rr-card overflow-hidden">
      <div className="h-1 bg-[var(--rr-flame)]" />
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">{name}</h3>
          <CheckCircle2 size={18} className="text-[var(--rr-muted)]" />
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          <Decision label="WHY" value={why} />
          <Decision label="EVIDENCE" value={evidence} />
          <Decision label="DO" value={action} accent />
        </div>
      </div>
    </article>
  );
}

function Decision({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <p className={`text-[11px] font-bold tracking-[0.13em] ${accent ? "text-[var(--rr-orange)]" : "text-[var(--rr-muted)]"}`}>{label}</p>
      <p className="mt-2 text-sm font-medium leading-6">{value}</p>
    </div>
  );
}
