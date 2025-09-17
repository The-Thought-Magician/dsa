from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_study_plan_endpoints_exist():
    res_today = client.get("/api/study-plan/today")
    assert res_today.status_code == 200
    assert "task_count" in res_today.json()

    res_plan = client.get("/api/study-plan")
    assert res_plan.status_code == 200
    data = res_plan.json()
    assert "plans" in data
    assert "summary" in data


def test_rebuild_endpoint_exists():
    res = client.post("/api/rebuild")
    assert res.status_code == 200
    payload = res.json()
    assert "status" in payload
