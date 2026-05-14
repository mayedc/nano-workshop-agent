# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Nano Workshop Agent is a full-stack Agentic AI platform for academic workshop data analysis. It is a pnpm monorepo with a FastAPI backend (`apps/api`) and a Next.js 15 frontend (`apps/web`).

## Tech Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, TanStack Query, Zustand, React Flow, Recharts
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Celery (Redis), MinIO, python-docx, python-pptx
- **Database**: PostgreSQL with pgvector (production); SQLite with aiosqlite (demo/tests)
- **Infra**: Docker Compose for PostgreSQL, Redis, and MinIO

## Commands

All `pnpm` commands run from the repository root unless noted. The Python API is not a pnpm workspace member.

### Demo Mode (zero dependencies)

```bash
cd apps/api
# Delete old DB if models changed:
rm -f demo.db
# Start (auto-creates SQLite tables + uses MemoryStorage + Mock AI providers)
python demo_main.py
```
API runs on port 8000. No PostgreSQL, Redis, MinIO, or API keys needed.

### Development

```bash
# Frontend
pnpm dev:web

# Backend (PostgreSQL required)
cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Build

```bash
pnpm build                                    # All Node.js packages
pnpm --filter web build                       # Frontend only
```

### Tests

```bash
# Backend (run from apps/api/)
cd apps/api
pytest                              # All 64 tests
pytest tests/test_health.py         # Single file
pytest -k test_name                 # Single test by name

# Frontend
pnpm --filter web typecheck         # TypeScript only (no test suite)
```

### Lint / Format

```bash
# Frontend
pnpm lint

# Backend (run from apps/api/)
cd apps/api
ruff check . && ruff format . && mypy .
```

## Architecture

### Monorepo Structure

- `apps/web/` — Next.js 15 App Router. Rewrites `/api/:path*` → `http://localhost:8000/api/:path*` in dev.
- `apps/api/` — FastAPI backend (Python only, not a pnpm workspace member).
- `packages/shared/` — Shared TypeScript types.
- `templates/workshop/` — YAML workshop template definitions.

### Backend Architecture (layered, registry-driven)

1. **Templates** (`app/templates/`) — Workshop logic in YAML files (`templates/workshop/*.yaml`). `TemplateRegistry` loads/validates at startup. Workflow steps use `depends_on` for DAGs.
2. **Providers** (`app/providers/`) — AI service interfaces (LLM, OCR, STT, Vision, Embedding, Image Gen). Mock implementations in `mock.py` so app runs without API keys.
3. **Processors** (`app/processors/`) — File processors (text, pdf, image, audio, video, table, model3d) dispatched by MIME type through `ProviderRegistry`.
4. **Agents** (`app/agents/`) — `BaseWorkshopAgent` base class. `AgentRegistry` holds all agents. `WorkflowOrchestrator` runs steps concurrently respecting `depends_on`, stops on failure, supports reruns.

   **Agent categories (20 total):**
   - Core: ProjectSetup, MaterialIntake, Preprocessing, MetadataFusion, GoalUnderstanding, WorkshopPlanning
   - Analysis: QualitativeAnalysis, Coding, ThemeExtraction, QuantitativeAnalysis
   - Design: PrototypeAnalysis, DesignInsight, DesignConcept
   - Reporting: ExpertReview, Iteration, ReportGeneration, Export
   - Realtime: MeetingRealtime, MCPConnector
   - Evaluation: EvaluationAgent

5. **Services** (`app/services/`) — `CRUDBase[ModelType]` generic DB operations. `export_generator.py` handles DOCX/PPTX/JSON/CSV generation.
6. **Storage** (`app/services/storage.py`) — `MinioStorage` (production) and `MemoryStorage` (tests/demo).

### Database Models (15 tables)

`users`, `workshop_templates`, `projects`, `assets`, `evidence`, `codes`, `themes`, `requirements`, `agent_runs`, `export_records`, `expert_feedback`, `questionnaire_results`, `design_insights`, `prototype_reviews`, `concept_designs`

### API Routes

