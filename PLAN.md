---
phase: 1
plan: implementation
type: auto
autonomous: true
wave: 1
requirements: []
duration: "3-5 days"
---

# DSA Question Practice System Implementation Plan

## Overview

Comprehensive DSA (Data Structures & Algorithms) question practice platform with 361+ coding challenges extracted from Striver's A2Z DSA course. Real-time code execution, progress tracking, and Gemini AI-powered assistance for learning optimization.

## Objective

Build a complete DSA learning platform with:
- FastAPI backend for question management and code execution
- Modern responsive frontend for interactive problem solving
- Real-time Python code compilation and execution with timeout protection
- Progress tracking and statistics
- Gemini AI integration for hints and assistance
- Complete question dataset from Striver's repository

## Context

This implementation follows best practices for educational platforms:
- Type-safe Python backend (Pydantic models)
- Progressive enhancement frontend (HTML/CSS/JS, no build tools)
- RESTful API with automatic OpenAPI documentation
- Containerized deployment ready
- Comprehensive error handling and logging
- Secure code execution sandbox with timeout protection

---

## Implementation Steps

### 1. Data Pipeline: Extract & Normalize Questions

**Duration:** 1-2 days | **Type:** auto

**What gets built:**
- Question extraction script from C++ repository
- Normalization of C++ code to Python equivalent
- Data validation and quality checks
- JSON question dataset (361+ questions)

**Implementation details:**
- Parse C++ files from Strivers-A2Z-DSA-Sheet repository
- Extract problem statement, examples, and constraints
- Convert C++ solutions to Python equivalents for execution
- Map questions to topics/difficulty levels
- Create structured JSON: id, title, description, difficulty, topic, examples, constraints
- Add test case generation from examples
- Validate: no duplicate IDs, required fields present, valid JSON

**Acceptance criteria:**
- `data/questions/questions.json` contains 360+ questions
- Each question has: id, title, difficulty, topic, description, examples, test_cases
- All test cases are valid and runnable
- No malformed JSON in output
- Questions cover 15+ algorithm categories

### 2. Backend Project Scaffolding & FastAPI Setup

**Duration:** 1 day | **Type:** auto

**What gets built:**
- FastAPI application structure
- Pydantic models for type safety
- Database/file storage for progress tracking
- Environment configuration and .env setup

**Implementation details:**
- Create FastAPI app with `uvicorn` server
- Define Pydantic models: Question, QuestionResponse, ExecutionRequest, ExecutionResult
- Set up logging with Python logging module
- Create main.py entry point
- Configure CORS for frontend communication
- Load questions from JSON at startup
- Set up .env for API keys and configuration
- Create requirements.txt with dependencies: fastapi, uvicorn, pydantic, google-generativeai

**Acceptance criteria:**
- `python run_server.py` starts server on 0.0.0.0:8000
- GET /docs renders interactive API documentation
- GET /api/questions returns list of all questions
- Server gracefully handles missing environment variables
- Logging configured and working

### 3. Question Management API Endpoints

**Duration:** 1 day | **Type:** auto

**What gets built:**
- RESTful endpoints for question browsing and filtering
- Search and filter capabilities
- Pagination support
- Difficulty and topic filtering

**Implementation details:**
- GET /api/questions - List all questions with filters (difficulty, topic, limit, offset)
- GET /api/questions/{id} - Get single question details
- GET /api/questions/search - Full-text search by title/description
- GET /api/topics - List all available topics
- GET /api/difficulties - List all difficulty levels
- All endpoints return JSON with metadata (total count, has_more)
- Implement case-insensitive filtering
- Return 404 for non-existent questions

**Acceptance criteria:**
- All endpoints return proper JSON responses
- Filtering by difficulty returns correct subset
- Search matches on title and description
- Pagination works with limit/offset
- Non-existent question returns 404
- Response times < 200ms for typical queries

### 4. Code Execution Engine & Sandbox

**Duration:** 1-2 days | **Type:** auto

**What gets built:**
- Safe Python code execution with timeout protection
- Code validation before execution
- Test case runner
- Error handling and reporting

**Implementation details:**
- POST /api/questions/{id}/execute - Execute submitted code
- Create secure subprocess execution with 5-second timeout
- Prevent dangerous imports (os, sys, subprocess, __import__)
- Capture stdout/stderr for test results
- Run code against sample test cases
- Return: success/failure, test results, execution time, error messages
- Log all executions for security
- Handle execution timeouts gracefully
- Validate Python syntax before execution

