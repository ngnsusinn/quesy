import io
import csv
import zipfile
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import SessionLocal
from backend.models import (
    ExamMatrix, MatrixItem, MasterExam, MasterExamItem,
    ExamVariant, ExamVariantItem, Question, QuestionOption, SubStatement
)
from backend.schemas import Option as SchemaOption
from backend.services.shuffling import shuffle_question_options
from backend.services.shuffling_engine import shuffle_options_with_anchor_rule


@pytest.fixture
def client():
    return TestClient(app)


# =========================================================================
# 1. KIỂM THỬ MA TRẬN ĐỀ THI: ROUTE ALIASES (/matrix & /matrices)
# =========================================================================

def test_matrix_route_aliases_parity(client):
    """Xác nhận cả hai route alias /api/v1/matrix và /api/v1/matrices đều hoạt động đồng bộ."""
    # 1. GET list matrices
    res_plural = client.get("/api/v1/matrices")
    res_singular = client.get("/api/v1/matrix")

    assert res_plural.status_code == 200
    assert res_singular.status_code == 200

    plural_data = res_plural.json()
    singular_data = res_singular.json()

    assert len(plural_data) == len(singular_data)
    if plural_data:
        assert plural_data[0]["id"] == singular_data[0]["id"]

    # 2. POST create matrix via singular route alias
    tree_res = client.get("/api/v1/taxonomy/tree")
    assert tree_res.status_code == 200
    tree = tree_res.json()
    subj_id = tree.get("subject_id", "subj-toan")
    grade_id = tree.get("grade_id", "grade-12")
    yccd_id = tree["strands"][0]["topics"][0]["lessons"][0]["learning_outcomes"][0]["id"]

    matrix_payload = {
        "title": "Ma trận Kiểm thử Route Alias",
        "subject_id": subj_id,
        "grade_id": grade_id,
        "duration_minutes": 50,
        "total_points": 10.0,
        "items": [
            {
                "learning_outcome_id": yccd_id,
                "cognitive_level": "RECOGNITION",
                "item_format": "SINGLE_CHOICE",
                "quantity": 2,
                "points_per_item": 0.25
            }
        ]
    }

    create_singular = client.post("/api/v1/matrix", json=matrix_payload)
    assert create_singular.status_code == 201
    created_id = create_singular.json()["id"]

    # 3. GET single matrix via both aliases
    get_plural = client.get(f"/api/v1/matrices/{created_id}")
    get_singular = client.get(f"/api/v1/matrix/{created_id}")
    assert get_plural.status_code == 200
    assert get_singular.status_code == 200
    assert get_plural.json()["id"] == created_id
    assert get_singular.json()["id"] == created_id

    # 4. POST check-availability via both aliases
    avail_plural = client.post(f"/api/v1/matrices/{created_id}/check-availability")
    avail_singular = client.post(f"/api/v1/matrix/{created_id}/check-availability")
    assert avail_plural.status_code == 200
    assert avail_singular.status_code == 200
    assert avail_plural.json()["is_sufficient"] == avail_singular.json()["is_sufficient"]

    # 5. Default check-availability without ID via both aliases
    def_plural = client.post("/api/v1/matrices/check-availability")
    def_singular = client.post("/api/v1/matrix/check-availability")
    assert def_plural.status_code == 200
    assert def_singular.status_code == 200


# =========================================================================
# 2. KIỂM THỬ XUẤT BẢN ĐẶC TẢ MA TRẬN (JSON, CSV UTF-8 BOM, PDF)
# =========================================================================

