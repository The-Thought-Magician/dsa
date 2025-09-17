# A2Z DSA Learning System - Technical Design

## System Architecture

### Overview
The A2Z DSA Learning System is built as a collection of loosely-coupled Python scripts with a unified CLI interface. The architecture emphasizes simplicity, maintainability, and extensibility while providing comprehensive learning workflow automation.

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface (main.py)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────── │
│  │    list     │ │    gaps     │ │    plan     │ │  stats  │
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────── │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Data Layer     │   │  Scripts Layer   │   │ Analytics Layer │
│                 │   │                 │   │                │
│ • index.jsonl   │   │ • analyze_repos │   │ • coverage_check│
│ • mapping.jsonl │   │ • build_index   │   │ • study_planner │
│ • a2z_structure │   │ • build_a2z     │   │ • gap_analysis  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│              Source Data Repositories                       │
│  ┌──────────────────┐        ┌──────────────────┐           │
│  │ striver-a2z-dsa/ │        │Strivers-A2Z-DSA- │           │
│  │ (Python solutions│        │Sheet/ (C++ ref)  │           │
│  │  324 files)      │        │ (369 files)      │           │
│  └──────────────────┘        └──────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Data Model & Schema Design

### Core Entities

#### 1. IndexEntry Schema
```json
{
  "id": "step01_basics",
  "title": "Learn the basics",
  "path": "Step 01 - Learn the basics",
  "tags": ["variables", "loops", "functions"],
  "source_links": ["https://takeuforward.org/..."],
  "related_problems": ["step01_basics_problem1", "step01_basics_problem2"],
  "local_files": ["/path/to/python/file.py", "/path/to/cpp/file.cpp"],
  "notes": "Python: 6 files, C++: 39 files",
  "difficulty": null,
  "step_number": 1,
  "status": "available"
}
```

#### 2. MappingEntry Schema
```json
{
  "problem_id": "step03_arrays_largest_element",
  "title": "Largest Element In Array",
  "a2z_path": "Step 03 - Arrays",
  "links": [],
  "python_file_path": "/home/user/striver-a2z-dsa/Step 03 - Arrays/LARGEST.py",
  "cpp_file_path": "/home/user/Strivers-A2Z-DSA-Sheet/01.Arrays/1.Easy/01.Largest_element_in_array.cpp",
  "status": "exact-match",
  "approach_summary": "Initialize ans with first element, traverse and update",
  "time_complexity": "O(N)",
  "space_complexity": "O(1)",
  "tags": ["array", "traversal"]
}
```

#### 3. A2ZSection Schema
```json
{
  "id": "step03_arrays",
  "title": "Solve Problems on Arrays",
  "step_number": 3,
  "python_section": "Step 03 - Arrays",
  "cpp_section": "01.Arrays",
  "subsections": ["Easy", "Medium", "Hard"],
  "total_problems": 74,
  "python_count": 35,
  "cpp_count": 39,
  "topics": ["Array Manipulation", "Two Pointers", "Sliding Window"],
  "source_url": "https://takeuforward.org/strivers-a2z-dsa-course/"
}
```

### Data Flow Architecture

#### 1. Ingestion Pipeline
```
Raw Repositories → analyze_repos.py → {python,cpp}_analysis.json
                                     ↓
A2Z Structure ← build_a2z_structure.py ← Course Definition
                                     ↓
Cross-References ← build_index.py ← {index,mapping}.jsonl
```

#### 2. Query Pipeline
```
CLI Commands → load_jsonl() → Filter/Transform → Rich UI Display
             ↓
Analytics Scripts → Statistical Analysis → Reports/Plans
```

### File Organization

```
dsa/
├── data/                          # Generated data files
│   ├── index.jsonl               # Main topic index (71 entries)
│   ├── mapping.jsonl             # Problem cross-references (478 entries)
│   ├── a2z_structure.json        # Course structure definition
│   ├── python_analysis.json      # Python repo analysis
│   ├── cpp_analysis.json         # C++ repo analysis
│   └── study_plan_14day.json     # Generated study plans
├── scripts/                       # Automation utilities
│   ├── analyze_repos.py          # Repository structure analysis
│   ├── build_a2z_structure.py    # Course structure generation
│   ├── build_index.py            # Index and mapping generation
│   ├── coverage_checker.py       # Gap analysis and validation
│   └── study_plan_generator.py   # Intelligent scheduling
├── main.py                        # CLI interface
├── striver-a2z-dsa/              # Python solutions repository
├── Strivers-A2Z-DSA-Sheet/       # C++ reference repository
└── docs/                          # Documentation
    ├── plan.md
    ├── design.md
    └── done.md
```

## Algorithm Design

### 1. Problem Matching Algorithm
The cross-reference mapping uses a hybrid approach:

