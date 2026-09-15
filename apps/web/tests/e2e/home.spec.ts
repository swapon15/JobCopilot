import { expect, test } from "@playwright/test";

test("creates a candidate profile and saves a pasted job from the dashboard", async ({ page }) => {
  await page.route("http://localhost:8000/candidate-profile", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ json: null });
      return;
    }

    await route.fulfill({
      json: {
        id: "profile-1",
        headline: "Principal Software/Data Engineer",
        summary: "Builds platform and data systems.",
        target_roles: ["Staff Software Engineer"],
        preferred_locations: ["Remote"],
        work_preferences: ["Remote"],
        sponsorship_required: false,
        created_at: "2026-09-15T00:00:00Z",
        updated_at: "2026-09-15T00:00:00Z",
        evidence: [
          {
            id: "evidence-1",
            candidate_profile_id: "profile-1",
            project_or_position: "Licensing-data ingestion infrastructure",
            description: "Built automated ingestion workflows.",
            skills: ["Python", "SQL"],
            responsibilities: ["Pipeline design"],
            measurable_outcomes: ["Reduced processing time"],
            experience_type: "direct"
          }
        ]
      }
    });
  });
  await page.route("http://localhost:8000/candidate-profile/draft", async (route) => {
    await route.fulfill({
      json: {
        headline: "Principal Software/Data Engineer",
        summary: "Builds platform and data systems.",
        target_roles: ["Staff Software Engineer"],
        preferred_locations: ["Remote"],
        work_preferences: ["Remote"],
        sponsorship_required: false,
        evidence: [
          {
            project_or_position: "Licensing-data ingestion infrastructure",
            description: "Built automated ingestion workflows.",
            skills: ["Python", "SQL"],
            responsibilities: ["Pipeline design"],
            measurable_outcomes: ["Reduced processing time"],
            experience_type: "direct"
          }
        ]
      }
    });
  });
  await page.route("http://localhost:8000/jobs", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ json: [] });
      return;
    }

    await route.fulfill({
      json: {
        id: "job-1",
        raw_description: "Staff Software Engineer\nRequirements:\n- Must have Python experience",
        source_url: null,
        title: "Staff Software Engineer",
        company: "Example Co",
        location: "Remote - US",
        compensation: "$180,000 - $220,000",
        work_mode: "remote",
        normalized_requirements: [
          {
            text: "Must have Python experience",
            mandatory: true,
            match_category: null,
            evidence_ids: []
          }
        ],
        created_at: "2026-09-15T00:00:00Z",
        updated_at: "2026-09-15T00:00:00Z"
      }
    });
  });
  await page.route("http://localhost:8000/jobs/job-1/match", async (route) => {
    await route.fulfill({
      json: {
        id: "match-1",
        candidate_profile_id: "profile-1",
        job_description_id: "job-1",
        scores: {
          technical: 88,
          direct_experience: 70,
          level: 75,
          leadership: 70,
          preference: 80
        },
        recommendation: "APPLY",
        recommendation_score: 81,
        recommendation_reason:
          "APPLY because the overall score is at least 80 with no mandatory gaps.",
        mandatory_gaps: [],
        preferred_gaps: [],
        evidence_matches: [
          {
            requirement_text: "Must have Python experience",
            match_category: "direct",
            evidence_ids: ["evidence-1"],
            rationale: "Matched on: python."
          }
        ],
        concise_rationale: "Fake matcher preview based on keyword overlap.",
        interview_risks: ["Review direct versus transferable experience manually."],
        work_preference_conflicts: [],
        model_name: "fake-local-matcher",
        prompt_version: "fake-match-v1",
        input_tokens: null,
        output_tokens: null,
        estimated_cost_usd: null,
        created_at: "2026-09-15T00:00:00Z"
      }
    });
  });
  await page.route("http://localhost:8000/jobs/job-1/decision", async (route) => {
    await route.fulfill({
      json: {
        id: "decision-1",
        job_description_id: "job-1",
        state: "saved",
        notes: null,
        created_at: "2026-09-15T00:00:00Z"
      }
    });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "AI Job Search Copilot" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Candidate Profile" })).toBeVisible();
  await expect(page.getByText("First vertical slice")).toBeVisible();

  await page
    .getByLabel("Paste resume, LinkedIn summary, or rough notes")
    .fill("Principal Software/Data Engineer\nBuilt automated ingestion workflows.");
  await page.getByRole("button", { name: "Draft Profile" }).click();

  await expect(
    page.getByText("Draft ready. Review the fields, then save the profile.")
  ).toBeVisible();
  await expect(page.getByLabel("Headline")).toHaveValue("Principal Software/Data Engineer");
  await expect(page.getByLabel("Project or position")).toHaveValue(
    "Licensing-data ingestion infrastructure"
  );

  await page.getByRole("button", { name: "Create Profile" }).click();

  await expect(page.getByText("Profile saved.")).toBeVisible();

  await page
    .getByLabel("Job description")
    .fill("Staff Software Engineer\nCompany: Example Co\nRequirements:\n- Must have Python");
  await page.getByRole("button", { name: "Save Job" }).click();

  await expect(page.getByText("Job saved and normalized.")).toBeVisible();
  await expect(page.getByText("Must have Python experience")).toBeVisible();
  await page.getByRole("button", { name: "Generate Match Preview" }).click();

  await expect(page.getByText("Manual match dashboard generated.")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Manual Match Dashboard" })).toBeVisible();
  await expect(page.getByText("Score 81: APPLY")).toBeVisible();
  await expect(page.getByText("Technical 88")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Supporting Evidence" })).toBeVisible();
  await expect(page.getByText("No work-preference conflicts detected.")).toBeVisible();

  await page.getByRole("button", { name: "Save for Later" }).click();

  await expect(page.getByText("Job marked saved.")).toBeVisible();
  await expect(page.getByText("Decision saved: saved")).toBeVisible();
});
