"""Tests for API services."""

import json
import subprocess
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.services import (
    DataService,
    validate_code_for_execution,
    sanitize_code_output,
    DANGEROUS_PATTERNS,
)


class TestCodeValidation:
    """Tests for code validation security functions."""

    def test_valid_code_passes(self):
        """Test that safe code passes validation."""
        code = """
def solve():
    arr = [1, 2, 3, 4, 5]
    total = sum(arr)
    print(total)
    return total

if __name__ == "__main__":
    solve()
"""
        is_valid, error = validate_code_for_execution(code)
        assert is_valid
        assert error == ""

    def test_import_blocked(self):
        """Test that imports are blocked."""
        code = "import os\nprint('test')"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "not allowed" in error.lower()

    def test_subprocess_blocked(self):
        """Test that subprocess calls are blocked."""
        code = "subprocess.run(['ls'])"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "not allowed" in error.lower()

    def test_eval_blocked(self):
        """Test that eval() is blocked."""
        code = "eval('print(1)')"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "not allowed" in error.lower()

    def test_path_traversal_blocked(self):
        """Test that path traversal is blocked."""
        code = "print(open('../etc/passwd').read())"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "not allowed" in error.lower()

    def test_network_call_blocked(self):
        """Test that network calls are blocked."""
        code = "import urllib.request\nurllib.request.urlopen('http://example.com')"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid

    def test_code_too_long(self):
        """Test that excessively long code is rejected."""
        code = "print(" + "x" * 10001 + ")"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "maximum length" in error.lower()

    def test_code_too_many_lines(self):
        """Test that code with too many lines is rejected."""
        code = "\n".join(["print('line')"] * 201)
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "line count" in error.lower()

    def test_globals_blocked(self):
        """Test that use of globals() is blocked."""
        code = "print(globals())"
        is_valid, error = validate_code_for_execution(code)
        assert not is_valid
        assert "not allowed" in error.lower()


class TestOutputSanitization:
    """Tests for output sanitization."""

    def test_normal_output_unchanged(self):
        """Test that normal output is unchanged."""
        output = "42\n43\n44"
        result = sanitize_code_output(output)
        assert result == output

    def test_file_path_removed(self):
        """Test that file paths are removed."""
        output = "Result: 42\n/tmp/test.py line 10\nDone"
        result = sanitize_code_output(output)
        assert "/tmp/test.py" not in result

    def test_traceback_simplified(self):
        """Test that traceback is simplified."""
        output = """Traceback (most recent call last):
  File "/tmp/test.py", line 5, in <module>
    main()
NameError: name 'main' is not defined"""
        result = sanitize_code_output(output)
        assert "Traceback" in result
        assert "/tmp/test.py" not in result
        assert "NameError" in result


class TestDataService:
    """Tests for DataService."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a DataService instance with temporary directory."""
        with patch('api.services.Path') as mock_path:
            mock_path.return_value = Path(tmp_path)
            service = DataService()
            service.data_dir = tmp_path
            service.questions_payload_path = tmp_path / "questions.json"
            service.question_progress_path = tmp_path / "progress.json"
            return service

    def test_load_jsonl_file_not_found(self, service):
        """Test loading non-existent JSONL file returns empty list."""
        result = service.load_jsonl(Path("nonexistent.jsonl"))
        assert result == []

    def test_load_jsonl_success(self, service, tmp_path):
        """Test loading valid JSONL file."""
        jsonl_file = tmp_path / "test.jsonl"
        jsonl_file.write_text('{"id": "1", "name": "test"}\n{"id": "2", "name": "test2"}')

        result = service.load_jsonl(jsonl_file)
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"


class TestAPIClients:
    """Tests for FastAPI client endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_stats_endpoint(self, client):
        """Test stats endpoint returns expected structure."""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_problems" in data
        assert "coverage_percentage" in data
        assert isinstance(data["total_problems"], int)

    def test_topics_endpoint(self, client):
        """Test topics endpoint returns list."""
        response = client.get("/api/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_coverage_endpoint(self, client):
        """Test coverage endpoint returns expected structure."""
        response = client.get("/api/coverage")
        assert response.status_code == 200
        data = response.json()
        assert "total_problems" in data
        assert "coverage_percentage" in data

    def test_study_plan_endpoint(self, client):
        """Test study plan endpoint returns expected structure."""
        response = client.get("/api/study-plan")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert "summary" in data

    def test_rebuild_endpoint_post_only(self, client):
        """Test that rebuild only accepts POST requests."""
        response = client.get("/api/rebuild")
        assert response.status_code == 405  # Method Not Allowed

    def test_spa_fallback(self, client):
        """Test SPA fallback routes."""
        response = client.get("/topics")
        # Should return HTML for SPA
        assert response.status_code == 200


class TestSecurityPatterns:
    """Tests for security pattern definitions."""

    def test_all_dangerous_patterns_defined(self):
        """Test that all dangerous patterns are properly defined."""
        assert len(DANGEROUS_PATTERNS) > 0

        required_patterns = ["import", "subprocess", "eval", "exec", "open", "os"]
        pattern_strings = [pattern for pattern, _ in DANGEROUS_PATTERNS]

        for required in required_patterns:
            assert any(required in p for p in pattern_strings), f"Pattern for '{required}' not found"

    def test_all_patterns_have_messages(self):
        """Test that all patterns have error messages."""
        for pattern, message in DANGEROUS_PATTERNS:
            assert isinstance(message, str)
            assert len(message) > 0


@pytest.mark.parametrize("code,should_pass", [
    ("print('hello')", True),
    ("x = [1,2,3]\nprint(sum(x))", True),
    ("def f(): return 42", True),
    ("import os", False),
    ("subprocess.run", False),
    ("eval('1+1')", False),
    ("exec('print(1)')", False),
    ("open('file.txt')", False),
    ("os.system('ls')", False),
    ("../etc/passwd", False),
])
def test_code_validation_examples(code, should_pass):
    """Parametrized test for various code examples."""
    is_valid, _ = validate_code_for_execution(code)
    assert is_valid == should_pass, f"Code: {code}"
