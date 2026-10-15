import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    JSON,
)
from sqlalchemy.orm import relationship, synonym
from backend.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# ==============================================================================
# 6-TIER TAXONOMY (VIETNAM MOET CIRCULAR 32/2018/TT-BGDĐT)
# Strictly competency-based; ABSOLUTELY NO textbook edition fields or tables.
# Subject -> Grade -> Strand -> Topic -> Lesson -> LearningOutcome -> ProblemArchetype
# ==============================================================================

class Subject(Base):
    """Tier 1: Môn học (e.g. Toán học, Vật lí, Hoá học, Sinh học...)"""
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strands = relationship("Strand", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject")


class Grade(Base):
    """Tier 2: Cấp học / Khối lớp (e.g. Lớp 10, Lớp 11, Lớp 12)"""
    __tablename__ = "grades"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strands = relationship("Strand", back_populates="grade", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="grade")


class Strand(Base):
    """Tier 3: Mạch nội dung theo TT 32
    (e.g. Số & Đại số, Hình học & Đo lường, Thống kê & Xác suất, Hoạt động thực hành)
    """
    __tablename__ = "strands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    grade_id = Column(String(36), ForeignKey("grades.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="strands")
    grade = relationship("Grade", back_populates="strands")
    topics = relationship("Topic", back_populates="strand", cascade="all, delete-orphan")


# Backward compatibility alias
ContentStrand = Strand


