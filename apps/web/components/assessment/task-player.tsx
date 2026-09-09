"use client";

import { useMemo, useState } from "react";
import { Mic, Pause, RotateCcw, Sparkles, Volume2 } from "lucide-react";
import type { AssessmentTask, EvidenceDraft } from "@readright/task-schema";

const demoTask: AssessmentTask = {
  id: "en-phon-blend-cvc-001",
  language: "en",
  skillId: "EN-PHON-BLEND-CVC",
  type: "listen_and_respond",
  prompt: {
    learnerText: "What word do these sounds make?",
    spokenPrompt: "/m/ /a/ /p/",
  },
  capture: "voice",
  difficulty: 0.3,
  estimatedSeconds: 20,
  evidenceTargets: ["phoneme_blending"],
};

export function TaskPlayer() {
  const [phase, setPhase] = useState<"ready" | "listening" | "review">("ready");
  const [assistance, setAssistance] = useState<EvidenceDraft["assistance"]>("none");

  const status = useMemo(() => {
    if (phase === "listening") return "Listening";
    if (phase === "review") return "Response captured";
    return "Ready";
  }, [phase]);

  return (
    <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-6xl overflow-hidden rounded-[28px] border border-[var(--rr-border)] bg-[var(--rr-background)] lg:grid-cols-[1fr_360px]">
      <section className="relative flex min-h-[620px] flex-col items-center justify-center overflow-hidden px-6 py-10 text-center">
        <div className="rr-assessment-arc" aria-hidden="true" />
        <div className="relative z-10 max-w-3xl">
          <div className={`mx-auto grid h-14 w-14 place-items-center rounded-full border border-[var(--rr-border)] bg-white text-2xl text-[var(--rr-orange)] transition ${phase === "listening" ? "rr-listening-pulse" : ""}`}>
            <Sparkles size={24} strokeWidth={1.7} />
          </div>
          <p className="mt-8 text-sm font-semibold uppercase tracking-[0.16em] text-[var(--rr-orange-deep)]">{status}</p>
          <h1 className="mt-5 text-3xl font-semibold tracking-[-0.035em] md:text-5xl">{demoTask.prompt.learnerText}</h1>
          <button className="mt-8 inline-flex items-center gap-3 rounded-2xl border border-[var(--rr-border)] bg-white px-6 py-4 text-2xl font-semibold shadow-sm">
            <Volume2 size={24} />
            {demoTask.prompt.spokenPrompt}
          </button>

          <div className="mt-10">
            {phase === "ready" && (
              <button className="rr-mic-button" onClick={() => setPhase("listening")} aria-label="Start listening">
                <Mic size={30} />
              </button>
            )}
            {phase === "listening" && (
              <button className="rr-mic-button" onClick={() => setPhase("review")} aria-label="Stop listening">
                <Pause size={28} />
              </button>
            )}
            {phase === "review" && <p className="text-base text-[var(--rr-muted)]">Thank you.</p>}
          </div>
        </div>
      </section>

      <aside className="border-t border-[var(--rr-border)] bg-white p-6 lg:border-l lg:border-t-0">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-[var(--rr-muted)]">Teacher controls</p>
        <h2 className="mt-2 text-xl font-semibold">Evidence review</h2>

        <div className="mt-6 rounded-2xl bg-[var(--rr-background)] p-4">
          <p className="text-xs font-semibold text-[var(--rr-muted)]">Machine suggestion</p>
          <p className="mt-2 text-lg font-semibold">“map”</p>
          <p className="mt-1 text-xs text-[var(--rr-muted)]">Demo only. Teacher confirmation remains authoritative.</p>
        </div>

        <div className="mt-6 grid grid-cols-3 gap-2">
          {['Correct', 'Incorrect', "Couldn't tell"].map((label) => (
            <button key={label} className="rounded-xl border border-[var(--rr-border)] px-3 py-3 text-sm font-medium hover:border-[var(--rr-orange)]">
              {label}
            </button>
          ))}
        </div>

        <div className="mt-7">
          <p className="text-sm font-semibold">Assistance used</p>
          <div className="mt-3 space-y-2">
            {([
              ["none", "None"],
              ["repeat", "Prompt repeated"],
              ["hint", "Small hint"],
              ["model", "Full model"],
            ] as const).map(([value, label]) => (
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

        <button onClick={() => setPhase("ready")} className="mt-8 inline-flex items-center gap-2 text-sm font-semibold text-[var(--rr-muted)]">
          <RotateCcw size={16} /> Reset demo
        </button>
      </aside>
    </div>
  );
}
