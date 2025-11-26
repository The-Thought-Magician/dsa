import argparse
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

from typing import Iterable, List, Dict

def load_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    env = Path(".env")
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "GEMINI_API_KEY":
                return v.strip()
    return ""

def coerce_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("\n", 1)[0]
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end+1])
        raise

def build_prompt(source_cpp: str) -> str:
    return textwrap.dedent(
        f"""
        You curate programming problems. Analyze the C++ file and return a compact JSON object with keys:
        statement_markdown, approach_markdown, theory_markdown, concepts, python_solution, starter_code, sample_tests, solution_markdown, topic_summary.

        Rules:
        - Output MUST be valid JSON only.
        - concepts: exactly 3 objects with name, summary, why_it_matters, practice_tips.
        - python_solution: runnable Python 3 reading stdin and printing stdout.
        - starter_code: minimal Python scaffold for the problem.
        - sample_tests: at least 3 realistic cases with id, input, output, explanation, matching python_solution.
        - Be concise and specific.

        Source:
        {source_cpp}
        """
    )

def extract_text(response) -> str:
    direct = getattr(response, "text", None)
    if direct:
        return direct
    parts: List[str] = []
    candidates = getattr(response, "candidates", []) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            piece = getattr(part, "text", None)
            if piece:
                parts.append(piece)
    return "\n".join(parts)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--validate", action="store_true")
    return parser.parse_args()


def call_model(model, prompt: str) -> Dict[str, object]:
    from google.api_core import exceptions as google_exceptions

    delays = [5, 10, 20]
    last_error = None
    for delay in delays:
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.5, "top_p": 0.8, "top_k": 40, "max_output_tokens": 2048},
                request_options={"timeout": 120},
            )
            text = extract_text(response)
            return coerce_json(text)
        except google_exceptions.ResourceExhausted as exc:
            last_error = exc
            time.sleep(delay)
        except google_exceptions.ServiceUnavailable as exc:
            last_error = exc
            time.sleep(delay)
        except google_exceptions.DeadlineExceeded as exc:
            last_error = exc
            time.sleep(delay)
        except google_exceptions.InternalServerError as exc:
            last_error = exc
            time.sleep(delay)
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    raise RuntimeError(str(last_error) if last_error else "Gemini request failed")


def run_python_solution(code: str, tests: Iterable[Dict[str, str]]) -> None:
    solutions_dir = Path("data/solutions")
    solutions_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        temp_path = Path(tmp.name)
    try:
        for test in tests:
            proc = subprocess.run(
                [sys.executable, str(temp_path)],
                input=test["input"],
                text=True,
                capture_output=True,
                timeout=6,
            )
            expected = test["output"].strip()
            actual = proc.stdout.strip()
            if proc.returncode != 0 or actual != expected:
                raise RuntimeError("Sample test mismatch")
    finally:
        temp_path.unlink(missing_ok=True)


def save_python_solution(identifier: str, code: str) -> str:
    solutions_dir = Path("data/solutions")
    solutions_dir.mkdir(parents=True, exist_ok=True)
    path = solutions_dir / f"{identifier}.py"
    path.write_text(code, encoding="utf-8")
    return path.as_posix()


def enrich_one(model, item: dict, validate: bool) -> dict:
    src_path = item.get("metadata", {}).get("source_file") or item.get("resources", [{}])[0].get("url", "").replace("file://", "")
    if not src_path:
        return item
    try:
        source_text = Path(src_path).read_text(encoding="utf-8")
    except Exception:
        return item
    prompt = build_prompt(source_text)
    data = call_model(model, prompt)
    if not isinstance(data, dict):
        return item
    out = dict(item)
    out["statement_markdown"] = data.get("statement_markdown", item.get("statement_markdown", ""))
    out["approach_markdown"] = data.get("approach_markdown")
    out["theory_markdown"] = data.get("theory_markdown")
    out["concepts"] = data.get("concepts")
    out["topic_summary"] = data.get("topic_summary")
    out["starter_code"] = data.get("starter_code", item.get("starter_code", ""))
    tests = data.get("sample_tests") or []
    normalized_tests = []
    for i, t in enumerate(tests, start=1):
        try:
            normalized_tests.append({
                "id": int(t.get("id", i)),
                "input": str(t.get("input", "")).rstrip("\n") + "\n",
                "output": str(t.get("output", "")).rstrip("\n") + "\n",
                "explanation": t.get("explanation") or None,
            })
        except Exception:
            continue
    if len(normalized_tests) < 3:
        raise RuntimeError("Not enough sample tests")
    out["sample_tests"] = normalized_tests
    if data.get("solution_markdown"):
        out["solution_markdown"] = data["solution_markdown"]
    meta = dict(out.get("metadata") or {})
    python_solution = data.get("python_solution")
    if not python_solution:
        raise RuntimeError("Missing python_solution")
    if validate:
        run_python_solution(python_solution, normalized_tests)
    solution_path = save_python_solution(out["id"], python_solution)
    meta["python_solution_path"] = solution_path
    meta.pop("needs_ai_generation", None)
    out["metadata"] = meta
    return out

def main():
    args = parse_args()
    key = load_key()
    if not key:
        raise SystemExit("GEMINI_API_KEY not set")
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel("models/gemini-2.5-pro")

    path = Path("data/questions/questions.json")
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"questions": []}
    items = data.get("questions", [])
    only_ids = set([ident.strip() for ident in args.only]) if args.only else None
    start_index = args.offset if args.offset else 0
    limit = args.limit if args.limit is not None else None
    updated = []
    processed = 0
    enriched_count = 0
    for index, item in enumerate(items):
        meta = item.get("metadata", {})
        needs = bool(meta.get("needs_ai_generation", False)) or any(
            (not t.get("input") or t.get("input").strip().startswith("#")) for t in item.get("sample_tests", [])
        )
        include = True
        if only_ids is not None and item["id"] not in only_ids:
            include = False
        if index < start_index:
            include = False
        if limit is not None and processed >= limit:
            include = False
        if needs and include:
            try:
                enriched = enrich_one(model, item, args.validate)
                updated.append(enriched)
                enriched_count += 1
            except Exception as exc:
                print(f"Failed to enrich {item['id']}: {exc}")
                updated.append(item)
            processed += 1
        else:
            updated.append(item)

    out = {"questions": updated}
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated {enriched_count} questions")

if __name__ == "__main__":
    main()