class Topic(Base):
    """Tier 4: Chủ đề / Chuyên đề học tập (e.g. Ứng dụng đạo hàm, Phương pháp toạ độ Oxyz...)"""
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    strand_id = Column(String(36), ForeignKey("strands.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    strand = relationship("Strand", back_populates="topics")
    lessons = relationship("Lesson", back_populates="topic", cascade="all, delete-orphan")


class Lesson(Base):
    """Tier 5: Bài học / Đơn vị kiến thức cụ thể"""
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="lessons")
    learning_outcomes = relationship("LearningOutcome", back_populates="lesson", cascade="all, delete-orphan")


class LearningOutcome(Base):
    """Tier 6: Yêu cầu Cần đạt (YCCĐ) - Chuẩn kiến thức kỹ năng theo TT 32 (e.g. TOAN12.GT.01)"""
    __tablename__ = "learning_outcomes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=False, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    competence = Column(String(255), nullable=True)  # Năng lực đặc thù theo TT 32
    cognitive_level = Column(String(50), default="RECOGNITION")  # RECOGNITION, COMPREHENSION, APPLICATION
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson = relationship("Lesson", back_populates="learning_outcomes")
    problem_archetypes = relationship("ProblemArchetype", back_populates="learning_outcome", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="learning_outcome")
    matrix_items = relationship("ExamMatrixItem", back_populates="learning_outcome")


class ProblemArchetype(Base):
    """Dạng câu hỏi / Dạng bài tập chuyên đề dưới mỗi YCCĐ nhằm chống lệch dạng khi sinh đề"""
    __tablename__ = "problem_archetypes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    learning_outcome_id = Column(String(36), ForeignKey("learning_outcomes.id"), nullable=False, index=True)
    code = Column(String(100), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    learning_outcome = relationship("LearningOutcome", back_populates="problem_archetypes")
    questions = relationship("Question", back_populates="problem_archetype")
    matrix_items = relationship("ExamMatrixItem", back_populates="problem_archetype")


# ==============================================================================
# ITEM BANK & QUESTIONS (CIRCULAR 32 & DECISION 764/QĐ-BGDĐT)
# ==============================================================================

class Question(Base):
    """Ngân hàng Câu hỏi Khảo thí chuẩn hóa.
    Item Formats: SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, PASSAGE_GROUP, ESSAY
    Cognitive Levels: RECOGNITION (Biết), COMPREHENSION (Hiểu), APPLICATION (Vận dụng)
    Statuses: DRAFT, PENDING_REVIEW, APPROVED, ARCHIVED
    """
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=True, index=True)
    grade_id = Column(String(36), ForeignKey("grades.id"), nullable=True, index=True)
    strand_id = Column(String(36), ForeignKey("strands.id"), nullable=True, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id"), nullable=True, index=True)
    lesson_id = Column(String(36), ForeignKey("lessons.id"), nullable=True, index=True)
    learning_outcome_id = Column(String(36), ForeignKey("learning_outcomes.id"), nullable=True, index=True)
    problem_archetype_id = Column(String(36), ForeignKey("problem_archetypes.id"), nullable=True, index=True)

    # Self-referencing foreign key for passage groups (reading comprehension / shared context)
    parent_id = Column(String(36), ForeignKey("questions.id"), nullable=True, index=True)
    passage_id = Column(String(100), nullable=True, index=True)
    passage_content = Column(Text, nullable=True)

    # Question stem with rich LaTeX formulas
    stem = Column(Text, nullable=False)

    # Formats: SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, PASSAGE_GROUP, ESSAY
    question_type = Column(String(50), nullable=False, default="SINGLE_CHOICE", index=True)
    item_format = synonym("question_type")

    # Cognitive levels: RECOGNITION, COMPREHENSION, APPLICATION (TT 32 verb table)
    cognitive_level = Column(String(50), nullable=False, default="RECOGNITION", index=True)

    # Detailed solution / explanation
    explanation = Column(Text, nullable=True)

    # Psychometrics: Difficulty index p (0..1), Discrimination index D (-1..1)
    difficulty_p = Column(Float, nullable=True)
    discrimination_d = Column(Float, nullable=True)
    is_defective = Column(Boolean, default=False)

    # Status: DRAFT, PENDING_REVIEW, APPROVED, ARCHIVED
    status = Column(String(50), nullable=False, default="DRAFT", index=True)

    # Embeddings for duplicate checking (pgvector JSON float list or 1536-dim vector)
    embedding_vector = Column(JSON, nullable=True)

    # Assets & Multimedia
    image_urls = Column(JSON, nullable=True)  # List of URLs to cropped WebP images

    # Short answer specific fields
    short_answer_key = Column(String(255), nullable=True)
    tolerance = Column(Float, nullable=True)  # Numerical tolerance e.g. ±0.01

    # Essay rubric (JSON criteria list)
    rubric = Column(JSON, nullable=True)

    # Source & metadata
    source_reference = Column(String(255), nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subject = relationship("Subject", back_populates="questions")
    grade = relationship("Grade", back_populates="questions")
    strand = relationship("Strand")
    topic = relationship("Topic")
    lesson = relationship("Lesson")
    learning_outcome = relationship("LearningOutcome", back_populates="questions")
    problem_archetype = relationship("ProblemArchetype", back_populates="questions")

    options = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.order_index",
    )
    sub_statements = relationship(
        "SubStatement",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="SubStatement.order_index",
    )

    parent = relationship("Question", remote_side=[id], back_populates="sub_questions")
    sub_questions = relationship("Question", back_populates="parent", cascade="all, delete-orphan")

    master_exam_items = relationship("MasterExamItem", back_populates="question")
    exam_variant_items = relationship("ExamVariantItem", back_populates="question")


class QuestionOption(Base):
    """Phương án trả lời cho SINGLE_CHOICE (A, B, C, D)"""
    __tablename__ = "question_options"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(10), nullable=False)  # A, B, C, D
    content = Column(Text, nullable=False)  # Rich LaTeX
    is_correct = Column(Boolean, default=False, nullable=False)
    is_fixed = Column(Boolean, default=False, nullable=False)  # RULE-02: Option Anchor Rule
    order_index = Column(Integer, default=0)

    # Relationship
    question = relationship("Question", back_populates="options")


class SubStatement(Base):
    """Khẳng định con cho TRUE_FALSE_GROUP (a, b, c, d theo Quyết định 764/QĐ-BGDĐT)"""
    __tablename__ = "sub_statements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(10), nullable=False)  # a, b, c, d
    content = Column(Text, nullable=False)  # Rich LaTeX
    is_true = Column(Boolean, default=False, nullable=False)
    correct_answer = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)

    # Relationship
    question = relationship("Question", back_populates="sub_statements")


# ==============================================================================
# AI DIGITIZATION JOBS (AI PARSER & HITL STUDIO)
# ==============================================================================

