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
