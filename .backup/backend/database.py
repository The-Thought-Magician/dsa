"""
Database Management for DSA Learning System

Handles data persistence and retrieval operations.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Problem, UserProgress, LearningSession, AIInteraction


class DatabaseManager:
    """Simple JSON-based database manager for development"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Database files
        self.problems_db = self.data_dir / "problems_database.json"
        self.categories_index = self.data_dir / "categories_index.json"
        self.patterns_index = self.data_dir / "patterns_index.json"
        self.difficulty_index = self.data_dir / "difficulty_index.json"

        # User data files
        self.user_progress_db = self.data_dir / "user_progress.json"
        self.learning_sessions_db = self.data_dir / "learning_sessions.json"
        self.ai_interactions_db = self.data_dir / "ai_interactions.json"

        # Initialize databases
        self._init_user_databases()

    def _init_user_databases(self):
        """Initialize user-specific database files"""
        if not self.user_progress_db.exists():
            with open(self.user_progress_db, 'w') as f:
                json.dump({}, f)

        if not self.learning_sessions_db.exists():
            with open(self.learning_sessions_db, 'w') as f:
                json.dump({}, f)

        if not self.ai_interactions_db.exists():
            with open(self.ai_interactions_db, 'w') as f:
                json.dump([], f)

    def load_problems(self) -> List[Problem]:
        """Load all problems from database"""
        try:
            with open(self.problems_db, 'r') as f:
                problems_data = json.load(f)
            return [Problem(**data) for data in problems_data]
        except FileNotFoundError:
            return []

    def get_problem_by_id(self, problem_id: str) -> Optional[Problem]:
        """Get a specific problem by ID"""
        problems = self.load_problems()
        for problem in problems:
            if problem.id == problem_id:
                return problem
        return None

    def get_problems_by_category(self, category: str) -> List[Problem]:
        """Get problems by category"""
        problems = self.load_problems()
        return [p for p in problems if p.category == category]

    def get_problems_by_pattern(self, pattern: str) -> List[Problem]:
        """Get problems by pattern"""
        problems = self.load_problems()
        return [p for p in problems if pattern in p.patterns]

    def get_problems_by_difficulty(self, difficulty: str) -> List[Problem]:
        """Get problems by difficulty"""
        problems = self.load_problems()
        return [p for p in problems if p.difficulty == difficulty]

    def search_problems(self, query: str) -> List[Problem]:
        """Search problems by title or description"""
        problems = self.load_problems()
        query_lower = query.lower()
        return [
            p for p in problems
            if query_lower in p.title.lower() or
            (p.description and query_lower in p.description.lower())
        ]

    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories and their problem counts"""
        try:
            with open(self.categories_index, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_patterns(self) -> Dict[str, List[str]]:
        """Get all patterns and their problem IDs"""
        try:
            with open(self.patterns_index, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_difficulty_distribution(self) -> Dict[str, List[str]]:
        """Get difficulty distribution"""
        try:
            with open(self.difficulty_index, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_user_progress(self, progress: UserProgress):
        """Save user progress for a problem"""
        try:
            with open(self.user_progress_db, 'r') as f:
                all_progress = json.load(f)
        except FileNotFoundError:
            all_progress = {}

        user_id = progress.user_id
        if user_id not in all_progress:
            all_progress[user_id] = {}

        # Convert datetime to string for JSON serialization
        progress_dict = progress.dict()
        if progress_dict['last_attempt']:
            progress_dict['last_attempt'] = progress_dict['last_attempt'].isoformat()

        all_progress[user_id][progress.problem_id] = progress_dict

        with open(self.user_progress_db, 'w') as f:
            json.dump(all_progress, f, indent=2)

    def get_user_progress(self, user_id: str, problem_id: Optional[str] = None) -> List[UserProgress]:
        """Get user progress for problems"""
        try:
            with open(self.user_progress_db, 'r') as f:
                all_progress = json.load(f)
        except FileNotFoundError:
            return []

        if user_id not in all_progress:
            return []

        user_progress = all_progress[user_id]

        if problem_id:
            if problem_id in user_progress:
                progress_data = user_progress[problem_id]
                # Convert string back to datetime
                if progress_data.get('last_attempt'):
                    progress_data['last_attempt'] = datetime.fromisoformat(progress_data['last_attempt'])
                return [UserProgress(**progress_data)]
            return []
        else:
            result = []
            for prog_data in user_progress.values():
                if prog_data.get('last_attempt'):
                    prog_data['last_attempt'] = datetime.fromisoformat(prog_data['last_attempt'])
                result.append(UserProgress(**prog_data))
            return result

    def save_learning_session(self, session: LearningSession):
        """Save learning session"""
        try:
            with open(self.learning_sessions_db, 'r') as f:
                all_sessions = json.load(f)
        except FileNotFoundError:
            all_sessions = {}

        user_id = session.user_id
        if user_id not in all_sessions:
            all_sessions[user_id] = []

        # Convert datetime to string
        session_dict = session.dict()
        session_dict['start_time'] = session_dict['start_time'].isoformat()
        if session_dict['end_time']:
            session_dict['end_time'] = session_dict['end_time'].isoformat()

        all_sessions[user_id].append(session_dict)

        with open(self.learning_sessions_db, 'w') as f:
            json.dump(all_sessions, f, indent=2)

    def get_learning_sessions(self, user_id: str, limit: int = 10) -> List[LearningSession]:
        """Get recent learning sessions for user"""
        try:
            with open(self.learning_sessions_db, 'r') as f:
                all_sessions = json.load(f)
        except FileNotFoundError:
            return []

        if user_id not in all_sessions:
            return []

        sessions = all_sessions[user_id][-limit:]  # Get latest sessions

        result = []
        for session_data in sessions:
            # Convert strings back to datetime
            session_data['start_time'] = datetime.fromisoformat(session_data['start_time'])
            if session_data.get('end_time'):
                session_data['end_time'] = datetime.fromisoformat(session_data['end_time'])
            result.append(LearningSession(**session_data))

        return result

    def save_ai_interaction(self, interaction: AIInteraction):
        """Save AI interaction"""
        try:
            with open(self.ai_interactions_db, 'r') as f:
                interactions = json.load(f)
        except FileNotFoundError:
            interactions = []

        # Convert datetime to string
        interaction_dict = interaction.dict()
        interaction_dict['timestamp'] = interaction_dict['timestamp'].isoformat()

        interactions.append(interaction_dict)

        with open(self.ai_interactions_db, 'w') as f:
            json.dump(interactions, f, indent=2)

    def get_ai_interactions(self, user_id: str, limit: int = 50) -> List[AIInteraction]:
        """Get recent AI interactions for user"""
        try:
            with open(self.ai_interactions_db, 'r') as f:
                all_interactions = json.load(f)
        except FileNotFoundError:
            return []

        user_interactions = [
            i for i in all_interactions
            if i.get('user_id') == user_id
        ][-limit:]

        result = []
        for interaction_data in user_interactions:
            # Convert string back to datetime
            interaction_data['timestamp'] = datetime.fromisoformat(interaction_data['timestamp'])
            result.append(AIInteraction(**interaction_data))

        return result


# Global database instance
db = DatabaseManager()


async def init_db():
    """Initialize database on application startup"""
    # Any additional initialization logic can go here
    print(f"Database initialized with {len(db.load_problems())} problems")
    print(f"Categories: {len(db.get_categories())}")
    print(f"Patterns: {len(db.get_patterns())}")


async def get_database() -> DatabaseManager:
    """Dependency injection for database"""
    return db