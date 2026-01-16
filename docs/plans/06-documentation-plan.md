# Documentation Plan

## Overview

This plan addresses documentation gaps across the project, including user guides, API documentation, developer setup, and data pipeline documentation.

## Current Documentation Status

| Document | Location | Status | Notes |
|----------|----------|--------|-------|
| Master Plan | docs/plan.md | Complete | Phase 1 complete, future phases outlined |
| Design Doc | docs/design.md | Complete | Architecture and algorithms |
| TODO List | docs/TODO.md | Complete | 76-item checklist |
| Done Log | docs/done.md | Complete | Progress history |
| Frontend Design | docs/frontend_design.md | Complete | UI/UX specifications |
| Context | docs/context.md | Complete | Project background |
| README | docs/README.md | Complete | API reference and user guide |
| Plans | docs/plans/ | **Missing** | To be created |

## Documentation Gaps

1. **Getting Started Guide** - No step-by-step setup for new users
2. **Data Pipeline Documentation** - Extract → Enrich → Validate flow not documented
3. **Contributing Guidelines** - No contribution standards defined
4. **Troubleshooting Guide** - No common issue resolutions
5. **Deployment Guide** - No production deployment instructions
6. **API Examples** - Limited usage examples
7. **Scripts Documentation** - Automation scripts lack detailed docs

## Phase 1: Getting Started Guide

### 1.1 User Quick Start

**File**: `docs/getting-started.md`

```markdown
# Getting Started

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager)
- Google Gemini API key (for AI features)

## Installation

### 1. Clone the repository

\`\`\`bash
git clone <repository-url>
cd dsa
\`\`\`

### 2. Install dependencies

\`\`\`bash
uv pip install -e .
\`\`\`

### 3. Configure environment

\`\`\`bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
\`\`\`

### 4. Start the server

\`\`\`bash
python run_server.py
\`\`\`

### 5. Open in browser

Navigate to http://localhost:8000

## First Steps

1. View the Dashboard to see your progress
2. Browse Topics to find questions to practice
3. Start solving questions in the Questions section
4. Use AI Chat for help when stuck
5. Check Planning for a personalized study schedule

## CLI Usage

\`\`\`bash
# List all topics
python -m dsa list topics

# Show coverage gaps
python -m dsa gaps

# Generate a study plan
python -m dsa plan --days 14
\`\`\`
```

### 1.2 Developer Setup Guide

**File**: `docs/developer-setup.md`

```markdown
# Developer Setup

## Development Environment

### Required Tools

- Python 3.11+
- uv (package manager)
- Git
- VS Code (recommended) or any Python IDE

### VS Code Extensions

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- REST Client (humao.rest-client)

### Running the Development Server

\`\`\`bash
# With auto-reload
uvicorn api.main:app --reload --port 8000

# Or using the helper script
python run_server.py
\`\`\`

### Project Structure

\`\`\`
dsa/
├── api/                    # FastAPI backend
│   ├── main.py            # Application entry point
│   ├── models.py          # Pydantic models
│   ├── services.py        # Business logic
│   └── routers/           # API routes
├── frontend/              # Web interface
│   ├── index.html         # Main SPA
│   ├── assets/            # CSS, JS
│   └── components/        # HTML partials
├── scripts/               # Automation utilities
├── data/                  # Generated data
└── docs/                  # Documentation
\`\`\`

## Development Workflow

1. Create a feature branch from `dev`
2. Make changes with tests
3. Run linting: `ruff check api/ scripts/`
4. Run tests: `pytest`
5. Submit PR to `dev`
```

## Phase 2: Data Pipeline Documentation

### 2.1 Pipeline Overview

**File**: `docs/data-pipeline.md`

