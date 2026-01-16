from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..models import (
    QuestionListItem,
    QuestionDetail,
    QuestionRunRequest,
    QuestionRunResponse,
    QuestionSolutionResponse,
)
from ..services import data_service

limiter = Limiter(key_func=get_remote_address)
questions_router = APIRouter(prefix="/api/questions", tags=["questions"])


@questions_router.get("", response_model=list[QuestionListItem])
async def list_questions(request: Request):
    """List all questions with filtering support."""
    try:
        return data_service.get_question_list()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load questions")


@questions_router.get("/{question_id}", response_model=QuestionDetail)
async def get_question_detail(question_id: str):
    """Get detailed information about a specific question."""
    try:
        return data_service.get_question_detail(question_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load question")


@questions_router.post("/{question_id}/run", response_model=QuestionRunResponse)
async def run_question(question_id: str, request: QuestionRunRequest):
    """Run code against sample tests. Rate limited to 10/minute."""
    try:
        return data_service.run_question(question_id, request, finalize=False)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to execute code")


@questions_router.post("/{question_id}/submit", response_model=QuestionRunResponse)
async def submit_question(question_id: str, request: QuestionRunRequest):
    """Submit solution and update status. Rate limited to 10/minute."""
    try:
        return data_service.run_question(question_id, request, finalize=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to submit solution")


@questions_router.post("/{question_id}/solution/view", response_model=QuestionSolutionResponse)
async def view_solution(question_id: str):
    """View the solution for a question."""
    try:
        return data_service.view_question_solution(question_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load solution")
