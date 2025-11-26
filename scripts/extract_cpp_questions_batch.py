"""Extract questions from C++ repository in batches to manage API limits."""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import os

class CPPQuestionExtractor:
    def __init__(self):
        self.cpp_repo_path = Path("Strivers-A2Z-DSA-Sheet")
        self.output_path = Path("data/questions")

    def extract_cpp_content(self, file_path: Path) -> Optional[Dict]:
        """Extract structured content from a C++ file."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract question section - more flexible patterns
            question_match = re.search(r'/\*\s*QUEST?ION[:\-]?\s*\n?(.*?)(?=\*/|APPROACH|CODE)', content, re.DOTALL | re.IGNORECASE)
            if not question_match:
                # Try without comment blocks
                question_match = re.search(r'QUEST?ION[:\-]?\s*\n?(.*?)(?=APPROACH|CODE|Example)', content, re.DOTALL | re.IGNORECASE)

            # Extract approach section
            approach_match = re.search(r'APPROACH[:\-]?\s*\n?(.*?)(?=CODE|TIME|SPACE|COMPLEXITY|\*/)', content, re.DOTALL | re.IGNORECASE)

            # Extract code section - more flexible
            code_match = re.search(r'(?:CODE[:\-]?\s*\*/\s*|//\s*CODE[:\-]?\s*\n)(.*?)(?=/\*|//\s*TIME|//\s*SPACE|$)', content, re.DOTALL)
            if not code_match:
                # Try to extract everything after code marker
                code_match = re.search(r'(?://\s*)?CODE[:\-]?\s*\n?(.*)', content, re.DOTALL | re.IGNORECASE)

            # Extract complexity information
            time_complexity = None
            space_complexity = None

            time_match = re.search(r'TIME COMPLEXITY[:\-=]?\s*([^\n]*)', content, re.IGNORECASE)
            if time_match:
                time_complexity = time_match.group(1).strip()

            space_match = re.search(r'SPACE COMPLEXITY[:\-=]?\s*([^\n]*)', content, re.IGNORECASE)
            if space_match:
                space_complexity = space_match.group(1).strip()

            if not question_match:
                return None

            question_text = question_match.group(1).strip()
            approach_text = approach_match.group(1).strip() if approach_match else ""
            code_text = code_match.group(1).strip() if code_match else ""

            # Clean up extracted text
            question_text = re.sub(r'\s+', ' ', question_text).strip()
            approach_text = re.sub(r'\s+', ' ', approach_text).strip()

            return {
                "file_path": file_path.as_posix(),
                "title": self._extract_title_from_path(file_path),
                "question": question_text,
                "approach": approach_text,
                "cpp_code": code_text,
                "time_complexity": time_complexity,
                "space_complexity": space_complexity,
                "difficulty": self._determine_difficulty(file_path),
                "tags": self._extract_tags_from_path(file_path)
            }

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def _extract_title_from_path(self, file_path: Path) -> str:
        """Extract a clean title from the file path."""
        filename = file_path.stem
        # Remove numbers and clean up
        title = re.sub(r'^\d+\.\s*', '', filename)
        title = re.sub(r'_', ' ', title)
        return title.title()

    def _determine_difficulty(self, file_path: Path) -> str:
        """Determine difficulty from path structure."""
        path_str = str(file_path).lower()
        if 'easy' in path_str:
            return "Easy"
        elif 'medium' in path_str:
            return "Medium"
        elif 'hard' in path_str:
            return "Hard"
        else:
            return "Medium"  # Default

    def _extract_tags_from_path(self, file_path: Path) -> List[str]:
        """Extract tags from the directory structure."""
        parts = file_path.parts
        tags = []

        for part in parts:
            if 'arrays' in part.lower():
                tags.append('array')
            elif 'heap' in part.lower():
                tags.append('heap')
            elif 'tree' in part.lower():
                tags.append('tree')
            elif 'graph' in part.lower():
                tags.append('graph')
            elif 'string' in part.lower():
                tags.append('string')
            elif 'dp' in part.lower() or 'dynamic' in part.lower():
                tags.append('dynamic-programming')
            elif 'greedy' in part.lower():
                tags.append('greedy')
            elif 'recursion' in part.lower():
                tags.append('recursion')
            elif 'bit' in part.lower():
                tags.append('bit-manipulation')
            elif 'stack' in part.lower() or 'queue' in part.lower():
                tags.append('stack')
            elif 'linked' in part.lower():
                tags.append('linked-list')
            elif 'binary' in part.lower():
                tags.append('binary-search')
            elif 'sliding' in part.lower():
                tags.append('sliding-window')
            elif 'trie' in part.lower():
                tags.append('trie')

        return tags if tags else ['general']

    def create_basic_question_object(self, question_data: Dict) -> Dict:
        """Create a basic question object without AI generation."""
        # Generate ID from title
        question_id = re.sub(r'[^a-z0-9]+', '-', question_data['title'].lower()).strip('-')

        # Create basic starter code template
        starter_code = """def solve():
    # TODO: Implement your solution
    pass

if __name__ == "__main__":
    solve()"""

        # Create basic test case
        basic_test = [{
            "id": 1,
            "input": "# Input will be provided",
            "output": "# Expected output",
            "explanation": "Basic test case"
        }]

        return {
            "id": question_id,
            "title": question_data['title'],
            "difficulty": question_data['difficulty'],
            "tags": question_data['tags'],
            "statement_markdown": f"{question_data['question']}\n\n**Approach:** {question_data['approach']}",
            "starter_code": starter_code,
            "sample_tests": basic_test,
            "resources": [
                {
                    "title": f"Original C++ Solution",
                    "url": f"file://{question_data['file_path']}",
                    "notes": "Original implementation"
                }
            ],
            "metadata": {
                "time_complexity": question_data.get('time_complexity', 'O(n)'),
                "space_complexity": question_data.get('space_complexity', 'O(1)'),
                "source_file": question_data['file_path'],
                "needs_ai_generation": True
            },
            "solution_markdown": f"```cpp\n{question_data['cpp_code']}\n```"
        }

    def extract_all_questions(self) -> List[Dict]:
        """Extract all questions from the C++ repository."""
        cpp_files = list(self.cpp_repo_path.rglob("*.cpp"))
        questions = []

        print(f"Found {len(cpp_files)} C++ files")

        for i, cpp_file in enumerate(cpp_files):
            print(f"Processing ({i+1}/{len(cpp_files)}): {cpp_file.name}")

            question_data = self.extract_cpp_content(cpp_file)
            if question_data and question_data['question']:
                question_obj = self.create_basic_question_object(question_data)
                questions.append(question_obj)
            else:
                print(f"  - Skipped (no question found)")

        print(f"Successfully extracted {len(questions)} questions")
        return questions

    def save_questions(self, questions: List[Dict]):
        """Save questions to JSON file."""
        self.output_path.mkdir(parents=True, exist_ok=True)
        output_file = self.output_path / "questions.json"

        dataset = {"questions": questions}

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(questions)} questions to {output_file}")

def main():
    extractor = CPPQuestionExtractor()
    questions = extractor.extract_all_questions()
    extractor.save_questions(questions)
    print(f"Question extraction complete! Generated {len(questions)} questions.")
    print("Note: Questions are marked for AI generation. Run the AI enhancement script separately.")

if __name__ == "__main__":
    main()
