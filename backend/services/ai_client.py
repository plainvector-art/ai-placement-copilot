"""
Unified AI client supporting Gemini (primary) and OpenAI (fallback).
Includes caching, rate limiting, retry logic, circuit breakers, and schema validation.
"""
import os
import time
import hashlib
import json
import threading
from typing import Optional, Dict, Any, List
from functools import lru_cache
from cachetools import TTLCache
from loguru import logger
from backend.utils.config import get_secret
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
AI_PROVIDER = get_secret("AI_PROVIDER", "gemini")
GEMINI_MODEL_DEFAULT = get_secret("GEMINI_MODEL", "gemini-1.5-flash")
OPENAI_MODEL = get_secret("OPENAI_MODEL", "gpt-4o-mini")
CACHE_TTL = int(get_secret("CACHE_TTL_SECONDS", "3600"))

PRIORITIZED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# ── Circuit Breaker Pattern ──────────────────────────────────────────────────
class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 3, recovery_time: float = 60.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.lock = threading.Lock()

    def record_success(self):
        with self.lock:
            self.failures = 0
            self.state = "CLOSED"

    def record_failure(self):
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(f"Circuit Breaker for {self.name} opened due to {self.failures} failures.")

    def can_execute(self) -> bool:
        with self.lock:
            if self.state == "CLOSED":
                return True
            if self.state == "OPEN":
                # Check if cooldown elapsed
                if time.time() - self.last_failure_time > self.recovery_time:
                    self.state = "HALF-OPEN"
                    logger.info(f"Circuit Breaker for {self.name} entered HALF-OPEN state. Testing connection...")
                    return True
                return False
            return True


_gemini_breaker = CircuitBreaker("Gemini")
_openai_breaker = CircuitBreaker("OpenAI")

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

def discover_gemini_models(api_key: str = None) -> List[str]:
    """Configures Gemini and queries available generative models."""
    if not api_key:
        api_key = get_gemini_api_key()
    if not api_key:
        return []
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        models = []
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                name = m.name.split("/")[-1]
                models.append(name)
        return models
    except Exception as e:
        logger.warning(f"Failed to discover Gemini models dynamically: {e}")
        return []

def get_best_available_model(models_list: List[str] = None) -> str:
    """Finds the best model available from the list based on priority."""
    if not models_list:
        try:
            import streamlit as st
            models_list = st.session_state.get("discovered_gemini_models")
        except Exception:
            pass
    
    if not models_list:
        models_list = discover_gemini_models()
        
    if not models_list:
        models_list = PRIORITIZED_MODELS
        
    for priority in PRIORITIZED_MODELS:
        for m in models_list:
            if priority in m:
                return m
                
    return models_list[0] if models_list else GEMINI_MODEL_DEFAULT

def get_selected_gemini_model() -> str:
    """Gets the currently selected Gemini model, checking session state first."""
    try:
        import streamlit as st
        if "gemini_model" in st.session_state and st.session_state["gemini_model"]:
            return st.session_state["gemini_model"]
    except Exception:
        pass
    return get_best_available_model()

def get_ai_provider() -> str:
    """Returns the active AI provider based on configuration and key presence."""
    if get_gemini_api_key() and _gemini_breaker.can_execute():
        return "gemini"
    elif get_openai_api_key() and _openai_breaker.can_execute():
        return "openai"
    return "demo"

def get_gemini_client(model_name: str = None):
    """Lazily initialize Gemini model client."""
    try:
        import google.generativeai as genai
        key = get_gemini_api_key()
        if not key:
            raise ValueError("GEMINI_API_KEY not configured.")
        genai.configure(api_key=key)
        if not model_name:
            model_name = get_selected_gemini_model()
        return genai.GenerativeModel(model_name)
    except ImportError:
        raise ImportError("google-generativeai is not installed.")

def verify_gemini_connection(api_key: str) -> tuple[bool, str]:
    """Tests the Gemini API connection with a given key."""
    if not api_key:
        return False, "API Key is empty."
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_name = get_best_available_model()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            "Ping", 
            generation_config={"max_output_tokens": 5},
            request_options={"timeout": 15.0}
        )
        if response.text:
            return True, "Connected successfully."
        return False, "Received empty response from Gemini API."
    except Exception as e:
        logger.error(f"Gemini connection test failed: {e}")
        return False, str(e)

