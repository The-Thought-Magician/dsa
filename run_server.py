#!/usr/bin/env python3
"""
A2Z DSA Learning System Web Server

Simple script to start the FastAPI server with the frontend.
"""

import uvicorn
from api.main import app

if __name__ == "__main__":
    print("🚀 Starting A2Z DSA Learning System Web Server...")
    print("📊 Dashboard: http://localhost:8000")
    print("🔗 API Docs: http://localhost:8000/docs")
    print("📋 Topics: http://localhost:8000/#topics")
    print("📈 Coverage: http://localhost:8000/#coverage")
    print("📅 Planning: http://localhost:8000/#planning")
    print("\nPress Ctrl+C to stop the server")

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )