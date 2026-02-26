from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.upload import router as upload_router
import os

app = FastAPI(title="AI Marketing Report Generator API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(upload_router, prefix="/api")

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
