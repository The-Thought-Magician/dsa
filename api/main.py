from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import topics, coverage, planning

app = FastAPI(
    title="A2Z DSA Learning System API",
    description="RESTful API for the A2Z DSA learning system with comprehensive topic management, progress tracking, and study planning.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topics.router)
app.include_router(coverage.router)
app.include_router(planning.router)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "A2Z DSA Learning System API is running"}