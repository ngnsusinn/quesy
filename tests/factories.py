import uuid
from typing import Dict, Any, List, Optional
from backend.models import (
    Grade, Subject, ContentStrand, Topic, Lesson, LearningOutcome,
    ProblemArchetype, Question, QuestionOption, SubStatement,
    ExamMatrix, ExamMatrixItem
)

def create_grade_data(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"grade_{uid}",
        "code": f"GRADE_{uid.upper()}",
        "name": f"Khối Lớp {uid}",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_subject_data(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"sub_{uid}",
        "code": f"SUB_{uid.upper()}",
        "name": f"Môn học {uid}",
        "description": "Môn học kiểm thử chuẩn hóa TT 32",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_strand_data(subject_id: str, grade_id: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"strand_{uid}",
        "subject_id": subject_id,
        "grade_id": grade_id,
        "code": f"STRAND_{uid.upper()}",
        "name": f"Mạch nội dung {uid}",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_topic_data(strand_id: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"topic_{uid}",
        "strand_id": strand_id,
        "code": f"TOPIC_{uid.upper()}",
        "name": f"Chủ đề {uid}",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_lesson_data(topic_id: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"lesson_{uid}",
        "topic_id": topic_id,
        "code": f"LESSON_{uid.upper()}",
        "name": f"Bài học {uid}",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_yccd_data(lesson_id: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"yccd_{uid}",
        "lesson_id": lesson_id,
        "code": f"TOAN12.TEST.{uid[:4].upper()}",
        "name": f"Yêu cầu cần đạt {uid}",
        "description": "Nhận biết và vận dụng kiến thức chuẩn hóa theo Thông tư 32/2018",
        "cognitive_level": "RECOGNITION",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_archetype_data(learning_outcome_id: str, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "id": f"arch_{uid}",
        "learning_outcome_id": learning_outcome_id,
        "code": f"ARCH_{uid.upper()}",
        "name": f"Dạng bài tập {uid}",
        "description": "Dạng câu hỏi chuyên đề khảo sát",
        "order_index": 1
    }
    if overrides:
        data.update(overrides)
    return data

def create_question_payload(yccd_id: str, archetype_id: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "learning_outcome_id": yccd_id,
        "problem_archetype_id": archetype_id,
        "item_format": "SINGLE_CHOICE",
        "cognitive_level": "RECOGNITION",
        "stem": f"Cho hàm số $y = f(x)$ có đạo hàm $f'(x) = x^2 - {uid[:2]}$. Tìm nghiệm phương trình?",
        "options": [
            {"label": "A", "content": f"$x = {uid[:2]}$", "is_correct": True, "is_fixed": False, "order_index": 1},
            {"label": "B", "content": f"$x = -{uid[:2]}$", "is_correct": False, "is_fixed": False, "order_index": 2},
            {"label": "C", "content": "$x = 0$", "is_correct": False, "is_fixed": False, "order_index": 3},
            {"label": "D", "content": "Tất cả các đáp án trên đều sai", "is_correct": False, "is_fixed": True, "order_index": 4}
        ],
        "explanation": "Lời giải chi tiết: xét dấu đạo hàm...",
        "source_reference": "Đề khảo sát năng lực 2026"
    }
    if overrides:
        data.update(overrides)
    return data

def create_true_false_question_payload(yccd_id: str, archetype_id: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    uid = str(uuid.uuid4())[:8]
    data = {
        "learning_outcome_id": yccd_id,
        "problem_archetype_id": archetype_id,
        "item_format": "TRUE_FALSE_GROUP",
        "cognitive_level": "COMPREHENSION",
        "stem": f"Cho hàm số $y = x^3 - 3x + {uid[:2]}$ xác định trên $\\mathbb{{R}}$.",
        "sub_statements": [
            {"label": "a", "content": "Hàm số đồng biến trên khoảng $(1; +\\infty)$.", "is_true": True, "explanation": "Đạo hàm dương."},
            {"label": "b", "content": "Hàm số đạt cực đại tại $x = -1$.", "is_true": True, "explanation": "Đạo hàm đổi dấu từ dương sang âm."},
            {"label": "c", "content": "Giá trị nhỏ nhất của hàm số trên toàn bộ $\\mathbb{R}$ bằng 0.", "is_true": False, "explanation": "Hàm số bậc ba không có min trên R."},
            {"label": "d", "content": "Đồ thị hàm số có tâm đối xứng nằm trên trục tung.", "is_true": True, "explanation": "Điểm uốn có hoành độ x = 0."}
        ],
        "explanation": "Khảo sát hàm số bậc ba chuẩn mực",
        "source_reference": "Đề tham khảo tốt nghiệp THPT 2025"
    }
    if overrides:
        data.update(overrides)
    return data
