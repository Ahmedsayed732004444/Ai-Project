"""
API routes for CV Parser.
Includes CV parsing, database operations, and roadmap generation.
"""

import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse

from app.schemas.cv_schema import ModelExtrationResponse, ErrorResponse
from app.schemas.matching_schema import MatchJobsRequest, MatchJobsResponse
from app.schemas.roadmap_schema import RoadmapResponse
from app.services.file_parser import extract_text
from app.services.cv_analyzer import analyse_cv
from app.services.database import (
    save_model_extration,
    get_model_extration_by_user,
    delete_model_extration,
)
from app.services.job_matcher import compute_matches
from app.services.roadmap_service import generate_roadmap
from app.utils.helpers import validate_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# CV Parsing Endpoints
# ─────────────────────────────────────────────────────────────

@router.post(
    "/parse-cv",
    response_model=ModelExtrationResponse,
    summary="Parse CV and optionally save to database",
    responses={
        200: {"description": "CV parsed successfully"},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def parse_cv(
    file: UploadFile = File(..., description="CV file (PDF or DOCX)"),
    user_id: Optional[str] = Query(
        None,
        description="ApplicationUserId to save the CV data. If provided, data will be saved to ModelExtrations table.",
    ),
):
    """
    Parse a CV file and extract structured data using AI.
    
    **Flow:**
    1. Upload CV (PDF/DOCX)
    2. Extract text from file
    3. Analyze with AI (Groq)
    4. Return structured data
    5. If user_id provided: Save to database
    
    **Note:** user_id must exist in AspNetUsers table.
    """
    try:
        # Validate file
        validate_uploaded_file(file)
        
        # Read file
        file_bytes = await file.read()
        logger.info(f"Processing file: {file.filename} ({len(file_bytes)} bytes)")
        
        # Extract text
        cv_text = await extract_text(file_bytes, file.filename)
        if not cv_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the file. "
                       "Ensure it's not an image-based PDF or corrupted.",
            )
        
        logger.info(f"Extracted {len(cv_text)} characters from {file.filename}")
        
        # Analyze CV
        cv_data = await analyse_cv(cv_text)
        
        # Save to database if user_id provided
        if user_id:
            try:
                model_id = save_model_extration(cv_data, user_id)
                logger.info(f"CV data saved to database with ID: {model_id}")
            except Exception as db_error:
                logger.error(f"Database save failed: {db_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"CV parsed successfully but database save failed: {str(db_error)}",
                )
        
        return cv_data
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        logger.exception("Unexpected error during CV parsing")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(exc)}")


# ─────────────────────────────────────────────────────────────
# Database CRUD Endpoints
# ─────────────────────────────────────────────────────────────

@router.get(
    "/model-extration/{user_id}",
    summary="Get ModelExtration by user ID",
    responses={
        200: {"description": "ModelExtration data retrieved"},
        404: {"model": ErrorResponse},
    },
)
async def get_model_extration(user_id: str):
    """
    Retrieve ModelExtration data for a specific user.
    
    Returns complete data including:
    - Personal info
    - Skills
    - Education (from Education table)
    - Experience (from Experience table)
    - Certifications
    - Languages
    """
    try:
        data = get_model_extration_by_user(user_id)
        
        if data is None:
            raise HTTPException(
                status_code=404,
                detail=f"No ModelExtration found for user: {user_id}",
            )
        
        return JSONResponse(content=data)
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error retrieving ModelExtration for {user_id}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete(
    "/model-extration/{user_id}",
    summary="Delete ModelExtration by user ID",
    responses={
        200: {"description": "Deleted successfully"},
        404: {"model": ErrorResponse},
    },
)
async def delete_model_extration_endpoint(user_id: str):
    """
    Delete ModelExtration for a user.
    
    This will also delete:
    - All Education records (CASCADE)
    - All Experience records (CASCADE)
    """
    try:
        deleted = delete_model_extration(user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"No ModelExtration found for user: {user_id}",
            )
        
        return {"message": f"ModelExtration deleted for user {user_id}"}
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error deleting ModelExtration for {user_id}")
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# Job Matching Endpoint
# ─────────────────────────────────────────────────────────────

@router.post(
    "/match-jobs",
    response_model=MatchJobsResponse,
    summary="Match user skills with jobs",
    responses={
        200: {"description": "Jobs matched and sorted by percentage"},
        400: {"model": ErrorResponse},
    },
)
async def match_jobs(request: MatchJobsRequest):
    """
    Match user skills against multiple job postings.
    
    **Returns:**
    - Jobs sorted by match percentage (highest first)
    - Matched skills for each job
    - Missing skills for each job
    - Match percentage (0-100%)
    """
    try:
        response = compute_matches(request.userSkills, request.jobSkills)
        return response
    except Exception as exc:
        logger.exception("Error in job matching")
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────
# 🆕 Roadmap Generation Endpoint
# ─────────────────────────────────────────────────────────────

@router.post(
    "/generate-roadmap/{user_id}",
    response_model=RoadmapResponse,
    summary="Generate personalized learning roadmap",
    responses={
        200: {"description": "Roadmap generated successfully"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def generate_roadmap_endpoint(user_id: str):
    """
    Generate a personalized 3-6 month learning roadmap for a user.
    
    **Process:**
    1. Fetch user's ModelExtration data from database
    2. Analyze current skill level (Junior/Mid-level)
    3. Generate customized roadmap using AI
    4. Return structured roadmap with:
       - Monthly/weekly phases
       - Skills to develop
       - New skills to learn
       - Practical project ideas
       - Mermaid diagram for visualization
    
    **Requirements:**
    - User must have ModelExtration data in database
    - Uses free AI models (Groq/llama-3.3-70b)
    
    **Response includes:**
    - `userId`: User identifier
    - `roadmap_duration`: "3-6 months"
    - `roadmap`: Array of phases with focus areas, topics, and projects
    - `mermaid_code`: Mermaid diagram code for visualization
    """
    try:
        # Get user data from database
        logger.info(f"Fetching data for user: {user_id}")
        user_data = get_model_extration_by_user(user_id)
        
        if user_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for user: {user_id}. "
                       "Please upload a CV first using /parse-cv endpoint.",
            )
        
        # Format data for roadmap generation
        formatted_data = {
            "personal_info": {
                "full_name": user_data.get("full_name", ""),
                "email": user_data.get("email", ""),
                "phone": user_data.get("phone", ""),
                "location": user_data.get("location", ""),
            },
            "summary": user_data.get("summary", ""),
            "skills": user_data.get("skills", []),
            "education": user_data.get("education", []),
            "experience": user_data.get("experience", []),
            "certifications": user_data.get("certifications", []),
            "languages": user_data.get("languages", []),
        }
        
        logger.info(f"Generating roadmap for user with {len(formatted_data['skills'])} skills")
        
        # Generate roadmap
        roadmap = await generate_roadmap(formatted_data, user_id)
        
        logger.info(f"Roadmap generated: {roadmap.roadmap_duration}, {len(roadmap.roadmap)} phases")
        
        return roadmap
        
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error generating roadmap for {user_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate roadmap: {str(exc)}",
        )
