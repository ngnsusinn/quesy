import os
import uuid
from pathlib import Path
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import MasterExam, MasterExamItem, ExamVariant, ExamVariantItem
from backend.services.matrix_solver import solve_and_generate_master_exam
from backend.services.shuffling_engine import generate_shuffled_variants, get_answer_key_matrix
from backend.services.docx_exporter import (
    export_exam_package_zip, compute_item_analytics, export_single_variant_pdf
)

router = APIRouter(prefix="/api/v1/exams", tags=["Exams"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class GenerateExamRequest(BaseModel):
    matrix_id: str
    title: Optional[str] = None
    excluded_question_ids: Optional[List[str]] = None
    allow_partial: Optional[bool] = False


class ShuffleExamRequest(BaseModel):
    variant_codes: Optional[List[str]] = ["101", "102", "103", "104"]


class StudentAnswerSubmission(BaseModel):
    student_id: str
    total_score: float
    answers: Dict[str, bool]  # e.g. {"q_1": True, "q_2": False, ...}


class AnalyticsRequest(BaseModel):
    student_scores: List[StudentAnswerSubmission]


class MasterExamItemOut(BaseModel):
    id: str
    question_id: str
    section: int
    order_index: int
    points: float
    stem: Optional[str] = None
    item_format: Optional[str] = None
    cognitive_level: Optional[str] = None
    code: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    learning_outcome_code: Optional[str] = None
    options: List[Any] = []
    sub_statements: List[Any] = []
    has_anchor: bool = False
    short_answer_value: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SwapQuestionRequest(BaseModel):
    new_question_id: str


class MasterExamOut(BaseModel):
    id: str
    matrix_id: str
    title: str
    subject_id: str
    grade_id: str
    total_questions: int
    total_points: float
    status: str
    items: List[MasterExamItemOut] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("", response_model=List[MasterExamOut])
def list_master_exams(
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List master exams."""
    query = db.query(MasterExam)
    if subject_id:
        query = query.filter(MasterExam.subject_id == subject_id)
    if grade_id:
        query = query.filter(MasterExam.grade_id == grade_id)
    return query.order_by(MasterExam.created_at.desc()).all()


def _enrich_master_item(it: MasterExamItem) -> MasterExamItemOut:
    q = it.question
    opts = [
        {
            "label": o.label,
            "content": o.content,
            "is_correct": o.is_correct,
            "is_fixed": getattr(o, "is_fixed", False)
        }
        for o in (q.options if q else [])
    ]
    subs = [
        {
            "label": s.label,
            "content": s.content,
            "is_true": s.is_true
        }
        for s in (q.sub_statements if q else [])
    ]
    has_anchor = any(
        o.get("is_fixed") or any(kw in o.get("content", "").lower() for kw in ["cả a và b", "tất cả", "không có"])
        for o in opts
    )
    return MasterExamItemOut(
        id=it.id,
        question_id=it.question_id,
        section=it.section,
        order_index=it.order_index,
        points=it.points,
        stem=q.stem if q else None,
        item_format=q.item_format if q else None,
        cognitive_level=q.cognitive_level if q else None,
        code=getattr(q, "code", None) or (q.learning_outcome.code if q and q.learning_outcome else None),
        learning_outcome_id=q.learning_outcome_id if q else None,
        learning_outcome_code=q.learning_outcome.code if (q and q.learning_outcome) else None,
        options=opts,
        sub_statements=subs,
        has_anchor=has_anchor,
        short_answer_value=getattr(q, "short_answer_value", None)
    )


@router.post("/generate", response_model=MasterExamOut, status_code=status.HTTP_201_CREATED)
def generate_master_exam(payload: GenerateExamRequest, db: Session = Depends(get_db)):
    """POST /api/v1/exams/generate
    Solves matrix constraints and generates MasterExam with items.
    """
    try:
        master_exam = solve_and_generate_master_exam(
            matrix_id=payload.matrix_id,
            db=db,
            title=payload.title,
            excluded_question_ids=payload.excluded_question_ids,
            allow_partial=bool(payload.allow_partial)
        )

        items_out = [_enrich_master_item(it) for it in master_exam.items]

        return MasterExamOut(
            id=master_exam.id,
            matrix_id=master_exam.matrix_id,
            title=master_exam.title,
            subject_id=master_exam.subject_id,
            grade_id=master_exam.grade_id,
            total_questions=master_exam.total_questions,
            total_points=master_exam.total_points,
            status=master_exam.status,
            items=items_out
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{master_id}", response_model=MasterExamOut)
def get_master_exam(master_id: str, db: Session = Depends(get_db)):
    master = db.query(MasterExam).filter(MasterExam.id == master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="MasterExam not found")

    items_out = [_enrich_master_item(it) for it in master.items]

    return MasterExamOut(
        id=master.id,
        matrix_id=master.matrix_id,
        title=master.title,
        subject_id=master.subject_id,
        grade_id=master.grade_id,
        total_questions=master.total_questions,
        total_points=master.total_points,
        status=master.status,
        items=items_out
    )


@router.get("/{master_id}/items/{item_id}/replacement-candidates")
def get_replacement_candidates(
    master_id: str,
    item_id: str,
    db: Session = Depends(get_db)
):
    """Finds equivalent questions in Question Bank for in-place item swap."""
    master_item = db.query(MasterExamItem).filter(MasterExamItem.id == item_id).first()
    if not master_item:
        raise HTTPException(status_code=404, detail="MasterExamItem not found")

    q = master_item.question
    master = db.query(MasterExam).filter(MasterExam.id == master_id).first()
    excluded_q_ids = {it.question_id for it in master.items} if master else {master_item.question_id}

    from backend.models import Question
    candidates = []
    if q:
        candidates = db.query(Question).filter(
            Question.status == "APPROVED",
            Question.learning_outcome_id == q.learning_outcome_id,
            Question.cognitive_level == q.cognitive_level,
            Question.item_format == q.item_format,
            Question.is_defective.is_(False),
            ~Question.id.in_(list(excluded_q_ids))
        ).all()

    if not candidates and q:
        candidates = db.query(Question).filter(
            Question.status == "APPROVED",
            Question.item_format == q.item_format,
            ~Question.id.in_(list(excluded_q_ids))
        ).limit(10).all()

    return [
        {
            "id": c.id,
            "code": getattr(c, "code", None) or (c.learning_outcome.code if c and c.learning_outcome else None),
            "stem": c.stem,
            "cognitive_level": c.cognitive_level,
            "item_format": c.item_format,
            "options": [{"label": o.label, "content": o.content, "is_correct": o.is_correct} for o in c.options],
            "sub_statements": [{"label": s.label, "content": s.content, "is_true": s.is_true} for s in c.sub_statements],
        }
        for c in candidates
    ]


@router.post("/{master_id}/items/{item_id}/swap", response_model=MasterExamItemOut)
def swap_master_question(
    master_id: str,
    item_id: str,
    payload: SwapQuestionRequest,
    db: Session = Depends(get_db)
):
    """Swaps question in MasterExamItem and clears existing variants."""
    master_item = db.query(MasterExamItem).filter(MasterExamItem.id == item_id).first()
    if not master_item:
        raise HTTPException(status_code=404, detail="MasterExamItem not found")

    from backend.models import Question, ExamVariant
    new_q = db.query(Question).filter(Question.id == payload.new_question_id).first()
    if not new_q:
        raise HTTPException(status_code=404, detail="New question not found")

    master_item.question_id = new_q.id
    db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_id).delete()
    db.commit()
    db.refresh(master_item)

    return _enrich_master_item(master_item)


class DirectExamShuffleRequest(BaseModel):
    title: str = "Đề thi"
    questions: List[Dict[str, Any]]
    num_variants: int = 4
    variant_codes: Optional[List[str]] = None


@router.post("/shuffle")
def direct_shuffle_exam(payload: DirectExamShuffleRequest):
    """POST /api/v1/exams/shuffle
    Generates N safe variants directly from question list, enforcing RULE-02 and RULE-03.
    """
    from backend.schemas import Question, Option, SubStatement
    from backend.services.shuffling import generate_exam_variants

    parsed_questions: List[Question] = []
    for q_data in payload.questions:
        opts = [
            Option(
                label=o["label"],
                content=o["content"],
                is_correct=o.get("is_correct", False),
                is_fixed=o.get("is_fixed", False),
            )
            for o in q_data.get("options", [])
        ]
        subs = [
            SubStatement(
                label=s["label"],
                content=s["content"],
                is_true=s.get("is_true", False),
                explanation=s.get("explanation"),
            )
            for s in q_data.get("sub_statements", [])
        ]
        parsed_questions.append(
            Question(
                id=q_data.get("id", str(uuid.uuid4())),
                stem=q_data["stem"],
                subject_id=q_data.get("subject_id", "subj-default"),
                grade_id=q_data.get("grade_id", "grade-default"),
                learning_outcome_id=q_data.get("learning_outcome_id", "TOAN12.GT.01"),
                cognitive_level=q_data.get("cognitive_level", "RECOGNITION"),
                item_format=q_data.get("item_format", "SINGLE_CHOICE"),
                passage_id=q_data.get("passage_id"),
                options=opts if opts else [],
                sub_statements=subs if subs else [],
            )
        )

    variants = generate_exam_variants(
        exam_title=payload.title,
        questions=parsed_questions,
        num_variants=payload.num_variants,
        variant_codes=payload.variant_codes,
    )

    return {
        "exam_id": str(uuid.uuid4()),
        "title": payload.title,
        "variants": [v.model_dump() for v in variants],
    }


@router.post("/{master_id}/shuffle")
def shuffle_exam(
    master_id: str,
    payload: Optional[ShuffleExamRequest] = None,
    db: Session = Depends(get_db)
):
    """POST /api/v1/exams/:master_id/shuffle
    Generates N safe variants with Answer Key Matrix.
    """
    master = db.query(MasterExam).filter(MasterExam.id == master_id).first()
    if not master:
        master = db.query(MasterExam).first()
    if not master:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi trong hệ thống.")
    master_id = master.id

    variant_codes = payload.variant_codes if payload and payload.variant_codes else ["101", "102", "103", "104"]
    try:
        variants = generate_shuffled_variants(
            master_exam_id=master_id,
            db=db,
            variant_codes=variant_codes
        )
        key_matrix = get_answer_key_matrix(master_id, db)

        return {
            "master_exam_id": master_id,
            "generated_variants_count": len(variants),
            "variant_codes": [v.variant_code for v in variants],
            "answer_key_matrix": key_matrix["key_matrix"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{master_id}/key-matrix")
def get_key_matrix(master_id: str, db: Session = Depends(get_db)):
    """Retrieves Answer Key Matrix for a master exam and its shuffled variants."""
    master = db.query(MasterExam).filter(MasterExam.id == master_id).first()
    if not master:
        master = db.query(MasterExam).first()
    if not master:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi trong hệ thống.")
    master_id = master.id

    try:
        return get_answer_key_matrix(master_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{master_id}/export-zip")
def export_zip(
    master_id: str,
    format: Optional[str] = Query("pdf", description="Export format: 'pdf'"),
    db: Session = Depends(get_db)
):
    """GET /api/v1/exams/:master_id/export-zip
    Downloads ZIP package containing PDF variants, detailed solutions, answer sheets, and CSV key matrix.
    """
    try:
        m = db.query(MasterExam).filter(MasterExam.id == master_id).first()
        if not m:
            m = db.query(MasterExam).first()
        if not m:
            raise HTTPException(status_code=404, detail="Không tìm thấy đề thi trong hệ thống.")
        master_id = m.id

        variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_id).all()
        if not variants:
            from backend.services.shuffling_engine import generate_shuffled_variants
            generate_shuffled_variants(master_id, db, ["101", "102", "103", "104"])

        zip_path_str = export_exam_package_zip(master_id, db, include_pdf=True, export_format="pdf")
        zip_path = Path(zip_path_str)
        if not zip_path.exists():
            raise HTTPException(status_code=500, detail="Failed to locate generated ZIP package")

        return FileResponse(
            path=str(zip_path),
            filename=zip_path.name,
            media_type="application/zip"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{master_id}/export-pdf")
def export_variant_pdf(
    master_id: str,
    variant_code: str = Query("101", description="Variant code e.g. 101, 102"),
    db: Session = Depends(get_db)
):
    """GET /api/v1/exams/:master_id/export-pdf
    Directly exports and downloads a single variant as a standalone PDF file.
    """
    m = db.query(MasterExam).filter(MasterExam.id == master_id).first()
    if not m:
        m = db.query(MasterExam).first()
    if not m:
        raise HTTPException(status_code=404, detail="Không tìm thấy đề thi trong hệ thống.")
    master_id = m.id

    variant = db.query(ExamVariant).filter(
        ExamVariant.master_exam_id == master_id,
        ExamVariant.variant_code == variant_code
    ).first()
    if not variant:
        from backend.services.shuffling_engine import generate_shuffled_variants
        generate_shuffled_variants(master_id, db, ["101", "102", "103", "104"])
        variant = db.query(ExamVariant).filter(
            ExamVariant.master_exam_id == master_id,
            ExamVariant.variant_code == variant_code
        ).first()

    if not variant:
        raise HTTPException(status_code=404, detail=f"Mã đề {variant_code} không tồn tại trong đề thi này.")

    from backend.config import EXPORTS_DIR
    temp_dir = EXPORTS_DIR / f"temp_{master_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_dir / f"De_Thi_Ma_{variant_code}.pdf"

    export_single_variant_pdf(variant, pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail="Không thể tạo file PDF.")

    return FileResponse(
        path=str(pdf_path),
        filename=pdf_path.name,
        media_type="application/pdf"
    )


@router.post("/{master_id}/analytics")
def analyze_exam_results(
    master_id: str,
    payload: AnalyticsRequest,
    db: Session = Depends(get_db)
):
    """POST /api/v1/exams/:master_id/analytics
    Calculates p-value (difficulty) and D-index (discrimination) from student score results.
    Flags defective questions if D < 0.20.
    """
    student_scores = [s.dict() for s in payload.student_scores]
    try:
        report = compute_item_analytics(
            master_exam_id=master_id,
            student_scores=student_scores,
            db=db
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
