"""
Pydantic schemas for the /generate-roadmap endpoint.
"""

from pydantic import BaseModel, Field
from typing import List


class ProjectImprovement(BaseModel):
    """A single project improvement suggestion."""
    area: str = Field(..., description="Area of improvement (e.g., Architecture, Security)")
    current_issue: str = Field(..., description="Description of current problem")
    recommended_improvement: str = Field(..., description="Specific actionable improvement")


class RoadmapPhase(BaseModel):
    """A single phase in the roadmap."""
    phase: str = Field(..., description="Phase name (e.g., 'Month1', 'Month2')")
    focus: List[str] = Field(..., description="Main skills to focus on in this phase")
    topics: List[str] = Field(..., description="Specific topics to learn")
    projects: List[str] = Field(..., description="Practical project ideas")


class RoadmapResponse(BaseModel):
    """Complete roadmap response."""
    userId: str = Field(..., description="User ID from the request")
    roadmap_duration: str = Field(..., description="Total duration (e.g., '6 months')")
    project_improvements: List[ProjectImprovement] = Field(..., description="Project improvement suggestions")
    roadmap: List[RoadmapPhase] = Field(..., description="List of roadmap phases")
    mermaid_code: str = Field(..., description="Mermaid diagram code for visualization")