**Acceptance criteria:**
- Valid Python code executes and returns results
- Timeout kills execution after 5 seconds
- Dangerous imports rejected with error message
- Test cases validated correctly
- Execution time tracked and reported
- Error messages clear and helpful
- No code execution errors crash server

### 5. Progress Tracking & User State Management

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Progress storage (solved/attempted/unsolved status)
- User stats and metrics
- Progress persistence (JSON or simple database)

**Implementation details:**
- Create progress.json storing: question_id, status (solved/attempted/unsolved), attempts, last_attempt_time
- POST /api/progress/{id}/mark-solved - Mark question as solved
- POST /api/progress/{id}/mark-attempted - Mark as attempted
- GET /api/stats - Return overall progress stats
- GET /api/stats/by-topic - Progress breakdown by topic
- GET /api/stats/by-difficulty - Progress breakdown by difficulty
- Update progress on successful code execution
- Calculate metrics: total_solved, total_attempted, accuracy_rate
- Persist progress to storage on every update

**Acceptance criteria:**
- Solved questions persist across application restarts
- Stats endpoint returns accurate counts
- Progress breakdown by topic is correct
- Solving a question updates status immediately
- Progress history available for analytics

### 6. Solution Viewing & Learning Features

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Solution display after attempt
- Solution access control (only after attempting)
- Multiple solution approaches
- Explanation/editorial content

**Implementation details:**
- GET /api/questions/{id}/solution - Return solution (after user attempts)
- Store solutions with code, complexity analysis, explanation
- Include time/space complexity for each solution
- Add tips and hints before viewing full solution
- Create editorial explanations for difficult problems
- Solution contains: code, approach explanation, complexity, key insights
- Require at least one failed attempt to view solution
- Log solution access for analytics

**Acceptance criteria:**
- Solutions only accessible after attempting question
- Solution includes explanation and complexity analysis
- Code is properly formatted and readable
- Multiple approaches shown when available
- Hints available before full solution reveal

### 7. Gemini AI Integration: Chat Assistance

**Duration:** 1-2 days | **Type:** auto

**What gets built:**
- Gemini API integration for chat
- AI-powered hints and explanations
- Solution validation via AI
- Context-aware assistance

**Implementation details:**
- POST /api/ai/chat - Send message to Gemini AI
- Include question context in system prompt
- Store conversation history per session
- Prevent users from asking for direct answers
- Guide users toward solutions with hints
- Implement rate limiting (10 AI requests per question)
- Create prompts that encourage learning, not just answers
- Handle API errors gracefully with fallback responses

**Acceptance criteria:**
- AI chat works for supported questions
- Responses are helpful and contextual
- Rate limiting prevents abuse
- AI suggests hints before solutions
- Conversation history maintained per session
- API errors handled gracefully

### 8. Frontend: HTML/CSS/JS Static Interface

**Duration:** 1-2 days | **Type:** auto

**What gets built:**
- Single-page application using vanilla JS
- Question browser with filtering UI
- Code editor with syntax highlighting
- Progress dashboard
- Responsive design (Bootstrap 5)

**Implementation details:**
- Create index.html as main entry point
- Use Bootstrap 5 for responsive design
- Fetch questions from /api/questions on load
- Implement client-side filtering (difficulty, topic)
- Create modular JavaScript components (no build tools)
- Use local storage for UI state
- Add dark mode support with CSS variables
- Mobile-responsive layout

**Acceptance criteria:**
- Page loads and displays 361+ questions
- Filtering works smoothly without full reload
- Layout responsive on mobile/tablet/desktop
- Dark mode toggle persists
- No JavaScript build tools required
- Performance: page load < 2s

### 9. Code Editor Component

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Code editor with Python syntax highlighting
- Line numbers and formatting
- Execute button triggering backend
- Real-time validation feedback

**Implementation details:**
- Use CodeMirror or Ace editor (CDN-based)
- Python syntax highlighting
- Code execution on button click
- Loading spinner during execution
- Display execution results in real-time
- Show test case results with pass/fail
- Auto-save code to localStorage
- Clear errors display when running again

**Acceptance criteria:**
- Code editor loads quickly from CDN
- Syntax highlighting works for Python
- Execute button sends to API and shows results
- Loading indicator appears during execution
- Results display with test case details
- Code persists between page reloads

### 10. Results & Feedback Display

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Test case pass/fail display
- Execution time and memory info
- Error messages with debugging hints
- Success/failure notifications

**Implementation details:**
- Show each test case result: input → expected output → actual output
- Highlight passed/failed tests with colors
- Display execution time and any error messages
- Show helpful error messages (syntax, runtime, timeout)
- Toast notifications for success/failure
- Provide hints if code fails
- Show complexity analysis when solution is revealed
- Compare user solution with optimal approach