def test_matrix_spec_export_formats_json_csv_pdf(client):
    """Kiểm thử GET /matrix/{id}/spec với 3 định dạng: JSON, CSV UTF-8 BOM, và PDF Vector."""
    # Lấy ma trận có sẵn
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrices = m_res.json()
    assert len(matrices) > 0
    matrix_id = matrices[0]["id"]

    # --- Định dạng JSON ---
    res_json = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=json")
    assert res_json.status_code == 200
    assert "application/json" in res_json.headers.get("content-type", "").lower()
    spec_json = res_json.json()
    assert spec_json["id"] == matrix_id
    assert "title" in spec_json
    assert "duration_minutes" in spec_json
    assert "total_points" in spec_json
    assert "items" in spec_json
    assert isinstance(spec_json["items"], list)
    if spec_json["items"]:
        first_item = spec_json["items"][0]
        assert "cognitive_level" in first_item
        assert "item_format" in first_item
        assert "quantity" in first_item
        assert "points_per_item" in first_item

    # Kiểm tra alias route /matrices/{id}/spec?format=json
    res_json_alias = client.get(f"/api/v1/matrices/{matrix_id}/spec?format=json")
    assert res_json_alias.status_code == 200
    assert res_json_alias.json()["id"] == matrix_id

    # --- Định dạng CSV (UTF-8 BOM) ---
    res_csv = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "").lower()
    # Khẳng định tệp bắt đầu bằng byte UTF-8 BOM \xef\xbb\xbf
    assert res_csv.content.startswith(b"\xef\xbb\xbf"), "Tệp CSV bản đặc tả bắt buộc phải chứa tiền tố UTF-8 BOM"

    # Kiểm tra tính toàn vẹn của nội dung CSV khi giải mã
    csv_text = res_csv.content.decode("utf-8-sig")
    csv_reader = csv.reader(io.StringIO(csv_text))
    header = next(csv_reader)
    expected_headers = ["STT", "Mã YCCĐ", "Mức độ nhận thức", "Dạng câu hỏi", "Số lượng", "Điểm/câu", "Tổng điểm"]
    assert header == expected_headers

    # --- Định dạng PDF (Vector PDF A4 Portrait) ---
    res_pdf = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers.get("content-type") == "application/pdf"
    # Khẳng định tệp PDF bắt đầu bằng ma thuật nhận dạng PDF
    assert res_pdf.content.startswith(b"%PDF"), "Tệp xuất bản PDF phải bắt đầu bằng byte b'%PDF'"
    assert len(res_pdf.content) > 1000, "Tệp PDF bản đặc tả phải có dung lượng thực chất"

    # --- Định dạng không hợp lệ -> 400 Bad Request ---
    res_invalid = client.get(f"/api/v1/matrix/{matrix_id}/spec?format=invalid_fmt")
    assert res_invalid.status_code == 400
    assert "invalid format" in res_invalid.json()["detail"].lower()


# =========================================================================
# 3. KIỂM THỬ TỒN KHO THỰC TẾ (CHECK AVAILABILITY)
# =========================================================================

def test_matrix_check_availability_real_inventory(client):
    """Kiểm tra báo cáo tồn kho câu hỏi APPROVED thực tế theo YCCĐ và Bloom."""
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrix_id = m_res.json()[0]["id"]

    res = client.post(f"/api/v1/matrix/{matrix_id}/check-availability")
    assert res.status_code == 200
    data = res.json()

    assert "matrix_id" in data
    assert "is_sufficient" in data
    assert isinstance(data["is_sufficient"], bool)
    assert "total_required" in data
    assert "total_available" in data
    assert "total_deficit" in data
    assert "items" in data
    assert isinstance(data["items"], list)

    for cell in data["items"]:
        assert "learning_outcome_id" in cell
        assert "cognitive_level" in cell
        assert "item_format" in cell
        assert "required_quantity" in cell
        assert "available_quantity" in cell
        assert "is_sufficient" in cell
        assert "deficit" in cell
        # deficit = max(0, required - available)
        expected_deficit = max(0, cell["required_quantity"] - cell["available_quantity"])
        assert cell["deficit"] == expected_deficit
        assert cell["is_sufficient"] == (cell["available_quantity"] >= cell["required_quantity"])


# =========================================================================
# 4. KIỂM THỬ SINH ĐỀ GỐC (GENERATE MASTER EXAM FULL SCHEMA)
# =========================================================================

