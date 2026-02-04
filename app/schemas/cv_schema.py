"""
Pydantic schemas matching Career_Path.Entities
These match exactly with your .NET entity classes.
"""

from pydantic import BaseModel, Field


# ─── Education (Owned Entity) ────────────────────────────────

class Education(BaseModel):
    """Matches Career_Path.Entities.Education"""
    degree: str = ""
    field: str = ""
    institution: str = ""
    year: str = ""


# ─── Experience (Owned Entity) ───────────────────────────────

class Experience(BaseModel):
    """Matches Career_Path.Entities.Experience"""
    job_title: str = Field(default="", alias="jobTitle")
    company: str = ""
    start_date: str = Field(default="", alias="startDate")
    end_date: str = Field(default="", alias="endDate")
    description: str = ""

    class Config:
        populate_by_name = True


# ─── ModelExtration Response ─────────────────────────────────

class ModelExtrationResponse(BaseModel):
    """
    Matches Career_Path.Entities.ModelExtration
    This is what the AI will extract from CVs.
    """
    full_name: str = Field(default="", alias="fullName")
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: list[str] = []
    education: list[Education] = []
    experience: list[Experience] = []
    certifications: list[str] = []
    languages: list[str] = []

    class Config:
        populate_by_name = True


# ─── Database Entity (for saving) ────────────────────────────

class ModelExtrationCreate(BaseModel):
    """
    Schema for creating ModelExtration in database.
    Includes ApplicationUserId.
    """
    application_user_id: str = Field(..., alias="applicationUserId")
    full_name: str = Field(default="", alias="fullName")
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: list[str] = []
    education: list[Education] = []
    experience: list[Experience] = []
    certifications: list[str] = []
    languages: list[str] = []

    class Config:
        populate_by_name = True


# ─── Error Response ──────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
