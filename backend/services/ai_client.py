"""
Unified AI client supporting Gemini (primary) and OpenAI (fallback).
Includes caching, rate limiting, retry logic, and prompt injection protection.
"""
import os
import time
import hashlib
import json
from typing import Optional, Dict, Any, List
from functools import lru_cache
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
from backend.utils.config import get_secret
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
AI_PROVIDER = get_secret("AI_PROVIDER", "gemini")
GEMINI_MODEL = get_secret("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")
CACHE_TTL = int(get_secret("CACHE_TTL_SECONDS", "3600"))

# ── API Key Resolvers ─────────────────────────────────────────────────────────
def get_gemini_api_key() -> str:
    """Gets the Gemini API key, prioritizing user input in session state."""
    try:
        import streamlit as st
        if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
            key = st.session_state["gemini_api_key"].strip()
            if key and not key.startswith("your_"):
                return key
    except Exception:
        pass
    return get_secret("GEMINI_API_KEY", "")

def get_openai_api_key() -> str:
    """Gets the OpenAI API key, prioritizing user input in session state."""
    try:
        import streamlit as st
        if "openai_api_key" in st.session_state and st.session_state["openai_api_key"]:
            key = st.session_state["openai_api_key"].strip()
            if key and not key.startswith("your_"):
                return key
    except Exception:
        pass
    return get_secret("OPENAI_API_KEY", "")

def has_api_key() -> bool:
    """Check if either Gemini or OpenAI API keys are configured."""
    return bool(get_gemini_api_key() or get_openai_api_key())

def verify_gemini_connection(api_key: str) -> tuple[bool, str]:
    """Tests the Gemini API connection with a given key."""
    if not api_key:
        return False, "API Key is empty."
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Ping", generation_config={"max_output_tokens": 5})
        if response.text:
            return True, "Connected successfully."
        return False, "Received empty response from Gemini API."
    except Exception as e:
        logger.error(f"Gemini connection test failed: {e}")
        return False, str(e)

# ── Response cache (TTL-based) ────────────────────────────────────────────────
_response_cache: TTLCache = TTLCache(maxsize=200, ttl=CACHE_TTL)

# ── Rate limiting ─────────────────────────────────────────────────────────────
_rate_limit_per_min = int(get_secret("RATE_LIMIT_PER_MINUTE", "30"))
_request_timestamps: List[float] = []


def _check_rate_limit() -> None:
    """Simple sliding window rate limiter."""
    global _request_timestamps
    now = time.time()
    _request_timestamps = [t for t in _request_timestamps if now - t < 60]
    if len(_request_timestamps) >= _rate_limit_per_min:
        raise RuntimeError(
            f"Rate limit exceeded. Max {_rate_limit_per_min} requests/minute."
        )
    _request_timestamps.append(now)


def _sanitize_prompt(prompt: str) -> str:
    """Basic prompt injection protection."""
    injection_patterns = [
        "ignore previous instructions",
        "ignore all prior instructions",
        "forget your instructions",
        "you are now",
        "act as",
        "jailbreak",
    ]
    prompt_lower = prompt.lower()
    for pattern in injection_patterns:
        if pattern in prompt_lower:
            logger.warning(f"Potential prompt injection detected: '{pattern}'")
            prompt = prompt.replace(pattern, "[filtered]")
    return prompt