| Prefix | Tag | Notes |
|--------|-----|-------|
| `/api/health` | health | Health check |
| `/api/projects` | projects | CRUD + filtering |
| `/api/templates` | templates | Workshop template DSL |
| `/api/assets` | assets | Upload + processing |
| `/api/runs` | agent-runs | Agent execution records |
| `/api/evidence` | evidence | CRUD + project-scoped |
| `/api/exports` | exports | Generate DOCX/PPTX/JSON/CSV + list history |
| `/api/workflows` | workflows | Run orchestrated workflows |
| `/api/feedback` | feedback | Expert review CRUD with 8 actions |

### Expert Review System (Phase 8)

- `ExpertFeedback` model stores reviews on 6 target types: `codes`, `themes`, `requirements`, `insights`, `concepts`, `report_sections`
- 8 review actions: `approve`, `reject`, `revise`, `merge`, `split`, `score`, `comment`, `request_rerun`
- Side effects: `approve` → `review_status=approved`; `reject` → `rejected`; `request_rerun` → `pending_rerun`; updates cascade to `AgentRun.review_status` and target entity statuses
- `IterationAgent` processes feedback, generates rerun plans, detects approve/reject conflicts
- Frontend: `/projects/[id]/review` — feedback form, review history, agent run status, rerun button

### Export Pipeline (Phase 9)

- `ReportGenerationAgent` produces 12-section report structure
- `ExportAgent` triggers per-format generation
- `export_generator.py`: `generate_docx()` (Word with tables), `generate_pptx()` (11-slide deck), `generate_json_export()` (full metadata), `generate_csv_tables()` (ZIP of 7 CSVs)
- `GET /api/exports/generate/{project_id}?format=docx|pptx|json|csv` — generates and downloads
- Frontend: `/projects/[id]/exports` — format cards, generate buttons, history table with re-download

### Frontend Architecture

- **App Router**: `/projects/[id]/` routes for dashboard, upload, workflow, evidence, coding, themes, quantitative, insights, prototypes, review, report, exports
- **State**: TanStack Query (server), Zustand `src/lib/store.ts` (client: active project, sidebar, toasts)
- **API Client**: `src/lib/api.ts` — typed fetch wrappers; binary exports use direct fetch + blob download
- **Components**: shadcn/ui in `src/components/ui/`, layout (AppShell, ProjectSidebar) in `src/components/layout/`

### Data Flow

1. Create project from workshop template → 2. Upload multimodal assets to `/api/assets` → 3. Assets stored in MinIO/Memory, metadata in DB → 4. Assets processed (sync via endpoint or async via Celery) → 5. WorkflowOrchestrator runs agent DAG → 6. Expert reviews feedback → IterationAgent plans reruns → 7. Exports generated in DOCX/PPTX/JSON/CSV

## Important Conventions

### SQLite / Demo Mode

- `demo_main.py` must set `DATABASE_URL` env var **before** importing from `app`. It uses `os.environ.setdefault()` before the `from app.main import app` line.
- `import app.models` is required before `Base.metadata.create_all()` — otherwise tables won't be created because model classes haven't registered with SQLAlchemy metadata.
- SQLite has single-writer limitation. Concurrent writes (e.g., parallel orchestrator steps) must serialize through `asyncio.Lock` (see `orchestrator.py:_persist_run`).

### Pydantic v2

- Uses `model_config = ConfigDict(from_attributes=True)` instead of `class Config`.
- Settings use `SettingsConfigDict` from `pydantic_settings`, not `pydantic.BaseSettings`.
- `model_dump(exclude_unset=True)` for partial updates.

### Testing

- Tests use `aiosqlite` with in-memory DB, `httpx.ASGITransport` (httpx 0.28+ API), mock AI providers.
- Route tests use `dependency_overrides` for DB session injection.
- `conftest.py` provides `db` (SQLAlchemy async session) and `override_get_db` fixtures.
- Windows: `mimetypes.guess_type('data.csv')` returns `application/vnd.ms-excel`, not `text/csv`.

### Template YAML

- All YAML template fields use **snake_case** matching Pydantic DSL models.
- Agent names must match registered agent names exactly (e.g., `PreprocessingAgent` not `AssetProcessor`).
- Template loader path: `Path(__file__).parents[4]` to reach repo root from `app/templates/loader.py`.
