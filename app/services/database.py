"""
Database service for ModelExtration table.
Works with existing Career_Path database structure.
"""

import json
import logging
from typing import Optional

from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.schemas.cv_schema import ModelExtrationResponse, ModelExtrationCreate

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Engine and Session
# ─────────────────────────────────────────────────────────────

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        logger.info("Creating database engine for: %s", settings.db_server)
        try:
            _engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                echo=False,
            )
            logger.info("Database engine created successfully.")
        except Exception as exc:
            logger.exception("Failed to create database engine.")
            raise RuntimeError(f"Database connection failed: {exc}") from exc
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def get_db_session():
    """Get a database session."""
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise


# ─────────────────────────────────────────────────────────────
# Connection Testing
# ─────────────────────────────────────────────────────────────

def test_connection() -> bool:
    """Test the database connection."""
    try:
        session = get_db_session()
        result = session.execute(text("SELECT 1"))
        result.fetchone()
        session.close()
        logger.info("Database connection test: SUCCESS")
        return True
    except SQLAlchemyError as exc:
        logger.error("Database connection test: FAILED - %s", exc)
        return False


# ─────────────────────────────────────────────────────────────
# ModelExtration Operations
# ─────────────────────────────────────────────────────────────

def save_model_extration(
    data: ModelExtrationResponse,
    application_user_id: str
) -> int:
    """
    Save ModelExtration to database.
    
    Args:
        data: Parsed CV data from AI
        application_user_id: The user ID from AspNetUsers
        
    Returns:
        ID of the inserted ModelExtration record
    """
    session = get_db_session()
    
    try:
        # Check if user already has ModelExtration
        check_query = text("""
            SELECT Id FROM ModelExtrations 
            WHERE ApplicationUserId = :user_id
        """)
        existing = session.execute(
            check_query, 
            {"user_id": application_user_id}
        ).fetchone()
        
        if existing:
            # Update existing record
            model_id = existing[0]
            logger.info(f"Updating existing ModelExtration {model_id}")
            
            update_query = text("""
                UPDATE ModelExtrations
                SET 
                    FullName = :full_name,
                    Email = :email,
                    Phone = :phone,
                    Location = :location,
                    Summary = :summary,
                    Skills = :skills,
                    Certifications = :certifications,
                    Languages = :languages
                WHERE Id = :id
            """)
            
            session.execute(update_query, {
                "id": model_id,
                "full_name": data.full_name,
                "email": data.email,
                "phone": data.phone,
                "location": data.location,
                "summary": data.summary,
                "skills": json.dumps(data.skills),
                "certifications": json.dumps(data.certifications),
                "languages": json.dumps(data.languages),
            })
            
            # Delete old Education and Experience records
            session.execute(
                text("DELETE FROM Education WHERE ModelExtrationId = :id"),
                {"id": model_id}
            )
            session.execute(
                text("DELETE FROM Experience WHERE ModelExtrationId = :id"),
                {"id": model_id}
            )
            
        else:
            # Insert new record
            logger.info(f"Creating new ModelExtration for user {application_user_id}")
            
            insert_query = text("""
                INSERT INTO ModelExtrations (
                    ApplicationUserId, FullName, Email, Phone, Location,
                    Summary, Skills, Certifications, Languages
                )
                OUTPUT INSERTED.Id
                VALUES (
                    :user_id, :full_name, :email, :phone, :location,
                    :summary, :skills, :certifications, :languages
                )
            """)
            
            result = session.execute(insert_query, {
                "user_id": application_user_id,
                "full_name": data.full_name,
                "email": data.email,
                "phone": data.phone,
                "location": data.location,
                "summary": data.summary,
                "skills": json.dumps(data.skills),
                "certifications": json.dumps(data.certifications),
                "languages": json.dumps(data.languages),
            })
            
            model_id = result.scalar()
        
        # Insert Education records (owned collection)
        for edu in data.education:
            edu_query = text("""
                INSERT INTO Education (
                    ModelExtrationId, Degree, Field, Institution, Year
                ) VALUES (
                    :model_id, :degree, :field, :institution, :year
                )
            """)
            session.execute(edu_query, {
                "model_id": model_id,
                "degree": edu.degree,
                "field": edu.field,
                "institution": edu.institution,
                "year": edu.year,
            })
        
        # Insert Experience records (owned collection)
        for exp in data.experience:
            exp_query = text("""
                INSERT INTO Experience (
                    ModelExtrationId, JobTitle, Company, 
                    StartDate, EndDate, Description
                ) VALUES (
                    :model_id, :job_title, :company,
                    :start_date, :end_date, :description
                )
            """)
            session.execute(exp_query, {
                "model_id": model_id,
                "job_title": exp.job_title,
                "company": exp.company,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description,
            })
        
        session.commit()
        logger.info(f"ModelExtration saved successfully with ID: {model_id}")
        return model_id
        
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to save ModelExtration")
        raise RuntimeError(f"Database save failed: {exc}") from exc
    finally:
        session.close()


