import json
import re
import random
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from backend.models import MasterExam, MasterExamItem, ExamVariant, ExamVariantItem, Question, QuestionOption


# =========================================================================
# RULE-01: True/False 4-substatement progressive grading
# (Decision 764/QĐ-BGDĐT)
# =========================================================================

RULE_01_SCALE = {
    0: 0.0,
    1: 0.10,
    2: 0.25,
    3: 0.50,
    4: 1.00,
}


def calculate_rule01_score(
    student_answers: Dict[str, bool],
    correct_answers: Dict[str, bool],
    max_points: float = 1.0,
) -> float:
    """RULE-01: True/False 4-substatement progressive grading logic.
    Conforms strictly to Decision 764/QĐ-BGDĐT:
    - 1 correct sub-statement: 0.10 points (10%)
    - 2 correct sub-statements: 0.25 points (25%)
    - 3 correct sub-statements: 0.50 points (50%)
    - 4 correct sub-statements: 1.00 points (100%)
    - 0 correct sub-statements: 0.00 points (0%)

    Args:
        student_answers: Student responses {'a': True, 'b': False, ...}
        correct_answers: Ground truth {'a': True, 'b': True, ...}
        max_points: Total points for the question (default 1.0)

    Returns:
        Progressive score scaled to max_points.
    """
    if not correct_answers:
        return 0.0

    correct_count = 0
    for label, expected_val in correct_answers.items():
        clean_lbl = str(label).strip().lower()
        # Find matching student key case-insensitively
        for s_lbl, s_val in student_answers.items():
            if str(s_lbl).strip().lower() == clean_lbl:
                if bool(s_val) == bool(expected_val):
                    correct_count += 1
                break

    base_score = RULE_01_SCALE.get(correct_count, 0.0)
    return round(base_score * max_points, 4)


calculate_true_false_score = calculate_rule01_score


# =========================================================================
# RULE-02: Option Anchor Rule
# =========================================================================

ANCHOR_KEYWORD_PATTERNS = [
    r"\bcả\s+[ab]\s+và\s+[bc]\b",
    r"\bcả\s+[abc],\s+[bc]\s+và\s+[cd]\b",
    r"\bcả\s+[a-d]\s+và\s+[a-d]\b",
    r"\bcả\s+(?:3|ba)\s+(?:đáp\s+án|phương\s+án|ý)\s+trên\b",
    r"\btất\s+cả\s+(?:các\s+)?(?:đáp\s+án|phương\s+án|ý)\s+trên\b",
    r"\btất\s+cả\s+phương\s+án\s+trên\b",
    r"\btất\s+cả\s+đáp\s+án\s+trên\b",
    r"\btất\s+cả\s+đều\s+(?:đúng|sai)\b",
    r"\bkhông\s+có\s+(?:đáp\s+án|phương\s+án|giá\s+trị)(?:\s+nào)?(?:\s+(?:đúng|thỏa\s+mãn))?\b",
    r"\bkhông\s+tồn\s+tại\b",
]

ANCHOR_REGEX = re.compile("|".join(ANCHOR_KEYWORD_PATTERNS), re.IGNORECASE)


def is_anchor_option(opt: Any) -> bool:
    """Check if an option must be locked to position D (RULE-02)."""
    if getattr(opt, "is_fixed", False):
        return True
    content = getattr(opt, "content", "") or ""
    if ANCHOR_REGEX.search(content.strip()):
        return True
    return False


def shuffle_options_with_anchor_rule(
    options: List[QuestionOption],
    rng: Optional[random.Random] = None,
) -> Tuple[List[QuestionOption], Dict[str, str], str]:
    """Applies Option Anchor Rule (RULE-02):
    - Any option with is_fixed=True or containing position-dependent phrases
      ('Cả A và B', 'Tất cả các đáp án trên', 'Không có đáp án nào') is LOCKED at position D (the last slot).
    - Other options are randomly permuted across the remaining slots.

    Returns:
    - new_ordered_options: list of options in new order
    - option_mapping: dict mapping original label -> new label
    - correct_variant_label: the label of the correct option in this variant
    """
    labels = ["A", "B", "C", "D", "E", "F"][:len(options)]
    _rnd = rng or random

    fixed_options = []
    movable_options = []

    for opt in options:
        if is_anchor_option(opt):
            fixed_options.append(opt)
        else:
            movable_options.append(opt)

    # Permute movable options
    _rnd.shuffle(movable_options)

    # Fixed options stay at the end (position D for 4 options)
    variant_options = movable_options + fixed_options

    option_mapping: Dict[str, str] = {}
    correct_variant_label = ""

    for idx, opt in enumerate(variant_options):
        new_label = labels[idx] if idx < len(labels) else str(idx + 1)
        orig_label = opt.label
        option_mapping[orig_label] = new_label
        if opt.is_correct:
            correct_variant_label = new_label

    return variant_options, option_mapping, correct_variant_label


