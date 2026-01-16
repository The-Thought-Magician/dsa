# Security & Robustness Plan

## Overview

This plan addresses security vulnerabilities and robustness issues in the A2Z DSA Learning System, particularly around code execution, API security, and error handling.

## Current Security Concerns

| Area | Risk | Severity |
|------|------|----------|
| Python Code Execution | Arbitrary code execution via subprocess | High |
| API Endpoints | No rate limiting, no authentication | Medium |
| File Access | Potential path traversal via resource links | Medium |
| AI Chat | No input sanitization, prompt injection | Medium |
| Error Messages | Stack traces may leak information | Low |
| Environment | `.env` file should be gitignored | Low |

## Phase 1: Code Execution Sandbox

### 1.1 Current Implementation

**File**: `api/services.py:332`

```python
# Current: Direct subprocess execution
result = subprocess.run(
    ["python3", "-c", code],
    capture_output=True,
    timeout=5,
    cwd="/tmp"
)
```

**Issues**:
- No resource limits (memory, CPU)
- Can access parent filesystem via `../`
- Can make network requests
- Can spawn infinite processes

### 1.2 Sandboxing Strategy

**Option A: Docker Container (Recommended)**

```python
import docker

client = docker.from_env()

def execute_code_safely(code: str, timeout: int = 5):
    """Execute Python code in isolated Docker container."""
    try:
        container = client.containers.run(
            image="python:3.11-slim",
            command=f"python3 -c {shlex.quote(code)}",
            mem_limit="128m",        # Memory limit
            cpu_quota=50000,         # 50% of 1 CPU
            network_disabled=True,   # No network access
            read_only=True,          # Read-only filesystem
            timeout=timeout,
            remove=True,
            stdout=True,
            stderr=True
        )
        return {"stdout": container, "stderr": ""}
    except docker.errors.ContainerError as e:
        return {"stdout": "", "stderr": str(e.stderr)}
    except Exception as e:
        return {"stdout": "", "stderr": str(e)}
```

**Option B: Restricted Python (Fallback)**

```python
import RestrictedPython

def execute_code_restricted(code: str, timeout: int = 5):
    """Execute code with RestrictedPython."""
    from RestrictedPython import compile_restricted
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError("Execution timeout")

    # Compile with restrictions
    compiled = compile_restricted(code, filename="<string>", mode="exec")
    if compiled.errors:
        return {"stdout": "", "stderr": "\n".join(compiled.errors)}

    # Execute in limited globals
    safe_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "str": str,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
            "max": max,
            "min": min,
            "sum": sum,
            "sorted": sorted,
        }
    }

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        exec(compiled.code, safe_globals)
        signal.alarm(0)
        return {"stdout": safe_globals.get("_output", ""), "stderr": ""}
    except TimeoutError:
        return {"stdout": "", "stderr": "Execution timeout"}
    except Exception as e:
        return {"stdout": "", "stderr": str(e)}
    finally:
        signal.alarm(0)
```

### 1.3 Resource Cleanup

**File**: `api/services.py`

Add guaranteed cleanup:

```python
import tempfile
import shutil
from contextlib import contextmanager

@contextmanager
def isolated_execution(code: str):
    """Create isolated temp directory with cleanup."""
    temp_dir = tempfile.mkdtemp(prefix="dsa_exec_")
    try:
        # Set resource limits
        resource.setrlimit(resource.RLIMIT_AS, (128_000_000, 128_000_000))
        yield temp_dir
    finally:
        # Always cleanup, even on exception
        shutil.rmtree(temp_dir, ignore_errors=True)
        # Kill any orphaned Python processes
        subprocess.run(["pkill", "-9", "-f", "python3"], stderr=subprocess.DEVNULL)
```

### 1.4 Input Validation

Before executing code, validate for:

```python
def validate_code_for_execution(code: str) -> tuple[bool, str]:
    """Validate code doesn't contain dangerous patterns."""
    dangerous_patterns = [
        ("import", "Imports are not allowed"),
        ("__import__", "Dynamic imports are not allowed"),
        ("eval", "eval() is not allowed"),
        ("exec", "exec() is not allowed"),
        ("open", "File operations are not allowed"),
        ("subprocess", "Subprocess calls are not allowed"),
        ("os.", "OS module is not allowed"),
        ("sys.", "Sys module is not allowed"),
        ("../", "Path traversal detected"),
        ("http", "Network calls are not allowed"),
    ]

    code_lower = code.lower()
    for pattern, message in dangerous_patterns:
        if pattern in code_lower:
            return False, message

    # Check for excessively long code
    if len(code) > 10_000:
        return False, "Code exceeds maximum length"

    # Check for too many lines
    if len(code.split("\n")) > 200:
        return False, "Code exceeds maximum line count"

    return True, ""
```

## Phase 2: API Security

### 2.1 Rate Limiting

**File**: `api/main.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Apply to sensitive endpoints
@app.post("/api/questions/{id}/run")
@limiter.limit("10/minute")  # 10 executions per minute
async def run_code(...):
    ...

@app.post("/api/ai/chat")
@limiter.limit("20/minute")  # 20 AI messages per minute
async def ai_chat(...):
    ...
```

### 2.2 Input Sanitization

**File**: `api/routers/ai.py`

```python
import re

def sanitize_chat_input(message: str) -> str:
    """Sanitize user input to AI chat."""
    # Remove potential prompt injection patterns
    message = re.sub(r"(?i)ignore (all )?(previous|above) instructions", "", message)
    message = re.sub(r"(?i)system:", "", message)
    message = re.sub(r"(?i)assistant:", "", message)

    # Limit length
    if len(message) > 5000:
        message = message[:5000] + "..."

    return message.strip()
```

