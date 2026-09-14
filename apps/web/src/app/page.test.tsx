import { render, screen } from "@testing-library/react";
import React from "react";
import Home from "./page";

describe("Home", () => {
  it("renders the milestone dashboard", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "AI Job Search Copilot" })).toBeInTheDocument();
    expect(screen.getByText("Manual job description paste")).toBeInTheDocument();
    expect(screen.getByText("APPLY")).toBeInTheDocument();
  });
});
