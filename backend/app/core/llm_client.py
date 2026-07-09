"""
core/llm_client.py — Groq LLM wrapper with streaming + retry logic.

Features:
- Regular completion (for agents)
- Streaming completion (for chat — ChatGPT-style word by word)
- Auto retry on failure
- Configurable model
"""

import asyncio
from groq import Groq, AsyncGroq
from app.core.config import settings
from app.core.logging_config import logger

_sync_client = None
_async_client = None


def get_sync_client() -> Groq:
    global _sync_client
    if not _sync_client:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing in .env file")
        _sync_client = Groq(api_key=settings.GROQ_API_KEY, timeout=settings.LLM_TIMEOUT)
    return _sync_client


def get_async_client() -> AsyncGroq:
    global _async_client
    if not _async_client:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY missing in .env file")
        _async_client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=settings.LLM_TIMEOUT)
    return _async_client


def ask_llm(system_prompt: str, user_prompt: str,
            temperature: float = 0.3, max_tokens: int = 1200) -> str:
    """Synchronous LLM call with retry logic — used by agents."""
    client = get_sync_client()
    last_error = None

    for attempt in range(settings.LLM_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            logger.warning(f"LLM attempt {attempt+1} failed: {e}")
            if attempt < settings.LLM_MAX_RETRIES:
                import time
                time.sleep(0.5 * (attempt + 1))

    raise Exception(f"LLM failed after {settings.LLM_MAX_RETRIES + 1} attempts: {last_error}")


async def ask_llm_stream(system_prompt: str, user_prompt: str,
                          conversation_history: list = None,
                          temperature: float = 0.4, max_tokens: int = 1500):
    """
    Async generator for streaming LLM responses — ChatGPT-style word by word.

    Usage:
        async for chunk in ask_llm_stream(sys, user):
            yield chunk   # each chunk is a string fragment

    conversation_history: list of {"role": "user"/"assistant", "content": "..."}
    for multi-turn memory.
    """
    client = get_async_client()

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history for memory (last 10 messages)
    if conversation_history:
        messages.extend(conversation_history[-10:])

    messages.append({"role": "user", "content": user_prompt})

    try:
        stream = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except Exception as e:
        logger.error(f"LLM streaming failed: {e}")
        yield f"\n\n[AI service error: {str(e)}]"
