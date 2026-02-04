"""
Pydantic schemas for the /generate-roadmap endpoint.
"""

from pydantic import BaseModel, Field


class RoadmapPhase(BaseModel):
    """A single phase in the roadmap."""
    phase: str = Field(..., description="Phase name (e.g., 'Month 1', 'Week 1-2')")
    focus: list[str] = Field(..., description="Main skills to focus on in this phase")
    topics: list[str] = Field(..., description="Specific topics to learn")
    projects: list[str] = Field(..., description="Practical project ideas")


class RoadmapResponse(BaseModel):
    """Complete roadmap response."""
    userId: str = Field(..., description="User ID from the request")
    roadmap_duration: str = Field(..., description="Total duration (e.g., '3-6 months')")
    roadmap: list[RoadmapPhase] = Field(..., description="List of roadmap phases")
    mermaid_code: str = Field(..., description="Mermaid diagram code for visualization")
