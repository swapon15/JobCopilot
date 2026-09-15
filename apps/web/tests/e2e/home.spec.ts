import { expect, test } from "@playwright/test";

test("creates a candidate profile from the dashboard", async ({ page }) => {
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

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "AI Job Search Copilot" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Candidate Profile" })).toBeVisible();
  await expect(page.getByText("First vertical slice")).toBeVisible();

  await page.getByLabel("Headline").fill("Principal Software/Data Engineer");
  await page.getByLabel("Professional summary").fill("Builds platform and data systems.");
  await page.getByLabel("Project or position").fill("Licensing-data ingestion infrastructure");
  await page.getByLabel("Evidence description").fill("Built automated ingestion workflows.");
  await page.getByRole("button", { name: "Create Profile" }).click();

  await expect(page.getByText("Profile saved.")).toBeVisible();
});
