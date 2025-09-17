import argparse
import json
import os
import re
import sys
from datetime import datetime

import requests


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def read_text(url: str, timeout: int = 30) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\-\_ ]+", "", value)
    value = value.strip().lower().replace(" ", "-")
    value = re.sub(r"-+", "-", value)
    return value


def extract_steps(markdown_text: str) -> list:
    steps = []
    pattern = re.compile(r"^(Step\s+(\d+)\s*:\s*(.+))$", re.IGNORECASE | re.MULTILINE)
    for m in pattern.finditer(markdown_text):
        full = m.group(1).strip()
        step_id = int(m.group(2))
        title = m.group(3).strip()
        steps.append({"id": step_id, "title": title, "raw": full})
    return steps


def scan_local_solutions(repo_root: str) -> dict:
    base = os.path.join(repo_root, "striver-a2z-dsa")
    steps = []
    if not os.path.isdir(base):
        return {"steps": steps}
    for name in sorted(os.listdir(base)):
        path = os.path.join(base, name)
        if not os.path.isdir(path):
            continue
        m = re.match(r"^Step\s+(\d+)[^\-]*-\s*(.+)$", name)
        if not m:
            continue
        step_id = int(m.group(1))
        step_title = m.group(2).strip()
        items = []
        for fn in sorted(os.listdir(path)):
            fp = os.path.join(path, fn)
            if os.path.isdir(fp):
                continue
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (".py", ".ipynb"):
                continue
            key = os.path.splitext(fn)[0]
            items.append(
                {
                    "key": key,
                    "file": os.path.relpath(fp, repo_root),
                    "ext": ext,
                }
            )
        steps.append(
            {
                "id": step_id,
                "title": step_title,
                "items": items,
                "count": len(items),
            }
        )
    return {"steps": steps}


def build_manifest(overview_steps: list, local_map: dict) -> dict:
    local_by_id = {s["id"]: s for s in local_map.get("steps", [])}
    steps = []
    for s in overview_steps:
        sid = s["id"]
        merged = {
            "id": sid,
            "title": s["title"],
            "local_items": local_by_id.get(sid, {}).get("items", []),
            "local_count": local_by_id.get(sid, {}).get("count", 0),
        }
        steps.append(merged)
    steps.sort(key=lambda x: x["id"])
    return {
        "source": "takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "steps": steps,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=(
            "https://r.jina.ai/http://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/"
        ),
    )
    parser.add_argument("--out", default="docs/striver-a2z")
    parser.add_argument("--repo-root", default=os.getcwd())
    args = parser.parse_args()

    ensure_dir(args.out)
    pages_dir = os.path.join(args.out, "pages")
    ensure_dir(pages_dir)

    text = read_text(args.url)
    overview_path = os.path.join(pages_dir, "a2z-sheet.md")
    with open(overview_path, "w", encoding="utf-8") as f:
        f.write(text)

    overview_steps = extract_steps(text)
    local_map = scan_local_solutions(args.repo_root)
    manifest = build_manifest(overview_steps, local_map)

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    with open(os.path.join(args.out, "local_solutions.json"), "w", encoding="utf-8") as f:
        json.dump(local_map, f, indent=2, ensure_ascii=False)

    progress_path = os.path.join(args.out, "progress.csv")
    if not os.path.exists(progress_path):
        with open(progress_path, "w", encoding="utf-8") as f:
            f.write("step_id,problem_key,status,attempts,notes\n")

    print("Saved:", overview_path)
    print("Saved:", os.path.join(args.out, "manifest.json"))
    print("Saved:", os.path.join(args.out, "local_solutions.json"))
    print("Saved:", progress_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)

