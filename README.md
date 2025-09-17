# A2Z DSA Learning System

A comprehensive, Python-first learning system for mastering Striver's A2Z DSA course with zero topic gaps. Features intelligent indexing, progress tracking, personalized study planning, and a modern web interface.

## 🚀 Quick Start

### 🌐 Web Interface (Recommended)

```bash
# 1. Setup virtual environment
uv venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install -e .

# 3. Initialize the system
python main.py init

# 4. Start web server
python run_server.py

# 5. Open browser to http://localhost:8000
```

### 💻 CLI Interface

```bash
# View your topics
python main.py list

# Check coverage gaps
python main.py gaps

# Get today's study plan
python main.py plan
```

## 📊 System Overview

- **18 A2Z Sections**: Complete coverage of Striver's curriculum
- **478 Problems**: Mapped across Python and C++ repositories
- **70% Coverage**: 324 Python + 345 C++ solutions
- **Smart Matching**: 33 exact + 158 approximate cross-references
- **Spaced Repetition**: Intelligent 14-day study cycles
- **Modern Web UI**: Interactive dashboard with charts and analytics

## 🌟 Features

### 🌐 Web Dashboard
- **Interactive Dashboard**: Real-time statistics and progress charts
- **Topic Browser**: Filterable topic list with search functionality
- **Coverage Analytics**: Visual gap analysis and recommendations
- **Study Planner**: Daily task planning with spaced repetition
- **Responsive Design**: Works on desktop and mobile devices

### 📋 Topic Management
```bash
# List all topics
python main.py list

# Filter by section
python main.py list --section "arrays"

# Filter by status
python main.py list --status "available"
```

### 📊 Progress Tracking
```bash
# View statistics
python main.py stats

# Check coverage gaps
python main.py gaps
```

### 📅 Study Planning
```bash
# Get today's plan
python main.py plan

# View coverage analysis
python main.py gaps
```

## 🛠️ Architecture

### Backend (FastAPI)
- RESTful API serving all CLI functionality
- Automatic OpenAPI documentation at `/docs`
- Real-time data processing
- High performance with async support

### Frontend (Modern Web)
- Pure HTML/CSS/JavaScript (no build tools)
- Bootstrap 5 for responsive design
- Chart.js for data visualization
- Real-time data updates

### Project Structure
```
dsa/
├── api/                    # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── services.py        # Business logic
│   └── routers/           # API route modules
├── frontend/              # Web interface
│   ├── index.html         # Main application
│   └── assets/            # CSS, JS, components
├── scripts/               # Automation scripts
├── data/                  # Generated data files
└── docs/                  # Documentation
```

## 📁 Data Files

### Generated Files
- `data/index.jsonl` - Topic index (71 entries)
- `data/mapping.jsonl` - Problem cross-references (478 entries)
- `data/a2z_structure.json` - Course structure
- `data/study_plan_14day.json` - Generated study plans

### Input Repositories
- `striver-a2z-dsa/` - Python solutions (324 files)
- `Strivers-A2Z-DSA-Sheet/` - C++ reference (369 files)

## 🌐 API Endpoints

### Core Endpoints
```
GET  /                     # Web dashboard
GET  /api/topics           # List topics with filters
GET  /api/coverage         # Coverage analysis
GET  /api/stats            # Progress statistics
GET  /api/study-plan       # Generate study plan
GET  /api/study-plan/today # Today's tasks
POST /api/rebuild          # Rebuild data
GET  /docs                 # API documentation
```

## 📚 Usage Examples

### Daily Web Workflow
1. Open http://localhost:8000
2. Check dashboard for progress overview
3. View today's study plan
4. Track completed tasks
5. Review coverage gaps

### Daily CLI Workflow
```bash
# Morning routine
python main.py plan          # Get today's tasks
python main.py stats         # Check progress

# Weekly review
python main.py gaps          # Identify areas to focus on
python main.py list --status "partial"  # Find incomplete sections
```

## 🎯 Success Criteria Validation

The system validates against these criteria:

- ✅ **100% A2Z sections represented** (18/18)
- ✅ **Every section has problems linked** (0 empty sections)
- ⚠️ **Coverage above 80%** (currently 70.0%)
- ✅ **At least 300 problems mapped** (478 achieved)

### Coverage Status
```
📊 Current Coverage: 70.0%
🎯 Python Solutions: 324 (67.8%)
🔍 C++ Solutions: 345 (72.2%)
✨ Exact Matches: 33
🔍 Approx Matches: 158
❌ Missing Python: 154
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

### Adding New Solutions
1. Add Python files to `striver-a2z-dsa/`
2. Run `python main.py init` to rebuild indexes
3. Check coverage with `python main.py gaps`
4. Refresh web dashboard to see updates

## 📊 Data Schema

### API Response Models
- **TopicResponse**: Complete topic information
- **CoverageResponse**: Gap analysis and metrics
- **StudyPlanResponse**: Daily tasks with scheduling
- **StatsResponse**: Progress statistics

## 🎉 Phase 1 Complete + Web Interface

The A2Z DSA Learning System Phase 1 is **COMPLETE** with additional web interface:

- ✅ Complete A2Z curriculum coverage
- ✅ Intelligent automation scripts
- ✅ Rich CLI interface
- ✅ Modern web dashboard
- ✅ RESTful API with documentation
- ✅ Interactive data visualization
- ✅ Responsive mobile-friendly design
- ✅ 70% solution coverage

**Access Methods:**
- 🌐 **Web Dashboard**: http://localhost:8000
- 💻 **CLI Interface**: `python main.py --help`
- 📚 **API Docs**: http://localhost:8000/docs

## 📞 Support

For issues or questions:
1. Check web dashboard at http://localhost:8000
2. Review API documentation at http://localhost:8000/docs
3. Run `python main.py init` to rebuild data
4. Check `docs/done.md` for troubleshooting tips

---

*Built with Python 3.11+, FastAPI, Rich CLI, Bootstrap 5, and Chart.js.*