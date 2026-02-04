"""
LLM service using Groq.
"""

import logging
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

_client = Groq(api_key=settings.groq_api_key)


async def call_llm(prompt: str) -> str:
    """Send prompt to Groq and return response."""
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in .env file.")

    logger.info("Calling Groq AI model: %s", settings.groq_model)

    try:
        response = _client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert CV parser. Return ONLY valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=settings.llm_max_tokens,
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
