#!/usr/bin/env python3
"""
Local development server startup script
"""
import os
import sys
from pathlib import Path

# Load local environment
from dotenv import load_dotenv

# Load .env.local file
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded local environment from {env_path}")
else:
    print(f"[WARN] Local environment file not found: {env_path}")
    print("Using default settings...")

# Now import and run the main application
from main_enhanced import app

if __name__ == "__main__":
    import uvicorn
    print("[START] Starting DIY Assistant Local Development Server...")
    print(f"[DB] Database: {os.getenv('DATABASE_URL', 'Not configured')}")
    print(f"[API] OpenAI API: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured (will use mock data)'}")
    print(f"[CORS] CORS Origins: {os.getenv('CORS_ORIGINS', 'Default')}")
    print("\n[URL] Backend will be available at: http://localhost:8001")
    print("[DOCS] API docs at: http://localhost:8001/docs")
    print("\n[STOP] Press Ctrl+C to stop\n")
    
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )