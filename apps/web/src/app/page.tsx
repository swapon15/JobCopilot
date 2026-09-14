import React from "react";

const workflowSteps = [
  "Structured candidate profile",
  "Manual job description paste",
  "Normalized job details",
  "Evidence-based recommendation"
];

export default function Home() {
  return (
    <main className="dashboard">
      <section className="intro" aria-labelledby="page-title">
        <p className="eyebrow">Milestone 1 scaffold</p>
        <h1 id="page-title">AI Job Search Copilot</h1>
        <p className="summary">
          A personal workspace for evaluating job descriptions against structured engineering
          experience before any portal automation is introduced.
        </p>
      </section>

      <section className="panel" aria-labelledby="workflow-title">
        <h2 id="workflow-title">First vertical slice</h2>
        <ol className="workflow-list">
          {workflowSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>

      <section className="status-grid" aria-label="Recommendation outcomes">
        <article>
          <strong>APPLY</strong>
          <span>High-confidence match with no material mandatory gaps.</span>
        </article>
        <article>
          <strong>CONSIDER</strong>
          <span>Potential fit where tradeoffs or gaps need review.</span>
        </article>
        <article>
          <strong>SKIP</strong>
          <span>Low fit, material conflicts, or missing mandatory requirements.</span>
        </article>
      </section>
    </main>
  );
}