```python
def find_matching_problems(python_data, cpp_data):
    # Step 1: Exact string matching (normalized)
    # Step 2: Jaccard similarity with 30% threshold
    # Step 3: Fallback to manual mapping hints

    for python_problem in python_data:
        normalized_title = normalize_problem_title(python_problem.title)

        # Exact match
        if normalized_title in cpp_normalized_lookup:
            return create_exact_match()

        # Similarity matching
        best_match = find_best_similarity_match(normalized_title, cpp_data)
        if similarity_score > 0.3:
            return create_approximate_match()

        # Mark as missing implementation
        return create_missing_match()
```

**Complexity**: O(P × C) where P = Python problems, C = C++ problems
**Optimization**: Pre-computed normalized lookup tables reduce to O(P + C) for exact matches

### 2. Study Plan Generation Algorithm
Uses spaced repetition with difficulty-aware scheduling:

```python
def generate_2_week_plan(tasks, max_daily_hours=2.0):
    # Priority-based task sorting
    # Daily time budget allocation (70% new, 30% review)
    # Spaced repetition scheduling (3-7 day intervals)

    sorted_tasks = sort_by_priority_and_difficulty(tasks)

    for day in range(14):
        daily_plan = []
        time_budget = max_daily_hours * 60

        # Add review tasks (spaced repetition)
        add_review_tasks(daily_plan, review_queue, 0.3 * time_budget)

        # Add new tasks (remaining budget)
        add_new_tasks(daily_plan, sorted_tasks, remaining_budget)

        # Schedule reviews for completed new tasks
        schedule_future_reviews(daily_plan, review_queue)
```

**Features**:
- Adaptive difficulty scaling (easy: 15min, medium: 30min, hard: 45min)
- Review efficiency (70% of original time)
- Load balancing across 14-day cycles

### 3. Coverage Analysis Algorithm
Multi-dimensional gap detection:

```python
def check_a2z_coverage():
    # Section-level coverage (18 A2Z sections)
    # Problem-level coverage (478 total problems)
    # Implementation coverage (Python vs C++)

    gaps = {
        'missing_sections': find_sections_with_zero_problems(),
        'missing_python': find_problems_without_python_impl(),
        'low_coverage': find_sections_below_threshold(),
    }

    overall_score = calculate_weighted_coverage_score()
    recommendations = generate_prioritized_recommendations()
```

## Integration Points

### 1. External Dependencies
- **Rich/Typer**: CLI interface with colors and tables
- **Pydantic**: Data validation and serialization
- **Google Generative AI**: Future enhancement for content generation
- **uv**: Virtual environment and dependency management

### 2. File System Integration
- **JSONL Format**: Streaming-friendly for large datasets
- **Absolute Paths**: Cross-platform compatibility
- **Git Integration**: Version control for progress tracking

### 3. Extensibility Hooks
- **Plugin Architecture**: Add new content sources
- **Custom Schedulers**: Alternative study plan algorithms
- **Export Formats**: CSV/Anki/Notion integration points

## Performance Characteristics

### Scalability Limits
- **Index Size**: Tested up to 1000+ entries (current: 71)
- **Mapping Complexity**: O(P×C) algorithm scales to ~10K problems
- **Memory Usage**: <50MB for current dataset
- **Build Time**: Complete rebuild in <10 seconds

### Optimization Strategies
1. **Lazy Loading**: JSONL entries loaded on-demand
2. **Caching**: Pre-computed similarity matrices
3. **Incremental Updates**: Delta-only rebuilds for changed files
4. **Parallel Processing**: Multi-threaded repository analysis

## Security & Error Handling

### Data Validation
- **Schema Enforcement**: Pydantic models for all data structures
- **File Existence**: Validate all referenced paths
- **Encoding Safety**: UTF-8 with error handling for malformed files

### Error Recovery
- **Graceful Degradation**: Partial results when some files fail
- **Rollback Capability**: Backup previous data before rebuilds
- **User Feedback**: Rich error messages with actionable suggestions

### Privacy Considerations
- **Local Processing**: No data transmitted to external services
- **Path Sanitization**: Prevent directory traversal attacks
- **Minimal Logging**: No sensitive information in error logs

## Future Architecture Evolution

### Phase 2: System Design Integration
- **Knowledge Graph**: Neo4j for concept relationships
- **Content API**: RESTful service for multi-client access
- **Progress Tracking**: SQLite for temporal learning analytics

### Phase 3: ML/AI Enhancement
- **Difficulty Prediction**: ML models for problem complexity estimation
- **Personalized Scheduling**: Adaptive algorithms based on performance
- **Content Generation**: LLM-powered problem explanations and hints

### Phase 4: Multi-Domain Expansion
- **Microservices**: Domain-specific learning modules
- **Event Architecture**: Pub/sub for cross-domain progress correlation
- **Analytics Dashboard**: Real-time learning insights and trends

This design provides a solid foundation for systematic learning while maintaining the flexibility to evolve with changing requirements and expanding domains.