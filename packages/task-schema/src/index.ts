export type TaskType =
  | "listen_and_respond"
  | "read_aloud"
  | "tap_choice"
  | "image_choice"
  | "sound_choice"
  | "sequence_repeat"
  | "ran_grid"
  | "letter_sound"
  | "word_decode"
  | "spelling_input"
  | "story_reader"
  | "teacher_observation";

export type CaptureMode = "voice" | "tap" | "text" | "teacher" | "mixed";

export interface AssessmentTask {
  id: string;
  language: "en" | "hi";
  skillId: string;
  type: TaskType;
  prompt: {
    learnerText?: string;
    spokenPrompt?: string;
    teacherText?: string;
  };
  capture: CaptureMode;
  difficulty: number;
  estimatedSeconds: number;
  evidenceTargets: string[];
}

export interface EvidenceDraft {
  taskId: string;
  responseRaw?: string;
  correct?: boolean | null;
  latencyMs?: number;
  assistance: "none" | "repeat" | "hint" | "model";
  selfCorrected?: boolean;
  teacherConfirmed?: boolean;
  qualityFlags?: string[];
}

export type AssessmentOutcome =
  | "ACTIONABLE_BARRIER_IDENTIFIED"
  | "MORE_EVIDENCE_REQUIRED"
  | "CONFLICTING_EVIDENCE"
  | "SKILL_LIKELY_SECURE"
  | "REFER_FOR_SPECIALIST_INPUT";
