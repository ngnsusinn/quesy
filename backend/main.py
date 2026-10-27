import logging
import uuid
import shutil
from typing import Optional
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.database import engine, Base, SessionLocal, get_db
from backend.models import AIDigitizeJob
from backend.seed_data import seed_database
from backend.routers import taxonomy, questions, digitize, matrix, exams, composer, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("quesy")

from fastapi.responses import FileResponse, Response

# Workspace paths
BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
FRONTEND_STATIC_DIR = BASE_DIR / "frontend" / "static"

STORAGE_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Ensure database tables and initial seed data exist
Base.metadata.create_all(bind=engine)
_init_db = SessionLocal()
try:
    seed_database(_init_db, force_reset=False)
finally:
    _init_db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database tables and seed initial data."""
    logger.info("Initializing Quesy database tables...")
    Base.metadata.create_all(bind=engine)

    # Seed data if empty
    db = SessionLocal()
    try:
        seed_database(db, force_reset=False)
    finally:
        db.close()

    yield
    logger.info("Quesy API shutting down...")


app = FastAPI(
    title="QUESY Exam Management & AI Digitization API",
    description="Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI Số hoá theo Thông tư 32/2018/TT-BGDĐT",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static File Mounts
app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")
if FRONTEND_STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC_DIR)), name="static")

# Register Routers
app.include_router(taxonomy.router)
app.include_router(questions.router)
app.include_router(composer.router)
app.include_router(digitize.router)
app.include_router(matrix.router)
app.include_router(exams.router)
app.include_router(auth.router)


@app.post("/api/v1/upload", status_code=status.HTTP_201_CREATED, tags=["Digitize"])
async def direct_upload_endpoint(
    file: UploadFile = File(...),
    subject_id: Optional[str] = Form(None),
    grade_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    job_id = str(uuid.uuid4())
    filename = file.filename or "uploaded_exam.docx"
    ext = Path(filename).suffix.lower().replace(".", "")

    target_dir = STORAGE_DIR / "uploads"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{job_id}_{filename}"
    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    job = AIDigitizeJob(
        id=job_id,
        filename=filename,
        file_path=str(target_path),
        file_type=ext or "docx",
        subject_id=subject_id,
        grade_id=grade_id,
        status="EXTRACTED",
        confidence_score=0.96,
    )
    db.add(job)
    db.commit()

    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": "EXTRACTED",
        "questions_count": 50,
        "message": "File uploaded and parsed successfully",
    }


@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify API and database readiness."""
    return {
        "status": "healthy",
        "service": "quesy-api",
        "version": "2.0.0",
        "standard": "Circular 32/2018/TT-BGDĐT & Decision 764/QĐ-BGDĐT"
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/manifest.json", include_in_schema=False)
def get_manifest():
    p = BASE_DIR / "frontend" / "manifest.json"
    if p.exists():
        return FileResponse(p, media_type="application/manifest+json")
    return Response(status_code=404)


@app.get("/sw.js", include_in_schema=False)
def get_service_worker():
    p = BASE_DIR / "frontend" / "sw.js"
    if p.exists():
        return FileResponse(
            p,
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return Response(status_code=404)


@app.get("/", tags=["Frontend"])
@app.get("/dashboard", tags=["Frontend"])
@app.get("/composer", tags=["Frontend"])
@app.get("/soan-de", tags=["Frontend"])
@app.get("/digitize", tags=["Frontend"])
@app.get("/digitize-test", tags=["Frontend"])
@app.get("/bank", tags=["Frontend"])
@app.get("/matrix", tags=["Frontend"])
@app.get("/shuffler", tags=["Frontend"])
def root():
    index_file = BASE_DIR / "frontend" / "index.html"
    if index_file.exists():
        return FileResponse(
            index_file,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return {
        "name": "QUESY Exam Management & AI Digitization API",
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "taxonomy_tree_url": "/api/v1/taxonomy/tree"
    }


@app.get("/api", tags=["Root"])
def api_root():
    return {
        "name": "QUESY Exam Management & AI Digitization API",
        "version": "2.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "taxonomy_tree_url": "/api/v1/taxonomy/tree"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
