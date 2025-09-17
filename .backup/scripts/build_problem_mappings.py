import os
import re
import json
import hashlib
from datetime import datetime


def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(8192)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def slug(text):
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip('-')


def normalize_cpp_name(name):
    base = os.path.splitext(name)[0]
    base = re.sub(r"^\d+\.?\s*", "", base)
    base = base.replace('_', ' ')
    return slug(base)


def normalize_py_name(path):
    base = os.path.splitext(os.path.basename(path))[0]
    base = base.replace('_', ' ').replace('-', ' ')
    return slug(base)


def load_python_db(db_path):
    if not os.path.isfile(db_path):
        return []
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_python_index(python_items):
    index = {}
    for item in python_items:
        title_slug = slug(item.get('title', ''))
        file_slug = normalize_py_name(item.get('file_path', ''))
        idx_slug = slug(item.get('id', ''))
        for s in {title_slug, file_slug, idx_slug}:
            if s:
                index.setdefault(s, []).append(item)
    return index


def scan_cpp(root):
    cpp_root = os.path.join(root, 'Strivers-A2Z-DSA-Sheet')
    out = []
    for dirpath, _, filenames in os.walk(cpp_root):
        for fn in filenames:
            if fn.lower().endswith('.cpp'):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root)
                out.append({'file': rel, 'name': fn})
    return out


def parse_cpp_metadata(path):
    data = {'approach': '', 'time_complexity': '', 'space_complexity': '', 'problem_statement': ''}
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f.readlines()[:300]]
    except Exception:
        return data
    for line in lines:
        low = line.lower()
        if not data['problem_statement'] and low.startswith('problem statement'):
            data['problem_statement'] = line.split(':', 1)[-1].strip()
        if not data['approach'] and low.startswith('approach'):
            data['approach'] = line.split(':', 1)[-1].strip()
        if not data['time_complexity'] and 'time complexity' in low:
            m = re.search(r'time complexity\s*[:\-]?\s*(.+)', line, re.I)
            if m:
                data['time_complexity'] = m.group(1).strip()
        if not data['space_complexity'] and 'space complexity' in low:
            m = re.search(r'space complexity\s*[:\-]?\s*(.+)', line, re.I)
            if m:
                data['space_complexity'] = m.group(1).strip()
    return data


def load_patterns(patterns_path):
    if not os.path.isfile(patterns_path):
        return {}
    with open(patterns_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def patterns_for_id(problem_id, patterns_map):
    res = []
    for pat, ids in patterns_map.items():
        if problem_id in ids:
            res.append(pat)
    return sorted(res)


def map_problems(root):
    python_db = load_python_db(os.path.join(root, 'data', 'problems_database.json'))
    py_index = build_python_index(python_db)
    patterns_map = load_patterns(os.path.join(root, 'data', 'patterns_index.json'))
    cpp_files = scan_cpp(root)
    mappings = []
    unmatched_cpp = []
    matched_ids = set()
    for entry in cpp_files:
        cpp_slug = normalize_cpp_name(entry['name'])
        candidates = py_index.get(cpp_slug, [])
        if not candidates:
            unmatched_cpp.append(entry['file'])
            mappings.append({
                'key': cpp_slug,
                'cpp': {
                    'file': entry['file'],
                    'hash': file_hash(os.path.join(root, entry['file']))
                },
                'python': None,
                'match_status': 'unmatched'
            })
            continue
        py_item = candidates[0]
        matched_ids.add(py_item['id'])
        mappings.append({
            'key': cpp_slug,
            'cpp': {
                'file': entry['file'],
                'hash': file_hash(os.path.join(root, entry['file']))
            },
            'python': {
                'id': py_item['id'],
                'file': py_item['file_path'],
                'hash': file_hash(os.path.join(root, 'striver-a2z-dsa', py_item['file_path'].split('/',1)[-1])) if os.path.isfile(os.path.join(root, py_item['file_path'])) else None,
                'title': py_item.get('title'),
                'difficulty': py_item.get('difficulty'),
                'category': py_item.get('category')
            },
            'patterns': patterns_for_id(py_item['id'], patterns_map),
            'match_status': 'matched'
        })
    python_unmapped = [p for p in python_db if p['id'] not in matched_ids]
    for p in python_unmapped:
        mappings.append({
            'key': slug(p.get('title','')) or slug(p['id']),
            'cpp': None,
            'python': {
                'id': p['id'],
                'file': p['file_path'],
                'hash': file_hash(os.path.join(root, p['file_path'])) if os.path.isfile(os.path.join(root, p['file_path'])) else None,
                'title': p.get('title'),
                'difficulty': p.get('difficulty'),
                'category': p.get('category')
            },
            'patterns': patterns_for_id(p['id'], patterns_map),
            'match_status': 'python_only'
        })
    return mappings


def main():
    root = os.getcwd()
    mappings = map_problems(root)
    out_path = os.path.join(root, 'data', 'problem_mappings.json')
    payload = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'count': len(mappings),
        'items': mappings
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    print('Saved', out_path)


if __name__ == '__main__':
    main()
