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
You are an expert career advisor and technical mentor specializing in .NET software development.

Analyze the following user data and create a personalized learning roadmap:

USER DATA:
{user_data}

ANALYSIS REQUIREMENTS:
1. Assess the user's current level based on:
   - Skills they already have
   - Years of experience
   - Education background
   - Existing projects/certifications

2. Create a 3-6 month roadmap (EXACTLY 6 phases) for Junior → Mid-Level .NET Developer that includes:
   - Skills to strengthen from existing skills
   - New skills to learn within .NET Ecosystem ONLY
   - NO Node.js, NestJS, or non-.NET technologies
   - Focus on: ASP.NET Core, EF Core, Clean Architecture, CQRS, MediatR, Docker, Azure, Testing, Security
   - Practical projects suitable for their level

3. Also provide project improvements based on the current CV Parser project structure

CRITICAL MERMAID REQUIREMENTS:
- Node names MUST NOT contain spaces or hyphens
- Use underscore _ or camelCase only
- Example: Month1, Month2, Month_1, ProjectCleanArch
- NO special characters that break Mermaid syntax

REQUIRED JSON SCHEMA (STRICT):
{{
  "userId": "{user_id}",
  "roadmap_duration": "6 months",
  "project_improvements": [
    {{
      "area": "Architecture/Database/Security/Testing/etc",
      "current_issue": "Detailed description of current problem in the CV Parser project",
      "recommended_improvement": "Specific actionable improvement within .NET ecosystem"
    }}
  ],
  "roadmap": [
    {{
      "phase": "Month1",
      "focus": ["Main .NET skill 1", "Main .NET skill 2"],
      "topics": ["Specific .NET topic A", "Specific .NET topic B", "..."],
      "projects": ["Concrete .NET project idea with clear description"]
    }}
  ],
  "mermaid_code": "graph TD\\nStart[Current: Junior] --> Month1[Month 1: Topic]\\nMonth1 --> Month2[Month 2: Topic]\\nMonth2 --> Month3[Month 3: Topic]\\nMonth3 --> Month4[Month 4: Topic]\\nMonth4 --> Month5[Month 5: Topic]\\nMonth5 --> Month6[Month 6: Topic]\\nMonth6 --> End[Target: MidLevel]\\n\\nMonth1 -.-> P1[Project: Name]\\nMonth2 -.-> P2[Project: Name]\\nMonth3 -.-> P3[Project: Name]\\nMonth4 -.-> P4[Project: Name]\\nMonth5 -.-> P5[Project: Name]\\nMonth6 -.-> P6[Project: Name]"
}}

IMPORTANT RULES:
- Return ONLY valid JSON matching the exact schema above
- NO markdown fences, NO extra text, NO explanations outside JSON
- MUST include exactly 10 project_improvements (covering Architecture, Database, Security, Testing, Validation, Logging, Error Handling, API Design, Dependency Injection, Code Quality)
- MUST include exactly 6 roadmap phases (Month1 through Month6)
- Each phase should have 8-10 specific topics
- Each phase should have 3-5 concrete project ideas
- Focus on .NET ecosystem only: ASP.NET Core, EF Core, C#, Azure, Docker, xUnit, FluentValidation, MediatR, Serilog, etc.
- Mermaid code MUST use node names without spaces or hyphens (use Month1, Month2, etc.)
- All project improvements must be based on the current Python CV Parser project and suggest .NET best practices

MERMAID SYNTAX RULES (CRITICAL):
- Use ONLY alphanumeric characters and underscores in node IDs
- Correct: Month1, Month2, P1, P2, Start, End, MidLevel
- WRONG: Month-1, Month 1, Project-Clean, Project Clean
- NO spaces, NO hyphens in node identifiers

Now analyze the user data and create the roadmap:
"""


async def generate_roadmap(user_data: dict, user_id: str) -> RoadmapResponse:
    """
    Generate personalized roadmap based on user data.
    
    Args:
        user_data: User's CV data (skills, education, experience, etc.)
        user_id: User identifier
        
    Returns:
        RoadmapResponse with complete learning roadmap and project improvements
    """
    
    # Format user data for better readability
    user_data_str = json.dumps(user_data, indent=2, ensure_ascii=False)
    
    prompt = _ROADMAP_PROMPT_TEMPLATE.format(
        user_data=user_data_str,
        user_id=user_id
    )
    
    logger.info(f"Generating comprehensive roadmap for user: {user_id}")
    
    # Call LLM with increased token limit for comprehensive response
    raw_response: str = await call_llm(prompt, max_tokens=4000)
    
    # Parse JSON response
    try:
        parsed: dict = extract_json_from_llm_response(raw_response)
    except Exception as exc:
        logger.error("Failed to parse LLM JSON response:\n%s", raw_response)
        raise RuntimeError("LLM returned invalid JSON.") from exc
    
    # Ensure userId is set
    if "userId" not in parsed or not parsed["userId"]:
        parsed["userId"] = user_id
    
    # Ensure roadmap_duration is set
    if "roadmap_duration" not in parsed:
        parsed["roadmap_duration"] = "6 months"
    
    # Validate mermaid code doesn't have invalid characters
    if "mermaid_code" in parsed:
        mermaid = parsed["mermaid_code"]
        # Check for common errors
        if "Month-" in mermaid or "Month " in mermaid:
            logger.warning("Fixing mermaid code with invalid node names")
            mermaid = mermaid.replace("Month-", "Month")
            mermaid = mermaid.replace("Month ", "Month")
            parsed["mermaid_code"] = mermaid
    
    # Validate with Pydantic
    try:
        roadmap = RoadmapResponse.model_validate(parsed)
    except Exception as exc:
        logger.error("Pydantic validation error: %s", exc)
        logger.error("Parsed data: %s", json.dumps(parsed, indent=2))
        raise ValueError(f"Roadmap data does not match schema: {exc}") from exc
    
    logger.info(f"Roadmap generated successfully for user {user_id}")
    logger.info(f"Duration: {roadmap.roadmap_duration}, Phases: {len(roadmap.roadmap)}")
    logger.info(f"Project improvements: {len(roadmap.project_improvements)}")
    
    return roadmap


def _assess_user_level(skills: list[str], experience: list[dict]) -> str:
    """
    Quick assessment of user level based on skills and experience.
    Helper function for more accurate roadmap generation.
    """
    
    # Count experience years
    total_years = len(experience)
    
    # Advanced .NET skills indicators
    advanced_skills = {
        "clean architecture", "cqrs", "mediatr", "ddd", "microservices",
        "azure", "docker", "kubernetes", "ci/cd", "devops",
        "event sourcing", "message queues", "rabbitmq", "redis",
        "elasticsearch", "application insights", "serilog"
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