def test_exams_generate_master_with_full_item_structure(client):
    """Kiểm tra POST /exams/generate tạo đề gốc với options, sub_statements, has_anchor."""
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrices = m_res.json()

    # Chọn ma trận có câu hỏi
    target_matrix = matrices[0]
    matrix_id = target_matrix["id"]

    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": matrix_id,
        "title": "Đề Khảo Thí Tích Hợp Test Suite",
        "allow_partial": True
    })
    assert gen_res.status_code == 201
    master_exam = gen_res.json()

    assert master_exam["id"] is not None
    assert master_exam["matrix_id"] == matrix_id
    assert master_exam["title"] == "Đề Khảo Thí Tích Hợp Test Suite"
    assert master_exam["total_questions"] > 0
    assert len(master_exam["items"]) > 0

    single_choice_found = False
    true_false_found = False

    for item in master_exam["items"]:
        assert "id" in item
        assert "question_id" in item
        assert "section" in item
        assert "order_index" in item
        assert "points" in item
        assert "stem" in item
        assert "item_format" in item
        assert "cognitive_level" in item
        assert "has_anchor" in item
        assert isinstance(item["has_anchor"], bool)
        assert "options" in item
        assert "sub_statements" in item

        if item["item_format"] == "SINGLE_CHOICE" and item["options"]:
            single_choice_found = True
            for opt in item["options"]:
                assert "label" in opt
                assert "content" in opt
                assert "is_correct" in opt

        if item["item_format"] == "TRUE_FALSE_GROUP" and item["sub_statements"]:
            true_false_found = True
            for sub in item["sub_statements"]:
                assert "label" in sub
                assert "content" in sub
                assert "is_true" in sub

    assert single_choice_found or true_false_found, "Phải kiểm tra được ít nhất một câu hỏi có options hoặc sub_statements"


# =========================================================================
# 5. KIỂM THỬ REPLACEMENT CANDIDATES & ĐỔI CÂU HỎI (SWAP QUESTION)
# =========================================================================

def test_exams_replacement_candidates_and_swap_clears_variants(client):
    """Kiểm tra tìm câu hỏi thay thế tương đương và đổi câu hỏi thành công, xóa variants cũ."""
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrix_id = m_res.json()[0]["id"]

    # 1. Tạo đề thi gốc
    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": matrix_id,
        "title": "Đề Test Replacement và Swap",
        "allow_partial": True
    })
    assert gen_res.status_code == 201
    master = gen_res.json()
    master_id = master["id"]
    first_item = master["items"][0]
    item_id = first_item["id"]
    old_q_id = first_item["question_id"]

    # 2. Sinh trước các variants
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={
        "variant_codes": ["101", "102"]
    })
    assert shuf_res.status_code == 200
    assert shuf_res.json()["generated_variants_count"] == 2

    # Xác nhận DB có variants
    db = SessionLocal()
    try:
        variants_before = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_id).all()
        assert len(variants_before) == 2
    finally:
        db.close()

    # 3. Lấy danh sách câu hỏi thay thế (replacement candidates)
    cand_res = client.get(f"/api/v1/exams/{master_id}/items/{item_id}/replacement-candidates")
    assert cand_res.status_code == 200
    candidates = cand_res.json()
    assert isinstance(candidates, list)

    if not candidates:
        # Nếu ngân hàng chưa có câu khác, tạo 1 câu APPROVED cùng YCCĐ để test
        db = SessionLocal()
        try:
            new_candidate = Question(
                stem="Câu hỏi bổ sung phục vụ swap candidate",
                item_format=first_item["item_format"] or "SINGLE_CHOICE",
                cognitive_level=first_item["cognitive_level"] or "RECOGNITION",
                learning_outcome_id=first_item["learning_outcome_id"],
                status="APPROVED",
                is_defective=False
            )
            db.add(new_candidate)
            db.commit()
            db.refresh(new_candidate)
            new_q_id = new_candidate.id
        finally:
            db.close()
    else:
        new_q_id = candidates[0]["id"]
        # Đảm bảo không trùng câu cũ
        assert new_q_id != old_q_id

    # 4. Thực hiện swap câu hỏi
    swap_res = client.post(
        f"/api/v1/exams/{master_id}/items/{item_id}/swap",
        json={"new_question_id": new_q_id}
    )
    assert swap_res.status_code == 200
    swapped_item = swap_res.json()
    assert swapped_item["question_id"] == new_q_id

    # 5. Khẳng định toàn bộ variants cũ đã bị xóa sạch (buộc người dùng phải trộn lại đề mới)
    db = SessionLocal()
    try:
        variants_after = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_id).all()
        assert len(variants_after) == 0, "Sau khi swap câu hỏi trong đề gốc, toàn bộ variants cũ bắt buộc phải bị xóa"
    finally:
        db.close()


# =========================================================================
# 6. KIỂM THỬ OPTION ANCHOR RULE: ĐẠT 100% TẠI VỊ TRÍ D
# =========================================================================

