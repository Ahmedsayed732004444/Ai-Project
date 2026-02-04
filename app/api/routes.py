"""
API routes for CV parsing and ModelExtration management.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse

from app.schemas.cv_schema import ModelExtrationResponse, ErrorResponse
from app.services.cv_analyzer import analyse_cv
from app.services.file_parser import extract_text
from app.services.database import (
    save_model_extration,
    get_model_extration_by_user,
    delete_model_extration
)
from app.utils.helpers import validate_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# POST /parse-cv - Parse CV and optionally save to database
# ─────────────────────────────────────────────────────────────

@router.post(
    "/parse-cv",
    response_model=ModelExtrationResponse,
    status_code=200,
    summary="Parse a CV/Resume with AI",
    description=(
        "Upload a PDF or DOCX file. The service extracts text, "
        "analyzes it with AI, and returns structured data matching "
        "Career_Path.Entities.ModelExtration."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def parse_cv(
    file: UploadFile = File(..., description="CV file (PDF or DOCX)"),
    user_id: Optional[str] = Query(
        None, 
        description="ApplicationUserId - if provided, saves to ModelExtrations table"
    ),
) -> JSONResponse:
    """
    Main endpoint - parse CV with AI.
    If user_id is provided, saves result to database.
    """

    # ── 1. Validate file ─────────────────────────────────────
    try:
        validate_uploaded_file(file)
    except ValueError as exc:
        logger.warning("Upload validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))

    # ── 2. Read file bytes ───────────────────────────────────
    try:
        file_bytes: bytes = await file.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded file.")
        raise HTTPException(
            status_code=500, 
            detail="Could not read file."
        ) from exc

    if not file_bytes:
        raise HTTPException(status_code=400, detail="File is empty.")

    filename: str = file.filename or "unknown"
    logger.info("Processing file: %s (%d bytes)", filename, len(file_bytes))

    # ── 3. Extract text ──────────────────────────────────────
    try:
        cv_text: str = await extract_text(file_bytes, filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Text extraction failed for: %s", filename)
        raise HTTPException(
            status_code=500,
            detail="Text extraction failed. File may be corrupted.",
        ) from exc

    if not cv_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text extracted. File may be image-only or empty.",
        )

    # ── 4. AI analysis ───────────────────────────────────────
    try:
        cv_response: ModelExtrationResponse = await analyse_cv(cv_text)
    except (RuntimeError, ValueError) as exc:
        logger.exception("CV analysis failed.")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # ── 5. Save to database if user_id provided ──────────────
    if user_id:
        try:
            model_id = save_model_extration(cv_response, user_id)
            logger.info(
                "ModelExtration saved for user %s with ID: %d", 
                user_id, 
                model_id
            )
        except Exception as exc:
            logger.exception("Failed to save ModelExtration")
            # Don't fail the request - still return parsed data
            logger.warning(
                "Continuing without database save due to error: %s", 
                exc
            )

    # ── 6. Return parsed data ────────────────────────────────
    return JSONResponse(content=cv_response.model_dump(by_alias=True))


# ─────────────────────────────────────────────────────────────
# GET /model-extration/{user_id} - Get ModelExtration by user
# ─────────────────────────────────────────────────────────────

@router.get(
    "/model-extration/{user_id}",
    response_model=ModelExtrationResponse,
    summary="Get ModelExtration for a user",
    description="Retrieve the stored CV data (ModelExtration) for a specific user.",
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_model_extration(user_id: str) -> JSONResponse:
    """Get ModelExtration by ApplicationUserId."""
    
    try:
        data = get_model_extration_by_user(user_id)
    except Exception as exc:
        logger.exception("Failed to retrieve ModelExtration")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve data from database.",
        ) from exc

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No ModelExtration found for user: {user_id}",
        )

    return JSONResponse(content=data)


# ─────────────────────────────────────────────────────────────
# DELETE /model-extration/{user_id} - Delete ModelExtration
# ─────────────────────────────────────────────────────────────

@router.delete(
    "/model-extration/{user_id}",
    status_code=200,
    summary="Delete ModelExtration for a user",
    description="Remove all CV data for a specific user from the database.",
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def delete_model_extration_endpoint(user_id: str) -> JSONResponse:
    """Delete ModelExtration by ApplicationUserId."""
    
    try:
        deleted = delete_model_extration(user_id)
    except Exception as exc:
        logger.exception("Failed to delete ModelExtration")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete from database.",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"No ModelExtration found for user: {user_id}",
        )

    return JSONResponse(content={
        "message": f"ModelExtration deleted successfully for user {user_id}"
    })
