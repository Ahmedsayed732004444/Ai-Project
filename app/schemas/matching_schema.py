"""
Pydantic schemas for the /match-jobs endpoint.
"""

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    """A single job with its required skills."""
    job_id: str = Field(..., description="Unique identifier for the job.")
    title: str = Field(..., description="Job title.")
    company: str = Field(..., description="Company name.")
    skills: list[str] = Field(..., description="Skills required for this position.")


class MatchJobsRequest(BaseModel):
    """Top-level request body sent to POST /match-jobs."""
    userSkills: list[str] = Field(..., description="Skills the user currently possesses.")
    jobSkills: list[JobInput] = Field(..., description="List of jobs.")


class MatchResult(BaseModel):
    """Per-job match result."""
    job_id: str
    title: str
    company: str
    match_percentage: float = Field(..., description="Percentage of job skills matched.")
    matched_skills: list[str] = Field(..., description="Skills present in both.")
    missing_skills: list[str] = Field(..., description="Skills required but absent.")


class MatchJobsResponse(BaseModel):
    """Top-level response — jobs sorted descending by match_percentage."""
    results: list[MatchResult]
