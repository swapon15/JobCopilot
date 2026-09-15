export type ExperienceType = "direct" | "transferable" | "knowledge_only" | "missing";

export type CandidateEvidenceInput = {
  project_or_position: string;
  description: string;
  skills: string[];
  responsibilities: string[];
  measurable_outcomes: string[];
  experience_type: ExperienceType;
};

export type CandidateProfileInput = {
  headline: string;
  summary: string;
  target_roles: string[];
  preferred_locations: string[];
  work_preferences: string[];
  sponsorship_required: boolean;
  evidence: CandidateEvidenceInput[];
};

export type CandidateEvidence = CandidateEvidenceInput & {
  id: string;
  candidate_profile_id: string;
};

export type CandidateProfile = Omit<CandidateProfileInput, "evidence"> & {
  id: string;
  created_at: string;
  updated_at: string;
  evidence: CandidateEvidence[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function requestCandidateProfile(
  path: string,
  init?: RequestInit
): Promise<CandidateProfile | null> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });

  if (!response.ok) {
    throw new Error(`Candidate profile request failed with ${response.status}`);
  }

  return response.json() as Promise<CandidateProfile | null>;
}

export function getLatestCandidateProfile(): Promise<CandidateProfile | null> {
  return requestCandidateProfile("/candidate-profile");
}

export function createCandidateProfile(
  profile: CandidateProfileInput
): Promise<CandidateProfile | null> {
  return requestCandidateProfile("/candidate-profile", {
    method: "POST",
    body: JSON.stringify(profile)
  });
}

export function updateCandidateProfile(
  profileId: string,
  profile: CandidateProfileInput
): Promise<CandidateProfile | null> {
  return requestCandidateProfile(`/candidate-profile/${profileId}`, {
    method: "PUT",
    body: JSON.stringify(profile)
  });
}

export function commaTextToList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function listToCommaText(value: string[]): string {
  return value.join(", ");
}
