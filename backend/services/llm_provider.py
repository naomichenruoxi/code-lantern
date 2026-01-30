# backend/services/llm_provider.py
"""
Multi-LLM Provider with Fallback Chain
Supports: Groq → Gemini → Cohere with automatic failover
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    COHERE = "cohere"


class LLMError(Exception):
    """Custom exception for LLM errors"""
    def __init__(self, provider: str, message: str, is_rate_limit: bool = False):
        self.provider = provider
        self.message = message
        self.is_rate_limit = is_rate_limit
        super().__init__(f"[{provider}] {message}")


# Provider configurations
PROVIDER_CONFIGS = {
    LLMProvider.GROQ: {
        "api_key_env": "GROQ_API_KEY",
        "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
    },
    LLMProvider.GEMINI: {
        "api_key_env": "GEMINI_API_KEY",
        "model": "gemini-1.5-flash",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
    },
    LLMProvider.COHERE: {
        "api_key_env": "COHERE_API_KEY",
        "model": "command-r",
        "endpoint": "https://api.cohere.ai/v1/chat",
    },
}

# Priority order for fallback
PROVIDER_PRIORITY = [LLMProvider.GROQ, LLMProvider.GEMINI, LLMProvider.COHERE]

# Track which providers are currently available (not rate-limited)
_provider_status: Dict[LLMProvider, bool] = {p: True for p in LLMProvider}


def get_available_providers() -> List[LLMProvider]:
    """Get list of providers that have API keys configured"""
    available = []
    for provider in PROVIDER_PRIORITY:
        config = PROVIDER_CONFIGS[provider]
        api_key = os.getenv(config["api_key_env"])
        if api_key and api_key.strip():
            available.append(provider)
    return available


async def call_groq(prompt: str, max_tokens: int = 500) -> str:
    """Call Groq API"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError("groq", "API key not configured")
    
    config = PROVIDER_CONFIGS[LLMProvider.GROQ]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            config["endpoint"],
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 429:
            raise LLMError("groq", "Rate limit exceeded", is_rate_limit=True)
        
        if response.status_code != 200:
            raise LLMError("groq", f"API error: {response.status_code}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def call_gemini(prompt: str, max_tokens: int = 500) -> str:
    """Call Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("gemini", "API key not configured")
    
    config = PROVIDER_CONFIGS[LLMProvider.GEMINI]
    url = f"{config['endpoint']}/{config['model']}:generateContent?key={api_key}"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": max_tokens
                }
            }
        )
        
        if response.status_code == 429:
            raise LLMError("gemini", "Rate limit exceeded", is_rate_limit=True)
        
        if response.status_code != 200:
            raise LLMError("gemini", f"API error: {response.status_code}")
        
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise LLMError("gemini", "No response generated")
        
        return candidates[0]["content"]["parts"][0]["text"]


async def call_cohere(prompt: str, max_tokens: int = 500) -> str:
    """Call Cohere API"""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise LLMError("cohere", "API key not configured")
    
    config = PROVIDER_CONFIGS[LLMProvider.COHERE]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            config["endpoint"],
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config["model"],
                "message": prompt,
                "temperature": 0.3,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 429:
            raise LLMError("cohere", "Rate limit exceeded", is_rate_limit=True)
        
        if response.status_code != 200:
            raise LLMError("cohere", f"API error: {response.status_code}")
        
        data = response.json()
        return data.get("text", "")


# Provider call functions mapping
PROVIDER_CALLS = {
    LLMProvider.GROQ: call_groq,
    LLMProvider.GEMINI: call_gemini,
    LLMProvider.COHERE: call_cohere,
}


async def generate_with_fallback(prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
    """
    Generate text using available LLM providers with automatic fallback.
    Returns dict with 'text' and 'provider' used.
    """
    available = get_available_providers()
    
    if not available:
        return {
            "text": "",
            "provider": "none",
            "error": "No LLM providers configured. Add API keys to .env"
        }
    
    errors = []
    
    for provider in available:
        try:
            print(f"[LLM] Trying {provider.value}...")
            call_fn = PROVIDER_CALLS[provider]
            text = await call_fn(prompt, max_tokens)
            print(f"[LLM] Success with {provider.value}")
            return {
                "text": text,
                "provider": provider.value,
                "error": None
            }
        except LLMError as e:
            errors.append(f"{e.provider}: {e.message}")
            print(f"[LLM] {e.provider} failed: {e.message}")
            if e.is_rate_limit:
                print(f"[LLM] {e.provider} rate limited, trying next...")
            continue
        except Exception as e:
            errors.append(f"{provider.value}: {str(e)}")
            print(f"[LLM] {provider.value} error: {e}")
            continue
    
    # All providers failed
    return {
        "text": "",
        "provider": "none",
        "error": f"All providers failed: {'; '.join(errors)}"
    }


def parse_json_from_response(text: str) -> Optional[Dict]:
    """Extract JSON from LLM response text"""
    try:
        # Find JSON in response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except json.JSONDecodeError:
        pass
    return None
