# routes/analysis.py
"""
Analysis routes for Code Lantern.
Uses tree-sitter based analyzer from core for accurate AST analysis.
"""

import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Import the enhanced tree-sitter analyzer
from core.analyzer import (
    analyze_file_detailed,
    analyze_repo_detailed,
    find_source_files,
    get_function_code,
    detect_language,
    SUPPORTED_EXTENSIONS,
    IGNORED_DIRECTORIES,
)

# Import LLM provider and rate limiter
from services.llm_provider import generate_with_fallback, parse_json_from_response
from services.rate_limiter import rate_limiter


# -------------------------------
# API Endpoints
# -------------------------------

@router.get("/analyze/{repo_id}")
async def analyze_project(repo_id: str):
    """Analyze uploaded project and generate architecture map using tree-sitter AST."""
    
    # Find the repo directory
    repo_path = os.path.join("processed_repos", repo_id)
    
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Use enhanced tree-sitter analyzer
    architecture_map = analyze_repo_detailed(repo_path)
    
    if not architecture_map["listOfFiles"]:
        raise HTTPException(status_code=404, detail="No source files found")
    
    # Save to JSON file
    json_path = os.path.join(repo_path, "architecture_map.json")
    with open(json_path, 'w') as f:
        json.dump(architecture_map, f, indent=2)
    
    return {
        "status": "ok",
        "repo_id": repo_id,
        "files_analyzed": architecture_map["totalFiles"],
        "functions_found": architecture_map["totalFunctions"],
        "json_path": json_path,
        "architecture_map": {"listOfFiles": architecture_map["listOfFiles"]}
    }


@router.get("/files/{repo_id}")
async def get_project_files(repo_id: str):
    """Get list of files in the project for file browser"""
    repo_path = os.path.join("processed_repos", repo_id)
    
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Read the architecture map if it exists
    json_path = os.path.join(repo_path, "architecture_map.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Architecture map not found. Run analysis first.")
    
    with open(json_path, 'r') as f:
        architecture_map = json.load(f)
    
    # Transform for file browser view
    files_with_functions = []
    for file_data in architecture_map.get('listOfFiles', []):
        functions = file_data.get('listOfFunctions', [])
        file_info = {
            "filePath": file_data['filePath'],
            "language": file_data.get('language', 'unknown'),
            "functionCount": len(functions),
            "functions": [func.get('name', func['functionName'].split('-')[-1]) for func in functions]
        }
        files_with_functions.append(file_info)
    
    return {
        "status": "ok",
        "repo_id": repo_id,
        "totalFiles": len(files_with_functions),
        "files": files_with_functions
    }


@router.get("/function/{repo_id}")
async def get_function_details(repo_id: str, file_path: str, function_name: str, request: Request):
    """Get detailed description of a specific function with rate limiting"""
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check cache first (doesn't count against rate limit)
    cached = rate_limiter.get_cached_function(repo_id, file_path, function_name)
    if cached:
        print(f"[Rate Limiter] Cache hit for {function_name}")
        return {
            "status": "ok",
            "repo_id": repo_id,
            "file_path": file_path,
            "details": cached,
            "cached": True
        }
    
    # Check rate limit
    allowed, current, max_allowed = rate_limiter.check_function_detail_limit(client_ip, repo_id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "message": f"Rate limit reached. You can analyze up to {max_allowed} functions per project.",
                "current_usage": current,
                "max_allowed": max_allowed,
                "tip": "Upload a new project to reset your limit, or try again later."
            }
        )
    
    repo_path = os.path.join("processed_repos", repo_id)
    
    print(f"[DEBUG] get_function_details called:")
    print(f"  repo_id: {repo_id}")
    print(f"  file_path: {file_path}")
    print(f"  function_name: {function_name}")
    print(f"  client_ip: {client_ip}")
    print(f"  usage: {current + 1}/{max_allowed}")
    
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail=f"Repository not found: {repo_id}")
    
    # Try multiple path variations to find the file
    full_file_path = None
    paths_tried = []
    
    # Variation 1: Direct path
    direct_path = os.path.join(repo_path, file_path)
    paths_tried.append(direct_path)
    if os.path.exists(direct_path):
        full_file_path = direct_path
    
    # Variation 2: Try without leading directory (common with cloned repos)
    if not full_file_path and '/' in file_path:
        parts = file_path.split('/')
        for i in range(len(parts)):
            partial_path = '/'.join(parts[i:])
            test_path = os.path.join(repo_path, partial_path)
            paths_tried.append(test_path)
            if os.path.exists(test_path):
                full_file_path = test_path
                break
    
    # Variation 3: Search recursively for the filename
    if not full_file_path:
        filename = os.path.basename(file_path)
        for root, dirs, files in os.walk(repo_path):
            if filename in files:
                full_file_path = os.path.join(root, filename)
                break
    
    if not full_file_path:
        raise HTTPException(
            status_code=404, 
            detail=f"File not found: {file_path}. Tried: {paths_tried[:3]}"
        )
    
    # Use tree-sitter based function code extraction
    function_code = get_function_code(full_file_path, function_name)
    
    if not function_code:
        raise HTTPException(status_code=404, detail="Function not found in file")
    
    # Determine file type for display
    lang = detect_language(full_file_path)
    file_type = SUPPORTED_EXTENSIONS.get(os.path.splitext(file_path)[1].lower(), 'unknown')
    
    # Record usage BEFORE making AI call
    rate_limiter.record_function_detail(client_ip, repo_id)
    
    # Generate description using AI
    function_description = await generate_function_description(function_code, function_name, file_path)
    
    # Cache the result
    rate_limiter.cache_function(repo_id, file_path, function_name, function_description)
    
    # Get updated usage
    used, max_limit = rate_limiter.get_function_detail_usage(client_ip, repo_id)
    
    return {
        "status": "ok",
        "repo_id": repo_id,
        "file_path": file_path,
        "details": function_description,
        "cached": False,
        "rate_limit": {
            "used": used,
            "max": max_limit,
            "remaining": max_limit - used
        }
    }


