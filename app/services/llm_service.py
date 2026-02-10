"""
LLM service using Groq.
"""

import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

_client = Groq(api_key=settings.groq_api_key)


async def call_llm(prompt: str, max_tokens: int = None) -> str:
    """Send prompt to Groq and return response."""
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env file.")

    # Use provided max_tokens or default from settings
    token_limit = max_tokens if max_tokens is not None else settings.llm_max_tokens

    logger.info("Calling Groq AI model: %s (max_tokens: %d)", settings.groq_model, token_limit)

    try:
        response = _client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert .NET career advisor and technical mentor. Return ONLY valid JSON with no markdown formatting.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=token_limit,
            temperature=0.0,
        )
    except Exception as exc:
        logger.exception("Groq API call failed.")
        raise RuntimeError(f"LLM call failed: {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Groq returned empty response.")

    logger.info("Received %d characters from Groq.", len(content))
    return content