"""
CV-analysis service using Groq AI.
"""

import logging
from pydantic import ValidationError
from app.schemas.cv_schema import ModelExtrationResponse
from app.services.llm_service import call_llm
from app.utils.helpers import extract_json_from_llm_response

logger = logging.getLogger(__name__)

_EXTRACTION_PROMPT_TEMPLATE = """
You are given the following CV / resume text:

---
{cv_text}
---

Extract the information and return it as a single JSON object matching this schema:

{{
  "full_name": "<string>",
  "email": "<string>",
  "phone": "<string>",
  "location": "<string>",
  "summary": "<string>",
  "skills": ["<skill>", ...],
  "education": [
    {{
      "degree": "<Bachelor, Master, PhD, etc>",
      "field": "<major/field of study>",
      "institution": "<university name>",
      "year": "<graduation year or attendance years>"
    }}
  ],
  "experience": [
    {{
      "job_title": "<title>",
      "company": "<company name>",
      "start_date": "<e.g. Jan 2020>",
      "end_date": "<e.g. Mar 2023 or Present>",
      "description": "<brief summary of responsibilities>"
    }}
  ],
  "certifications": ["<certification name>", ...],
  "languages": ["<language + level>", ...]
}}

Rules:
- Return ONLY valid JSON. No markdown fences, no extra text.
- If a section is missing, return empty string or empty list.
- Use camelCase for field names (e.g., "full_name", "job_title").
"""


async def analyse_cv(cv_text: str) -> ModelExtrationResponse:
    """
    Analyze CV text and return structured ModelExtration data.
    
    Args:
        cv_text: Plain text extracted from uploaded CV
        
    Returns:
        ModelExtrationResponse matching Career_Path.Entities.ModelExtration
    """
    if not cv_text.strip():
        raise ValueError("CV text is empty — nothing to analyse.")

    prompt = _EXTRACTION_PROMPT_TEMPLATE.format(cv_text=cv_text)
    raw_response: str = await call_llm(prompt)

    try:
        parsed: dict = extract_json_from_llm_response(raw_response)
    except Exception as exc:
        logger.error("Failed to parse LLM JSON response:\n%s", raw_response)
        raise RuntimeError("LLM returned invalid JSON.") from exc

    try:
        cv_response = ModelExtrationResponse.model_validate(parsed)
    except ValidationError as exc:
        logger.error("Pydantic validation error: %s", exc)
        raise ValueError(f"Data does not match schema: {exc}") from exc

    logger.info("CV analysis complete - extracted data for: %s", cv_response.full_name)
    return cv_response