@router.get("/function")
async def get_function_details_latest(file_path: str, function_name: str, request: Request):
    """Get function details for the latest uploaded repo"""
    repo_id = get_latest_repo_id()
    if not repo_id:
        raise HTTPException(status_code=404, detail="No repo uploaded yet")
    return await get_function_details(repo_id, file_path, function_name, request)


@router.get("/project-summary/{repo_id}")
async def get_project_summary(repo_id: str):
    """Generate comprehensive AI-powered project summary and analytics"""
    repo_path = os.path.join("processed_repos", repo_id)
    
    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Read project metadata if it exists
    project_name = repo_id  # Default to repo_id
    project_source = "unknown"
    metadata_path = os.path.join(repo_path, "project_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                project_name = metadata.get("project_name", repo_id)
                project_source = metadata.get("source", "unknown")
        except Exception:
            pass
    
    # Read the architecture map
    json_path = os.path.join(repo_path, "architecture_map.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Architecture map not found. Run analysis first.")
    
    with open(json_path, 'r') as f:
        architecture_map = json.load(f)
    
    # Analyze project statistics - now using tree-sitter derived data
    project_stats = analyze_project_statistics(architecture_map, repo_path)
    
    # Generate AI summary
    ai_summary = await generate_project_ai_summary(project_stats, architecture_map)
    
    return {
        "status": "ok",
        "repo_id": repo_id,
        "project_name": project_name,
        "project_source": project_source,
        "project_stats": project_stats,
        "ai_summary": ai_summary,
        "generated_at": get_current_timestamp()
    }


# -------------------------------
# AI-Powered Analysis Functions
# -------------------------------

async def generate_function_description(function_code: str, function_name: str, file_path: str) -> Dict[str, str]:
    """Generate function description using multi-LLM provider with automatic fallback"""
    
    prompt = f"""Analyze this function and provide a structured description:

File: {file_path}
Function Code:
```
{function_code}
```

Please provide:
1. Function Name: {function_name}
2. Inputs: What parameters does this function take? (include types if visible)
3. Outputs: What does this function return? (include type if visible)
4. Description: What does this function do? (2-3 sentences, clear and concise)

Format your response as JSON:
{{
    "function_name": "{function_name}",
    "inputs": "description of inputs/parameters",
    "outputs": "description of return value",
    "description": "clear description of what the function does"
}}"""

    # Use the multi-LLM provider with automatic fallback
    result = await generate_with_fallback(prompt, max_tokens=500)
    
    if result["error"]:
        print(f"[AI] All providers failed: {result['error']}")
        return {
            "function_name": function_name,
            "inputs": "Analysis: Check function parameters in code",
            "outputs": "Analysis: Check return statements in code",
            "description": f"Function '{function_name}' in '{file_path}'. AI analysis unavailable."
        }
    
    # Parse JSON from response
    parsed = parse_json_from_response(result["text"])
    if parsed:
        parsed["_provider"] = result["provider"]  # Include which provider was used
        return parsed
    
    # Fallback if JSON parsing fails
    return {
        "function_name": function_name,
        "inputs": "Analysis: Check function parameters in code",
        "outputs": "Analysis: Check return statements in code",
        "description": f"Function '{function_name}' in '{file_path}'. AI response could not be parsed."
    }


# -------------------------------
# Project Statistics (Enhanced)
# -------------------------------

def analyze_project_statistics(architecture_map: dict, repo_path: str) -> dict:
    """Analyze comprehensive project statistics using tree-sitter derived data"""
    list_of_files = architecture_map.get('listOfFiles', [])
    
    # File analysis
    total_files = len(list_of_files)
    file_extensions = {}
    total_lines = 0
    
    # Function analysis - now uses accurate tree-sitter complexity
    total_functions = 0
    total_calls = 0
    complexity_values = []
    
    # Language detection
    language_stats = {}
    
    for file_data in list_of_files:
        file_path = file_data.get('filePath', '')
        functions = file_data.get('listOfFunctions', [])
        
        # Use totalLines from analyzer if available
        total_lines += file_data.get('totalLines', 0)
        
        # Get file extension
        ext = os.path.splitext(file_path)[1]
        if ext:
            file_extensions[ext] = file_extensions.get(ext, 0) + 1
            
            # Map extensions to languages
            lang_mapping = {
                '.py': 'Python',
                '.js': 'JavaScript', '.jsx': 'JavaScript',
                '.ts': 'TypeScript', '.tsx': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.h': 'C++', '.hpp': 'C++',
                '.c': 'C',
                '.go': 'Go',
                '.rs': 'Rust'
            }
            lang_name = lang_mapping.get(ext)
            if lang_name:
                language_stats[lang_name] = language_stats.get(lang_name, 0) + 1
        
        # Function statistics - use tree-sitter complexity
        total_functions += len(functions)
        for func in functions:
            calls = func.get('calls', [])
            total_calls += len(calls)
            # Use the accurate tree-sitter calculated complexity
            complexity = func.get('complexity', 1)
            complexity_values.append(complexity)
    
    # Calculate percentages
    total_language_files = sum(language_stats.values())
    language_percentages = {}
    if total_language_files > 0:
        for lang, count in language_stats.items():
            language_percentages[lang] = round((count / total_language_files) * 100, 1)
    
    # Calculate complexity metrics using actual AST complexity
    avg_complexity = sum(complexity_values) / len(complexity_values) if complexity_values else 0
    max_complexity = max(complexity_values) if complexity_values else 0
    
    # Calculate code health score
    code_health = calculate_code_health_score(total_files, total_functions, avg_complexity, language_stats)
    
    return {
        "file_stats": {
            "total_files": total_files,
            "file_extensions": file_extensions,
            "estimated_lines_of_code": total_lines
        },
        "function_stats": {
            "total_functions": total_functions,
            "total_function_calls": total_calls,
            "average_complexity": round(avg_complexity, 2),
            "max_complexity": max_complexity,
            "functions_per_file": round(total_functions / total_files, 2) if total_files > 0 else 0
        },
        "language_stats": {
            "languages": language_stats,
            "language_percentages": language_percentages,
            "primary_language": max(language_stats, key=language_stats.get) if language_stats else "Unknown"
        },
        "complexity_metrics": {
            "code_health_score": code_health,
            "project_size": categorize_project_size(total_files, total_functions),
            "architecture_complexity": categorize_architecture_complexity(avg_complexity)
        }
    }


def calculate_code_health_score(total_files: int, total_functions: int, avg_complexity: float, language_stats: dict) -> int:
    """Calculate code health score out of 100 - strict and honest evaluation"""
    score = 100
    
    # Penalize for project size issues
    if total_files < 3:
        score -= 20  # Very small project, likely incomplete
    elif total_files > 100:
        score -= 15  # Very large, likely needs better organization
    elif total_files > 50:
        score -= 10
    
    # Strict complexity penalties (using accurate AST-based complexity)
    if avg_complexity > 15:
        score -= 40  # Very high complexity - major refactoring needed
    elif avg_complexity > 10:
        score -= 30  # High complexity
    elif avg_complexity > 7:
        score -= 20  # Moderate-high complexity
    elif avg_complexity > 5:
        score -= 10  # Slightly high complexity
    elif avg_complexity > 3:
        score -= 5   # Room for improvement
    
    # Penalize poor function distribution
    if total_files > 0:
        functions_per_file = total_functions / total_files
        if functions_per_file < 1:
            score -= 15  # Too few functions, might indicate incomplete analysis
        elif functions_per_file > 15:
            score -= 20  # Too many functions per file - needs splitting
        elif functions_per_file > 10:
            score -= 10
        elif functions_per_file < 2 or functions_per_file > 8:
            score -= 5
    
    # Small bonus for multi-language projects (but not much)
    if len(language_stats) > 2:
        score += 3
    
    return max(0, min(100, score))


def categorize_project_size(total_files: int, total_functions: int) -> str:
    """Categorize project size"""
    if total_files <= 5 and total_functions <= 20:
        return "Small"
    elif total_files <= 15 and total_functions <= 60:
        return "Medium"
    elif total_files <= 30 and total_functions <= 150:
        return "Large"
    else:
        return "Enterprise"


def categorize_architecture_complexity(avg_complexity: float) -> str:
    """Categorize architecture complexity"""
    if avg_complexity <= 3:
        return "Simple"
    elif avg_complexity <= 6:
        return "Moderate"
    elif avg_complexity <= 10:
        return "Complex"
    else:
        return "Highly Complex"


async def generate_project_ai_summary(project_stats: dict, architecture_map: dict) -> dict:
    """Generate an AI-powered summary using multi-LLM provider with automatic fallback."""
    
    fs = project_stats.get('file_stats', {})
    fns = project_stats.get('function_stats', {})
    lang = project_stats.get('language_stats', {})
    cmx = project_stats.get('complexity_metrics', {})
    
    prompt = f"""You are a senior software architect reviewing a codebase. Analyze this project and provide insights in JSON format.

Project Statistics:
- Total Files: {fs.get('total_files', 0)}
- Total Functions: {fns.get('total_functions', 0)}
- Lines of Code: {fs.get('estimated_lines_of_code', 0)}
- Primary Language: {lang.get('primary_language', 'Unknown')}
- Languages: {', '.join(lang.get('languages', {}).keys())}
- Average Complexity: {fns.get('average_complexity', 0)}
- Code Health Score: {cmx.get('code_health_score', 0)}/100
- Project Size: {cmx.get('project_size', 'Unknown')}

Provide a comprehensive analysis in this exact JSON format:
{{
    "overview": "2-3 sentence overview of the project architecture and purpose",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
    "architecture_insights": "Brief analysis of the architecture patterns and design",
    "technology_assessment": "Analysis of the technology stack and language choices"
}}"""

    # Use the multi-LLM provider with automatic fallback
    result = await generate_with_fallback(prompt, max_tokens=800)
    
    if result["error"]:
        print(f"[AI] All providers failed: {result['error']}")
        return {
            "source": "static",
            "overview": f"Project with {fs.get('total_files', 0)} files and {fns.get('total_functions', 0)} functions. Primary language: {lang.get('primary_language', 'Unknown')}.",
            "strengths": ["Architecture map generated", "Complexity metrics computed", "Multi-language support"],
            "recommendations": ["Document complex areas", "Add unit tests", "Consider code linting"],
            "architecture_insights": f"Average complexity: {fns.get('average_complexity', 0)}. Health score: {cmx.get('code_health_score', 0)}/100",
            "technology_assessment": f"Primary language: {lang.get('primary_language', 'Unknown')}. Project size: {cmx.get('project_size', 'Unknown')}"
        }
    
    # Parse JSON from response
    parsed = parse_json_from_response(result["text"])
    if parsed:
        parsed["source"] = result["provider"]
        return parsed
    
    # Fallback if JSON parsing fails
    return {
        "source": "static",
        "overview": f"Project with {fs.get('total_files', 0)} files and {fns.get('total_functions', 0)} functions. Primary language: {lang.get('primary_language', 'Unknown')}.",
        "strengths": ["Architecture map generated", "Complexity metrics computed", "Multi-language support"],
        "recommendations": ["Document complex areas", "Add unit tests", "Consider code linting"],
        "architecture_insights": f"Average complexity: {fns.get('average_complexity', 0)}. Health score: {cmx.get('code_health_score', 0)}/100",
        "technology_assessment": f"Primary language: {lang.get('primary_language', 'Unknown')}. Project size: {cmx.get('project_size', 'Unknown')}"
    }


# -------------------------------
# Utility Functions
# -------------------------------

def get_current_timestamp():
    """Get current timestamp"""
    from datetime import datetime
    return datetime.now().isoformat()


BASE_REPO_DIR = os.path.join(os.getcwd(), "processed_repos")


def get_latest_repo_id() -> str | None:
    try:
        latest_ptr = os.path.join(BASE_REPO_DIR, 'LATEST')
        if os.path.exists(latest_ptr):
            with open(latest_ptr, 'r') as f:
                return f.read().strip()
    except Exception:
        return None
    return None


@router.get("/analyze")
async def analyze_latest():
    repo_id = get_latest_repo_id()
    if not repo_id:
        raise HTTPException(status_code=404, detail="No repo uploaded yet")
    return await analyze_project(repo_id)


@router.get("/project-summary")
async def project_summary_latest():
    repo_id = get_latest_repo_id()
    if not repo_id:
        raise HTTPException(status_code=404, detail="No repo uploaded yet")
    return await get_project_summary(repo_id)