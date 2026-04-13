"""
GET /v1/models — returns all models available for use.

Cloud models are hard-coded.
Ollama models are fetched live from OLLAMA_BASE_URL/api/tags.
vLLM models are fetched live from VLLM_API_BASE/v1/models.
If a self-hosted source is unreachable it is silently skipped.
"""
from fastapi import APIRouter, Depends
import httpx
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/models", tags=["models"])

# ── Static cloud catalogue ────────────────────────────────────────────────────

_CLOUD_MODELS = [
    {"id": "gpt-4o",                        "name": "GPT-4o",                    "provider": "openai"},
    {"id": "gpt-4o-mini",                   "name": "GPT-4o Mini",               "provider": "openai"},
    {"id": "claude-opus-4-6",               "name": "Claude Opus 4.6",           "provider": "anthropic"},
    {"id": "claude-sonnet-4-6",             "name": "Claude Sonnet 4.6",         "provider": "anthropic"},
    {"id": "claude-haiku-4-5",              "name": "Claude Haiku 4.5",          "provider": "anthropic"},
    {"id": "groq/llama-3.3-70b-versatile",  "name": "Llama 3.3 70B Versatile",  "provider": "groq"},
    {"id": "groq/llama-3.1-8b-instant",     "name": "Llama 3.1 8B Instant",     "provider": "groq"},
    {"id": "groq/mixtral-8x7b-32768",       "name": "Mixtral 8x7B",             "provider": "groq"},
    {"id": "groq/gemma2-9b-it",             "name": "Gemma 2 9B",               "provider": "groq"},
]


class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _fetch_ollama_models() -> list[ModelInfo]:
    """
    Call Ollama's tag listing API.
    Returns an empty list if Ollama is not running or not configured.
    """
    base = settings.OLLAMA_BASE_URL.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{base}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [
                ModelInfo(
                    id=f"ollama/{m['name']}",
                    name=m["name"],
                    provider="ollama",
                )
                for m in data.get("models", [])
            ]
    except Exception:
        return []


async def _fetch_vllm_models() -> list[ModelInfo]:
    """
    Call the vLLM /v1/models endpoint.
    Returns an empty list if VLLM_API_BASE is not set or unreachable.
    """
    if not settings.VLLM_API_BASE:
        return []

    base = settings.VLLM_API_BASE.rstrip("/")
    headers = {}
    if settings.VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.VLLM_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{base}/v1/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [
                ModelInfo(
                    id=f"openai/{m['id']}",
                    name=m["id"],
                    provider="vllm",
                )
                for m in data.get("data", [])
            ]
    except Exception:
        return []


# ── Route ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ModelInfo])
async def list_models(
    current_user: User = Depends(get_current_user),
):
    """Return available cloud models plus any self-hosted models that are reachable."""
    # Filter out providers whose API keys are not configured
    cloud = [
        ModelInfo(**m)
        for m in _CLOUD_MODELS
        if not (m["provider"] == "groq" and not settings.GROQ_API_KEY)
        and not (m["provider"] == "openai" and not settings.OPENAI_API_KEY)
        and not (m["provider"] == "anthropic" and not settings.ANTHROPIC_API_KEY)
    ]

    ollama, vllm = await _fetch_ollama_models(), await _fetch_vllm_models()

    return cloud + ollama + vllm
