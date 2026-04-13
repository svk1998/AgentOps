"""
LiteLLM routing helper.

Centralises the logic that maps a model string to the correct
api_base / api_key kwargs so callers don't need to know provider details.

Supported prefixes
------------------
  ollama/<name>          → Ollama REST API  (OLLAMA_BASE_URL)
  openai/<name>          → vLLM endpoint  (VLLM_API_BASE)
  groq/<name>            → Groq cloud  (GROQ_API_KEY)
  anything else          → LiteLLM default cloud routing (OpenAI, Anthropic, …)
"""
import litellm

from app.core.config import settings


def _routing_kwargs(model: str) -> dict:
    """Return extra kwargs that litellm needs for self-hosted or keyed providers."""
    if model.startswith("ollama/"):
        return {"api_base": settings.OLLAMA_BASE_URL}

    if model.startswith("openai/") and settings.VLLM_API_BASE:
        kwargs: dict = {"api_base": settings.VLLM_API_BASE}
        if settings.VLLM_API_KEY:
            kwargs["api_key"] = settings.VLLM_API_KEY
        return kwargs

    if model.startswith("groq/") and settings.GROQ_API_KEY:
        return {"api_key": settings.GROQ_API_KEY}

    return {}


async def chat(model: str, messages: list[dict], **kwargs) -> tuple[str, dict]:
    """
    Single non-streaming LiteLLM call.

    Returns (content, usage_dict).
    """
    kwargs.update(_routing_kwargs(model))
    response = await litellm.acompletion(model=model, messages=messages, **kwargs)
    content = response.choices[0].message.content or ""
    usage: dict = {}
    if hasattr(response, "usage") and response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    return content.strip(), usage


async def stream(model: str, messages: list[dict], **kwargs):
    """
    Streaming LiteLLM call.

    Returns an async iterable of chunks (same as litellm.acompletion with stream=True).
    """
    kwargs.update(_routing_kwargs(model))
    return await litellm.acompletion(model=model, messages=messages, stream=True, **kwargs)
