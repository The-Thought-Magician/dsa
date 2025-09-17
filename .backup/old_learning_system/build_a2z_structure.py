#!/usr/bin/env python3
"""
Build comprehensive A2Z DSA course structure by mapping Python and C++ repos.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class A2ZSection:
    """Represents a section in the A2Z course"""
    id: str
    title: str
    step_number: int
    python_section: Optional[str] = None
    cpp_section: Optional[str] = None
    subsections: List[str] = None
    total_problems: int = 0
    python_count: int = 0
    cpp_count: int = 0
    topics: List[str] = None
    source_url: str = "https://takeuforward.org/strivers-a2z-dsa-course/strivers-a2z-dsa-course-sheet-2/"

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []
        if self.topics is None:
            self.topics = []

def create_a2z_structure() -> List[A2ZSection]:
    """Create the complete A2Z structure mapping both repositories"""

    sections = [
        A2ZSection(
            id="step01_basics",
            title="Learn the basics",
            step_number=1,
            python_section="Step 01 - Basics",
            cpp_section="01.Arrays",  # Some basics concepts overlap
            topics=["Variables", "Data Types", "I/O", "Conditionals", "Loops", "Functions", "Patterns", "Recursion Basics", "Hashing", "Math"]
        ),
        A2ZSection(
            id="step02_sorting",
            title="Learn Important Sorting Techniques",
            step_number=2,
            python_section="Step 02 - Sorting Techniques",
            cpp_section=None,  # Not directly mapped in C++ repo
            topics=["Selection Sort", "Bubble Sort", "Insertion Sort", "Merge Sort", "Quick Sort", "Recursive Sorting"]
        ),
        A2ZSection(
            id="step03_arrays",
            title="Solve Problems on Arrays",
            step_number=3,
            python_section="Step 03 - Arrays",
            cpp_section="01.Arrays",
            subsections=["Easy", "Medium", "Hard"],
            topics=["Array Manipulation", "Two Pointers", "Sliding Window", "Prefix Sum", "Array Rotation", "Subarray Problems"]
        ),
        A2ZSection(
            id="step04_binary_search",
            title="Binary Search",
            step_number=4,
            python_section="Step 04 - Binary Search",
            cpp_section="02.Binary Search",
            subsections=["1D Arrays", "2D Arrays", "Search Space"],
            topics=["Basic Binary Search", "Lower/Upper Bound", "Search in Rotated Array", "Peak Element", "Square Root", "Aggressive Cows"]
        ),
        A2ZSection(
            id="step05_strings",
            title="Strings",
            step_number=5,
            python_section="Step 05 + 18 - Strings",
            cpp_section="03.Strings",
            subsections=["Easy", "Medium", "Hard"],
            topics=["String Manipulation", "Pattern Matching", "Palindromes", "Anagrams", "String Compression", "KMP Algorithm"]
        ),
        A2ZSection(
            id="step06_linked_list",
            title="Learn LinkedList",
            step_number=6,
            python_section="Step 06 - Linked List",
            cpp_section="04.Linked List",
            subsections=["Single LL", "Doubly LL", "Medium Problems", "Hard Problems"],
            topics=["LL Creation", "Traversal", "Insertion", "Deletion", "Reversal", "Merge", "Detect Cycle", "Clone with Random"]
        ),
        A2ZSection(
            id="step07_recursion",
            title="Recursion",
            step_number=7,
            python_section="Step 07 - Recursion",
            cpp_section="05.Recursion",
            subsections=["Get Strong Hold", "Subsequences Pattern", "Try All Combos"],
            topics=["Basic Recursion", "Subsequences", "Combinations", "Permutations", "N-Queens", "Sudoku Solver"]
        ),
        A2ZSection(
            id="step08_bit_manipulation",
            title="Bit Manipulation",
            step_number=8,
            python_section="Step 08 - Bit Manipulation",
            cpp_section="06.Bit Manipulation",
            subsections=["Learn Bits", "Interview Problems", "Advanced Maths"],
            topics=["Bit Operations", "XOR Properties", "Set/Clear/Toggle Bits", "Count Set Bits", "Power of 2", "Subset Generation"]
        ),
        A2ZSection(
            id="step09_stacks_queues",
            title="Stacks and Queues",
            step_number=9,
            python_section="Step 09 - Stacks Queues",
            cpp_section="07.Stack and Queues",
            subsections=["Learning", "Infix/Postfix/Prefix", "Monotonic Stack/Queue", "Implementation"],
            topics=["Stack Operations", "Queue Operations", "Expression Conversion", "Next Greater Element", "Sliding Window Maximum"]
        ),
        A2ZSection(
            id="step10_sliding_window",
            title="Sliding Window Two Pointer Combined Problems",
            step_number=10,
            python_section="Step 10 - Sliding Window",
            cpp_section="08. Sliding Window",
            subsections=["Medium Problems", "Hard Problems"],
            topics=["Fixed Size Window", "Variable Size Window", "Two Pointers", "Substring Problems", "Subarray Problems"]
        ),
        A2ZSection(
            id="step11_heaps",
            title="Heaps",
            step_number=11,
            python_section="Step 11 - Heaps",
            cpp_section="09. Heaps",
            subsections=["Learning", "Medium Problems", "Hard Problems"],
            topics=["Priority Queue", "Heap Operations", "Kth Largest/Smallest", "Merge K Lists", "Median from Stream"]
        ),
        A2ZSection(
            id="step12_greedy",
            title="Greedy Algorithms",
            step_number=12,
            python_section="Step 12 - Greedy Algorithm",
            cpp_section="10. Greedy Approach",
            subsections=["Easy", "Medium"],
            topics=["Activity Selection", "Fractional Knapsack", "Job Sequencing", "Huffman Coding", "Optimal Merge Pattern"]
        ),
        A2ZSection(
            id="step13_binary_trees",
            title="Binary Trees",
            step_number=13,
            python_section="Step 13 + 14 - Trees + BST",
            cpp_section="11. Binary Trees",
            subsections=["Traversals", "Medium Problems", "Hard"],
            topics=["Tree Traversals", "Level Order", "Views", "Diameter", "LCA", "Serialize/Deserialize"]
        ),
        A2ZSection(
            id="step14_binary_search_trees",
            title="Binary Search Trees",
            step_number=14,
            python_section="Step 13 + 14 - Trees + BST",
            cpp_section="12. Binary Search Trees",
            subsections=["Concept", "Practice Problems"],
            topics=["BST Properties", "Search/Insert/Delete", "Inorder Successor", "Validate BST", "Convert to DLL"]
        ),
        A2ZSection(
            id="step15_graphs",
            title="Graphs",
            step_number=15,
            python_section="Step 15 - Graphs",
            cpp_section="13. Graphs",
            subsections=["Learning", "Traversal Problems", "Topo Sort", "Shortest Path", "MST", "Other Algorithms"],
            topics=["Graph Representation", "BFS/DFS", "Topological Sort", "Dijkstra", "Floyd Warshall", "Union Find", "MST Algorithms"]
        ),
        A2ZSection(
            id="step16_dynamic_programming",
            title="Dynamic Programming",
            step_number=16,
            python_section="Step 16 - Dynamic Programming",
            cpp_section="14. Dynamic Programming",
            subsections=["Intro to DP", "1D DP", "2D DP", "DP on Subsequences", "DP on Strings", "DP on Stocks", "DP on LIS", "DP on Partition", "DP on Squares"],
            topics=["Memoization", "Tabulation", "LCS", "LIS", "Knapsack", "Edit Distance", "Matrix Chain", "Stock Problems", "Partition Problems"]
        ),
        A2ZSection(
            id="step17_tries",
            title="Tries",
            step_number=17,
            python_section="Step 17 - Tries",
            cpp_section="15. Tries",
            subsections=["Theory", "Problems"],
            topics=["Trie Construction", "Search", "Prefix Count", "Word Break", "Maximum XOR"]
        ),
        A2ZSection(
            id="step18_strings_hard",
            title="Strings [Advanced]",
            step_number=18,
            python_section="Step 05 + 18 - Strings",  # Combined with step 5
            cpp_section="16. Strings (Hard)",
            subsections=["Hard"],
            topics=["KMP Algorithm", "Z Algorithm", "Rolling Hash", "Manacher's Algorithm", "Suffix Array"]
        )
    ]

    return sections

def main():
    """Build and save A2Z structure"""
    print("🏗️  Building A2Z DSA course structure...")

    # Load analysis data
    base_path = Path(__file__).parent.parent
    data_dir = base_path / "data"

    with open(data_dir / "python_analysis.json", 'r') as f:
        python_data = json.load(f)

    with open(data_dir / "cpp_analysis.json", 'r') as f:
        cpp_data = json.load(f)

    # Create structure
    sections = create_a2z_structure()

    # Count problems per section
    python_counts = {}
    for item in python_data:
        section = item["step_section"]
        python_counts[section] = python_counts.get(section, 0) + 1

    cpp_counts = {}
    for item in cpp_data:
        section_key = f"{item['section']}"
        cpp_counts[section_key] = cpp_counts.get(section_key, 0) + 1

    # Update sections with counts
    for section in sections:
        if section.python_section:
            section.python_count = python_counts.get(section.python_section, 0)

        if section.cpp_section:
            section.cpp_count = cpp_counts.get(section.cpp_section, 0)

        section.total_problems = section.python_count + section.cpp_count

    # Save structure
    with open(data_dir / "a2z_structure.json", 'w') as f:
        json.dump([asdict(section) for section in sections], f, indent=2)

    # Print summary
    print(f"\n📊 A2Z Structure Summary:")
    print(f"Total sections: {len(sections)}")

    total_python = sum(s.python_count for s in sections)
    total_cpp = sum(s.cpp_count for s in sections)

    print(f"Python solutions mapped: {total_python}")
    print(f"C++ solutions mapped: {total_cpp}")

    print(f"\n📋 Section breakdown:")
    for section in sections:
        print(f"  {section.step_number:2d}. {section.title}")
        print(f"      Python: {section.python_count:3d} | C++: {section.cpp_count:3d} | Topics: {len(section.topics)}")

    print(f"\n✅ A2Z structure saved to data/a2z_structure.json")

if __name__ == "__main__":
    main()