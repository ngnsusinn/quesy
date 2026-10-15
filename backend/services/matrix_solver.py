import random
import uuid
from typing import Dict, Any, List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import not_
from backend.models import ExamMatrix, MatrixItem, Question, MasterExam, MasterExamItem


class InsufficientInventoryError(Exception):
    """Raised when question bank does not have enough approved questions to satisfy matrix."""
    def __init__(self, message: str, report: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.report = report or {}


def _get_excluded_question_ids(
    db: Optional[Session] = None,
    exclude_exam_ids: Optional[List[str]] = None,
    exclude_question_ids: Optional[List[str]] = None,
) -> Set[str]:
    """Aggregate all question IDs that must be excluded:
    - Questions used in recent exam IDs.
    - Explicitly excluded question IDs.
    """
    excluded: Set[str] = set(exclude_question_ids or [])
    if exclude_exam_ids and db is not None:
        used_items = (
            db.query(MasterExamItem.question_id)
            .filter(MasterExamItem.master_exam_id.in_(exclude_exam_ids))
            .all()
        )
        for row in used_items:
            excluded.add(row[0])
    return excluded


def _calculate_psychometric_weight(q: Question, target_p: float = 0.55) -> float:
    """Computes sampling weight prioritizing questions with good discrimination D >= 0.3
    and balanced difficulty p ~ 0.55.
    """
    p_val = q.difficulty_p if q.difficulty_p is not None else 0.55
    d_val = q.discrimination_d if q.discrimination_d is not None else 0.40

    p_score = max(0.1, 1.0 - abs(p_val - target_p) * 1.5)
    d_score = max(0.1, d_val * 2.0)

    weight = (p_score * 0.4) + (d_score * 0.6)
    return max(0.05, weight)


def check_matrix_availability(
    matrix_id: str,
    db: Session,
    exclude_exam_ids: Optional[List[str]] = None,
    exclude_question_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Validates whether the item bank has sufficient APPROVED questions
    to assemble an exam according to the ExamMatrix specification.
    """
    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise ValueError(f"ExamMatrix with id '{matrix_id}' not found.")

    excluded_ids = _get_excluded_question_ids(db, exclude_exam_ids, exclude_question_ids)

    items_status = []
    warnings: List[str] = []
    overall_sufficient = True
    total_required = 0
    total_available = 0
    total_deficit = 0

    for idx, item in enumerate(matrix.items, start=1):
        # Query approved questions matching matrix constraints
        q_query = db.query(Question).filter(
            Question.status == "APPROVED",
            Question.learning_outcome_id == item.learning_outcome_id,
            Question.cognitive_level == item.cognitive_level,
            Question.item_format == item.item_format,
            Question.is_defective.is_(False),
        )

        if item.problem_archetype_id:
            q_query = q_query.filter(Question.problem_archetype_id == item.problem_archetype_id)

        if excluded_ids:
            q_query = q_query.filter(not_(Question.id.in_(list(excluded_ids))))

        available_count = q_query.count()
        sufficient = available_count >= item.quantity
        deficit = max(0, item.quantity - available_count)

        if not sufficient:
            overall_sufficient = False
            total_deficit += deficit
            yccd_code = item.learning_outcome.code if item.learning_outcome else item.learning_outcome_id
            warn_msg = (
                f"Cảnh báo thiếu câu hỏi ở ô ma trận #{idx}: YCCĐ='{yccd_code}', "
                f"Mức độ='{item.cognitive_level}', Dạng='{item.item_format}'. "
                f"Yêu cầu: {item.quantity} câu, Khả dụng: {available_count} câu (Thiếu {deficit} câu)."
            )
            warnings.append(warn_msg)

        total_required += item.quantity
        total_available += available_count

        items_status.append({
            "matrix_item_id": item.id,
            "cell_index": idx,
            "learning_outcome_id": item.learning_outcome_id,
            "learning_outcome_code": item.learning_outcome.code if item.learning_outcome else None,
            "problem_archetype_id": item.problem_archetype_id,
            "cognitive_level": item.cognitive_level,
            "item_format": item.item_format,
            "required_quantity": item.quantity,
            "available_quantity": available_count,
            "is_sufficient": sufficient,
            "deficit": deficit,
        })

    return {
        "matrix_id": matrix.id,
        "matrix_title": matrix.title,
        "is_sufficient": overall_sufficient,
        "total_required": total_required,
        "total_available": total_available,
        "total_deficit": total_deficit,
        "items": items_status,
        "warnings": warnings,
    }


def solve_and_generate_master_exam(
    matrix_id: str,
    db: Session,
    title: Optional[str] = None,
    exclude_exam_ids: Optional[List[str]] = None,
    excluded_question_ids: Optional[List[str]] = None,
    allow_partial: bool = False,
    random_seed: Optional[int] = None,
) -> MasterExam:
    """Solves the constraint satisfaction problem defined by the ExamMatrix
    and generates a new MasterExam with MasterExamItems.

    - Matches each cell (YCCD, Problem Archetype, Cognitive Level, Question Type).
    - Applies exclusion rules (excludes questions used in recent exam IDs or excluded list).
    - Checks bank availability and warns if question inventory is insufficient.
    - Applies psychometric weighting (prioritizing D >= 0.3 and non-defective items).
    """
    if random_seed is not None:
        random.seed(random_seed)

    matrix = db.query(ExamMatrix).filter(ExamMatrix.id == matrix_id).first()
    if not matrix:
        raise ValueError(f"ExamMatrix with id '{matrix_id}' not found.")

    # 1. Aggregate excluded question IDs (recent exams + explicit exclusion)
    excluded_set = _get_excluded_question_ids(db, exclude_exam_ids, excluded_question_ids)

    # 2. Check bank availability
    inv_check = check_matrix_availability(
        matrix_id=matrix.id,
        db=db,
        exclude_exam_ids=exclude_exam_ids,
        exclude_question_ids=excluded_question_ids,
    )

    if not inv_check["is_sufficient"] and not allow_partial:
        deficit = inv_check["total_deficit"]
        warn_summary = "; ".join(inv_check["warnings"])
        raise InsufficientInventoryError(
            f"Insufficient questions in bank (missing {deficit} questions). {warn_summary}",
            inv_check,
        )

    selected_questions: List[Tuple[Question, MatrixItem]] = []

    # Format ordering: Section 1 = SINGLE_CHOICE, Section 2 = TRUE_FALSE_GROUP, Section 3 = SHORT_ANSWER, Section 4 = ESSAY/OTHER
    section_map = {
        "SINGLE_CHOICE": 1,
        "TRUE_FALSE_GROUP": 2,
        "SHORT_ANSWER": 3,
        "PASSAGE_GROUP": 4,
        "ESSAY": 4,
    }

    # Sort matrix items so questions are ordered logically by section
    sorted_items = sorted(matrix.items, key=lambda it: section_map.get(it.item_format, 99))
    used_question_ids = set(excluded_set)

    for item in sorted_items:
        q_query = db.query(Question).filter(
            Question.status == "APPROVED",
            Question.learning_outcome_id == item.learning_outcome_id,
            Question.cognitive_level == item.cognitive_level,
            Question.item_format == item.item_format,
            Question.is_defective.is_(False),
        )

        if item.problem_archetype_id:
            q_query = q_query.filter(Question.problem_archetype_id == item.problem_archetype_id)

        candidates = [q for q in q_query.all() if q.id not in used_question_ids]

        if len(candidates) < item.quantity and not allow_partial:
            # Fallback check: relax archetype constraint if specified
            if item.problem_archetype_id:
                relaxed_query = db.query(Question).filter(
                    Question.status == "APPROVED",
                    Question.learning_outcome_id == item.learning_outcome_id,
                    Question.cognitive_level == item.cognitive_level,
                    Question.item_format == item.item_format,
                    Question.is_defective.is_(False),
                )
                candidates = [q for q in relaxed_query.all() if q.id not in used_question_ids]

        if len(candidates) < item.quantity and not allow_partial:
            yccd_name = item.learning_outcome.code if item.learning_outcome else item.learning_outcome_id
            raise InsufficientInventoryError(
                f"Insufficient questions for YCCĐ '{yccd_name}' "
                f"({item.cognitive_level}, {item.item_format}). Required {item.quantity}, available {len(candidates)}.",
                inv_check,
            )

        # Weighted selection without replacement prioritizing psychometric quality
        pick_count = min(len(candidates), item.quantity)
        picked: List[Question] = []
        pool = list(candidates)

        while len(picked) < pick_count and pool:
            weights = [_calculate_psychometric_weight(q) for q in pool]
            chosen = random.choices(pool, weights=weights, k=1)[0]
            pool.remove(chosen)
            picked.append(chosen)

        for q in picked:
            used_question_ids.add(q.id)
            selected_questions.append((q, item))

    # Create MasterExam record
    master_exam = MasterExam(
        id=str(uuid.uuid4()),
        matrix_id=matrix.id,
        title=title or f"Đề Gốc - {matrix.title}",
        subject_id=matrix.subject_id,
        grade_id=matrix.grade_id,
        total_questions=len(selected_questions),
        total_points=matrix.total_points,
        status="GENERATED",
    )
    db.add(master_exam)
    db.flush()

    # Create MasterExamItems
    order_idx = 1
    for q, item in selected_questions:
        sec = section_map.get(q.item_format, 1)
        master_item = MasterExamItem(
            id=str(uuid.uuid4()),
            master_exam_id=master_exam.id,
            question_id=q.id,
            section_number=sec,
            question_number=order_idx,
            points=item.points_per_item,
        )
        master_item.question = q
        db.add(master_item)
        order_idx += 1

    db.commit()
    db.refresh(master_exam)
    return master_exam
