from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.analysis import router as analysis_router
from routes.github import router as github_router

app = FastAPI(title="Code Lantern API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Documentation
"""
Code Lantern Backend API

Frontend-ready endpoints for project architecture analysis.

## Workflow:
1. POST /api/upload - Upload ZIP file
2. GET /api/analyze/{repo_id} - Generate architecture map

## Response Format:
All responses follow consistent JSON format with status indicators.
"""

@app.get("/")
async def root():
    """API health check and info"""
    return {
        "status": "ok",
        "service": "Code Lantern API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "analyze": "/api/analyze/{repo_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}

app.include_router(upload_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(github_router, prefix="/api")

import os

# ... imports ...

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        reload_dirs=["routes", "core"],
        reload_excludes=["processed_repos/*"]
    )
