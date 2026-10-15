import os
import json
import shutil
from pathlib import Path
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import AIDigitizeJob, Question, QuestionOption, SubStatement, LearningOutcome
from backend.services.ai_parser import process_digitize_job, parse_document_file
from backend.services.tagging_service import suggest_auto_tagging

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
    file: UploadFile = File(...),
    subject_id: Optional[str] = Form(None),
    grade_id: Optional[str] = Form(None),
    sync: bool = Form(False),  # Option to run synchronously if testing
    db: Session = Depends(get_db)
):
    """Upload DOCX/PDF/Image, create AIDigitizeJob, trigger AI parsing worker.
    POST /api/v1/digitize/upload
    """
    ext = Path(file.filename or "").suffix.lower().replace(".", "")
    if ext not in ["docx", "doc", "pdf", "png", "jpg", "jpeg", "txt"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Supported: .docx, .doc, .pdf, .png, .jpg, .jpeg, .txt"
        )

    # Create job in database
    job = AIDigitizeJob(
        filename=file.filename or "unknown",
        file_path="",
        file_type=ext,
        subject_id=subject_id,
        grade_id=grade_id,
        status="PENDING",
        confidence_score=0.0
    )
    db.add(job)
    db.flush()

    # Save uploaded file to storage/uploads/{job_id}_{filename}
    target_filename = f"{job.id}_{Path(file.filename or 'upload').name}"
    target_path = STORAGE_UPLOADS_DIR / target_filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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
        "message": "File uploaded successfully. AI digitization worker initiated."
    }


@router.get("/jobs/{job_id}", response_model=DigitizeJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Poll job status, confidence score, extracted JSON.
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

    return DigitizeJobResponse(
        id=job.id,
        filename=job.filename,
        file_type=job.file_type,
        subject_id=job.subject_id,
        grade_id=job.grade_id,
        status=job.status,
        confidence_score=job.confidence_score,
        extracted_questions=extracted_list,
        error_message=job.error_message
    )


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
