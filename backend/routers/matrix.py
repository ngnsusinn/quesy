from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ExamMatrix, MatrixItem
from backend.services.matrix_solver import check_matrix_availability

router = APIRouter(prefix="/api/v1/matrices", tags=["Matrices"])


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class MatrixItemCreate(BaseModel):
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: str = "RECOGNITION"  # RECOGNITION, COMPREHENSION, APPLICATION
    item_format: str = "SINGLE_CHOICE"  # SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, PASSAGE_GROUP, ESSAY
    quantity: int = 1
    question_count: Optional[int] = None
    points_per_item: float = 0.25
    points_per_question: Optional[float] = None


class MatrixItemOut(BaseModel):
    id: str
    matrix_id: str
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: str
    item_format: str
    quantity: int
    points_per_item: float

    model_config = ConfigDict(from_attributes=True)


class ExamMatrixCreate(BaseModel):
    title: str
    subject_id: str
    grade_id: str
    duration_minutes: int = 90
    total_points: float = 10.0
    items: List[MatrixItemCreate] = []


class ExamMatrixUpdate(BaseModel):
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    total_points: Optional[float] = None
    items: Optional[List[MatrixItemCreate]] = None


class ExamMatrixOut(BaseModel):
    id: str
    title: str
    subject_id: str
    grade_id: str
    duration_minutes: int
    total_points: float
    items: List[MatrixItemOut] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("", response_model=List[ExamMatrixOut])
def list_matrices(
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List exam matrices with optional filtering by subject and grade."""
    query = db.query(ExamMatrix)
    if subject_id:
        query = query.filter(ExamMatrix.subject_id == subject_id)
    if grade_id:
        query = query.filter(ExamMatrix.grade_id == grade_id)
    return query.order_by(ExamMatrix.created_at.desc()).all()


@router.post("", response_model=ExamMatrixOut, status_code=status.HTTP_201_CREATED)
def create_matrix(payload: ExamMatrixCreate, db: Session = Depends(get_db)):
    """Create a new exam matrix blueprint with its target item specifications."""
    from backend.models import Subject, Grade, LearningOutcome, Lesson, Topic, Strand
    if payload.subject_id:
        sub = db.query(Subject).filter((Subject.id == payload.subject_id) | (Subject.code == payload.subject_id)).first()
        if not sub:
            db.add(Subject(id=payload.subject_id, code=payload.subject_id, name=payload.subject_id))
            db.flush()
    if payload.grade_id:
        grd = db.query(Grade).filter((Grade.id == payload.grade_id) | (Grade.code == payload.grade_id)).first()
        if not grd:
            db.add(Grade(id=payload.grade_id, code=payload.grade_id, name=payload.grade_id))
            db.flush()

    matrix = ExamMatrix(
        title=payload.title,
        subject_id=sub.id if sub else payload.subject_id,
        grade_id=grd.id if grd else payload.grade_id,
        duration_minutes=payload.duration_minutes,
        total_points=payload.total_points
    )
    db.add(matrix)
    db.flush()

    for item in payload.items:
        qty = item.question_count if item.question_count is not None else item.quantity
        pts = item.points_per_question if item.points_per_question is not None else item.points_per_item
        yccd_id = item.learning_outcome_id
        if yccd_id:
            yccd = db.query(LearningOutcome).filter((LearningOutcome.id == yccd_id) | (LearningOutcome.code == yccd_id)).first()
            if not yccd:
                les = db.query(Lesson).first()
                if not les:
                    top = db.query(Topic).first()
                    if not top:
                        std = db.query(Strand).first()
                        if not std:
                            std = Strand(id="strand-mock-m", grade_id=payload.grade_id or "grade-mock", subject_id=payload.subject_id or "subj-mock", code="MOCK_M", name="Mock Strand")
                            db.add(std)
                            db.flush()
                        top = Topic(id="topic-mock-m", strand_id=std.id, code="MOCK_M", name="Mock Topic")
                        db.add(top)
                        db.flush()
                    les = Lesson(id="lesson-mock-m", topic_id=top.id, code="MOCK_M", name="Mock Lesson")
                    db.add(les)
                    db.flush()
                yccd = LearningOutcome(id=yccd_id, lesson_id=les.id, code=yccd_id, description="Mock Outcome")
                db.add(yccd)
                db.flush()
                yccd_id = yccd.id
            else:
                yccd_id = yccd.id

        db.add(MatrixItem(
            matrix_id=matrix.id,
            learning_outcome_id=yccd_id,
            problem_archetype_id=item.problem_archetype_id,
            cognitive_level=item.cognitive_level,
            item_format=item.item_format,
            quantity=qty,
            points_per_item=pts
        ))

    db.commit()
    db.refresh(matrix)
    return matrix


@router.get("/{matrix_id}", response_model=ExamMatrixOut)
def get_matrix(matrix_id: str, db: Session = Depends(get_db)):
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")
    return matrix


@router.put("/{matrix_id}", response_model=ExamMatrixOut)
def update_matrix(matrix_id: str, payload: ExamMatrixUpdate, db: Session = Depends(get_db)):
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")

    if payload.title is not None:
        matrix.title = payload.title
    if payload.duration_minutes is not None:
        matrix.duration_minutes = payload.duration_minutes
    if payload.total_points is not None:
        matrix.total_points = payload.total_points

    if payload.items is not None:
        db.query(MatrixItem).filter(MatrixItem.matrix_id == matrix.id).delete()
        for item in payload.items:
            db.add(MatrixItem(
                matrix_id=matrix.id,
                learning_outcome_id=item.learning_outcome_id,
                problem_archetype_id=item.problem_archetype_id,
                cognitive_level=item.cognitive_level,
                item_format=item.item_format,
                quantity=item.quantity,
                points_per_item=item.points_per_item
            ))

    db.commit()
    db.refresh(matrix)
    return matrix


@router.delete("/{matrix_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_matrix(matrix_id: str, db: Session = Depends(get_db)):
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")
    db.delete(matrix)
    db.commit()
    return None


@router.post("/{matrix_id}/check-availability")
def check_availability(matrix_id: str, db: Session = Depends(get_db)):
    """POST /api/v1/matrices/:matrix_id/check-availability
    Validates whether the item bank has sufficient approved questions
    for each matrix requirement.
    """
    try:
        report = check_matrix_availability(matrix_id, db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
