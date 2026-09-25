"""FastAPI application entrypoint for SentryMesh Guardian — ParentCall Guardian.

Tagline: Pause. Verify. Protect.
Loads the real SentryMesh V4 binary scam-risk model at startup.
Fails visibly if model or metrics files are missing.
"""

from contextlib import asynccontextmanager
import sys
from pathlib import Path
import logging

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.model_loader import get_model_loader
from app.routers import health, analysis, audio, family

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sentrymesh")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event: loads V4 model artifact and metrics before accepting requests."""
    logger.info("Initializing SentryMesh Guardian backend...")
    logger.info("Resolving model artifacts from: %s", settings.model_path)
    logger.info("Resolving metrics from: %s", settings.metrics_path)

    # Strictly load model and threshold once at startup
    try:
        loader = get_model_loader()
        logger.info(
            "Successfully loaded '%s' with selected threshold: %.4f",
            loader.model_name,
            loader.selected_threshold
        )
    except Exception as exc:
        logger.critical("FAILED TO LOAD MODEL ARTIFACTS AT STARTUP: %s", exc)
        raise

    yield

    logger.info("Shutting down SentryMesh Guardian backend.")


app = FastAPI(
    title="SentryMesh Guardian — ParentCall Guardian API",
    description="Privacy-first AI scam defense helping families analyze suspicious calls and messages.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(audio.router)
app.include_router(family.router)


@app.get("/", tags=["Root"])
def root_info():
    """System overview and active module metadata."""
    loader = get_model_loader()
    return {
        "service": "SentryMesh Guardian — ParentCall Guardian",
        "tagline": "Pause. Verify. Protect.",
        "module": "parent_call_guardian",
        "model_loaded": loader.is_loaded,
        "selected_threshold": loader.selected_threshold,
        "privacy": "In-memory analysis only. No background call recording or chat scraping."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
