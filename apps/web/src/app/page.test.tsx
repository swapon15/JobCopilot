import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import Home from "./page";

describe("Home", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the profile editor and creates a candidate profile", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => null
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
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
        })
      } as Response);

    render(<Home />);

    expect(screen.getByRole("heading", { name: "AI Job Search Copilot" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Candidate Profile" })).toBeInTheDocument();
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
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/candidate-profile",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("loads the latest profile and saves edits", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
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
        })
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: "profile-1",
          headline: "Principal Software/Data Engineer",
          summary: "Original summary.",
          target_roles: ["Principal Software Engineer"],
          preferred_locations: ["Remote"],
          work_preferences: ["Remote"],
          sponsorship_required: false,
          created_at: "2026-09-15T00:00:00Z",
          updated_at: "2026-09-15T00:00:00Z",
          evidence: [
            {
              id: "evidence-2",
              candidate_profile_id: "profile-1",
              project_or_position: "Installer platform",
              description: "Built C++ installer platform features.",
              skills: ["C++"],
              responsibilities: ["Platform development"],
              measurable_outcomes: ["Improved reliability"],
              experience_type: "direct"
            }
          ]
        })
      } as Response);

    render(<Home />);

    expect(await screen.findByDisplayValue("Principal Engineer")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Headline"), {
      target: { value: "Principal Software/Data Engineer" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Save Changes" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenLastCalledWith(
        "http://localhost:8000/candidate-profile/profile-1",
        expect.objectContaining({ method: "PUT" })
      );
    });
  });
});
