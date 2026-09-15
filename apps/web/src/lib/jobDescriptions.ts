export type NormalizedRequirement = {
  text: string;
  mandatory: boolean;
  match_category: "direct" | "transferable" | "knowledge_only" | "missing" | null;
  evidence_ids: string[];
};

export type JobDescriptionInput = {
  raw_description: string;
  source_url?: string | null;
  title?: string | null;
  company?: string | null;
  location?: string | null;
  compensation?: string | null;
  work_mode?: string | null;
};

export type JobDescription = JobDescriptionInput & {
  id: string;
  source_url: string | null;
  title: string | null;
  company: string | null;
  location: string | null;
  compensation: string | null;
  work_mode: string | null;
  normalized_requirements: NormalizedRequirement[];
  created_at: string;
  updated_at: string;
};

export type MatchResult = {
  id: string;
  candidate_profile_id: string;
  job_description_id: string;
  scores: {
    technical: number;
    direct_experience: number;
    level: number;
    leadership: number;
    preference: number;
  };
  mandatory_gaps: string[];
  preferred_gaps: string[];
  evidence_matches: Array<{
    requirement_text: string;
    match_category: "direct" | "transferable" | "knowledge_only" | "missing";
    evidence_ids: string[];
    rationale: string;
  }>;
  concise_rationale: string;
  interview_risks: string[];
  model_name: string;
  prompt_version: string;
  input_tokens: number | null;
  output_tokens: number | null;
  estimated_cost_usd: number | null;
  created_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function requestJobDescriptions<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    throw new Error(`Job description request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listJobDescriptions(): Promise<JobDescription[]> {
  return requestJobDescriptions<JobDescription[]>("/jobs");
}

export function createJobDescription(job: JobDescriptionInput): Promise<JobDescription> {
  return requestJobDescriptions<JobDescription>("/jobs", {
    method: "POST",
    body: JSON.stringify(job)
  });
}

export function createJobMatch(jobId: string): Promise<MatchResult> {
  return requestJobDescriptions<MatchResult>(`/jobs/${jobId}/match`, {
    method: "POST"
  });
}
