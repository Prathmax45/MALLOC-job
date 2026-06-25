"""
Entry point for the FastAPI server.
(Backward compatibility stub for the old Python HTTP server)
"""

import uvicorn

if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
