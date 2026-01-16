# Data Quality Enhancement Plan

## Overview

This plan addresses critical data quality issues in the A2Z DSA Learning System. The primary issues are placeholder test cases, incomplete AI enrichment, and sub-80% solution coverage.

## Current Status

- **Total Questions**: 361
- **Python Solutions**: 324 (67.8%)
- **C++ Solutions**: 345 (72.2%)
- **Overall Coverage**: 70.0%
- **Target Coverage**: 80%+

## Problem Statement

1. **Placeholder Tests**: Many questions have `# Input will be provided` instead of actual test cases
2. **Missing Python Solutions**: 154 Python implementations need to be added to reach 80% coverage
3. **Incomplete AI Enrichment**: Questions have `metadata.needs_ai_generation: true` flags
4. **Inconsistent Metadata**: Some questions missing difficulty, tags, or proper resource links

## Phase 1: Test Case Completion

### 1.1 Identify Placeholder Tests

**File**: `scripts/identify_placeholder_tests.py`

- Create script to scan `data/questions/questions.json`
- Find all questions with placeholder test inputs
- Generate report: `data/reports/placeholder_tests.json`

**Success Criteria**: All placeholder tests identified and documented

### 1.2 Generate Real Test Cases

**File**: `scripts/generate_test_cases.py`

**Approach**:
- Use Gemini AI to generate test cases based on problem statements
- For each question with placeholder tests:
  - Generate 3-5 sample test cases
  - Include edge cases (boundary conditions, empty inputs, etc.)
  - Validate expected outputs

**API Call Pattern**:
```python
prompt = f"""
Generate 3-5 test cases for this problem:

Title: {question.title}
Statement: {question.statement_markdown}
Difficulty: {question.difficulty}

Return JSON format:
[{{"input": "...", "output": "...", "explanation": "..."}}]
"""
```

**Success Criteria**: All questions have at least 3 valid test cases

### 1.3 Validate Test Cases

**File**: `scripts/validate_test_cases.py`

- Run generated Python solutions against test cases
- Verify outputs match expected results
- Flag any failing tests for manual review

## Phase 2: AI Enrichment Pipeline

### 2.1 Enhance Enricher Script

**File**: `scripts/enrich_questions_with_gemini.py`

**Current Issues**:
- Processes all questions at once (memory intensive)
- No resume capability for failures
- No rate limiting handling

**Required Changes**:

1. **Add Resume Capability**:
   ```python
   # Skip already enriched questions
   if not question.metadata.get("needs_ai_generation"):
       continue
   ```

2. **Add Control Flags**:
   ```python
   @app.command()
   def enrich(
       only: str = Option(None, "--only", help="Enrich specific question ID"),
       limit: int = Option(10, "--limit", help="Max questions to enrich"),
       offset: int = Option(0, "--offset", help="Skip N questions")
   ):
   ```

3. **Add Retry Logic**:
   ```python
   def enrich_with_retry(question, max_retries=3):
       for attempt in range(max_retries):
           try:
               return call_gemini(question)
           except RateLimitError:
               time.sleep(2 ** attempt)  # Exponential backoff
   ```

4. **Store Python Solutions**:
   ```python
   # Save to separate file
   solution_path = f"data/solutions/{question.id}.py"
   with open(solution_path, "w") as f:
       f.write(generated_python_code)
   ```

### 2.2 Enrichment Fields

For each question, generate:

| Field | Description |
|-------|-------------|
| `statement_markdown` | Complete problem statement with examples |
| `approach_markdown` | Step-by-step explanation |
| `theory_markdown` | Background concepts needed |
| `concepts` | Array of concept objects with name/summary/tips |
| `starter_code` | Python function signature with TODO |
| `sample_tests` | 3-5 validated test cases |
| `solution_markdown` | Complete solution with explanation |
| `python_solution` | Working Python code (saved separately) |

### 2.3 Validation

**File**: `scripts/validate_enrichment.py`

Checks:
- All required fields present
- Sample tests produce expected output
- Python solution passes all tests
- Concepts match expected schema
- Resource URLs are valid

## Phase 3: Coverage Improvement

### 3.1 Identify Gaps

**File**: `scripts/analyze_coverage_gaps.py`

- Find questions without Python solutions
- Group by A2Z section
- Prioritize by:
  1. Difficulty (Easy first for quick wins)
  2. Section completeness (finish sections partially done)
  3. Interview frequency (common patterns first)

### 3.2 Generate Missing Solutions

**File**: `scripts/generate_missing_solutions.py`

- Use C++ solutions as reference
- Convert to Python with AI assistance
- Validate against test cases
- Save to `data/solutions/<id>.py`

### 3.3 Coverage Tracking

**Metrics Dashboard**:
```json
{
  "total_questions": 361,
  "with_python_solution": 324,
  "with_valid_tests": 156,
  "fully_enriched": 89,
  "target_80_percent": 289,
  "remaining_needed": 154
}
```

## Phase 4: Data Integrity

### 4.1 Schema Validation

**File**: `scripts/validate_dataset.py`

Validate each question has:
- [ ] `id` (unique, kebab-case)
- [ ] `title` (non-empty string)
- [ ] `difficulty` (Easy/Medium/Hard)
- [ ] `tags` (array of strings)
- [ ] `resources` (at least one, with valid URL)
- [ ] `metadata.source_file` (valid path)
- [ ] `sample_tests` (at least 3 valid tests)

### 4.2 Path Normalization

**File**: `scripts/normalize_paths.py`

- Convert `file://` URLs to `/repos/...` format
- Ensure forward slashes on all platforms
- Validate paths exist in repository

### 4.3 Cleanup Script

**File**: `scripts/cleanup_dataset.py`

- Remove `metadata.needs_ai_generation` flags after enrichment
- Remove duplicate or dead code
- Format JSON with consistent indentation

## Execution Order

| Step | Task | Estimated Time | Dependencies |
|------|------|----------------|--------------|
| 1 | Create placeholder test identifier | 1 hour | - |
| 2 | Generate test cases for 50 questions | 2 hours | Step 1 |
| 3 | Validate generated tests | 1 hour | Step 2 |
| 4 | Enhance enricher with resume/control | 2 hours | - |
| 5 | Run enrichment on 100 highest-priority questions | 4 hours | Step 4 |
| 6 | Generate 50 missing Python solutions | 3 hours | - |
| 7 | Run full dataset validation | 1 hour | All above |
| 8 | Fix validation failures | 2 hours | Step 7 |
| 9 | Normalize all paths | 1 hour | - |
| 10 | Final cleanup and verification | 1 hour | All above |

**Total Estimated Time**: 18 hours

## Success Criteria

- [ ] All 361 questions have at least 3 valid test cases
- [ ] At least 289 questions (80%) have Python solutions
- [ ] All questions have complete metadata
- [ ] No placeholder strings remain in dataset
- [ ] All resource URLs are valid
- [ ] Dataset validation passes without errors

## Rollback Plan

Before each bulk update:
1. Backup `data/questions/questions.json` to `.backup/questions.json.timestamp`
2. Use Git commits with descriptive messages
3. Keep previous enrichment outputs for comparison

## Notes

- AI enrichment rate limits: ~10 requests/minute for free tier
- Consider batch processing overnight for large datasets
- Manual review recommended for Hard difficulty problems
