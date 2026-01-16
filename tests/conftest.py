"""Pytest configuration and fixtures."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_questions_data():
    """Mock questions data for testing."""
    return {
        "questions": [
            {
                "id": "test-question-1",
                "title": "Test Question 1",
                "difficulty": "Easy",
                "tags": ["array", "basics"],
                "statement_markdown": "This is a test question.",
                "starter_code": "def solve():\n    pass\n\nif __name__ == \"__main__\":\n    solve()",
                "sample_tests": [
                    {
                        "id": 1,
                        "input": "5\n1 2 3 4 5",
                        "output": "15",
                        "explanation": "Sum of array elements"
                    },
                    {
                        "id": 2,
                        "input": "3\n10 20 30",
                        "output": "60",
                        "explanation": "Another test case"
                    },
                    {
                        "id": 3,
                        "input": "1\n42",
                        "output": "42",
                        "explanation": "Single element"
                    }
                ],
                "resources": [
                    {
                        "title": "Test Resource",
                        "url": "/repos/test/file.cpp",
                        "notes": "Test reference"
                    }
                ],
                "metadata": {
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "source_file": "test/file.cpp"
                },
                "solution_markdown": "```python\ndef solve():\n    pass\n```"
            }
        ]
    }


@pytest.fixture
def mock_progress_data():
    """Mock progress data for testing."""
    return {
        "statuses": {
            "test-question-1": "unsolved"
        },
        "solution_views": {}
    }


@pytest.fixture
def temp_questions_file(tmp_path, mock_questions_data):
    """Create a temporary questions JSON file."""
    questions_file = tmp_path / "questions.json"
    questions_file.write_text(json.dumps(mock_questions_data), encoding="utf-8")
    return questions_file


@pytest.fixture
def temp_progress_file(tmp_path, mock_progress_data):
    """Create a temporary progress JSON file."""
    progress_file = tmp_path / "question_progress.json"
    progress_file.write_text(json.dumps(mock_progress_data), encoding="utf-8")
    return progress_file


@pytest.fixture
def mock_data_dir(tmp_path, temp_questions_file, temp_progress_file):
    """Create a mock data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "questions").mkdir()
    (temp_questions_file.replace(data_dir / "questions" / "questions.json"))
    (temp_progress_file.replace(data_dir / "question_progress.json"))
    return data_dir


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini AI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Here's how to solve this problem step by step."
    mock_client.models.generate_content.return_value = mock_response
    return mock_client
