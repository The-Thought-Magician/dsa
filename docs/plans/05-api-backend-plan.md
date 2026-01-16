# API & Backend Plan

## Overview

This plan addresses API backend improvements including endpoint verification, error handling, static file serving, and study plan functionality.

## Current API Endpoints

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/stats` | GET | Implemented | Returns question statistics |
| `/api/topics` | GET | Implemented | Derived from question tags |
| `/api/coverage` | GET | Implemented | Coverage analysis |
| `/api/questions` | GET | Implemented | List/filter questions |
| `/api/questions/{id}` | GET | Implemented | Single question detail |
| `/api/questions/{id}/run` | POST | Implemented | Execute Python code |
| `/api/questions/{id}/submit` | POST | Implemented | Submit solution |
| `/api/questions/{id}/solution/view` | POST | Implemented | View solution |
| `/api/ai/chat` | POST | Implemented | AI assistance |
| `/api/study-plan` | GET | Implemented | Study plan data |
| `/api/study-plan/today` | GET | Implemented | Today's tasks |
| `/api/rebuild` | POST | Implemented | Rebuild data |

## Known Issues

1. Static mounts need verification
2. Study plan endpoints return empty data
3. Rebuild endpoint may not work correctly
4. Error handling not comprehensive
5. No proper logging for debugging

## Phase 1: Static File Serving

### 1.1 Verify Static Mounts

**File**: `api/main.py`

Current mounts:
```python
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
app.mount("/repos", StaticFiles(directory="Strivers-A2Z-DSA-Sheet"), name="repos")
app.mount("/components", StaticFiles(directory="frontend/components"), name="components")
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

**Verification Tasks**:
- [ ] `/assets/css/*` serves CSS files
- [ ] `/assets/js/*` serves JavaScript files
- [ ] `/repos/*` serves C++ source files
- [ ] `/components/*` serves HTML partials
- [ ] `/favicon.ico` returns favicon file

### 1.2 Fix Favicon Route

**File**: `api/main.py`

```python
import os
from pathlib import Path

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon with proper content type."""
    favicon_path = Path("frontend/favicon.ico")
    if not favicon_path.exists():
        # Return 1x1 transparent GIF as fallback
        return Response(
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            media_type="image/gif"
        )
    return FileResponse(favicon_path, media_type="image/x-icon")
```

## Phase 2: Study Plan API

### 2.1 Current Implementation

**File**: `api/services.py`

The study plan endpoints currently return empty data because:
1. No actual study plan file exists
2. `get_study_plan()` method is a stub
3. `rebuild_data()` doesn't trigger plan generation

### 2.2 Implement Study Plan Service

**File**: `api/services.py`

```python
from pathlib import Path
import json
from datetime import datetime, timedelta

class StudyPlanService:
    """Service for generating and managing study plans."""

    PLAN_FILE = Path("data/study_plan.json")

    def get_study_plan(self) -> dict:
        """Get the current study plan."""
        if not self.PLAN_FILE.exists():
            return self._generate_default_plan()

        with open(self.PLAN_FILE) as f:
            return json.load(f)

    def get_today_plan(self) -> dict:
        """Get today's study tasks."""
        plan = self.get_study_plan()
        today = datetime.now().strftime("%A").lower()

        for day_plan in plan.get("plans", []):
            if day_plan.get("day_name", "").lower() == today:
                return day_plan

        # Return first day if today not found
        return plan.get("plans", [{}])[0]

    def generate_plan(self, days: int = 14, daily_hours: float = 2.0) -> dict:
        """Generate a new study plan."""
        from scripts.study_plan_generator import generate_study_plan

        questions = data_service.get_question_list()
        unsolved = [q for q in questions if q.status != "solved"]

        plan = generate_study_plan(
            tasks=unsolved,
            days=days,
            daily_hours=daily_hours
        )

        # Save plan
        self.PLAN_FILE.parent.mkdir(exist_ok=True)
        with open(self.PLAN_FILE, "w") as f:
            json.dump(plan, f, indent=2)

        return plan

    def _generate_default_plan(self) -> dict:
        """Generate a minimal default plan."""
        return {
            "plans": [],
            "summary": {
                "total_study_time": 0,
                "average_daily_time": 0,
                "total_tasks": 0,
                "average_tasks_per_day": 0
            },
            "generated_at": datetime.now().isoformat()
        }

study_plan_service = StudyPlanService()
```

### 2.3 Update API Endpoints

**File**: `api/main.py`

```python
@app.post("/api/study-plan/generate")
async def generate_study_plan(
    days: int = 14,
    daily_hours: float = 2.0
):
    """Generate a new study plan."""
    try:
        plan = study_plan_service.generate_plan(days, daily_hours)
        return {"status": "ok", "plan": plan}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}

@app.get("/api/study-plan")
async def get_study_plan():
    """Get the current study plan."""
    try:
        return study_plan_service.get_study_plan()
    except Exception as exc:
        logger.error(f"Error getting study plan: {exc}")
        return {"plans": [], "summary": {}}

@app.get("/api/study-plan/today")
async def get_today_plan():
    """Get today's study tasks."""
    try:
        return study_plan_service.get_today_plan()
    except Exception as exc:
        logger.error(f"Error getting today's plan: {exc}")
        return {"day_name": "", "tasks": [], "total_time": 0}
```