def generate_shuffled_variants(
    master_exam_id: str,
    db: Session,
    variant_codes: Optional[List[str]] = None,
    seed: Optional[int] = None,
) -> List[ExamVariant]:
    """Generates N safe exam variants adhering to 4 core principles:
    1. Section Integrity: questions remain within their respective section (Part I, Part II, Part III).
    2. Passage Integrity (RULE-03): passage parent and child questions remain strictly contiguous.
    3. Option Anchor Rule (RULE-02): position-dependent options locked at last position (D).
    4. Key Generator: derives exact answer key matrix across all variants.
    """
    master_exam = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master_exam:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    if not variant_codes:
        variant_codes = ["101", "102", "103", "104"]

    # Delete existing variants if re-shuffling
    db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_exam_id).delete()
    db.flush()

    master_items = master_exam.items  # Ordered by section and order_index

    # Group items by section (Section 1: SINGLE_CHOICE, 2: TRUE_FALSE, 3: SHORT_ANSWER, 4: OTHER)
    sections_dict: Dict[int, List[MasterExamItem]] = {}
    for item in master_items:
        sections_dict.setdefault(item.section, []).append(item)

    created_variants: List[ExamVariant] = []

    for v_idx, code in enumerate(variant_codes):
        # Create deterministic RNG per variant if seed provided
        variant_rng = random.Random(seed + v_idx) if seed is not None else random.Random()

        variant = ExamVariant(
            master_exam_id=master_exam.id,
            variant_code=str(code)
        )
        db.add(variant)
        db.flush()

        variant_order_index = 1

        for sec_num in sorted(sections_dict.keys()):
            sec_items = sections_dict[sec_num]

            # Group by passage to preserve Passage Integrity (RULE-03)
            # Standalone items form 1-item blocks; passage child questions form multi-item blocks
            blocks: List[List[MasterExamItem]] = []
            passage_groups: Dict[str, List[MasterExamItem]] = {}

            for it in sec_items:
                pid = it.question.passage_id if it.question else None
                if pid:
                    passage_groups.setdefault(pid, []).append(it)
                else:
                    blocks.append([it])

            # Append passage blocks (preserving inner child question order)
            for p_items in passage_groups.values():
                blocks.append(p_items)

            # Shuffle blocks within section (Section Integrity + Passage Integrity)
            variant_rng.shuffle(blocks)

            # Flatten blocks: child questions in each passage block remain strictly contiguous
            shuffled_sec_items: List[MasterExamItem] = []
            for blk in blocks:
                shuffled_sec_items.extend(blk)

            # Process each question in this section
            for item in shuffled_sec_items:
                q = item.question
                opt_mapping_json = None
                ans_key_str = ""

                if q.item_format == "SINGLE_CHOICE" and q.options:
                    _, opt_mapping, correct_lbl = shuffle_options_with_anchor_rule(list(q.options), rng=variant_rng)
                    opt_mapping_json = json.dumps(opt_mapping, ensure_ascii=False)
                    ans_key_str = correct_lbl
                elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
                    # TRUE_FALSE affirmations: format e.g. "a-Đ, b-Đ, c-S, d-Đ"
                    tf_parts = []
                    for sub in q.sub_statements:
                        tf_parts.append(f"{sub.label}-{'Đ' if sub.is_true else 'S'}")
                    ans_key_str = ", ".join(tf_parts)
                elif q.item_format == "SHORT_ANSWER":
                    # Check first sub_statement correct_answer or stem regex
                    if q.sub_statements and q.sub_statements[0].correct_answer:
                        ans_key_str = q.sub_statements[0].correct_answer
                    else:
                        ans_key_str = "Đáp án tự luận/ngắn"

                var_item = ExamVariantItem(
                    id=str(uuid.uuid4()),
                    variant_id=variant.id,
                    question_id=q.id,
                    section_number=sec_num,
                    question_number=variant_order_index,
                    original_question_number=item.question_number if hasattr(item, "question_number") else item.order_index,
                    option_mapping=opt_mapping if opt_mapping else None,
                    answer_key=ans_key_str
                )
                db.add(var_item)
                variant_order_index += 1

        created_variants.append(variant)

    db.commit()
    for v in created_variants:
        db.refresh(v)

    return created_variants


def get_answer_key_matrix(master_exam_id: str, db: Session) -> Dict[str, Any]:
    """Generates the comprehensive Answer Key Matrix comparing Master and all Variants."""
    master = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_exam_id).all()
    num_questions = master.total_questions

    # Build matrix table: rows = question number 1..N, columns = [Master, 101, 102, 103, ...]
    matrix_rows = []
    quick_keys: Dict[str, Dict[int, str]] = {v.variant_code: {} for v in variants}

    for q_num in range(1, num_questions + 1):
        # Find master item
        m_item = next((mi for mi in master.items if mi.order_index == q_num), None)
        sec_num = m_item.section if m_item else 1
        q_fmt = m_item.question.item_format if (m_item and m_item.question) else "SINGLE_CHOICE"

        row: Dict[str, Any] = {
            "master_question_index": q_num,
            "section": sec_num,
            "item_format": q_fmt,
        }

        for v in variants:
            v_item = next((vi for vi in v.items if vi.variant_order_index == q_num), None)
            ans = v_item.answer_key if v_item and v_item.answer_key else "-"
            row[f"variant_{v.variant_code}"] = ans
            quick_keys[v.variant_code][q_num] = ans

        matrix_rows.append(row)

    return {
        "master_exam_id": master.id,
        "master_title": master.title,
        "variant_codes": [v.variant_code for v in variants],
        "key_matrix": matrix_rows,
        "quick_keys": quick_keys,
    }
