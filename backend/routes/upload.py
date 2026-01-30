
# routes/upload.py
import os
import uuid
import zipfile
import shutil
import time
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

BASE_REPO_DIR = "processed_repos"   # where unzipped repos are stored
os.makedirs(BASE_REPO_DIR, exist_ok=True)

def cleanup_old_projects(max_age_seconds: int = 3600):
    """Remove projects older than max_age_seconds (default 1 hour)"""
    if not os.path.exists(BASE_REPO_DIR):
        return

    now = time.time()
    for item in os.listdir(BASE_REPO_DIR):
        item_path = os.path.join(BASE_REPO_DIR, item)
        
        # Skip LATEST pointer
        if item == 'LATEST':
            continue
            
        try:
            # Check modification time
            mtime = os.path.getmtime(item_path)
            if now - mtime > max_age_seconds:
                print(f"[Cleanup] Removing old project: {item}")
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
        except Exception as e:
            print(f"[Cleanup] Error removing {item}: {e}")

@router.post("/upload")
async def upload_repo(file: UploadFile = File(...)):
    # cleanup old projects
    cleanup_old_projects()

    # validate file type
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are allowed")
    
    # generate unique repo id
    repo_id = str(uuid.uuid4())

    # paths
    zip_path = os.path.join(BASE_REPO_DIR, f"{repo_id}.zip")
    extract_path = os.path.join(BASE_REPO_DIR, repo_id)

    try:
        # save uploaded zip file
        with open(zip_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # unzip into folder
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        # cleanup - remove zip file after extraction
        os.remove(zip_path)

        # Record latest repo id for convenience endpoints
        try:
            latest_ptr = os.path.join(BASE_REPO_DIR, 'LATEST')
            os.makedirs(BASE_REPO_DIR, exist_ok=True)
            with open(latest_ptr, 'w') as lp:
                lp.write(repo_id)
        except Exception:
            pass

        # Save project metadata including name
        try:
            import json
            project_name = os.path.splitext(file.filename)[0]  # Remove .zip extension
            metadata = {
                "project_name": project_name,
                "source": "upload",
                "original_filename": file.filename
            }
            metadata_path = os.path.join(extract_path, "project_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass

        return {
            "status": "ok",
            "repo_id": repo_id,
            "project_name": project_name if 'project_name' in dir() else file.filename,
            "extracted_to": extract_path
        }
    
    except zipfile.BadZipFile:
        # cleanup on error
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        # cleanup on error
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
