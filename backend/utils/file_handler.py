# backend/utils/file_handler.py

from fastapi import UploadFile
import os
import tempfile


def save_uploaded_file(file: UploadFile) -> str:
    _, temp_path = tempfile.mkstemp(suffix=".csv")
    with open(temp_path, "wb") as buffer:
        buffer.write(file.file.read())
    return temp_path
