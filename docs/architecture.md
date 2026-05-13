# Architecture

## Overview

Nano Workshop Agent is a full-stack Agentic AI platform for academic workshop data analysis.

## High-Level Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web App   │────▶│  API Layer  │────▶│   Agents    │
│  (Next.js)  │◄────│  (FastAPI)  │◄────│(NanoClaw)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌─────────┐   ┌─────────┐
              │PostgreSQL│   │  Redis  │
              │+ pgvector│   │         │
              └─────────┘   └─────────┘
                    │
                    ▼
              ┌─────────┐
              │  MinIO  │
              │ (S3)    │
              └─────────┘
```

## Layers

### 1. Frontend (apps/web)
- Next.js 15 with App Router
- React 19 + TypeScript
- Tailwind CSS + shadcn/ui
- TanStack Query for server state
- Zustand for client state
- React Flow for workflow visualization
- Recharts for data visualization

### 2. Backend (apps/api)
- FastAPI with async handlers
- Pydantic for validation
- SQLAlchemy async with PostgreSQL
- Alembic for migrations
- Redis for caching and job queues
- MinIO for object storage

### 3. AI / Agent Layer
- NanoClaw-style agent orchestration
- Agent registry and tool registry
- Workflow orchestrator with human review loop
- MCP connector abstraction
- Provider interfaces for all AI services

### 4. Workshop Templates
- YAML-driven workshop configuration
- Domain-specific ontology
- Configurable workflow steps
- Template validation

## Data Flow

1. User creates project from workshop template
2. Uploads multimodal materials (images, audio, video, documents)
3. Pipeline processors extract text and metadata
4. Agents perform analysis (thematic, quantitative, design insights)
5. Expert review loop for quality control
6. Export to academic report formats

## Key Principles

1. Template-driven — never hard-code domain logic
2. Evidence-based — every output references source evidence
3. Reproducible — every export is deterministic from metadata
4. Async — all long-running processes are non-blocking
5. Testable — mock providers for all AI calls
