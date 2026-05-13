from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agent_runs, assets, health, projects, templates
from app.core.config import settings
from app.providers.mock import register_mock_providers
from app.templates.loader import load_and_validate_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: load templates and register mock providers
    load_and_validate_templates()
    register_mock_providers()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(agent_runs.router, prefix="/api/runs", tags=["agent-runs"])


@app.get("/api")
async def root():
    return {"message": "Nano Workshop Agent API", "version": settings.VERSION}
