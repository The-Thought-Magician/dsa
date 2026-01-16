# Data Pipeline Documentation

## Overview

The data pipeline transforms C++ source files into a structured question database with AI-enriched content and validated test cases.

## Pipeline Stages

### Stage 1: Extraction

**Script**: `scripts/extract_cpp_questions_batch.py`

Extracts questions from the C++ reference repository.

```bash
python scripts/extract_cpp_questions_batch.py
```

**Input**: `Strivers-A2Z-DSA-Sheet/**/*.cpp`
**Output**: `data/questions/questions.json`

**What it does**:
- Scans all `.cpp` files in the repository
- Parses comments for metadata (title, approach, complexity)
- Generates question IDs from file names
- Creates resource links to original files

### Stage 2: Enrichment

**Script**: `scripts/enrich_questions_with_gemini.py`

Uses AI to generate missing content.

```bash
# Enrich all questions that need it
python scripts/enrich_questions_with_gemini.py

# Enrich specific question
python scripts/enrich_questions_with_gemini.py --only implement-min-heap

# Enrich with limit
python scripts/enrich_questions_with_gemini.py --limit 10 --offset 0

# Enrich with validation (tests solutions)
python scripts/enrich_questions_with_gemini.py --validate
```

**Input**: `data/questions/questions.json`
**Output**: Updated `data/questions/questions.json`, `data/solutions/*.py`

**What it does**:
- Generates problem statements from titles
- Creates step-by-step approach explanations
- Adds background theory
- Generates 3-5 sample test cases
- Creates Python solutions with validation
- Stores generated solutions separately

**API**: Uses Google Gemini 2.5 Flash

### Stage 3: Validation

**Script**: `scripts/validate_dataset.py` (to be created)

Validates data integrity.

```bash
python scripts/validate_dataset.py
```

**Checks**:
- All required fields present
- No placeholder test inputs
- At least 3 test cases per question
- Valid resource URLs
- Python solutions pass tests

### Stage 4: Rebuild

**API Endpoint**: `POST /api/rebuild`

Triggers full pipeline rebuild.

```bash
curl -X POST http://localhost:8000/api/rebuild
```

## Data Schema

### Question Object

```json
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
      "summary": "A binary heap is a...",
      "why_it_matters": "Essential for priority queues...",
      "practice_tips": "Start with insertion..."
    }
  ],
  "starter_code": "def solve():\n    pass",
  "sample_tests": [
    {
      "id": 1,
      "input": "5\n1 2 3 4 5",
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
    "source_file": "Strivers-A2Z-DSA-Sheet/09. Heaps/...",
    "python_solution_path": "data/solutions/implement-min-heap.py"
  },
  "solution_markdown": "Complete solution explanation...",
  "status": "unsolved",
  "attempts": 0
}
```

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

## Progress Tracking

User progress is stored separately in `data/question_progress.json`:

```json
{
  "statuses": {
    "implement-min-heap": "solved",
    "check-if-array-is-heap": "attempted"
  },
  "solution_views": {
    "implement-min-heap": "2024-01-15T10:30:00Z"
  }
}
```

## AI Enrichment Details

### Enrichment Prompt

The enricher sends this prompt to Gemini:

```
You curate programming problems. Analyze the C++ file and return a compact JSON object with keys:
statement_markdown, approach_markdown, theory_markdown, concepts, python_solution, starter_code, sample_tests, solution_markdown, topic_summary.

Rules:
- Output MUST be valid JSON only.
- concepts: exactly 3 objects with name, summary, why_it_matters, practice_tips.
- python_solution: runnable Python 3 reading stdin and printing stdout.
- starter_code: minimal Python scaffold for the problem.
- sample_tests: at least 3 realistic cases with id, input, output, explanation, matching python_solution.
- Be concise and specific.
```

### Retry Logic

The enricher implements exponential backoff:
- Initial request
- 5s delay on rate limit
- 10s delay on timeout
- 20s delay on server error

### Resume Capability

The enricher skips questions that:
- Already have `python_solution_path` in metadata
- Have valid test cases (not starting with `#`)

## Running the Pipeline

### Full Pipeline

```bash
# 1. Extract from C++ sources
python scripts/extract_cpp_questions_batch.py

# 2. Enrich with AI (in batches)
python scripts/enrich_questions_with_gemini.py --limit 50
python scripts/enrich_questions_with_gemini.py --limit 50 --offset 50
# ... continue as needed

# 3. Validate
python scripts/validate_dataset.py
```

### Via API

```bash
# Trigger rebuild (runs extraction + enrichment)
curl -X POST http://localhost:8000/api/rebuild
```

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| Questions data | `data/questions/questions.json` | Main dataset |
| Progress | `data/question_progress.json` | User progress |
| Solutions | `data/solutions/*.py` | Generated Python solutions |
| C++ source | `Strivers-A2Z-DSA-Sheet/` | Reference implementations |
| Logs | `logs/api.log` | Application logs |

## Monitoring

### Check Enrichment Progress

```bash
# Count enriched questions
python -c "
import json
from pathlib import Path

data = json.loads(Path('data/questions/questions.json').read_text())
total = len(data['questions'])
with_solution = sum(1 for q in data['questions'] if q.get('metadata', {}).get('python_solution_path'))
print(f'{with_solution}/{total} questions have Python solutions')
"
```

### Check Placeholder Tests

```bash
python -c "
import json
from pathlib import Path

data = json.loads(Path('data/questions/questions.json').read_text())
placeholders = 0
for q in data['questions']:
    for test in q.get('sample_tests', []):
        if test.get('input', '').strip().startswith('#'):
            placeholders += 1
print(f'{placeholders} placeholder tests found')
"
```

## Troubleshooting

### Enrichment Fails

**Error**: `GEMINI_API_KEY not set`

**Solution**: Set up your `.env` file with a valid API key.

### Rate Limiting

**Error**: Too many 429 responses

**Solution**: Use smaller batches and add delays:
```bash
python scripts/enrich_questions_with_gemini.py --limit 10
# Wait between batches
python scripts/enrich_questions_with_gemini.py --limit 10 --offset 10
```

### Invalid Test Cases

**Error**: Solution fails test validation

**Solution**: Run with `--validate` flag to catch these early, or skip validation for faster enrichment.

## Related Documentation

- [Getting Started](getting-started.md)
- [Developer Setup](developer-setup.md)
- [Troubleshooting](troubleshooting.md)
