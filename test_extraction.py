"""Test question extraction on a few files first."""

import os
from pathlib import Path
from scripts.extract_questions_from_cpp import QuestionExtractor

# Set environment variable, take from .env file if exists
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            os.environ[key] = value


def test_extraction():
    extractor = QuestionExtractor()

    # Test with just a few files
    test_files = [
        Path("Strivers-A2Z-DSA-Sheet/01.Arrays/2.Medium/01.2_sum_problem.cpp"),
        Path("Strivers-A2Z-DSA-Sheet/09. Heaps/1. Learning/01. Implement min heap.cpp"),
        Path("Strivers-A2Z-DSA-Sheet/09. Heaps/1. Learning/02. Check if array is heap.cpp")
    ]

    questions = []
    for test_file in test_files:
        if test_file.exists():
            print(f"Processing: {test_file}")
            question_data = extractor.extract_cpp_content(test_file)
            if question_data and question_data['question']:
                question_obj = extractor.create_question_object(question_data)
                questions.append(question_obj)
                print(f"  Success: {question_obj['title']}")
            else:
                print(f"  Failed to extract question")
        else:
            print(f"  File not found: {test_file}")

    print(f"\nGenerated {len(questions)} test questions")

    # Save test results
    if questions:
        extractor.save_questions(questions)
        print("Test extraction completed successfully!")

    return questions

if __name__ == "__main__":
    questions = test_extraction()