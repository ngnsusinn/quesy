import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==============================================================================
# ENUMS (CIRCULAR 32/2018/TT-BGDĐT & DECISION 764/QĐ-BGDĐT)
# ==============================================================================

class CognitiveLevel(str, Enum):
    RECOGNITION = "RECOGNITION"             # Nhận biết
    COMPREHENSION = "COMPREHENSION"         # Thông hiểu
    APPLICATION = "APPLICATION"             # Vận dụng
    HIGH_APPLICATION = "HIGH_APPLICATION"   # Vận dụng cao


class ItemFormat(str, Enum):
    SINGLE_CHOICE = "SINGLE_CHOICE"        # Phần I: Trắc nghiệm 4 lựa chọn (A, B, C, D)
    TRUE_FALSE_GROUP = "TRUE_FALSE_GROUP"  # Phần II: Trắc nghiệm Đúng/Sai 4 ý (a, b, c, d)
    SHORT_ANSWER = "SHORT_ANSWER"          # Phần III: Trắc nghiệm trả lời ngắn
    PASSAGE_GROUP = "PASSAGE_GROUP"        # Câu hỏi chùm (ngữ liệu chung)
    ESSAY = "ESSAY"                        # Tự luận kèm rubric


# Alias for QuestionType
QuestionType = ItemFormat


class QuestionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    ARCHIVED = "ARCHIVED"
    REJECTED = "REJECTED"


class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExamStatus(str, Enum):
    DRAFT = "DRAFT"
    GENERATED = "GENERATED"
    FINALIZED = "FINALIZED"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


# Base model strictly forbidding any extra fields (including textbook editions)
class BaseModelNoTextbook(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, populate_by_name=True)


# ==============================================================================
# 6-Level Taxonomy Hierarchy according to Circular 32/2018
# ==============================================================================

class Grade(BaseModelNoTextbook):
    id: str
    code: str
    name: str
    level: Optional[int] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class GradeCreate(BaseModelNoTextbook):
    code: str
    name: str
    level: Optional[int] = None
    order_index: int = 0


class GradeUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    level: Optional[int] = None
    order_index: Optional[int] = None


class Subject(BaseModelNoTextbook):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class SubjectCreate(BaseModelNoTextbook):
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class SubjectUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class Strand(BaseModelNoTextbook):
    id: str
    grade_id: str
    subject_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class StrandCreate(BaseModelNoTextbook):
    grade_id: str
    subject_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class StrandUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class Topic(BaseModelNoTextbook):
    id: str
    strand_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class TopicCreate(BaseModelNoTextbook):
    strand_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class TopicUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class Lesson(BaseModelNoTextbook):
    id: str
    topic_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class LessonCreate(BaseModelNoTextbook):
    topic_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class LessonUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


YCCD_REGEX = re.compile(r"^[A-Z0-9]+(\.[A-Z0-9]+)+$")


class LearningOutcome(BaseModelNoTextbook):
    """Yêu cầu cần đạt (YCCĐ) theo Thông tư 32/2018/TT-BGDĐT."""
    id: str
    lesson_id: str
    code: str
    name: Optional[str] = None
    description: str
    competence: Optional[str] = None
    cognitive_level: CognitiveLevel = CognitiveLevel.RECOGNITION
    order_index: int = 0
    created_at: Optional[datetime] = None

    @field_validator("code")
    @classmethod
    def validate_yccd_code(cls, value: str) -> str:
        if not YCCD_REGEX.match(value):
            raise ValueError(
                f"Invalid YCCD code format '{value}'. Expected uppercase dot-separated format (e.g. TOAN12.GT.01)."
            )
        return value


class LearningOutcomeCreate(BaseModelNoTextbook):
    lesson_id: str
    code: str
    name: Optional[str] = None
    description: str
    competence: Optional[str] = None
    cognitive_level: CognitiveLevel = CognitiveLevel.RECOGNITION
    order_index: int = 0

    @field_validator("code")
    @classmethod
    def validate_yccd_code(cls, value: str) -> str:
        if not YCCD_REGEX.match(value):
            raise ValueError(
                f"Invalid YCCD code format '{value}'. Expected uppercase dot-separated format (e.g. TOAN12.GT.01)."
            )
        return value


class LearningOutcomeUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    competence: Optional[str] = None
    cognitive_level: Optional[CognitiveLevel] = None
    order_index: Optional[int] = None


class ProblemArchetype(BaseModelNoTextbook):
    """Dạng câu hỏi con thuộc YCCĐ."""
    id: str
    learning_outcome_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None


