# Learning System Design

- Goal: fast, comprehensive prep across DSA (Python) → System Design → ML/DL/LLM → Frontend.
- Source of truth: Striver A2Z sheet and additional-content.md links.
- Output: local manifest + offline pages + structured learning path with checkpoints.

Data Pipeline
- Fetch Striver A2Z sheet page and extract sections, topics, and problem links.
- Persist `docs/striver-a2z/manifest.json` with normalized topics and items.
- Cache raw HTML under `docs/striver-a2z/pages/{slug}.html` for offline study.
- Map topics to local solutions in `striver-a2z-dsa/` by filename heuristics.

Structure
- `plan.md` at repo root for active checklist.
- `docs/design.md` for system and course design.
- `docs/done.md` for session summaries and deviations.
- `docs/striver-a2z/` to store manifest and cached pages.

Script
- `scripts/fetch_striver_a2z.py` using `requests`, `beautifulsoup4`, `lxml`.
- Inputs: course URL, output directory.
- Outputs: manifest.json, cached HTML, simple mapping to local solutions.

Learning Path: DSA in Python
- Order: Basics → Arrays → Binary Search → Strings → Linked List → Recursion → Bit Manipulation → Stacks/Queues → Sliding Window/Two Pointers → Heaps → Greedy → Trees/BST → Graphs → DP → Tries.
- For each topic: watch Striver video if linked, read notes, solve core set, then mixed practice.
- Checkpoints: topic quiz, 8–12 curated problems, 1 mixed mock.
- Timebox: 4–6 hrs/day; topic cadence 1–3 days depending on depth.

Progress Tracking
- Use `manifest.json` ids as keys in a progress CSV (`docs/striver-a2z/progress.csv`).
- Mark statuses: todo, in_progress, solved, revise; record attempts and notes.
- Optional CLI later: list next items, mark done, filter by tag.

Extensibility
- Add curricula for System Design, ML/DL/LLM, Frontend to the same manifest format.
- Integrate `additional-content.md` as supplemental resources tagged per topic.

DSA Fast-Track Plan
- Week 1: Basics, Arrays core patterns (prefix/suffix, hashing, two pointers).
- Week 2: Binary Search on arrays and answer space; Strings basics and hashing.
- Week 3: Linked List ops; Stack/Queue; Sliding Window and Two Pointers drills.
- Week 4: Recursion fundamentals; Backtracking; Bit manipulation techniques.
- Week 5: Trees traversals, views, LCA; Binary Search Trees operations.
- Week 6: Heaps and priority problems; Greedy patterns; Graph traversal and shortest paths.
- Week 7: DP patterns (1D/2D, subsequences, knapsack, DP on trees); Tries.

Daily Loop

Problem Mapping
- Build cross reference between C++ reference solutions and local Python implementations.
- Script: scripts/build_problem_mappings.py outputs data/problem_mappings.json.
- Key fields: key, cpp.file, python.file, difficulty, category, patterns, match_status.
- Unmatched entries guide coverage gaps prioritization.

Ingestion Pipeline Extension
- Extend manifest with additional-content.md resources tagged per pattern.
- Normalize resource types: article, video, repo.
- Store in docs/resources.json for future UI consumption.

Coverage Gap Strategy
- Compute unmatched ratios per step from problem_mappings.json.
- Prioritize filling gaps in core interview patterns (Arrays, Binary Search, DP, Graphs, Trees, Sliding Window).
- Add remaining high-yield problems before advanced niche topics.

Planned CLI (Deferred)
- List next unsolved high-priority problems.
- Mark progress status transitions.
- Summarize daily streak metrics.
- 45m concept review, 3–5 problems mixed difficulty, 15m reflection.
- Track attempts in `docs/striver-a2z/progress.csv` with statuses.
- Target 8–12 problems per day; 1 mock every 3 days.
