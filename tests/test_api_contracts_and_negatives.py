import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas import (
    QuestionDetailResponse, Question, ExamMatrix, MasterExam,
    Subject, Grade, Strand, Topic, Lesson,
    LearningOutcome, ProblemArchetype
)
from tests.factories import (
    create_question_payload, create_true_false_question_payload
)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def sample_taxonomy(client):
    res = client.get("/api/v1/taxonomy/tree")
    assert res.status_code == 200
    tree = res.json()
    assert len(tree["strands"]) > 0
    strand = tree["strands"][0]
    topic = strand["topics"][0]
    lesson = topic["lessons"][0]
    yccd = lesson["learning_outcomes"][0]
    archetype = yccd["archetypes"][0] if yccd.get("archetypes") else None
    return {
        "subject_id": tree["subject_id"],
        "grade_id": tree["grade_id"],
        "yccd_id": yccd["id"],
        "archetype_id": archetype["id"] if archetype else None
    }


# ==============================================================================
# 1. CONTRACT & SCHEMA VALIDATION (Rule: contract-schema-validation)
# ==============================================================================

def test_contract_get_taxonomy_tree_schema(client):
    """Assert response matches TaxonomyTree structure with all 6 tiers."""
    # Arrange & Act
    res = client.get("/api/v1/taxonomy/tree")
    
    # Assert (Status and Shape)
    assert res.status_code == 200
    data = res.json()
    assert "subject_id" in data
    assert "subject_name" in data
    assert "grade_id" in data
    assert "grade_name" in data
    assert isinstance(data["strands"], list)
    assert len(data["strands"]) >= 4  # Circular 32 Math 12 has 4 strands

    # Validate each tier's schema integrity
    first_strand = data["strands"][0]
    assert "id" in first_strand
    assert "code" in first_strand
    assert "name" in first_strand
    assert "topics" in first_strand
    
    first_topic = first_strand["topics"][0]
    assert "id" in first_topic
    assert "lessons" in first_topic
    
    first_lesson = first_topic["lessons"][0]
    assert "id" in first_lesson
    assert "learning_outcomes" in first_lesson
    
    first_yccd = first_lesson["learning_outcomes"][0]
    assert "id" in first_yccd
    assert "code" in first_yccd
    assert "archetypes" in first_yccd


from backend.routers.questions import QuestionOut

