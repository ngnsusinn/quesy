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


def test_api_matrix_spec_and_availability_and_swap(client):
    """Test matrix spec exports (json, csv with UTF-8 BOM, pdf with %PDF),
    route aliases (/matrix and /matrices), live availability checker,
    master exam generation, item swap with variant invalidation,
    safe shuffling, and ZIP packaging containing 5 standard components.
    """
    import zipfile

    # 1. Route alias test: List matrices via both /matrices and /matrix
    m_res_plural = client.get("/api/v1/matrices")
    m_res_singular = client.get("/api/v1/matrix")
    assert m_res_plural.status_code == 200
    assert m_res_singular.status_code == 200
    matrices = m_res_plural.json()
    assert len(matrices) > 0
    matrix_id = matrices[0]["id"]

    # 2. Check availability via singular and plural aliases
    avail_res = client.post(f"/api/v1/matrix/{matrix_id}/check-availability")
    assert avail_res.status_code == 200
    avail_plural = client.post(f"/api/v1/matrices/{matrix_id}/check-availability")
    assert avail_plural.status_code == 200
    avail_data = avail_res.json()
    assert "is_sufficient" in avail_data
    assert "total_required" in avail_data
    assert "total_available" in avail_data
    assert "items" in avail_data

    # 3. Export matrix spec (JSON, CSV with UTF-8 BOM, PDF with %PDF)
    spec_json = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=json")
    assert spec_json.status_code == 200
    assert spec_json.json()["id"] == matrix_id

    spec_csv = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=csv")
    assert spec_csv.status_code == 200
    assert "utf-8" in spec_csv.headers.get("content-type", "").lower()
    # Confirm UTF-8 BOM byte prefix
    assert spec_csv.content.startswith(b"\xef\xbb\xbf"), "Matrix spec CSV must start with UTF-8 BOM bytes"

    spec_pdf = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=pdf")
    assert spec_pdf.status_code == 200
    assert spec_pdf.headers.get("content-type") == "application/pdf"
    # Confirm %PDF magic bytes
    assert spec_pdf.content.startswith(b"%PDF"), "Matrix spec PDF must start with %PDF magic bytes"

    # 4. Generate Master Exam and test replacement candidates & swap
    gen_res = client.post("/api/v1/exams/generate", json={"matrix_id": matrix_id, "title": "Test Exam", "allow_partial": True})
    assert gen_res.status_code in [200, 201]
    exam_data = gen_res.json()
    master_id = exam_data["id"]
    assert len(exam_data["items"]) > 0

    item = exam_data["items"][0]
    item_id = item["id"]

    # Generate variants first to test variant invalidation on swap
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={"variant_codes": ["101", "102"]})
    assert shuf_res.status_code == 200
    assert shuf_res.json()["generated_variants_count"] == 2

    # Query replacement candidates
    cand_res = client.get(f"/api/v1/exams/{master_id}/items/{item_id}/replacement-candidates")
    assert cand_res.status_code == 200
    candidates = cand_res.json()
    if len(candidates) > 0:
        new_q_id = candidates[0]["id"]
        swap_res = client.post(f"/api/v1/exams/{master_id}/items/{item_id}/swap", json={"new_question_id": new_q_id})
        assert swap_res.status_code == 200
        assert swap_res.json()["question_id"] == new_q_id

        # Re-shuffle after swap to generate all 4 variants
        re_shuf = client.post(f"/api/v1/exams/{master_id}/shuffle", json={"variant_codes": ["101", "102", "103", "104"]})
        assert re_shuf.status_code == 200
        assert re_shuf.json()["generated_variants_count"] == 4

        # Export ZIP and verify 5 standard components
        zip_res = client.get(f"/api/v1/exams/{master_id}/export-zip")
        assert zip_res.status_code == 200
        assert zip_res.headers.get("content-type") == "application/zip"

        with zipfile.ZipFile(io.BytesIO(zip_res.content), "r") as zf:
            namelist = zf.namelist()
            assert any(f.startswith("De_") and f.endswith(".pdf") for f in namelist), "ZIP must contain De_{code}.pdf"
            assert any(f.startswith("LoiGiai_") and f.endswith(".pdf") for f in namelist), "ZIP must contain LoiGiai_{code}.pdf"
            assert "BangDapAn_TongHop.pdf" in namelist, "ZIP must contain BangDapAn_TongHop.pdf"
            assert "BangDapAn_TongHop.csv" in namelist, "ZIP must contain BangDapAn_TongHop.csv"
            assert "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf" in namelist, "ZIP must contain Phieu_Tra_Loi_Trac_Nghiem_2025.pdf"
            # Verify CSV in ZIP has UTF-8 BOM
            assert zf.read("BangDapAn_TongHop.csv").startswith(b"\xef\xbb\xbf")


