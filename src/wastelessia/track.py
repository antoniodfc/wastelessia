import asyncio
import functools
import inspect
import time
from datetime import datetime, timezone
from typing import Any, Optional

from ._pricing import calculate_cost
from ._sender import send_event_async


def track(
    team: Optional[str] = None,
    feature: Optional[str] = None,
    env: Optional[str] = None,
    client: Optional[str] = None,
):
    """Decorator that captures LLM usage metadata and sends it to Wastelessia.

    Usage::

        @track(team="backend", feature="search", env="prod")
        def call_llm(prompt):
            return anthropic.messages.create(...)
    """
    tags = {k: v for k, v in {"team": team, "feature": feature, "env": env, "client": client}.items() if v is not None}

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start = time.monotonic()
                success = True
                result = None
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    success = False
                    raise
                finally:
                    _maybe_send(result, time.monotonic() - start, success, tags)
            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.monotonic()
            success = True
            result = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                success = False
                raise
            finally:
                _maybe_send(result, time.monotonic() - start, success, tags)
        return sync_wrapper

    return decorator


def _maybe_send(response: Any, elapsed: float, success: bool, tags: dict) -> None:
    usage = _extract_usage(response)
    if usage is None:
        return
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": usage["model"],
        "tokens_in": usage["tokens_in"],
        "tokens_out": usage["tokens_out"],
        "cost_usd": calculate_cost(usage["model"], usage["tokens_in"], usage["tokens_out"]),
        "duration_ms": int(elapsed * 1000),
        "success": success,
        "tags": tags,
    }
    send_event_async(event)


def _extract_usage(response: Any) -> Optional[dict]:
    if response is None:
        return None

    usage = getattr(response, "usage", None)
    model = getattr(response, "model", None)
    if usage is None or model is None:
        return None

    # Anthropic SDK: input_tokens / output_tokens
    if hasattr(usage, "input_tokens"):
        return {"model": model, "tokens_in": usage.input_tokens, "tokens_out": usage.output_tokens}

    # OpenAI SDK: prompt_tokens / completion_tokens
    if hasattr(usage, "prompt_tokens"):
        return {"model": model, "tokens_in": usage.prompt_tokens, "tokens_out": usage.completion_tokens}

    return None
