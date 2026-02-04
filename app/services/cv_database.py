"""
CV Database operations – save and retrieve parsed CVs.

This module shows how to store parsed CV data in SQL Server.
"""

import logging
from datetime import datetime
from typing import Optional

from app.schemas.cv_schema import CVResponse
from app.services.database import execute_non_query, execute_query, execute_scalar

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Save CV to Database
# ─────────────────────────────────────────────


def save_cv_to_database(cv_data: CVResponse, user_id: Optional[int] = None) -> int:
    """
    Save parsed CV data to the database.
    
    Args:
        cv_data: Parsed CV response from the analyzer
        user_id: Optional user ID to associate with this CV
        
    Returns:
        ID of the inserted CV record
        
    Note:
        This assumes you have a table structure. Adjust the SQL based on your schema.
    """
    
    # Example: Insert into a CVs table
    insert_query = """
    INSERT INTO CVs (
        user_id,
        full_name,
        email,
        phone,
        location,
        summary,
        skills,
        created_at
    )
    OUTPUT INSERTED.id
    VALUES (
        :user_id,
        :full_name,
        :email,
        :phone,
        :location,
        :summary,
        :skills,
        :created_at
    )
    """
    
    params = {
        "user_id": user_id,
        "full_name": cv_data.personal_info.full_name,
        "email": cv_data.personal_info.email,
        "phone": cv_data.personal_info.phone,
        "location": cv_data.personal_info.location,
        "summary": cv_data.summary,
        "skills": ", ".join(cv_data.skills),  # Store as comma-separated
        "created_at": datetime.utcnow(),
    }
    
    cv_id = execute_scalar(insert_query, params)
    logger.info("CV saved to database with ID: %s", cv_id)
    
    # Save education entries
    for edu in cv_data.education:
        save_education(cv_id, edu)
    
    # Save experience entries
    for exp in cv_data.experience:
        save_experience(cv_id, exp)
    
    return cv_id


def save_education(cv_id: int, education: dict):
    """Save education entry linked to a CV."""
    query = """
    INSERT INTO Education (
        cv_id, degree, field, institution, year
    ) VALUES (
        :cv_id, :degree, :field, :institution, :year
    )
    """
    params = {
        "cv_id": cv_id,
        "degree": education.get("degree", ""),
        "field": education.get("field", ""),
        "institution": education.get("institution", ""),
        "year": education.get("year", ""),
    }
    execute_non_query(query, params)


def save_experience(cv_id: int, experience: dict):
    """Save experience entry linked to a CV."""
    query = """
    INSERT INTO Experience (
        cv_id, job_title, company, start_date, end_date, description
    ) VALUES (
        :cv_id, :job_title, :company, :start_date, :end_date, :description
    )
    """
    params = {
        "cv_id": cv_id,
        "job_title": experience.get("job_title", ""),
        "company": experience.get("company", ""),
        "start_date": experience.get("start_date", ""),
        "end_date": experience.get("end_date", ""),
        "description": experience.get("description", ""),
    }
    execute_non_query(query, params)


# ─────────────────────────────────────────────
# Retrieve CV from Database
# ─────────────────────────────────────────────


def get_cv_by_id(cv_id: int) -> Optional[dict]:
    """
    Retrieve a CV record by ID.
    
    Args:
        cv_id: ID of the CV to retrieve
        
    Returns:
        Dictionary with CV data or None if not found
    """
    query = "SELECT * FROM CVs WHERE id = :cv_id"
    results = execute_query(query, {"cv_id": cv_id})
    
    if results:
        return results[0]
    return None


def get_cvs_by_user(user_id: int) -> list[dict]:
    """
    Get all CVs for a specific user.
    
    Args:
        user_id: User ID to search for
        
    Returns:
        List of CV records
    """
    query = "SELECT * FROM CVs WHERE user_id = :user_id ORDER BY created_at DESC"
    return execute_query(query, {"user_id": user_id})


def search_cvs_by_skill(skill: str) -> list[dict]:
    """
    Search for CVs that contain a specific skill.
    
    Args:
        skill: Skill to search for
        
    Returns:
        List of matching CV records
    """
    query = """
    SELECT * FROM CVs 
    WHERE skills LIKE :skill_pattern
    ORDER BY created_at DESC
    """
    return execute_query(query, {"skill_pattern": f"%{skill}%"})
