from fastapi import APIRouter, HTTPException

from ..models import AIChatRequest, AIChatResponse
from ..services import (
    ai_service,
    MissingAIKeyError,
    AIServiceError,
    AIModelTimeoutError,
    AIModelRateLimitError,
    AIModelBadInputError,
)

ai_router = APIRouter(prefix="/api/ai", tags=["ai"])


@ai_router.post("/ask", response_model=AIChatResponse)
async def ask_ai(request: AIChatRequest) -> AIChatResponse:
    try:
        return ai_service.ask(request)
    except MissingAIKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except AIModelTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc))
    except AIModelRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except AIModelBadInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except AIServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except RuntimeError as exc:
        # dependency or model initialization failure
        raise HTTPException(status_code=503, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))
