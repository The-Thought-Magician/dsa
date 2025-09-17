# TODO — Single Shot Plan

- Fix favicon 404 by serving `frontend/favicon.ico` at `/favicon.ico`.
- Stabilize AI chat: upgrade Gemini calls to 2.5 models, remove unsupported system role, map timeouts and 429s to HTTP errors.
- Ensure `/api/study-plan`, `/api/study-plan/today`, `/api/rebuild` work with current UI.
- Use the C++ repo for source data: extract all `.cpp` files, sanitize, and build `data/questions/questions.json`.
- Enrich questions with Gemini: generate statement, approach, theory, concepts, runnable Python solution, and real sample tests.
- Surface new fields in UI: approach, theory, concepts, and keep run/submit + solution reveal intact.
- Keep assets small, non-blocking overlay wired across fetch.

Commands

- Create venv and install: `uv venv && source .venv/bin/activate && uv pip install -e .`
- Extract dataset: `python scripts/extract_cpp_questions_batch.py`
- Enrich dataset: `python scripts/enrich_questions_with_gemini.py`
- Run server: `python run_server.py` then open `http://localhost:8000`

Acceptance

- Dashboard loads without console errors; favicon resolves.
- Questions list non-empty; detail shows statement, resources, samples.
- Approach/Theory/Concepts sections render when present.
- Run executes code against sample tests; Submit updates status.
- AI chat responds and respects guardrails; 429/timeout show friendly toasts.
- Study plan endpoints return data; rebuild triggers extractor/enricher.

Notes

- Use real data only; do not handcraft placeholder tests.
- Large enrichment runs may take time and quota; run once and commit dataset.
