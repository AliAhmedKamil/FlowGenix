from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.upload import router as upload_router  # احتفظ به إذا عندك
import os
import uuid
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ----- FastAPI app -----
app = FastAPI(title="AI Marketing Report Generator API", version="1.0.0")

# ----- Health check -----
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ----- Include other routers -----
app.include_router(upload_router, prefix="/api")

# ----- Serve static files (JS, CSS, HTML) -----
# افترضنا عندك مجلد project/static يحتوي على index.html, style.css, script.js
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

# ----- PDF generation endpoint -----
@app.post("/generate-report")
async def generate_report(file: UploadFile = File(...)):
    content = await file.read()
    report_text = "Generated marketing report"  # تقدر تعدل حسب مشروعك

    filename = f"{uuid.uuid4()}.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = [Paragraph(report_text, styles["Normal"])]
    doc.build(elements)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename="marketing-report.pdf"
    )

# ----- Main -----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)  # على Railway استبدل port بـ $PORT عند deploy
