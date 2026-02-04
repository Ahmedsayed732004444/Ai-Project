"""
Roadmap generation service using Groq AI.
Analyzes user data and creates personalized learning roadmap.
"""

import logging
import json
from app.schemas.roadmap_schema import RoadmapResponse
from app.services.llm_service import call_llm
from app.utils.helpers import extract_json_from_llm_response

logger = logging.getLogger(__name__)

_ROADMAP_PROMPT_TEMPLATE = """
You are an expert career advisor and technical mentor specializing in software development.

Analyze the following user data and create a personalized learning roadmap:

USER DATA:
{user_data}

ANALYSIS REQUIREMENTS:
1. Assess the user's current level (Junior/Mid-level) based on:
   - Skills they already have
   - Years of experience
   - Education background
   - Existing projects/certifications

2. Create a 3-6 month roadmap that includes:
   - Skills to strengthen (from existing skills)
   - New skills to learn (based on market demand and career progression)
   - Practical projects suitable for their level
   - Learning directions aligned with current job market

3. Structure the roadmap in phases (monthly or bi-weekly)

4. Create a Mermaid diagram showing the complete roadmap flow

IMPORTANT RULES:
- Return ONLY valid JSON matching the exact schema below
- No markdown fences, no extra text, no explanations outside JSON
- Be specific and actionable
- Focus on practical, hands-on learning
- Consider current tech industry trends (2024-2025)
- For backend developers, emphasize: microservices, cloud, Docker, CI/CD, testing
- Include real project ideas (not just "build a project")

REQUIRED JSON SCHEMA:
{{
  "userId": "<user_id>",
  "roadmap_duration": "3-6 months",
  "roadmap": [
    {{
      "phase": "Month 1" or "Week 1-2",
      "focus": ["Main skill 1", "Main skill 2"],
      "topics": ["Specific topic A", "Specific topic B", "..."],
      "projects": ["Concrete project idea with description"]
    }}
  ],
  "mermaid_code": "graph TD\\nA[Start] --> B[Month 1]\\nB --> C[Month 2]\\n..."
}}

MERMAID DIAGRAM REQUIREMENTS:
- Use "graph TD" for top-down flow
- Include all phases
- Show skill progression
- Use proper Mermaid syntax (no special characters that break syntax)
- Make it clear and readable
- Example structure:
  graph TD
    Start[Current Level: Junior] --> Month1[Month 1: Foundation]
    Month1 --> Month2[Month 2: Intermediate]
    Month2 --> Month3[Month 3: Advanced]
    Month3 --> End[Target Level: Mid-Level]

Now analyze and create the roadmap:
"""


async def generate_roadmap(user_data: dict, user_id: str) -> RoadmapResponse:
    """
    Generate personalized roadmap based on user data.
    
    Args:
        user_data: User's CV data (skills, education, experience, etc.)
        user_id: User identifier
        
    Returns:
        RoadmapResponse with complete learning roadmap
    """
    
    # Format user data for better readability
    user_data_str = json.dumps(user_data, indent=2, ensure_ascii=False)
    
    prompt = _ROADMAP_PROMPT_TEMPLATE.format(
        user_data=user_data_str
    )
    
    logger.info(f"Generating roadmap for user: {user_id}")
    
    # Call LLM
    raw_response: str = await call_llm(prompt)
    
    # Parse JSON response
    try:
        parsed: dict = extract_json_from_llm_response(raw_response)
    except Exception as exc:
        logger.error("Failed to parse LLM JSON response:\n%s", raw_response)
        raise RuntimeError("LLM returned invalid JSON.") from exc
    
    # Ensure userId is set
    if "userId" not in parsed or not parsed["userId"]:
        parsed["userId"] = user_id
    
    # Validate with Pydantic
    try:
        roadmap = RoadmapResponse.model_validate(parsed)
    except Exception as exc:
        logger.error("Pydantic validation error: %s", exc)
        raise ValueError(f"Roadmap data does not match schema: {exc}") from exc
    
    logger.info(f"Roadmap generated successfully for user {user_id}")
    logger.info(f"Duration: {roadmap.roadmap_duration}, Phases: {len(roadmap.roadmap)}")
    
    return roadmap


def _assess_user_level(skills: list[str], experience: list[dict]) -> str:
    """
    Quick assessment of user level based on skills and experience.
    Helper function for more accurate roadmap generation.
    """
    
    # Count experience years
    total_years = len(experience)
    
    # Advanced skills indicators
    advanced_skills = {
        "microservices", "kubernetes", "docker", "ci/cd", "azure", "aws",
        "system design", "architecture", "redis", "rabbitmq", "kafka",
        "mongodb", "postgresql", "elasticsearch"
    }
    
    skills_lower = [s.lower() for s in skills]
    advanced_count = sum(1 for skill in skills_lower if any(adv in skill for adv in advanced_skills))
    
    # Determine level
    if total_years == 0 and advanced_count < 2:
        return "Junior"
    elif total_years <= 2 and advanced_count < 4:
        return "Junior-Mid"
    elif total_years <= 4 or advanced_count >= 4:
        return "Mid-level"
    else:
        return "Senior"
