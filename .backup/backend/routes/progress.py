"""
Progress Tracking API Routes

Handles user progress tracking, statistics, and learning analytics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_database, DatabaseManager
from ..models import (
    UserProgress, LearningSession, ProblemStatus, ProgressSummary,
    DifficultyLevel
)

router = APIRouter()


@router.post("/update")
async def update_progress(
    progress: UserProgress,
    db: DatabaseManager = Depends(get_database)
):
    """Update user progress for a problem"""
    # Update last_attempt timestamp
    progress.last_attempt = datetime.utcnow()

    # Save to database
    db.save_user_progress(progress)

    return {"message": "Progress updated successfully", "progress": progress}


@router.get("/{user_id}", response_model=List[UserProgress])
async def get_user_progress(
    user_id: str,
    problem_id: Optional[str] = Query(None, description="Specific problem ID"),
    db: DatabaseManager = Depends(get_database)
):
    """Get user progress for all problems or a specific problem"""
    progress = db.get_user_progress(user_id, problem_id)
    return progress


@router.get("/{user_id}/summary", response_model=ProgressSummary)
async def get_progress_summary(
    user_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get comprehensive progress summary for user"""

    # Get all user progress
    user_progress = db.get_user_progress(user_id)
    all_problems = db.load_problems()

    # Calculate basic stats
    total_problems = len(all_problems)
    solved_problems = len([p for p in user_progress if p.status == ProblemStatus.SOLVED])
    in_progress_problems = len([p for p in user_progress if p.status == ProblemStatus.IN_PROGRESS])
    mastered_problems = len([p for p in user_progress if p.status == ProblemStatus.MASTERED])

    # Calculate pattern mastery
    pattern_mastery = {}
    for progress in user_progress:
        for pattern, mastery in progress.pattern_mastery.items():
            if pattern not in pattern_mastery:
                pattern_mastery[pattern] = []
            pattern_mastery[pattern].append(mastery)

    # Average mastery per pattern
    avg_pattern_mastery = {}
    for pattern, masteries in pattern_mastery.items():
        avg_pattern_mastery[pattern] = sum(masteries) / len(masteries)

    # Difficulty breakdown
    difficulty_breakdown = {
        DifficultyLevel.EASY: {"solved": 0, "total": 0},
        DifficultyLevel.MEDIUM: {"solved": 0, "total": 0},
        DifficultyLevel.HARD: {"solved": 0, "total": 0}
    }

    # Count problems by difficulty
    for problem in all_problems:
        difficulty_breakdown[problem.difficulty]["total"] += 1

    # Count solved problems by difficulty
    solved_problem_ids = [p.problem_id for p in user_progress if p.status == ProblemStatus.SOLVED]
    for problem in all_problems:
        if problem.id in solved_problem_ids:
            difficulty_breakdown[problem.difficulty]["solved"] += 1

    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activity = []
    for progress in user_progress:
        if progress.last_attempt and progress.last_attempt > week_ago:
            problem = next((p for p in all_problems if p.id == progress.problem_id), None)
            if problem:
                recent_activity.append({
                    "problem_id": progress.problem_id,
                    "problem_title": problem.title,
                    "status": progress.status,
                    "last_attempt": progress.last_attempt,
                    "attempts": progress.attempts
                })

    # Sort by last attempt
    recent_activity.sort(key=lambda x: x["last_attempt"], reverse=True)

    return ProgressSummary(
        user_id=user_id,
        total_problems=total_problems,
        solved_problems=solved_problems,
        in_progress_problems=in_progress_problems,
        mastered_problems=mastered_problems,
        pattern_mastery=avg_pattern_mastery,
        difficulty_breakdown=difficulty_breakdown,
        recent_activity=recent_activity[:10]  # Latest 10 activities
    )


