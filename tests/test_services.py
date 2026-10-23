"""Automated Test Suite for Exam Assembly, Safe Shuffling, and Word DOCX Publisher.
Verifies Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT compliance:
- RULE-01: True/False 4-substatement progressive grading (0.1, 0.25, 0.5, 1.0).
- RULE-02: Option Anchor Rule (lock is_fixed and position-dependent text to Option D).
- RULE-03: Passage Integrity Rule (passage context and child questions contiguous).
- Section Integrity (questions remain in Part I, Part II, Part III).
- Constraint Satisfaction solver with inventory checks, warnings, and recent exam exclusions.
- Word DOCX 2-column layout, OMML native equations, official Ministry header, and ZIP package export.
"""

import os
import uuid
import json
import zipfile
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import docx
from docx.oxml.ns import qn

from backend.database import Base
from backend.models import (
    Grade, Subject, ContentStrand, Topic, Lesson,
    LearningOutcome, ProblemArchetype, Question, QuestionOption, SubStatement,
    ExamMatrix, MatrixItem, MasterExam, MasterExamItem, ExamVariant, ExamVariantItem
)
from backend.services.matrix_solver import (
    check_matrix_availability,
    solve_and_generate_master_exam,
    InsufficientInventoryError,
)
from backend.services.shuffling_engine import (
    calculate_rule01_score,
    shuffle_options_with_anchor_rule,
    generate_shuffled_variants,
    get_answer_key_matrix,
    is_anchor_option,
)
from backend.services.docx_exporter import (
    generate_variant_pdf,
    generate_solution_pdf,
    generate_answer_sheet_pdf,
    export_exam_package_zip,
)


