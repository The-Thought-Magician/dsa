# Getting Started

Welcome to the A2Z DSA Learning System! This guide will help you get up and running quickly.

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager) - recommended but not required
- Google Gemini API key (for AI features)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd dsa
```

### 2. Install dependencies

Using uv (recommended):

```bash
uv pip install -e .
```

Using pip:

```bash
pip install -e .
```

### 3. Configure environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from: https://aistudio.google.com/app/apikey

### 4. Start the server

```bash
python run_server.py
```

Or using uvicorn directly:

```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Open in browser

Navigate to: http://localhost:8000

## First Steps

### View Your Dashboard

The dashboard shows your overall progress:
- Total questions available
- Number of problems solved
- Coverage percentage
- Visual charts of your progress

### Browse Topics

- Click "Topics" in the navigation
- Filter by difficulty (Easy/Medium/Hard)
- Filter by tags (arrays, dynamic-programming, graphs, etc.)
- Select a topic to see related problems

### Start Solving Questions

1. Go to the "Questions" section
2. Click on any question card
3. Read the problem statement
4. Write your solution in the code editor
5. Click "Run Code" to test against sample cases
6. Click "Submit" to finalize your solution

### Get AI Help

Stuck on a problem? Use the AI chat assistant:
- Click the AI chat button in the question detail view
- Ask questions about the approach
- Get hints without seeing the full solution
- The AI adapts based on whether you've viewed the solution

### Study Planning

Access the "Planning" section to:
- See your personalized 14-day study plan
- View today's recommended tasks
- Track daily progress

## CLI Usage

The system also includes a command-line interface:

```bash
# List all topics
python -m dsa list topics

# Show coverage gaps
python -m dsa gaps

# Generate a new study plan
python -m dsa plan --days 14

# View statistics
python -m dsa stats
```

## Keyboard Shortcuts

- `Ctrl/Cmd + Enter`: Run code in editor
- `Ctrl/Cmd + Shift + Enter`: Submit solution
- `Escape`: Close modals/panels
- `Tab` / `Shift + Tab`: Navigate between inputs
- `Enter` / `Space`: Activate focused cards

## Troubleshooting

### Server won't start

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### AI chat returns errors

**Error**: `503 Service Configuration Error`

**Solution**:
1. Verify `GEMINI_API_KEY` is set in `.env`
2. Check your API key is valid at https://aistudio.google.com
3. Ensure you have available API quota

### Code execution times out

**Solution**:
1. Check that Python 3 is installed: `python3 --version`
2. Verify your code doesn't use blocked operations (imports, file I/O, etc.)
3. Keep execution under 5 seconds

## Next Steps

- Explore the [Developer Setup Guide](developer-setup.md) for contributing
- Read the [Data Pipeline Documentation](data-pipeline.md) to understand how questions are processed
- Check [Troubleshooting](troubleshooting.md) for more help

## Features Overview

| Feature | Description |
|---------|-------------|
| 361 Questions | Complete Striver A2Z DSA course coverage |
| Real-time Execution | Run Python code with 5-second timeout |
| Progress Tracking | Track solved/attempted/unsolved status |
| AI Assistance | Get hints and explanations via Gemini AI |
| Study Planning | Personalized 14-day study schedules |
| Spaced Repetition | Optimal review scheduling |

Happy coding!
