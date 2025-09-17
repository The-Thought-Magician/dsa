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
            "total_sections": 18,  # A2Z sections
            "total_problems": total_questions,
            "python_solutions": solved_count,
            "cpp_solutions": total_questions,  # All questions have C++ solutions
            "exact_matches": solved_count,
            "approx_matches": attempted_count,
            "coverage_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0.0
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

        # Group questions by tags
        topic_groups = {}
        for question in question_list:
            for tag in question.tags:
                if tag not in topic_groups:
                    topic_groups[tag] = {
                        "id": tag,
                        "title": tag.replace('-', ' ').title(),
                        "section": "Questions",
                        "problems": 0,
                        "status": "available"
                    }
                topic_groups[tag]["problems"] += 1

        return list(topic_groups.values())
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
            "total_questions": total_questions,
            "solved_questions": solved_count,
            "coverage_percentage": (solved_count / total_questions * 100) if total_questions > 0 else 0.0,
            "gaps": [],
            "recommendations": ["Practice more questions to improve coverage"]
        }
    except Exception:
        return {
            "total_questions": 361,
            "solved_questions": 0,
            "coverage_percentage": 0.0,
            "gaps": [],
            "recommendations": ["Start solving questions to track progress"]
        }

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
app.mount("/components", StaticFiles(directory="frontend/components"), name="components")
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/questions")
@app.get("/questions/{_:path}")
async def serve_questions(_: str = ""):
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "A2Z DSA Learning System API is running"}
