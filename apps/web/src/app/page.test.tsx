import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import Home from "./page";

const profileResponse = {
  id: "profile-1",
  headline: "Principal Engineer",
  summary: "Original summary.",
  target_roles: ["Principal Software Engineer"],
  preferred_locations: ["Remote"],
  work_preferences: ["Remote"],
  sponsorship_required: false,
  created_at: "2026-09-15T00:00:00Z",
  updated_at: "2026-09-15T00:00:00Z",
  evidence: [
    {
      id: "evidence-1",
      candidate_profile_id: "profile-1",
      project_or_position: "Installer platform",
      description: "Built C++ installer platform features.",
      skills: ["C++"],
      responsibilities: ["Platform development"],
      measurable_outcomes: ["Improved reliability"],
      experience_type: "direct"
    }
  ]
};

const jobResponse = {
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
};

function jsonResponse(body: unknown): Response {
  return {
    ok: true,
    json: async () => body
  } as Response;
}

function mockApi(options: { latestProfile?: unknown; jobs?: unknown[] } = {}) {
  return vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const url = input.toString();
    const method = init?.method ?? "GET";

    if (url.endsWith("/candidate-profile") && method === "GET") {
      return jsonResponse(options.latestProfile ?? null);
    }
    if (url.endsWith("/candidate-profile") && method === "POST") {
      return jsonResponse({ ...profileResponse, headline: "Principal Software/Data Engineer" });
    }
    if (url.endsWith("/candidate-profile/profile-1") && method === "PUT") {
      return jsonResponse({ ...profileResponse, headline: "Principal Software/Data Engineer" });
    }
    if (url.endsWith("/jobs") && method === "GET") {
      return jsonResponse(options.jobs ?? []);
    }
    if (url.endsWith("/jobs") && method === "POST") {
      return jsonResponse(jobResponse);
    }

    throw new Error(`Unhandled request in test: ${method} ${url}`);
  });
}

describe("Home", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the profile editor and creates a candidate profile", async () => {
    const fetchMock = mockApi();

    render(<Home />);

    expect(screen.getByRole("heading", { name: "AI Job Search Copilot" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Manual Job Intake" })).toBeInTheDocument();
    expect(screen.getByText("Manual job description paste")).toBeInTheDocument();
    expect(screen.getByText("APPLY")).toBeInTheDocument();

    await screen.findByText("No saved profile yet.");

    fireEvent.change(screen.getByLabelText("Headline"), {
      target: { value: "Principal Software/Data Engineer" }
    });
    fireEvent.change(screen.getByLabelText("Professional summary"), {
      target: { value: "Builds platform and data systems." }
    });
    fireEvent.change(screen.getByLabelText("Project or position"), {
      target: { value: "Licensing-data ingestion infrastructure" }
    });
    fireEvent.change(screen.getByLabelText("Evidence description"), {
      target: { value: "Built automated ingestion workflows." }
    });

    fireEvent.click(screen.getByRole("button", { name: "Create Profile" }));

    await screen.findByText("Profile saved.");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/candidate-profile",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("loads the latest profile and saves edits", async () => {
    const fetchMock = mockApi({ latestProfile: profileResponse });

    render(<Home />);

    expect(await screen.findByDisplayValue("Principal Engineer")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Headline"), {
      target: { value: "Principal Software/Data Engineer" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Changes" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://localhost:8000/candidate-profile/profile-1",
        expect.objectContaining({ method: "PUT" })
      );
    });
  });

  it("saves a pasted job and displays normalized fields", async () => {
    const fetchMock = mockApi();

    render(<Home />);

    await screen.findByText("No saved jobs yet.");

    fireEvent.change(screen.getByLabelText("Job description"), {
      target: {
        value: "Staff Software Engineer\nCompany: Example Co\nRequirements:\n- Must have Python"
      }
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Job" }));

    await screen.findByText("Job saved and normalized.");
    expect(screen.getByText("$180,000 - $220,000")).toBeInTheDocument();
    expect(screen.getByText("Must have Python experience")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/jobs",
      expect.objectContaining({ method: "POST" })
    );
  });
});
