# backend/routers/upload.py

from fastapi import APIRouter, File, UploadFile, HTTPException
from services.data_engine import process_csv_file
from services.ai_engine import generate_report_summary
from models.response import ReportResponse
from utils.file_handler import save_uploaded_file

router = APIRouter(tags=["report generation"]) 



@router.post("/generate-report", response_model=ReportResponse)
async def generate_report(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        file_path = save_uploaded_file(file)

        # Step 1: Call Data Engine to extract metrics
        metrics = process_csv_file(file_path)

        # Step 2: Call AI Engine to generate summary & recommendations
        ai_result = generate_report_summary(metrics)

        # Combine results into final response structure
        return ReportResponse(
            metrics=metrics,
            summary=ai_result["summary"],
            recommendations=ai_result["recommendations"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# backend/routers/upload.py (add this function)

def generate_full_report(file_path: str) -> ReportResponse:
    """Internal function to generate full report (for future PDF export)."""
    metrics = process_csv_file(file_path)
    ai_result = generate_report_summary(metrics)
    return ReportResponse(
        metrics=metrics,
        summary=ai_result["summary"],
        recommendations=ai_result["recommendations"]
    )

