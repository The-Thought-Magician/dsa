"""
Problems API Routes

Handles all problem-related endpoints including browsing, filtering, and searching.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_database, DatabaseManager
from ..models import (
    Problem, ProblemFilter, ProblemResponse, DifficultyLevel
)

router = APIRouter()


@router.get("/", response_model=ProblemResponse)
async def get_problems(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    pattern: Optional[str] = Query(None, description="Filter by pattern"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: DatabaseManager = Depends(get_database)
):
    """Get paginated list of problems with optional filtering"""

    # Load all problems
    all_problems = db.load_problems()

    # Apply filters
    filtered_problems = all_problems

    if category:
        filtered_problems = [p for p in filtered_problems if p.category == category]

    if pattern:
        filtered_problems = [p for p in filtered_problems if pattern in p.patterns]

    if difficulty:
        filtered_problems = [p for p in filtered_problems if p.difficulty == difficulty]

    if search:
        search_lower = search.lower()
        filtered_problems = [
            p for p in filtered_problems
            if search_lower in p.title.lower() or
            (p.description and search_lower in p.description.lower())
        ]

    # Calculate pagination
    total_count = len(all_problems)
    filtered_count = len(filtered_problems)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_problems = filtered_problems[start_idx:end_idx]

    return ProblemResponse(
        problems=paginated_problems,
        total_count=total_count,
        filtered_count=filtered_count,
        page=page,
        page_size=page_size
    )


@router.get("/{problem_id}", response_model=Problem)
async def get_problem(
    problem_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get a specific problem by ID"""
    problem = db.get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/categories/list")
async def get_categories(db: DatabaseManager = Depends(get_database)):
    """Get all problem categories with counts"""
    categories = db.get_categories()

    # Add problem counts
    result = {}
    for category, problem_ids in categories.items():
        result[category] = {
            "count": len(problem_ids),
            "problems": problem_ids
        }

    return result


@router.get("/patterns/list")
async def get_patterns(db: DatabaseManager = Depends(get_database)):
    """Get all patterns with problem counts"""
    patterns = db.get_patterns()

    # Add problem counts
    result = {}
    for pattern, problem_ids in patterns.items():
        result[pattern] = {
            "count": len(problem_ids),
            "problems": problem_ids
        }

    return result


@router.get("/difficulty/distribution")
async def get_difficulty_distribution(db: DatabaseManager = Depends(get_database)):
    """Get problem difficulty distribution"""
    distribution = db.get_difficulty_distribution()

    # Add counts
    result = {}
    for difficulty, problem_ids in distribution.items():
        result[difficulty] = {
            "count": len(problem_ids),
            "problems": problem_ids
        }

    return result


@router.get("/search/{query}")
async def search_problems(
    query: str,
    limit: int = Query(20, ge=1, le=100),
    db: DatabaseManager = Depends(get_database)
):
    """Search problems by query string"""
    problems = db.search_problems(query)
    return {
        "query": query,
        "results": problems[:limit],
        "total_found": len(problems)
    }


@router.get("/category/{category}")
async def get_problems_by_category(
    category: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get all problems in a specific category"""
    problems = db.get_problems_by_category(category)
    if not problems:
        raise HTTPException(status_code=404, detail="Category not found or empty")

    return {
        "category": category,
        "count": len(problems),
        "problems": problems
    }


@router.get("/pattern/{pattern}")
async def get_problems_by_pattern(
    pattern: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get all problems for a specific pattern"""
    problems = db.get_problems_by_pattern(pattern)
    if not problems:
        raise HTTPException(status_code=404, detail="Pattern not found or no problems available")

    return {
        "pattern": pattern,
        "count": len(problems),
        "problems": problems
    }


@router.get("/random/{difficulty}")
async def get_random_problem(
    difficulty: DifficultyLevel,
    pattern: Optional[str] = Query(None, description="Filter by pattern"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: DatabaseManager = Depends(get_database)
):
    """Get a random problem with optional filters"""
    import random

    problems = db.get_problems_by_difficulty(difficulty.value)

    if pattern:
        problems = [p for p in problems if pattern in p.patterns]

    if category:
        problems = [p for p in problems if p.category == category]

    if not problems:
        raise HTTPException(status_code=404, detail="No problems found matching criteria")

    return random.choice(problems)