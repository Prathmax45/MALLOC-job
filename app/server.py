"""
Entry point for the FastAPI server.
(Backward compatibility stub for the old Python HTTP server)
"""

import sys
from pathlib import Path
import uvicorn

# Ensure the root project directory is in the Python path so uvicorn can find 'app.main'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
