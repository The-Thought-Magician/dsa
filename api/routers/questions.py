from fastapi import APIRouter, HTTPException

from ..models import (
    QuestionListItem,
    QuestionDetail,
    QuestionRunRequest,
    QuestionRunResponse,
    QuestionSolutionResponse,
)
from ..services import data_service

questions_router = APIRouter(prefix="/api/questions", tags=["questions"])


@questions_router.get("", response_model=list[QuestionListItem])
async def list_questions() -> list[QuestionListItem]:
    try:
        return data_service.get_question_list()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # pragma: no cover - unexpected server error
        raise HTTPException(status_code=500, detail=str(exc))


@questions_router.get("/{question_id}", response_model=QuestionDetail)
async def get_question_detail(question_id: str) -> QuestionDetail:
    try:
        return data_service.get_question_detail(question_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@questions_router.post("/{question_id}/run", response_model=QuestionRunResponse)
async def run_question(question_id: str, request: QuestionRunRequest) -> QuestionRunResponse:
    try:
        return data_service.run_question(question_id, request, finalize=False)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@questions_router.post("/{question_id}/submit", response_model=QuestionRunResponse)
async def submit_question(question_id: str, request: QuestionRunRequest) -> QuestionRunResponse:
    try:
        return data_service.run_question(question_id, request, finalize=True)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@questions_router.post("/{question_id}/solution/view", response_model=QuestionSolutionResponse)
async def view_solution(question_id: str) -> QuestionSolutionResponse:
    try:
        return data_service.view_question_solution(question_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Question not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))
