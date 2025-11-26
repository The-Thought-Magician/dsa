# DSA Question Practice System

A comprehensive DSA question practice platform with 361 coding challenges extracted from Striver's A2Z DSA course. Features real-time code execution, progress tracking, and Gemini AI-powered assistance.

## 🚀 Quick Start

### 🌐 Web Interface (Recommended)

```bash
# 1. Setup virtual environment
uv venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -e .

# 3. Start web server
python run_server.py

# 4. Open browser to http://localhost:8000
```

### 💻 Question Management

```bash
# Extract questions from C++ repository
python scripts/extract_cpp_questions_batch.py

# View available questions via API
curl http://localhost:8000/api/questions
```

## 📊 System Overview

- **361 DSA Questions**: Extracted from Striver's comprehensive C++ repository
- **Complete Coverage**: Arrays, Trees, Graphs, DP, Greedy, and all major algorithms
- **Real-time Code Execution**: Python code compilation with 5-second timeout
- **Progress Tracking**: Solved/Attempted/Unsolved status for each question
- **Modern Web UI**: Interactive question browser with filtering and search
- **AI Integration**: Gemini-powered assistance and chat functionality
- **Solution System**: View solutions after attempting problems

## 🌟 Features

### 🌐 Question Practice Interface
- **Question Browser**: Browse all 361 questions with filtering by difficulty and tags
- **Code Editor**: Write and test Python solutions with real-time execution
- **Progress Tracking**: Automatic tracking of solved, attempted, and unsolved questions
- **Solution Viewing**: Access solutions after attempting problems
- **AI Chat**: Get help from Gemini AI while solving problems

### 📝 Code Execution Engine
- **Python Runtime**: Execute Python code with 5-second timeout protection
- **Test Case Validation**: Automatic validation against sample test cases
- **Error Handling**: Clear error messages and debugging assistance
- **Status Updates**: Real-time feedback on solution correctness

### 🤖 AI Integration
- **Gemini Chat**: Ask questions and get help while solving problems
- **Solution Generation**: AI-generated Python solutions (for reference)
- **Test Case Creation**: Automatically generated test cases for each problem

## 🛠️ Architecture

### Backend (FastAPI)
- RESTful API for question management and code execution
- Python code compilation with subprocess execution
- Progress tracking and status management
- Gemini AI integration for chat assistance
- Automatic OpenAPI documentation at `/docs`

### Frontend (Modern Web)
- Pure HTML/CSS/JavaScript (no build tools)
- Bootstrap 5 for responsive design
- Real-time code editor and execution
- Progress visualization and statistics

### Project Structure
```
dsa/
├── api/                    # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── services.py        # Business logic & code execution
│   └── routers/           # API route modules
├── frontend/              # Web interface
│   ├── index.html         # Main application
│   └── assets/            # CSS, JS, components
├── scripts/               # Question extraction scripts
├── data/                  # Question dataset
└── Strivers-A2Z-DSA-Sheet/ # Source C++ repository
```

## 📁 Data Files

### Core Files
- `data/questions/questions.json` - Complete question dataset (361 questions)
- `data/questions/progress.json` - User progress tracking
- `.env` - Gemini API key configuration

### Source Repository
- `Strivers-A2Z-DSA-Sheet/` - C++ solutions source (369 files)

### Archived Files (moved to .backup)
- Old learning system files (topic mapping, index generation, etc.)
- Previous question generation scripts

## 🌐 API Endpoints

### Core Endpoints
```
GET  /                           # Web application
GET  /api/questions              # List all questions
GET  /api/questions/{id}         # Get question details
POST /api/questions/{id}/execute # Execute solution code
GET  /api/questions/{id}/solution # Get solution (after attempt)
POST /api/ai/chat                # Gemini AI chat assistance
GET  /docs                       # API documentation
```

## 📚 Usage Examples

### Daily Practice Workflow
1. Open http://localhost:8000
2. Browse available questions by difficulty or topic
3. Select a question and read the problem statement
4. Write your Python solution in the code editor
5. Test your solution against sample test cases
6. View the solution after attempting the problem
7. Use AI chat for hints and explanations

### API Usage Examples
```bash
# Get all questions
curl http://localhost:8000/api/questions

# Get specific question
curl http://localhost:8000/api/questions/implement-min-heap

# Execute code for a question
curl -X POST http://localhost:8000/api/questions/implement-min-heap/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "def solve():\n    print(\"Hello World\")", "language": "python"}'
```

## 🎯 System Status

Current system achievements:

- ✅ **361 DSA Questions**: Successfully extracted from C++ repository
- ✅ **Complete Algorithm Coverage**: Arrays, Trees, Graphs, DP, Greedy, and more
- ✅ **Real-time Code Execution**: Python solutions with timeout protection
- ✅ **Progress Tracking**: Solved/Attempted/Unsolved status management
- ✅ **AI Integration**: Gemini-powered chat assistance
- ✅ **Modern Web Interface**: Responsive design with interactive features

### Question Distribution
```
📊 Total Questions: 361
🎯 Difficulty Levels: Easy, Medium, Hard
🔍 Topic Coverage: 15+ algorithm categories
✨ Code Execution: Real-time Python compilation
🤖 AI Support: Gemini-powered assistance
```

## 📖 Documentation

- [`docs/plan.md`](docs/plan.md) - Master plan with phases and milestones
- [`docs/design.md`](docs/design.md) - Technical architecture and algorithms
- [`docs/done.md`](docs/done.md) - Progress log and changelog
- [`docs/frontend_design.md`](docs/frontend_design.md) - Frontend architecture

## 🔧 Development

### Environment Setup
```bash
# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e .
```

### Running the Application
```bash
# Web server (recommended)
python run_server.py

# CLI commands
python main.py --help
```

### Adding New Questions
1. Add C++ files to `Strivers-A2Z-DSA-Sheet/` repository
2. Run `python scripts/extract_cpp_questions_batch.py` to extract questions
3. Restart the application to load new questions
4. Questions are automatically available via the web interface

### Enhancing with AI
1. Set `GEMINI_API_KEY` in `.env` file
2. Use the AI enhancement script for generating better solutions and test cases
3. The system supports AI-powered assistance during problem solving

## 📊 Data Schema

### API Response Models
- **TopicResponse**: Complete topic information
- **CoverageResponse**: Gap analysis and metrics
- **StudyPlanResponse**: Daily tasks with scheduling
- **StatsResponse**: Progress statistics

## 🎉 DSA Question Practice System - Complete!

The DSA Question Practice System is **FULLY OPERATIONAL**:

- ✅ **361 DSA Questions**: Complete extraction from Striver's C++ repository
- ✅ **Real-time Code Execution**: Python compilation with timeout protection
- ✅ **Progress Tracking**: Solved/Attempted/Unsolved status management
- ✅ **AI Integration**: Gemini-powered chat assistance
- ✅ **Modern Web Interface**: Responsive design with interactive features
- ✅ **RESTful API**: Complete documentation at `/docs`
- ✅ **Solution System**: View solutions after attempting problems

**Access Methods:**
- 🌐 **Web Application**: http://localhost:8000
- 📚 **API Documentation**: http://localhost:8000/docs
- 🤖 **AI Chat**: Integrated Gemini assistance

## 📞 Support

For issues or questions:
1. Check the web application at http://localhost:8000
2. Review API documentation at http://localhost:8000/docs
3. Re-run question extraction: `python scripts/extract_cpp_questions_batch.py`
4. Verify Gemini API key is set in `.env` file

---

*Built with Python 3.11+, FastAPI, Bootstrap 5, and Google Gemini AI.*