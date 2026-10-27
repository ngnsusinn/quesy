import json
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Question, QuestionOption, SubStatement
from backend.schemas import CognitiveLevel, ItemFormat
from backend.services.tagging_service import check_question_duplicate, suggest_auto_tagging

router = APIRouter(prefix="/api/v1/questions", tags=["Questions"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class OptionCreate(BaseModel):
    label: str
    content: str
    is_correct: bool = False
    is_fixed: bool = False
    order_index: int = 0


class OptionOut(BaseModel):
    id: str
    label: str
    content: str
    is_correct: bool
    is_fixed: bool
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class SubStatementCreate(BaseModel):
    label: str
    content: str
    is_true: bool = False
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order_index: int = 0


class SubStatementOut(BaseModel):
    id: str
    label: str
    content: str
    is_true: bool
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    strand_id: Optional[str] = None
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: CognitiveLevel = CognitiveLevel.RECOGNITION
    item_format: ItemFormat = ItemFormat.SINGLE_CHOICE
    stem: str
    short_answer_key: Optional[str] = None
    tolerance: Optional[float] = 0.0
    image_urls: Optional[List[str]] = []
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    status: str = "APPROVED"
    passage_id: Optional[str] = None
    passage_content: Optional[str] = None
    embedding: Optional[List[float]] = None
    options: Optional[List[OptionCreate]] = []
    sub_statements: Optional[List[SubStatementCreate]] = []


class QuestionUpdate(BaseModel):
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    strand_id: Optional[str] = None
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: Optional[str] = None
    item_format: Optional[str] = None
    stem: Optional[str] = None
    short_answer_key: Optional[str] = None
    tolerance: Optional[float] = None
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    status: Optional[str] = None
    passage_id: Optional[str] = None
    passage_content: Optional[str] = None
    options: Optional[List[OptionCreate]] = None
    sub_statements: Optional[List[SubStatementCreate]] = None


class QuestionOut(BaseModel):
    id: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    strand_id: Optional[str] = None
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: str
    item_format: str
    stem: str
    short_answer_key: Optional[str] = None
    tolerance: Optional[float] = 0.0
    image_urls: Optional[str] = None
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    status: str
    passage_id: Optional[str] = None
    passage_content: Optional[str] = None
    difficulty_p: Optional[float] = None
    discrimination_d: Optional[float] = None
    is_defective: Optional[bool] = False
    options: List[OptionOut] = []
    sub_statements: List[SubStatementOut] = []

    model_config = ConfigDict(from_attributes=True)


class DuplicateCheckRequest(BaseModel):
    stem: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    threshold: Optional[float] = 0.90


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    similarity_score: float
    threshold: float
    matching_question: Optional[QuestionOut] = None


class AutoTagRequest(BaseModel):
    stem: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("", response_model=List[QuestionOut])
def list_questions(
    learning_outcome_id: Optional[str] = None,
    problem_archetype_id: Optional[str] = None,
    cognitive_level: Optional[str] = None,
    item_format: Optional[str] = None,
    question_type: Optional[str] = None,  # Alias for item_format
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None,
    strand_id: Optional[str] = None,
    topic_id: Optional[str] = None,
    lesson_id: Optional[str] = None,
    keyword: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Filters questions in the item bank by YCCĐ, Archetype, CognitiveLevel, Format, Strand, Topic, Lesson, Keyword."""
    query = db.query(Question)

    if learning_outcome_id:
        query = query.filter(Question.learning_outcome_id == learning_outcome_id)
    if problem_archetype_id:
        query = query.filter(Question.problem_archetype_id == problem_archetype_id)
    if cognitive_level:
        query = query.filter(Question.cognitive_level == cognitive_level)
    fmt = item_format or question_type
    if fmt:
        query = query.filter(Question.item_format == fmt)
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if grade_id:
        query = query.filter(Question.grade_id == grade_id)
    if strand_id:
        query = query.filter(Question.strand_id == strand_id)
    if topic_id:
        query = query.filter(Question.topic_id == topic_id)
    if lesson_id:
        query = query.filter(Question.lesson_id == lesson_id)
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter((Question.stem.ilike(kw)) | (Question.explanation.ilike(kw)))
    if status_filter:
        query = query.filter(Question.status == status_filter)

    return query.order_by(Question.created_at.desc()).offset(offset).limit(limit).all()


@router.post("", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    """Creates a new question with its options or sub-statements in the item bank."""
    if payload.embedding:
        from backend.services.deduplication import check_duplicate_question
        existing_qs = db.query(Question).filter(Question.embedding_vector.isnot(None)).all()
        existing_list = [
            {"id": q.id, "stem": q.stem, "embedding": q.embedding_vector}
            for q in existing_qs
        ]
        dup_result = check_duplicate_question(payload.embedding, existing_list, threshold=0.90)
        if dup_result["is_duplicate"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=dup_result["warning"] or "Duplicate question detected"
            )

    from backend.models import Subject, Grade, LearningOutcome, Lesson, Topic, Strand
    sub = None
    grd = None
    if payload.subject_id:
        sub = db.query(Subject).filter((Subject.id == payload.subject_id) | (Subject.code == payload.subject_id)).first()
        if not sub:
            sub = Subject(id=payload.subject_id, code=payload.subject_id, name=payload.subject_id)
            db.add(sub)
            db.flush()
    if payload.grade_id:
        grd = db.query(Grade).filter((Grade.id == payload.grade_id) | (Grade.code == payload.grade_id)).first()
        if not grd:
            grd = Grade(id=payload.grade_id, code=payload.grade_id, name=payload.grade_id)
            db.add(grd)
            db.flush()
    if payload.learning_outcome_id:
        yccd = db.query(LearningOutcome).filter((LearningOutcome.id == payload.learning_outcome_id) | (LearningOutcome.code == payload.learning_outcome_id)).first()
        if not yccd:
            les = db.query(Lesson).first()
            if not les:
                top = db.query(Topic).first()
                if not top:
                    std = db.query(Strand).first()
                    if not std:
                        std = Strand(id="strand-mock", grade_id=payload.grade_id or "grade-mock", subject_id=payload.subject_id or "subj-mock", code="MOCK", name="Mock Strand")
                        db.add(std)
                        db.flush()
                    top = Topic(id="topic-mock", strand_id=std.id, code="MOCK", name="Mock Topic")
                    db.add(top)
                    db.flush()
                les = Lesson(id="lesson-mock", topic_id=top.id, code="MOCK", name="Mock Lesson")
                db.add(les)
                db.flush()
            yccd = LearningOutcome(id=payload.learning_outcome_id, lesson_id=les.id, code=payload.learning_outcome_id, description="Mock Outcome")
            db.add(yccd)
            db.flush()
        lo_id = yccd.id
    else:
        lo_id = None

    images_str = json.dumps(payload.image_urls or [], ensure_ascii=False)

    q = Question(
        subject_id=sub.id if sub else payload.subject_id,
        grade_id=grd.id if grd else payload.grade_id,
        strand_id=payload.strand_id,
        topic_id=payload.topic_id,
        lesson_id=payload.lesson_id,
        learning_outcome_id=lo_id,
        problem_archetype_id=payload.problem_archetype_id,
        cognitive_level=payload.cognitive_level,
        item_format=payload.item_format,
        stem=payload.stem,
        image_urls=images_str,
        explanation=payload.explanation,
        source_reference=payload.source_reference,
        status=payload.status,
        passage_id=payload.passage_id,
        passage_content=payload.passage_content,
        embedding_vector=payload.embedding,
    )
    db.add(q)
    db.flush()

    if payload.options:
        for idx, opt in enumerate(payload.options):
            db.add(QuestionOption(
                question_id=q.id,
                label=opt.label,
                content=opt.content,
                is_correct=opt.is_correct,
                is_fixed=opt.is_fixed,
                order_index=opt.order_index or (idx + 1)
            ))

    if payload.sub_statements:
        for idx, sub in enumerate(payload.sub_statements):
            db.add(SubStatement(
                question_id=q.id,
                label=sub.label,
                content=sub.content,
                is_true=sub.is_true,
                correct_answer=sub.correct_answer,
                explanation=sub.explanation,
                order_index=sub.order_index or (idx + 1)
            ))

    db.commit()
    db.refresh(q)
    return q


@router.get("/count")
def get_questions_count(db: Session = Depends(get_db)):
    total = db.query(Question).count()
    single_choice = db.query(Question).filter(Question.item_format == "SINGLE_CHOICE").count()
    true_false = db.query(Question).filter(Question.item_format == "TRUE_FALSE_GROUP").count()
    short_answer = db.query(Question).filter(Question.item_format == "SHORT_ANSWER").count()
    return {
        "total": total,
        "single_choice": single_choice,
        "true_false": true_false,
        "short_answer": short_answer
    }


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@router.put("/{question_id}", response_model=QuestionOut)
def update_question(question_id: str, payload: QuestionUpdate, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = payload.model_dump(exclude_unset=True)
    options_data = update_data.pop("options", None)
    sub_data = update_data.pop("sub_statements", None)

    for field, val in update_data.items():
        setattr(q, field, val)

    if options_data is not None:
        db.query(QuestionOption).filter(QuestionOption.question_id == q.id).delete()
        for idx, opt in enumerate(options_data):
            db.add(QuestionOption(
                question_id=q.id,
                label=opt["label"],
                content=opt["content"],
                is_correct=opt.get("is_correct", False),
                is_fixed=opt.get("is_fixed", False),
                order_index=opt.get("order_index", idx + 1)
            ))

    if sub_data is not None:
        db.query(SubStatement).filter(SubStatement.question_id == q.id).delete()
        for idx, sub in enumerate(sub_data):
            db.add(SubStatement(
                question_id=q.id,
                label=sub["label"],
                content=sub["content"],
                is_true=sub.get("is_true", False),
                correct_answer=sub.get("correct_answer"),
                explanation=sub.get("explanation"),
                order_index=sub.get("order_index", idx + 1)
            ))

    db.commit()
    db.refresh(q)
    return q


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: str, db: Session = Depends(get_db)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return None


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate(payload: DuplicateCheckRequest, db: Session = Depends(get_db)):
    """Deduplication check endpoint: POST /api/v1/questions/check-duplicate
    Calculates cosine similarity and returns similarity score and matching question if >= 0.90.
    """
    threshold = payload.threshold if payload.threshold is not None else 0.90
    is_dup, score, matched = check_question_duplicate(
        stem=payload.stem,
        db=db,
        subject_id=payload.subject_id,
        grade_id=payload.grade_id,
        threshold=threshold
    )

    return DuplicateCheckResponse(
        is_duplicate=is_dup,
        similarity_score=score,
        threshold=threshold,
        matching_question=matched if is_dup else None
    )


@router.post("/auto-tag")
def auto_tag(payload: AutoTagRequest, db: Session = Depends(get_db)):
    """Suggests Circular 32 taxonomy tags and cognitive levels based on question content."""
    return suggest_auto_tagging(
        stem=payload.stem,
        db=db,
        subject_id=payload.subject_id,
        grade_id=payload.grade_id
    )





class ExportQuestionsRequest(BaseModel):
    format: str = Field("json", description="json, csv, latex, pdf")
    question_ids: Optional[List[str]] = None


@router.post("/export")
def export_questions(payload: ExportQuestionsRequest, db: Session = Depends(get_db)):
    query = db.query(Question)
    if payload.question_ids:
        query = query.filter(Question.id.in_(payload.question_ids))
    questions = query.all()

    if payload.format == "csv":
        import csv
        import io
        from fastapi.responses import StreamingResponse
        output = io.StringIO()
        output.write('\ufeff')  # UTF-8 BOM
        writer = csv.writer(output)
        writer.writerow(["ID", "Format", "CognitiveLevel", "Stem", "Explanation"])
        for q in questions:
            writer.writerow([q.id, q.item_format, q.cognitive_level, q.stem, q.explanation or ""])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=quesy_bank_export.csv"}
        )
    elif payload.format == "latex":
        latex_lines = []
        for q in questions:
            latex_lines.append(r"\\begin{ex}")
            latex_lines.append(q.stem)
            if q.item_format == "SINGLE_CHOICE" and q.options:
                latex_lines.append(r"\\choice")
                for opt in q.options:
                    prefix = r"\\True " if opt.is_correct else ""
                    latex_lines.append(f"{{{prefix}{opt.content}}}")
            elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
                latex_lines.append(r"\\choiceTF")
                for sub in q.sub_statements:
                    prefix = r"\\True " if sub.is_true else ""
                    latex_lines.append(f"{{{prefix}{sub.content}}}")
            elif q.item_format == "SHORT_ANSWER":
                ans = q.short_answer_key or "0"
                latex_lines.append(f"\\\\shortans{{{ans}}}")
            if q.explanation:
                latex_lines.append(r"\\begin{loigiai}")
                latex_lines.append(q.explanation)
                latex_lines.append(r"\\end{loigiai}")
            latex_lines.append(r"\\end{ex}")
            latex_lines.append("")
        return {"success": True, "format": "latex", "latex_code": "\\n".join(latex_lines)}
    else:
        return {
            "success": True,
            "count": len(questions),
            "questions": [
                {
                    "id": q.id,
                    "stem": q.stem,
                    "item_format": q.item_format,
                    "cognitive_level": q.cognitive_level,
                    "explanation": q.explanation
                }
                for q in questions
            ]
        }


class ImportQuestionsRequest(BaseModel):
    latex_code: Optional[str] = None
    questions_json: Optional[List[Dict[str, Any]]] = None


@router.post("/import")
def import_questions(payload: ImportQuestionsRequest, db: Session = Depends(get_db)):
    from backend.services.composer_service import extract_questions_from_latex
    imported_list = []
    if payload.latex_code:
        extracted = extract_questions_from_latex(payload.latex_code)
        for q_data in extracted:
            tags = suggest_auto_tagging(stem=q_data["stem"], db=db)
            q = Question(
                stem=q_data["stem"],
                item_format=q_data.get("item_format", "SINGLE_CHOICE"),
                short_answer_key=q_data.get("short_answer_value") or q_data.get("short_answer_key"),
                tolerance=q_data.get("tolerance", 0.0),
                cognitive_level=q_data.get("cognitive_level", tags.get("cognitive_level", "RECOGNITION")),
                learning_outcome_id=tags.get("learning_outcome_id"),
                status="APPROVED"
            )
            if q_data.get("options"):
                for idx, opt in enumerate(q_data["options"]):
                    q.options.append(QuestionOption(
                        label=opt.get("label", "A"),
                        content=opt.get("content", ""),
                        is_correct=opt.get("is_correct", False),
                        order_index=idx
                    ))
            if q_data.get("sub_statements"):
                for idx, sub in enumerate(q_data["sub_statements"]):
                    q.sub_statements.append(SubStatement(
                        label=sub.get("label", "a"),
                        content=sub.get("content", ""),
                        is_true=sub.get("is_true", False),
                        order_index=idx
                    ))
            db.add(q)
            imported_list.append(q)
    elif payload.questions_json:
        for q_item in payload.questions_json:
            stem = q_item.get("stem", "")
            tags = suggest_auto_tagging(stem=stem, db=db)
            q = Question(
                stem=stem,
                item_format=q_item.get("item_format", "SINGLE_CHOICE"),
                short_answer_key=q_item.get("short_answer_key"),
                tolerance=q_item.get("tolerance", 0.0),
                cognitive_level=q_item.get("cognitive_level", tags.get("cognitive_level", "RECOGNITION")),
                learning_outcome_id=q_item.get("learning_outcome_id") or tags.get("learning_outcome_id"),
                status="APPROVED"
            )
            for opt in q_item.get("options", []):
                q.options.append(QuestionOption(
                    label=opt.get("label", "A"),
                    content=opt.get("content", ""),
                    is_correct=opt.get("is_correct", False)
                ))
            for sub in q_item.get("sub_statements", []):
                q.sub_statements.append(SubStatement(
                    label=sub.get("label", "a"),
                    content=sub.get("content", ""),
                    is_true=sub.get("is_true", False)
                ))
            db.add(q)
            imported_list.append(q)

    db.commit()
    return {
        "success": True,
        "imported_count": len(imported_list),
        "message": f"Successfully imported {len(imported_list)} questions into the bank."
    }
