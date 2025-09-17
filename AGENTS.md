# Repository Guidelines

## Project Structure & Module Organization
The Python backend lives in `api/`, with `main.py` bootstrapping FastAPI, request models in `models.py`, and feature-specific routers under `api/routers/`. CLI entrypoints are provided by `main.py` (Typer commands) and `run_server.py` for the web server. Static web assets sit in `frontend/` — the HTML shell in `frontend/index.html`, component fragments under `frontend/components/`, and Bootstrap/Chart.js helpers in `frontend/assets/{css,js}/`. Automation utilities reside in `scripts/` (index builders, coverage checks, study-plan generators). Generated datasets (`data/*.json*`) and scraped reference repositories (`striver-a2z-dsa/`, `Strivers-A2Z-DSA-Sheet/`) should be treated as derived artifacts; never edit them manually.

## Build, Test, and Development Commands
- `uv venv && source .venv/bin/activate` — create and enter the project virtualenv.
- `uv pip install -e .` — install backend and CLI in editable mode with FastAPI dependencies.
- `python main.py init` — rebuild local indexes and datasets; run after changing scripts or upstream repos.
- `python run_server.py` — start the FastAPI + static frontend server on `http://localhost:8000`.
- `python main.py list --section "arrays"` — inspect CLI output while iterating on topics.
- `python scripts/coverage_checker.py` — recompute coverage metrics surfaced in the dashboard.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, descriptive type hints, and `Path` utilities for filesystem access. Prefer explicit returns over implicit fall-through in service methods. Router modules should expose a `router` object named after the feature (`topics_router`, etc.). Frontend scripts stay ES modules in `frontend/assets/js/`; name files after the view they serve (`dashboard.js`, `coverage.js`). Keep HTML components lowercase with hyphenated filenames.

## Testing Guidelines
A formal test suite is still emerging; use `pytest` when adding automated checks and place them under a new `tests/` or feature-level `api/tests/` package with `test_<feature>.py` filenames. Until that exists, rely on CLI sanity checks (`python main.py stats`, `python main.py gaps`) and the coverage script before opening a PR. Document any manual verification steps in the PR description so others can replicate quickly.

## Commit & Pull Request Guidelines
Write commits in imperative mood with an optional scope prefix, e.g., `feat: add coverage endpoint` or `fix(api): handle empty mappings`. Keep PRs focused, link related issues, and include screenshots/GIFs for frontend updates or cURL snippets for API changes. Every PR should call out data-regeneration commands that reviewers must run and highlight any schema changes to the generated JSON assets.