@router.post("/session/start")
async def start_learning_session(
    user_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Start a new learning session"""
    session = LearningSession(
        session_id=f"session_{user_id}_{int(datetime.utcnow().timestamp())}",
        user_id=user_id,
        start_time=datetime.utcnow()
    )

    db.save_learning_session(session)

    return {"message": "Learning session started", "session": session}


@router.post("/session/{session_id}/end")
async def end_learning_session(
    session_id: str,
    problems_attempted: List[str],
    problems_solved: List[str],
    patterns_practiced: List[str],
    performance_score: Optional[float] = None,
    db: DatabaseManager = Depends(get_database)
):
    """End a learning session with results"""

    # For simplicity, we'll create a new session object
    # In a real app, you'd update the existing session
    session = LearningSession(
        session_id=session_id,
        user_id="",  # Would need to look this up from existing session
        start_time=datetime.utcnow() - timedelta(hours=1),  # Placeholder
        end_time=datetime.utcnow(),
        problems_attempted=problems_attempted,
        problems_solved=problems_solved,
        patterns_practiced=patterns_practiced,
        performance_score=performance_score
    )

    return {"message": "Learning session ended", "session": session}


@router.get("/{user_id}/sessions")
async def get_learning_sessions(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: DatabaseManager = Depends(get_database)
):
    """Get recent learning sessions for user"""
    sessions = db.get_learning_sessions(user_id, limit)
    return sessions


@router.get("/{user_id}/patterns/analysis")
async def get_pattern_analysis(
    user_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get detailed pattern analysis for user"""

    user_progress = db.get_user_progress(user_id)
    all_problems = db.load_problems()
    patterns_index = db.get_patterns()

    analysis = {}

    for pattern, problem_ids in patterns_index.items():
        # Get user progress for this pattern
        pattern_progress = []
        for progress in user_progress:
            problem = next((p for p in all_problems if p.id == progress.problem_id), None)
            if problem and pattern in problem.patterns:
                pattern_progress.append(progress)

        # Calculate mastery level
        if pattern_progress:
            solved_count = len([p for p in pattern_progress if p.status == ProblemStatus.SOLVED])
            mastery_level = solved_count / len(problem_ids) if problem_ids else 0
        else:
            mastery_level = 0

        # Find recommended problems (unsolved problems in this pattern)
        solved_problem_ids = [p.problem_id for p in pattern_progress if p.status == ProblemStatus.SOLVED]
        recommended_problems = [pid for pid in problem_ids if pid not in solved_problem_ids][:5]

        # Identify weak areas (problems with multiple failed attempts)
        weak_areas = []
        for progress in pattern_progress:
            if progress.attempts > 3 and progress.status != ProblemStatus.SOLVED:
                problem = next((p for p in all_problems if p.id == progress.problem_id), None)
                if problem:
                    weak_areas.append(problem.title)

        analysis[pattern] = {
            "problems_count": len(problem_ids),
            "solved_count": len([p for p in pattern_progress if p.status == ProblemStatus.SOLVED]),
            "mastery_level": mastery_level,
            "recommended_problems": recommended_problems,
            "weak_areas": weak_areas,
            "total_attempts": sum(p.attempts for p in pattern_progress),
            "avg_attempts_per_problem": (
                sum(p.attempts for p in pattern_progress) / len(pattern_progress)
                if pattern_progress else 0
            )
        }

    return analysis


@router.get("/{user_id}/streaks")
async def get_learning_streaks(
    user_id: str,
    db: DatabaseManager = Depends(get_database)
):
    """Get learning streaks and consistency metrics"""

    user_progress = db.get_user_progress(user_id)

    # Sort by last attempt date
    progress_by_date = {}
    for progress in user_progress:
        if progress.last_attempt:
            date_key = progress.last_attempt.date()
            if date_key not in progress_by_date:
                progress_by_date[date_key] = 0
            progress_by_date[date_key] += 1

    # Calculate current streak
    current_streak = 0
    current_date = datetime.utcnow().date()

    while current_date in progress_by_date:
        current_streak += 1
        current_date -= timedelta(days=1)

    # Calculate longest streak
    longest_streak = 0
    temp_streak = 0
    sorted_dates = sorted(progress_by_date.keys())

    for i, date in enumerate(sorted_dates):
        if i == 0 or (date - sorted_dates[i-1]).days == 1:
            temp_streak += 1
        else:
            longest_streak = max(longest_streak, temp_streak)
            temp_streak = 1

    longest_streak = max(longest_streak, temp_streak)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "active_days": len(progress_by_date),
        "problems_solved_today": progress_by_date.get(datetime.utcnow().date(), 0),
        "weekly_activity": dict(list(progress_by_date.items())[-7:])  # Last 7 days
    }