class ProblemArchetypeCreate(BaseModelNoTextbook):
    learning_outcome_id: str
    code: str
    name: str
    description: Optional[str] = None
    order_index: int = 0


class ProblemArchetypeUpdate(BaseModelNoTextbook):
    name: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


# --- Detailed Nested Taxonomy Views ---
class LearningOutcomeWithArchetypes(LearningOutcome):
    problem_archetypes: List[ProblemArchetype] = []


class LessonDetailResponse(Lesson):
    learning_outcomes: List[LearningOutcomeWithArchetypes] = []


class TopicDetailResponse(Topic):
    lessons: List[LessonDetailResponse] = []


class StrandDetailResponse(Strand):
    topics: List[TopicDetailResponse] = []


# ==============================================================================
# Question Models & Components
# ==============================================================================

class Option(BaseModelNoTextbook):
    id: Optional[str] = None
    question_id: Optional[str] = None
    label: str
    content: str
    is_correct: bool = False
    is_fixed: bool = False
    order_index: int = 0


QuestionOption = Option
QuestionOptionResponse = Option


class SubStatement(BaseModelNoTextbook):
    id: Optional[str] = None
    question_id: Optional[str] = None
    label: str
    content: str
    is_true: bool = False
    explanation: Optional[str] = None
    order_index: int = 0


SubStatementResponse = SubStatement


class QuestionCreate(BaseModelNoTextbook):
    stem: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    strand_id: Optional[str] = None
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    parent_id: Optional[str] = None
    cognitive_level: CognitiveLevel = CognitiveLevel.RECOGNITION
    item_format: ItemFormat = ItemFormat.SINGLE_CHOICE
    question_type: Optional[QuestionType] = None
    options: Optional[List[Option]] = None
    sub_statements: Optional[List[SubStatement]] = None
    short_answer_solution: Optional[str] = None
    short_answer_key: Optional[str] = None
    tolerance: Optional[float] = None
    passage_id: Optional[str] = None
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    image_urls: Optional[List[str]] = None
    embedding: Optional[List[float]] = None
    embedding_vector: Optional[List[float]] = None
    rubric: Optional[Dict[str, Any]] = None
    difficulty_p: Optional[float] = None
    discrimination_d: Optional[float] = None
    status: QuestionStatus = QuestionStatus.DRAFT
    order_index: int = 0


