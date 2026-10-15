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
