# Testing & Code Quality Plan

## Overview

This plan establishes comprehensive testing strategies and code quality standards for the A2Z DSA Learning System.

## Current State

- No unit tests exist
- No integration tests exist
- No code linting configured
- Manual testing only
- No CI/CD pipeline

## Goals

1. Achieve 80%+ code coverage for critical paths
2. All Python code passes linting (ruff)
3. All JavaScript code is linted (ESLint)
4. Automated tests run on every commit
5. Security tests pass

## Phase 1: Python Testing

### 1.1 Test Framework Setup

**File**: `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=api --cov=scripts --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["api", "scripts"]
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
fail_under = 80
```

### 1.2 API Endpoint Tests

**File**: `tests/test_api_questions.py`

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestQuestionsEndpoint:
    """Test questions API endpoints."""

    def test_get_questions_list(self):
        """Test retrieving all questions."""
        response = client.get("/api/questions")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert len(data["questions"]) > 0

    def test_get_question_by_id(self):
        """Test retrieving a specific question."""
        response = client.get("/api/questions/implement-min-heap")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "implement-min-heap"
        assert "title" in data
        assert "difficulty" in data

    def test_get_nonexistent_question(self):
        """Test 404 for non-existent question."""
        response = client.get("/api/questions/nonexistent")
        assert response.status_code == 404

    def test_questions_filter_by_difficulty(self):
        """Test filtering questions by difficulty."""
        response = client.get("/api/questions?difficulty=Easy")
        assert response.status_code == 200
        data = response.json()
        for q in data["questions"]:
            assert q["difficulty"] == "Easy"

    def test_questions_search(self):
        """Test searching questions."""
        response = client.get("/api/questions?search=heap")
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) > 0
```

### 1.3 Code Execution Tests

**File**: `tests/test_code_execution.py`

```python
import pytest
from api.services import execute_code

class TestCodeExecution:
    """Test Python code execution service."""

    def test_simple_print(self):
        """Test basic print statement."""
        result = execute_code("print('Hello, World!')")
        assert result["exit_code"] == 0
        assert "Hello, World!" in result["stdout"]
        assert result["stderr"] == ""

    def test_syntax_error(self):
        """Test syntax error handling."""
        result = execute_code("print('unclosed string")
        assert result["exit_code"] != 0
        assert "SyntaxError" in result["stderr"]

    def test_timeout(self):
        """Test execution timeout."""
        infinite_code = "while True: pass"
        result = execute_code(infinite_code, timeout=1)
        assert result["timeout"] == True
        assert "timeout" in result["stderr"].lower()

    def test_runtime_error(self):
        """Test runtime error handling."""
        result = execute_code("1/0")
        assert result["exit_code"] != 0
        assert "ZeroDivisionError" in result["stderr"]

    def test_multiple_lines(self):
        """Test multi-line code."""
        code = """
def add(a, b):
    return a + b
print(add(2, 3))
"""
        result = execute_code(code)
        assert result["exit_code"] == 0
        assert "5" in result["stdout"]
```

### 1.4 AI Chat Tests

**File**: `tests/test_ai_chat.py`

```python
import pytest
from unittest.mock import patch, MagicMock

class TestAIChat:
    """Test AI chat functionality."""

    @patch('api.services.gemini')
    def test_successful_chat_response(self, mock_gemini):
        """Test successful AI chat response."""
        mock_response = MagicMock()
        mock_response.text = "Here's how to solve this problem..."
        mock_gemini.GenerativeModel.return_value.generate_content.return_value = mock_response

        from api.services import get_ai_response
        response = get_ai_response("How do I implement a heap?")

        assert "solve this problem" in response or response  # Non-empty response

    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': ''}):
            response = client.post("/api/ai/chat", json={"message": "test"})
            assert response.status_code == 503

    @patch('api.services.gemini')
    def test_rate_limit_error(self, mock_gemini):
        """Test rate limit error handling."""
        import google.api_core.exceptions as google_exceptions
        mock_gemini.GenerativeModel.side_effect = google_exceptions.ResourceExhausted("Quota exceeded")

        response = client.post("/api/ai/chat", json={"message": "test"})
        assert response.status_code == 429
```

### 1.5 Dataset Regression Tests

**File**: `tests/test_dataset.py`

```python
import json
from pathlib import Path

class TestDataset:
    """Test dataset integrity."""

    @pytest.fixture
    def questions_data(self):
        """Load questions data."""
        questions_path = Path("data/questions/questions.json")
        with open(questions_path) as f:
            return json.load(f)

    def test_all_questions_have_required_fields(self, questions_data):
        """Test all questions have required fields."""
        required_fields = ["id", "title", "difficulty", "tags", "sample_tests"]
        for question in questions_data["questions"]:
            for field in required_fields:
                assert field in question, f"Question {question.get('id')} missing {field}"

    def test_minimum_test_cases(self, questions_data):
        """Test each question has at least 3 test cases."""
        for question in questions_data["questions"]:
            assert len(question.get("sample_tests", [])) >= 3, \
                f"Question {question['id']} has fewer than 3 tests"

    def test_no_placeholder_tests(self, questions_data):
        """Test no placeholder test inputs remain."""
        placeholder = "# Input will be provided"
        for question in questions_data["questions"]:
            for test in question.get("sample_tests", []):
                assert placeholder not in test.get("input", ""), \
                    f"Question {question['id']} has placeholder test"

    def test_difficulty_values(self, questions_data):
        """Test difficulty values are valid."""
        valid_difficulties = ["Easy", "Medium", "Hard"]
        for question in questions_data["questions"]:
            assert question["difficulty"] in valid_difficulties, \
                f"Question {question['id']} has invalid difficulty"
