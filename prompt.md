Master brief: build a fast, complete learning system starting with Striver’s A2Z DSA (Python-first), then System Design, ML/DL with LLM basics, and core React/JS/TS. Use my local repos and produce a practical plan, content index, and runnable helpers.

Scope and priorities (ordered):
1) DSA in Python (Striver A2Z coverage with zero topic gaps)
2) System Design
3) ML + DL basics with a clear map of LLM architecture fundamentals for a junior AI engineer
4) Frontend foundations: React + JS/TS core concepts

Primary inputs:
- Course: https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/
- Local Python solutions: `striver-a2z-dsa/`
- Additional topics: `additional-content.md`
- A second repo exists with items of the form: Problem Statement, Approach, Code (C++), Time/Space complexity. Map those to the Python solutions when relevant.

Operating constraints and tools:
- Environment: Linux + zsh; when providing commands, make them zsh-friendly.
- Use Python with a virtual environment managed via `uv`.
- If you need AI assistance (summarize/generate/extract), use Gemini (googleapis/python-genai) with the API key from `.env`. Prefer the current best Gemini model.
- Respect site terms: do not scrape beyond robots/TOS; prefer metadata capture (URLs/titles/IDs) and short notes. Only download content when allowed.
- Be autonomous, but ask at most one blocking clarifying question if necessary; otherwise proceed with reasonable defaults and document assumptions.

Deliverables and acceptance criteria:
- plan.md: concrete milestones, weekly cadence, time estimates, and success metrics. Include checkpoints for each priority area.
- design.md: system architecture for the learning workflow, data model for topic/problem indexing, and how scripts/automation fit together.
- done.md: rolling changelog and coverage report (topics covered %, problems linked, tests run, QA notes).
- data/index.jsonl (or similar): canonical index of all A2Z topics with fields: id, title, path (A2Z section/subsection), tags, source links, related problems, local files, notes.
- data/mapping.jsonl: crosswalk entries mapping “Question/Approach/C++/Complexities” repo items to local Python solutions; include: problem_id, title, a2z_path, links, python_file_path, status (exact-match|approx|missing), approach_summary, time/space.
- scripts/: small, robust helpers (Python) to:
  - build the index from inputs (manual + automated, where allowed)
  - validate coverage (no missing A2Z topics)
  - generate a spaced practice schedule
- README.md updates: how to run scripts and interpret outputs.

Coverage and quality gates (must pass):
- 100% of A2Z sections/rows represented in the index with IDs, titles, and links.
- Every indexed problem cross-referenced to at least one local artifact (Python file or TODO placeholder).
- Lint/type check passes (if types used). Scripts execute without errors in a fresh venv.
- A simple smoke test demonstrating: index build → coverage report → sample study plan.

Execution plan (agent workflow):
1) Inventory and analysis
	- Parse `striver-a2z-dsa/` to list available Python solutions.
	- Parse the “Question/Approach/C++/Complexities” repo structure and extract metadata.
	- Read `additional-content.md` to expand scope items.
	- Produce a gap analysis vs A2Z sheet; enumerate missing topics/problems.
2) Data model + index
	- Propose a lean schema (JSONL) for topics and mappings.
	- Generate initial `data/index.jsonl` covering the full A2Z outline.
3) Cross-mapping
	- Link each A2Z topic to: local Python solutions, external source links, and alternative C++ references where available.
	- Mark approximate matches; open TODOs for missing solutions.
4) Automation
	- Add `scripts/` to build index, check coverage, and draft a spaced practice plan (by difficulty and recency).
	- Use `uv` for environment management. Include make-like tasks if helpful.
5) Artifacts & docs
	- Write `plan.md`, `design.md`, `done.md`.
	- Update `README.md` with minimal usage.
6) Report
	- Summarize coverage %, blockers, and next steps.

Engineering ground rules:
- Keep changes minimal, focused, and reproducible. Prefer small PR-sized commits with clear messages.
- Provide commands as single-line zsh entries inside fenced blocks when necessary.
- Validate after substantive edits: quick lint/run/tests and include a brief PASS/FAIL note.
- If something cannot be automated ethically, create a manual step with a checklist.

Virtual environment and tooling (use these exact conventions):
- Use `uv` to create and run the venv; pin packages in `pyproject.toml` when adding dependencies.
- Prefer: requests/httpx, BeautifulSoup/lxml for parsing; pydantic/attrs for structured data; rich/typer for CLI niceties (optional); python-genai for Gemini.

Minimal commands the agent may use (Linux + zsh):
```sh
# Create venv and run
uv venv
source .venv/bin/activate
uv pip install -e .

# If adding tools
uv pip install beautifulsoup4 lxml httpx typer rich pydantic python-genai
```

Acceptance tests the agent should implement:
- Build index from zero and output counts by section; FAIL if any A2Z section has 0 items.
- Cross-map check: FAIL if >0 unmapped local Python solutions or >0 unindexed A2Z entries.
- Generate a 2-week DSA study plan with daily tasks ≤ 2 hours including spaced review.

Reporting cadence:
- After each 3–5 automation steps or when touching >3 files, post a compact progress update: what changed, key results, next step.
- Keep todos visible and update statuses immediately upon completion.

Assumptions and clarifications:
- If `AGENTS.md` exists, follow it strictly. If not, infer a minimal agent contract from this brief and document it in `design.md`.
- If any URLs change or content is paginated, prefer resilient scraping (again: respect TOS) and fallback to manual seeding.

Creativity and extras (nice-to-haves):
- Lightweight CLI in `main.py` to: list topics, show gaps, and print today’s plan.
- Export flashcards (CSV/JSON) for spaced repetition tools.
- Optional simple dashboard using textual/rich to visualize coverage and streaks.

Start with DSA (Phase 1) and deliver a first PASS with: plan.md, design.md, done.md, index + mapping skeletons, and a working coverage checker. Then iterate.


Quick variants you can copy-paste elsewhere

1) Lightning version (one paragraph):
“Autonomously build a Python-first learning system covering Striver A2Z end-to-end with zero topic gaps: index all topics (JSONL), map each to my local `striver-a2z-dsa/` Python solutions and to a second repo’s C++ references, add scripts (uv-managed venv) to build index, verify coverage, and output a 2-week study plan; write plan.md/design.md/done.md, update README with run steps, and report progress after each 3–5 actions. Use Gemini when helpful, respect website TOS, and provide a smoke test that builds the index and prints coverage.”

2) Single-task DSA indexer:
“Create `data/index.jsonl` covering every row in Striver A2Z (IDs, titles, section path, tags, source links). Add `scripts/build_index.py` and a coverage checker. Use uv venv, Python, and short zsh commands. Briefly report coverage % and missing items.”

3) Mapping-only:
“Generate `data/mapping.jsonl` linking A2Z topics to my local Python solutions and to a C++-based repo (Problem/Approach/Code/Complexities). Mark status exact/approx/missing, include file paths and source links. Output a gap report.”

4) Daily study plan:
“From the index and mappings, output a 14-day, ≤2 hr/day plan mixing new topics and spaced reviews by difficulty. Include 1–2 problems per topic and link to local Python files.”

Success = complete A2Z coverage with actionable daily plans, verified mappings, and runnable helpers—delivered fast and clean.