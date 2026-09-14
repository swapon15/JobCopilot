# AI Job Search Copilot

Personal web-hosted job-search copilot for evaluating job descriptions against a structured candidate profile.

Milestone 1 scaffolds the local development foundation only:

- Next.js + TypeScript frontend
- FastAPI backend
- Health-check endpoint
- PostgreSQL via Docker Compose
- Basic linting, formatting, type checking, and test configuration

This milestone intentionally does not include job matching, authentication, OpenAI integration, or company-portal connectors.

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
mypy app
```

## Current Assumptions

- The initial deployment target is Vercel for the frontend, a small managed service for FastAPI, and hosted PostgreSQL/Supabase.
- The first product workflow will remain manual job-description matching before any portal monitoring is introduced.
- Final recommendation thresholds will live in backend domain policy, not in LLM prompts or browser code.