def test_api_questions_limit_1000_and_sqlite_persistence(client):
    """Kiểm thử /questions?limit=1000:
    - Nạp danh sách câu hỏi với limit=1000 thành công (200 OK).
    - Hỗ trợ limit tới 5000 (le=5000) và từ chối 5001 với lỗi 422.
    - Đảm bảo tính bền vững (persistence) trong SQLite: câu hỏi vừa tạo được lưu và truy xuất đầy đủ,
      không bị ghi đè bởi mock.
    """
    import uuid
    unique_tag = f"PERSIST_{uuid.uuid4().hex[:8]}"

    # 1. Tạo câu hỏi mới trực tiếp vào SQLite qua API
    payload = {
        "stem": f"Câu hỏi kiểm thử tính bền vững SQLite {unique_tag}: Cho $f'(x) = 3x^2$.",
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "learning_outcome_id": "TOAN12.GT.01",
        "cognitive_level": "RECOGNITION",
        "item_format": "SINGLE_CHOICE",
        "options": [
            {"label": "A", "content": "$f(x) = x^3 + C$", "is_correct": True, "is_fixed": False},
            {"label": "B", "content": "$f(x) = 6x + C$", "is_correct": False, "is_fixed": False},
            {"label": "C", "content": "$f(x) = x^2 + C$", "is_correct": False, "is_fixed": False},
            {"label": "D", "content": "$f(x) = 3 + C$", "is_correct": False, "is_fixed": False},
        ],
        "explanation": "Nguyên hàm của 3x^2 là x^3 + C."
    }

    create_resp = client.post("/api/v1/questions", json=payload)
    assert create_resp.status_code == 201, create_resp.text
    created_id = create_resp.json()["id"]

    # 2. Gọi GET /questions?limit=1000
    res_1000 = client.get("/api/v1/questions?limit=1000")
    assert res_1000.status_code == 200
    qs_1000 = res_1000.json()
    assert isinstance(qs_1000, list)
    # Xác nhận câu hỏi vừa tạo nằm trong danh sách trả về từ SQLite
    assert any(q["id"] == created_id for q in qs_1000), "Câu hỏi mới phải tồn tại trong SQLite và được nạp qua limit=1000"

    # 3. Kiểm thử biên độ tối đa le=5000:
    res_5000 = client.get("/api/v1/questions?limit=5000")
    assert res_5000.status_code == 200

    # 4. Kiểm thử âm tính vượt quá limit 5000 -> 422 Unprocessable Entity
    res_5001 = client.get("/api/v1/questions?limit=5001")
    assert res_5001.status_code == 422