class Question(QuestionCreate):
    id: str
    is_defective: bool = False
    options: Optional[List[Option]] = Field(default_factory=list)
    sub_statements: Optional[List[SubStatement]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


QuestionResponse = Question


class QuestionDetailResponse(Question):
    learning_outcome: Optional[LearningOutcome] = None
    problem_archetype: Optional[ProblemArchetype] = None
    sub_questions: List[Question] = []


class QuestionUpdate(BaseModelNoTextbook):
    stem: Optional[str] = None
    cognitive_level: Optional[CognitiveLevel] = None
    item_format: Optional[ItemFormat] = None
    question_type: Optional[QuestionType] = None
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    strand_id: Optional[str] = None
    topic_id: Optional[str] = None
    lesson_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    parent_id: Optional[str] = None
    options: Optional[List[Option]] = None
    sub_statements: Optional[List[SubStatement]] = None
    short_answer_solution: Optional[str] = None
    short_answer_key: Optional[str] = None
    tolerance: Optional[float] = None
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    image_urls: Optional[List[str]] = None
    difficulty_p: Optional[float] = None
    discrimination_d: Optional[float] = None
    status: Optional[QuestionStatus] = None
    embedding: Optional[List[float]] = None
    embedding_vector: Optional[List[float]] = None


# ==============================================================================
# Matrix and Shuffling Schemas
# ==============================================================================

class ExamMatrixItem(BaseModelNoTextbook):
    id: Optional[str] = None
    matrix_id: Optional[str] = None
    learning_outcome_id: Optional[str] = None
    problem_archetype_id: Optional[str] = None
    cognitive_level: CognitiveLevel = CognitiveLevel.RECOGNITION
    item_format: ItemFormat = ItemFormat.SINGLE_CHOICE
    question_type: Optional[QuestionType] = None
    question_count: int = 1
    quantity: Optional[int] = None
    points_per_question: float = 0.25
    points_per_item: Optional[float] = None
    section_number: int = 1
    order_index: int = 0
    learning_outcome: Optional[LearningOutcome] = None
    problem_archetype: Optional[ProblemArchetype] = None


ExamMatrixItemResponse = ExamMatrixItem


class ExamMatrixCreate(BaseModelNoTextbook):
    title: str
    grade_id: str
    subject_id: str
    duration_minutes: int = 90
    total_points: float = 10.0
    description: Optional[str] = None
    items: List[ExamMatrixItem] = []


class ExamMatrixUpdate(BaseModelNoTextbook):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    total_points: Optional[float] = None
    items: Optional[List[ExamMatrixItem]] = None


class ExamMatrix(ExamMatrixCreate):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


ExamMatrixResponse = ExamMatrix


# ==============================================================================
# Master Exam & Variants Schemas
# ==============================================================================

class MasterExamItem(BaseModelNoTextbook):
    id: Optional[str] = None
    master_exam_id: Optional[str] = None
    question_id: str
    section_number: int = 1
    question_number: int
    points: float = 0.25
    question: Optional[Question] = None


MasterExamItemResponse = MasterExamItem


class MasterExam(BaseModelNoTextbook):
    id: str
    title: str
    subject_id: str
    grade_id: str
    matrix_id: Optional[str] = None
    total_questions: int = 0
    total_points: float = 10.0
    duration_minutes: int = 90
    status: ExamStatus = ExamStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[MasterExamItem] = []


MasterExamResponse = MasterExam


class MasterExamCreate(BaseModelNoTextbook):
    title: str
    subject_id: str
    grade_id: str
    matrix_id: Optional[str] = None
    duration_minutes: int = 90
    total_points: float = 10.0
    items: List[MasterExamItem] = []


class VariantItem(BaseModelNoTextbook):
    question_id: str
    stem: str
    item_format: ItemFormat
    passage_id: Optional[str] = None
    options: Optional[List[Option]] = None
    sub_statements: Optional[List[SubStatement]] = None
    position: int


class VariantOutput(BaseModelNoTextbook):
    variant_code: str
    questions: List[VariantItem]
    answer_keys: Dict[str, Any]


class ExamVariantItem(BaseModelNoTextbook):
    id: Optional[str] = None
    variant_id: Optional[str] = None
    question_id: str
    section_number: int = 1
    question_number: int
    original_question_number: int
    option_mapping: Optional[Dict[str, str]] = None
    sub_statement_mapping: Optional[Dict[str, str]] = None
    answer_key: Optional[str] = None
    question: Optional[Question] = None


ExamVariantItemResponse = ExamVariantItem


class ExamVariant(BaseModelNoTextbook):
    id: str
    master_exam_id: str
    variant_code: str
    created_at: Optional[datetime] = None
    items: List[ExamVariantItem] = []


ExamVariantResponse = ExamVariant


class ExamShuffleRequest(BaseModelNoTextbook):
    title: Optional[str] = None
    master_exam_id: Optional[str] = None
    questions: Optional[List[Question]] = None
    num_variants: int = 4
    variant_codes: Optional[List[str]] = None


class ExamShuffleResponse(BaseModelNoTextbook):
    exam_id: str
    title: str
    variants: List[VariantOutput]


# ==============================================================================
# AI Digitize Job Schemas
# ==============================================================================

class AIDigitizeJobCreate(BaseModelNoTextbook):
    filename: Optional[str] = None
    file_path: str
    file_type: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None


class AIDigitizeJobUpdate(BaseModelNoTextbook):
    status: Optional[JobStatus] = None
    confidence_score: Optional[float] = None
    extracted_json: Optional[Any] = None
    error_message: Optional[str] = None


class AIDigitizeJobResponse(BaseModelNoTextbook):
    id: str
    filename: Optional[str] = None
    file_path: str
    file_type: str
    subject_id: Optional[str] = None
    grade_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    confidence_score: float = 0.0
    extracted_json: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UploadResponse(BaseModelNoTextbook):
    job_id: str
    filename: str
    status: str
    questions_count: int
    message: str


# ==============================================================================
# Stepwise Scoring Rule for True/False Questions (Decision 764/QĐ-BGDĐT)
# ==============================================================================

class TrueFalseScoreCalcRequest(BaseModelNoTextbook):
    correct_count: int = Field(..., ge=0, le=4)
    max_points: float = 1.0


class TrueFalseScoreCalcResponse(BaseModelNoTextbook):
    correct_count: int
    score: float
    percentage: float
    formula_note: str = (
        "Đúng 1 ý: 0.1đ (10%); Đúng 2 ý: 0.25đ (25%); Đúng 3 ý: 0.5đ (50%); Đúng cả 4 ý: 1.0đ (100%)"
    )

