from typing import List, Optional, Dict, Any, Literal
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


class QuestionResource(BaseModel):
    title: str
    url: str
    notes: Optional[str] = None


class QuestionSampleTest(BaseModel):
    id: int
    input: str
    output: str
    explanation: Optional[str] = None


class QuestionListItem(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: List[str]
    status: Literal["unsolved", "attempted", "solved"]
    solution_viewed: bool = False


class QuestionDetail(BaseModel):
    id: str
    title: str
    difficulty: str
    tags: List[str]
    status: Literal["unsolved", "attempted", "solved"]
    statement_markdown: str
    starter_code: str
    resources: List[QuestionResource]
    sample_tests: List[QuestionSampleTest]
    metadata: Dict[str, Any]
    solution_available: bool = True
    solution_viewed: bool = False


class QuestionSolutionResponse(BaseModel):
    solution_markdown: str
    metadata: Dict[str, Any]
    viewed_at_iso: str


class TestCaseResult(BaseModel):
    index: int
    input_preview: str
    expected_output: str
    actual_output: str
    stderr: str
    passed: bool
    runtime_ms: float


class QuestionRunRequest(BaseModel):
    code: str
    language: Literal["python"] = "python"


class QuestionRunResponse(BaseModel):
    verdict: Literal["passed", "failed", "error"]
    summary: str
    results: List[TestCaseResult]
    updated_status: Literal["unsolved", "attempted", "solved"]


class AIMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AIChatRequest(BaseModel):
    question_id: str
    messages: List[AIMessage]
    code: Optional[str] = None
    language: Literal["python"] = "python"


class AIChatResponse(BaseModel):
    message: str
    references: List[QuestionResource]
    guardrail_triggered: bool = False
