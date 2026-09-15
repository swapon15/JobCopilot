"use client";

import React, { FormEvent, useEffect, useMemo, useState } from "react";
import {
  CandidateProfile,
  CandidateProfileInput,
  ExperienceType,
  commaTextToList,
  createCandidateProfile,
  getLatestCandidateProfile,
  listToCommaText,
  updateCandidateProfile
} from "../lib/candidateProfile";

type FormState = {
  headline: string;
  summary: string;
  targetRoles: string;
  preferredLocations: string;
  workPreferences: string;
  sponsorshipRequired: boolean;
  projectOrPosition: string;
  evidenceDescription: string;
  skills: string;
  responsibilities: string;
  measurableOutcomes: string;
  experienceType: ExperienceType;
};

const emptyForm: FormState = {
  headline: "",
  summary: "",
  targetRoles: "",
  preferredLocations: "Remote",
  workPreferences: "Remote, Strong work-life balance",
  sponsorshipRequired: false,
  projectOrPosition: "",
  evidenceDescription: "",
  skills: "",
  responsibilities: "",
  measurableOutcomes: "",
  experienceType: "direct"
};

function profileToForm(profile: CandidateProfile): FormState {
  const firstEvidence = profile.evidence[0];

  return {
    headline: profile.headline,
    summary: profile.summary,
    targetRoles: listToCommaText(profile.target_roles),
    preferredLocations: listToCommaText(profile.preferred_locations),
    workPreferences: listToCommaText(profile.work_preferences),
    sponsorshipRequired: profile.sponsorship_required,
    projectOrPosition: firstEvidence?.project_or_position ?? "",
    evidenceDescription: firstEvidence?.description ?? "",
    skills: listToCommaText(firstEvidence?.skills ?? []),
    responsibilities: listToCommaText(firstEvidence?.responsibilities ?? []),
    measurableOutcomes: listToCommaText(firstEvidence?.measurable_outcomes ?? []),
    experienceType: firstEvidence?.experience_type ?? "direct"
  };
}

function formToProfileInput(form: FormState): CandidateProfileInput {
  return {
    headline: form.headline.trim(),
    summary: form.summary.trim(),
    target_roles: commaTextToList(form.targetRoles),
    preferred_locations: commaTextToList(form.preferredLocations),
    work_preferences: commaTextToList(form.workPreferences),
    sponsorship_required: form.sponsorshipRequired,
    evidence:
      form.projectOrPosition.trim() || form.evidenceDescription.trim()
        ? [
            {
              project_or_position: form.projectOrPosition.trim(),
              description: form.evidenceDescription.trim(),
              skills: commaTextToList(form.skills),
              responsibilities: commaTextToList(form.responsibilities),
              measurable_outcomes: commaTextToList(form.measurableOutcomes),
              experience_type: form.experienceType
            }
          ]
        : []
  };
}