```markdown
# Data Pipeline Documentation

## Overview

The data pipeline transforms C++ source files into a structured question database
with AI-enriched content and validated test cases.

## Pipeline Stages

### Stage 1: Extraction

**Script**: `scripts/extract_cpp_questions_batch.py`

Extracts questions from the C++ reference repository.

\`\`\`bash
python scripts/extract_cpp_questions_batch.py
\`\`\`

**Input**: `Strivers-A2Z-DSA-Sheet/**/*.cpp`
**Output**: `data/questions/questions.json`

**What it does**:
- Scans all .cpp files in the repository
- Parses comments for metadata (title, approach, complexity)
- Generates question IDs from file names
- Creates resource links to original files

### Stage 2: Enrichment

**Script**: `scripts/enrich_questions_with_gemini.py`

Uses AI to generate missing content.

\`\`\`bash
# Enrich all questions
python scripts/enrich_questions_with_gemini.py

# Enrich specific question
python scripts/enrich_questions_with_gemini.py --only implement-min-heap

# Enrich with limit
python scripts/enrich_questions_with_gemini.py --limit 10 --offset 0
\`\`\`

**Input**: `data/questions/questions.json`
**Output**: Updated `data/questions/questions.json`, `data/solutions/*.py`

**What it does**:
- Generates problem statements from titles
- Creates step-by-step approach explanations
- Adds background theory
- Generates 3-5 sample test cases
- Creates Python solutions with validation

**API**: Uses Google Gemini 2.5 Flash

### Stage 3: Validation

**Script**: `scripts/validate_dataset.py`

Validates data integrity.

\`\`\`bash
python scripts/validate_dataset.py
\`\`\`

**Checks**:
- All required fields present
- No placeholder test inputs
- At least 3 test cases per question
- Valid resource URLs
- Python solutions pass tests

### Stage 4: Rebuild

**API Endpoint**: `POST /api/rebuild`

Triggers full pipeline rebuild.

\`\`\`bash
curl -X POST http://localhost:8000/api/rebuild
\`\`\`

## Data Schema

See `docs/data-schema.md` for complete schema documentation.
```

### 2.2 Data Schema Reference

**File**: `docs/data-schema.md`

```markdown
# Data Schema Reference

## Question Object

\`\`\`json
{
  "id": "implement-min-heap",
  "title": "Implement Min Heap",
  "difficulty": "Medium",
  "tags": ["heap", "priority-queue"],
  "statement_markdown": "Complete problem statement...",
  "approach_markdown": "Step-by-step explanation...",
  "theory_markdown": "Background concepts...",
  "concepts": [
    {
      "name": "Binary Heap",
      "summary": "...",
      "why_it_matters": "...",
      "practice_tips": "..."
    }
  ],
  "starter_code": "def solve():\\n    pass",
  "sample_tests": [
    {
      "id": 1,
      "input": "5\\n1 2 3 4 5",
      "output": "1",
      "explanation": "Minimum element is 1"
    }
  ],
  "resources": [
    {
      "title": "Original C++ Solution",
      "url": "/repos/09. Heaps/1. Learning/01. Implement min heap.cpp",
      "notes": "Reference implementation"
    }
  ],
  "metadata": {
    "time_complexity": "O(log n)",
    "space_complexity": "O(n)",
    "source_file": "Strivers-A2Z-DSA-Sheet/09. Heaps/..."
  },
  "solution_markdown": "Complete solution explanation...",
  "status": "unsolved",
  "attempts": 0
}
\`\`\`

## Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier (kebab-case) |
| title | string | Yes | Question title |
| difficulty | string | Yes | Easy/Medium/Hard |
| tags | string[] | Yes | Topic tags |
| statement_markdown | string | No | Problem statement |
| starter_code | string | No | Python starter code |
| sample_tests | Test[] | Yes | Sample test cases (min 3) |
| resources | Resource[] | Yes | Reference materials |
| metadata | Metadata | Yes | Complexity info |
| status | string | Yes | unsolved/attempted/solved |
| attempts | number | Yes | Number of attempts |
```

## Phase 3: API Documentation

### 3.1 Complete API Reference

**File**: `docs/api-reference.md`

```markdown
# API Reference

## Base URL

\`\`\`
http://localhost:8000
\`\`\`

## Authentication

Currently no authentication required (development mode).

## Endpoints

### Statistics

\`\`\`http
GET /api/stats
\`\`\`

Returns overall system statistics.

**Response**:
\`\`\`json
{
  "total_sections": 18,
  "total_problems": 361,
  "python_solutions": 324,
  "coverage_percentage": 67.8
}
\`\`\`

### Questions

\`\`\`http
GET /api/questions?difficulty=Medium&tag=array&search=heap&page=1&limit=50
\`\`\`

List and filter questions.

**Query Parameters**:
- `difficulty`: Filter by difficulty (Easy/Medium/Hard)
- `tag`: Filter by topic tag
- `search`: Search in title and statement
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)

### Question Detail

\`\`\`http
GET /api/questions/{id}
\`\`\`

Get full question details.

### Run Code

\`\`\`http
POST /api/questions/{id}/run
Content-Type: application/json

{
  "code": "print('Hello, World!')"
}
\`\`\`

Execute Python code with 5-second timeout.

### AI Chat

\`\`\`http
POST /api/ai/chat
Content-Type: application/json

{
  "message": "How do I implement a heap?",
  "question_id": "implement-min-heap"
}
\`\`\`

Get AI assistance for a question.

### Study Plans

\`\`\`http
GET /api/study-plan
GET /api/study-plan/today
POST /api/study-plan/generate?days=14&daily_hours=2
\`\`\`

Manage personalized study plans.
```

## Phase 4: Troubleshooting Guide

### 4.1 Common Issues

**File**: `docs/troubleshooting.md`

```markdown
# Troubleshooting

## Common Issues

### Server won't start

**Symptom**: `Address already in use` error

**Solution**:
\`\`\`bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn api.main:app --port 8001
\`\`\`

### AI chat returns errors

**Symptom**: 503 Service Configuration Error

**Solution**:
1. Verify GEMINI_API_KEY is set in .env
2. Check the API key is valid at https://aistudio.google.com
3. Ensure you have API quota available

### Code execution timeout

**Symptom**: All code executions timeout

**Solution**:
1. Check if Python 3 is available: `python3 --version`
2. Verify subprocess isn't blocked by antivirus
3. Check logs in `logs/api.log`

### Frontend shows console errors

**Symptom**: Charts don't render, API errors

**Solution**:
1. Open browser DevTools Console
2. Check for CORS errors
3. Verify API_BASE_URL in `frontend/assets/js/config.js`
4. Clear browser cache

## Getting Help

- Check logs in `logs/api.log`
- Review GitHub Issues
- Create a new issue with error details
```

## Phase 5: Contributing Guidelines

### 5.1 Contribution Standards

**File**: `CONTRIBUTING.md`

```markdown
# Contributing to A2Z DSA Learning System

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run linting and tests
6. Submit a pull request

## Code Style

### Python

- Use ruff for linting
- Follow PEP 8 guidelines
- Add type hints for functions
- Keep functions under 50 lines

### JavaScript

- Use 4-space indentation
- Prefer const/let over var
- Add JSDoc comments for functions
- Avoid global variables

## Commit Messages

Follow conventional commits:

\`\`\`
feat: add question filtering by difficulty
fix: resolve chart rendering issue
docs: update API documentation
test: add code execution tests
\`\`\`

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Request review from maintainers
4. Address review feedback
5. Squash commits if requested
```

## Phase 6: Migration Notes

### 6.1 Legacy File Cleanup

**File**: `docs/migration-notes.md`

```markdown
# Migration Notes

## Moved Files

The following files have been moved to maintain project structure:

| Original | New Location | Reason |
|----------|--------------|--------|
| `CLAUDE.md` | `.backup/CLAUDE.md` | Not needed for users |
| `TRANSFORMATION_SUMMARY.md` | `.backup/` | Historical reference |
| `striver-a2z-dsa/` | `.backup/` | Duplicate repository |
| `test_extraction.py` | `.backup/` | Test file, not production |

## Breaking Changes

### API Changes

- Old: `/repos/` required full file paths
- New: All resource URLs normalized to `/repos/` format

### Frontend Changes

- Old: Hardcoded `localhost:8000` URLs
- New: Use `Config.endpoint()` method
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Create getting-started.md | High | - |
| 2 | Create developer-setup.md | High | - |
| 3 | Create data-pipeline.md | High | - |
| 4 | Create data-schema.md | High | Step 3 |
| 5 | Update api-reference.md | Medium | - |
| 6 | Create troubleshooting.md | Medium | - |
| 7 | Create CONTRIBUTING.md | Medium | - |
| 8 | Create migration-notes.md | Low | - |
| 9 | Update main README with links | Medium | All above |
| 10 | Verify all links work | Low | All above |

## Success Criteria

- [ ] New users can set up in < 10 minutes
- [ ] Data pipeline flow is clearly documented
- [ ] All endpoints have examples
- [ ] Common issues have solutions documented
- [ ] Contributors have clear guidelines
- [ ] All documentation links work
- [ ] Schema reference is complete
- [ ] Migration history is preserved
