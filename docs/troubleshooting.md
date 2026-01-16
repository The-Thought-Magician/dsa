# Troubleshooting Guide

This document helps you resolve common issues when using the A2Z DSA Learning System.

## Server Issues

### Server won't start

**Symptom**: `Address already in use` error

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn api.main:app --port 8001
```

**Symptom**: `ModuleNotFoundError: No module named 'api'`

**Solution**:
```bash
# Make sure you're in the project root
cd dsa

# Reinstall the package
pip install -e .
```

**Symptom**: `ImportError: cannot import name 'Limiter' from 'slowapi'`

**Solution**:
```bash
# Install slowapi
pip install slowapi>=0.1.9
```

## AI Chat Issues

### AI chat returns errors

**Symptom**: `503 Service Configuration Error`

**Solution**:
1. Verify `GEMINI_API_KEY` is set in `.env`
2. Check the API key is valid at https://aistudio.google.com/app/apikey
3. Ensure you have API quota available

**Symptom**: `429 Too Many Requests`

**Solution**: Wait a moment and retry. The rate limit is 20 requests per minute for AI chat.

**Symptom**: `504 Request timeout`

**Solution**: The AI request took too long. Try again with a shorter question.

## Code Execution Issues

### Code execution timeout

**Symptom**: All code executions timeout

**Solutions**:
1. Check that Python 3 is available: `python3 --version`
2. Verify your code doesn't use blocked operations:
   - No `import` statements
   - No file I/O (`open()`)
   - No `subprocess` calls
   - No `os` module
   - No network calls

**Example of blocked code**:
```python
# This will be blocked
import os
os.system('ls')
```

**Example of allowed code**:
```python
# This works fine
def solve():
    arr = [1, 2, 3, 4, 5]
    return sum(arr)

print(solve())
```

### Wrong output

**Symptom**: Output doesn't match expected

**Solutions**:
1. Make sure your code reads from `stdin` and writes to `stdout`
2. Check for extra whitespace in your output
3. Verify you're handling all edge cases

**Correct pattern**:
```python
def solve():
    import sys
    data = sys.stdin.read().strip().split()
    # Process data
    result = process(data)
    print(result)

if __name__ == "__main__":
    solve()
```

## Frontend Issues

### Charts don't render

**Symptom**: Charts show as blank or console errors

**Solutions**:
1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify Chart.js is loaded: `typeof Chart !== 'undefined'`
4. Check that `window.app.data.stats` is populated

**Common error**: `Cannot read properties of undefined`

**Solution**: Wait for data to load before rendering charts.

### Questions not loading

**Symptom**: Questions list is empty

**Solutions**:
1. Check Network tab in DevTools
2. Verify `/api/questions` returns 200 status
3. Check that `data/questions/questions.json` exists

### Mobile layout issues

**Symptom**: Layout broken on mobile

**Solutions**:
1. Clear browser cache
2. Verify viewport meta tag exists in `index.html`
3. Check that `responsive.css` is loaded

## Data Issues

### Missing questions

**Symptom**: Expected questions not showing

**Solution**:
```bash
# Rebuild the dataset
python scripts/extract_cpp_questions_batch.py
curl -X POST http://localhost:8000/api/rebuild
```

### Placeholder tests still showing

**Symptom**: Tests show `# Input will be provided`

**Solution**:
```bash
# Run enricher to generate real tests
python scripts/enrich_questions_with_gemini.py
```

## Progress Tracking Issues

### Progress not saving

**Symptom**: Solved questions reset to unsolved

**Solutions**:
1. Check that `data/question_progress.json` is writable
2. Check file permissions: `ls -la data/`
3. Verify the server has write access

### Status not updating after submit

**Symptom**: Status remains "unsolved" after correct submission

**Solution**:
1. Check browser console for errors
2. Verify the `/api/questions/{id}/submit` endpoint returns 200
3. Check that all test cases pass

## Performance Issues

### Slow page load

**Symptom**: Dashboard takes long time to load

**Solutions**:
1. Check number of questions (should be ~361)
2. Verify API response time in Network tab
3. Consider pagination if > 500 questions

### Slow code execution

**Symptom**: Code runs slowly even for simple problems

**Solutions**:
1. Check system resources (CPU, memory)
2. Verify resource limits are set in `api/services.py`
3. The execution timeout is 5 seconds by design

## Getting Help

### Check logs

```bash
# View API logs
tail -f logs/api.log

# View recent logs
tail -100 logs/api.log
```

### Enable debug logging

```bash
# Start server with debug logging
LOG_LEVEL=DEBUG python run_server.py
```

### Report issues

When reporting issues, include:
1. Error message (full traceback)
2. Steps to reproduce
3. Browser and OS version
4. Relevant logs from `logs/api.log`

### Useful debugging commands

```bash
# Test API health
curl http://localhost:8000/health

# Check stats endpoint
curl http://localhost:8000/api/stats

# Test with specific question
curl http://localhost:8000/api/questions/implement-min-heap

# Count questions
python -c "import json; print(len(json.load(open('data/questions/questions.json'))['questions']))"
```

## Error Messages Reference

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Bad Request | Check your input data |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limit | Wait before retrying |
| 500 | Server Error | Check logs, retry |
| 502 | AI Unavailable | AI service down, retry later |
| 503 | Service Unavailable | API key missing or invalid |
| 504 | Timeout | Request took too long |

## Still Having Issues?

1. Check the [Data Pipeline Documentation](data-pipeline.md)
2. Review the [Developer Setup Guide](developer-setup.md)
3. Search existing [GitHub Issues](../../issues)
4. Create a new issue with the troubleshooting template