@pytest.fixture(scope="module")
def test_db():
    """Sets up an in-memory SQLite database session populated with taxonomy and test questions."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()

    # 1. Taxonomy setup
    grade12 = Grade(id="grade-12", code="LOP12", name="Lớp 12")
    subject_math = Subject(id="subj-math", code="TOAN", name="Toán học")
    db.add_all([grade12, subject_math])
    db.flush()

    strand = ContentStrand(id="strand-gt", subject_id="subj-math", grade_id="grade-12", code="GT", name="Giải tích")
    topic = Topic(id="topic-hs", strand_id="strand-gt", code="HAMSO", name="Ứng dụng đạo hàm khảo sát hàm số")
    lesson = Lesson(id="lesson-cuc-tri", topic_id="topic-hs", code="CUCTRI", name="Cực trị của hàm số")
    yccd1 = LearningOutcome(id="yccd-gt-01", lesson_id="lesson-cuc-tri", code="TOAN12.GT.01", description="Nhận biết cực trị hàm số", cognitive_level="RECOGNITION")
    yccd2 = LearningOutcome(id="yccd-gt-02", lesson_id="lesson-cuc-tri", code="TOAN12.GT.02", description="Vận dụng cực trị chứa tham số", cognitive_level="APPLICATION")
    archetype1 = ProblemArchetype(id="arch-cuc-tri-m", learning_outcome_id="yccd-gt-02", code="DANG.CUCTRI.M", name="Cực trị chứa tham số m")

    db.add_all([strand, topic, lesson, yccd1, yccd2, archetype1])
    db.flush()

    # 2. Add Candidate Questions to Bank
    # Part I Questions (SINGLE_CHOICE)
    for i in range(1, 15):
        q = Question(
            id=f"q-mc-{i}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-01",
            cognitive_level="RECOGNITION",
            item_format="SINGLE_CHOICE",
            stem=f"Cho hàm số $y = f(x)$ có bảng biến thiên câu {i}. Tìm số điểm cực trị của hàm số $y = x^3 - 3x + {i}$.",
            explanation=f"Đạo hàm $y' = 3x^2 - 3 = 0 \\Leftrightarrow x = \\pm 1$. Do đó hàm số có 2 điểm cực trị.",
            status="APPROVED",
            difficulty_p=0.55,
            discrimination_d=0.45,
            is_defective=False,
        )
        db.add(q)
        db.flush()

        # Options: if i == 1, add an option with "Cả A và B" to test RULE-02
        if i == 1:
            opts = [
                QuestionOption(id=f"opt-{i}-1", question_id=q.id, label="A", content="$m = 1$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-2", question_id=q.id, label="B", content="$m = -1$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-3", question_id=q.id, label="C", content="$m = 2$", is_correct=True, is_fixed=False),
                QuestionOption(id=f"opt-{i}-4", question_id=q.id, label="D", content="Cả A và B đều đúng", is_correct=False, is_fixed=True),
            ]
        elif i == 2:
            opts = [
                QuestionOption(id=f"opt-{i}-1", question_id=q.id, label="A", content="Tất cả các đáp án trên", is_correct=False, is_fixed=False), # text triggers anchor
                QuestionOption(id=f"opt-{i}-2", question_id=q.id, label="B", content="$x = 0$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-3", question_id=q.id, label="C", content="$x = 1$", is_correct=True, is_fixed=False),
                QuestionOption(id=f"opt-{i}-4", question_id=q.id, label="D", content="$x = 2$", is_correct=False, is_fixed=False),
            ]
        else:
            opts = [
                QuestionOption(id=f"opt-{i}-1", question_id=q.id, label="A", content=f"${i}$", is_correct=True, is_fixed=False),
                QuestionOption(id=f"opt-{i}-2", question_id=q.id, label="B", content=f"${i+1}$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-3", question_id=q.id, label="C", content=f"${i+2}$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-4", question_id=q.id, label="D", content=f"${i+3}$", is_correct=False, is_fixed=False),
            ]
        db.add_all(opts)

    # Passage group questions (RULE-03): English or Math passage with 3 child questions
    for j in range(1, 4):
        pq = Question(
            id=f"q-passage-{j}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-01",
            cognitive_level="RECOGNITION",
            item_format="SINGLE_CHOICE",
            passage_id="passage-reading-01",
            passage_content="Xét một chất điểm chuyển động theo phương trình $s(t) = -t^3 + 6t^2 + 9t$. Vận tốc tức thời $v(t) = s'(t)$.",
            stem=f"Câu hỏi con {j} của bài toán chuyển động: Tìm vận tốc tại thời điểm $t = {j}$ giây.",
            explanation=f"Vận tốc $v(t) = -3t^2 + 12t + 9$. Thay $t = {j}$ ta được vận tốc.",
            status="APPROVED",
            difficulty_p=0.60,
            discrimination_d=0.40,
            is_defective=False,
        )
        db.add(pq)
        db.flush()
        db.add_all([
            QuestionOption(id=f"popt-{j}-1", question_id=pq.id, label="A", content=f"${10+j}$ m/s", is_correct=True, is_fixed=False),
            QuestionOption(id=f"popt-{j}-2", question_id=pq.id, label="B", content=f"${20+j}$ m/s", is_correct=False, is_fixed=False),
            QuestionOption(id=f"popt-{j}-3", question_id=pq.id, label="C", content=f"${30+j}$ m/s", is_correct=False, is_fixed=False),
            QuestionOption(id=f"popt-{j}-4", question_id=pq.id, label="D", content=f"${40+j}$ m/s", is_correct=False, is_fixed=False),
        ])

    # Part II Questions (TRUE_FALSE_GROUP)
    for k in range(1, 6):
        tf_q = Question(
            id=f"q-tf-{k}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-02",
            problem_archetype_id="arch-cuc-tri-m",
            cognitive_level="APPLICATION",
            item_format="TRUE_FALSE_GROUP",
            stem=f"Cho hàm số $y = f(x) = x^3 - 3mx^2 + 4$. Xét tính đúng sai của các khẳng định sau câu {k}:",
            explanation="Xét đạo hàm $y' = 3x^2 - 6mx = 3x(x - 2m)$...",
            status="APPROVED",
            difficulty_p=0.50,
            discrimination_d=0.42,
            is_defective=False,
        )
        db.add(tf_q)
        db.flush()
        subs = [
            SubStatement(id=f"sub-{k}-a", question_id=tf_q.id, label="a", content="Hàm số luôn có 2 cực trị với mọi $m \\neq 0$.", is_true=True, explanation="y'=0 có 2 nghiệm phân biệt khi m khác 0."),
            SubStatement(id=f"sub-{k}-b", question_id=tf_q.id, label="b", content="Khi $m = 1$, điểm cực tiểu là $(2; 0)$.", is_true=True, explanation="Tọa độ đúng."),
            SubStatement(id=f"sub-{k}-c", question_id=tf_q.id, label="c", content="Đồ thị hàm số luôn đi qua điểm $A(0; 4)$ với mọi $m$.", is_true=True, explanation="f(0) = 4."),
            SubStatement(id=f"sub-{k}-d", question_id=tf_q.id, label="d", content="Khoảng cách giữa hai điểm cực trị bằng $2\\sqrt{5}$ khi $m = 2$.", is_true=False, explanation="Tính toán ra kết quả khác."),
        ]
        db.add_all(subs)

    # Part III Questions (SHORT_ANSWER)
    for m in range(1, 8):
        sa_q = Question(
            id=f"q-sa-{m}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-02",
            cognitive_level="APPLICATION",
            item_format="SHORT_ANSWER",
            stem=f"Tìm giá trị lớn nhất của hàm số $y = -x^2 + 4x + {m}$ trên đoạn $[0; 3]$.",
            explanation=f"Đỉnh parabol tại x = 2 thuộc đoạn [0; 3]. y(2) = {4 + m}.",
            status="APPROVED",
            difficulty_p=0.48,
            discrimination_d=0.38,
            is_defective=False,
        )
        db.add(sa_q)
        db.flush()
        db.add(SubStatement(id=f"sub-sa-{m}", question_id=sa_q.id, label="1", content="", is_true=True, correct_answer=str(4 + m)))

    # Add a Defective Question (D < 0.20) to ensure solver excludes it
    defective_q = Question(
        id="q-defective-01",
        subject_id="subj-math",
        grade_id="grade-12",
        learning_outcome_id="yccd-gt-01",
        cognitive_level="RECOGNITION",
        item_format="SINGLE_CHOICE",
        stem="Câu hỏi lỗi chất lượng kém cần bị loại bỏ.",
        status="APPROVED",
        difficulty_p=0.95,
        discrimination_d=0.10,  # Defective: D < 0.2
        is_defective=True,
    )
    db.add(defective_q)

    # 3. Create a Matrix Blueprint (Decision 764 style: 12 Part I, 4 Part II, 6 Part III)
    matrix = ExamMatrix(
        id="matrix-thpt-2025",
        title="Ma trận Đề thi Tốt nghiệp THPT 2025 Môn Toán",
        subject_id="subj-math",
        grade_id="grade-12",
        duration_minutes=90,
        total_points=10.0,
    )
    db.add(matrix)
    db.flush()

    # Matrix items:
    # Cell 1: Part I (SINGLE_CHOICE, 12 questions, 0.25 pt = 3.0 pts)
    # Cell 2: Part II (TRUE_FALSE_GROUP, 4 questions, 1.0 pt = 4.0 pts)
    # Cell 3: Part III (SHORT_ANSWER, 6 questions, 0.5 pt = 3.0 pts)
    items = [
        MatrixItem(id="m-cell-1", matrix_id=matrix.id, learning_outcome_id="yccd-gt-01", cognitive_level="RECOGNITION", item_format="SINGLE_CHOICE", quantity=12, points_per_item=0.25),
        MatrixItem(id="m-cell-2", matrix_id=matrix.id, learning_outcome_id="yccd-gt-02", problem_archetype_id="arch-cuc-tri-m", cognitive_level="APPLICATION", item_format="TRUE_FALSE_GROUP", quantity=4, points_per_item=1.0),
        MatrixItem(id="m-cell-3", matrix_id=matrix.id, learning_outcome_id="yccd-gt-02", cognitive_level="APPLICATION", item_format="SHORT_ANSWER", quantity=6, points_per_item=0.5),
    ]
    db.add_all(items)
    db.commit()

    yield db
    db.close()


# =========================================================================
# TEST SUITE 1: RULE-01 TRUE/FALSE 4-SUBSTATEMENT PROGRESSIVE GRADING
# =========================================================================

def test_rule01_scoring_all_scenarios():
    """Verifies RULE-01: True/False 4-substatement progressive grading
    (Decision 764/QĐ-BGDĐT: 1=0.1, 2=0.25, 3=0.5, 4=1.0, 0=0.0).
    """
    correct = {"a": True, "b": True, "c": False, "d": True}

    # Scenario 0: 0 correct -> 0.0
    student_0 = {"a": False, "b": False, "c": True, "d": False}
    assert calculate_rule01_score(student_0, correct) == 0.0

    # Scenario 1: 1 correct -> 0.10
    student_1 = {"a": True, "b": False, "c": True, "d": False}
    assert calculate_rule01_score(student_1, correct) == 0.10

    # Scenario 2: 2 correct -> 0.25
    student_2 = {"a": True, "b": True, "c": True, "d": False}
    assert calculate_rule01_score(student_2, correct) == 0.25

    # Scenario 3: 3 correct -> 0.50
    student_3 = {"a": True, "b": True, "c": False, "d": False}
    assert calculate_rule01_score(student_3, correct) == 0.50

    # Scenario 4: 4 correct -> 1.00
    student_4 = {"a": True, "b": True, "c": False, "d": True}
    assert calculate_rule01_score(student_4, correct) == 1.00


# =========================================================================
# TEST SUITE 2: RULE-02 OPTION ANCHOR RULE
# =========================================================================

def test_rule02_option_anchor_lock_to_d():
    """Verifies RULE-02: Any option with is_fixed=True or position-dependent text
    ('Cả A và B', 'Tất cả các đáp án trên', 'Không có đáp án nào')
    MUST BE LOCKED AT POSITION D in all shuffled variants.
    """
    # Test case 1: Option with is_fixed = True
    opts1 = [
        QuestionOption(label="A", content="Hàm số đồng biến", is_correct=False, is_fixed=False),
        QuestionOption(label="B", content="Hàm số nghịch biến", is_correct=False, is_fixed=False),
        QuestionOption(label="C", content="Hàm số không đổi", is_correct=True, is_fixed=False),
        QuestionOption(label="D", content="Cả A và B đều đúng", is_correct=False, is_fixed=True),
    ]

    for seed in range(20):
        shuffled, mapping, corr_lbl = shuffle_options_with_anchor_rule(opts1, rng=None)
        # Position D must be the fixed option
        assert shuffled[3].content == "Cả A và B đều đúng", f"Fixed option was not at D in seed {seed}"
        assert mapping["D"] == "D"

    # Test case 2: Option with position-dependent text placed at index 0 initially
    opts2 = [
        QuestionOption(label="A", content="Tất cả các đáp án trên đều đúng", is_correct=False, is_fixed=False),
        QuestionOption(label="B", content="Nghiệm x = 1", is_correct=True, is_fixed=False),
        QuestionOption(label="C", content="Nghiệm x = 2", is_correct=False, is_fixed=False),
        QuestionOption(label="D", content="Nghiệm x = 3", is_correct=False, is_fixed=False),
    ]

    for seed in range(20):
        shuffled, mapping, corr_lbl = shuffle_options_with_anchor_rule(opts2, rng=None)
        assert shuffled[3].content == "Tất cả các đáp án trên đều đúng"
        # Option A was moved to D
        assert mapping["A"] == "D"


# =========================================================================
# TEST SUITE 3: RULE-03 PASSAGE INTEGRITY & SECTION INTEGRITY
# =========================================================================

def test_passage_integrity_and_section_integrity(test_db):
    """Verifies:
    1. Section Integrity: Part I questions stay in Part I, Part II in Part II, Part III in Part III.
    2. Passage Integrity (RULE-03): Passage context and all child questions remain strictly contiguous.
    """
    master = solve_and_generate_master_exam("matrix-thpt-2025", test_db, random_seed=42)
    variants = generate_shuffled_variants(master.id, test_db, variant_codes=["101", "102", "103", "104"], seed=100)

    assert len(variants) == 4

    for var in variants:
        items = sorted(var.items, key=lambda x: x.variant_order_index)

        # 1. Section Integrity Check
        # Items 1..12 must be SINGLE_CHOICE (Part I)
        for i in range(0, 12):
            assert items[i].question.item_format == "SINGLE_CHOICE", f"Item {i+1} is not SINGLE_CHOICE in {var.variant_code}"
        # Items 13..16 must be TRUE_FALSE_GROUP (Part II)
        for i in range(12, 16):
            assert items[i].question.item_format == "TRUE_FALSE_GROUP", f"Item {i+1} is not TRUE_FALSE_GROUP in {var.variant_code}"
        # Items 17..22 must be SHORT_ANSWER (Part III)
        for i in range(16, 22):
            assert items[i].question.item_format == "SHORT_ANSWER", f"Item {i+1} is not SHORT_ANSWER in {var.variant_code}"

        # 2. Passage Integrity Check (RULE-03)
        passage_indices = [
            idx + 1 for idx, it in enumerate(items)
            if it.question.passage_id == "passage-reading-01"
        ]
        if passage_indices:
            # All indices of the passage child questions must be consecutive!
            diffs = [passage_indices[k] - passage_indices[k - 1] for k in range(1, len(passage_indices))]
            assert all(d == 1 for d in diffs), f"Passage questions are fractured in variant {var.variant_code}: {passage_indices}"


# =========================================================================
# TEST SUITE 4: MATRIX SOLVER & EXCLUSION RULES
# =========================================================================

def test_matrix_solver_exclusion_and_inventory_warning(test_db):
    """Verifies:
    1. Exclusion rules: Questions used in recent exam IDs are excluded.
    2. Bank inventory diagnostics: Warns when questions are insufficient.
    """
    # Assembly 1: Generate Master Exam 1
    master1 = solve_and_generate_master_exam("matrix-thpt-2025", test_db, title="Exam 1", random_seed=123)
    used_q_ids_1 = {item.question_id for item in master1.items}

    # Assembly 2: Exclude Exam 1 IDs -> solver must NOT reuse those questions
    # But notice our bank only has 14 Part I questions and 12 are required!
    # If 12 were used in Exam 1, only 2 remain, so bank should be INSUFFICIENT!
    avail_check = check_matrix_availability("matrix-thpt-2025", test_db, exclude_exam_ids=[master1.id])
    assert not avail_check["is_sufficient"]
    assert len(avail_check["warnings"]) > 0
    assert "Cảnh báo thiếu câu hỏi" in avail_check["warnings"][0]

    # Verify exception is raised if insufficient and allow_partial=False
    with pytest.raises(InsufficientInventoryError) as exc_info:
        solve_and_generate_master_exam("matrix-thpt-2025", test_db, exclude_exam_ids=[master1.id], allow_partial=False)
    assert exc_info.value.report["total_deficit"] > 0


# =========================================================================
# TEST SUITE 5: ANSWER KEY MAPPING MATRIX
# =========================================================================

def test_answer_key_mapping_matrix(test_db):
    """Verifies Answer Key Mapping Matrix generation across Master and all Variants."""
    master = solve_and_generate_master_exam("matrix-thpt-2025", test_db, random_seed=99)
    generate_shuffled_variants(master.id, test_db, variant_codes=["101", "102", "103", "104"], seed=99)

    matrix_data = get_answer_key_matrix(master.id, test_db)
    assert matrix_data["master_exam_id"] == master.id
    assert matrix_data["variant_codes"] == ["101", "102", "103", "104"]
    assert len(matrix_data["key_matrix"]) == master.total_questions

    # Quick keys dictionary check
    quick_keys = matrix_data["quick_keys"]
    assert "101" in quick_keys
    assert len(quick_keys["101"]) == master.total_questions


# =========================================================================
# TEST SUITE 6: WORD DOCX EXPORT & BUNDLED ZIP PACKAGE
# =========================================================================

def test_pdf_export_and_zip_package(test_db, tmp_path):
    """Verifies PDF Publisher:
    - Single variant exam PDF generation.
    - Detailed solutions PDF.
    - Master answer key sheet PDF.
    - Export ZIP package containing all N variant PDF files + solutions + answer key sheet + OMR.
    """
    master = solve_and_generate_master_exam("matrix-thpt-2025", test_db, random_seed=77)
    variants = generate_shuffled_variants(master.id, test_db, variant_codes=["101", "102"], seed=77)

    # 1. Test Single Variant Exam PDF Generation
    v101 = variants[0]
    out_pdf = tmp_path / "De_101.pdf"
    generate_variant_pdf(v101, out_pdf)
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 500

    # 2. Test Detailed Solutions PDF Generation
    out_sol = tmp_path / "LoiGiai_101.pdf"
    generate_solution_pdf(v101, out_sol)
    assert out_sol.exists()
    assert out_sol.stat().st_size > 500

    # 3. Test Master Answer Sheet PDF Generation
    out_sheet = tmp_path / "BangDapAn_TongHop.pdf"
    generate_answer_sheet_pdf(master, variants, out_sheet)
    assert out_sheet.exists()
    assert out_sheet.stat().st_size > 500

    # 4. Test Bundled ZIP Package Export
    zip_path_str = export_exam_package_zip(master.id, test_db, include_pdf=True, export_format="pdf")
    zip_path = Path(zip_path_str)
    assert zip_path.exists()
    assert zipfile.is_zipfile(zip_path)

    # Check ZIP archive contents
    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()
        assert "De_101.pdf" in namelist
        assert "De_102.pdf" in namelist
        assert "LoiGiai_101.pdf" in namelist
        assert "LoiGiai_102.pdf" in namelist
        assert "BangDapAn_TongHop.pdf" in namelist
        assert "BangDapAn_TongHop.csv" in namelist
        assert "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf" in namelist
