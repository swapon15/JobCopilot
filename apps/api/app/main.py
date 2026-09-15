from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.candidate_profiles import router as candidate_profile_router
from app.api.health import router as health_router
from app.api.job_descriptions import router as job_description_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="AI Job Search Copilot API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(candidate_profile_router)
    app.include_router(job_description_router)
    return app


app = create_app()
