#!/usr/bin/env python3
"""
Quick Start Script for DSA Learning System

This script provides easy commands to manage the learning system.
"""

import subprocess
import sys
import os
from pathlib import Path


def activate_venv():
    """Activate virtual environment"""
    venv_path = Path("learning-env/bin/activate")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Run setup first.")
        return False
    return True


def start_backend():
    """Start the backend API server"""
    print("🚀 Starting DSA Learning System Backend...")
    if not activate_venv():
        return

    try:
        # Change to project directory
        os.chdir(Path(__file__).parent)

        # Start the backend
        subprocess.run([
            "bash", "-c",
            "source learning-env/bin/activate && python -m backend.main"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")


def run_demo():
    """Run the demo script"""
    print("🎯 Running DSA Learning System Demo...")
    if not activate_venv():
        return

    try:
        subprocess.run([
            "bash", "-c",
            "source learning-env/bin/activate && python demo.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running demo: {e}")


def process_problems():
    """Process Striver problems"""
    print("📊 Processing Striver A2Z DSA problems...")
    if not activate_venv():
        return

    try:
        subprocess.run([
            "bash", "-c",
            "source learning-env/bin/activate && python scripts/process_striver_problems.py"
        ], check=True)
        print("✅ Problems processed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error processing problems: {e}")


def show_stats():
    """Show system statistics"""
    print("📊 DSA Learning System Statistics")
    print("=" * 40)

    # Check if data exists
    data_path = Path("data/problems_database.json")
    if not data_path.exists():
        print("❌ No data found. Run 'python start.py process' first.")
        return

    import json
    with open(data_path, 'r') as f:
        problems = json.load(f)

    categories = {}
    patterns = {}
    difficulties = {"Easy": 0, "Medium": 0, "Hard": 0}

    for problem in problems:
        cat = problem['category']
        categories[cat] = categories.get(cat, 0) + 1

        for pattern in problem['patterns']:
            patterns[pattern] = patterns.get(pattern, 0) + 1

        difficulties[problem['difficulty']] += 1

    print(f"📚 Total Problems: {len(problems)}")
    print(f"📁 Categories: {len(categories)}")
    print(f"🔍 Patterns: {len(patterns)}")
    print()
    print("💡 Difficulty Distribution:")
    for diff, count in difficulties.items():
        percentage = (count / len(problems)) * 100
        print(f"   • {diff}: {count} problems ({percentage:.1f}%)")

    print()
    print("🔥 Top 10 Patterns:")
    top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (pattern, count) in enumerate(top_patterns, 1):
        print(f"   {i:2d}. {pattern}: {count} problems")


def show_help():
    """Show help information"""
    print("🎯 DSA Learning System - Quick Start")
    print("=" * 40)
    print()
    print("Available commands:")
    print("  python start.py backend     - Start the backend API server")
    print("  python start.py demo        - Run the demo script")
    print("  python start.py process     - Process Striver problems")
    print("  python start.py stats       - Show system statistics")
    print("  python start.py help        - Show this help")
    print()
    print("🚀 Quick Start Guide:")
    print("  1. python start.py process  (if not done already)")
    print("  2. python start.py backend  (in one terminal)")
    print("  3. python start.py demo     (in another terminal)")
    print()
    print("📖 Documentation:")
    print("  • plan.md     - Learning roadmap and strategy")
    print("  • design.md   - Technical architecture")
    print("  • done.md     - Completed tasks and progress")


def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "backend":
        start_backend()
    elif command == "demo":
        run_demo()
    elif command == "process":
        process_problems()
    elif command == "stats":
        show_stats()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == "__main__":
    main()