def test_exams_shuffle_option_anchor_rule_100_percent_at_d(client):
    """Kiểm tra quy tắc Option Anchor Rule: 100% đáp án mỏ neo luôn khóa ở vị trí D."""
    anchor_phrases = [
        "Cả A và B đều đúng",
        "Cả 3 đáp án trên",
        "Tất cả các đáp án trên",
        "Tất cả đều đúng",
        "Tất cả đều sai",
        "Không có đáp án nào đúng",
        "Không tồn tại",
    ]

    for phrase in anchor_phrases:
        # Trường hợp 1: Ban đầu nằm ở vị trí A
        opts_pos_a = [
            QuestionOption(label="A", content=phrase, is_correct=True, is_fixed=False),
            QuestionOption(label="B", content="Hàm số nghịch biến", is_correct=False, is_fixed=False),
            QuestionOption(label="C", content="Hàm số đồng biến", is_correct=False, is_fixed=False),
            QuestionOption(label="D", content="Hàm số không đổi", is_correct=False, is_fixed=False),
        ]
        # Xáo trộn 50 lần, vị trí luôn luôn phải là D
        for seed in range(50):
            shuffled_opts, mapping, correct_lbl = shuffle_options_with_anchor_rule(opts_pos_a)
            assert len(shuffled_opts) == 4
            # Khóa 100% tại vị trí cuối cùng (D)
            last_opt = shuffled_opts[3]
            assert last_opt.content == phrase
            assert mapping["A"] == "D"
            assert correct_lbl == "D"

        # Trường hợp 2: Ban đầu nằm ở vị trí B
        opts_pos_b = [
            QuestionOption(label="A", content="Hàm số đồng biến", is_correct=False, is_fixed=False),
            QuestionOption(label="B", content=phrase, is_correct=True, is_fixed=False),
            QuestionOption(label="C", content="Hàm số nghịch biến", is_correct=False, is_fixed=False),
            QuestionOption(label="D", content="Hàm số không đổi", is_correct=False, is_fixed=False),
        ]
        for seed in range(50):
            shuffled_opts, mapping, correct_lbl = shuffle_options_with_anchor_rule(opts_pos_b)
            assert shuffled_opts[3].content == phrase
            assert mapping["B"] == "D"
            assert correct_lbl == "D"

    # Kiểm tra trực tiếp qua API POST /api/v1/exams/shuffle
    direct_payload = {
        "title": "Kiểm thử Trộn Đề Trực Tiếp Anchor Rule",
        "num_variants": 4,
        "variant_codes": ["201", "202", "203", "204"],
        "questions": [
            {
                "id": "q-anchor-test-1",
                "stem": "Chọn khẳng định đúng nhất:",
                "item_format": "SINGLE_CHOICE",
                "options": [
                    {"label": "A", "content": "Tất cả các đáp án trên", "is_correct": True, "is_fixed": False},
                    {"label": "B", "content": "Đáp án 1", "is_correct": False, "is_fixed": False},
                    {"label": "C", "content": "Đáp án 2", "is_correct": False, "is_fixed": False},
                    {"label": "D", "content": "Đáp án 3", "is_correct": False, "is_fixed": False},
                ]
            }
        ]
    }
    direct_res = client.post("/api/v1/exams/shuffle", json=direct_payload)
    assert direct_res.status_code == 200
    direct_data = direct_res.json()
    assert len(direct_data["variants"]) == 4

    for var in direct_data["variants"]:
        q_item = var["questions"][0]
        var_opts = q_item["options"]
        assert len(var_opts) == 4
        assert var_opts[3]["label"] == "D"
        assert var_opts[3]["content"] == "Tất cả các đáp án trên", "Trong mã đề con, đáp án mỏ neo bắt buộc phải ở vị trí D"


# =========================================================================
# 7. KIỂM THỬ ĐÓNG GÓI TRỌN BỘ ẤN PHẨM KHẢO THÍ (.ZIP 5 THÀNH PHẦN)
# =========================================================================

