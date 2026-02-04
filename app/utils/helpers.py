"""Helper utilities."""
import json
import re
from pathlib import PurePath
from fastapi import UploadFile
from app.core.config import settings

def get_file_extension(filename: str) -> str:
    return PurePath(filename).suffix.lower()

def validate_uploaded_file(file: UploadFile) -> None:
    filename = file.filename or ""
    ext = get_file_extension(filename)
    if ext not in settings.allowed_extensions:
        raise ValueError(f"Unsupported: {ext}")
    content_length = file.headers.get("content-length")
    if content_length and int(content_length) > settings.max_file_size_bytes:
        raise ValueError("File too large")

def extract_json_from_llm_response(text: str) -> dict:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON found")
    return json.loads(text[start : end + 1])