class AIDigitizeJob(Base):
    """Tiến trình bóc tách đề thi bằng AI Vision LLM & HITL Review"""
    __tablename__ = "ai_digitize_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # .docx, .pdf, .png, etc.
    subject_id = Column(String(36), nullable=True)
    grade_id = Column(String(36), nullable=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, PROCESSING, EXTRACTED, COMPLETED, FAILED
    confidence_score = Column(Float, default=0.0)
    extracted_json = Column(JSON, nullable=True)
    extracted_data = synonym("extracted_json")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ==============================================================================
# EXAM MATRIX & TEST BLUEPRINT BUILDER
# ==============================================================================

class ExamMatrix(Base):
    """Bản đặc tả Ma trận Đề thi theo YCCĐ (Test Blueprint)"""
    __tablename__ = "exam_matrices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=True, index=True)
    grade_id = Column(String(36), ForeignKey("grades.id"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=90)
    total_points = Column(Float, default=10.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subject = relationship("Subject")
    grade = relationship("Grade")
    items = relationship("ExamMatrixItem", back_populates="matrix", cascade="all, delete-orphan")
    master_exams = relationship("MasterExam", back_populates="matrix")


class ExamMatrixItem(Base):
    """Chi tiết từng ô chỉ tiêu trong Ma trận Đề thi"""
    __tablename__ = "exam_matrix_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    matrix_id = Column(String(36), ForeignKey("exam_matrices.id", ondelete="CASCADE"), nullable=False, index=True)
    learning_outcome_id = Column(String(36), ForeignKey("learning_outcomes.id"), nullable=True, index=True)
    problem_archetype_id = Column(String(36), ForeignKey("problem_archetypes.id"), nullable=True, index=True)
    cognitive_level = Column(String(50), nullable=False, default="RECOGNITION")  # RECOGNITION, COMPREHENSION, APPLICATION
    question_type = Column(String(50), nullable=False, default="SINGLE_CHOICE")  # SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, PASSAGE_GROUP, ESSAY
    item_format = synonym("question_type")
    quantity = Column(Integer, default=1, nullable=False)
    points_per_item = Column(Float, default=0.25, nullable=False)
    section_number = Column(Integer, default=1)  # 1: Phần I, 2: Phần II, 3: Phần III
    order_index = Column(Integer, default=0)

    # Relationships
    matrix = relationship("ExamMatrix", back_populates="items")
    learning_outcome = relationship("LearningOutcome", back_populates="matrix_items")
    problem_archetype = relationship("ProblemArchetype", back_populates="matrix_items")


# Backward compatibility alias
MatrixItem = ExamMatrixItem


# ==============================================================================
# MASTER EXAM & SHUFFLED EXAM VARIANTS
# ==============================================================================

class MasterExam(Base):
    """Đề thi Gốc sinh ra từ Ma trận (Master Blueprint Exam)"""
    __tablename__ = "master_exams"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    matrix_id = Column(String(36), ForeignKey("exam_matrices.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    subject_id = Column(String(36), ForeignKey("subjects.id"), nullable=False, index=True)
    grade_id = Column(String(36), ForeignKey("grades.id"), nullable=False, index=True)
    total_questions = Column(Integer, default=0)
    total_points = Column(Float, default=10.0)
    duration_minutes = Column(Integer, default=90)
    status = Column(String(50), default="DRAFT", index=True)  # DRAFT, GENERATED, FINALIZED, APPROVED, PUBLISHED, ARCHIVED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matrix = relationship("ExamMatrix", back_populates="master_exams")
    subject = relationship("Subject")
    grade = relationship("Grade")
    items = relationship(
        "MasterExamItem",
        back_populates="master_exam",
        cascade="all, delete-orphan",
        order_by="MasterExamItem.order_index",
    )
    variants = relationship("ExamVariant", back_populates="master_exam", cascade="all, delete-orphan")


class MasterExamItem(Base):
    """Câu hỏi thành phần trong Đề thi Gốc"""
    __tablename__ = "master_exam_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_exam_id = Column(String(36), ForeignKey("master_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    section_number = Column(Integer, default=1)  # 1: Phần I, 2: Phần II, 3: Phần III
    section = synonym("section_number")
    question_number = Column(Integer, nullable=False)  # 1, 2, 3...
    order_index = synonym("question_number")
    points = Column(Float, default=0.25)

    # Relationships
    master_exam = relationship("MasterExam", back_populates="items")
    question = relationship("Question", back_populates="master_exam_items")


class ExamVariant(Base):
    """Mã đề thi hoán vị an toàn (e.g. Mã 101, 102, 103, 104)"""
    __tablename__ = "exam_variants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_exam_id = Column(String(36), ForeignKey("master_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_code = Column(String(20), nullable=False)  # 101, 102, 103, 104
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    master_exam = relationship("MasterExam", back_populates="variants")
    items = relationship(
        "ExamVariantItem",
        back_populates="variant",
        cascade="all, delete-orphan",
        order_by="ExamVariantItem.question_number",
    )


class ExamVariantItem(Base):
    """Vị trí và ánh xạ hoán vị câu hỏi / phương án trong mã đề"""
    __tablename__ = "exam_variant_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    variant_id = Column(String(36), ForeignKey("exam_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    section_number = Column(Integer, default=1)
    section = synonym("section_number")
    question_number = Column(Integer, nullable=False)  # Vị trí câu trong đề hoán vị
    original_question_number = Column(Integer, nullable=False)  # Vị trí câu trong đề gốc
    variant_order_index = synonym("question_number")
    original_order_index = synonym("original_question_number")
    option_mapping = Column(JSON, nullable=True)  # e.g. {"A": "C", "B": "A", "C": "B", "D": "D"}
    sub_statement_mapping = Column(JSON, nullable=True)
    answer_key = Column(String(255), nullable=True)  # Đáp án chính xác của câu này trong mã đề

    # Relationships
    variant = relationship("ExamVariant", back_populates="items")
    question = relationship("Question", back_populates="exam_variant_items")

