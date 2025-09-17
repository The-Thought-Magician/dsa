"""Extract questions from C++ repository and generate dataset with Gemini."""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import google.genai as genai
import os
from google.genai import types

class QuestionExtractor:
    def __init__(self):
        self.cpp_repo_path = Path("Strivers-A2Z-DSA-Sheet")
        self.output_path = Path("data/questions")
        self.client = None
        self._setup_gemini()

    def _setup_gemini(self):
        """Initialize Gemini client with API key from environment."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

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

            question_text = (question_match.group(1) or question_match.group(2) or "").strip()
            approach_text = approach_match.group(1).strip() if approach_match else ""
            code_text = code_match.group(1).strip() if code_match else ""

            # Clean up extracted text
            question_text = re.sub(r'\s+', ' ', question_text).strip()
            approach_text = re.sub(r'\s+', ' ', approach_text).strip()

            return {
                "file_path": str(file_path),
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

    def generate_python_solution(self, question_data: Dict) -> str:
        """Generate Python solution using Gemini."""
        prompt = f"""
Convert the following C++ solution to Python, following these requirements:

**Problem:** {question_data['question']}

**C++ Code:**
```cpp
{question_data['cpp_code']}
```

**Requirements:**
1. Convert to clean, idiomatic Python code
2. Use proper Python naming conventions (snake_case)
3. Add type hints where appropriate
4. Structure as a function that takes input from stdin and prints output
5. Keep the same algorithm and approach
6. Add proper error handling if needed

Return only the Python code, no explanations.
"""

        try:
            # Add rate limiting
            time.sleep(7)  # 7 seconds between calls to stay under 10/minute limit

            response = self.client.models.generate_content(
                model='gemini-1.5-flash',  # Use more stable model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=2000
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Python solution: {e}")
            return f"# Error generating Python solution\n# Original C++ code:\n{question_data['cpp_code']}"

    def generate_test_cases(self, question_data: Dict) -> List[Dict]:
        """Generate test cases using Gemini."""
        prompt = f"""
Generate 3-5 comprehensive test cases for this problem:

**Problem:** {question_data['question']}

**Approach:** {question_data['approach']}

Return the test cases in this exact JSON format:
[
  {{
    "id": 1,
    "input": "input_string_here",
    "output": "expected_output_here",
    "explanation": "brief explanation"
  }}
]

Include edge cases and different scenarios. Make sure inputs and outputs are strings as they would appear in stdin/stdout.
"""

        try:
            # Add rate limiting
            time.sleep(7)  # 7 seconds between calls

            response = self.client.models.generate_content(
                model='gemini-1.5-flash',  # Use more stable model
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    max_output_tokens=1500
                )
            )

            # Extract JSON from response
            response_text = response.text.strip()
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback test case
                return [{
                    "id": 1,
                    "input": "sample input",
                    "output": "sample output",
                    "explanation": "Generated test case"
                }]
        except Exception as e:
            print(f"Error generating test cases: {e}")
            return [{
                "id": 1,
                "input": "sample input",
                "output": "sample output",
                "explanation": "Default test case"
            }]

    def create_question_object(self, question_data: Dict) -> Dict:
        """Create a complete question object."""
        # Generate ID from title
        question_id = re.sub(r'[^a-z0-9]+', '-', question_data['title'].lower()).strip('-')

        # Generate Python solution and test cases
        python_solution = self.generate_python_solution(question_data)
        test_cases = self.generate_test_cases(question_data)

        # Create starter code from Python solution (remove implementation)
        starter_code = self._create_starter_code(python_solution)

        return {
            "id": question_id,
            "title": question_data['title'],
            "difficulty": question_data['difficulty'],
            "tags": question_data['tags'],
            "statement_markdown": question_data['question'],
            "starter_code": starter_code,
            "sample_tests": test_cases,
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
                "source_file": question_data['file_path']
            },
            "solution_markdown": f"```python\n{python_solution}\n```"
        }

    def _create_starter_code(self, python_solution: str) -> str:
        """Create starter code by removing implementation details."""
        lines = python_solution.split('\n')
        starter_lines = []
        in_function = False

        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                starter_lines.append(line)
                in_function = True
            elif 'import ' in line or 'from ' in line:
                starter_lines.append(line)
            elif line.strip() == '' or line.strip().startswith('#'):
                starter_lines.append(line)
            elif 'if __name__' in line:
                starter_lines.append(line)
                starter_lines.append('    # TODO: Implement your solution')
                starter_lines.append('    pass')
                break
            elif in_function and (line.strip() == '' or line.strip().startswith('"""') or line.strip().startswith('Args:') or line.strip().startswith('Returns:')):
                starter_lines.append(line)
            elif in_function and not line.strip().startswith('#'):
                # Replace function body with TODO
                indent = len(line) - len(line.lstrip())
                starter_lines.append(' ' * indent + '# TODO: Implement your solution')
                starter_lines.append(' ' * indent + 'pass')
                in_function = False
            else:
                if not in_function:
                    starter_lines.append(line)

        if not any('TODO' in line for line in starter_lines):
            starter_lines.append('# TODO: Implement your solution')
            starter_lines.append('pass')

        return '\n'.join(starter_lines)

    def extract_all_questions(self) -> List[Dict]:
        """Extract all questions from the C++ repository."""
        cpp_files = list(self.cpp_repo_path.rglob("*.cpp"))
        questions = []

        print(f"Found {len(cpp_files)} C++ files")

        for i, cpp_file in enumerate(cpp_files):
            print(f"Processing ({i+1}/{len(cpp_files)}): {cpp_file.name}")

            question_data = self.extract_cpp_content(cpp_file)
            if question_data and question_data['question']:
                question_obj = self.create_question_object(question_data)
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
    extractor = QuestionExtractor()
    questions = extractor.extract_all_questions()
    extractor.save_questions(questions)
    print(f"Question extraction complete! Generated {len(questions)} questions.")

if __name__ == "__main__":
    main()