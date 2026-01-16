# Developer Setup Guide

## Development Environment

### Required Tools

- **Python 3.11+** - The application requires Python 3.11 or higher
- **uv** - Fast Python package manager (recommended)
- **Git** - Version control
- **VS Code** (recommended) or any Python IDE

### VS Code Extensions

- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)

### Optional Tools

- **Docker** - For containerized deployment
- **Postman** - For API testing

## Setting Up Your Development Environment

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone <your-fork-url>
cd dsa

# Add upstream remote
git remote add upstream <original-repo-url>
```

### 2. Create Virtual Environment

Using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

Using venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 5. Verify Installation

```bash
# Run tests
pytest -q

# Run linting
ruff check api/ scripts/

# Start dev server
python run_server.py
```

## Project Structure

```
dsa/
├── api/                    # FastAPI backend
│   ├── __init__.py
│   ├── main.py            # Application entry point
│   ├── models.py          # Pydantic models
│   ├── services.py        # Business logic
│   └── routers/           # API route modules
│       ├── questions.py
│       └── ai.py
├── frontend/              # Web interface
│   ├── index.html         # Main SPA
│   ├── assets/            # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   ├── config.js
│   │   │   ├── questions.js
│   │   │   ├── charts.js
│   │   │   ├── ai_chat.js
│   │   │   └── ui/
│   │   └── components/
│   └── favicon.ico
├── scripts/               # Automation utilities
│   ├── extract_cpp_questions_batch.py
│   └── enrich_questions_with_gemini.py
├── data/                  # Generated data
│   ├── questions/
│   │   └── questions.json
│   └── question_progress.json
├── tests/                 # Test suite
│   ├── conftest.py
│   └── test_api_services.py
├── docs/                  # Documentation
│   ├── getting-started.md
│   ├── developer-setup.md
│   └── plans/
├── .github/               # GitHub workflows
│   └── workflows/
│       └── test.yml
├── pyproject.toml         # Project config
├── run_server.py          # Server startup script
└── README.md
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout dev
git pull upstream dev
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write code following existing style
- Add tests for new features
- Update documentation as needed

### 3. Run Tests and Linting

```bash
# Format code
ruff format api/ scripts/

# Check linting
ruff check api/ scripts/

# Run tests with coverage
pytest --cov=api --cov=scripts --cov-report=html
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Commit message conventions:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub targeting the `dev` branch.

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_services.py

# Run with coverage
pytest --cov=api --cov=scripts --cov-report=html

# Run specific test
pytest tests/test_api_services.py::TestCodeValidation::test_valid_code_passes

# Verbose output
pytest -v
```

## Code Style

This project uses:
- **Ruff** for linting and formatting
- **Pytest** for testing
- **Pydantic** for data validation

### Python Style Guide

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use type hints for function signatures
- Document classes and major functions

### JavaScript Style Guide

- Use 4 spaces for indentation
- Prefer `const`/`let` over `var`
- Use template literals for strings
- Add JSDoc comments for functions

## API Development

### Adding a New Endpoint

1. Define the Pydantic model in `api/models.py`
2. Add the business logic in `api/services.py`
3. Create the route in `api/routers/`
4. Add tests in `tests/test_api_services.py`

Example:

```python
# models.py
class MyResponse(BaseModel):
    message: str

# routers.py
@router.get("/api/my-endpoint", response_model=MyResponse)
async def my_endpoint():
    return {"message": "Hello"}
```

## Frontend Development

The frontend uses vanilla JavaScript with ES6 modules. No build process required.

### Adding a New Page/View

1. Create the HTML structure in `frontend/components/` or `frontend/index.html`
2. Add JavaScript logic in `frontend/assets/js/`
3. Add CSS in `frontend/assets/css/`
4. Update the navigation in `frontend/assets/js/app.js`

### Using the Config

```javascript
import { Config } from './assets/js/config.js';

// Get API URL
const url = Config.buildEndpoint('QUESTION_DETAIL', { id: 'test-question' });

// Show error message
const errorMsg = Config.getErrorMessage(error);
```

## Debugging

### Backend Debugging

```bash
# Run with verbose logging
uvicorn api.main:app --reload --log-level debug

# Check logs
tail -f logs/api.log
```

### Frontend Debugging

1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Use Network tab to inspect API calls
4. Use Sources tab for JavaScript debugging

## Common Issues

### ImportError: No module named 'api'

**Solution**: Make sure you're running from the project root and the package is installed:
```bash
pip install -e .
```

### CORS errors in browser

**Solution**: Check that your origin is in `allowed_origins` in `api/main.py`

### Tests failing with FileNotFoundError

**Solution**: Tests require data files. Make sure `data/questions/questions.json` exists or use test fixtures.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Getting Started Guide](getting-started.md)
- [Data Pipeline Documentation](data-pipeline.md)
