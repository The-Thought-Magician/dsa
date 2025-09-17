import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from .models import (
    TopicResponse,
    MappingResponse,
    CoverageResponse,
    StatsResponse,
    StudyPlanResponse,
    DailyPlanResponse,
    StudyTaskResponse,
    QuestionListItem,
    QuestionDetail,
    QuestionRunRequest,
    QuestionRunResponse,
    QuestionSolutionResponse,
    TestCaseResult,
    QuestionResource,
    AIChatRequest,
    AIChatResponse,
)

class MissingAIKeyError(RuntimeError):
    """Raised when no Gemini API key can be resolved."""


class DataService:
    def __init__(self):
        self.data_dir = Path("data")
        self.scripts_dir = Path("scripts")
        self.questions_payload_path = self.data_dir / "questions" / "questions.json"
        self.question_progress_path = self.data_dir / "question_progress.json"
        self._questions_cache: Optional[Dict[str, Any]] = None

    def load_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        entries = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line.strip()))
        return entries

    def get_topics(self, section: Optional[str] = None, status: Optional[str] = None) -> List[TopicResponse]:
        index_entries = self.load_jsonl(self.data_dir / "index.jsonl")

        filtered = index_entries
        if section:
            filtered = [e for e in filtered if section.lower() in e['title'].lower()]
        if status:
            filtered = [e for e in filtered if e['status'] == status]

        topics = []
        for entry in filtered:
            if 'sub' not in entry['id']:
                topics.append(TopicResponse(
                    id=entry['id'],
                    title=entry['title'],
                    path=entry['path'],
                    step_number=entry['step_number'],
                    status=entry['status'],
                    problem_count=len(entry['related_problems']),
                    file_count=len(entry['local_files']),
                    tags=entry['tags'],
                    source_links=entry['source_links'],
                    related_problems=entry['related_problems'],
                    local_files=entry['local_files'],
                    notes=entry['notes']
                ))

        return sorted(topics, key=lambda x: x.step_number)

    def get_topic_by_id(self, topic_id: str) -> Optional[TopicResponse]:
        topics = self.get_topics()
        return next((t for t in topics if t.id == topic_id), None)

    def get_mappings(self) -> List[MappingResponse]:
        mapping_entries = self.load_jsonl(self.data_dir / "mapping.jsonl")

        mappings = []
        for entry in mapping_entries:
            mappings.append(MappingResponse(
                problem_id=entry['problem_id'],
                title=entry['title'],
                a2z_path=entry['a2z_path'],
                python_file_path=entry.get('python_file_path'),
                cpp_file_path=entry.get('cpp_file_path'),
                status=entry['status'],
                approach_summary=entry.get('approach_summary'),
                time_complexity=entry.get('time_complexity'),
                space_complexity=entry.get('space_complexity'),
                tags=entry.get('tags', [])
            ))

        return mappings

    def get_coverage(self) -> CoverageResponse:
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/coverage_checker.py'],
                capture_output=True,
                text=True,
                cwd='.'
            )

            index_entries = self.load_jsonl(self.data_dir / "index.jsonl")
            mapping_entries = self.load_jsonl(self.data_dir / "mapping.jsonl")

            total_sections = len([e for e in index_entries if 'sub' not in e['id']])
            total_problems = len(mapping_entries)

            python_solutions = len([m for m in mapping_entries if m.get('python_file_path')])
            cpp_solutions = len([m for m in mapping_entries if m.get('cpp_file_path')])

            exact_matches = len([m for m in mapping_entries if m.get('status') == 'exact-match'])
            approx_matches = len([m for m in mapping_entries if m.get('status') == 'approx'])

            missing_implementations = len([m for m in mapping_entries if not m.get('python_file_path')])

            coverage_percentage = (python_solutions + cpp_solutions) / (total_problems * 2) * 100 if total_problems > 0 else 0

            coverage_by_section = {}
            for entry in index_entries:
                if 'sub' not in entry['id']:
                    coverage_by_section[entry['title']] = {
                        'id': entry['id'],
                        'status': entry['status'],
                        'problem_count': len(entry['related_problems']),
                        'file_count': len(entry['local_files']),
                        'step_number': entry['step_number']
                    }

            missing_python = [m['title'] for m in mapping_entries if not m.get('python_file_path')]

            gaps = {
                'missing_sections': [],
                'missing_python': missing_python[:10],
                'low_coverage': []
            }

            recommendations = [
                f"Overall coverage is {coverage_percentage:.1f}%. Focus on completing missing implementations.",
                f"{missing_implementations} problems missing Python implementations. Prioritize these for practice."
            ]

            return CoverageResponse(
                total_sections=total_sections,
                total_problems=total_problems,
                coverage_percentage=coverage_percentage,
                exact_matches=exact_matches,
                approximate_matches=approx_matches,
                missing_implementations=missing_implementations,
                coverage_by_section=coverage_by_section,
                gaps=gaps,
                recommendations=recommendations
            )

        except Exception as e:
            raise Exception(f"Error generating coverage report: {str(e)}")

    def get_stats(self) -> StatsResponse:
        index_entries = self.load_jsonl(self.data_dir / "index.jsonl")
        mapping_entries = self.load_jsonl(self.data_dir / "mapping.jsonl")

        total_sections = len([e for e in index_entries if 'sub' not in e['id']])
        total_problems = len(mapping_entries)

        python_solutions = len([m for m in mapping_entries if m.get('python_file_path')])
        cpp_solutions = len([m for m in mapping_entries if m.get('cpp_file_path')])

        exact_matches = len([m for m in mapping_entries if m.get('status') == 'exact-match'])
        approx_matches = len([m for m in mapping_entries if m.get('status') == 'approx'])

        coverage = (python_solutions + cpp_solutions) / (total_problems * 2) * 100 if total_problems > 0 else 0

        return StatsResponse(
            total_sections=total_sections,
            total_problems=total_problems,
            python_solutions=python_solutions,
            cpp_solutions=cpp_solutions,
            exact_matches=exact_matches,
            approx_matches=approx_matches,
            coverage_percentage=coverage
        )

    # -----------------------------
    # Question dataset helpers
    # -----------------------------

    def _load_questions_payload(self) -> Dict[str, Any]:
        if self._questions_cache is None:
            if not self.questions_payload_path.exists():
                raise FileNotFoundError(
                    "Questions dataset missing. Run 'python scripts/build_questions_dataset.py'."
                )
            with open(self.questions_payload_path, encoding="utf-8") as fh:
                self._questions_cache = json.load(fh)
        return self._questions_cache

    def _load_question_progress(self) -> Dict[str, Any]:
        if not self.question_progress_path.exists():
            return {"statuses": {}, "solution_views": {}}
        with open(self.question_progress_path, encoding="utf-8") as fh:
            data = json.load(fh)
        data.setdefault("statuses", {})
        data.setdefault("solution_views", {})
        return data

    def _save_question_progress(self, progress: Dict[str, Any]) -> None:
        progress.setdefault("statuses", {})
        progress.setdefault("solution_views", {})
        self.question_progress_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.question_progress_path, "w", encoding="utf-8") as fh:
            json.dump(progress, fh, indent=2)

    def _preview_text(self, value: str, limit: int = 120) -> str:
        clean = value.replace("\n", "\\n")
        if len(clean) <= limit:
            return clean
        return f"{clean[: limit - 3]}..."

    def preview_text(self, value: str, limit: int = 120) -> str:
        return self._preview_text(value, limit)

    def _get_question_payload(self, question_id: str) -> Dict[str, Any]:
        payload = self._load_questions_payload()
        questions = {item["id"]: item for item in payload.get("questions", [])}
        if question_id not in questions:
            raise KeyError(f"Question '{question_id}' not found")
        return questions[question_id]

    def get_question_list(self) -> List[QuestionListItem]:
        payload = self._load_questions_payload()
        progress = self._load_question_progress()
        statuses = progress.get("statuses", {})
        solution_views = progress.get("solution_views", {})

        items: List[QuestionListItem] = []
        for raw in payload.get("questions", []):
            question_id = raw["id"]
            status = statuses.get(question_id, "unsolved")
            viewed = question_id in solution_views
            items.append(
                QuestionListItem(
                    id=question_id,
                    title=raw["title"],
                    difficulty=raw["difficulty"],
                    tags=raw.get("tags", []),
                    status=status,
                    solution_viewed=viewed,
                )
            )
        return items

    def get_question_detail(self, question_id: str) -> QuestionDetail:
        raw = self._get_question_payload(question_id)
        progress = self._load_question_progress()
        status = progress.get("statuses", {}).get(question_id, "unsolved")
        viewed = question_id in progress.get("solution_views", {})

        sample_tests = [
            {
                "id": idx,
                "input": test.get("input", ""),
                "output": test.get("output", ""),
                "explanation": test.get("explanation"),
            }
            for idx, test in enumerate(raw.get("sample_tests", []), start=1)
        ]

        return QuestionDetail(
            id=raw["id"],
            title=raw["title"],
            difficulty=raw.get("difficulty", "Unknown"),
            tags=raw.get("tags", []),
            status=status,
            statement_markdown=raw.get("statement_markdown", ""),
            starter_code=raw.get("starter_code", ""),
            resources=raw.get("resources", []),
            sample_tests=sample_tests,
            metadata=raw.get("metadata", {}),
            solution_available=bool(raw.get("solution_markdown")),
            solution_viewed=viewed,
        )

    def view_question_solution(self, question_id: str) -> QuestionSolutionResponse:
        raw = self._get_question_payload(question_id)
        if not raw.get("solution_markdown"):
            raise ValueError("Solution not available for this question")

        progress = self._load_question_progress()
        viewed_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        progress.setdefault("solution_views", {})[question_id] = viewed_at
        self._save_question_progress(progress)

        metadata = raw.get("metadata", {}).copy()
        metadata.setdefault("time_complexity", "")
        metadata.setdefault("space_complexity", "")

        return QuestionSolutionResponse(
            solution_markdown=raw["solution_markdown"],
            metadata=metadata,
            viewed_at_iso=viewed_at,
        )

    def _execute_python(self, code: str, stdin: str) -> Tuple[str, str, float, int]:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temp_path: Optional[Path] = None
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            temp_path = Path(tmp.name)
            tmp.write(code)

        if temp_path is None:
            raise RuntimeError("Could not create temporary execution file")

        try:
            started = time.perf_counter()
            completed = subprocess.run(
                [sys.executable, str(temp_path)],
                input=stdin,
                text=True,
                capture_output=True,
                timeout=5,
                cwd="."
            )
            runtime_ms = (time.perf_counter() - started) * 1000
            return completed.stdout, completed.stderr, runtime_ms, completed.returncode
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def run_question(self, question_id: str, request: QuestionRunRequest, *, finalize: bool = False) -> QuestionRunResponse:
        if request.language.lower() != "python":
            raise ValueError("Only Python execution is supported at the moment")
        if not request.code.strip():
            raise ValueError("Submission code cannot be empty")

        raw = self._get_question_payload(question_id)
        progress = self._load_question_progress()
        current_status = progress.get("statuses", {}).get(question_id, "unsolved")

        results: List[TestCaseResult] = []
        verdict = "passed"

        for index, test in enumerate(raw.get("sample_tests", []), start=1):
            stdin = test.get("input", "")
            expected = test.get("output", "")
            try:
                stdout, stderr, runtime_ms, return_code = self._execute_python(request.code, stdin)
            except subprocess.TimeoutExpired:
                verdict = "failed"
                results.append(
                    TestCaseResult(
                        index=index,
                        input_preview=self.preview_text(stdin),
                        expected_output=expected.strip(),
                        actual_output="",
                        stderr="Execution timed out after 5s",
                        passed=False,
                        runtime_ms=5000.0,
                    )
                )
                continue

            actual_clean = stdout.strip()
            expected_clean = expected.strip()
            stderr_clean = stderr.strip()

            passed = return_code == 0 and actual_clean == expected_clean and not stderr_clean
            if not passed and verdict == "passed":
                verdict = "failed"

            results.append(
                TestCaseResult(
                    index=index,
                    input_preview=self.preview_text(stdin),
                    expected_output=expected_clean,
                    actual_output=actual_clean,
                    stderr=stderr_clean,
                    passed=passed,
                    runtime_ms=round(runtime_ms, 2),
                )
            )

        if not results:
            verdict = "error"
            summary = "No sample tests available to validate the solution."
        elif verdict == "passed":
            summary = f"All {len(results)} sample tests passed."
        else:
            failed_cases = sum(1 for result in results if not result.passed)
            summary = f"{failed_cases} of {len(results)} sample tests failed."

        updated_status = current_status
        if finalize:
            updated_status = "solved" if verdict == "passed" else "attempted"
        else:
            if verdict != "error" and current_status == "unsolved":
                updated_status = "attempted"

        progress.setdefault("statuses", {})[question_id] = updated_status
        self._save_question_progress(progress)

        return QuestionRunResponse(
            verdict=verdict,
            summary=summary,
            results=results,
            updated_status=updated_status,
        )

    def get_study_plan(self) -> DailyPlanResponse:
        plan_file = self.data_dir / "study_plan_14day.json"

        if not plan_file.exists():
            subprocess.run([sys.executable, 'scripts/study_plan_generator.py'], check=True, cwd='.')

        with open(plan_file) as f:
            plan_data = json.load(f)

        plans = []
        total_time = 0
        total_tasks = 0

        for date_key, tasks in plan_data.items():
            date_parts = date_key.split(' (')
            date = date_parts[0]
            day_name = date_parts[1].rstrip(')') if len(date_parts) > 1 else ""

            daily_time = sum(task['estimated_time'] for task in tasks)
            total_time += daily_time
            total_tasks += len(tasks)

            study_tasks = []
            for task in tasks:
                study_tasks.append(StudyTaskResponse(
                    id=task['id'],
                    title=task['title'],
                    type=task['type'],
                    section=task['section'],
                    problems=task['problems'],
                    estimated_time=task['estimated_time'],
                    priority=task['priority'],
                    files=task['files'],
                    notes=task['notes'],
                    difficulty=task['difficulty']
                ))

            plans.append(StudyPlanResponse(
                date=date,
                day_name=day_name,
                total_time=daily_time,
                task_count=len(tasks),
                tasks=study_tasks
            ))

        summary = {
            'total_study_time': total_time,
            'average_daily_time': total_time // 14,
            'total_tasks': total_tasks,
            'average_tasks_per_day': total_tasks / 14
        }

        return DailyPlanResponse(plans=plans, summary=summary)

    def rebuild_data(self):
        scripts = [
            "analyze_repos.py",
            "build_a2z_structure.py",
            "build_index.py",
            "build_questions_dataset.py"
        ]

        for script in scripts:
            subprocess.run([sys.executable, f'scripts/{script}'], check=True, cwd='.')

        # ensure fresh view of generated datasets
        self._questions_cache = None