def verify_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """Tests connection/credentials for Gemini or OpenAI."""
    if not api_key:
        return False, "API Key is empty."
    provider = provider.lower()
    if provider == "gemini":
        return verify_gemini_connection(api_key)
    elif provider == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=15.0)
            client.models.list()
            return True, "Connected successfully."
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False, str(e)
    return False, f"Unknown provider: {provider}"

# ── Response cache (TTL-based & Thread-safe) ──────────────────────────────────
_response_cache: TTLCache = TTLCache(maxsize=200, ttl=CACHE_TTL)
_cache_lock = threading.Lock()

# ── Rate limiting ─────────────────────────────────────────────────────────────
_rate_limit_per_min = int(get_secret("RATE_LIMIT_PER_MINUTE", "30"))
_request_timestamps: List[float] = []
_rate_limit_lock = threading.Lock()


def _check_rate_limit() -> None:
    """Sliding window rate limiter."""
    global _request_timestamps
    with _rate_limit_lock:
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


# ── Core Generation Pipeline with Circuit Breakers & Retries ──────────────────

def generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    use_cache: bool = True,
    system_context: Optional[str] = None,
) -> str:
    """Primary AI text generation with circuit breaker, discovery, retries, and OpenAI fallbacks."""
    start_time = time.time()
    prompt = _sanitize_prompt(prompt)
    full_prompt = f"{system_context}\n\n{prompt}" if system_context else prompt

    # Thread-safe Cache Read
    if use_cache:
        key = _cache_key(full_prompt, temperature=temperature)
        with _cache_lock:
            if key in _response_cache:
                logger.info("Cache hit for AI text generation request")
                return _response_cache[key]

    _check_rate_limit()

    gemini_key = get_gemini_api_key()
    openai_key = get_openai_api_key()
    
    primary_model = get_selected_gemini_model()
    result = None

    # 1. Try Gemini (if breaker is CLOSED or HALF-OPEN)
    if gemini_key and _gemini_breaker.can_execute():
        import google.generativeai as genai
        
        models_to_try = [primary_model]
        discovered = []
        try:
            import streamlit as st
            discovered = st.session_state.get("discovered_gemini_models", [])
        except Exception:
            pass
        if not discovered:
            discovered = PRIORITIZED_MODELS
            
        for m in discovered:
            if m not in models_to_try:
                models_to_try.append(m)

        for current_model in models_to_try:
            try:
                logger.info(f"Attempting Gemini request on model: {current_model}")
                genai.configure(api_key=gemini_key)
                model_obj = genai.GenerativeModel(current_model)
                config = genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                
                # Request execution with explicit timeout (30 seconds)
                resp_start = time.time()
                response = model_obj.generate_content(
                    full_prompt, 
                    generation_config=config, 
                    request_options={"timeout": 30.0}
                )
                result = response.text
                latency = time.time() - resp_start
                
                _gemini_breaker.record_success()
                logger.info(f"Gemini success using {current_model}. Latency: {latency:.2f}s")
                break
            except Exception as e:
                _gemini_breaker.record_failure()
                logger.warning(f"Gemini attempt failed for model {current_model}: {e}")

    # 2. Try OpenAI Fallback (if breaker is CLOSED or HALF-OPEN)
    if not result and openai_key and _openai_breaker.can_execute():
        try:
            logger.info("Initiating OpenAI fallback routing...")
            from openai import OpenAI
            client = OpenAI(api_key=openai_key, timeout=30.0)
            
            resp_start = time.time()
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            result = response.choices[0].message.content
            latency = time.time() - resp_start
            
            _openai_breaker.record_success()
            logger.info(f"OpenAI fallback success. Latency: {latency:.2f}s")
        except Exception as e:
            _openai_breaker.record_failure()
            logger.error(f"OpenAI fallback routing failed: {e}")

    # 3. Fallback to Demo Mode
    if not result:
        logger.warning("All AI providers bypassed or failed. Yielding Demo Mode response.")
        result = _demo_response(prompt)

    total_latency = time.time() - start_time
    logger.info(f"Total AI routing complete. Total Latency: {total_latency:.2f}s")

    # Thread-safe Cache Write
    if use_cache and result:
        with _cache_lock:
            _response_cache[_cache_key(full_prompt, temperature=temperature)] = result

    return result


