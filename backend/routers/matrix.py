from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import ExamMatrix, MatrixItem
from backend.services.matrix_solver import check_matrix_availability
from backend.config import EXPORTS_DIR
import csv
import io

router = APIRouter(prefix="/api/v1/matrices", tags=["Matrices"])
router_singular = APIRouter(prefix="/api/v1/matrix", tags=["Matrices"])


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
@router_singular.get("", response_model=List[ExamMatrixOut])
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
@router_singular.post("", response_model=ExamMatrixOut, status_code=status.HTTP_201_CREATED)
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
@router_singular.get("/{matrix_id}", response_model=ExamMatrixOut)
def get_matrix(matrix_id: str, db: Session = Depends(get_db)):
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")
    return matrix


@router.put("/{matrix_id}", response_model=ExamMatrixOut)
@router_singular.put("/{matrix_id}", response_model=ExamMatrixOut)
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
@router_singular.delete("/{matrix_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_matrix(matrix_id: str, db: Session = Depends(get_db)):
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")
    db.delete(matrix)
    db.commit()
    return None


@router.post("/check-availability")
@router_singular.post("/check-availability")
@router.post("/{matrix_id}/check-availability")
@router_singular.post("/{matrix_id}/check-availability")
def check_availability(matrix_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Validates whether the item bank has sufficient approved questions
    for each matrix requirement.
    """
    if not matrix_id or matrix_id == "default":
        m = db.query(ExamMatrix).first()
        if not m:
            raise HTTPException(status_code=404, detail="No exam matrix found in system.")
        matrix_id = m.id
    try:
        report = check_matrix_availability(matrix_id, db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{matrix_id}/spec")
@router_singular.get("/{matrix_id}/spec")
def get_matrix_spec(
    matrix_id: str,
    format: str = Query("json", description="json, csv, or pdf"),
    db: Session = Depends(get_db)
):
    """Exports exam matrix specification in json, csv (utf-8 bom), or pdf (ReportLab)."""
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        matrix = db.query(ExamMatrix).first()
    if not matrix:
        raise HTTPException(status_code=404, detail="ExamMatrix not found")

    if format.lower() == "json":
        return {
            "id": matrix.id,
            "title": matrix.title,
            "subject_id": matrix.subject_id,
            "grade_id": matrix.grade_id,
            "duration_minutes": matrix.duration_minutes,
            "total_points": matrix.total_points,
            "items": [
                {
                    "id": i.id,
                    "learning_outcome_id": i.learning_outcome_id,
                    "cognitive_level": i.cognitive_level,
                    "item_format": i.item_format,
                    "quantity": i.quantity,
                    "points_per_item": i.points_per_item
                }
                for i in matrix.items
            ]
        }

    elif format.lower() == "csv":
        output = io.StringIO()
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["STT", "Mã YCCĐ", "Mức độ nhận thức", "Dạng câu hỏi", "Số lượng", "Điểm/câu", "Tổng điểm"])
        for idx, item in enumerate(matrix.items, 1):
            yccd = item.learning_outcome.code if item.learning_outcome else (item.learning_outcome_id or "N/A")
            tot = round(item.quantity * item.points_per_item, 2)
            writer.writerow([idx, yccd, item.cognitive_level, item.item_format, item.quantity, item.points_per_item, tot])
        
        csv_data = output.getvalue()
        return Response(
            content=csv_data,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=BanDacTa_Matrix_{matrix.id}.csv"}
        )

    elif format.lower() == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from backend.services.docx_exporter import register_vietnamese_fonts
            from reportlab.pdfbase import pdfmetrics

            register_vietnamese_fonts()
            registered = pdfmetrics.getRegisteredFontNames() if 'pdfmetrics' in globals() else []
            font_main = 'TimesNewRoman' if 'TimesNewRoman' in registered else 'Helvetica'
            font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in registered else 'Helvetica-Bold'

            export_dir = EXPORTS_DIR / "specs"
            export_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = export_dir / f"BanDacTa_Matrix_{matrix.id}.pdf"

            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=16, leading=20, alignment=1)
            style_subtitle = ParagraphStyle('Sub', fontName=font_main, fontSize=11, leading=15, alignment=1)
            style_cell = ParagraphStyle('Cell', fontName=font_main, fontSize=10, leading=13)
            style_header = ParagraphStyle('Header', fontName=font_bold, fontSize=10, leading=13, textColor=colors.white)

            story = [
                Paragraph("BẢN ĐẶC TẢ MA TRẬN ĐỀ THI", style_title),
                Spacer(1, 5),
                Paragraph(f"<b>Kỳ thi:</b> {matrix.title} | <b>Thời gian:</b> {matrix.duration_minutes} phút | <b>Tổng điểm:</b> {matrix.total_points}", style_subtitle),
                Spacer(1, 15)
            ]

            table_data = [[
                Paragraph("STT", style_header),
                Paragraph("Yêu cầu cần đạt", style_header),
                Paragraph("Mức độ", style_header),
                Paragraph("Dạng câu hỏi", style_header),
                Paragraph("SL", style_header),
                Paragraph("Điểm", style_header),
                Paragraph("Tổng", style_header),
            ]]

            for idx, item in enumerate(matrix.items, 1):
                yccd = item.learning_outcome.code if item.learning_outcome else (item.learning_outcome_id or "N/A")
                tot = round(item.quantity * item.points_per_item, 2)
                table_data.append([
                    Paragraph(str(idx), style_cell),
                    Paragraph(str(yccd), style_cell),
                    Paragraph(str(item.cognitive_level), style_cell),
                    Paragraph(str(item.item_format), style_cell),
                    Paragraph(str(item.quantity), style_cell),
                    Paragraph(str(item.points_per_item), style_cell),
                    Paragraph(str(tot), style_cell),
                ])

            t = Table(table_data, colWidths=[35, 140, 90, 100, 40, 50, 50])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#002244')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
            doc.build(story)

            if pdf_path.exists():
                return FileResponse(path=str(pdf_path), filename=pdf_path.name, media_type="application/pdf")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    raise HTTPException(status_code=400, detail="Invalid format specified. Use json, csv, or pdf.")
