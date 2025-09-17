from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

router = APIRouter()

MAPPINGS_PATH = Path('data/problem_mappings.json')


def load_mappings():
    if not MAPPINGS_PATH.exists():
        raise HTTPException(status_code=404, detail='Mapping file not generated')
    with open(MAPPINGS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.get('/mappings')
async def get_all_mappings(status: str | None = None, limit: int | None = None):
    data = load_mappings()
    items = data.get('items', [])
    if status:
        items = [m for m in items if m.get('match_status') == status]
    if limit:
        items = items[:limit]
    return {'count': len(items), 'items': items}


@router.get('/mappings/summary')
async def get_mappings_summary():
    data = load_mappings()
    items = data.get('items', [])
    summary = {'matched': 0, 'python_only': 0, 'unmatched': 0}
    for m in items:
        st = m.get('match_status')
        if st in summary:
            summary[st] += 1
    return {'generated_at': data.get('generated_at'), 'summary': summary, 'total': len(items)}


@router.get('/mappings/next')
async def get_next_unmatched(limit: int = 20):
    data = load_mappings()
    items = [m for m in data.get('items', []) if m.get('match_status') == 'unmatched']
    return {'count': len(items[:limit]), 'items': items[:limit]}
