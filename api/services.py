import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from .models import TopicResponse, MappingResponse, CoverageResponse, StatsResponse, StudyPlanResponse, DailyPlanResponse, StudyTaskResponse

class DataService:
    def __init__(self):
        self.data_dir = Path("data")
        self.scripts_dir = Path("scripts")

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
                ['python', 'scripts/coverage_checker.py'],
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

    def get_study_plan(self) -> DailyPlanResponse:
        plan_file = self.data_dir / "study_plan_14day.json"

        if not plan_file.exists():
            subprocess.run(['python', 'scripts/study_plan_generator.py'], check=True, cwd='.')

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
            "build_index.py"
        ]

        for script in scripts:
            subprocess.run(['python', f'scripts/{script}'], check=True, cwd='.')

data_service = DataService()