"""Generate the question datasets for the Questions workflow."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

def _question_two_sum() -> dict[str, object]:
    return {
        "id": "two-sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "tags": ["array", "hashmap", "two-pointer"],
        "statement_markdown": dedent(
            """
            Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to `target`.

            * Exactly one valid answer exists for each test case.
            * Use 0-based indexing for the result.
            * Print the indices in ascending order separated by a single space.

            **Input**
            ```
            n            # size of the array
            n integers   # the array elements
            target       # integer target
            ```

            **Output**
            ```
            i j
            ```
            such that `nums[i] + nums[j] == target` and `i < j`.
            """
        ).strip(),
        "starter_code": dedent(
            """
            from typing import List


            def solve() -> None:
                n = int(input().strip())
                nums = list(map(int, input().split()))
                target = int(input().strip())

                # TODO: implement your solution
                # Print two indices (0-based) separated by a space, in ascending order.
                print("0 0")


            if __name__ == "__main__":
                solve()
            """
        ).strip(),
        "sample_tests": [
            {
                "id": 1,
                "input": "4\n2 7 11 15\n9\n",
                "output": "0 1\n",
                "explanation": "2 + 7 = 9 => indices 0 and 1"
            },
            {
                "id": 2,
                "input": "5\n3 4 5 8 11\n9\n",
                "output": "1 2\n",
                "explanation": "4 + 5 = 9 => indices 1 and 2"
            }
        ],
        "resources": [
            {
                "title": "Striver A2Z - Two Sum",
                "url": "https://takeuforward.org/data-structure/two-sum-classic-question/",
                "notes": "Hash map approach recommended"
            },
            {
                "title": "LeetCode #1",
                "url": "https://leetcode.com/problems/two-sum/",
                "notes": "Original problem statement"
            }
        ],
        "metadata": {
            "time_complexity": "O(n)",
            "space_complexity": "O(n)"
        },
        "solution_markdown": dedent(
            """
            ```python
            from typing import Dict, List


            def solve() -> None:
                n = int(input().strip())
                nums = list(map(int, input().split()))
                target = int(input().strip())

                seen: Dict[int, int] = {}
                for idx, value in enumerate(nums):
                    remaining = target - value
                    if remaining in seen:
                        i = seen[remaining]
                        j = idx
                        print(f"{min(i, j)} {max(i, j)}")
                        return
                    seen[value] = idx
            ```
            """
        ).strip()
    }

def _question_valid_parentheses() -> dict[str, object]:
    return {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "difficulty": "Medium",
        "tags": ["stack", "string", "simulation"],
        "statement_markdown": dedent(
            """
            Given a string containing only the characters `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.

            A string is valid if:

            * Open brackets must be closed by the same type of brackets.
            * Open brackets must be closed in the correct order.

            Print `YES` if the string is valid, otherwise print `NO`.

            **Input**
            ```
            s  # a string of bracket characters
            ```

            **Output**
            ```
            YES|NO
            ```
            """
        ).strip(),
        "starter_code": dedent(
            """
            def solve() -> None:
                s = input().strip()

                # TODO: implement your solution
                print("YES")


            if __name__ == "__main__":
                solve()
            """
        ).strip(),
        "sample_tests": [
            {
                "id": 1,
                "input": "()[]{ }\n".replace(" ", ""),
                "output": "YES\n",
                "explanation": "All brackets closed in correct order"
            },
            {
                "id": 2,
                "input": "([)]\n",
                "output": "NO\n",
                "explanation": "Mismatched closing bracket"
            }
        ],
        "resources": [
            {
                "title": "Striver A2Z - Valid Parentheses",
                "url": "https://takeuforward.org/data-structure/check-for-balanced-parentheses/",
                "notes": "Discusses stack based validation"
            },
            {
                "title": "LeetCode #20",
                "url": "https://leetcode.com/problems/valid-parentheses/",
                "notes": "Original constraints and samples"
            }
        ],
        "metadata": {
            "time_complexity": "O(n)",
            "space_complexity": "O(n)"
        },
        "solution_markdown": dedent(
            """
            ```python
            def solve() -> None:
                s = input().strip()
                matching = {
                    ')': '(',
                    ']': '[',
                    '}': '{'
                }
                stack = []

                for ch in s:
                    if ch in '([{':
                        stack.append(ch)
                    else:
                        if not stack or stack.pop() != matching.get(ch):
                            print('NO')
                            return

                print('YES' if not stack else 'NO')
            ```
            """
        ).strip()
    }

def build_dataset() -> None:
    questions = [_question_two_sum(), _question_valid_parentheses()]
    output_dir = Path("data/questions")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "questions.json"

    payload = {"questions": questions}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Generated {len(questions)} questions at {output_path}")


def main() -> None:
    build_dataset()


if __name__ == "__main__":
    main()
