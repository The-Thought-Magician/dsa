from fastapi import APIRouter, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..models import AIChatRequest, AIChatResponse
from ..services import (
    ai_service,
    MissingAIKeyError,
    AIServiceError,
    AIModelTimeoutError,
    AIModelRateLimitError,
    AIModelBadInputError,
)

limiter = Limiter(key_func=get_remote_address)
ai_router = APIRouter(prefix="/api/ai", tags=["ai"])


@ai_router.post("/ask", response_model=AIChatResponse)
async def ask_ai(request: AIChatRequest):
    """Get AI assistance for a question. Rate limited to 20/minute."""
    try:
        return ai_service.ask(request)
    except MissingAIKeyError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI service configuration error. Please contact support."
        )
    except AIModelTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="AI request timed out. Please try again."
        )
    except AIModelRateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="AI rate limit exceeded. Please wait a moment and retry."
        )
    except AIModelBadInputError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid input provided to AI service."
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail="AI service temporarily unavailable. Please try again shortly."
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI service initialization failed. Please contact support."
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred with the AI service."
        )