def test_exams_export_zip_five_standard_components(client):
    """Kiểm tra GET /exams/{id}/export-zip xuất file ZIP chứa đủ 5 nhóm thành phần chuẩn."""
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrix_id = m_res.json()[0]["id"]

    # 1. Sinh đề thi gốc
    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": matrix_id,
        "title": "Đề Khảo Thí Xuất Bản ZIP 5 Thành Phần",
        "allow_partial": True
    })
    assert gen_res.status_code == 201
    master_id = gen_res.json()["id"]

    # 2. Trộn 4 mã đề chuẩn
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={
        "variant_codes": ["101", "102", "103", "104"]
    })
    assert shuf_res.status_code == 200
    assert shuf_res.json()["generated_variants_count"] == 4

    # 3. Tải gói ZIP xuất bản
    zip_res = client.get(f"/api/v1/exams/{master_id}/export-zip")
    assert zip_res.status_code == 200
    assert zip_res.headers.get("content-type") == "application/zip"

    # 4. Phân tích nội dung bên trong tệp ZIP
    zip_buffer = io.BytesIO(zip_res.content)
    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        file_list = zipf.namelist()

        # Thành phần 1: Đề thi từng mã đề dạng PDF (De_{code}.pdf)
        for code in ["101", "102", "103", "104"]:
            assert f"De_{code}.pdf" in file_list, f"Thiếu tệp đề thi De_{code}.pdf trong gói ZIP"
            # Kiểm tra nội dung tệp là PDF hợp lệ
            exam_bytes = zipf.read(f"De_{code}.pdf")
            assert exam_bytes.startswith(b"%PDF"), f"Tệp De_{code}.pdf không phải định dạng PDF hợp lệ"

        # Thành phần 2: Hướng dẫn giải chi tiết từng mã đề (LoiGiai_{code}.pdf)
        for code in ["101", "102", "103", "104"]:
            assert f"LoiGiai_{code}.pdf" in file_list, f"Thiếu tệp lời giải LoiGiai_{code}.pdf trong gói ZIP"
            sol_bytes = zipf.read(f"LoiGiai_{code}.pdf")
            assert sol_bytes.startswith(b"%PDF"), f"Tệp LoiGiai_{code}.pdf không phải định dạng PDF hợp lệ"

        # Thành phần 3: Bảng ma trận đáp án tổng hợp dạng PDF (BangDapAn_TongHop.pdf)
        assert "BangDapAn_TongHop.pdf" in file_list, "Thiếu tệp BangDapAn_TongHop.pdf trong gói ZIP"
        ans_pdf_bytes = zipf.read("BangDapAn_TongHop.pdf")
        assert ans_pdf_bytes.startswith(b"%PDF")

        # Thành phần 4: Bảng ma trận đáp án tổng hợp dạng CSV UTF-8 BOM (BangDapAn_TongHop.csv)
        assert "BangDapAn_TongHop.csv" in file_list, "Thiếu tệp BangDapAn_TongHop.csv trong gói ZIP"
        ans_csv_bytes = zipf.read("BangDapAn_TongHop.csv")
        assert ans_csv_bytes.startswith(b"\xef\xbb\xbf"), "Tệp BangDapAn_TongHop.csv trong ZIP phải bắt đầu bằng UTF-8 BOM"

        # Thành phần 5: Phiếu trả lời trắc nghiệm chuẩn OMR 2025 (Phieu_Tra_Loi_Trac_Nghiem_2025.pdf)
        assert "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf" in file_list, "Thiếu tệp Phieu_Tra_Loi_Trac_Nghiem_2025.pdf trong gói ZIP"
        omr_bytes = zipf.read("Phieu_Tra_Loi_Trac_Nghiem_2025.pdf")
        assert omr_bytes.startswith(b"%PDF")


# =========================================================================
# 8. KIỂM THỬ 3 PRESETS MA TRẬN CHUẨN HÓA (THPT 2025, GIỮA KỲ, CUỐI KỲ)
# =========================================================================

