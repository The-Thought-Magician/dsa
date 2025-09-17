#!/usr/bin/env python3
"""
Coverage checker to validate A2Z completeness and identify gaps.
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

def load_jsonl(file_path: str) -> List[dict]:
    """Load JSONL file"""
    entries = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line.strip()))
    return entries

def check_a2z_coverage() -> dict:
    """Check A2Z course coverage and identify gaps"""
    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data"

    # Load data
    index_entries = load_jsonl(data_dir / "index.jsonl")
    mapping_entries = load_jsonl(data_dir / "mapping.jsonl")

    results = {
        'total_sections': len(index_entries),
        'coverage_by_section': {},
        'gaps': {
            'missing_sections': [],
            'missing_python': [],
            'missing_cpp': [],
            'low_coverage': []
        },
        'statistics': {
            'total_problems': len(mapping_entries),
            'exact_matches': 0,
            'approx_matches': 0,
            'missing_implementations': 0,
            'coverage_percentage': 0.0
        },
        'recommendations': []
    }

    # Analyze index coverage
    sections_with_issues = []
    step_coverage = {}

    for entry in index_entries:
        if 'sub' not in entry['id']:  # Only main sections
            step_num = entry['step_number']
            section_id = entry['id']
            section_title = entry['title']
            status = entry['status']

            problem_count = len(entry['related_problems'])
            local_file_count = len(entry['local_files'])

            coverage_info = {
                'id': section_id,
                'title': section_title,
                'status': status,
                'problem_count': problem_count,
                'file_count': local_file_count,
                'coverage_score': 0
            }

            # Calculate coverage score
            if status == 'available':
                coverage_info['coverage_score'] = 100
            elif status == 'partial':
                coverage_info['coverage_score'] = 50
            else:
                coverage_info['coverage_score'] = 0

            if problem_count == 0:
                sections_with_issues.append(section_title)
                results['gaps']['missing_sections'].append(section_title)

            if coverage_info['coverage_score'] < 50:
                results['gaps']['low_coverage'].append(section_title)

            step_coverage[step_num] = coverage_info
            results['coverage_by_section'][section_title] = coverage_info

    # Analyze mapping statistics
    for mapping in mapping_entries:
        status = mapping['status']
        if status == 'exact-match':
            results['statistics']['exact_matches'] += 1
        elif status == 'approx':
            results['statistics']['approx_matches'] += 1

        if mapping['python_file_path'] is None:
            results['gaps']['missing_python'].append(mapping['title'])

        if mapping['cpp_file_path'] is None:
            results['gaps']['missing_cpp'].append(mapping['title'])

    results['statistics']['missing_implementations'] = len(results['gaps']['missing_python'])

    # Calculate overall coverage percentage
    total_possible = len(mapping_entries) * 2  # Python + C++ for each problem
    total_available = 0
    for mapping in mapping_entries:
        if mapping['python_file_path']:
            total_available += 1
        if mapping['cpp_file_path']:
            total_available += 1

    results['statistics']['coverage_percentage'] = (total_available / total_possible) * 100 if total_possible > 0 else 0

    # Generate recommendations
    recommendations = []

    if results['statistics']['coverage_percentage'] < 90:
        recommendations.append(f"Overall coverage is {results['statistics']['coverage_percentage']:.1f}%. Focus on completing missing implementations.")

    if len(results['gaps']['missing_python']) > 50:
        recommendations.append(f"{len(results['gaps']['missing_python'])} problems missing Python implementations. Prioritize these for practice.")

    if sections_with_issues:
        recommendations.append(f"Sections with no mapped problems: {', '.join(sections_with_issues[:3])}")

    # Identify priority areas
    low_coverage_sections = [s for s in results['coverage_by_section'].values() if s['coverage_score'] < 70]
    if low_coverage_sections:
        section_names = [s['title'] for s in low_coverage_sections[:3]]
        recommendations.append(f"Priority sections needing attention: {', '.join(section_names)}")

    results['recommendations'] = recommendations

    return results

def print_coverage_report():
    """Print detailed coverage report"""
    print("🔍 A2Z DSA Coverage Analysis")
    print("=" * 50)

    results = check_a2z_coverage()

    # Overall statistics
    print(f"\n📊 Overall Statistics:")
    print(f"Total sections: {results['total_sections']}")
    print(f"Total problems: {results['statistics']['total_problems']}")
    print(f"Coverage percentage: {results['statistics']['coverage_percentage']:.1f}%")
    print(f"Exact matches: {results['statistics']['exact_matches']}")
    print(f"Approximate matches: {results['statistics']['approx_matches']}")
    print(f"Missing Python implementations: {results['statistics']['missing_implementations']}")

    # Coverage by section
    print(f"\n📋 Coverage by Section:")
    for section_title, info in results['coverage_by_section'].items():
        status_icon = "✅" if info['coverage_score'] == 100 else "⚠️" if info['coverage_score'] >= 50 else "❌"
        print(f"  {status_icon} {section_title:<40} | Score: {info['coverage_score']:3d}% | Problems: {info['problem_count']:3d} | Files: {info['file_count']:3d}")

    # Gap analysis
    print(f"\n🚨 Gap Analysis:")

    if results['gaps']['missing_sections']:
        print(f"Sections with no problems: {len(results['gaps']['missing_sections'])}")
        for section in results['gaps']['missing_sections'][:5]:
            print(f"  - {section}")

    if results['gaps']['low_coverage']:
        print(f"Low coverage sections: {len(results['gaps']['low_coverage'])}")
        for section in results['gaps']['low_coverage'][:5]:
            print(f"  - {section}")

    if results['gaps']['missing_python']:
        print(f"Problems missing Python solutions: {len(results['gaps']['missing_python'])}")
        if len(results['gaps']['missing_python']) <= 10:
            for problem in results['gaps']['missing_python']:
                print(f"  - {problem}")
        else:
            print(f"  (First 10 shown, {len(results['gaps']['missing_python']) - 10} more...)")
            for problem in results['gaps']['missing_python'][:10]:
                print(f"  - {problem}")

    # Recommendations
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")

    # Success criteria check
    print(f"\n✅ Success Criteria Check:")

    criteria = [
        ("100% A2Z sections represented", results['total_sections'] >= 15),
        ("Every section has problems linked", len(results['gaps']['missing_sections']) == 0),
        ("Coverage above 80%", results['statistics']['coverage_percentage'] >= 80.0),
        ("At least 300 problems mapped", results['statistics']['total_problems'] >= 300)
    ]

    all_passed = True
    for criterion, passed in criteria:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {criterion}")
        if not passed:
            all_passed = False

    print(f"\n🎯 Overall Status: {'PASS' if all_passed else 'NEEDS WORK'}")

def main():
    """Main coverage check function"""
    try:
        print_coverage_report()

        # Return exit code based on success criteria
        results = check_a2z_coverage()
        has_critical_gaps = (
            len(results['gaps']['missing_sections']) > 0 or
            results['statistics']['coverage_percentage'] < 80.0 or
            results['statistics']['total_problems'] < 300
        )

        return 1 if has_critical_gaps else 0

    except Exception as e:
        print(f"❌ Error during coverage check: {e}")
        return 1

if __name__ == "__main__":
    exit(main())