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
    assert len(data) > 0


def test_question_detail_contains_statement():
    # pick first available question id
    qid = client.get("/api/questions").json()[0]["id"]
    response = client.get(f"/api/questions/{qid}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == qid
    assert "statement_markdown" in detail
    assert "solution_available" in detail


def test_run_question_returns_verdict():
    qid = client.get("/api/questions").json()[0]["id"]
    # trivial program that prints nothing; with no usable sample tests it will return error
    trivial = "def solve():\n    pass\n\nif __name__ == '__main__':\n    solve()\n"
    response = client.post(
        f"/api/questions/{qid}/run",
        json={"code": trivial, "language": "python"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["verdict"] in {"passed", "failed", "error"}
    assert payload["updated_status"] in {"unsolved", "attempted", "solved"}


def test_view_solution_marks_as_viewed():
    qid = client.get("/api/questions").json()[0]["id"]
    response = client.post(f"/api/questions/{qid}/solution/view")
    # Some extracted questions may not include editorial; handle both cases gracefully
    if response.status_code == 200:
        payload = response.json()
        assert "solution_markdown" in payload
        assert payload["viewed_at_iso"].endswith("Z")
    else:
        # Accept 400 if no solution available
        assert response.status_code == 400