def get_model_extration_by_user(application_user_id: str) -> Optional[dict]:
    """
    Retrieve ModelExtration for a specific user.
    
    Args:
        application_user_id: The user ID from AspNetUsers
        
    Returns:
        Dictionary with ModelExtration data or None
    """
    session = get_db_session()
    
    try:
        # Get main ModelExtration data
        query = text("""
            SELECT 
                Id, ApplicationUserId, FullName, Email, Phone, 
                Location, Summary, Skills, Certifications, Languages
            FROM ModelExtrations
            WHERE ApplicationUserId = :user_id
        """)
        
        result = session.execute(query, {"user_id": application_user_id}).fetchone()
        
        if not result:
            return None
        
        model_id = result[0]
        
        # Get Education records
        edu_query = text("""
            SELECT Degree, Field, Institution, Year
            FROM Education
            WHERE ModelExtrationId = :model_id
        """)
        education = [
            {
                "degree": row[0],
                "field": row[1],
                "institution": row[2],
                "year": row[3]
            }
            for row in session.execute(edu_query, {"model_id": model_id})
        ]
        
        # Get Experience records
        exp_query = text("""
            SELECT JobTitle, Company, StartDate, EndDate, Description
            FROM Experience
            WHERE ModelExtrationId = :model_id
        """)
        experience = [
            {
                "job_title": row[0],
                "company": row[1],
                "start_date": row[2],
                "end_date": row[3],
                "description": row[4]
            }
            for row in session.execute(exp_query, {"model_id": model_id})
        ]
        
        return {
            "id": result[0],
            "application_user_id": result[1],
            "full_name": result[2],
            "email": result[3],
            "phone": result[4],
            "location": result[5],
            "summary": result[6],
            "skills": json.loads(result[7]) if result[7] else [],
            "certifications": json.loads(result[8]) if result[8] else [],
            "languages": json.loads(result[9]) if result[9] else [],
            "education": education,
            "experience": experience,
        }
        
    except Exception as exc:
        logger.exception("Failed to retrieve ModelExtration")
        return None
    finally:
        session.close()


def delete_model_extration(application_user_id: str) -> bool:
    """
    Delete ModelExtration for a user.
    Education and Experience will be deleted automatically (CASCADE).
    
    Args:
        application_user_id: The user ID from AspNetUsers
        
    Returns:
        True if deleted, False if not found
    """
    session = get_db_session()
    
    try:
        query = text("""
            DELETE FROM ModelExtrations
            WHERE ApplicationUserId = :user_id
        """)
        
        result = session.execute(query, {"user_id": application_user_id})
        session.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"ModelExtration deleted for user {application_user_id}")
        
        return deleted
        
    except Exception as exc:
        session.rollback()
        logger.exception("Failed to delete ModelExtration")
        return False
    finally:
        session.close()