**Acceptance criteria:**
- Test case results clear and easy to understand
- Failed tests show actual vs expected output
- Error messages are helpful for debugging
- Success toasts appear on solve
- Execution metrics displayed accurately
- No sensitive error information leaked

### 11. Progress Dashboard & Statistics

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Stats page showing overall progress
- Charts: solved/attempted/unsolved breakdown
- Topic-wise progress visualization
- Difficulty-wise completion rates
- Weekly activity tracking

**Implementation details:**
- GET /api/stats returns: total_solved, total_attempted, total_unsolved, accuracy_rate
- Create charts using Chart.js (CDN)
- Topic breakdown pie chart
- Difficulty completion bar chart
- Weekly activity heatmap
- Show streaks and milestones
- Calculate and display study recommendations
- Update stats in real-time after solving

**Acceptance criteria:**
- Dashboard loads stats correctly
- Charts render and update dynamically
- Progress percentages calculated accurately
- Topic breakdown sums to 100%
- Stats refresh after solving a problem
- Performance: charts render < 500ms

### 12. AI Chat UI Component

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Chat panel in question interface
- Message sending and receiving UI
- Chat history display
- Type indicator while AI is thinking

**Implementation details:**
- Chat panel on right side of question view
- Text input for sending messages
- Message history scrollable
- Show loading indicator while waiting for response
- Format AI responses with markdown support
- Disable certain question requests (e.g., "give me the answer")
- Clear chat on question change
- Store limited history (last 10 messages)

**Acceptance criteria:**
- Chat opens and closes smoothly
- Messages send to API and display response
- Loading indicator shows while waiting
- Responsive on mobile (stack vs side-by-side)
- History clears when switching questions
- Chat doesn't slow down UI

### 13. Search & Discovery Features

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Full-text search by title/description/tags
- Search-as-you-type with autocomplete
- Filter combinations (difficulty + topic + search term)
- Saved filters/searches

**Implementation details:**
- Implement client-side search (no server-side search needed for 361 items)
- Debounce search input (300ms)
- Filter questions by search term + selected filters
- Show search results count
- Highlight matching text in results
- Save last-used filters to localStorage
- Create "Recommended for you" based on solved topics
- Search suggestions from popular questions

**Acceptance criteria:**
- Search works as-you-type
- Results update in < 100ms
- Filters combine correctly
- Search highlights relevant text
- No server calls for search (client-side only)
- Performance smooth at 361 items

### 14. Local Storage & Offline Support

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Progress persistence to localStorage
- Code draft auto-save
- Filter preferences storage
- Offline fallback (read-only)

**Implementation details:**
- Store progress in localStorage with 30-day expiry
- Auto-save code drafts every 10 seconds
- Persist user preferences: theme, default filter
- Provide offline mode: show cached questions read-only
- Sync progress to server when online
- Handle storage quota exceeded gracefully
- Clear old data periodically

**Acceptance criteria:**
- Progress persists across browser restarts
- Code drafts auto-save and restore
- Offline mode shows cached questions
- Storage limit handled gracefully
- No data loss on browser cache clear
- Sync works on reconnection

### 15. Docker Containerization

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Dockerfile for FastAPI application
- Docker Compose for local development
- Health checks and graceful shutdown
- Optimized image size

**Implementation details:**
- Create Dockerfile: Python 3.11 slim base, install dependencies, expose 8000
- Multi-stage build if needed (optional)
- Docker Compose: FastAPI service, volume for code changes
- Health check: GET / returns 200
- Graceful shutdown: handle SIGTERM
- .dockerignore excludes: __pycache__, .git, .env, tests
- Run as non-root user
- Keep image size < 200MB

**Acceptance criteria:**
- `docker build -t dsa-app .` builds successfully
- Image size < 200MB
- `docker-compose up` brings service up
- Health check passes within 30s
- Application accessible at localhost:8000
- Logs visible in docker compose output

### 16. API Documentation & Developer Guide

**Duration:** 1 day | **Type:** auto

**What gets built:**
- OpenAPI/Swagger documentation (auto-generated)
- README with setup and usage instructions
- Architecture documentation
- Example curl/Python API requests

**Implementation details:**
- FastAPI generates Swagger docs automatically at /docs
- Create README.md: overview, setup, running, API usage
- Document all endpoints with examples
- Create architecture diagram in ARCHITECTURE.md
- Include example requests in cURL and Python
- Document data models and response schemas
- Add troubleshooting section
- Include links to Striver's course

