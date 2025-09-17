#!/usr/bin/env python3
"""
Generate spaced practice study plans with daily tasks.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class StudyTask:
    """Represents a single study task"""
    id: str
    title: str
    type: str  # "new_topic", "review", "practice"
    section: str
    problems: List[str]
    estimated_time: int  # minutes
    priority: str  # "high", "medium", "low"
    files: List[str]
    notes: str
    difficulty: str  # "easy", "medium", "hard"

def load_jsonl(file_path: str) -> List[dict]:
    """Load JSONL file"""
    entries = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line.strip()))
    return entries

def estimate_difficulty_from_section(section_title: str, subsection: str = "") -> str:
    """Estimate difficulty based on section and subsection"""
    # Basic heuristics for difficulty
    if any(word in section_title.lower() for word in ["basic", "learn", "intro"]):
        return "easy"

    if subsection:
        if "easy" in subsection.lower():
            return "easy"
        elif "medium" in subsection.lower():
            return "medium"
        elif "hard" in subsection.lower():
            return "hard"

    # Advanced topics are generally harder
    advanced_topics = ["dynamic programming", "graphs", "trees", "tries", "strings [advanced]"]
    if any(topic in section_title.lower() for topic in advanced_topics):
        return "hard"

    return "medium"  # Default

def estimate_time_per_problem(difficulty: str, problem_type: str) -> int:
    """Estimate time needed per problem in minutes"""
    base_times = {
        "easy": 15,
        "medium": 30,
        "hard": 45
    }

    multipliers = {
        "new_topic": 1.5,
        "review": 0.7,
        "practice": 1.0
    }

    return int(base_times.get(difficulty, 30) * multipliers.get(problem_type, 1.0))

def create_study_tasks_from_data(index_entries: List[dict], mapping_entries: List[dict]) -> List[StudyTask]:
    """Create study tasks from index and mapping data"""
    tasks = []

    # Group mappings by section
    mappings_by_section = defaultdict(list)
    for mapping in mapping_entries:
        section = mapping.get('a2z_path', '').split('/')[0] if '/' in mapping.get('a2z_path', '') else mapping.get('a2z_path', '')
        mappings_by_section[section].append(mapping)

    # Create tasks for each section
    for entry in index_entries:
        if 'sub' in entry['id']:  # Skip subsections for now
            continue

        section_title = entry['title']
        step_number = entry['step_number']

        # Find related problems
        section_key = None
        for key in mappings_by_section.keys():
            if key.lower().replace(' ', '').replace('-', '') in section_title.lower().replace(' ', '').replace('-', ''):
                section_key = key
                break

        if not section_key:
            # Try to match by step number pattern
            for key in mappings_by_section.keys():
                if f"step {step_number:02d}" in key.lower() or f"step{step_number:02d}" in key.lower():
                    section_key = key
                    break

        related_mappings = mappings_by_section.get(section_key, [])

        # Filter to problems with Python solutions for practice
        python_problems = [m for m in related_mappings if m.get('python_file_path')]

        if not python_problems:
            continue

        # Determine difficulty
        difficulty = estimate_difficulty_from_section(section_title)

        # Split problems into chunks for daily tasks
        chunk_size = min(5, max(1, len(python_problems) // 3))  # 1-5 problems per task
        problem_chunks = [python_problems[i:i + chunk_size] for i in range(0, len(python_problems), chunk_size)]

        for i, chunk in enumerate(problem_chunks):
            task_id = f"{entry['id']}_task_{i+1}"

            # Determine task type based on position
            if i == 0:
                task_type = "new_topic"
                priority = "high"
            elif i < len(problem_chunks) - 1:
                task_type = "practice"
                priority = "medium"
            else:
                task_type = "review"
                priority = "medium"

            # Calculate estimated time
            time_per_problem = estimate_time_per_problem(difficulty, task_type)
            total_time = time_per_problem * len(chunk)

            # Collect problem info
            problem_titles = [p.get('title', 'Unknown') for p in chunk]
            files = []
            for p in chunk:
                if p.get('python_file_path'):
                    files.append(p['python_file_path'])
                if p.get('cpp_file_path'):
                    files.append(p['cpp_file_path'])

            task = StudyTask(
                id=task_id,
                title=f"{section_title} - Part {i+1}",
                type=task_type,
                section=section_title,
                problems=problem_titles,
                estimated_time=total_time,
                priority=priority,
                files=files,
                notes=f"{len(chunk)} problems, {difficulty} difficulty",
                difficulty=difficulty
            )
            tasks.append(task)

    return tasks

def generate_2_week_plan(tasks: List[StudyTask], max_daily_hours: float = 2.0) -> Dict[str, List[StudyTask]]:
    """Generate a 2-week study plan with daily tasks"""
    max_daily_minutes = int(max_daily_hours * 60)

    # Sort tasks by priority and difficulty
    priority_order = {"high": 3, "medium": 2, "low": 1}
    difficulty_order = {"easy": 1, "medium": 2, "hard": 3}

    sorted_tasks = sorted(tasks, key=lambda t: (
        -priority_order.get(t.priority, 0),  # Higher priority first
        difficulty_order.get(t.difficulty, 2),  # Easier first within same priority
        t.estimated_time  # Shorter tasks first
    ))

    # Generate 14 days of plans
    study_plan = {}
    start_date = datetime.now()

    # Keep track of when topics were last reviewed for spaced repetition
    topic_last_seen = {}
    review_tasks = []

    task_index = 0
    for day in range(14):
        current_date = start_date + timedelta(days=day)
        date_key = current_date.strftime("%Y-%m-%d")
        day_name = current_date.strftime("%A")

        daily_tasks = []
        daily_time = 0

        # Add review tasks (spaced repetition) - 30% of time
        review_time_budget = max_daily_minutes * 0.3
        while review_tasks and daily_time + review_tasks[0].estimated_time <= review_time_budget:
            review_task = review_tasks.pop(0)
            # Convert to review task
            review_task.type = "review"
            review_task.estimated_time = int(review_task.estimated_time * 0.7)  # Reviews take less time
            review_task.title += " (Review)"
            daily_tasks.append(review_task)
            daily_time += review_task.estimated_time

        # Add new tasks - remaining time
        while task_index < len(sorted_tasks) and daily_time < max_daily_minutes:
            task = sorted_tasks[task_index]

            if daily_time + task.estimated_time <= max_daily_minutes:
                daily_tasks.append(task)
                daily_time += task.estimated_time

                # Schedule this task for review in 3-7 days (spaced repetition)
                if task.type == "new_topic":
                    review_date = day + random.randint(3, 7)
                    if review_date < 14:
                        # Create a review task
                        review_task = StudyTask(
                            id=task.id + "_review",
                            title=task.title,
                            type="review",
                            section=task.section,
                            problems=task.problems[:2],  # Review fewer problems
                            estimated_time=int(task.estimated_time * 0.5),
                            priority="low",
                            files=task.files,
                            notes=f"Review of {task.section}",
                            difficulty=task.difficulty
                        )
                        review_tasks.append(review_task)

                task_index += 1
            else:
                break

        study_plan[f"{date_key} ({day_name})"] = daily_tasks

    return study_plan

def print_study_plan(study_plan: Dict[str, List[StudyTask]]):
    """Print formatted study plan"""
    print("📅 14-Day A2Z DSA Study Plan")
    print("=" * 60)

    total_time = 0
    total_tasks = 0

    for date, tasks in study_plan.items():
        daily_time = sum(task.estimated_time for task in tasks)
        total_time += daily_time
        total_tasks += len(tasks)

        print(f"\n📍 {date}")
        print(f"   Total time: {daily_time//60}h {daily_time%60}m | Tasks: {len(tasks)}")

        for i, task in enumerate(tasks, 1):
            type_icon = {"new_topic": "🆕", "review": "🔄", "practice": "💪"}.get(task.type, "📝")
            priority_icon = {"high": "🔥", "medium": "⭐", "low": "📝"}.get(task.priority, "")

            print(f"   {i}. {type_icon} {task.title} {priority_icon}")
            print(f"      Time: {task.estimated_time}min | Problems: {len(task.problems)} | Difficulty: {task.difficulty}")

            if len(task.problems) <= 3:
                print(f"      Problems: {', '.join(task.problems)}")
            else:
                print(f"      Problems: {', '.join(task.problems[:3])}, +{len(task.problems)-3} more")

            if task.files:
                local_files = [f for f in task.files if 'striver-a2z-dsa' in f][:2]
                if local_files:
                    print(f"      Files: {', '.join([Path(f).name for f in local_files])}")

    print(f"\n📊 Plan Summary:")
    print(f"Total study time: {total_time//60}h {total_time%60}m")
    print(f"Average per day: {total_time//14//60}h {(total_time//14)%60}m")
    print(f"Total tasks: {total_tasks}")
    print(f"Average tasks per day: {total_tasks/14:.1f}")

def main():
    """Main study plan generation function"""
    print("📚 Generating A2Z DSA Study Plan...")

    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data"

    try:
        # Load data
        index_entries = load_jsonl(data_dir / "index.jsonl")
        mapping_entries = load_jsonl(data_dir / "mapping.jsonl")

        # Create study tasks
        print("🎯 Creating study tasks...")
        tasks = create_study_tasks_from_data(index_entries, mapping_entries)

        # Generate 2-week plan
        print("📅 Generating 14-day schedule...")
        study_plan = generate_2_week_plan(tasks, max_daily_hours=2.0)

        # Print plan
        print_study_plan(study_plan)

        # Save plan to file
        plan_file = data_dir / "study_plan_14day.json"
        with open(plan_file, 'w') as f:
            # Convert to JSON-serializable format
            json_plan = {}
            for date, tasks in study_plan.items():
                json_plan[date] = [
                    {
                        'id': task.id,
                        'title': task.title,
                        'type': task.type,
                        'section': task.section,
                        'problems': task.problems,
                        'estimated_time': task.estimated_time,
                        'priority': task.priority,
                        'files': task.files,
                        'notes': task.notes,
                        'difficulty': task.difficulty
                    }
                    for task in tasks
                ]
            json.dump(json_plan, f, indent=2)

        print(f"\n💾 Study plan saved to: {plan_file}")
        return 0

    except Exception as e:
        print(f"❌ Error generating study plan: {e}")
        return 1

if __name__ == "__main__":
    exit(main())