"use client";

import React, { FormEvent, useEffect, useMemo, useState } from "react";
import {
  JobDescription,
  JobDescriptionInput,
  MatchResult,
  createJobDescription,
  createJobMatch,
  listJobDescriptions
} from "../lib/jobDescriptions";

type JobFormState = {
  rawDescription: string;
  sourceUrl: string;
  title: string;
  company: string;
  location: string;
  compensation: string;
  workMode: string;
};

const emptyJobForm: JobFormState = {
  rawDescription: "",
  sourceUrl: "",
  title: "",
  company: "",
  location: "",
  compensation: "",
  workMode: ""
};

function optionalValue(value: string): string | null {
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
}

function formToJobInput(form: JobFormState): JobDescriptionInput {
  return {
    raw_description: form.rawDescription.trim(),
    source_url: optionalValue(form.sourceUrl),
    title: optionalValue(form.title),
    company: optionalValue(form.company),
    location: optionalValue(form.location),
    compensation: optionalValue(form.compensation),
    work_mode: optionalValue(form.workMode)
  };
}

export default function JobDescriptionIntake() {
  const [form, setForm] = useState<JobFormState>(emptyJobForm);
  const [jobs, setJobs] = useState<JobDescription[]>([]);
  const [selectedJob, setSelectedJob] = useState<JobDescription | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "error">(
    "loading"
  );
  const [message, setMessage] = useState("Loading saved jobs...");

  useEffect(() => {
    let ignore = false;

    listJobDescriptions()
      .then((savedJobs) => {
        if (ignore) {
          return;
        }
        setJobs(savedJobs);
        setSelectedJob(savedJobs[0] ?? null);
        setMatchResult(null);
        setStatus("idle");
        setMessage(savedJobs.length ? "Loaded saved jobs." : "No saved jobs yet.");
      })
      .catch(() => {
        if (!ignore) {
          setStatus("error");
          setMessage("Could not load jobs. Is the backend running?");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  const canSave = useMemo(
    () => form.rawDescription.trim().length > 0 && status !== "saving",
    [form.rawDescription, status]
  );

  function updateForm<K extends keyof JobFormState>(key: K, value: JobFormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
    if (status === "saved" || status === "error") {
      setStatus("idle");
      setMessage("Editing pasted job.");
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("saving");
    setMessage("Normalizing and saving job...");

    try {
      const savedJob = await createJobDescription(formToJobInput(form));
      setJobs((current) => [savedJob, ...current.filter((job) => job.id !== savedJob.id)]);
      setSelectedJob(savedJob);
      setMatchResult(null);
      setForm(emptyJobForm);
      setStatus("saved");
      setMessage("Job saved and normalized.");
    } catch {
      setStatus("error");
      setMessage("Could not save the job. Check the backend and try again.");
    }
  }

  async function handleGenerateMatch() {
    if (!selectedJob) {
      return;
    }
    setStatus("saving");
    setMessage("Generating fake match preview...");

    try {
      const preview = await createJobMatch(selectedJob.id);
      setMatchResult(preview);
      setStatus("saved");
      setMessage("Fake match preview generated.");
    } catch {
      setStatus("error");
      setMessage("Could not generate a match preview. Save a candidate profile first.");
    }
  }

  return (
    <section className="editor-shell" aria-labelledby="job-intake-title">
      <div className="section-heading">
        <p className="eyebrow">Milestone 1.3</p>
        <h2 id="job-intake-title">Manual Job Intake</h2>
        <p>
          Paste a job description to save it and extract obvious title, location, compensation,
          work-mode, and requirement signals before any LLM matching exists.
        </p>
      </div>

      <form className="profile-form" onSubmit={handleSubmit}>
        <label>
          <span>Job description</span>
          <textarea
            name="rawDescription"
            value={form.rawDescription}
            onChange={(event) => updateForm("rawDescription", event.target.value)}
            placeholder="Paste the full job description here."
            required
          />
        </label>

        <div className="form-grid">
          <label>
            <span>Source URL</span>
            <input
              name="sourceUrl"
              value={form.sourceUrl}
              onChange={(event) => updateForm("sourceUrl", event.target.value)}
              placeholder="https://company.example/jobs/123"
            />
          </label>

          <label>
            <span>Title override</span>
            <input
              name="jobTitle"
              value={form.title}
              onChange={(event) => updateForm("title", event.target.value)}
              placeholder="Staff Software Engineer"
            />
          </label>

          <label>
            <span>Company override</span>
            <input
              name="company"
              value={form.company}
              onChange={(event) => updateForm("company", event.target.value)}
              placeholder="Example Co"
            />
          </label>

          <label>
            <span>Location override</span>
            <input
              name="location"
              value={form.location}
              onChange={(event) => updateForm("location", event.target.value)}
              placeholder="Remote - US"
            />
          </label>

          <label>
            <span>Compensation override</span>
            <input
              name="compensation"
              value={form.compensation}
              onChange={(event) => updateForm("compensation", event.target.value)}
              placeholder="$180,000 - $220,000"
            />
          </label>

          <label>
            <span>Work mode override</span>
            <select
              name="workMode"
              value={form.workMode}
              onChange={(event) => updateForm("workMode", event.target.value)}
            >
              <option value="">Infer from description</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </select>
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={!canSave}>
            Save Job
          </button>
          <button
            type="button"
            disabled={!selectedJob || status === "saving"}
            onClick={handleGenerateMatch}
          >
            Generate Match Preview
          </button>
          <output className={`form-status ${status}`} aria-live="polite">
            {message}
          </output>
        </div>
      </form>

      <div className="normalized-job-grid">
        <section className="normalized-panel" aria-labelledby="normalized-job-title">
          <h3 id="normalized-job-title">Normalized Job</h3>
          {selectedJob ? (
            <dl className="normalized-details">
              <div>
                <dt>Title</dt>
                <dd>{selectedJob.title ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Company</dt>
                <dd>{selectedJob.company ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Location</dt>
                <dd>{selectedJob.location ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Compensation</dt>
                <dd>{selectedJob.compensation ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Work mode</dt>
                <dd>{selectedJob.work_mode ?? "Unknown"}</dd>
              </div>
            </dl>
          ) : (
            <p className="empty-state">Save a job to see normalized fields.</p>
          )}
        </section>

        <section className="normalized-panel" aria-labelledby="requirements-title">
          <h3 id="requirements-title">Requirements</h3>
          {selectedJob?.normalized_requirements.length ? (
            <ul className="requirements-list">
              {selectedJob.normalized_requirements.map((requirement) => (
                <li key={`${selectedJob.id}-${requirement.text}`}>
                  <span>{requirement.mandatory ? "Mandatory" : "Preferred"}</span>
                  {requirement.text}
                </li>
              ))}
            </ul>
          ) : (
            <p className="empty-state">No requirements extracted yet.</p>
          )}
        </section>
      </div>

      {jobs.length > 0 ? (
        <section className="saved-jobs" aria-labelledby="saved-jobs-title">
          <h3 id="saved-jobs-title">Saved Jobs</h3>
          <div className="saved-job-list">
            {jobs.slice(0, 4).map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() => {
                  setSelectedJob(job);
                  setMatchResult(null);
                }}
              >
                {job.title ?? "Untitled job"}
              </button>
            ))}
          </div>
        </section>
      ) : null}

      {matchResult ? (
        <section className="match-preview" aria-labelledby="match-preview-title">
          <h3 id="match-preview-title">Fake Match Preview</h3>
          <div className="score-grid">
            <span>Technical {matchResult.scores.technical}</span>
            <span>Direct {matchResult.scores.direct_experience}</span>
            <span>Level {matchResult.scores.level}</span>
            <span>Leadership {matchResult.scores.leadership}</span>
            <span>Preference {matchResult.scores.preference}</span>
          </div>
          <p>{matchResult.concise_rationale}</p>
          <ul className="requirements-list">
            {matchResult.evidence_matches.map((match) => (
              <li key={`${match.requirement_text}-${match.match_category}`}>
                <span>{match.match_category}</span>
                {match.requirement_text}
                <small>{match.rationale}</small>
              </li>
            ))}
          </ul>
          <p className="metadata-line">
            {matchResult.model_name} · {matchResult.prompt_version} · cost not estimated
          </p>
        </section>
      ) : null}
    </section>
  );
}
