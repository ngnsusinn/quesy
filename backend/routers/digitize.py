import os
import re
import json
import shutil
from pathlib import Path
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AIDigitizeJob, Question, QuestionOption, SubStatement, LearningOutcome
from backend.services.ai_parser import process_digitize_job, parse_document_file
from backend.services.tagging_service import suggest_auto_tagging
from backend.services.latex_converter import extract_and_convert_docx_content
from backend.services.ai_provider_service import default_ai_provider_service

router = APIRouter(prefix="/api/v1/digitize", tags=["Digitize"])

STORAGE_UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "uploads"
STORAGE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class DigitizeJobResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    status: str
    confidence_score: float
    extracted_questions: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    preview_url: Optional[str] = None
    preview_images: List[str] = []
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommitOptionPayload(BaseModel):
    label: str
    content: str
    is_correct: bool = False
    is_fixed: bool = False
    order_index: int = 0


class CommitSubStatementPayload(BaseModel):
    label: str
    content: str
    is_true: bool = False
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order_index: int = 0


class CommitQuestionItem(BaseModel):
    stem: str
    item_format: str = "SINGLE_CHOICE"
    cognitive_level: str = "RECOGNITION"
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    options: Optional[List[CommitOptionPayload]] = []
    sub_statements: Optional[List[CommitSubStatementPayload]] = []


class CommitJobRequest(BaseModel):
    questions: Optional[List[CommitQuestionItem]] = None
    default_learning_outcome_id: Optional[str] = None
    status: str = "APPROVED"