def test_three_matrix_presets_spec_and_calculations(client):
    """Kiểm tra cấu hình và tính toán điểm của 3 Presets chuẩn hóa:
    - THPT 2025: 34 câu, 10.0đ
    - Giữa kỳ: 20 câu, 10.0đ
    - Cuối kỳ: 28 câu, 10.0đ
    """
    tree_res = client.get("/api/v1/taxonomy/tree")
    assert tree_res.status_code == 200
    tree = tree_res.json()
    subj_id = tree.get("subject_id", "subj-toan")
    grade_id = tree.get("grade_id", "grade-12")
    yccd_id = tree["strands"][0]["topics"][0]["lessons"][0]["learning_outcomes"][0]["id"]

    presets = [
        {
            "name": "THPT 2025",
            "expected_questions": 34,
            "expected_points": 10.0,
            "items": [
                # 24 câu trắc nghiệm 4 lựa chọn x 0.25đ = 6.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "RECOGNITION", "item_format": "SINGLE_CHOICE", "quantity": 24, "points_per_item": 0.25},
                # 2 câu Đúng/Sai x 1.0đ = 2.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "COMPREHENSION", "item_format": "TRUE_FALSE_GROUP", "quantity": 2, "points_per_item": 1.0},
                # 8 câu Trả lời ngắn x 0.25đ = 2.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "APPLICATION", "item_format": "SHORT_ANSWER", "quantity": 8, "points_per_item": 0.25},
            ]
        },
        {
            "name": "Giữa kỳ",
            "expected_questions": 20,
            "expected_points": 10.0,
            "items": [
                # 12 câu trắc nghiệm x 0.25đ = 3.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "RECOGNITION", "item_format": "SINGLE_CHOICE", "quantity": 12, "points_per_item": 0.25},
                # 4 câu Đúng/Sai x 1.0đ = 4.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "COMPREHENSION", "item_format": "TRUE_FALSE_GROUP", "quantity": 4, "points_per_item": 1.0},
                # 4 câu Trả lời ngắn x 0.75đ = 3.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "APPLICATION", "item_format": "SHORT_ANSWER", "quantity": 4, "points_per_item": 0.75},
            ]
        },
        {
            "name": "Cuối kỳ",
            "expected_questions": 28,
            "expected_points": 10.0,
            "items": [
                # 20 câu trắc nghiệm x 0.25đ = 5.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "RECOGNITION", "item_format": "SINGLE_CHOICE", "quantity": 20, "points_per_item": 0.25},
                # 4 câu Đúng/Sai x 1.0đ = 4.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "COMPREHENSION", "item_format": "TRUE_FALSE_GROUP", "quantity": 4, "points_per_item": 1.0},
                # 4 câu Trả lời ngắn x 0.25đ = 1.0đ
                {"learning_outcome_id": yccd_id, "cognitive_level": "APPLICATION", "item_format": "SHORT_ANSWER", "quantity": 4, "points_per_item": 0.25},
            ]
        }
    ]

    for p in presets:
        # Tính toán tổng câu và tổng điểm lý thuyết
        calc_questions = sum(it["quantity"] for it in p["items"])
        calc_points = round(sum(it["quantity"] * it["points_per_item"] for it in p["items"]), 2)
        assert calc_questions == p["expected_questions"]
        assert calc_points == p["expected_points"]

        # Tạo matrix qua API
        res = client.post("/api/v1/matrix", json={
            "title": f"Preset {p['name']}",
            "subject_id": subj_id,
            "grade_id": grade_id,
            "duration_minutes": 90,
            "total_points": p["expected_points"],
            "items": p["items"]
        })
        assert res.status_code == 201
        m_data = res.json()
        assert m_data["total_points"] == p["expected_points"]
        assert len(m_data["items"]) == len(p["items"])


# =========================================================================
# 9. KIỂM THỬ MASTER EXAM SOURCE TOOLBAR & SHUFFLER VECTOR PDF EXPORT
# =========================================================================