**Acceptance criteria:**
- GET /docs shows complete OpenAPI schema
- README has working setup instructions
- All endpoints documented with examples
- Architecture diagram included
- Code examples are executable
- Documentation is current and accurate

### 17. Testing: Unit & Integration Tests

**Duration:** 1-2 days | **Type:** auto

**What gets built:**
- Unit tests for business logic
- Integration tests for API endpoints
- Code execution safety tests
- Data validation tests

**Implementation details:**
- Create tests/ directory with pytest
- Unit tests: question filtering, progress tracking, stat calculations
- Integration tests: API endpoints with real data
- Security tests: dangerous imports blocked, timeout works
- Test code execution with various inputs
- Test error handling and edge cases
- Aim for >= 70% coverage of critical paths
- Run `pytest` with coverage report

**Acceptance criteria:**
- All tests pass with `pytest`
- Coverage >= 70% for business logic
- Security tests verify sandbox safety
- API contract tests document expected responses
- Tests run < 60 seconds
- No flaky tests

### 18. Deployment: Fly.io or Cloud Setup

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Fly.io configuration (fly.toml)
- Environment variables and secrets management
- Zero-downtime deployment strategy
- Health checks and monitoring

**Implementation details:**
- Create fly.toml with FastAPI configuration
- Set up GEMINI_API_KEY as secret
- Configure auto-scaling if needed
- Set up health check: GET / returns 200
- Deploy with `flyctl deploy`
- Configure log aggregation
- Set up monitoring for error rate and latency
- Document deployment process in README

**Acceptance criteria:**
- `flyctl deploy` succeeds
- Application accessible at *.fly.dev
- Environment variables properly configured
- Health checks pass
- Logs accessible via `flyctl logs`
- Graceful handling of secrets

### 19. Observability: Logging & Monitoring

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Structured logging throughout application
- Request/response logging with correlation IDs
- Error logging with full context
- Performance metrics collection

**Implementation details:**
- Configure Python logging with JSON format
- Log all requests: method, path, status, latency
- Log all code executions: question_id, success, error
- Add correlation IDs to traces
- Monitor error rates and latencies
- Track execution timeouts
- Log AI API calls and responses
- Create dashboard for key metrics

**Acceptance criteria:**
- All requests logged with timestamp and correlation ID
- Errors include full context and stack trace
- Logs parseable as JSON
- Key metrics visible in monitoring dashboard
- Performance: < 100ms for 95% of requests
- Error rate < 1% under normal load

### 20. Final Verification & Performance Testing

**Duration:** 1 day | **Type:** auto

**What gets built:**
- Smoke tests for critical user journeys
- Load testing to verify performance
- Security vulnerability scanning
- Production readiness checklist

**Implementation details:**
- Smoke test: browse questions → select question → execute code → view solution
- Load test: 100 concurrent requests, verify < 200ms p95 latency
- Security scan: check for dangerous imports, verify timeout works
- Performance: benchmark code execution (should be < 100ms)
- Database integrity check: all 361 questions present and valid
- Verify Gemini integration works
- Test offline functionality
- Verify all deployment configurations

**Acceptance criteria:**
- Smoke test completes end-to-end in < 10s
- Load test shows p95 latency < 200ms
- Zero critical security issues
- Code execution sandbox verified safe
- 361+ questions available and searchable
- All features working correctly
- Ready for production deployment

---

## Success Criteria

- **Functionality:** All question operations work, code execution safe, AI integration functional
- **Performance:** API response p95 < 200ms, code execution < 5s timeout, page load < 2s
- **Safety:** Code execution sandbox prevents dangerous operations, timeout protection works
- **Usability:** Question browser intuitive, code editor responsive, results clear
- **Reliability:** Zero unhandled errors, graceful degradation, persistent progress
- **Observability:** All requests logged, errors traced, metrics collected
- **Testing:** >= 70% code coverage, critical paths tested, security verified
- **Documentation:** API docs complete, README covers setup, architecture documented

## Output Specification

- **Backend:** Python FastAPI application in `api/`, Docker image ready
- **Frontend:** Static HTML/CSS/JS in `frontend/`, no build tools required
- **Data:** Complete question dataset in `data/questions/questions.json` (361+ questions)
- **Tests:** Passing test suite with `pytest`, coverage report available
- **Deployment:** fly.toml configured, ready for cloud deployment
- **Documentation:** README, ARCHITECTURE.md, API docs at /docs

---

**Version:** 1.0 | **Status:** Ready for Implementation