### 2.4 Rebuild Endpoint Enhancement

**File**: `api/main.py`

```python
import asyncio

@app.post("/api/rebuild")
async def rebuild_data():
    """Rebuild all data indices."""
    try:
        # Run rebuild in background thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _perform_rebuild)
        return {"status": "ok", "message": "Data rebuilt successfully"}
    except Exception as exc:
        logger.error(f"Rebuild failed: {exc}")
        return {"status": "error", "detail": str(exc)}

def _perform_rebuild():
    """Perform the actual rebuild."""
    from scripts.extract_cpp_questions_batch import main as extract_main
    from scripts.build_index import main as index_main

    # Extract questions
    extract_main()

    # Build index
    index_main()

    # Generate new study plan
    study_plan_service.generate_plan()
```

## Phase 3: Error Handling

### 3.1 API Error Response Model

**File**: `api/models.py`

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str
    error_code: str | None = None
    context: dict | None = None

class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    detail: list[dict]
```

### 3.2 Exception Handlers

**File**: `api/main.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid input data",
            "errors": exc.errors()
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileNotFoundError)
async def not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle not found errors."""
    logger.info(f"FileNotFoundError: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Resource not found"}
    )
```

### 3.3 Endpoint-Specific Error Handling

**File**: `api/routers/questions.py`

```python
from fastapi import HTTPException

@router.post("/questions/{question_id}/run")
async def run_code(question_id: str, code_request: CodeRequest):
    """Run code with comprehensive error handling."""
    try:
        question = data_service.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        result = execute_code(code_request.code)

        if result.get("timeout"):
            raise HTTPException(
                status_code=408,
                detail="Execution timeout. Your code took too long to run."
            )

        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Code execution error: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while executing your code."
        )
```

## Phase 4: Request/Response Models

### 4.1 Complete Pydantic Models

**File**: `api/models.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SampleTest(BaseModel):
    """Sample test case model."""
    id: int
    input: str
    output: str
    explanation: Optional[str] = None

class Resource(BaseModel):
    """Resource link model."""
    title: str
    url: str
    notes: Optional[str] = None

class Metadata(BaseModel):
    """Question metadata model."""
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    source_file: Optional[str] = None

class Question(BaseModel):
    """Question model."""
    id: str
    title: str
    difficulty: str
    tags: List[str]
    statement_markdown: Optional[str] = None
    starter_code: Optional[str] = None
    sample_tests: List[SampleTest] = []
    resources: List[Resource] = []
    metadata: Metadata
    status: str = "unsolved"
    attempts: int = 0

class QuestionList(BaseModel):
    """Question list response."""
    questions: List[Question]
    total: int
    page: int = 1
    per_page: int = 50

class CodeRequest(BaseModel):
    """Code execution request."""
    code: str = Field(..., min_length=1, max_length=10000)

class CodeResponse(BaseModel):
    """Code execution response."""
    stdout: str
    stderr: str
    exit_code: int
    timeout: bool = False
    execution_time: float
```

## Phase 5: Response Building

### 5.1 Path Normalization in Responses

**File**: `api/services.py`

```python
def build_question_response(question_data: dict) -> dict:
    """Build API response with normalized paths."""
    response = question_data.copy()

    # Normalize resource URLs
    if "resources" in response:
        for resource in response["resources"]:
            if "url" in resource:
                resource["url"] = normalize_resource_path(resource["url"])

    # Ensure all required fields exist
    response.setdefault("status", "unsolved")
    response.setdefault("attempts", 0)

    # Clean up metadata
    if "metadata" in response and response["metadata"]:
        # Remove internal flags
        response["metadata"].pop("needs_ai_generation", None)

    return response
```

## Phase 6: Logging Configuration

### 6.1 Setup Application Logging

**File**: `api/logging_config.py`

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """Configure application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

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
```

### 6.2 Request Logging Middleware

**File**: `api/main.py`

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing."""

    async def dispatch(self, request, call_next):
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

app.add_middleware(RequestLoggingMiddleware)
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Fix favicon route | Low | - |
| 2 | Verify all static mounts work | Medium | - |
| 3 | Implement StudyPlanService | High | - |
| 4 | Add generate study plan endpoint | High | Step 3 |
| 5 | Enhance rebuild endpoint | Medium | Step 4 |
| 6 | Add exception handlers | High | - |
| 7 | Complete Pydantic models | Medium | - |
| 8 | Add path normalization | Medium | - |
| 9 | Setup logging configuration | High | - |
| 10 | Add request logging middleware | Medium | Step 9 |

## Success Criteria

- [ ] All static files serve correctly (no 404s)
- [ ] Favicon loads without errors
- [ ] Study plan endpoints return valid data
- [ ] Generate study plan creates actual plans
- [ ] All errors return structured JSON responses
- [ ] No stack traces exposed to clients
- [ ] Request/response models match frontend expectations
- [ ] All resource URLs use `/repos/` format
- [ ] Logs capture all API activity
- [ ] Request timing is logged
