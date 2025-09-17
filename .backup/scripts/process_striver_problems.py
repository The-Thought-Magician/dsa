#!/usr/bin/env python3
"""
Data Processing Script for Striver A2Z DSA Problems

This script processes the Striver A2Z DSA repository to extract:
- Problem metadata and classifications
- Pattern mappings
- Difficulty levels
- Solution code and analysis
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import ast


@dataclass
class Problem:
    """Data structure for a DSA problem"""
    id: str
    title: str
    file_path: str
    category: str
    step: str
    difficulty: str
    patterns: List[str]
    concepts: List[str]
    solution_code: str
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    description: Optional[str] = None
    hints: List[str] = None

    def __post_init__(self):
        if self.hints is None:
            self.hints = []


class StriverProblemProcessor:
    """Process Striver A2Z DSA problems into structured format"""

    def __init__(self, striver_repo_path: str, output_dir: str):
        self.striver_path = Path(striver_repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Pattern mappings based on problem categories and common patterns
        self.pattern_mappings = {
            "Step 03 - Arrays": ["Array", "Two Pointers", "Sorting"],
            "Step 04 - Binary Search": ["Binary Search", "Search"],
            "Step 05 + 18 - Strings": ["String", "Two Pointers", "Sliding Window"],
            "Step 06 - Linked List": ["Linked List", "Two Pointers"],
            "Step 07 - Recursion": ["Recursion", "Backtracking"],
            "Step 08 - Bit Manipulation": ["Bit Manipulation"],
            "Step 09 - Stacks Queues": ["Stack", "Queue", "Monotonic Stack"],
            "Step 10 - Sliding Window": ["Sliding Window", "Two Pointers"],
            "Step 11 - Heaps": ["Heap", "Priority Queue"],
            "Step 12 - Greedy Algorithm": ["Greedy", "Sorting"],
            "Step 13 + 14 - Trees + BST": ["Tree", "Binary Tree", "BST", "DFS", "BFS"],
            "Step 15 - Graphs": ["Graph", "DFS", "BFS", "Union Find"],
            "Step 16 - Dynamic Programming": ["Dynamic Programming", "Optimization"],
            "Step 17 - Tries": ["Trie", "String"],
        }

        # Difficulty mappings based on problem names and patterns
        self.difficulty_keywords = {
            "easy": ["basic", "simple", "count", "check", "find"],
            "medium": ["longest", "maximum", "minimum", "optimal"],
            "hard": ["all", "combination", "permutation", "complex", "advanced"]
        }

    def extract_problem_info(self, file_path: Path) -> Problem:
        """Extract problem information from a Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract basic info
        filename = file_path.stem
        category = file_path.parent.name

        # Clean up title
        title = filename.replace('-', ' ').replace('_', ' ').title()

        # Generate unique ID
        problem_id = f"{category.lower().replace(' ', '_')}_{filename.lower()}"

        # Determine step
        step = category

        # Get patterns for this category
        patterns = self.pattern_mappings.get(category, ["General"])

        # Determine difficulty
        difficulty = self._determine_difficulty(filename, content)

        # Extract concepts
        concepts = self._extract_concepts(content, filename)

        # Extract complexity from comments if available
        time_complexity, space_complexity = self._extract_complexity(content)

        # Extract description from comments
        description = self._extract_description(content)

        return Problem(
            id=problem_id,
            title=title,
            file_path=str(file_path.relative_to(self.striver_path)),
            category=category,
            step=step,
            difficulty=difficulty,
            patterns=patterns,
            concepts=concepts,
            solution_code=content,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            description=description,
            hints=self._generate_hints(filename, patterns)
        )

    def _determine_difficulty(self, filename: str, content: str) -> str:
        """Determine problem difficulty based on filename and content"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Check for explicit difficulty mentions
        if any(word in content_lower for word in ["hard", "difficult", "complex"]):
            return "Hard"
        if any(word in content_lower for word in ["medium", "moderate"]):
            return "Medium"
        if any(word in content_lower for word in ["easy", "simple", "basic"]):
            return "Easy"

        # Pattern-based difficulty
        hard_patterns = ["permutation", "combination", "backtrack", "dp", "graph"]
        medium_patterns = ["binary", "tree", "heap", "sliding", "two-pointer"]
        easy_patterns = ["array", "string", "math", "basic"]

        if any(pattern in filename_lower for pattern in hard_patterns):
            return "Hard"
        elif any(pattern in filename_lower for pattern in medium_patterns):
            return "Medium"
        else:
            return "Easy"

    def _extract_concepts(self, content: str, filename: str) -> List[str]:
        """Extract key programming concepts from the solution"""
        concepts = []

        # Analyze imports and function usage
        if "from collections import" in content or "import collections" in content:
            concepts.append("Collections")
        if "heapq" in content:
            concepts.append("Heap")
        if "bisect" in content:
            concepts.append("Binary Search")
        if "itertools" in content:
            concepts.append("Itertools")

        # Analyze code patterns
        if "def dfs" in content or "def bfs" in content:
            concepts.extend(["Graph Traversal", "Recursion"])
        if "dp[" in content or "memo" in content:
            concepts.append("Dynamic Programming")
        if "left" in content and "right" in content:
            concepts.append("Two Pointers")
        if "stack" in content.lower():
            concepts.append("Stack")
        if "queue" in content.lower():
            concepts.append("Queue")

        return list(set(concepts)) if concepts else ["Implementation"]

    def _extract_complexity(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract time and space complexity from comments"""
        time_complexity = None
        space_complexity = None

        # Look for complexity comments
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'time complexity' in line_lower or 'tc:' in line_lower:
                # Extract O(...) pattern
                match = re.search(r'O\([^)]+\)', line)
                if match:
                    time_complexity = match.group()
            elif 'space complexity' in line_lower or 'sc:' in line_lower:
                match = re.search(r'O\([^)]+\)', line)
                if match:
                    space_complexity = match.group()

        return time_complexity, space_complexity

    def _extract_description(self, content: str) -> Optional[str]:
        """Extract problem description from comments"""
        lines = content.split('\n')
        description_lines = []
        in_description = False

        for line in lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''"):
                if in_description:
                    break
                in_description = True
                continue
            elif line.startswith('#') and not in_description:
                description_lines.append(line[1:].strip())
            elif in_description:
                description_lines.append(line)

        return ' '.join(description_lines).strip() if description_lines else None

    def _generate_hints(self, filename: str, patterns: List[str]) -> List[str]:
        """Generate helpful hints based on problem type and patterns"""
        hints = []

        filename_lower = filename.lower()

        # Pattern-specific hints
        if "Two Pointers" in patterns:
            hints.append("Consider using two pointers technique")
        if "Binary Search" in patterns:
            hints.append("Think about binary search on the answer")
        if "Sliding Window" in patterns:
            hints.append("Can you solve this with a sliding window approach?")
        if "Dynamic Programming" in patterns:
            hints.append("Look for overlapping subproblems")
        if "Graph" in patterns:
            hints.append("Consider DFS or BFS traversal")

        # Problem-specific hints
        if "sort" in filename_lower:
            hints.append("Think about different sorting algorithms and their properties")
        if "merge" in filename_lower:
            hints.append("Consider the merge operation in merge sort")
        if "palindrome" in filename_lower:
            hints.append("Palindromes read the same forwards and backwards")

        return hints[:3]  # Limit to 3 hints

    def process_all_problems(self) -> List[Problem]:
        """Process all Python files in the Striver repository"""
        problems = []

        # Find all Python files
        for python_file in self.striver_path.rglob("*.py"):
            if python_file.name == "__init__.py":
                continue

            try:
                problem = self.extract_problem_info(python_file)
                problems.append(problem)
                print(f"Processed: {problem.title}")
            except Exception as e:
                print(f"Error processing {python_file}: {e}")

        return problems

    def save_problems_database(self, problems: List[Problem]):
        """Save problems to JSON database"""
        problems_data = [asdict(problem) for problem in problems]

        # Save main database
        with open(self.output_dir / "problems_database.json", 'w') as f:
            json.dump(problems_data, f, indent=2)

        # Create category index
        categories = {}
        for problem in problems:
            if problem.category not in categories:
                categories[problem.category] = []
            categories[problem.category].append(problem.id)

        with open(self.output_dir / "categories_index.json", 'w') as f:
            json.dump(categories, f, indent=2)

        # Create patterns index
        patterns_index = {}
        for problem in problems:
            for pattern in problem.patterns:
                if pattern not in patterns_index:
                    patterns_index[pattern] = []
                patterns_index[pattern].append(problem.id)

        with open(self.output_dir / "patterns_index.json", 'w') as f:
            json.dump(patterns_index, f, indent=2)

        # Create difficulty index
        difficulty_index = {"Easy": [], "Medium": [], "Hard": []}
        for problem in problems:
            difficulty_index[problem.difficulty].append(problem.id)

        with open(self.output_dir / "difficulty_index.json", 'w') as f:
            json.dump(difficulty_index, f, indent=2)

        print(f"Saved {len(problems)} problems to database")
        print(f"Categories: {len(categories)}")
        print(f"Patterns: {len(patterns_index)}")
        print(f"Difficulty distribution: {[(k, len(v)) for k, v in difficulty_index.items()]}")


def main():
    """Main function to process Striver problems"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    striver_repo_path = project_root / "striver-a2z-dsa"
    output_dir = project_root / "data"

    if not striver_repo_path.exists():
        print(f"Error: Striver repository not found at {striver_repo_path}")
        return

    processor = StriverProblemProcessor(str(striver_repo_path), str(output_dir))

    print("Processing Striver A2Z DSA problems...")
    problems = processor.process_all_problems()

    print("Saving to database...")
    processor.save_problems_database(problems)

    print("Done! Check the 'data' directory for processed files.")


if __name__ == "__main__":
    main()