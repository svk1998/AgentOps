"""
Agent execution service.

Wraps LiteLLM to run an agent given a Run record.
Tools are resolved from the tool registry and injected as LiteLLM tool definitions.
"""
from collections.abc import Callable

from app.core.config import settings
from app.models.run import Run
from app.services.llm import stream as llm_stream


async def run_agent(
    run: Run,
    emit: Callable,
) -> tuple[dict, dict]:
    """
    Execute an agent run.

    Args:
        run:  The Run ORM instance (agent + input already loaded).
        emit: Async callback to stream log lines — emit(level, message, data).

    Returns:
        (output dict, usage dict)
    """
    agent = run.agent
    model = agent.model or settings.DEFAULT_MODEL
    system_prompt = agent.system_prompt or ""
    parameters = agent.parameters or {}

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": run.input.get("message", "")},
    ]

    await emit("info", f"Starting agent '{agent.name}' with model {model}")

    response = await llm_stream(model, messages, **parameters)

    full_content = ""
    async for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            full_content += delta.content
            await emit("info", delta.content)

    usage = {}
    if hasattr(response, "usage") and response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    await emit("info", "Agent run completed")
    return {"message": full_content}, usage
