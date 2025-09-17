#!/usr/bin/env python3
"""
DSA Learning System - Main FastAPI Application

This is the main entry point for the DSA learning platform backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from .routes import problems, progress, ai_tutor, mappings, problem_summary
from .database import init_db

app = FastAPI(
    title="DSA Learning System",
    description="AI-powered platform for mastering Data Structures and Algorithms",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(ai_tutor.router, prefix="/api/ai", tags=["ai-tutor"])
app.include_router(mappings.router, prefix="/api", tags=["mappings"])
app.include_router(problem_summary.router, prefix="/api", tags=["problems"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await init_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DSA Learning System API",
        "version": "1.0.0",
        "endpoints": {
            "problems": "/api/problems",
            "progress": "/api/progress",
            "ai_tutor": "/api/ai",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dsa-learning-system"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )