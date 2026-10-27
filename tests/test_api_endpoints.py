import io
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas import CognitiveLevel, ItemFormat, QuestionStatus


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------------------------------------------
# 1. Test Upload API Endpoint
# -----------------------------------------------------------------

def test_api_upload_document(client):
    """Test file upload endpoint for AI parsing ingestion (PDF/DOCX)."""
    fake_content = b"Fake Word/PDF binary content for exam paper"
    files = {
        "file": ("De_Khao_Sat_12.docx", io.BytesIO(fake_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    data = {
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
    }

    response = client.post("/api/v1/upload", files=files, data=data)
    assert response.status_code in [200, 201]
    res_data = response.json()
    assert "job_id" in res_data
    assert res_data["filename"] == "De_Khao_Sat_12.docx"
    assert res_data["status"] in ["EXTRACTED", "PENDING", "COMPLETED"]
    assert "questions_count" in res_data


# -----------------------------------------------------------------
# 2. Test Questions CRUD & Duplicate Handling
# -----------------------------------------------------------------

def test_api_questions_crud(client):
    """Test Question CRUD operations (Create, Read, Update, Delete)."""
    # 1. CREATE a single-choice question
    q_payload = {
        "stem": "Tìm cực trị của hàm số $y = x^3 - 3x$.",
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "learning_outcome_id": "TOAN12.GT.01",
        "cognitive_level": "APPLICATION",
        "item_format": "SINGLE_CHOICE",
        "options": [
            {"label": "A", "content": "$y_{CD} = 2$", "is_correct": True, "is_fixed": False},
            {"label": "B", "content": "$y_{CD} = -2$", "is_correct": False, "is_fixed": False},
            {"label": "C", "content": "$y_{CD} = 0$", "is_correct": False, "is_fixed": False},
            {"label": "D", "content": "Cả A và B đều đúng", "is_correct": False, "is_fixed": True},
        ],
        "explanation": "Đạo hàm y' = 3x^2 - 3 = 0 <=> x = +-1...",
        "source_reference": "Đề Chuyên ĐHSP 2024",
        "embedding": [0.85, 0.42, 0.21, 0.11],
    }

    create_resp = client.post("/api/v1/questions", json=q_payload)
    assert create_resp.status_code == 201, create_resp.text
    created_q = create_resp.json()
    q_id = created_q["id"]
    assert q_id is not None
    assert created_q["stem"] == q_payload["stem"]
    assert created_q["learning_outcome_id"] is not None

    # 2. READ by ID
    get_resp = client.get(f"/api/v1/questions/{q_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == q_id

    # 3. LIST questions
    list_resp = client.get("/api/v1/questions")
    assert list_resp.status_code == 200
    all_qs = list_resp.json()
    assert any(q["id"] == q_id for q in all_qs)

    # 4. UPDATE question
    update_payload = {
        "stem": "Tìm cực trị của hàm số $y = x^3 - 3x + 1$.",
        "status": "APPROVED",
    }
    put_resp = client.put(f"/api/v1/questions/{q_id}", json=update_payload)
    assert put_resp.status_code == 200
    updated_q = put_resp.json()
    assert updated_q["stem"] == "Tìm cực trị của hàm số $y = x^3 - 3x + 1$."
    assert updated_q["status"] == "APPROVED"

    # 5. DUPLICATE CHECK: POST identical vector question without confirmation -> should be blocked / warned
    dup_payload = dict(q_payload)
    dup_payload["stem"] = "Tìm cực trị của hàm số y = x^3 - 3x (bản sao)."
    # Same or very close embedding (cosine similarity >= 0.90)
    dup_payload["embedding"] = [0.85, 0.42, 0.21, 0.11]
    dup_resp = client.post("/api/v1/questions", json=dup_payload)
    # Expect 409 Conflict or duplicate warning response
    assert dup_resp.status_code == 409 or "duplicate" in dup_resp.text.lower()

    # 6. DELETE question
    del_resp = client.delete(f"/api/v1/questions/{q_id}")
    assert del_resp.status_code in [200, 204]

    # Verify deleted
    get_again = client.get(f"/api/v1/questions/{q_id}")
    assert get_again.status_code == 404


# -----------------------------------------------------------------
# 3. Test Exam Matrix API Endpoint
# -----------------------------------------------------------------

def test_api_matrix_creation(client):
    """Test Exam Matrix Specification creation and retrieval."""
    matrix_payload = {
        "title": "Ma trận Đề kiểm tra cuối kỳ I - Toán 12",
        "grade_id": "grade-12",
        "subject_id": "subj-toan",
        "duration_minutes": 90,
        "total_points": 10.0,
        "items": [
            {
                "learning_outcome_id": "TOAN12.GT.01",
                "cognitive_level": "RECOGNITION",
                "item_format": "SINGLE_CHOICE",
                "question_count": 10,
                "points_per_question": 0.25,
            },
            {
                "learning_outcome_id": "TOAN12.GT.01",
                "cognitive_level": "APPLICATION",
                "item_format": "TRUE_FALSE_GROUP",
                "question_count": 4,
                "points_per_question": 1.0,
            },
        ],
    }

    create_resp = client.post("/api/v1/matrices", json=matrix_payload)
    assert create_resp.status_code == 201, create_resp.text
    matrix_data = create_resp.json()
    matrix_id = matrix_data["id"]
    assert matrix_id is not None
    assert matrix_data["title"] == matrix_payload["title"]
    assert len(matrix_data["items"]) == 2

    # Retrieve matrix
    get_resp = client.get(f"/api/v1/matrices/{matrix_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == matrix_id


# -----------------------------------------------------------------
# 4. Test Variant Shuffling API Endpoint
# -----------------------------------------------------------------

def test_api_variant_shuffling(client):
    """Test generating shuffled exam variants via API, asserting RULE-02 and RULE-03."""
    passage_id = "pas-reading-01"
    questions = [
        # Standalone question 1 with fixed option (RULE-02)
        {
            "id": "q-shuffle-1",
            "stem": "Phương án nào sau đây đúng?",
            "subject_id": "subj-toan",
            "grade_id": "grade-12",
            "learning_outcome_id": "TOAN12.GT.01",
            "cognitive_level": "APPLICATION",
            "item_format": "SINGLE_CHOICE",
            "options": [
                {"label": "A", "content": "Mệnh đề A", "is_correct": False, "is_fixed": False},
                {"label": "B", "content": "Mệnh đề B", "is_correct": False, "is_fixed": False},
                {"label": "C", "content": "Mệnh đề C", "is_correct": False, "is_fixed": False},
                {"label": "D", "content": "Cả A và B đều đúng", "is_correct": True, "is_fixed": True},
            ],
            "status": "APPROVED",
        },
        # Passage child 1 (RULE-03)
        {
            "id": "q-child-1",
            "stem": "Câu hỏi đọc hiểu 1",
            "subject_id": "subj-toan",
            "grade_id": "grade-12",
            "learning_outcome_id": "TOAN12.GT.01",
            "cognitive_level": "COMPREHENSION",
            "item_format": "PASSAGE_GROUP",
            "passage_id": passage_id,
            "options": [
                {"label": "A", "content": "Opt 1A", "is_correct": True, "is_fixed": False},
                {"label": "B", "content": "Opt 1B", "is_correct": False, "is_fixed": False},
            ],
            "status": "APPROVED",
        },
        # Passage child 2 (RULE-03)
        {
            "id": "q-child-2",
            "stem": "Câu hỏi đọc hiểu 2",
            "subject_id": "subj-toan",
            "grade_id": "grade-12",
            "learning_outcome_id": "TOAN12.GT.01",
            "cognitive_level": "COMPREHENSION",
            "item_format": "PASSAGE_GROUP",
            "passage_id": passage_id,
            "options": [
                {"label": "A", "content": "Opt 2A", "is_correct": True, "is_fixed": False},
                {"label": "B", "content": "Opt 2B", "is_correct": False, "is_fixed": False},
            ],
            "status": "APPROVED",
        },
        # Standalone question 2
        {
            "id": "q-shuffle-2",
            "stem": "Hàm số nào sau đây đồng biến trên R?",
            "subject_id": "subj-toan",
            "grade_id": "grade-12",
            "learning_outcome_id": "TOAN12.GT.01",
            "cognitive_level": "RECOGNITION",
            "item_format": "SINGLE_CHOICE",
            "options": [
                {"label": "A", "content": "y = x^3 + x", "is_correct": True, "is_fixed": False},
                {"label": "B", "content": "y = -x^3", "is_correct": False, "is_fixed": False},
            ],
            "status": "APPROVED",
        },
    ]

    shuffle_payload = {
        "title": "Kỳ thi Khảo sát Khối 12",
        "questions": questions,
        "num_variants": 4,
        "variant_codes": ["101", "102", "103", "104"],
    }

    resp = client.post("/api/v1/exams/shuffle", json=shuffle_payload)
    assert resp.status_code == 200, resp.text
    result = resp.json()
    assert "variants" in result
    variants = result["variants"]
    assert len(variants) == 4

    for variant in variants:
        # Check RULE-02: option 'Cả A và B đều đúng' must ALWAYS be at position D
        q1 = next((q for q in variant["questions"] if q["question_id"] == "q-shuffle-1"), None)
        assert q1 is not None
        assert q1["options"][3]["label"] == "D"
        assert q1["options"][3]["content"] == "Cả A và B đều đúng"

        # Check RULE-03: passage child 1 and child 2 must be consecutive
        child_indices = [
            idx for idx, q in enumerate(variant["questions"])
            if q["passage_id"] == passage_id
        ]
        assert len(child_indices) == 2
        assert child_indices[1] == child_indices[0] + 1


# -----------------------------------------------------------------
# 5. Test Question Bank Count, Export, Import, Filters & Cascade Delete
# -----------------------------------------------------------------

def test_api_questions_count_endpoint(client):
    """Test GET /api/v1/questions/count returns distribution by format."""
    res = client.get("/api/v1/questions/count")
    assert res.status_code == 200
    counts = res.json()
    assert "total" in counts
    assert "single_choice" in counts
    assert "true_false" in counts
    assert "short_answer" in counts
    assert counts["total"] >= 0
    assert counts["single_choice"] >= 0
    assert counts["true_false"] >= 0
    assert counts["short_answer"] >= 0


def test_api_questions_export_csv_utf8_bom(client):
    """Test POST /api/v1/questions/export with format=csv returns UTF-8 BOM."""
    res = client.post("/api/v1/questions/export", json={"format": "csv"})
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    assert "quesy_bank_export.csv" in res.headers.get("content-disposition", "")
    # Check binary UTF-8 BOM marker (\xef\xbb\xbf)
    assert res.content.startswith(b"\xef\xbb\xbf"), "CSV stream must start with UTF-8 BOM bytes"
    # Check text representation
    assert res.text.startswith("\ufeff"), "Decoded CSV text must start with \\ufeff character"
    assert "ID,Format,CognitiveLevel,Stem,Explanation" in res.text


def test_api_questions_export_latex_and_json(client):
    """Test POST /api/v1/questions/export for latex and json formats."""
    # LaTeX format
    res_tex = client.post("/api/v1/questions/export", json={"format": "latex"})
    assert res_tex.status_code == 200
    data_tex = res_tex.json()
    assert data_tex["success"] is True
    assert data_tex["format"] == "latex"
    assert "latex_code" in data_tex
    assert r"\begin{ex}" in data_tex["latex_code"]

    # JSON format
    res_json = client.post("/api/v1/questions/export", json={"format": "json"})
    assert res_json.status_code == 200
    data_json = res_json.json()
    assert data_json["success"] is True
    assert "count" in data_json
    assert "questions" in data_json
    assert isinstance(data_json["questions"], list)


def test_api_questions_import_latex_and_json(client):
    """Test POST /api/v1/questions/import for LaTeX snippet and JSON payloads."""
    # 1. Import via LaTeX
    latex_snippet = r"""
\begin{ex}
Tìm họ nguyên hàm của hàm số $f(x) = 2x$.
\choice
{\True $x^2 + C$}
{$2x^2 + C$}
{$x + C$}
{$2 + C$}
\begin{loigiai}
Ta có $\int 2x dx = x^2 + C$.
\end{loigiai}
\end{ex}
"""
    res_tex = client.post("/api/v1/questions/import", json={"latex_code": latex_snippet})
    assert res_tex.status_code == 200
    data_tex = res_tex.json()
    assert data_tex["success"] is True
    assert data_tex["imported_count"] >= 1

    # 2. Import via questions_json
    json_payload = [
        {
            "stem": "Cho hàm số bậc ba $y = f(x)$. Tính $f'(1)$.",
            "item_format": "SHORT_ANSWER",
            "short_answer_key": "3.5",
            "tolerance": 0.01,
            "cognitive_level": "APPLICATION"
        }
    ]
    res_json = client.post("/api/v1/questions/import", json={"questions_json": json_payload})
    assert res_json.status_code == 200
    data_json = res_json.json()
    assert data_json["success"] is True
    assert data_json["imported_count"] >= 1


def test_api_questions_keyword_search_and_taxonomy_filters(client):
    """Test filtering questions by keyword and taxonomy hierarchy (strand_id, topic_id, lesson_id)."""
    import uuid
    from backend.database import SessionLocal
    from backend.models import Strand, Topic, Lesson

    db = SessionLocal()
    strand = db.query(Strand).first()
    topic = db.query(Topic).first()
    lesson = db.query(Lesson).first()
    strand_id = strand.id if strand else None
    topic_id = topic.id if topic else None
    lesson_id = lesson.id if lesson else None
    db.close()

    unique_marker = f"KW_TEST_{uuid.uuid4().hex[:8]}"
    create_payload = {
        "stem": f"Câu hỏi kiểm thử tìm kiếm từ khóa: {unique_marker}",
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "strand_id": strand_id,
        "topic_id": topic_id,
        "lesson_id": lesson_id,
        "cognitive_level": "RECOGNITION",
        "item_format": "SINGLE_CHOICE",
        "options": [
            {"label": "A", "content": "Đáp án đúng", "is_correct": True},
            {"label": "B", "content": "Đáp án sai", "is_correct": False}
        ]
    }
    c_res = client.post("/api/v1/questions", json=create_payload)
    assert c_res.status_code == 201
    q_id = c_res.json()["id"]

    try:
        # Search by unique keyword
        kw_res = client.get(f"/api/v1/questions?keyword={unique_marker}")
        assert kw_res.status_code == 200
        kw_data = kw_res.json()
        assert len(kw_data) >= 1
        assert any(q["id"] == q_id for q in kw_data)

        # Search by non-existent keyword
        empty_res = client.get(f"/api/v1/questions?keyword=NON_EXISTENT_{uuid.uuid4().hex}")
        assert empty_res.status_code == 200
        assert len(empty_res.json()) == 0

        # Filter by strand_id if present
        if strand_id:
            strand_res = client.get(f"/api/v1/questions?strand_id={strand_id}")
            assert strand_res.status_code == 200
            assert any(q["id"] == q_id for q in strand_res.json())

        # Filter by topic_id if present
        if topic_id:
            topic_res = client.get(f"/api/v1/questions?topic_id={topic_id}")
            assert topic_res.status_code == 200
            assert any(q["id"] == q_id for q in topic_res.json())

        # Filter by lesson_id if present
        if lesson_id:
            lesson_res = client.get(f"/api/v1/questions?lesson_id={lesson_id}")
            assert lesson_res.status_code == 200
            assert any(q["id"] == q_id for q in lesson_res.json())
    finally:
        client.delete(f"/api/v1/questions/{q_id}")


def test_api_question_delete_cascade_options_and_substatements(client):
    """Test that deleting a question cascades deletion to its QuestionOptions and SubStatements."""
    from backend.database import SessionLocal
    from backend.models import QuestionOption, SubStatement

    payload = {
        "stem": "Câu hỏi kiểm tra cascade delete",
        "cognitive_level": "COMPREHENSION",
        "item_format": "SINGLE_CHOICE",
        "options": [
            {"label": "A", "content": "Option 1", "is_correct": True},
            {"label": "B", "content": "Option 2", "is_correct": False}
        ],
        "sub_statements": [
            {"label": "a", "content": "Khẳng định a", "is_true": True},
            {"label": "b", "content": "Khẳng định b", "is_true": False}
        ]
    }
    c_res = client.post("/api/v1/questions", json=payload)
    assert c_res.status_code == 201
    q_id = c_res.json()["id"]

    # Verify options and sub-statements exist in database
    db = SessionLocal()
    try:
        opts = db.query(QuestionOption).filter(QuestionOption.question_id == q_id).all()
        subs = db.query(SubStatement).filter(SubStatement.question_id == q_id).all()
        assert len(opts) == 2
        assert len(subs) == 2
    finally:
        db.close()

    # Delete the question via DELETE endpoint
    del_res = client.delete(f"/api/v1/questions/{q_id}")
    assert del_res.status_code in [200, 204]

    # Verify cascade deletion
    db2 = SessionLocal()
    try:
        opts_after = db2.query(QuestionOption).filter(QuestionOption.question_id == q_id).all()
        subs_after = db2.query(SubStatement).filter(SubStatement.question_id == q_id).all()
        assert len(opts_after) == 0, "QuestionOption records must be deleted on cascade"
        assert len(subs_after) == 0, "SubStatement records must be deleted on cascade"
    finally:
        db2.close()

