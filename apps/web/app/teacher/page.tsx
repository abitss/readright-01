import Link from "next/link";
import {
  BookOpen,
  CircleHelp,
  ClipboardCheck,
  Home,
  Search,
  Sparkles,
  Users,
} from "lucide-react";
import { ReadRightMark } from "@/components/brand/readright-mark";
import {
  getClassPlan,
  getLearners,
  getTeacherDecision,
  type ClassPlan,
  type TeacherDecision,
} from "@/lib/readright-api";

const nav = [
  ["Today", Home],
  ["Learners", Users],
  ["Assess", Search],
  ["Teach", BookOpen],
  ["Verify", ClipboardCheck],
] as const;

export const dynamic = "force-dynamic";

export default async function TeacherPage() {
  let decisions: TeacherDecision[] = [];
  let plan: ClassPlan | null = null;
  let engineOnline = true;

  try {
    const learners = await getLearners();
    decisions = await Promise.all(learners.map((learner) => getTeacherDecision(learner.learner_id)));
    if (learners.length > 0) {
      plan = await getClassPlan(learners.map((learner) => learner.learner_id), 30);
    }
  } catch {
    engineOnline = false;
  }

  const needAction = decisions.filter((item) => item.outcome === "ACTION_READY").length;
  const needVerify = decisions.filter((item) => item.outcome === "VERIFY_DUE").length;
  const needEvidence = decisions.filter((item) => ["MORE_EVIDENCE", "CONFLICTING"].includes(item.outcome)).length;
  const priority = decisions.filter((item) => item.outcome !== "NO_ACTION");

  return (
    <main className="min-h-screen bg-[var(--rr-background)] md:grid md:grid-cols-[240px_1fr]">
      <aside className="hidden min-h-screen border-r border-[var(--rr-border)] bg-white p-5 md:flex md:flex-col">
        <ReadRightMark />
        <nav className="mt-10 space-y-1">
          {nav.map(([label, Icon], index) => (
            <div
              key={label}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${index === 0 ? "bg-[var(--rr-orange-soft)] text-[var(--rr-ink)]" : "text-[var(--rr-muted)]"}`}
            >
              <Icon size={18} strokeWidth={1.8} />
              {label}
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
              <div className="flex items-center gap-2">
                <p className="text-sm font-semibold text-[var(--rr-orange-deep)]">Today</p>
                <span className={`rounded-full px-2 py-1 text-[11px] font-semibold ${engineOnline ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                  {engineOnline ? "Live evidence" : "Engine unavailable"}
                </span>
              </div>
              <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em] md:text-4xl">What needs your attention</h1>
              <p className="mt-2 text-[var(--rr-muted)]">Live WHY → DO → VERIFY decisions from the learner evidence ledger.</p>
            </div>
            <Link href="/child/assessment" className="rr-flame-button self-start">Start assessment</Link>
          </div>

          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <Metric icon={Sparkles} value={String(needAction)} label="Need action" />
            <Metric icon={ClipboardCheck} value={String(needVerify)} label="Need verification" />
            <Metric icon={CircleHelp} value={String(needEvidence)} label="Need evidence" />
          </div>

          {!engineOnline ? (
            <EmptyState title="The scientific engine is not connected yet" body="The dashboard is ready, but it needs READRIGHT_API_BASE pointing to the live FastAPI service." />
          ) : priority.length === 0 ? (
            <EmptyState title="No learner evidence yet" body="Start a pilot assessment using a non-identifying learner code. Once evidence is saved, the teacher decision cards will appear here automatically." />
          ) : (
            <section className="mt-10">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Priority learners</h2>
                <span className="text-sm text-[var(--rr-muted)]">{priority.length} live decision{priority.length === 1 ? "" : "s"}</span>
              </div>
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                {priority.map((decision) => <LearnerCard key={decision.learner_id} decision={decision} />)}
              </div>
            </section>
          )}

          {plan && plan.rotations.length > 0 && (
            <section className="mt-10 rr-card p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.14em] text-[var(--rr-orange)]">30-minute plan</p>
                  <h2 className="mt-2 text-xl font-semibold">Teacher route for this session</h2>
                </div>
                <p className="text-sm text-[var(--rr-muted)]">Temporary groups, rebuilt as evidence changes.</p>
              </div>
              <div className="mt-6 grid gap-3">
                {plan.rotations.map((rotation) => (
                  <div key={`${rotation.order}-${rotation.title}`} className="grid gap-3 rounded-2xl border border-[var(--rr-border)] bg-white p-4 sm:grid-cols-[70px_180px_1fr] sm:items-start">
                    <div className="text-sm font-semibold text-[var(--rr-orange)]">{rotation.minutes} min</div>
                    <div>
                      <p className="font-semibold">{rotation.title}</p>
                      {rotation.learner_ids.length > 0 && <p className="mt-1 text-xs text-[var(--rr-muted)]">{rotation.learner_ids.join(", ")}</p>}
                    </div>
                    <p className="text-sm leading-6 text-[var(--rr-muted)]">{rotation.action}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
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

function LearnerCard({ decision }: { decision: TeacherDecision }) {
  const action = decision.outcome === "VERIFY_DUE"
    ? decision.verify?.instruction
    : decision.do?.title || "Collect distinguishing evidence before choosing an intervention.";
  const actionLabel = decision.outcome === "VERIFY_DUE" ? "VERIFY" : decision.outcome === "ACTION_READY" ? "DO" : "NEXT";

  return (
    <article className="rr-card overflow-hidden">
      <div className="h-1 bg-[var(--rr-flame)]" />
      <div className="p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.12em] text-[var(--rr-muted)]">Pilot learner</p>
            <h3 className="mt-1 text-lg font-semibold">{decision.learner_id}</h3>
          </div>
          <span className="rounded-full bg-[var(--rr-orange-soft)] px-2.5 py-1 text-[11px] font-semibold text-[var(--rr-orange-deep)]">{decision.outcome.replaceAll("_", " ")}</span>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-3">
          <Decision label="WHY" value={decision.why.headline} />
          <Decision label="EVIDENCE" value={`${decision.why.evidence_strength} evidence`} />
          <Decision label={actionLabel} value={action || "No immediate action"} accent />
        </div>
        {decision.do?.duration_minutes && (
          <p className="mt-5 border-t border-[var(--rr-border)] pt-4 text-xs text-[var(--rr-muted)]">
            Recommended routine: {decision.do.duration_minutes} minutes · {decision.do.group_size}
          </p>
        )}
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

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <section className="mt-10 rounded-3xl border border-dashed border-[var(--rr-border)] bg-white px-6 py-12 text-center">
      <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-[var(--rr-orange-soft)] text-[var(--rr-orange)]">
        <Sparkles size={20} />
      </div>
      <h2 className="mt-4 text-xl font-semibold">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-[var(--rr-muted)]">{body}</p>
    </section>
  );
}