def test_api_exam_latex_sanitization_and_canonical_true_false_format(client):
    """Kiểm thử API và quy trình xử lý đề thi chứa underscore và True/False:
    - Tạo câu hỏi có bare underscores như 'VAR_PARAM_999' ngoài math mode.
    - Tạo câu hỏi Đúng/Sai với 4 khẳng định con.
    - Xác nhận hàm sanitize_latex_for_xetex tự động escape dấu gạch dưới mà không làm ảnh hưởng math subscripts.
    - Xác nhận generate_variant_latex định dạng \\choiceTF[1] bọc từng khẳng định trong {...}.
    """
    from backend.services.latex_converter import sanitize_latex_for_xetex
    from backend.services.docx_exporter import generate_variant_latex
    from types import SimpleNamespace

    # 1. Tạo câu hỏi Đúng/Sai qua API
    payload_tf = {
        "stem": "Cho hàm số $y = \\dfrac{x_1 - 1}{x + 1}$ với hằng số SYSTEM_PARAM_01. Xét tính đúng sai:",
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "learning_outcome_id": "TOAN12.GT.01",
        "cognitive_level": "COMPREHENSION",
        "item_format": "TRUE_FALSE_GROUP",
        "options": [],
        "sub_statements": [
            {"label": "a", "content": "Tập xác định với $D = \\mathbb{R} \\setminus \\{-1\\}$", "is_correct": True, "explanation": "Mẫu số khác 0."},
            {"label": "b", "content": "Tiệm cận đứng là $x = -1$", "is_correct": True, "explanation": "Nghiệm mẫu số."},
            {"label": "c", "content": "Tiệm cận ngang là $y = 1$", "is_correct": True, "explanation": "Giới hạn tại vô cực."},
            {"label": "d", "content": "Đạo hàm luôn âm với mọi $x \\neq -1$", "is_correct": False, "explanation": "Đạo hàm dương."},
        ],
        "explanation": "Lời giải chi tiết cho câu hỏi Đúng Sai."
    }

    create_resp = client.post("/api/v1/questions", json=payload_tf)
    assert create_resp.status_code == 201, create_resp.text
    created_tf = create_resp.json()
    assert created_tf["item_format"] == "TRUE_FALSE_GROUP"

    # 2. Kiểm thử sanitize_latex_for_xetex trên stem
    sanitized_stem = sanitize_latex_for_xetex(payload_tf["stem"])
    assert "SYSTEM\\_PARAM\\_01" in sanitized_stem
    assert "$y = \\dfrac{x_1 - 1}{x + 1}$" in sanitized_stem
    assert "x\\_1" not in sanitized_stem

    # 3. Kiểm thử generate_variant_latex với format \choiceTF[1] có {...}
    mock_substatements = [
        SimpleNamespace(content=s["content"], is_correct=s["is_correct"], explanation=s["explanation"])
        for s in payload_tf["sub_statements"]
    ]
    mock_q = SimpleNamespace(
        id=created_tf["id"],
        item_format="TRUE_FALSE_GROUP",
        stem=payload_tf["stem"],
        options=[],
        sub_statements=mock_substatements,
        short_answer_key=None,
        explanation=payload_tf["explanation"]
    )
    mock_it = SimpleNamespace(
        variant_order_index=1,
        question=mock_q,
        option_mapping=None,
        answer_key="Đ-Đ-Đ-S"
    )
    mock_variant = SimpleNamespace(
        variant_code="505",
        items=[mock_it],
        master_exam=SimpleNamespace(
            title="Đề Thi Khảo Sát",
            subject=SimpleNamespace(name="Toán học", code="TOAN")
        )
    )

    latex_out = generate_variant_latex(mock_variant, is_solution=False)  # type: ignore[arg-type]
    assert r"\choiceTF[1]" in latex_out
    assert r"{\True Tập xác định với $D = \mathbb{R} \setminus \{-1\}$}" in latex_out
    assert r"{\True Tiệm cận đứng là $x = -1$}" in latex_out
    assert r"{\True Tiệm cận ngang là $y = 1$}" in latex_out
    assert r"{Đạo hàm luôn âm với mọi $x \neq -1$}" in latex_out
    assert "SYSTEM\\_PARAM\\_01" in latex_out
    assert r"\framebox{\textbf{Mã đề: 505}}" in latex_out
    assert not latex_out.startswith(r"\begin{center}")





