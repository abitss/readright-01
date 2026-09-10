export type TeacherDecisionOutcome =
  | "ACTION_READY"
  | "VERIFY_DUE"
  | "MORE_EVIDENCE"
  | "CONFLICTING"
  | "NO_ACTION";

export type TeacherDecision = {
  learner_id: string;
  language: string;
  outcome: TeacherDecisionOutcome;
  why: {
    headline: string;
    evidence_strength: string;
    supporting_points: string[];
    alternatives: string[];
  };
  do: null | {
    title: string;
    duration_minutes: number | null;
    group_size: string | null;
    steps: string[];
    intervention_id: string | null;
  };
  verify: null | {
    stage: string;
    instruction: string;
    task_ids: string[];
    status: string;
  };
  scientific_status: string;
};

export type LearnerIndexItem = {
  learner_id: string;
  language: string;
  created_at: string;
  event_count: number;
  latest_sequence_no: number;
};

export type ClassPlan = {
  total_minutes: number;
  groups: Array<{
    group_id: string;
    label: string;
    learner_ids: string[];
    intervention_id: string | null;
    verification_stage: string | null;
    priority: number;
    reason: string;
  }>;
  rotations: Array<{
    order: number;
    minutes: number;
    group_id: string | null;
    title: string;
    action: string;
    learner_ids: string[];
  }>;
  deferred_learner_ids: string[];
};

function apiBase() {
  const value = process.env.READRIGHT_API_BASE || process.env.NEXT_PUBLIC_READRIGHT_API_BASE;
  if (!value) throw new Error("READRIGHT_API_BASE is not configured");
  return value.replace(/\/$/, "");
}

async function readJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`ReadRight API ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export async function getLearners(): Promise<LearnerIndexItem[]> {
  const data = await readJson<{ learners: LearnerIndexItem[] }>("/learners");
  return data.learners;
}

export async function getTeacherDecision(learnerId: string): Promise<TeacherDecision> {
  return readJson<TeacherDecision>(`/teacher-decision/learners/${encodeURIComponent(learnerId)}`);
}

export async function getClassPlan(learnerIds: string[], totalMinutes = 30): Promise<ClassPlan> {
  const data = await readJson<{ plan: ClassPlan }>("/teacher-decision/class-plan", {
    method: "POST",
    body: JSON.stringify({ learner_ids: learnerIds, total_minutes: totalMinutes }),
  });
  return data.plan;
}
