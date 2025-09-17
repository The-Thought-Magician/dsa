from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TopicResponse(BaseModel):
    id: str
    title: str
    path: str
    step_number: int
    status: str
    problem_count: int
    file_count: int
    tags: List[str]
    source_links: List[str]
    related_problems: List[str]
    local_files: List[str]
    notes: str

class MappingResponse(BaseModel):
    problem_id: str
    title: str
    a2z_path: str
    python_file_path: Optional[str]
    cpp_file_path: Optional[str]
    status: str
    approach_summary: Optional[str]
    time_complexity: Optional[str]
    space_complexity: Optional[str]
    tags: List[str]

class CoverageResponse(BaseModel):
    total_sections: int
    total_problems: int
    coverage_percentage: float
    exact_matches: int
    approximate_matches: int
    missing_implementations: int
    coverage_by_section: Dict[str, Dict[str, Any]]
    gaps: Dict[str, List[str]]
    recommendations: List[str]

class StatsResponse(BaseModel):
    total_sections: int
    total_problems: int
    python_solutions: int
    cpp_solutions: int
    exact_matches: int
    approx_matches: int
    coverage_percentage: float

class StudyTaskResponse(BaseModel):
    id: str
    title: str
    type: str
    section: str
    problems: List[str]
    estimated_time: int
    priority: str
    files: List[str]
    notes: str
    difficulty: str

class StudyPlanResponse(BaseModel):
    date: str
    day_name: str
    total_time: int
    task_count: int
    tasks: List[StudyTaskResponse]

class DailyPlanResponse(BaseModel):
    plans: List[StudyPlanResponse]
    summary: Dict[str, Any]