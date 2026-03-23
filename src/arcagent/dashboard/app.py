"""FastAPI dashboard application."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ..config import AppConfig
from ..core.engine import AgentEngine
from ..skills.registry import SkillRegistry
from .routes import create_router

STATIC_DIR = Path(__file__).parent / "static"


def create_dashboard_app(
    engine: AgentEngine,
    skill_registry: SkillRegistry,
    tool_registry,
    config: AppConfig,
) -> FastAPI:
    """Create and configure the dashboard FastAPI app."""
    app = FastAPI(title="ArcAgent Dashboard", version="0.1.0")

    # API routes
    router = create_router(engine, skill_registry, tool_registry, config)
    app.include_router(router, prefix="/api")

    # Static files
    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    return app
