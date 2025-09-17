from fastapi import APIRouter, HTTPException

from ..models import AIChatRequest, AIChatResponse
from ..services import ai_service, MissingAIKeyError

ai_router = APIRouter(prefix="/api/ai", tags=["ai"])


@ai_router.post("/ask", response_model=AIChatResponse)
async def ask_ai(request: AIChatRequest) -> AIChatResponse:
    try:
        return ai_service.ask(request)
    except MissingAIKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))
