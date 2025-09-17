#!/usr/bin/env python3
"""
Main CLI for A2Z DSA Learning System

A comprehensive learning system for Striver's A2Z DSA course with Python focus.
"""

import typer
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

app = typer.Typer(help="A2Z DSA Learning System - Master data structures and algorithms systematically")
console = Console()

def load_jsonl(file_path: Path) -> list:
    """Load JSONL file"""
    entries = []
    if file_path.exists():
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
    return entries

@app.command("list")
def list_topics(
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Filter by section name"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by status (available/partial/missing)")
):
    """List all A2Z DSA topics and their status"""

    data_dir = Path("data")
    index_entries = load_jsonl(data_dir / "index.jsonl")

    if not index_entries:
        console.print("❌ No index data found. Run 'python scripts/build_index.py' first.", style="red")
        return

    # Filter entries
    filtered = index_entries
    if section:
        filtered = [e for e in filtered if section.lower() in e['title'].lower()]
    if status:
        filtered = [e for e in filtered if e['status'] == status]

    if not filtered:
        console.print("No topics match the filters.", style="yellow")
        return

    # Create table
    table = Table(title="A2Z DSA Topics")
    table.add_column("Step", style="cyan", width=4)
    table.add_column("Topic", style="white", width=40)
    table.add_column("Status", width=12)
    table.add_column("Problems", justify="right", width=8)
    table.add_column("Files", justify="right", width=6)

    for entry in filtered:
        if 'sub' in entry['id']:  # Skip subsections for main view
            continue

        status_style = "green" if entry['status'] == "available" else "yellow" if entry['status'] == "partial" else "red"
        status_icon = "✅" if entry['status'] == "available" else "⚠️" if entry['status'] == "partial" else "❌"

        table.add_row(
            str(entry['step_number']),
            entry['title'],
            f"{status_icon} {entry['status']}",
            str(len(entry['related_problems'])),
            str(len(entry['local_files']))
        )

    console.print(table)

@app.command("gaps")
def show_gaps():
    """Show coverage gaps and missing implementations"""

    try:
        import subprocess
        result = subprocess.run(['python', 'scripts/coverage_checker.py'],
                              capture_output=True, text=True, cwd='.')
        console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="red")
    except Exception as e:
        console.print(f"❌ Error running coverage check: {e}", style="red")

@app.command("plan")
def show_plan():
    """Generate and display today's study plan"""

    data_dir = Path("data")
    plan_file = data_dir / "study_plan_14day.json"

    if not plan_file.exists():
        console.print("📅 Generating new study plan...", style="blue")
        try:
            import subprocess
            subprocess.run(['python', 'scripts/study_plan_generator.py'], check=True, cwd='.')
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Error generating study plan: {e}", style="red")
            return

    # Load and display plan
    with open(plan_file) as f:
        plan_data = json.load(f)

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    # Find today's plan
    today_tasks = None
    today_key = None
    for date_key, tasks in plan_data.items():
        if today in date_key:
            today_tasks = tasks
            today_key = date_key
            break

    if not today_tasks:
        console.print("📅 No tasks scheduled for today. Check the 14-day plan:", style="yellow")
        console.print(f"Available dates: {list(plan_data.keys())[:5]}")
        return

    console.print(Panel.fit(f"📅 Today's A2Z DSA Plan: {today_key}", style="blue"))

    total_time = sum(task['estimated_time'] for task in today_tasks)
    console.print(f"⏱️  Total time: {total_time//60}h {total_time%60}m | Tasks: {len(today_tasks)}")

    for i, task in enumerate(today_tasks, 1):
        type_icon = {"new_topic": "🆕", "review": "🔄", "practice": "💪"}.get(task['type'], "📝")
        priority_icon = {"high": "🔥", "medium": "⭐", "low": "📝"}.get(task['priority'], "")

        console.print(f"\n{i}. {type_icon} {task['title']} {priority_icon}")
        console.print(f"   ⏱️  {task['estimated_time']}min | 🎯 {len(task['problems'])} problems | 📊 {task['difficulty']}")

        if len(task['problems']) <= 3:
            console.print(f"   📝 {', '.join(task['problems'])}")
        else:
            console.print(f"   📝 {', '.join(task['problems'][:3])}, +{len(task['problems'])-3} more")

@app.command("init")
def initialize():
    """Initialize the learning system by building all data files"""

    console.print("🚀 Initializing A2Z DSA Learning System...", style="blue")

    scripts = [
        ("analyze_repos.py", "Analyzing repositories"),
        ("build_a2z_structure.py", "Building A2Z structure"),
        ("build_index.py", "Creating index and mappings"),
        ("coverage_checker.py", "Checking coverage")
    ]

    import subprocess

    for script, description in scripts:
        console.print(f"📊 {description}...")
        try:
            result = subprocess.run(['python', f'scripts/{script}'],
                                  check=True, capture_output=True, text=True, cwd='.')
            console.print(f"✅ {description} complete")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Error in {script}: {e.stderr}", style="red")
            return

    console.print("\n🎉 Initialization complete! Try these commands:")
    console.print("  • python main.py list - View all topics")
    console.print("  • python main.py gaps - Check coverage")
    console.print("  • python main.py plan - Get today's study plan")

@app.command("stats")
def show_stats():
    """Show learning progress statistics"""

    data_dir = Path("data")
    index_entries = load_jsonl(data_dir / "index.jsonl")
    mapping_entries = load_jsonl(data_dir / "mapping.jsonl")

    if not index_entries or not mapping_entries:
        console.print("❌ No data found. Run 'python main.py init' first.", style="red")
        return

    # Calculate stats
    total_sections = len([e for e in index_entries if 'sub' not in e['id']])
    total_problems = len(mapping_entries)

    python_solutions = len([m for m in mapping_entries if m.get('python_file_path')])
    cpp_solutions = len([m for m in mapping_entries if m.get('cpp_file_path')])

    exact_matches = len([m for m in mapping_entries if m.get('status') == 'exact-match'])
    approx_matches = len([m for m in mapping_entries if m.get('status') == 'approx'])

    coverage = (python_solutions + cpp_solutions) / (total_problems * 2) * 100 if total_problems > 0 else 0

    # Display stats table
    stats_table = Table(title="📊 A2Z DSA Learning Progress")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", justify="right", style="white")
    stats_table.add_column("Progress", style="green")

    stats_table.add_row("Total Sections", str(total_sections), "📚")
    stats_table.add_row("Total Problems", str(total_problems), "🎯")
    stats_table.add_row("Python Solutions", str(python_solutions), f"{python_solutions/total_problems*100:.1f}%" if total_problems > 0 else "0%")
    stats_table.add_row("C++ Solutions", str(cpp_solutions), f"{cpp_solutions/total_problems*100:.1f}%" if total_problems > 0 else "0%")
    stats_table.add_row("Overall Coverage", f"{coverage:.1f}%", "✅" if coverage >= 80 else "⚠️")
    stats_table.add_row("Exact Matches", str(exact_matches), "🎯")
    stats_table.add_row("Approx Matches", str(approx_matches), "🔍")

    console.print(stats_table)

if __name__ == "__main__":
    app()