def test_shuffler_master_exam_source_toolbar_and_frontend_contract(client):
    """Kiểm thử Master Exam Source Toolbar trong Shuffler:
    - DOM Elements trong frontend/index.html: #shuffler-select-master-exam, #shuffler-select-matrix,
      #btn-shuffler-gen-matrix, #btn-shuffler-sync-matrix, #shuffler-exam-meta-bar.
    - JavaScript methods trong frontend/static/app.js: loadMasterExamsAndMatricesForShuffler,
      onShufflerMasterExamChange, generateMasterExamFromSelectedMatrix, syncFromCurrentMatrix.
    - Backend endpoints: GET /exams, GET /matrices, POST /exams/generate.
    """
    from pathlib import Path

    # 1. Kiểm tra DOM elements trong frontend/index.html
    html_path = Path("frontend/index.html")
    assert html_path.exists()
    html_content = html_path.read_text(encoding="utf-8")
    assert 'id="shuffler-select-master-exam"' in html_content
    assert 'id="shuffler-select-matrix"' in html_content
    assert 'id="btn-shuffler-gen-matrix"' in html_content
    assert 'id="btn-shuffler-sync-matrix"' in html_content
    assert 'id="shuffler-exam-meta-bar"' in html_content

    # 2. Kiểm tra JS methods trong frontend/static/app.js
    js_path = Path("frontend/static/app.js")
    assert js_path.exists()
    js_content = js_path.read_text(encoding="utf-8")
    assert "loadMasterExamsAndMatricesForShuffler" in js_content
    assert "onShufflerMasterExamChange" in js_content
    assert "generateMasterExamFromSelectedMatrix" in js_content
    assert "syncFromCurrentMatrix" in js_content

    # 3. Kiểm tra API endpoints phục vụ Toolbar
    exams_res = client.get("/api/v1/exams")
    assert exams_res.status_code == 200
    assert isinstance(exams_res.json(), list)

    matrices_res = client.get("/api/v1/matrices")
    assert matrices_res.status_code == 200
    matrices = matrices_res.json()
    assert len(matrices) > 0
    m_id = matrices[0]["id"]

    # 4. Sinh Đề Gốc từ Ma Trận đã chọn
    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": m_id,
        "title": "Đề Khảo Thí Từ Ma Trận Shuffler Toolbar",
        "allow_partial": True
    })
    assert gen_res.status_code in [200, 201]
    master = gen_res.json()
    assert "id" in master
    assert len(master.get("items", [])) > 0


def test_shuffler_export_single_variant_and_package_pure_vector_pdf(client):
    """Kiểm thử xuất bản Vector PDF của Shuffler:
    - GET /exams/{master_id}/export-pdf?variant_code=101 xuất PDF chuẩn (%PDF).
    - GET /exams/{master_id}/export-zip xuất trọn bộ gói ZIP với đầy đủ Vector PDF.
    """
    # 1. Lấy ma trận và sinh đề gốc
    m_res = client.get("/api/v1/matrices")
    assert m_res.status_code == 200
    matrix_id = m_res.json()[0]["id"]

    gen_res = client.post("/api/v1/exams/generate", json={
        "matrix_id": matrix_id,
        "title": "Đề Khảo Thí Xuất Bản Vector PDF",
        "allow_partial": True
    })
    assert gen_res.status_code in [200, 201]
    master_id = gen_res.json()["id"]

    # 2. Hoán vị 4 mã đề
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={
        "variant_codes": ["101", "102", "103", "104"]
    })
    assert shuf_res.status_code == 200

    # 3. Kiểm thử xuất đơn lẻ 1 mã đề PDF: GET /exams/{master_id}/export-pdf?variant_code=101
    pdf_res = client.get(f"/api/v1/exams/{master_id}/export-pdf?variant_code=101")
    assert pdf_res.status_code == 200
    assert "application/pdf" in pdf_res.headers.get("content-type", "").lower()
    assert pdf_res.content.startswith(b"%PDF"), "Mã đề xuất bản đơn lẻ phải là tệp PDF hợp lệ bắt đầu bằng %PDF"
    assert len(pdf_res.content) > 1000

    # 4. Kiểm thử xuất trọn bộ gói ZIP: GET /exams/{master_id}/export-zip
    zip_res = client.get(f"/api/v1/exams/{master_id}/export-zip")
    assert zip_res.status_code == 200
    assert "application/zip" in zip_res.headers.get("content-type", "").lower()

    with zipfile.ZipFile(io.BytesIO(zip_res.content), "r") as zf:
        namelist = zf.namelist()
        for c in ["101", "102", "103", "104"]:
            de_file = f"De_{c}.pdf"
            lg_file = f"LoiGiai_{c}.pdf"
            assert de_file in namelist, f"Gói ZIP phải chứa {de_file}"
            assert lg_file in namelist, f"Gói ZIP phải chứa {lg_file}"
            assert zf.read(de_file).startswith(b"%PDF"), f"{de_file} phải có định dạng %PDF"
            assert zf.read(lg_file).startswith(b"%PDF"), f"{lg_file} phải có định dạng %PDF"

        assert "BangDapAn_TongHop.pdf" in namelist
        assert zf.read("BangDapAn_TongHop.pdf").startswith(b"%PDF")
        assert "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf" in namelist
        assert zf.read("Phieu_Tra_Loi_Trac_Nghiem_2025.pdf").startswith(b"%PDF")

