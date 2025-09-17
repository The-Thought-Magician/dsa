from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import questions, ai
from .services import data_service

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

app.include_router(questions.questions_router)
app.include_router(ai.ai_router)

# Add endpoints that the frontend expects
@app.get("/api/stats")
async def get_stats():
    """Get question statistics for dashboard."""
    try:
        question_list = data_service.get_question_list()
        total_questions = len(question_list)
        solved_count = len([q for q in question_list if q.status == "solved"])
        attempted_count = len([q for q in question_list if q.status == "attempted"])

        return {
            "total_sections": 18,
            "total_problems": total_questions,
            "python_solutions": solved_count,
            "cpp_solutions": total_questions,
            "exact_matches": solved_count,
            "approx_matches": attempted_count,
            "coverage_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0.0,
        }
    except Exception:
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
async def get_topics():
    """Get topics for the frontend (simplified for question practice)."""
    try:
        question_list = data_service.get_question_list()

        # Group questions by tag and emit topic-like objects compatible with UI
        topic_groups = {}
        for q in question_list:
            tags = q.tags or ["general"]
            for tag in tags:
                grp = topic_groups.setdefault(tag, {
                    "id": tag,
                    "title": tag.replace('-', ' ').title(),
                    "path": f"/questions?tag={tag}",
                    "step_number": len(topic_groups) + 1,
                    "status": "available",
                    "related_problems": [],
                    "local_files": [],
                    "tags": [tag],
                    "source_links": [],
                    "notes": "",
                })
                grp.setdefault("problem_count", 0)
                grp.setdefault("file_count", 0)
                grp["problem_count"] += 1

        # Convert to list maintaining stable order
        topics = []
        for i, (tag, grp) in enumerate(sorted(topic_groups.items()), start=1):
            grp["step_number"] = i
            topics.append(grp)
        return topics
    except Exception:
        return []

@app.get("/api/coverage")
async def get_coverage():
    """Get coverage analysis for the frontend."""
    try:
        question_list = data_service.get_question_list()
        total_questions = len(question_list)
        solved_count = len([q for q in question_list if q.status == "solved"])

        return {
            "total_sections": 18,
            "total_problems": total_questions,
            "coverage_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0.0,
            "exact_matches": solved_count,
            "approximate_matches": 0,
            "missing_implementations": total_questions - solved_count,
            "coverage_by_section": {},
            "gaps": {"missing_sections": [], "missing_python": [], "low_coverage": []},
            "recommendations": ["Practice more questions to improve coverage"],
        }
    except Exception:
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

# Study plan endpoints (fallback implementation)
@app.get("/api/study-plan")
async def get_study_plan():
    try:
        return data_service.get_study_plan()
    except Exception:
        # return empty plan structure
        return {"plans": [], "summary": {"total_study_time": 0, "average_daily_time": 0, "total_tasks": 0, "average_tasks_per_day": 0}}

@app.get("/api/study-plan/today")
async def get_today_plan():
    try:
        plan = data_service.get_study_plan()
        # pick first plan as a reasonable default
        return plan.plans[0] if plan.plans else {"day_name": "", "total_time": 0, "task_count": 0, "tasks": []}
    except Exception:
        return {"day_name": "", "total_time": 0, "task_count": 0, "tasks": []}

@app.post("/api/rebuild")
async def rebuild():
    try:
        data_service.rebuild_data()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
app.mount("/repos", StaticFiles(directory="Strivers-A2Z-DSA-Sheet"), name="repos")
app.mount("/components", StaticFiles(directory="frontend/components"), name="components")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("frontend/favicon.ico")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/questions")
@app.get("/questions/{_:path}")
async def serve_questions(_: str = ""):
    return FileResponse("frontend/index.html")

# SPA fallbacks for in-app navigation
@app.get("/topics")
@app.get("/coverage")
@app.get("/planning")
async def serve_spa():
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "A2Z DSA Learning System API is running"}