export default function CandidateProfileEditor() {
  const [form, setForm] = useState<FormState>(emptyForm);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("Loading candidate profile...");

  useEffect(() => {
    let ignore = false;

    getLatestCandidateProfile()
      .then((profile) => {
        if (ignore) {
          return;
        }

        if (profile) {
          setProfileId(profile.id);
          setForm(profileToForm(profile));
          setMessage("Loaded the latest saved profile.");
        } else {
          setMessage("No saved profile yet.");
        }
        setStatus("idle");
      })
      .catch(() => {
        if (!ignore) {
          setStatus("error");
          setMessage("Could not load the profile API. Is the backend running?");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  const canSave = useMemo(
    () =>
      form.headline.trim().length > 0 &&
      form.summary.trim().length > 0 &&
      form.projectOrPosition.trim().length > 0 &&
      form.evidenceDescription.trim().length > 0 &&
      status !== "saving",
    [form, status]
  );

  function updateForm<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
    if (status === "saved" || status === "error") {
      setStatus("idle");
      setMessage(profileId ? "Editing saved profile." : "Editing a new profile.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    setMessage("Saving profile...");

    try {
      const payload = formToProfileInput(form);
      const savedProfile = profileId
        ? await updateCandidateProfile(profileId, payload)
        : await createCandidateProfile(payload);

      if (savedProfile) {
        setProfileId(savedProfile.id);
        setForm(profileToForm(savedProfile));
      }
      setStatus("saved");
      setMessage("Profile saved.");
    } catch {
      setStatus("error");
      setMessage("Could not save the profile. Check the backend and try again.");
    }
  }

  return (
    <section className="editor-shell" aria-labelledby="profile-editor-title">
      <div className="section-heading">
        <p className="eyebrow">Milestone 1.2</p>
        <h2 id="profile-editor-title">Candidate Profile</h2>
        <p>
          Capture the structured evidence the matcher will use later. Keep direct production
          experience separate from transferable or knowledge-only experience.
        </p>
      </div>

      <form className="profile-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            <span>Headline</span>
            <input
              name="headline"
              value={form.headline}
              onChange={(event) => updateForm("headline", event.target.value)}
              placeholder="Principal Software/Data Engineer"
              required
            />
          </label>

          <label>
            <span>Target roles</span>
            <input
              name="targetRoles"
              value={form.targetRoles}
              onChange={(event) => updateForm("targetRoles", event.target.value)}
              placeholder="Staff Software Engineer, AI Platform Engineer"
            />
          </label>

          <label>
            <span>Preferred locations</span>
            <input
              name="preferredLocations"
              value={form.preferredLocations}
              onChange={(event) => updateForm("preferredLocations", event.target.value)}
              placeholder="Remote, Hybrid for exceptional role"
            />
          </label>

          <label>
            <span>Work preferences</span>
            <input
              name="workPreferences"
              value={form.workPreferences}
              onChange={(event) => updateForm("workPreferences", event.target.value)}
              placeholder="Remote, Strong work-life balance"
            />
          </label>
        </div>

        <label>
          <span>Professional summary</span>
          <textarea
            name="summary"
            value={form.summary}
            onChange={(event) => updateForm("summary", event.target.value)}
            placeholder="Summarize the candidate's senior engineering, data, platform, and leadership experience."
            required
          />
        </label>

        <div className="inline-control">
          <input
            id="sponsorshipRequired"
            type="checkbox"
            checked={form.sponsorshipRequired}
            onChange={(event) => updateForm("sponsorshipRequired", event.target.checked)}
          />
          <label htmlFor="sponsorshipRequired">Requires employment sponsorship</label>
        </div>

        <fieldset className="evidence-fieldset">
          <legend>Evidence item</legend>
          <div className="form-grid">
            <label>
              <span>Project or position</span>
              <input
                name="projectOrPosition"
                value={form.projectOrPosition}
                onChange={(event) => updateForm("projectOrPosition", event.target.value)}
                placeholder="Licensing-data ingestion infrastructure"
                required
              />
            </label>

            <label>
              <span>Experience type</span>
              <select
                name="experienceType"
                value={form.experienceType}
                onChange={(event) =>
                  updateForm("experienceType", event.target.value as ExperienceType)
                }
              >
                <option value="direct">Direct</option>
                <option value="transferable">Transferable</option>
                <option value="knowledge_only">Knowledge only</option>
                <option value="missing">Missing</option>
              </select>
            </label>
          </div>

          <label>
            <span>Evidence description</span>
            <textarea
              name="evidenceDescription"
              value={form.evidenceDescription}
              onChange={(event) => updateForm("evidenceDescription", event.target.value)}
              placeholder="Built automated ingestion and data-quality workflows."
              required
            />
          </label>

          <div className="form-grid">
            <label>
              <span>Skills</span>
              <input
                name="skills"
                value={form.skills}
                onChange={(event) => updateForm("skills", event.target.value)}
                placeholder="Python, SQL, Snowflake"
              />
            </label>

            <label>
              <span>Responsibilities</span>
              <input
                name="responsibilities"
                value={form.responsibilities}
                onChange={(event) => updateForm("responsibilities", event.target.value)}
                placeholder="Pipeline design, Data validation"
              />
            </label>

            <label>
              <span>Measurable outcomes</span>
              <input
                name="measurableOutcomes"
                value={form.measurableOutcomes}
                onChange={(event) => updateForm("measurableOutcomes", event.target.value)}
                placeholder="Reduced processing time from hours to minutes"
              />
            </label>
          </div>
        </fieldset>

        <div className="form-actions">
          <button type="submit" disabled={!canSave}>
            {profileId ? "Save Changes" : "Create Profile"}
          </button>
          <output className={`form-status ${status}`} aria-live="polite">
            {message}
          </output>
        </div>
      </form>
    </section>
  );
}