def _cache_key(prompt: str, **kwargs) -> str:
    """Generate deterministic cache key from prompt and params."""
    key_data = json.dumps({"prompt": prompt, **kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


# ── Gemini Client ─────────────────────────────────────────────────────────────

def _get_gemini_client():
    """Lazily initialize Gemini client."""
    try:
        import google.generativeai as genai
        key = get_gemini_api_key()
        if not key:
            raise ValueError("GEMINI_API_KEY not set in environment or session state.")
        genai.configure(api_key=key)
        return genai.GenerativeModel(GEMINI_MODEL)
    except ImportError:
        raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_gemini(prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Call Gemini API with retry logic."""
    import google.generativeai as genai
    model = _get_gemini_client()
    config = genai.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    response = model.generate_content(prompt, generation_config=config)
    return response.text


# ── OpenAI Client ─────────────────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_openai(prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Call OpenAI API with retry logic."""
    try:
        from openai import OpenAI
        key = get_openai_api_key()
        if not key:
            raise ValueError("OPENAI_API_KEY not set in environment or session state.")
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except ImportError:
        raise ImportError("openai not installed. Run: pip install openai")


# ── Public Interface ──────────────────────────────────────────────────────────

def generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    use_cache: bool = True,
    system_context: Optional[str] = None,
) -> str:
    """
    Primary AI text generation function.

    Args:
        prompt: User prompt text
        temperature: Creativity level (0.0-1.0)
        max_tokens: Maximum response length
        use_cache: Whether to cache the response
        system_context: Optional system context prepended to prompt

    Returns:
        Generated text response
    """
    prompt = _sanitize_prompt(prompt)

    if system_context:
        full_prompt = f"{system_context}\n\n{prompt}"
    else:
        full_prompt = prompt

    # Check cache
    if use_cache:
        key = _cache_key(full_prompt, temperature=temperature)
        if key in _response_cache:
            logger.debug("Cache hit for AI response.")
            return _response_cache[key]

    _check_rate_limit()

    try:
        gemini_key = get_gemini_api_key()
        openai_key = get_openai_api_key()
        if AI_PROVIDER == "gemini" and gemini_key:
            result = _call_gemini(full_prompt, temperature, max_tokens)
            logger.info(f"Gemini API call successful ({len(result)} chars)")
        elif openai_key:
            result = _call_openai(full_prompt, temperature, max_tokens)
            logger.info(f"OpenAI API call successful ({len(result)} chars)")
        else:
            # Demo mode — return structured placeholder
            result = _demo_response(prompt)
            logger.warning("No API key configured. Running in demo mode.")
    except Exception as e:
        logger.error(f"AI API call failed: {e}")
        # Try fallback
        openai_key = get_openai_api_key()
        if AI_PROVIDER == "gemini" and openai_key:
            logger.info("Falling back to OpenAI...")
            result = _call_openai(full_prompt, temperature, max_tokens)
        else:
            raise

    if use_cache:
        _response_cache[_cache_key(full_prompt, temperature=temperature)] = result

    return result


def generate_json(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    fallback: Optional[Dict] = None,
) -> Dict:
    """
    Generate structured JSON from AI. Parses response safely.

    Returns:
        Parsed JSON dict or fallback if parsing fails
    """
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, "
        "no code blocks. Just raw JSON."
    )
    raw = generate_text(json_prompt, temperature=temperature, max_tokens=max_tokens)

    # Clean response
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed: {e}. Raw: {raw[:200]}")
        return fallback or {}


def _demo_response(prompt: str) -> str:
    """Returns structured demo data when no API key is configured."""
    return json.dumps({
        "status": "demo_mode",
        "message": "Configure GEMINI_API_KEY in AI Settings to enable AI features.",
        "prompt_preview": prompt[:100],
    })


def embed_text(texts: List[str]) -> List[List[float]]:
    """
    Generate vector embeddings for a list of texts using the configured AI provider.

    Args:
        texts: List of strings to embed

    Returns:
        List of embedding vectors (each vector is a list of floats)
    """
    if not texts:
        return []

    _check_rate_limit()

    gemini_key = get_gemini_api_key()
    openai_key = get_openai_api_key()

    # Try Gemini if configured as primary
    if AI_PROVIDER == "gemini" and gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            # models/text-embedding-004 is the standard Gemini embedding model
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document"
            )
            if "embedding" in result:
                return result["embedding"]
            else:
                raise ValueError("Embedding key not found in Gemini response.")
        except Exception as e:
            logger.warning(f"Gemini embedding failed: {e}. Trying OpenAI fallback if available...")
            if openai_key:
                return _embed_openai(texts)
            raise
    # Otherwise try OpenAI
    elif openai_key:
        try:
            return _embed_openai(texts)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    else:
        raise ValueError("No AI provider API key configured for embeddings.")


def _embed_openai(texts: List[str]) -> List[List[float]]:
    """Helper to call OpenAI embedding API."""
    from openai import OpenAI
    client = OpenAI(api_key=get_openai_api_key())
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [data.embedding for data in response.data]


def is_ai_configured() -> bool:
    """Check if any AI provider is properly configured."""
    return has_api_key()


def get_ai_provider_info() -> Dict:
    """Return current AI provider configuration info."""
    return {
        "provider": AI_PROVIDER if is_ai_configured() else "demo",
        "model": GEMINI_MODEL if AI_PROVIDER == "gemini" else OPENAI_MODEL,
        "configured": is_ai_configured(),
        "cache_ttl": CACHE_TTL,
        "rate_limit_per_min": _rate_limit_per_min,
    }
