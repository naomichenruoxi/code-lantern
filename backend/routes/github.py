# routes/github.py
"""
GitHub OAuth Integration for Code Lantern
Allows users to connect GitHub and analyze repositories directly
"""
import os
import uuid
import shutil
import tempfile
import subprocess
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/api/github/callback")

# Base directory for cloned repos (same as upload.py)
BASE_REPO_DIR = "processed_repos"
os.makedirs(BASE_REPO_DIR, exist_ok=True)

# In-memory token storage (for simplicity - use database/session in production)
# Key: session_id, Value: access_token
token_storage: Dict[str, str] = {}


def cleanup_previous_projects():
    """Remove all previous projects to keep only current one"""
    if os.path.exists(BASE_REPO_DIR):
        for item in os.listdir(BASE_REPO_DIR):
            if item == 'LATEST':
                continue
            item_path = os.path.join(BASE_REPO_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)


@router.get("/github/connect")
async def github_connect(frontend_redirect: Optional[str] = None):
    """
    Initiate GitHub OAuth flow.
    Returns the GitHub authorization URL for the frontend to redirect to.
    
    Args:
        frontend_redirect: Optional URL to redirect to after OAuth completion
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="GitHub OAuth not configured. Set GITHUB_CLIENT_ID in .env"
        )
    
    # Build OAuth authorization URL
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "repo read:user",  # Access to repos and user info
        "state": frontend_redirect or "http://localhost:3000"  # Store frontend URL in state
    }
    
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    
    return {
        "status": "ok",
        "auth_url": auth_url,
        "message": "Redirect user to auth_url to authorize GitHub access"
    }


@router.get("/github/callback")
async def github_callback(code: str = Query(...), state: Optional[str] = None):
    """
    Handle GitHub OAuth callback.
    Exchanges authorization code for access token.
    
    Args:
        code: Authorization code from GitHub
        state: Original state (contains frontend redirect URL)
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub OAuth not configured"
        )
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            },
            headers={"Accept": "application/json"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = response.json()
        
        if "error" in token_data:
            raise HTTPException(
                status_code=400,
                detail=f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}"
            )
        
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
    
    # Generate session ID and store token
    session_id = str(uuid.uuid4())
    token_storage[session_id] = access_token
    
    # Redirect back to frontend with session ID
    frontend_url = state or "http://localhost:5173"
    # Use & if URL already has query params, otherwise use ?
    separator = "&" if "?" in frontend_url else "?"
    redirect_url = f"{frontend_url}{separator}github_session={session_id}"
    
    return RedirectResponse(url=redirect_url)


@router.get("/github/repos")
async def list_github_repos(session_id: str = Query(...)):
    """
    List repositories for the authenticated user.
    
    Args:
        session_id: Session ID from OAuth callback
    """
    access_token = token_storage.get(session_id)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please reconnect GitHub.")
    
    async with httpx.AsyncClient() as client:
        # Get user's repositories
        response = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params={
                "sort": "updated",
                "direction": "desc",
                "per_page": 50,
                "type": "all"
            }
        )
        
        if response.status_code == 401:
            # Token expired or revoked
            del token_storage[session_id]
            raise HTTPException(status_code=401, detail="GitHub token expired. Please reconnect.")
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch repositories")
        
        repos = response.json()
    
    # Transform to simplified format
    repo_list = [
        {
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "owner": repo["owner"]["login"],
            "description": repo["description"],
            "private": repo["private"],
            "language": repo["language"],
            "updated_at": repo["updated_at"],
            "default_branch": repo["default_branch"],
            "clone_url": repo["clone_url"],
            "html_url": repo["html_url"]
        }
        for repo in repos
    ]
    
    return {
        "status": "ok",
        "count": len(repo_list),
        "repositories": repo_list
    }


@router.post("/github/clone/{owner}/{repo}")
async def clone_and_analyze(
    owner: str,
    repo: str,
    session_id: str = Query(...),
    branch: Optional[str] = None
):
    """
    Clone a GitHub repository and prepare it for analysis.
    
    Args:
        owner: Repository owner username
        repo: Repository name
        session_id: Session ID from OAuth callback
        branch: Optional branch to clone (defaults to default branch)
    """
    access_token = token_storage.get(session_id)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please reconnect GitHub.")
    
    # Clean up previous projects
    cleanup_previous_projects()
    
    # Generate unique repo id
    repo_id = str(uuid.uuid4())
    extract_path = os.path.join(BASE_REPO_DIR, repo_id)
    
    try:
        # Clone using authenticated URL
        clone_url = f"https://x-access-token:{access_token}@github.com/{owner}/{repo}.git"
        
        # Shallow clone for speed (--depth 1 gets all files, just skips history)
        cmd = ["git", "clone", "--depth", "1"]
        if branch:
            cmd.extend(["--branch", branch])
        cmd.extend([clone_url, extract_path])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute should be enough for shallow clone
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clone repository: {result.stderr}"
            )
        
        # Remove .git directory to save space and avoid issues
        git_dir = os.path.join(extract_path, ".git")
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
        
        # Record latest repo id
        try:
            latest_ptr = os.path.join(BASE_REPO_DIR, 'LATEST')
            with open(latest_ptr, 'w') as lp:
                lp.write(repo_id)
        except Exception:
            pass
        
        # Save project metadata including name
        try:
            import json
            project_name = repo  # Use repo name as project name
            metadata = {
                "project_name": project_name,
                "full_name": f"{owner}/{repo}",
                "source": "github",
                "owner": owner,
                "branch": branch or "default"
            }
            metadata_path = os.path.join(extract_path, "project_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass
        
        return {
            "status": "ok",
            "repo_id": repo_id,
            "project_name": project_name if 'project_name' in dir() else repo,
            "repository": f"{owner}/{repo}",
            "branch": branch or "default",
            "extracted_to": extract_path,
            "message": "Repository cloned. Call /api/analyze/{repo_id} to analyze."
        }
    
    except subprocess.TimeoutExpired:
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        raise HTTPException(status_code=504, detail="Clone timeout - repository may be too large")
    
    except Exception as e:
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        raise HTTPException(status_code=500, detail=f"Clone failed: {str(e)}")


@router.get("/github/status")
async def github_status(session_id: Optional[str] = None):
    """
    Check GitHub connection status.
    
    Args:
        session_id: Optional session ID to check
    """
    if not session_id:
        return {
            "status": "ok",
            "connected": False,
            "message": "No session provided"
        }
    
    access_token = token_storage.get(session_id)
    if not access_token:
        return {
            "status": "ok",
            "connected": False,
            "message": "Session expired or invalid"
        }
    
    # Verify token is still valid
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        if response.status_code == 200:
            user = response.json()
            return {
                "status": "ok",
                "connected": True,
                "user": {
                    "login": user["login"],
                    "name": user.get("name"),
                    "avatar_url": user["avatar_url"]
                }
            }
        else:
            del token_storage[session_id]
            return {
                "status": "ok",
                "connected": False,
                "message": "Token expired"
            }


@router.post("/github/disconnect")
async def github_disconnect(session_id: str = Query(...)):
    """
    Disconnect GitHub session.
    
    Args:
        session_id: Session ID to invalidate
    """
    if session_id in token_storage:
        del token_storage[session_id]
    
    return {
        "status": "ok",
        "message": "GitHub disconnected successfully"
    }
