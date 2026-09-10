"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Mic, Pause, Sparkles, Volume2 } from "lucide-react";

type Assistance = "none" | "repeat" | "hint" | "model";
type Task = {
  id: string;
  language: "en" | "hi";
  skill_id: string;
  type: string;
  prompt: {
    learner_text?: string | null;
    spoken_prompt?: string | null;
    teacher_text?: string | null;
  };
  capture: string;
  difficulty: number;
  estimated_seconds: number;
};

type AssessmentStartResponse = {
  session: { id: string; learner_id: string; current_task: Task };
  task_stimulus?: Record<string, unknown> | null;
};

type AssessmentResponse = {
  assessment_complete: boolean;
  outcome?: string;
  next_task?: Task;
  task_stimulus?: Record<string, unknown> | null;
  selection_reason?: string;
  decision_kind?: string;
};

export function TaskPlayer() {
  const [learnerId, setLearnerId] = useState("");
  const [language, setLanguage] = useState<"en" | "hi">("en");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [stimulus, setStimulus] = useState<Record<string, unknown> | null>(null);
  const [phase, setPhase] = useState<"setup" | "ready" | "listening" | "review" | "saving" | "complete">("setup");
  const [assistance, setAssistance] = useState<Assistance>("none");
  const [error, setError] = useState<string | null>(null);
  const [lastDecision, setLastDecision] = useState<string | null>(null);

  const status = useMemo(() => {
    if (phase === "listening") return "Listening";
    if (phase === "review") return "Teacher review";
    if (phase === "saving") return "Saving evidence";
    if (phase === "complete") return "Assessment complete";
    return "Ready";
  }, [phase]);

  async function startAssessment() {
    const clean = learnerId.trim();
    if (!clean) {
      setError("Enter a non-identifying pilot learner code.");
      return;
    }
    setError(null);
    try {
      const response = await fetch("/api/readright/assessments/start", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ learner_id: clean, language, mode: "baseline" }),
      });
      const data = (await response.json()) as AssessmentStartResponse & { detail?: unknown };
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Could not start assessment");
      setSessionId(data.session.id);
      setTask(data.session.current_task);
      setStimulus(data.task_stimulus || null);
      setPhase("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "ReadRight engine unavailable");
    }
  }

  async function saveJudgement(correct: boolean | null) {
    if (!sessionId || !task) return;
    setPhase("saving");
    setError(null);
    try {
      const response = await fetch(`/api/readright/assessments/${sessionId}/respond`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          task_id: task.id,
          response_raw: null,
          correct,
          latency_ms: null,
          assistance,
          self_corrected: false,
          teacher_confirmed: true,
          quality_flags: correct === null ? ["AMBIGUOUS_RESPONSE"] : [],
        }),
      });
      const data = (await response.json()) as AssessmentResponse & { detail?: unknown };
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Could not save evidence");

      if (data.assessment_complete) {
        setLastDecision(data.outcome || "EVIDENCE_COLLECTED");
        setPhase("complete");
        setTask(null);
        return;
      }

      setTask(data.next_task || null);
      setStimulus(data.task_stimulus || null);
      setLastDecision(data.selection_reason || null);
      setAssistance("none");
      setPhase("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save evidence");
      setPhase("review");
    }
  }

  if (phase === "setup") {
    return (
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-3xl items-center justify-center">
        <section className="rr-card w-full p-7 md:p-10">
          <ReadRightSpark />
          <p className="mt-6 text-xs font-bold uppercase tracking-[0.15em] text-[var(--rr-orange)]">Pilot assessment</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em]">Start with a learner code</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--rr-muted)]">
            Use a non-identifying pilot code, not a child&apos;s full name. Evidence from this session will feed the live WHY → DO → VERIFY dashboard.
          </p>

          <label className="mt-7 block text-sm font-semibold">Pilot learner code</label>
          <input
            value={learnerId}
            onChange={(event) => setLearnerId(event.target.value)}
            placeholder="e.g. PILOT-001"
            className="mt-2 w-full rounded-xl border border-[var(--rr-border)] bg-white px-4 py-3 outline-none focus:border-[var(--rr-orange)]"
          />

          <label className="mt-5 block text-sm font-semibold">Assessment language</label>
          <div className="mt-2 grid grid-cols-2 gap-2">
            {(["en", "hi"] as const).map((item) => (
              <button
                key={item}
                onClick={() => setLanguage(item)}
                className={`rounded-xl border px-4 py-3 text-sm font-semibold ${language === item ? "border-[var(--rr-orange)] bg-[var(--rr-orange-soft)]" : "border-[var(--rr-border)] bg-white"}`}
              >
                {item === "en" ? "English" : "Hindi pilot"}
              </button>
            ))}
          </div>

          {error && <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
          <button onClick={startAssessment} className="rr-flame-button mt-7">Begin baseline</button>
        </section>
      </div>
    );
  }

  if (phase === "complete") {
    return (
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-3xl items-center justify-center text-center">
        <section className="rr-card w-full p-8 md:p-12">
          <ReadRightSpark />
          <p className="mt-6 text-xs font-bold uppercase tracking-[0.15em] text-[var(--rr-orange)]">Evidence saved</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-[-0.04em]">ReadRight has enough evidence to stop this session.</h1>
          <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-[var(--rr-muted)]">
            Outcome: {lastDecision?.replaceAll("_", " ")}. This is an assessment stopping decision, not a diagnosis.
          </p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Link href="/teacher" className="rr-flame-button">Open teacher decisions</Link>
            <button onClick={() => { setPhase("setup"); setSessionId(null); setLearnerId(""); }} className="rounded-xl border border-[var(--rr-border)] bg-white px-5 py-3 text-sm font-semibold">New learner</button>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-6xl overflow-hidden rounded-[28px] border border-[var(--rr-border)] bg-[var(--rr-background)] lg:grid-cols-[1fr_360px]">
      <section className="relative flex min-h-[620px] flex-col items-center justify-center overflow-hidden px-6 py-10 text-center">
        <div className="rr-assessment-arc" aria-hidden="true" />
        <div className="relative z-10 max-w-3xl">
          <ReadRightSpark pulse={phase === "listening"} />
          <p className="mt-8 text-sm font-semibold uppercase tracking-[0.16em] text-[var(--rr-orange-deep)]">{status}</p>
          <p className="mt-2 text-xs text-[var(--rr-muted)]">{task?.skill_id}</p>
          <h1 className="mt-5 text-3xl font-semibold tracking-[-0.035em] md:text-5xl">{task?.prompt.learner_text || "Listen carefully."}</h1>

          {(task?.prompt.spoken_prompt || stimulus?.display) && (
            <button className="mt-8 inline-flex items-center gap-3 rounded-2xl border border-[var(--rr-border)] bg-white px-6 py-4 text-2xl font-semibold shadow-sm">
              {task?.prompt.spoken_prompt && <Volume2 size={24} />}
              {String(task?.prompt.spoken_prompt || stimulus?.display || "")}
            </button>
          )}

          <div className="mt-10">
            {phase === "ready" && (
              <button className="rr-mic-button" onClick={() => setPhase("listening")} aria-label="Start response">
                <Mic size={30} />
              </button>
            )}
            {phase === "listening" && (
              <button className="rr-mic-button" onClick={() => setPhase("review")} aria-label="Response captured">
                <Pause size={28} />
              </button>
            )}
            {phase === "saving" && <p className="text-sm text-[var(--rr-muted)]">Saving immutable evidence…</p>}
          </div>
        </div>
      </section>

      <aside className="border-t border-[var(--rr-border)] bg-white p-6 lg:border-l lg:border-t-0">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-[var(--rr-muted)]">Teacher controls</p>
        <h2 className="mt-2 text-xl font-semibold">Evidence review</h2>
        <p className="mt-2 text-xs leading-5 text-[var(--rr-muted)]">Teacher judgement is stored with assistance and quality context. Browser speech is not treated as scientific authority.</p>

        {task?.prompt.teacher_text && (
          <div className="mt-6 rounded-2xl bg-[var(--rr-background)] p-4">
            <p className="text-xs font-semibold text-[var(--rr-muted)]">Administration note</p>
            <p className="mt-2 text-sm leading-6">{task.prompt.teacher_text}</p>
          </div>
        )}

        <div className="mt-6 grid grid-cols-3 gap-2">
          <button disabled={phase !== "review"} onClick={() => saveJudgement(true)} className="rounded-xl border border-[var(--rr-border)] px-3 py-3 text-sm font-medium disabled:opacity-40">Correct</button>
          <button disabled={phase !== "review"} onClick={() => saveJudgement(false)} className="rounded-xl border border-[var(--rr-border)] px-3 py-3 text-sm font-medium disabled:opacity-40">Incorrect</button>
          <button disabled={phase !== "review"} onClick={() => saveJudgement(null)} className="rounded-xl border border-[var(--rr-border)] px-3 py-3 text-sm font-medium disabled:opacity-40">Couldn&apos;t tell</button>
        </div>

        <div className="mt-7">
          <p className="text-sm font-semibold">Assistance used</p>
          <div className="mt-3 space-y-2">
            {([[
              "none", "None"
            ], ["repeat", "Prompt repeated"], ["hint", "Small hint"], ["model", "Full model"]] as const).map(([value, label]) => (
              <button
                key={value}
                onClick={() => setAssistance(value)}
                className={`flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-left text-sm ${assistance === value ? "border-[var(--rr-orange)] bg-[var(--rr-orange-soft)]" : "border-[var(--rr-border)]"}`}
              >
                {label}
                <span className={`h-2.5 w-2.5 rounded-full ${assistance === value ? "bg-[var(--rr-orange)]" : "bg-[var(--rr-border)]"}`} />
              </button>
            ))}
          </div>
        </div>

        {lastDecision && <p className="mt-6 border-t border-[var(--rr-border)] pt-4 text-xs leading-5 text-[var(--rr-muted)]">Why this task: {lastDecision}</p>}
        {error && <p className="mt-4 rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">{error}</p>}
      </aside>
    </div>
  );
}

function ReadRightSpark({ pulse = false }: { pulse?: boolean }) {
  return (
    <div className={`mx-auto grid h-14 w-14 place-items-center rounded-full border border-[var(--rr-border)] bg-white text-[var(--rr-orange)] ${pulse ? "rr-listening-pulse" : ""}`}>
      <Sparkles size={24} strokeWidth={1.7} />
    </div>
  );
}
