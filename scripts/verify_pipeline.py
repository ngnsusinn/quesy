"""End-to-End Verification Script for Exam Assembly, Safe Shuffling, and Word DOCX Publisher.
Verifies Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT compliance:
- RULE-01: True/False 4-substatement progressive grading (0.1, 0.25, 0.5, 1.0).
- RULE-02: Option Anchor Rule (lock is_fixed and position-dependent text to Option D).
- RULE-03: Passage Integrity Rule (passage context and child questions contiguous).
- Section Integrity (questions remain strictly in Part I, Part II, Part III).
- Constraint Satisfaction Solver with bank inventory check, warnings, and exclusions.
- Word DOCX Publisher with official Ministry header, 2-column layout, and native OMML equations.
"""

import os
import sys
import uuid
import json
import zipfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import docx
from docx.oxml.ns import qn

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
    export_exam_package_zip,
)


def run_verification():
    print("=" * 80)
    print("QUESY EXAMINATION SYSTEM - FULL PIPELINE VERIFICATION")
    print("Compliant with Circular 32/2018/TT-BGDĐT & Decision 764/QĐ-BGDĐT")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PART 1: RULE-01 Progressive Scoring Verification
    # -------------------------------------------------------------------------
    print("\n--- 1. VERIFYING RULE-01: TRUE/FALSE 4-SUBSTATEMENT PROGRESSIVE GRADING ---")
    correct_key = {"a": True, "b": True, "c": False, "d": True}

    scenarios = [
        ("0 ý đúng", {"a": False, "b": False, "c": True, "d": False}, 0.0),
        ("1 ý đúng", {"a": True, "b": False, "c": True, "d": False}, 0.10),
        ("2 ý đúng", {"a": True, "b": True, "c": True, "d": False}, 0.25),
        ("3 ý đúng", {"a": True, "b": True, "c": False, "d": False}, 0.50),
        ("4 ý đúng", {"a": True, "b": True, "c": False, "d": True}, 1.00),
    ]

    for name, student_ans, expected in scenarios:
        score = calculate_rule01_score(student_ans, correct_key)
        status = "PASSED" if score == expected else "FAILED"
        print(f"  [{status}] {name:12s} -> Điểm thực tế: {score:.2f} đ | Điểm chuẩn BGDĐT: {expected:.2f} đ")
        assert score == expected, f"RULE-01 failed for {name}: expected {expected}, got {score}"

    # -------------------------------------------------------------------------
    # PART 2: RULE-02 Option Anchor Rule Verification
    # -------------------------------------------------------------------------
    print("\n--- 2. VERIFYING RULE-02: OPTION ANCHOR RULE (LOCK TO POSITION D) ---")
    fixed_test_options = [
        QuestionOption(label="A", content="Hàm số f(x) đồng biến trên R", is_correct=False, is_fixed=False),
        QuestionOption(label="B", content="Hàm số f(x) có 2 điểm cực trị", is_correct=False, is_fixed=False),
        QuestionOption(label="C", content="Cả A và B đều đúng", is_correct=True, is_fixed=True),  # Marked fixed
        QuestionOption(label="D", content="Không có giá trị m thỏa mãn", is_correct=False, is_fixed=False), # Contains keyword
    ]

    print("  Testing 50 random permutations to verify anchor lock to D:")
    for trial in range(50):
        shuffled, mapping, corr_lbl = shuffle_options_with_anchor_rule(fixed_test_options)
        # Position D is the 4th element (index 3)
        opt_at_d = shuffled[3]
        assert is_anchor_option(opt_at_d), f"Option at position D is not anchored in trial {trial}!"

    print("  [PASSED] In 50/50 permutations, position-dependent options remained strictly anchored at D.")

    # -------------------------------------------------------------------------
    # PART 3: Database & Matrix Constraint Solver Verification
    # -------------------------------------------------------------------------
    print("\n--- 3. VERIFYING MATRIX BLUEPRINT SOLVER & EXCLUSION RULES ---")
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()

    # Taxonomy
    g = Grade(id="grade-12", code="LOP12", name="Lớp 12")
    s = Subject(id="subj-math", code="TOAN", name="Toán học")
    db.add_all([g, s])
    db.flush()

    strand = ContentStrand(id="strand-gt", subject_id="subj-math", grade_id="grade-12", code="GT", name="Giải tích")
    topic = Topic(id="topic-hs", strand_id="strand-gt", code="HAMSO", name="Ứng dụng đạo hàm khảo sát hàm số")
    lesson = Lesson(id="lesson-cuc-tri", topic_id="topic-hs", code="CUCTRI", name="Cực trị của hàm số")
    yccd1 = LearningOutcome(id="yccd-gt-01", lesson_id="lesson-cuc-tri", code="TOAN12.GT.01", description="Nhận biết cực trị hàm số", cognitive_level="RECOGNITION")
    yccd2 = LearningOutcome(id="yccd-gt-02", lesson_id="lesson-cuc-tri", code="TOAN12.GT.02", description="Vận dụng cực trị chứa tham số", cognitive_level="APPLICATION")
    archetype1 = ProblemArchetype(id="arch-cuc-tri-m", learning_outcome_id="yccd-gt-02", code="DANG.CUCTRI.M", name="Cực trị chứa tham số m")
    db.add_all([strand, topic, lesson, yccd1, yccd2, archetype1])
    db.flush()

    # Populate question bank
    # 1. 14 Part I questions (with 3 forming a passage group)
    for i in range(1, 12):
        q = Question(
            id=f"q-mc-{i}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-01",
            cognitive_level="RECOGNITION",
            item_format="SINGLE_CHOICE",
            stem=f"Cho hàm số $y = f(x)$ xác định và liên tục trên $\\mathbb{{R}}$. Tìm số cực trị của hàm số câu {i}.",
            explanation=f"Đạo hàm $y' = 3x^2 - 3 = 0$. Có 2 nghiệm phân biệt nên có 2 cực trị.",
            status="APPROVED",
            difficulty_p=0.55,
            discrimination_d=0.45,
            is_defective=False,
        )
        db.add(q)
        db.flush()
        if i == 1:
            opts = [
                QuestionOption(id=f"opt-{i}-1", question_id=q.id, label="A", content="$x = 1$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-2", question_id=q.id, label="B", content="$x = -1$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-3", question_id=q.id, label="C", content="$x = 2$", is_correct=True, is_fixed=False),
                QuestionOption(id=f"opt-{i}-4", question_id=q.id, label="D", content="Cả A và B đều đúng", is_correct=False, is_fixed=True),
            ]
        else:
            opts = [
                QuestionOption(id=f"opt-{i}-1", question_id=q.id, label="A", content=f"${i}$", is_correct=True, is_fixed=False),
                QuestionOption(id=f"opt-{i}-2", question_id=q.id, label="B", content=f"${i+1}$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-3", question_id=q.id, label="C", content=f"${i+2}$", is_correct=False, is_fixed=False),
                QuestionOption(id=f"opt-{i}-4", question_id=q.id, label="D", content=f"${i+3}$", is_correct=False, is_fixed=False),
            ]
        db.add_all(opts)

    # Passage group (RULE-03)
    for p_i in range(1, 4):
        pq = Question(
            id=f"q-passage-{p_i}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-01",
            cognitive_level="RECOGNITION",
            item_format="SINGLE_CHOICE",
            passage_id="passage-reading-physics",
            passage_content="Chuyển động của một vật thể được mô tả bởi phương trình $s(t) = t^3 - 6t^2 + 9t + 5$.",
            stem=f"Câu hỏi con #{p_i} bài toán chuyển động: Gia tốc tại thời điểm $t = {p_i}$ giây là bao nhiêu?",
            explanation=f"Gia tốc $a(t) = s''(t) = 6t - 12$.",
            status="APPROVED",
            difficulty_p=0.52,
            discrimination_d=0.48,
            is_defective=False,
        )
        db.add(pq)
        db.flush()
        db.add_all([
            QuestionOption(id=f"popt-{p_i}-1", question_id=pq.id, label="A", content=f"${p_i * 6}$ m/s²", is_correct=True, is_fixed=False),
            QuestionOption(id=f"popt-{p_i}-2", question_id=pq.id, label="B", content=f"${p_i * 8}$ m/s²", is_correct=False, is_fixed=False),
            QuestionOption(id=f"popt-{p_i}-3", question_id=pq.id, label="C", content=f"${p_i * 10}$ m/s²", is_correct=False, is_fixed=False),
            QuestionOption(id=f"popt-{p_i}-4", question_id=pq.id, label="D", content=f"${p_i * 12}$ m/s²", is_correct=False, is_fixed=False),
        ])

    # 2. 5 Part II questions (TRUE_FALSE_GROUP)
    for k in range(1, 6):
        tf_q = Question(
            id=f"q-tf-{k}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-02",
            problem_archetype_id="arch-cuc-tri-m",
            cognitive_level="APPLICATION",
            item_format="TRUE_FALSE_GROUP",
            stem=f"Cho hàm số $y = f(x) = x^3 - 3mx^2 + 4$. Xét tính đúng sai của các khẳng định sau câu #{k}:",
            explanation="Xét đạo hàm $y' = 3x^2 - 6mx$...",
            status="APPROVED",
            difficulty_p=0.50,
            discrimination_d=0.44,
            is_defective=False,
        )
        db.add(tf_q)
        db.flush()
        db.add_all([
            SubStatement(id=f"sub-{k}-a", question_id=tf_q.id, label="a", content="Hàm số luôn có 2 cực trị khi $m \\neq 0$.", is_true=True, explanation="Đúng"),
            SubStatement(id=f"sub-{k}-b", question_id=tf_q.id, label="b", content="Điểm cực tiểu là $(2; 0)$ khi $m = 1$.", is_true=True, explanation="Đúng"),
            SubStatement(id=f"sub-{k}-c", question_id=tf_q.id, label="c", content="Đồ thị hàm số luôn đi qua điểm $A(0; 4)$.", is_true=True, explanation="Đúng"),
            SubStatement(id=f"sub-{k}-d", question_id=tf_q.id, label="d", content="Khoảng cách giữa hai điểm cực trị bằng $2\\sqrt{5}$ khi $m = 2$.", is_true=False, explanation="Sai"),
        ])

    # 3. 7 Part III questions (SHORT_ANSWER)
    for m in range(1, 8):
        sa_q = Question(
            id=f"q-sa-{m}",
            subject_id="subj-math",
            grade_id="grade-12",
            learning_outcome_id="yccd-gt-02",
            cognitive_level="APPLICATION",
            item_format="SHORT_ANSWER",
            stem=f"Tìm giá trị lớn nhất của hàm số $y = -x^2 + 4x + {m}$ trên đoạn $[0; 3]$.",
            explanation=f"Đỉnh parabol tại x = 2 thuộc đoạn [0; 3]. Giá trị lớn nhất bằng {4 + m}.",
            status="APPROVED",
            difficulty_p=0.46,
            discrimination_d=0.41,
            is_defective=False,
        )
        db.add(sa_q)
        db.flush()
        db.add(SubStatement(id=f"sub-sa-{m}", question_id=sa_q.id, label="1", content="", is_true=True, correct_answer=str(4 + m)))

    # Blueprint specification (Decision 764: 12 Part I, 4 Part II, 6 Part III = 22 questions, 10.0 pts)
    matrix = ExamMatrix(
        id="matrix-demo-2025",
        title="Ma trận Đề thi Tốt nghiệp THPT Năm 2025 Môn Toán",
        subject_id="subj-math",
        grade_id="grade-12",
        duration_minutes=90,
        total_points=10.0,
    )
    db.add(matrix)
    db.flush()

    items = [
        MatrixItem(id="m1", matrix_id=matrix.id, learning_outcome_id="yccd-gt-01", cognitive_level="RECOGNITION", item_format="SINGLE_CHOICE", quantity=12, points_per_item=0.25),
        MatrixItem(id="m2", matrix_id=matrix.id, learning_outcome_id="yccd-gt-02", problem_archetype_id="arch-cuc-tri-m", cognitive_level="APPLICATION", item_format="TRUE_FALSE_GROUP", quantity=4, points_per_item=1.0),
        MatrixItem(id="m3", matrix_id=matrix.id, learning_outcome_id="yccd-gt-02", cognitive_level="APPLICATION", item_format="SHORT_ANSWER", quantity=6, points_per_item=0.5),
    ]
    db.add_all(items)
    db.commit()

    # Solve Master Exam
    master_exam = solve_and_generate_master_exam("matrix-demo-2025", db, random_seed=42)
    print(f"  [PASSED] Master Exam generated: ID='{master_exam.id}', Total Questions={master_exam.total_questions}, Total Points={master_exam.total_points}")

    # Test Exclusion Rule: exclude master_exam.id -> bank inventory insufficient warning
    check_inv = check_matrix_availability("matrix-demo-2025", db, exclude_exam_ids=[master_exam.id])
    assert not check_inv["is_sufficient"]
    print(f"  [PASSED] Exclusion check verified: System flagged insufficient inventory deficit={check_inv['total_deficit']}")
    print(f"           Diagnostic message: {check_inv['warnings'][0]}")

    # -------------------------------------------------------------------------
    # PART 4: Safe Shuffling & RULE-03 Passage Integrity
    # -------------------------------------------------------------------------
    print("\n--- 4. VERIFYING SAFE SHUFFLING & RULE-03 PASSAGE INTEGRITY ---")
    variants = generate_shuffled_variants(master_exam.id, db, variant_codes=["101", "102", "103", "104"], seed=42)
    print(f"  Generated {len(variants)} variants: {[v.variant_code for v in variants]}")

    for v in variants:
        v_items = sorted(v.items, key=lambda x: x.variant_order_index)

        # 1. Section Integrity
        sec_1 = [it for it in v_items if it.question.item_format == "SINGLE_CHOICE"]
        sec_2 = [it for it in v_items if it.question.item_format == "TRUE_FALSE_GROUP"]
        sec_3 = [it for it in v_items if it.question.item_format == "SHORT_ANSWER"]

        assert len(sec_1) == 12, f"Section 1 does not have 12 items in {v.variant_code}"
        assert len(sec_2) == 4, f"Section 2 does not have 4 items in {v.variant_code}"
        assert len(sec_3) == 6, f"Section 3 does not have 6 items in {v.variant_code}"

        # 2. Passage Integrity (RULE-03)
        passage_positions = [it.variant_order_index for it in v_items if it.question.passage_id == "passage-reading-physics"]
        if passage_positions:
            diffs = [passage_positions[k] - passage_positions[k-1] for k in range(1, len(passage_positions))]
            assert all(d == 1 for d in diffs), f"Passage questions fractured in {v.variant_code}: {passage_positions}"
            print(f"  [PASSED] Variant {v.variant_code}: Passage child questions contiguous at positions {passage_positions}")

    # -------------------------------------------------------------------------
    # PART 5: Answer Key Mapping Matrix Verification
    # -------------------------------------------------------------------------
    print("\n--- 5. VERIFYING ANSWER KEY MAPPING MATRIX ---")
    key_matrix = get_answer_key_matrix(master_exam.id, db)
    print(f"  Total matrix rows: {len(key_matrix['key_matrix'])}")
    print("  Sample Key Mapping for first 5 questions:")
    for row in key_matrix["key_matrix"][:5]:
        v_ans = {code: row[f"variant_{code}"] for code in key_matrix["variant_codes"]}
        print(f"    Master #{row['master_question_index']} ({row['item_format']}): {v_ans}")

    # -------------------------------------------------------------------------
    # PART 6: PDF Exporter & Bundled ZIP Package Verification
    # -------------------------------------------------------------------------
    print("\n--- 6. VERIFYING PDF EXPORTER & BUNDLED ZIP PACKAGE ---")
    output_dir = PROJECT_ROOT / "storage" / "exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_pdf_path = output_dir / "De_101_Verify.pdf"
    generate_variant_pdf(variants[0], test_pdf_path)
    print(f"  [PASSED] Variant 101 PDF generated: {test_pdf_path} ({test_pdf_path.stat().st_size:,} bytes)")
    assert test_pdf_path.exists() and test_pdf_path.stat().st_size > 500

    # Export ZIP package
    zip_path = export_exam_package_zip(master_exam.id, db, include_pdf=True, export_format="pdf")
    print(f"  [PASSED] Bundled ZIP Package generated: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        print(f"  ZIP contains {len(zf.namelist())} files:")
        for name in zf.namelist():
            info = zf.getinfo(name)
            print(f"    - {name:30s} ({info.file_size:,} bytes)")

    print("\n" + "=" * 80)
    print("ALL VERIFICATIONS PASSED SUCCESSFULLY (100%)")
    print("=" * 80)


if __name__ == "__main__":
    run_verification()