### 2.3 Error Response Sanitization

**File**: `api/main.py`

```python
from fastapi.responses import JSONResponse
from fastapi import Request, status

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with sanitized errors."""
    # Log full error for debugging
    logger.error(f"Error: {exc}", exc_info=True)

    # Return generic message to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again."}
    )
```

### 2.4 CORS Configuration

**File**: `api/main.py`

```python
# Tighten CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:3000",
    ],  # Add production domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

## Phase 3: Environment & Secrets

### 3.1 Environment Configuration

**File**: `.env.example`

```bash
# API Keys
GEMINI_API_KEY=your_api_key_here

# Security
ALLOWED_ORIGINS=http://localhost:8000,http://localhost:3000
PRODUCTION=false

# Rate Limits
CODE_EXECUTION_RATE_LIMIT=10/minute
AI_CHAT_RATE_LIMIT=20/minute

# Execution Settings
EXECUTION_TIMEOUT_SECONDS=5
MAX_CODE_LENGTH=10000
```

### 3.2 Verify .gitignore

**File**: `.gitignore`

Ensure these entries exist:

```
.env
.env.local
.env.*.local
*.key
*.pem
data/solutions/
data/reports/
```

### 3.3 Secrets Management

**File**: `api/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable must be set")

    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000"
    ).split(",")

    PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"

    # Execution limits
    EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "5"))
    MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))

    @classmethod
    def validate(cls):
        """Validate configuration on startup."""
        if not cls.GEMINI_API_KEY or len(cls.GEMINI_API_KEY) < 10:
            raise ValueError("Invalid GEMINI_API_KEY")
        return True
```

## Phase 4: Error Handling & Logging

### 4.1 Structured Logging

**File**: `api/logging_config.py`

```python
import logging
import sys
from datetime import datetime

def setup_logging():
    """Configure structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/api.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Suppress verbose library logs
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
```

### 4.2 Error Mapping

**File**: `api/services.py`

```python
from fastapi import HTTPException

def map_gemini_error_to_http(error) -> HTTPException:
    """Map Gemini API errors to appropriate HTTP responses."""
    error_msg = str(error).lower()

    if "quota" in error_msg or "429" in error_msg:
        return HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    elif "timeout" in error_msg or "504" in error_msg:
        return HTTPException(
            status_code=504,
            detail="Request timeout. Please try again."
        )
    elif "key" in error_msg or "401" in error_msg or "403" in error_msg:
        return HTTPException(
            status_code=503,
            detail="Service configuration error. Please contact support."
        )
    else:
        return HTTPException(
            status_code=500,
            detail="An unexpected error occurred."
        )
```

## Phase 5: Path Security

### 5.1 Path Normalization

**File**: `api/services.py`

```python
import os
from pathlib import Path

def normalize_resource_path(raw_path: str) -> str:
    """Normalize and validate resource paths."""
    # Remove file:// prefix if present
    if raw_path.startswith("file://"):
        raw_path = raw_path[7:]

    # Convert to absolute path relative to repo
    repo_root = Path("Strivers-A2Z-DSA-Sheet").resolve()
    full_path = (repo_root / raw_path).resolve()

    # Ensure path is within repo (prevent traversal)
    try:
        full_path.relative_to(repo_root)
    except ValueError:
        raise ValueError("Path outside repository not allowed")

    # Convert to URL-safe forward slashes
    return f"/repos/{full_path.relative_to(repo_root).as_posix()}"
```

### 5.2 Resource Link Validation

```python
def validate_resource_url(url: str) -> bool:
    """Validate resource URL is safe."""
    allowed_patterns = [
        r"^/repos/",           # Local repository files
        r"^https://takeuforward\.org",  # Official course
        r"^https://leetcode\.com",      # LeetCode
        r"^https://practice\.geeksforgeeks\.org",  # GeeksForGeeks
    ]

    return any(re.match(pattern, url) for pattern in allowed_patterns)
```

## Execution Order

| Step | Task | Priority | Dependencies |
|------|------|----------|--------------|
| 1 | Verify .gitignore includes .env | High | - |
| 2 | Add code validation before execution | High | - |
| 3 | Implement Docker sandboxing | High | Docker installed |
| 4 | Add rate limiting to API | High | - |
| 5 | Sanitize AI chat inputs | Medium | - |
| 6 | Implement global error handler | Medium | - |
| 7 | Add structured logging | Medium | - |
| 8 | Normalize resource paths | Medium | - |
| 9 | Tighten CORS configuration | Low | - |
| 10 | Add secrets management | Low | - |

## Success Criteria

- [ ] Code execution runs in isolated environment
- [ ] Rate limits prevent abuse
- [ ] No stack traces exposed to clients
- [ ] All paths validated and normalized
- [ ] .env file properly gitignored
- [ ] Error messages are user-friendly
- [ ] Security audit passes

## Testing Security

**File**: `tests/test_security.py`

```python
def test_code_execution_blocks_dangerous_imports():
    """Test that dangerous imports are blocked."""
    response = client.post("/api/questions/1/run", json={
        "code": "import os; os.system('rm -rf /')"
    })
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]

def test_path_traversal_blocked():
    """Test that path traversal is blocked."""
    response = client.get("/api/resources?path=../../../etc/passwd")
    assert response.status_code == 400

def test_rate_limiting():
    """Test that rate limiting works."""
    for _ in range(15):  # Exceeds 10/minute limit
        client.post("/api/questions/1/run", json={"code": "print(1)"})
    # 11th request should be rate limited
    assert response.status_code == 429
```
