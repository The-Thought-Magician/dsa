"""
Data Models for DSA Learning System

Defines the core data structures used throughout the application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    """Problem difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class ProblemStatus(str, Enum):
    """User's progress status on a problem"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SOLVED = "Solved"
    MASTERED = "Mastered"


class Problem(BaseModel):
    """Core problem data structure"""
    id: str
    title: str
    file_path: str
    category: str
    step: str
    difficulty: DifficultyLevel
    patterns: List[str]
    concepts: List[str]
    solution_code: str
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    description: Optional[str] = None
    hints: List[str] = Field(default_factory=list)


class TestCase(BaseModel):
    """Test case for a problem"""
    input_data: str
    expected_output: str
    explanation: Optional[str] = None


class UserProgress(BaseModel):
    """User's progress on a specific problem"""
    user_id: str
    problem_id: str
    status: ProblemStatus
    attempts: int = 0
    time_spent: int = 0  # seconds
    solution_code: Optional[str] = None
    last_attempt: Optional[datetime] = None
    pattern_mastery: Dict[str, float] = Field(default_factory=dict)
    mistake_patterns: List[str] = Field(default_factory=list)


class AIInteraction(BaseModel):
    """AI tutor interaction record"""
    interaction_id: str
    user_id: str
    problem_id: Optional[str] = None
    query: str
    response: str
    interaction_type: str  # hint, explanation, review, etc.
    timestamp: datetime
    helpful: Optional[bool] = None


class LearningSession(BaseModel):
    """Learning session data"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    problems_attempted: List[str] = Field(default_factory=list)
    problems_solved: List[str] = Field(default_factory=list)
    patterns_practiced: List[str] = Field(default_factory=list)
    ai_interactions: List[str] = Field(default_factory=list)
    performance_score: Optional[float] = None


class ProblemFilter(BaseModel):
    """Filters for problem queries"""
    categories: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    difficulties: Optional[List[DifficultyLevel]] = None
    concepts: Optional[List[str]] = None
    status: Optional[List[ProblemStatus]] = None
    search_query: Optional[str] = None


class ProblemResponse(BaseModel):
    """Response model for problem queries"""
    problems: List[Problem]
    total_count: int
    filtered_count: int
    page: int
    page_size: int


class ProgressSummary(BaseModel):
    """Summary of user's overall progress"""
    user_id: str
    total_problems: int
    solved_problems: int
    in_progress_problems: int
    mastered_problems: int
    pattern_mastery: Dict[str, float]
    difficulty_breakdown: Dict[DifficultyLevel, Dict[str, int]]
    recent_activity: List[Dict[str, Any]]


class CodeExecutionRequest(BaseModel):
    """Request to execute code"""
    code: str
    problem_id: Optional[str] = None
    test_cases: Optional[List[TestCase]] = None


class CodeExecutionResult(BaseModel):
    """Result of code execution"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    test_results: Optional[List[Dict[str, Any]]] = None


class AITutorRequest(BaseModel):
    """Request to AI tutor"""
    query: str
    problem_id: Optional[str] = None
    code: Optional[str] = None
    interaction_type: str = "general"  # hint, explanation, review, general


class AITutorResponse(BaseModel):
    """Response from AI tutor"""
    response: str
    suggestions: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None
    helpful_resources: Optional[List[str]] = None


class PatternAnalysis(BaseModel):
    """Analysis of problem patterns"""
    pattern_name: str
    problems_count: int
    mastery_level: float
    recommended_problems: List[str]
    weak_areas: List[str]
    next_steps: List[str]


class InterviewSimulation(BaseModel):
    """Interview simulation configuration"""
    duration_minutes: int = 45
    difficulty_levels: List[DifficultyLevel] = Field(default_factory=lambda: [DifficultyLevel.MEDIUM])
    patterns: Optional[List[str]] = None
    include_behavioral: bool = False


class InterviewSession(BaseModel):
    """Interview simulation session"""
    session_id: str
    user_id: str
    config: InterviewSimulation
    problems: List[str]
    current_problem: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    performance_metrics: Optional[Dict[str, Any]] = None