#!/usr/bin/env python3
"""
Analyze both local repositories to understand structure and content.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict

@dataclass
class PythonSolution:
    """Represents a Python solution file"""
    file_path: str
    step_section: str
    file_name: str
    problem_name: str

@dataclass
class CppSolution:
    """Represents a C++ solution with metadata"""
    file_path: str
    section: str
    subsection: str
    file_name: str
    problem_title: str
    question: Optional[str] = None
    approach: Optional[str] = None
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None

def extract_cpp_metadata(file_path: str) -> CppSolution:
    """Extract metadata from C++ files with embedded comments"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Parse file path for structure
        parts = Path(file_path).parts
        section = parts[-3] if len(parts) >= 3 else ""
        subsection = parts[-2] if len(parts) >= 2 else ""
        file_name = parts[-1]

        # Extract problem title from filename
        problem_title = re.sub(r'^\d+\.', '', file_name.replace('.cpp', '')).replace('_', ' ').title()

        # Extract embedded metadata
        question = None
        approach = None
        time_complexity = None
        space_complexity = None

        # Look for QUESTION section
        question_match = re.search(r'/\*\s*QUESTION:-\s*(.*?)\*/', content, re.DOTALL)
        if question_match:
            question = question_match.group(1).strip()

        # Look for APPROACH section
        approach_match = re.search(r'/\*\s*APPROACH:-\s*(.*?)\*/', content, re.DOTALL)
        if approach_match:
            approach = approach_match.group(1).strip()

        # Look for complexity comments
        time_match = re.search(r'//\s*TIME COMPLEXITY\s*=\s*(.+)', content)
        if time_match:
            time_complexity = time_match.group(1).strip()

        space_match = re.search(r'//\s*SPACE COMPLEXITY\s*=\s*(.+)', content)
        if space_match:
            space_complexity = space_match.group(1).strip()

        return CppSolution(
            file_path=file_path,
            section=section,
            subsection=subsection,
            file_name=file_name,
            problem_title=problem_title,
            question=question,
            approach=approach,
            time_complexity=time_complexity,
            space_complexity=space_complexity
        )
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return CppSolution(
            file_path=file_path,
            section="",
            subsection="",
            file_name=os.path.basename(file_path),
            problem_title=os.path.basename(file_path).replace('.cpp', '')
        )

def analyze_python_repo(repo_path: str) -> List[PythonSolution]:
    """Analyze Python repository structure"""
    solutions = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # Extract step section from path
                rel_path = os.path.relpath(file_path, repo_path)
                step_section = rel_path.split(os.sep)[0] if os.sep in rel_path else "Unknown"

                # Clean up problem name
                problem_name = file.replace('.py', '').replace('-', ' ').replace('_', ' ').title()

                solutions.append(PythonSolution(
                    file_path=file_path,
                    step_section=step_section,
                    file_name=file,
                    problem_name=problem_name
                ))

    return solutions

def analyze_cpp_repo(repo_path: str) -> List[CppSolution]:
    """Analyze C++ repository structure and extract metadata"""
    solutions = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.cpp'):
                file_path = os.path.join(root, file)
                solution = extract_cpp_metadata(file_path)
                solutions.append(solution)

    return solutions

def main():
    """Main analysis function"""
    base_path = Path(__file__).parent.parent

    # Analyze both repositories
    print("🔍 Analyzing Python solutions...")
    python_solutions = analyze_python_repo(str(base_path / "striver-a2z-dsa"))

    print("🔍 Analyzing C++ solutions...")
    cpp_solutions = analyze_cpp_repo(str(base_path / "Strivers-A2Z-DSA-Sheet"))

    # Generate reports
    print(f"\n📊 Analysis Results:")
    print(f"Python solutions: {len(python_solutions)}")
    print(f"C++ solutions: {len(cpp_solutions)}")

    # Save raw data
    data_dir = base_path / "data"
    data_dir.mkdir(exist_ok=True)

    with open(data_dir / "python_analysis.json", 'w') as f:
        json.dump([asdict(sol) for sol in python_solutions], f, indent=2)

    with open(data_dir / "cpp_analysis.json", 'w') as f:
        json.dump([asdict(sol) for sol in cpp_solutions], f, indent=2)

    # Print section breakdown
    print(f"\n📂 Python sections:")
    python_sections = {}
    for sol in python_solutions:
        python_sections[sol.step_section] = python_sections.get(sol.step_section, 0) + 1

    for section, count in sorted(python_sections.items()):
        print(f"  {section}: {count} files")

    print(f"\n📂 C++ sections:")
    cpp_sections = {}
    for sol in cpp_solutions:
        section_key = f"{sol.section}/{sol.subsection}"
        cpp_sections[section_key] = cpp_sections.get(section_key, 0) + 1

    for section, count in sorted(cpp_sections.items()):
        print(f"  {section}: {count} files")

    print(f"\n✅ Analysis complete! Data saved to data/ directory.")

if __name__ == "__main__":
    main()