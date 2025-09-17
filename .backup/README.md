# DSA Learning System 🎯

AI-powered platform for mastering Data Structures and Algorithms with intelligent tutoring and comprehensive progress tracking.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- uv (for environment management)
- Git

### Setup & Installation

1. **Clone and Setup**
   ```bash
   cd /path/to/your/workspace
   # Repository should already contain processed problems
   ```

2. **Environment Setup**
   ```bash
   # Virtual environment is already created
   source learning-env/bin/activate

   # Dependencies are already installed
   ```

3. **Start the System**
   ```bash
   # Show statistics
   python3 start.py stats

   # Start backend API (in one terminal)
   python3 start.py backend

   # Run demo (in another terminal)
   python3 start.py demo
   ```

## 📊 System Overview

### Current Data
- **324 Problems** from Striver A2Z DSA Course
- **18 Categories** covering all DSA topics
- **28 Patterns** for comprehensive learning
- **Intelligent Classification** with difficulty levels

### Problem Distribution
- **Easy**: 295 problems (91.0%)
- **Medium**: 14 problems (4.3%)
- **Hard**: 15 problems (4.6%)

### Top Patterns
1. Two Pointers (91 problems)
2. DFS/BFS (57 problems each)
3. Sorting (51 problems)
4. Dynamic Programming (48 problems)
5. Graph Algorithms (39 problems)

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py              # Application entry point
├── models.py            # Data models and schemas
├── database.py          # Data persistence layer
└── routes/
    ├── problems.py      # Problem browsing and filtering
    ├── progress.py      # Progress tracking and analytics
    └── ai_tutor.py      # AI-powered tutoring system
```

### Data Processing
```
scripts/
└── process_striver_problems.py    # Extract and structure problems

data/
├── problems_database.json        # All problems with metadata
├── categories_index.json         # Category classifications
├── patterns_index.json          # Pattern mappings
└── difficulty_index.json        # Difficulty distributions
```

## 🎓 Learning Features

### Pattern-Based Learning
- **9 Core Patterns** identified from industry interviews
- **Progressive Difficulty** from basic to advanced
- **Cross-Pattern Problems** for comprehensive understanding

### AI-Powered Assistance
- **Intelligent Hints** without giving away solutions
- **Concept Explanations** with practical examples
- **Code Review** with optimization suggestions
- **Interview Simulation** for realistic practice

### Progress Tracking
- **Visual Analytics** showing learning progress
- **Pattern Mastery** tracking per algorithm type
- **Streak Tracking** for consistency motivation
- **Performance Metrics** for interview readiness

## 🔧 API Endpoints

### Problems
- `GET /api/problems` - List problems with filtering
- `GET /api/problems/{id}` - Get specific problem
- `GET /api/problems/categories/list` - List all categories
- `GET /api/problems/patterns/list` - List all patterns
- `GET /api/problems/random/{difficulty}` - Get random problem

### Progress
- `POST /api/progress/update` - Update solving progress
- `GET /api/progress/{user_id}` - Get user progress
- `GET /api/progress/{user_id}/summary` - Progress analytics
- `GET /api/progress/{user_id}/patterns/analysis` - Pattern mastery

### AI Tutor
- `POST /api/ai/ask` - Ask AI tutor questions
- `POST /api/ai/execute` - Execute and test code
- `GET /api/ai/interactions/{user_id}` - View AI interactions

## 📚 Learning Path

### Phase 1: Foundations (Weeks 1-2)
- [ ] Basic data structures and algorithms
- [ ] Sorting and searching techniques
- [ ] Array manipulation and optimization

### Phase 2: Core Patterns (Weeks 3-4)
- [ ] Two Pointers technique
- [ ] Sliding Window problems
- [ ] Binary Search variations
- [ ] String algorithms

### Phase 3: Advanced Structures (Weeks 5-6)
- [ ] Trees and Binary Search Trees
- [ ] Graphs and traversal algorithms
- [ ] Heaps and priority queues
- [ ] Advanced dynamic programming

### Phase 4: Interview Preparation (Weeks 7-8)
- [ ] Mock interview sessions
- [ ] Pattern combination problems
- [ ] Time complexity optimization
- [ ] System design basics

## 🛠️ Commands

```bash
# Development Commands
python3 start.py help        # Show all commands
python3 start.py stats       # System statistics
python3 start.py process     # Reprocess problems
python3 start.py backend     # Start API server
python3 start.py demo        # Run demonstration

# Direct API Access
curl http://localhost:8000/health                    # Health check
curl http://localhost:8000/api/problems             # List problems
curl http://localhost:8000/api/problems/patterns/list # List patterns
```

## 🔑 Environment Setup

Create `.env` file for AI features:
```bash
cp .env.example .env
# Add your Gemini API key for AI tutoring
GEMINI_API_KEY=your_key_here
```

## 📖 Documentation

- **`plan.md`** - Comprehensive learning roadmap (12-16 weeks)
- **`design.md`** - Technical architecture and implementation
- **`done.md`** - Progress tracking and completed tasks
- **`AGENTS.md`** - Development guidelines and conventions

## 🎯 Success Metrics

### Learning Goals
- **300+ Problems** solved across all patterns
- **90% Accuracy** in timed interview sessions
- **Pattern Mastery** in all 9 core areas
- **Interview Readiness** for top tech companies

### Technical Readiness
- **DSA Proficiency** - Python implementation expertise
- **System Design** - Scalable architecture understanding
- **ML/DL Basics** - AI engineering fundamentals
- **Frontend Skills** - Modern React/TypeScript development

## 🚧 Future Enhancements

### Phase 2 Features
- [ ] React frontend with interactive code editor
- [ ] Real-time collaboration for pair programming
- [ ] Video explanations for complex algorithms
- [ ] Integration with LeetCode and other platforms

### Advanced Features
- [ ] Machine learning for personalized learning paths
- [ ] Community features with discussion forums
- [ ] Certification and achievement system
- [ ] Mobile app for on-the-go learning

## 🤝 Contributing

The system is designed for extensibility:
- Add new problem sources in `scripts/`
- Extend AI capabilities in `backend/routes/ai_tutor.py`
- Enhance analytics in `backend/routes/progress.py`
- Follow conventions in `AGENTS.md`

## 📄 License

Educational use - Built for accelerated DSA learning and interview preparation.

---

**Start your journey**: `python3 start.py backend` and begin mastering DSA patterns! 🚀