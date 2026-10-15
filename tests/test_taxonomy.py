import re
import pytest
from pydantic import ValidationError

from backend.schemas import (
    Grade,
    Subject,
    Strand,
    Topic,
    Lesson,
    LearningOutcome,
    ProblemArchetype,
    QuestionCreate,
    Question,
    CognitiveLevel,
    ItemFormat,
    Option,
    SubStatement,
)


def test_taxonomy_6_level_hierarchy():
    """Verify 6-level taxonomy hierarchy (Grade, Subject, Strand, Topic, Lesson, YCCD, ProblemArchetype)."""
    # Level 1 & 2: Grade and Subject
    grade = Grade(id="grade-12", code="12", name="Lớp 12")
    subject = Subject(id="subj-toan", code="TOAN", name="Toán học")

    # Level 3: Strand (Mạch nội dung)
    strand = Strand(
        id="strand-gt",
        grade_id=grade.id,
        subject_id=subject.id,
        code="GT",
        name="Số, Đại số và Một số yếu tố giải tích",
    )
    assert strand.grade_id == grade.id
    assert strand.subject_id == subject.id

    # Level 4: Topic (Chủ đề / Chuyên đề)
    topic = Topic(
        id="topic-uddt",
        strand_id=strand.id,
        code="UDDT",
        name="Ứng dụng đạo hàm để khảo sát hàm số",
    )
    assert topic.strand_id == strand.id

    # Level 5: Lesson (Bài học)
    lesson = Lesson(
        id="lesson-cuc-tri",
        topic_id=topic.id,
        code="B02",
        name="Tính đơn điệu và cực trị của hàm số",
    )
    assert lesson.topic_id == topic.id

    # Level 6: LearningOutcome (Yêu cầu cần đạt - YCCĐ)
    yccd = LearningOutcome(
        id="yccd-01",
        lesson_id=lesson.id,
        code="TOAN12.GT.01",
        description="Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị",
        cognitive_level=CognitiveLevel.RECOGNITION,
    )
    assert yccd.lesson_id == lesson.id
    assert yccd.code == "TOAN12.GT.01"

    # Archetype (Dạng câu hỏi con dưới YCCĐ)
    archetype = ProblemArchetype(
        id="arch-01",
        learning_outcome_id=yccd.id,
        code="D01",
        name="Đọc đồ thị hàm số tìm điểm cực trị",
        description="Dạng câu hỏi cho trước đồ thị hoặc BBT và yêu cầu xác định cực trị",
    )
    assert archetype.learning_outcome_id == yccd.id

    # Complete hierarchy traversal verification
    hierarchy = [
        grade.__class__.__name__,
        subject.__class__.__name__,
        strand.__class__.__name__,
        topic.__class__.__name__,
        lesson.__class__.__name__,
        yccd.__class__.__name__,
        archetype.__class__.__name__,
    ]
    assert hierarchy == [
        "Grade",
        "Subject",
        "Strand",
        "Topic",
        "Lesson",
        "LearningOutcome",
        "ProblemArchetype",
    ]


def test_absence_of_textbook_edition_field():
    """Verify absence of textbook edition field in models/schemas per Circular 32/2018."""
    models_to_inspect = [
        Grade,
        Subject,
        Strand,
        Topic,
        Lesson,
        LearningOutcome,
        ProblemArchetype,
        QuestionCreate,
        Question,
        Option,
        SubStatement,
    ]

    forbidden_terms = ["textbook", "textbook_edition", "sach_giao_khoa", "bo_sach", "edition"]

    for model in models_to_inspect:
        field_names = set(model.model_fields.keys())
        for term in forbidden_terms:
            for field in field_names:
                assert term not in field.lower(), (
                    f"Forbidden field '{field}' containing '{term}' found in {model.__name__}! "
                    f"Circular 32/2018 strictly forbids textbook edition taxonomy."
                )

    # Verify that passing extra textbook_edition in QuestionCreate raises ValidationError (extra forbidden)
    with pytest.raises(ValidationError):
        QuestionCreate(
            subject_id="subj-toan",
            grade_id="grade-12",
            learning_outcome_id="yccd-01",
            cognitive_level=CognitiveLevel.RECOGNITION,
            item_format=ItemFormat.SINGLE_CHOICE,
            stem="Cho hàm số y = f(x)...",
            textbook_edition="Canh Dieu",  # Disallowed extra field
        )


def test_yccd_code_format_validation():
    """Verify YCCD code format (e.g. TOAN12.GT.01, VATLI11.CO.03)."""
    valid_codes = [
        "TOAN12.GT.01",
        "VATLI11.CO.03",
        "HOA10.HH.02",
        "SINH12.DT.04",
        "TOAN10.DS.01.A",
    ]
    for code in valid_codes:
        yccd = LearningOutcome(
            id=f"id-{code}",
            lesson_id="lesson-01",
            code=code,
            description="Mô tả chuẩn YCCĐ",
            cognitive_level=CognitiveLevel.COMPREHENSION,
        )
        assert yccd.code == code

    invalid_codes = [
        "toan12.gt.01",       # Lowercase not allowed
        "TOAN12_GT_01",       # Underscore instead of dots
        "TOAN12",             # Missing dot-separated parts
        "TOAN12..01",         # Double dots
        "TOAN 12.GT.01",      # Spaces
        "123",                # No subject prefix
        "",                   # Empty string
    ]
    for invalid_code in invalid_codes:
        with pytest.raises(ValidationError):
            LearningOutcome(
                id="id-invalid",
                lesson_id="lesson-01",
                code=invalid_code,
                description="Mô tả",
                cognitive_level=CognitiveLevel.COMPREHENSION,
            )
