from pathlib import Path

from fastapi.testclient import TestClient

from api.main import app
from api.services import data_service

client = TestClient(app)

TEST_PROGRESS_PATH = Path("data/question_progress_test.json")
_ORIGINAL_PROGRESS_PATH = data_service.question_progress_path


def setup_module(module):
    data_service.question_progress_path = TEST_PROGRESS_PATH
    if TEST_PROGRESS_PATH.exists():
        TEST_PROGRESS_PATH.unlink()


def teardown_module(module):
    data_service.question_progress_path = _ORIGINAL_PROGRESS_PATH
    if TEST_PROGRESS_PATH.exists():
        TEST_PROGRESS_PATH.unlink()


def test_list_questions_returns_items():
    response = client.get("/api/questions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == "two-sum" for item in data)


def test_question_detail_contains_statement():
    response = client.get("/api/questions/two-sum")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == "two-sum"
    assert "statement_markdown" in detail
    assert detail["solution_available"] is True


def test_run_question_produces_passed_verdict():
    solution_code = (
        "from typing import Dict, List\n\n"
        "def solve() -> None:\n"
        "    n = int(input().strip())\n"
        "    nums = list(map(int, input().split()))\n"
        "    target = int(input().strip())\n\n"
        "    seen: Dict[int, int] = {}\n"
        "    for idx, value in enumerate(nums):\n"
        "        remaining = target - value\n"
        "        if remaining in seen:\n"
        "            i = seen[remaining]\n"
        "            j = idx\n"
        "            print(f\"{min(i, j)} {max(i, j)}\")\n"
        "            return\n"
        "        seen[value] = idx\n\n"
        "if __name__ == '__main__':\n"
        "    solve()\n"
    )
    response = client.post(
        "/api/questions/two-sum/run",
        json={"code": solution_code, "language": "python"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["verdict"] == "passed"
    assert payload["updated_status"] in {"attempted", "solved"}


def test_view_solution_marks_as_viewed():
    response = client.post("/api/questions/two-sum/solution/view")
    assert response.status_code == 200
    payload = response.json()
    assert "solution_markdown" in payload
    assert payload["viewed_at_iso"].endswith("Z")