def test_contract_question_detail_pydantic_validation(client, sample_taxonomy):
    """Ensure POST and GET question response strictly validates against QuestionOut schema."""
    # Arrange
    payload = create_question_payload(
        yccd_id=sample_taxonomy["yccd_id"],
        archetype_id=sample_taxonomy["archetype_id"]
    )

    # Act
    create_res = client.post("/api/v1/questions", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()

    # Validate against Pydantic model (strict schema validation)
    validated_question = QuestionOut.model_validate(created_data)
    assert validated_question.id == created_data["id"]
    assert validated_question.learning_outcome_id == sample_taxonomy["yccd_id"]
    assert len(validated_question.options) == 4

    # Fetch detail
    get_res = client.get(f"/api/v1/questions/{created_data['id']}")
    assert get_res.status_code == 200
    fetched_data = get_res.json()
    validated_fetched = QuestionOut.model_validate(fetched_data)
    assert validated_fetched.id == created_data["id"]


# ==============================================================================
# 2. NEGATIVE TESTS & ERROR SHAPES (Rule: errors-negative-cases & consistent-shape)
# ==============================================================================

def test_negative_get_question_not_found_returns_consistent_error_shape(client):
    """Non-existent question ID must return 404 with structured detail error."""
    # Arrange
    non_existent_id = "00000000-0000-0000-0000-000000000000"

    # Act
    res = client.get(f"/api/v1/questions/{non_existent_id}")

    # Assert
    assert res.status_code == 404
    body = res.json()
    assert "detail" in body
    assert isinstance(body["detail"], str)
    assert "not found" in body["detail"].lower()


def test_negative_create_question_with_invalid_format_returns_422(client, sample_taxonomy):
    """Invalid item_format enum value must fail with 422 Unprocessable Entity."""
    # Arrange
    payload = create_question_payload(
        yccd_id=sample_taxonomy["yccd_id"],
        overrides={"item_format": "INVALID_QUESTION_FORMAT_XYZ"}
    )

    # Act
    res = client.post("/api/v1/questions", json=payload)

    # Assert
    assert res.status_code == 422
    body = res.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    error_fields = [err["loc"][-1] for err in body["detail"]]
    assert "item_format" in error_fields


def test_negative_create_question_missing_stem_returns_422(client, sample_taxonomy):
    """Missing required stem field must return 422."""
    # Arrange
    payload = {
        "learning_outcome_id": sample_taxonomy["yccd_id"],
        "item_format": "SINGLE_CHOICE",
        "cognitive_level": "RECOGNITION"
        # missing 'stem'
    }

    # Act
    res = client.post("/api/v1/questions", json=payload)

    # Assert
    assert res.status_code == 422
    body = res.json()
    assert "detail" in body
    assert any("stem" in str(err) for err in body["detail"])


def test_negative_upload_unsupported_file_extension_returns_400(client):
    """Uploading executable or unsupported file type (.exe) must return 400 Bad Request."""
    # Arrange
    file_content = b"fake executable binary content"

    # Act
    res = client.post(
        "/api/v1/digitize/upload",
        files={"file": ("malicious_payload.exe", file_content, "application/octet-stream")}
    )

    # Assert
    assert res.status_code == 400
    body = res.json()
    assert "detail" in body
    assert "unsupported" in body["detail"].lower() or "định dạng" in body["detail"].lower()


def test_negative_matrix_creation_missing_required_title_returns_422(client, sample_taxonomy):
    """Creating an ExamMatrix with missing title must return 422 Unprocessable Entity."""
    # Arrange: missing required 'title'
    bad_matrix_payload = {
        "subject_id": sample_taxonomy["subject_id"],
        "grade_id": sample_taxonomy["grade_id"],
        "duration_minutes": 45,
        "total_points": 10.0
    }

    # Act
    res = client.post("/api/v1/matrices", json=bad_matrix_payload)

    # Assert
    assert res.status_code == 422
    body = res.json()
    assert "detail" in body
    assert any("title" in str(err) for err in body["detail"])


def test_negative_generate_exam_with_nonexistent_matrix_returns_404(client):
    """Generating an exam from a non-existent matrix ID must return 404."""
    # Arrange
    fake_matrix_id = "00000000-0000-0000-0000-000000000000"

    # Act
    res = client.post("/api/v1/exams/generate", json={
        "matrix_id": fake_matrix_id,
        "title": "Đề thi ma trận ảo"
    })

    # Assert
    assert res.status_code == 404
    body = res.json()
    assert "detail" in body
    assert "not found" in body["detail"].lower()


def test_negative_generate_exam_with_excessive_inventory_requirement_returns_400(client, sample_taxonomy):
    """Requesting excessive questions exceeding bank inventory must return 400 with detailed inventory deficit."""
    # Arrange: create a matrix asking for 50000 questions (exceeds total bank capacity)
    matrix_payload = {
        "title": "Ma trận yêu cầu vượt ngưỡng",
        "subject_id": sample_taxonomy["subject_id"],
        "grade_id": sample_taxonomy["grade_id"],
        "duration_minutes": 90,
        "total_points": 10.0,
        "items": [
            {
                "section": "Part I: Trắc nghiệm",
                "learning_outcome_id": sample_taxonomy["yccd_id"],
                "cognitive_level": "RECOGNITION",
                "item_format": "SINGLE_CHOICE",
                "quantity": 50000,
                "points_per_item": 0.2,
                "order_index": 1
            }
        ]
    }
    mat_res = client.post("/api/v1/matrices", json=matrix_payload)
    assert mat_res.status_code == 201
    mat_id = mat_res.json()["id"]

    # Act: try to solve and generate
    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": mat_id,
        "title": "Đề thi quá tải"
    })

    # Assert: Must return 400 with explicit shortage description
    assert gen_res.status_code == 400
    body = gen_res.json()
    assert "detail" in body
    assert "insufficient" in body["detail"].lower() or "thiếu" in body["detail"].lower()


# ==============================================================================
# 3. IDEMPOTENCY VERIFICATION (Rule: requests-idempotency)
# ==============================================================================

def test_idempotency_delete_question(client, sample_taxonomy):
    """Deleting a question twice must be idempotent or return 404 on the second attempt."""
    # Arrange: create a question to delete
    payload = create_question_payload(yccd_id=sample_taxonomy["yccd_id"])
    create_res = client.post("/api/v1/questions", json=payload)
    q_id = create_res.json()["id"]

    # Act 1: first delete
    res1 = client.delete(f"/api/v1/questions/{q_id}")
    assert res1.status_code in [200, 204]

    # Act 2: second delete
    res2 = client.delete(f"/api/v1/questions/{q_id}")
    assert res2.status_code == 404  # Idempotently cleaned up and absent
