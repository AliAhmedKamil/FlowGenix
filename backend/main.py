# backend/main.py

from fastapi import FastAPI
from routers.upload import router as upload_router  # Import the router

app = FastAPI(title="AI Marketing Report Generator API", version="1.0.0")

# --- Add your routes here ---
@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Include the router with prefix "/api" ---
app.include_router(upload_router, prefix="/api")

# --- Optional: Add a debug route to test ---
@app.get("/")
def root():
    return {"message": "Welcome to AI Report Generator API"}

# --- Run server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