class CommitJobResponse(BaseModel):
    job_id: str
    committed_count: int
    question_ids: List[str]
    message: str


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    files: Optional[List[UploadFile]] = File(None),
    subject_id: Optional[str] = Form(None),
    grade_id: Optional[str] = Form(None),
    sync: bool = Form(False),  # Option to run synchronously if testing
    db: Session = Depends(get_db)
):
    """Upload DOCX/PDF/Image or multiple image pages, create AIDigitizeJob, trigger AI parsing worker.
    POST /api/v1/digitize/upload
    """
    uploaded_files: List[UploadFile] = []
    if files:
        uploaded_files.extend([f for f in files if f and f.filename])
    elif file and file.filename:
        uploaded_files.append(file)

    if not uploaded_files:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng chọn ít nhất một tệp (.docx, .pdf, .png, .jpg, .jpeg, .webp) để tải lên."
        )

    # Validate extensions
    allowed = ["docx", "doc", "pdf", "png", "jpg", "jpeg", "webp", "txt"]
    for f in uploaded_files:
        f_ext = Path(f.filename or "").suffix.lower().replace(".", "")
        if f_ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Định dạng tệp không được hỗ trợ: '{f.filename}'. Hỗ trợ: .docx, .doc, .pdf, .png, .jpg, .jpeg, .webp"
            )

    primary_file = uploaded_files[0]
    primary_ext = Path(primary_file.filename or "").suffix.lower().replace(".", "")

    is_multi_image = len(uploaded_files) > 1 and all(
        Path(f.filename or "").suffix.lower().replace(".", "") in ["png", "jpg", "jpeg", "webp"]
        for f in uploaded_files
    )

    display_name = f"{len(uploaded_files)} trang ảnh đề thi" if is_multi_image else (primary_file.filename or "unknown")
    job_type = "images" if is_multi_image else primary_ext

    # Create job in database
    job = AIDigitizeJob(
        filename=display_name,
        file_path="",
        file_type=job_type,
        subject_id=subject_id,
        grade_id=grade_id,
        status="PENDING",
        confidence_score=0.0
    )
    db.add(job)
    db.flush()

    if is_multi_image:
        job_dir = STORAGE_UPLOADS_DIR / job.id
        job_dir.mkdir(parents=True, exist_ok=True)
        saved_paths = []
        for idx, f in enumerate(uploaded_files):
            safe_name = f"{idx + 1:02d}_{Path(f.filename or 'page').name}"
            target_p = job_dir / safe_name
            with open(target_p, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            saved_paths.append(str(target_p))
        job.file_path = saved_paths[0] if saved_paths else ""
    else:
        target_filename = f"{job.id}_{Path(primary_file.filename or 'upload').name}"
        target_path = STORAGE_UPLOADS_DIR / target_filename
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(primary_file.file, buffer)
        job.file_path = str(target_path)

    db.commit()

    if sync:
        process_digitize_job(job.id)
    else:
        background_tasks.add_task(process_digitize_job, job.id)

    return {
        "job_id": job.id,
        "filename": job.filename,
        "status": "PROCESSING" if sync else "PENDING",
        "file_type": job.file_type,
        "preview_url": f"/api/v1/digitize/jobs/{job.id}/preview",
        "message": "File uploaded successfully. AI digitization worker initiated."
    }


@router.get("/jobs/{job_id}", response_model=DigitizeJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Poll job status, confidence score, extracted JSON and preview URL.
    GET /api/v1/digitize/jobs/:job_id
    """
    job = db.query(AIDigitizeJob).filter(AIDigitizeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AIDigitizeJob not found")

    extracted_list = []
    if job.extracted_data:
        try:
            extracted_list = json.loads(job.extracted_data)
        except Exception:
            extracted_list = []

    preview_images: List[str] = []
    job_p = Path(job.file_path)
    parent_d = job_p.parent
    if parent_d.name == job.id and parent_d.exists():
        for f in sorted(parent_d.glob("*.*")):
            if f.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                preview_images.append(f"/api/v1/digitize/jobs/{job.id}/files/{f.name}")

    return DigitizeJobResponse(
        id=job.id,
        filename=job.filename,
        file_type=job.file_type,
        subject_id=job.subject_id,
        grade_id=job.grade_id,
        status=job.status,
        confidence_score=job.confidence_score,
        extracted_questions=extracted_list,
        error_message=job.error_message,
        preview_url=f"/api/v1/digitize/jobs/{job.id}/preview",
        preview_images=preview_images,
        ai_provider=default_ai_provider_service.provider if default_ai_provider_service.is_configured() else "local_fallback",
        ai_model=default_ai_provider_service.model if default_ai_provider_service.is_configured() else "offline_rule_engine"
    )


@router.get("/jobs/{job_id}/preview")
def preview_job_document(job_id: str, db: Session = Depends(get_db)):
    """Serves the actual uploaded document directly for web browser preview.
    - PDF: native browser PDF streaming viewer with zoom and page controls.
    - Image: direct image stream.
    - DOCX: clean styled HTML preview with KaTeX mathematical formulas.
    GET /api/v1/digitize/jobs/:job_id/preview
    """
    job = db.query(AIDigitizeJob).filter(AIDigitizeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AIDigitizeJob not found")

    file_p = Path(job.file_path)
    if not file_p.exists():
        raise HTTPException(status_code=404, detail="Uploaded file not found on disk")

    ext = job.file_type.lower().replace(".", "")

    if ext == "pdf":
        return FileResponse(
            path=str(file_p),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=\"{Path(job.filename or 'document.pdf').name}\""}
        )

    if ext in ["png", "jpg", "jpeg", "webp"]:
        media_type = "image/jpeg" if ext == "jpg" else f"image/{ext}"
        return FileResponse(
            path=str(file_p),
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename=\"{Path(job.filename or 'image').name}\""}
        )

    if ext in ["docx", "doc"]:
        try:
            raw_content = extract_and_convert_docx_content(str(file_p))
        except Exception:
            raw_content = "Không thể đọc nội dung file Word DOCX."

        body_html = []
        for line in raw_content.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("PHẦN ") or line_str.startswith("BÀI THI:") or line_str.startswith("KỲ THI"):
                body_html.append(f"<h3 style='margin: 18px 0 8px 0; color: #1e3a8a; font-size: 15px; font-weight: bold;'>{line_str}</h3>")
            elif re.match(r"^Câu\s+\d+[\.\:]", line_str):
                body_html.append(f"<div style='margin-top: 14px; font-weight: bold; color: #0f172a;'>{line_str}</div>")
            elif re.match(r"^[A-D]\.", line_str):
                body_html.append(f"<div style='margin-left: 18px; margin-top: 4px; color: #334155;'>{line_str}</div>")
            else:
                body_html.append(f"<p style='margin: 6px 0; color: #1e293b;'>{line_str}</p>")

        html_page = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>{job.filename or 'Xem trước đề thi Word'}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$', right: '$', display: false}}, {{left: '$$', right: '$$', display: true}}]}});"></script>
  <style>
    body {{
      font-family: 'Times New Roman', Times, serif;
      font-size: 14px;
      line-height: 1.6;
      background: #ffffff;
      color: #0f172a;
      padding: 30px 40px;
      max-width: 820px;
      margin: 0 auto;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
  </style>
</head>
<body>
  {"".join(body_html)}
</body>
</html>"""
        return HTMLResponse(content=html_page, media_type="text/html")

    return FileResponse(path=str(file_p), media_type="text/plain; charset=utf-8")


@router.get("/jobs/{job_id}/files/{filename}")
def serve_job_file(job_id: str, filename: str):
    """Serves a specific page image or embedded asset for a digitize job."""
    job_dir = STORAGE_UPLOADS_DIR / job_id
    target_p = job_dir / filename
    if not target_p.exists():
        target_p = STORAGE_UPLOADS_DIR / f"{job_id}_{filename}"
    if not target_p.exists():
        raise HTTPException(status_code=404, detail="File not found")

    ext = target_p.suffix.lower().replace(".", "")
    media_type = "image/jpeg" if ext == "jpg" else f"image/{ext}"
    return FileResponse(path=str(target_p), media_type=media_type)


@router.post("/jobs/{job_id}/commit", response_model=CommitJobResponse)
def commit_reviewed_questions(
    job_id: str,
    payload: Optional[CommitJobRequest] = None,
    db: Session = Depends(get_db)
):
    """Commit reviewed questions from HITL studio into item bank with assigned YCCDs.
    POST /api/v1/digitize/jobs/:job_id/commit
    """
    job = db.query(AIDigitizeJob).filter(AIDigitizeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="AIDigitizeJob not found")

    items_to_commit: List[Dict[str, Any]] = []

    if payload and payload.questions:
        items_to_commit = [q.dict() for q in payload.questions]
    elif job.extracted_data:
        try:
            items_to_commit = json.loads(job.extracted_data)
        except Exception:
            items_to_commit = []

    if not items_to_commit:
        raise HTTPException(
            status_code=400,
            detail="No questions available to commit. Please ensure extraction succeeded or provide questions in payload."
        )

    # Find a default YCCĐ if not specified
    fallback_yccd = db.query(LearningOutcome).first()
    default_yccd_id = payload.default_learning_outcome_id if payload else None
    if not default_yccd_id and fallback_yccd:
        default_yccd_id = fallback_yccd.id

    committed_ids = []
    q_status = payload.status if payload and payload.status else "APPROVED"

    for item in items_to_commit:
        yccd_id = item.get("learning_outcome_id") or default_yccd_id
        archetype_id = item.get("problem_archetype_id")
        cog_level = item.get("cognitive_level", "RECOGNITION")
        fmt = item.get("item_format", "SINGLE_CHOICE")
        stem = item.get("stem", "")
        exp = item.get("explanation", "")
        source_ref = item.get("source_reference", f"AI Digitized from {job.filename}")

        q = Question(
            subject_id=job.subject_id,
            grade_id=job.grade_id,
            learning_outcome_id=yccd_id,
            problem_archetype_id=archetype_id,
            cognitive_level=cog_level,
            item_format=fmt,
            stem=stem,
            explanation=exp,
            source_reference=source_ref,
            status=q_status
        )
        db.add(q)
        db.flush()
        committed_ids.append(q.id)

        # Options
        raw_options = item.get("options", [])
        for idx, opt in enumerate(raw_options):
            db.add(QuestionOption(
                question_id=q.id,
                label=opt.get("label", "A"),
                content=opt.get("content", ""),
                is_correct=opt.get("is_correct", False),
                is_fixed=opt.get("is_fixed", False),
                order_index=opt.get("order_index", idx + 1)
            ))

        # Sub-statements
        raw_sub = item.get("sub_statements", [])
        for idx, sub in enumerate(raw_sub):
            db.add(SubStatement(
                question_id=q.id,
                label=sub.get("label", "a"),
                content=sub.get("content", ""),
                is_true=sub.get("is_true", False),
                correct_answer=sub.get("correct_answer"),
                explanation=sub.get("explanation"),
                order_index=sub.get("order_index", idx + 1)
            ))

    job.status = "COMPLETED"
    db.commit()

    return CommitJobResponse(
        job_id=job.id,
        committed_count=len(committed_ids),
        question_ids=committed_ids,
        message=f"Successfully committed {len(committed_ids)} reviewed questions into the item bank."
    )
