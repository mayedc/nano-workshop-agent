# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Nano Workshop Agent is a full-stack Agentic AI platform for academic workshop data analysis. It is a pnpm monorepo with a FastAPI backend (`apps/api`) and a Next.js 15 frontend (`apps/web`).

## Tech Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, TanStack Query, Zustand, React Flow, Recharts
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, Celery (Redis), MinIO
- **Database**: PostgreSQL with pgvector (via `ankane/pgvector` Docker image)
- **Infra**: Docker Compose for PostgreSQL, Redis, and MinIO

## Common Commands

All `pnpm` commands should be run from the repository root unless noted.

### Development

```bash
# Start frontend and shared package watcher
pnpm dev:web

# Start backend (must be run from apps/api/; uvicorn is the dev server)
cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start all Node.js packages in parallel (does NOT start the Python API)
pnpm dev
```

> **Note:** `pnpm dev:api` (defined in root `package.json`) does not currently work because `apps/api` has no `package.json` and is not a valid pnpm workspace package.

### Build

```bash
pnpm build        # Builds all Node.js packages/apps in parallel
pnpm --filter @nano-workshop/shared build   # Build shared types package only
pnpm --filter web build                     # Build Next.js frontend only
```

### Tests

```bash
# Backend (run from apps/api/)
cd apps/api
pytest                      # Run all tests
pytest tests/test_health.py # Run a single test file
pytest -k test_name         # Run a single test by name

# Frontend
pnpm --filter web typecheck  # TypeScript type checking only
# No frontend test suite currently exists.
```

### Lint / Format

```bash
# Frontend
pnpm lint                     # Lints all Node.js packages
pnpm --filter web lint        # Next.js lint

# Backend (run from apps/api/)
cd apps/api
ruff check .      # Lint
ruff format .     # Format
mypy .            # Type check
```

### Database & Migrations

```bash
# Start infrastructure dependencies
pnpm db:up        # docker-compose up -d postgres redis minio
pnpm db:down      # docker-compose down

# Run from apps/api/
cd apps/api
alembic upgrade head                                # Apply all migrations
alembic revision --autogenerate -m "description"    # Create a new migration
```

### Celery Worker

```bash
cd apps/api
celery -A app.core.celery worker --loglevel=info
```

## Architecture

### Monorepo Structure

- `apps/web/` — Next.js frontend. Next.js config rewrites `/api/:path*` to `http://localhost:8000/api/:path*` in development.
- `apps/api/` — FastAPI backend. Not a pnpm workspace member (Python only).
- `packages/shared/` — Shared TypeScript types. Built with `tsc`; output in `dist/`.
- `templates/workshop/` — YAML workshop template definitions.

### Backend Architecture

The backend follows a layered, registry-driven architecture:

1. **Templates** (`app/templates/`) — Workshop logic is defined in YAML files (`templates/workshop/*.yaml`), not hardcoded. `TemplateRegistry` loads and validates them at startup. Templates define workflow steps with `dependsOn` for dependency graphs.
2. **Providers** (`app/providers/`) — All AI services (LLM, OCR, STT, Vision, Embedding, Image Generation) are abstracted behind provider interfaces. Mock implementations exist for every provider so the app and tests run without API keys.
3. **Processors** (`app/processors/`) — Pluggable file processors (`text`, `pdf`, `image`, `audio`, `video`, `table`, `model3d`) based on MIME type. Each processor dispatches through `ProviderRegistry`.
4. **Agents** (`app/agents/`) — `BaseWorkshopAgent` is the base class. Agents are dynamically registered in `AgentRegistry` and can call tools via `ToolRegistry`. The `WorkflowOrchestrator` executes agent steps concurrently based on their dependency graph, stops on failure, and supports reruns.
5. **Services** (`app/services/`) — `CRUDBase[ModelType]` provides generic database operations used by route handlers.
6. **Storage** (`app/services/storage.py`) — `MinioStorage` (production) and `MemoryStorage` (tests) backends with file type detection and key generation.

**Agent Categories:**
- Core: ProjectSetup, MaterialIntake, Preprocessing, MetadataFusion, GoalUnderstanding, WorkshopPlanning
- Analysis: QualitativeAnalysis, Coding, ThemeExtraction, QuantitativeAnalysis
- Design: PrototypeAnalysis, DesignInsight, DesignConcept
- Reporting: ExpertReview, Iteration, ReportGeneration, Export
- Realtime: MeetingRealtime, MCPConnector
- Evaluation: EvaluationAgent

### Frontend Architecture

- **App Router** with nested project routes: `/projects/[id]/{dashboard,upload,workflow,evidence,coding,themes,quantitative,insights,prototypes,review,report,exports}`.
- **State**: TanStack Query for server state, Zustand (`src/lib/store.ts`) for client state (active project, sidebar, toasts).
- **API Client**: `src/lib/api.ts` contains typed fetch wrappers for all backend endpoints.
- **Components**: shadcn/ui components live in `src/components/ui/`. Custom layout components (AppShell, ProjectSidebar) live in `src/components/layout/`.

### Data Flow

1. User creates a project from a workshop template.
2. Uploads multimodal materials (images, audio, video, documents) to `/api/assets`.
3. Assets are stored in MinIO; metadata in PostgreSQL.
4. Asset processing can be synchronous (direct endpoint) or asynchronous (Celery task `process_asset_task`).
5. The `WorkflowOrchestrator` runs analysis agents based on the template's workflow steps.
6. Every agent output references `evidence_ids` (evidence-based outputs).
7. Results are persisted to the database and surfaced through the frontend.

## Environment Setup

1. `cp .env.example .env`
2. `pnpm install` (at root)
3. `pnpm db:up`
4. Install Python dependencies (e.g., `cd apps/api && pip install -e ".[dev]"`)
5. `cd apps/api && alembic upgrade head`
6. Start dev servers (see Common Commands)

## Testing Conventions

- Backend tests use `aiosqlite` for an in-memory async database (see `tests/conftest.py`).
- All AI provider calls use mock implementations in tests.
- When adding new processors or agents, register mock implementations in `app/providers/mock.py` and `app/agents/mock_agents.py` respectively.
