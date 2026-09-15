# AI Job Search Copilot

Personal web-hosted job-search copilot for evaluating job descriptions against a structured candidate profile.

Milestone 1 scaffolds the local development foundation only:

- Next.js + TypeScript frontend
- FastAPI backend
- Health-check endpoint
- PostgreSQL via Docker Compose
- Basic linting, formatting, type checking, and test configuration
- Candidate profile and manual job-description persistence
- Candidate profile editor in the web app
- Manual job intake with deterministic normalization
- Fake local match preview behind a matcher interface
- Backend-owned Apply/Consider/Skip recommendation policy
- Manual match dashboard with persisted job decisions

This project intentionally does not include authentication, OpenAI integration, or company-portal connectors yet.

## Repository Structure

```text
.
├── apps
│   ├── api          # FastAPI backend
│   └── web          # Next.js frontend
├── docker-compose.yml
├── package.json     # Root npm workspace scripts
└── README.md
```

## Prerequisites

- Node.js 20+
- npm 10+
- Python 3.10+
- Docker Desktop or another Docker Compose-compatible runtime

## Local Setup

Copy environment templates:

```sh
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Start PostgreSQL:

```sh
docker compose up -d postgres
```

Install frontend dependencies:

```sh
npm install
```

Install backend dependencies:

```sh
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Apply database migrations:

```sh
cd apps/api
source .venv/bin/activate
alembic -c alembic.ini upgrade head
```

Run the backend:

```sh
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Run the frontend:

```sh
npm run dev:web
```

Open http://localhost:3000.

The frontend loads and saves the latest candidate profile and pasted jobs through the backend API. Make sure the backend is running before using the dashboard.

## Checks

Frontend:

```sh
npm run lint:web
npm run typecheck:web
npm run test:web
```

Backend:

```sh
cd apps/api
source .venv/bin/activate
pytest
ruff check .
ruff format --check .
mypy app
```

Database:

```sh
cd apps/api
source .venv/bin/activate
alembic -c alembic.ini upgrade head
```

## Current API Surface

- `GET /health`
- `POST /candidate-profile`
- `GET /candidate-profile`
- `GET /candidate-profile/{profile_id}`
- `PUT /candidate-profile/{profile_id}`
- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/match`
- `POST /jobs/{job_id}/decision`

Job creation currently performs deterministic normalization only. It extracts obvious title, company, location, compensation, work mode, and requirement signals from the pasted description without using an LLM.

Match preview generation currently uses a deterministic fake matcher. It stores structured scores, evidence matches, gaps, rationale, interview risks, model name, prompt version, token usage fields, and estimated cost fields without calling OpenAI.

Recommendations are computed by backend policy code after matcher analysis:

- `APPLY`: overall score 80-100 with no mandatory gaps.
- `CONSIDER`: overall score 65-79.
- `SKIP`: overall score below 65, or any material mandatory gap.

The manual match dashboard displays the recommendation, supporting evidence, missing requirements, interview risks, work-preference conflicts, and decision actions to mark a job as applied, saved, or skipped.

## Current Assumptions

- The initial deployment target is Vercel for the frontend, a small managed service for FastAPI, and hosted PostgreSQL/Supabase.
- The first product workflow will remain manual job-description matching before any portal monitoring is introduced.
- Final recommendation thresholds live in backend domain policy, not in LLM prompts or browser code.
