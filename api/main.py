import logging
import sys
from pathlib import Path
from typing import Literal

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import questions, ai
from .services import data_service

# -----------------------------
# Logging Configuration
# -----------------------------


def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    simple_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # File handler (detailed)
    file_handler = logging.FileHandler(log_dir / "api.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler (simple)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(simple_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Suppress verbose library logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(__name__)

# -----------------------------
# Rate Limiting
# -----------------------------

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="A2Z DSA Learning System API",
    description="RESTful API for the A2Z DSA learning system with comprehensive topic management, progress tracking, and study planning.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -----------------------------
# CORS Configuration
# ------------------------------

# Get allowed origins from environment or use defaults
import os

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://localhost:3000,http://127.0.0.1:8000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# -----------------------------
# Request Logging Middleware
# -----------------------------


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing."""
    import time

    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response with timing
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code} ({duration:.3f}s)"
    )

    return response


# -----------------------------
# Include Routers
# ------------------------------

app.include_router(questions.questions_router)
app.include_router(ai.ai_router)

# -----------------------------
# API Endpoints
# ------------------------------


@app.get("/api/stats")
@limiter.limit("60/minute")
async def get_stats(request: Request):
    """Get question statistics for dashboard."""
    try:
        stats = data_service.get_stats()
        return {
            "total_sections": stats.total_sections,
            "total_problems": stats.total_problems,
            "python_solutions": stats.python_solutions,
            "cpp_solutions": stats.cpp_solutions,
            "exact_matches": stats.exact_matches,
            "approx_matches": stats.approx_matches,
            "coverage_percentage": stats.coverage_percentage,
        }
    except Exception as exc:
        logger.error(f"Error getting stats: {exc}", exc_info=True)
        return {
            "total_sections": 18,
            "total_problems": 361,
            "python_solutions": 0,
            "cpp_solutions": 361,
            "exact_matches": 0,
            "approx_matches": 0,
            "coverage_percentage": 0.0
        }


@app.get("/api/topics")
@limiter.limit("60/minute")
async def get_topics(request: Request):
    """Get topics for the frontend."""
    try:
        topic_groups = {}
        question_list = data_service.get_question_list()

        for q in question_list:
            tags = q.tags or ["general"]
            for tag in tags:
                grp = topic_groups.setdefault(tag, {
                    "id": tag,
                    "title": tag.replace("-", " ").replace("_", " ").title(),
                    "path": f"/questions?tag={tag}",
                    "step_number": len(topic_groups) + 1,
                    "status": "available",
                    "related_problems": [],
                    "local_files": [],
                    "tags": [tag],
                    "source_links": [],
                    "notes": "",
                    "problem_count": 0,
                    "file_count": 0,
                })
                grp["problem_count"] += 1

        # Convert to list maintaining stable order
        topics = []
        for i, (tag, grp) in enumerate(sorted(topic_groups.items()), start=1):
            grp["step_number"] = i
            topics.append(grp)
        return topics
    except Exception as exc:
        logger.error(f"Error getting topics: {exc}", exc_info=True)
        return []


@app.get("/api/coverage")
@limiter.limit("30/minute")
async def get_coverage(request: Request):
    """Get coverage analysis for the frontend."""
    try:
        coverage = data_service.get_coverage()
        return {
            "total_sections": coverage.total_sections,
            "total_problems": coverage.total_problems,
            "coverage_percentage": coverage.coverage_percentage,
            "exact_matches": coverage.exact_matches,
            "approximate_matches": coverage.approximate_matches,
            "missing_implementations": coverage.missing_implementations,
            "coverage_by_section": coverage.coverage_by_section,
            "gaps": coverage.gaps,
            "recommendations": coverage.recommendations,
        }
    except Exception as exc:
        logger.error(f"Error getting coverage: {exc}", exc_info=True)
        return {
            "total_sections": 18,
            "total_problems": 361,
            "coverage_percentage": 0.0,
            "exact_matches": 0,
            "approximate_matches": 0,
            "missing_implementations": 361,
            "coverage_by_section": {},
            "gaps": {"missing_sections": [], "missing_python": [], "low_coverage": []},
            "recommendations": ["Start solving questions to track progress"],
        }


@app.get("/api/study-plan")
@limiter.limit("30/minute")
async def get_study_plan(request: Request):
    """Get the current study plan."""
    try:
        return data_service.get_study_plan()
    except Exception as exc:
        logger.error(f"Error getting study plan: {exc}", exc_info=True)
        return {"plans": [], "summary": {"total_study_time": 0, "average_daily_time": 0, "total_tasks": 0, "average_tasks_per_day": 0}}


@app.get("/api/study-plan/today")
@limiter.limit("30/minute")
async def get_today_plan(request: Request):
    """Get today's study tasks."""
    try:
        plan = data_service.get_study_plan()
        # Get first plan or today's plan based on day of week
        if plan.plans:
            return plan.plans[0]
        return {"day_name": "", "total_time": 0, "task_count": 0, "tasks": []}
    except Exception as exc:
        logger.error(f"Error getting today's plan: {exc}", exc_info=True)
        return {"day_name": "", "total_time": 0, "task_count": 0, "tasks": []}


@app.post("/api/rebuild")
@limiter.limit("5/minute")
async def rebuild(request: Request):
    """Rebuild the data indices."""
    try:
        data_service.rebuild_data()
        return {"status": "ok", "message": "Data rebuilt successfully"}
    except Exception as exc:
        logger.error(f"Error rebuilding data: {exc}", exc_info=True)
        return {"status": "error", "detail": str(exc)}


# -----------------------------
# Static File Serving
# ------------------------------

# Mount static directories
assets_dir = Path("frontend/assets")
repos_dir = Path("Strivers-A2Z-DSA-Sheet")
components_dir = Path("frontend/components")

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

if repos_dir.exists():
    app.mount("/repos", StaticFiles(directory=str(repos_dir)), name="repos")

if components_dir.exists():
    app.mount("/components", StaticFiles(directory=str(components_dir)), name="components")

# Mount frontend as static
frontend_dir = Path("frontend")
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon with proper content type."""
    favicon_path = Path("frontend/favicon.ico")
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")

    # Return 1x1 transparent GIF as fallback
    gif_data = bytes([
        0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x21,
        0xF9, 0x04, 0x01, 0x0A, 0x00, 0x01, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00,
        0x01, 0x00, 0x00, 0x02, 0x02, 0x4C, 0x01, 0x00, 0x3B
    ])
    return Response(content=gif_data, media_type="image/gif")


# -----------------------------
# SPA Fallback Routes
# ------------------------------


@app.get("/")
async def serve_frontend():
    """Serve the main SPA."""
    return FileResponse("frontend/index.html")


@app.get("/questions")
@app.get("/questions/{_:path}")
async def serve_questions(_: str = ""):
    """Serve SPA for questions routes."""
    return FileResponse("frontend/index.html")


# SPA fallbacks for in-app navigation
@app.get("/topics")
@app.get("/coverage")
@app.get("/planning")
async def serve_spa():
    """Serve SPA for other routes."""
    return FileResponse("frontend/index.html")


# -----------------------------
# Health Check
# ------------------------------


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "A2Z DSA Learning System API is running"}


# -----------------------------
# Global Exception Handler
# ------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with sanitized errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # Return generic message to client
    return Response(
        content='{"detail": "An internal error occurred. Please try again."}',
        status_code=500,
        media_type="application/json"
    )


# -----------------------------
# Server Entry Point
# ------------------------------


def main(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: Literal["critical", "error", "warning", "info", "debug"] = "info"
):
    """Run the API server."""
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


if __name__ == "__main__":
    main()