class AIService:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
        self._model = None

    def _resolve_api_key(self) -> str:
        direct = os.getenv("GEMINI_API_KEY")
        if direct and direct.strip():
            return direct.strip()

        dotenv_path = Path(".env")
        if dotenv_path.exists():
            for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                if key.strip() == "GEMINI_API_KEY" and value.strip():
                    return value.strip()
        return ""

    def _ensure_model(self):
        if self._model is not None:
            return

        api_key = self._resolve_api_key()
        if not api_key:
            raise MissingAIKeyError("GEMINI_API_KEY is not configured")

        try:
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("google-generativeai package is not installed") from exc

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    def ask(self, request: AIChatRequest) -> AIChatResponse:
        self._ensure_model()

        question = self.data_service.get_question_detail(request.question_id)
        allow_full_solution = question.solution_viewed

        system_prompt = (
            "You are an instructional assistant for the A2Z DSA Learning System. "
            "Offer targeted hints, explain concepts step-by-step, and encourage problem solving. "
            "Keep answers concise and relevant to the user's current question."
        )
        if not allow_full_solution:
            system_prompt += (
                " Do not provide full source code or the final answer. Focus on strategies,"
                " edge cases, and clarifying questions."
            )
        else:
            system_prompt += " The user has already viewed the editorial solution and direct answers are acceptable."

        context_lines = [
            f"Question: {question.title}",
            f"Difficulty: {question.difficulty}",
            f"Tags: {', '.join(question.tags)}",
            "Statement:",
            question.statement_markdown,
        ]

        if question.metadata:
            meta_parts = [
                f"  - {key.replace('_', ' ').title()}: {value}"
                for key, value in question.metadata.items()
                if value
            ]
            if meta_parts:
                context_lines.append("Key metadata:\n" + "\n".join(meta_parts))

        if question.sample_tests:
            sample_summary = []
            for test in question.sample_tests:
                preview_input = self.data_service.preview_text(test.input, limit=60)
                sample_summary.append(
                    f"  - Test {test.id}: input={preview_input}, expected={test.output.strip()}"
                )
            context_lines.append("Sample tests:\n" + "\n".join(sample_summary))

        base_context = "\n\n".join(context_lines)

        conversation = [
            {"role": "system", "parts": [{"text": system_prompt}]},
            {"role": "user", "parts": [{"text": base_context}]},
        ]

        if request.code:
            conversation.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "Here is the current attempt in Python:\n\n"
                                f"```python\n{request.code}\n```"
                            )
                        }
                    ],
                }
            )

        for message in request.messages:
            if message.role not in {"user", "assistant", "system"}:
                continue
            gemini_role = message.role if message.role != "system" else "user"
            conversation.append({"role": gemini_role, "parts": [{"text": message.content}]})

        model_response = self._model.generate_content(conversation)
        text_response = getattr(model_response, "text", None)
        if not text_response:
            parts = []
            for part in getattr(model_response, "parts", []) or []:
                part_text = getattr(part, "text", "")
                if part_text:
                    parts.append(part_text)
            text_response = "\n".join(parts) if parts else "I could not generate a response."

        guardrail_triggered = False
        if not allow_full_solution and "```" in text_response and "def " in text_response:
            guardrail_triggered = True
            text_response = (
                "Let's focus on the approach before diving into the full implementation. "
                "Consider identifying the data structure that keeps track of complements, "
                "and think about the order in which you evaluate the characters or numbers."
            )

        references = [QuestionResource(**resource) for resource in question.resources]

        return AIChatResponse(
            message=text_response.strip(),
            references=references,
            guardrail_triggered=guardrail_triggered,
        )


data_service = DataService()
ai_service = AIService(data_service)
