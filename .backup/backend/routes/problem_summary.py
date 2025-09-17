from fastapi import APIRouter, Depends, Query
from ..database import get_database, DatabaseManager

router = APIRouter()


@router.get('/problems/summary')
async def problem_summaries(
    pattern: str | None = Query(None),
    difficulty: str | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: DatabaseManager = Depends(get_database)
):
    problems = db.load_problems()
    if pattern:
        problems = [p for p in problems if pattern in p.patterns]
    if difficulty:
        problems = [p for p in problems if p.difficulty.value == difficulty]
    items = [
        {
            'id': p.id,
            'title': p.title,
            'difficulty': p.difficulty.value,
            'patterns': p.patterns,
            'category': p.category
        }
        for p in problems[:limit]
    ]
    return {'count': len(items), 'items': items}
