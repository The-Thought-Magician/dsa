#!/usr/bin/env python3
"""
Build index.jsonl and mapping.jsonl files from analyzed data.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import re

@dataclass
class IndexEntry:
    """Represents a topic entry in the index"""
    id: str
    title: str
    path: str  # A2Z section/subsection path
    tags: List[str]
    source_links: List[str]
    related_problems: List[str]
    local_files: List[str]
    notes: str
    difficulty: Optional[str] = None
    step_number: int = 0
    status: str = "available"  # available, missing, partial

@dataclass
class MappingEntry:
    """Represents a cross-reference mapping"""
    problem_id: str
    title: str
    a2z_path: str
    links: List[str]
    python_file_path: Optional[str]
    cpp_file_path: Optional[str]
    status: str  # exact-match, approx, missing
    approach_summary: Optional[str]
    time_complexity: Optional[str]
    space_complexity: Optional[str]
    tags: List[str]

def normalize_problem_title(title: str) -> str:
    """Normalize problem titles for matching"""
    # Remove common prefixes/suffixes and normalize
    title = re.sub(r'^\d+\.?\s*', '', title)  # Remove leading numbers
    title = re.sub(r'\.py$|\.cpp$', '', title)  # Remove extensions
    title = title.replace('_', ' ').replace('-', ' ')
    title = re.sub(r'\s+', ' ', title).strip()
    return title.lower()

def find_matching_problems(python_data: List[dict], cpp_data: List[dict]) -> List[MappingEntry]:
    """Find and map matching problems between repositories"""
    mappings = []
    used_cpp = set()

    # Create lookup dictionaries
    cpp_by_normalized = {}
    for cpp in cpp_data:
        normalized = normalize_problem_title(cpp.get('problem_title', ''))
        if normalized not in cpp_by_normalized:
            cpp_by_normalized[normalized] = []
        cpp_by_normalized[normalized].append(cpp)

    # Map Python solutions
    for python in python_data:
        python_title = normalize_problem_title(python.get('problem_name', ''))
        python_path = python.get('file_path', '')

        # Find best C++ match
        best_cpp = None
        match_status = "missing"

        # Try exact match first
        if python_title in cpp_by_normalized:
            candidates = cpp_by_normalized[python_title]
            # Pick first unused candidate
            for candidate in candidates:
                if candidate['file_path'] not in used_cpp:
                    best_cpp = candidate
                    used_cpp.add(candidate['file_path'])
                    match_status = "exact-match"
                    break

        # Try partial match
        if not best_cpp:
            python_words = set(python_title.split())
            best_score = 0
            for normalized_cpp, candidates in cpp_by_normalized.items():
                cpp_words = set(normalized_cpp.split())
                # Calculate Jaccard similarity
                intersection = len(python_words & cpp_words)
                union = len(python_words | cpp_words)
                if union > 0:
                    score = intersection / union
                    if score > 0.3 and score > best_score:  # 30% similarity threshold
                        for candidate in candidates:
                            if candidate['file_path'] not in used_cpp:
                                best_cpp = candidate
                                used_cpp.add(candidate['file_path'])
                                match_status = "approx"
                                best_score = score
                                break

        # Create mapping entry
        problem_id = f"{python.get('step_section', '').replace(' ', '_').lower()}_{python.get('file_name', '').replace('.py', '')}"

        mapping = MappingEntry(
            problem_id=problem_id,
            title=python.get('problem_name', ''),
            a2z_path=python.get('step_section', ''),
            links=[],
            python_file_path=python_path,
            cpp_file_path=best_cpp.get('file_path') if best_cpp else None,
            status=match_status,
            approach_summary=best_cpp.get('approach') if best_cpp else None,
            time_complexity=best_cpp.get('time_complexity') if best_cpp else None,
            space_complexity=best_cpp.get('space_complexity') if best_cpp else None,
            tags=[]
        )
        mappings.append(mapping)

    # Add remaining C++ solutions that weren't mapped
    for cpp in cpp_data:
        if cpp['file_path'] not in used_cpp:
            problem_id = f"cpp_{cpp.get('section', '').replace('.', '_').replace(' ', '_').lower()}_{cpp.get('file_name', '').replace('.cpp', '')}"

            mapping = MappingEntry(
                problem_id=problem_id,
                title=cpp.get('problem_title', ''),
                a2z_path=f"{cpp.get('section', '')}/{cpp.get('subsection', '')}",
                links=[],
                python_file_path=None,
                cpp_file_path=cpp['file_path'],
                status="missing",  # Missing Python implementation
                approach_summary=cpp.get('approach'),
                time_complexity=cpp.get('time_complexity'),
                space_complexity=cpp.get('space_complexity'),
                tags=[]
            )
            mappings.append(mapping)

    return mappings

def build_index_from_structure(a2z_structure: List[dict], mappings: List[MappingEntry]) -> List[IndexEntry]:
    """Build index entries from A2Z structure and mappings"""
    index_entries = []

    # Group mappings by section
    mappings_by_section = {}
    for mapping in mappings:
        section_key = mapping.a2z_path.split('/')[0] if '/' in mapping.a2z_path else mapping.a2z_path
        if section_key not in mappings_by_section:
            mappings_by_section[section_key] = []
        mappings_by_section[section_key].append(mapping)

    # Create index entries for each A2Z section
    for section in a2z_structure:
        section_id = section['id']
        section_title = section['title']
        step_number = section['step_number']

        # Find related problems
        python_section = section.get('python_section', '')
        cpp_section = section.get('cpp_section', '')

        related_problems = []
        local_files = []

        # Get mappings for this section
        section_mappings = mappings_by_section.get(python_section, [])

        for mapping in section_mappings:
            related_problems.append(mapping.problem_id)
            if mapping.python_file_path:
                local_files.append(mapping.python_file_path)
            if mapping.cpp_file_path:
                local_files.append(mapping.cpp_file_path)

        # Determine status
        python_count = section.get('python_count', 0)
        cpp_count = section.get('cpp_count', 0)

        if python_count > 0 and cpp_count > 0:
            status = "available"
        elif python_count > 0 or cpp_count > 0:
            status = "partial"
        else:
            status = "missing"

        # Create index entry
        entry = IndexEntry(
            id=section_id,
            title=section_title,
            path=f"Step {step_number:02d} - {section_title}",
            tags=section.get('topics', []),
            source_links=[section.get('source_url', '')],
            related_problems=related_problems,
            local_files=local_files,
            notes=f"Python: {python_count} files, C++: {cpp_count} files",
            difficulty=None,  # Will be inferred from problems
            step_number=step_number,
            status=status
        )
        index_entries.append(entry)

        # Create entries for subsections if they exist
        for i, subsection in enumerate(section.get('subsections', [])):
            subsection_id = f"{section_id}_sub{i+1}"
            subsection_entry = IndexEntry(
                id=subsection_id,
                title=f"{section_title} - {subsection}",
                path=f"Step {step_number:02d} - {section_title}/{subsection}",
                tags=section.get('topics', []),
                source_links=[section.get('source_url', '')],
                related_problems=[],  # Would need more detailed mapping
                local_files=[],
                notes=f"Subsection of {section_title}",
                difficulty=None,
                step_number=step_number,
                status="available"
            )
            index_entries.append(subsection_entry)

    return index_entries

def main():
    """Build index and mapping files"""
    print("🏗️  Building index.jsonl and mapping.jsonl...")

    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data"

    # Load analyzed data
    with open(data_dir / "python_analysis.json", 'r') as f:
        python_data = json.load(f)

    with open(data_dir / "cpp_analysis.json", 'r') as f:
        cpp_data = json.load(f)

    with open(data_dir / "a2z_structure.json", 'r') as f:
        a2z_structure = json.load(f)

    # Build mappings
    print("🔗 Creating cross-reference mappings...")
    mappings = find_matching_problems(python_data, cpp_data)

    # Build index
    print("📋 Building topic index...")
    index_entries = build_index_from_structure(a2z_structure, mappings)

    # Convert to JSON format and save as JSONL
    print("💾 Saving files...")

    # Save index.jsonl
    with open(data_dir / "index.jsonl", 'w') as f:
        for entry in index_entries:
            entry_dict = {
                'id': entry.id,
                'title': entry.title,
                'path': entry.path,
                'tags': entry.tags,
                'source_links': entry.source_links,
                'related_problems': entry.related_problems,
                'local_files': entry.local_files,
                'notes': entry.notes,
                'difficulty': entry.difficulty,
                'step_number': entry.step_number,
                'status': entry.status
            }
            f.write(json.dumps(entry_dict) + '\n')

    # Save mapping.jsonl
    with open(data_dir / "mapping.jsonl", 'w') as f:
        for mapping in mappings:
            mapping_dict = {
                'problem_id': mapping.problem_id,
                'title': mapping.title,
                'a2z_path': mapping.a2z_path,
                'links': mapping.links,
                'python_file_path': mapping.python_file_path,
                'cpp_file_path': mapping.cpp_file_path,
                'status': mapping.status,
                'approach_summary': mapping.approach_summary,
                'time_complexity': mapping.time_complexity,
                'space_complexity': mapping.space_complexity,
                'tags': mapping.tags
            }
            f.write(json.dumps(mapping_dict) + '\n')

    # Print statistics
    print(f"\n📊 Build Statistics:")
    print(f"Index entries: {len(index_entries)}")
    print(f"Mapping entries: {len(mappings)}")

    # Mapping statistics
    exact_matches = len([m for m in mappings if m.status == "exact-match"])
    approx_matches = len([m for m in mappings if m.status == "approx"])
    missing_python = len([m for m in mappings if m.status == "missing" and m.python_file_path is None])
    missing_cpp = len([m for m in mappings if m.status == "missing" and m.cpp_file_path is None])

    print(f"\n🔗 Mapping Statistics:")
    print(f"Exact matches: {exact_matches}")
    print(f"Approximate matches: {approx_matches}")
    print(f"Missing Python solutions: {missing_python}")

    # Index status statistics
    available = len([e for e in index_entries if e.status == "available"])
    partial = len([e for e in index_entries if e.status == "partial"])
    missing = len([e for e in index_entries if e.status == "missing"])

    print(f"\n📋 Index Status:")
    print(f"Fully available: {available}")
    print(f"Partially available: {partial}")
    print(f"Missing: {missing}")

    print(f"\n✅ Files created:")
    print(f"  - data/index.jsonl")
    print(f"  - data/mapping.jsonl")

if __name__ == "__main__":
    main()