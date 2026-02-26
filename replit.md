# FlowGenix - AI Marketing Report Generator

## Overview
A web application that accepts a CSV file of marketing ad data and generates an AI-powered report with metrics, summary, and recommendations.

## Architecture
- **Backend**: FastAPI (Python 3.12) running on port 5000
  - Located in `backend/`
  - Serves both the REST API and static frontend files
  - API routes mounted under `/api` prefix
- **Frontend**: Static HTML/CSS/JS
  - Located in `static/`
  - Served by FastAPI's StaticFiles mount at root `/`

## Project Structure
```
backend/
  main.py              # FastAPI app entry point, mounts static files
  routers/upload.py    # POST /api/generate-report endpoint
  services/
    ai_engine.py       # AI summary generation (placeholder)
    data_engine.py     # CSV data processing (placeholder)
  models/response.py   # Pydantic response model
  utils/file_handler.py # File upload utilities
static/
  index.html           # Main upload UI
  aboutus.html         # About page
```

## Workflow
- **Start application**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 5000`
- Output type: webview on port 5000

## Key Endpoints
- `GET /` — Frontend (index.html)
- `GET /health` — Health check
- `POST /api/generate-report` — Upload CSV, returns JSON report with metrics, summary, recommendations

## Dependencies
- fastapi, uvicorn, python-multipart, python-dotenv, openai, pydantic