def validate_schema(data: dict, schema: dict) -> bool:
    """Strictly validates types and existence of dictionary keys."""
    if not isinstance(data, dict):
        return False
    for key, val_type in schema.items():
        if key not in data:
            return False
        if val_type == list and not isinstance(data[key], list):
            return False
        if val_type == dict and not isinstance(data[key], dict):
            return False
        if val_type == str and not isinstance(data[key], str):
            return False
        if val_type == int and not isinstance(data[key], (int, float)):
            return False
    return True


def generate_json(
    prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
    fallback: Optional[Dict] = None,
    schema: Optional[Dict] = None,
) -> Dict:
    """Generate structured JSON from AI. Safely parses output and executes schema-validation retries."""
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, "
        "no code blocks. Just raw JSON."
    )
    
    # Retry up to 3 times on parse or schema validation mismatch
    for attempt in range(3):
        raw = generate_text(json_prompt, temperature=temperature, max_tokens=max_tokens, use_cache=(attempt == 0))
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
            if schema:
                if validate_schema(parsed, schema):
                    return parsed
                else:
                    logger.warning(f"Schema mismatch on attempt {attempt + 1}. Retrying...")
            else:
                return parsed
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decoding failed on attempt {attempt + 1}: {e}")

    logger.error("JSON parsing/schema validation failed after 3 attempts. Returning fallback.")
    return fallback or {}


def _demo_response(prompt: str) -> str:
    """Returns structured demo data when no API key is configured."""
    return json.dumps({
        "status": "demo_mode",
        "message": "Configure GEMINI_API_KEY in AI Settings to enable AI features.",
        "prompt_preview": prompt[:100],
    })


def embed_text(texts: List[str]) -> List[List[float]]:
    """Generate vector embeddings with fallback options and timeout boundaries."""
    if not texts:
        return []

    _check_rate_limit()

    gemini_key = get_gemini_api_key()
    openai_key = get_openai_api_key()

    # 1. Try Gemini
    if gemini_key and _gemini_breaker.can_execute():
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=texts,
                task_type="retrieval_document",
                request_options={"timeout": 30.0}
            )
            if "embedding" in result:
                _gemini_breaker.record_success()
                return result["embedding"]
            else:
                raise ValueError("Embedding key not found in Gemini response.")
        except Exception as e:
            _gemini_breaker.record_failure()
            logger.warning(f"Gemini embedding failed: {e}. Trying OpenAI fallback...")

    # 2. Try OpenAI Fallback
    if openai_key and _openai_breaker.can_execute():
        try:
            resp = _embed_openai(texts)
            _openai_breaker.record_success()
            return resp
        except Exception as e:
            _openai_breaker.record_failure()
            logger.warning(f"OpenAI embedding fallback failed: {e}. Using local fallback...")

    # 3. Local Hash-based fallback
    return _generate_local_vectors(texts)


def _embed_openai(texts: List[str]) -> List[List[float]]:
    """Helper to call OpenAI embedding API."""
    from openai import OpenAI
    client = OpenAI(api_key=get_openai_api_key(), timeout=30.0)
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [data.embedding for data in response.data]


def _generate_local_vectors(texts: List[str], dimension: int = 768) -> List[List[float]]:
    """Generates simple local text vectors using hash-based word representation for ranker."""
    import numpy as np
    vectors = []
    for text in texts:
        vec = np.zeros(dimension)
        words = text.lower().split()
        if not words:
            vectors.append(vec.tolist())
            continue
        for word in words:
            idx = int(hashlib.sha256(word.encode()).hexdigest(), 16) % dimension
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        vectors.append(vec.tolist())
    return vectors


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Centralized text embedding generation with fallback and local options."""
    return embed_text(texts)


def is_ai_configured() -> bool:
    """Check if any AI provider is properly configured."""
    return has_api_key()


def get_ai_provider_info() -> Dict:
    """Return current AI provider configuration info."""
    return {
        "provider": get_ai_provider(),
        "model": get_selected_gemini_model() if get_ai_provider() == "gemini" else OPENAI_MODEL,
        "configured": is_ai_configured(),
        "cache_ttl": CACHE_TTL,
        "rate_limit_per_min": _rate_limit_per_min,
    }