```

## Phase 2: JavaScript Testing

### 2.1 Setup Vitest

**File**: `frontend/vitest.config.js`

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        environment: 'jsdom',
        include: ['**/*.test.js'],
        coverage: {
            provider: 'v8',
            reporter: ['text', 'html'],
            exclude: ['node_modules/', 'tests/'],
        },
    },
});
```

### 2.2 Utility Tests

**File**: `frontend/assets/js/utils.test.js`

```javascript
import { describe, it, expect } from 'vitest';
import { formatTime, calculateAccuracy, debounce } from './utils.js';

describe('Utility Functions', () => {
    describe('formatTime', () => {
        it('formats seconds as mm:ss', () => {
            expect(formatTime(125)).toBe('02:05');
            expect(formatTime(60)).toBe('01:00');
            expect(formatTime(59)).toBe('00:59');
        });

        it('handles zero', () => {
            expect(formatTime(0)).toBe('00:00');
        });
    });

    describe('calculateAccuracy', () => {
        it('calculates percentage correctly', () => {
            expect(calculateAccuracy(8, 10)).toBe(80);
            expect(calculateAccuracy(5, 5)).toBe(100);
            expect(calculateAccuracy(0, 5)).toBe(0);
        });

        it('handles division by zero', () => {
            expect(calculateAccuracy(0, 0)).toBe(0);
        });
    });

    describe('debounce', () => {
        it('delays function execution', async () => {
            const fn = vi.fn();
            const debounced = debounce(fn, 100);

            debounced();
            expect(fn).not.toHaveBeenCalled();

            await new Promise(r => setTimeout(r, 150));
            expect(fn).toHaveBeenCalledTimes(1);
        });
    });
});
```

## Phase 3: Linting & Formatting

### 3.1 Python Linting (Ruff)

**File**: `pyproject.toml`

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # Line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

**Run commands**:
```bash
# Check linting
ruff check api/ scripts/

# Auto-fix
ruff check --fix api/ scripts/

# Format
ruff format api/ scripts/
```

### 3.2 JavaScript Linting (ESLint)

**File**: `frontend/.eslintrc.js`

```javascript
module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    extends: ['eslint:recommended'],
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
    },
    rules: {
        'indent': ['error', 4],
        'quotes': ['error', 'single'],
        'semi': ['error', 'always'],
        'no-unused-vars': 'warn',
        'no-console': 'off',
    },
    globals: {
        'window': 'readonly',
        'document': 'readonly',
        'Chart': 'readonly',
    },
};
```

**File**: `frontend/package.json`

```json
{
  "scripts": {
    "lint": "eslint assets/js/**/*.js",
    "lint:fix": "eslint --fix assets/js/**/*.js",
    "test": "vitest",
    "test:coverage": "vitest --coverage"
  },
  "devDependencies": {
    "eslint": "^8.57.0",
    "vitest": "^1.3.0",
    "jsdom": "^24.0.0"
  }
}
```

## Phase 4: Integration Tests

### 4.1 End-to-End Tests (Playwright)

**File**: `tests/e2e/test_user_flow.spec.js`

```javascript
import { test, expect } from '@playwright/test';

test.describe('Question Solving Flow', () => {
    test('user can view and attempt a question', async ({ page }) => {
        await page.goto('/questions');

        // Click on first question
        await page.click('.question-card:first-child');

        // Verify question detail loads
        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('.code-editor')).toBeVisible();

        // Type code
        await page.fill('.code-editor textarea', 'print("test")');

        // Click run
        await page.click('button:has-text("Run")');

        // Verify output appears
        await expect(page.locator('.output-panel')).toContainText('test');
    });

    test('user can filter questions by difficulty', async ({ page }) => {
        await page.goto('/questions');

        // Select Medium difficulty
        await page.selectOption('select[name="difficulty"]', 'Medium');

        // Verify filtered results
        const badges = await page.locator('.difficulty-badge').allTextContents();
        badges.forEach(badge => expect(badge).toBe('Medium'));
    });
});
```

## Phase 5: CI/CD Pipeline

### 5.1 GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

```yaml
name: Test

on:
  push:
    branches: ['dev', 'master']
  pull_request:
    branches: ['dev', 'master']

jobs:
  lint-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff
      - run: ruff check api/ scripts/

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e '.[test]'
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v4

  test-javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: cd frontend && npm install
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run test
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Setup pytest in pyproject.toml | High | - |
| 2 | Write API endpoint tests | High | Step 1 |
| 3 | Write code execution tests | High | Step 1 |
| 4 | Write dataset regression tests | High | - |
| 5 | Setup ruff for Python linting | High | - |
| 6 | Run ruff and fix issues | High | Step 5 |
| 7 | Setup Vitest for JS testing | Medium | - |
| 8 | Write JS utility tests | Medium | Step 7 |
| 9 | Setup ESLint for frontend | Medium | - |
| 10 | Create GitHub Actions workflow | Low | All above |

## Success Criteria

- [ ] pytest runs without errors
- [ ] Code coverage >= 80% for api/ and scripts/
- [ ] ruff check passes with 0 errors
- [ ] All Python code formatted with ruff format
- [ ] ESLint passes for frontend JavaScript
- [ ] CI/CD pipeline runs on every push
- [ ] Dataset regression tests catch missing tests
- [ ] Security tests prevent dangerous code execution
- [ ] Integration tests cover user flows

## Test Coverage Targets

| Module | Target Coverage | Priority |
|--------|----------------|----------|
| `api/services.py` | 90% | High |
| `api/routers/*.py` | 85% | High |
| `scripts/*.py` | 70% | Medium |
| `frontend/assets/js/*.js` | 60% | Low |
