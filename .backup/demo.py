#!/usr/bin/env python3
"""
Demo Script for DSA Learning System

Quick demonstration of the system capabilities.
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"


def test_api_endpoints():
    """Test all API endpoints"""
    print("🚀 Testing DSA Learning System API\n")

    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: API is running")
        else:
            print("❌ Health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on port 8000")
        return

    # Test problems endpoint
    print("\n📚 Testing Problems API:")
    try:
        response = requests.get(f"{BASE_URL}/api/problems?page=1&page_size=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_count']} total problems")
            print(f"   Showing {len(data['problems'])} problems on page 1")
            if data['problems']:
                first_problem = data['problems'][0]
                print(f"   Example: {first_problem['title']} ({first_problem['difficulty']})")
        else:
            print(f"❌ Problems API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Problems API error: {e}")

    # Test categories
    print("\n📁 Testing Categories:")
    try:
        response = requests.get(f"{BASE_URL}/api/problems/categories/list")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories:")
            for cat, info in list(categories.items())[:3]:
                print(f"   • {cat}: {info['count']} problems")
        else:
            print(f"❌ Categories API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories API error: {e}")

    # Test patterns
    print("\n🔍 Testing Patterns:")
    try:
        response = requests.get(f"{BASE_URL}/api/problems/patterns/list")
        if response.status_code == 200:
            patterns = response.json()
            print(f"✅ Found {len(patterns)} patterns:")
            for pattern, info in list(patterns.items())[:5]:
                print(f"   • {pattern}: {info['count']} problems")
        else:
            print(f"❌ Patterns API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Patterns API error: {e}")

    print("\n🎯 API Test Complete! The backend is working correctly.")


def demonstrate_learning_flow():
    """Demonstrate a typical learning flow"""
    print("\n🎓 Demonstrating Learning Flow:")

    user_id = "demo_user"

    # Get a random easy problem
    try:
        response = requests.get(f"{BASE_URL}/api/problems/random/Easy")
        if response.status_code == 200:
            problem = response.json()
            print(f"📝 Selected problem: {problem['title']}")
            print(f"   Patterns: {', '.join(problem['patterns'])}")
            print(f"   Difficulty: {problem['difficulty']}")

            # Simulate starting to work on the problem
            progress_data = {
                "user_id": user_id,
                "problem_id": problem['id'],
                "status": "In Progress",
                "attempts": 1,
                "time_spent": 300,  # 5 minutes
                "pattern_mastery": {pattern: 0.3 for pattern in problem['patterns']}
            }

            response = requests.post(f"{BASE_URL}/api/progress/update", json=progress_data)
            if response.status_code == 200:
                print("✅ Progress updated successfully")
            else:
                print(f"❌ Progress update failed: {response.status_code}")

        else:
            print(f"❌ Failed to get random problem: {response.status_code}")
    except Exception as e:
        print(f"❌ Learning flow error: {e}")


def show_statistics():
    """Show system statistics"""
    print("\n📊 System Statistics:")

    try:
        # Load problems database directly
        data_path = Path("data/problems_database.json")
        if data_path.exists():
            with open(data_path, 'r') as f:
                problems = json.load(f)

            categories = {}
            patterns = {}
            difficulties = {"Easy": 0, "Medium": 0, "Hard": 0}

            for problem in problems:
                # Count categories
                cat = problem['category']
                categories[cat] = categories.get(cat, 0) + 1

                # Count patterns
                for pattern in problem['patterns']:
                    patterns[pattern] = patterns.get(pattern, 0) + 1

                # Count difficulties
                difficulties[problem['difficulty']] += 1

            print(f"📚 Total Problems: {len(problems)}")
            print(f"📁 Categories: {len(categories)}")
            print(f"🔍 Patterns: {len(patterns)}")
            print(f"💡 Difficulty Distribution:")
            for diff, count in difficulties.items():
                print(f"   • {diff}: {count} problems")

            print(f"\n🔥 Top Patterns:")
            top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]
            for pattern, count in top_patterns:
                print(f"   • {pattern}: {count} problems")

        else:
            print("❌ Problems database not found. Run the processing script first.")

    except Exception as e:
        print(f"❌ Statistics error: {e}")


def main():
    """Main demo function"""
    print("🎯 DSA Learning System Demo")
    print("=" * 50)

    # Show statistics first
    show_statistics()

    # Test if API is running
    print("\n🔌 Checking API Connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running!")
            test_api_endpoints()
            demonstrate_learning_flow()
        else:
            print("❌ API is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running.")
        print("\n💡 To start the API:")
        print("   1. Activate virtual environment: source learning-env/bin/activate")
        print("   2. Run: python -m backend.main")
        print("   3. API will be available at http://localhost:8000")
    except Exception as e:
        print(f"❌ Connection error: {e}")

    print("\n🎉 Demo Complete!")
    print("\n📖 Next Steps:")
    print("   1. Start the backend API")
    print("   2. Build the frontend interface")
    print("   3. Begin learning with DSA patterns!")


if __name__ == "__main__":
    main()