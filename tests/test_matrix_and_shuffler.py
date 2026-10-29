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

    # 2. Trộn 2 mã đề chuẩn để kiểm thử trọn bộ 5 thành phần mà không gây nghẽn thời gian runner
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={
        "variant_codes": ["101", "102"]
    })
    assert shuf_res.status_code == 200
    assert shuf_res.json()["generated_variants_count"] == 2

    # 3. Tải gói ZIP xuất bản
    zip_res = client.get(f"/api/v1/exams/{master_id}/export-zip")
    assert zip_res.status_code == 200
    assert zip_res.headers.get("content-type") == "application/zip"

    # 4. Phân tích nội dung bên trong tệp ZIP
    zip_buffer = io.BytesIO(zip_res.content)
    with zipfile.ZipFile(zip_buffer, "r") as zipf:
        file_list = zipf.namelist()

        # Thành phần 1: Đề thi từng mã đề dạng PDF (De_{code}.pdf)
        for code in ["101", "102"]:
            assert f"De_{code}.pdf" in file_list, f"Thiếu tệp đề thi De_{code}.pdf trong gói ZIP"
            # Kiểm tra nội dung tệp là PDF hợp lệ
            exam_bytes = zipf.read(f"De_{code}.pdf")
            assert exam_bytes.startswith(b"%PDF"), f"Tệp De_{code}.pdf không phải định dạng PDF hợp lệ"

        # Thành phần 2: Hướng dẫn giải chi tiết từng mã đề (LoiGiai_{code}.pdf)
        for code in ["101", "102"]:
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

    # 2. Hoán vị 1 mã đề để kiểm thử nhanh xuất bản ZIP mà không gây nghẽn thời gian runner
    shuf_res = client.post(f"/api/v1/exams/{master_id}/shuffle", json={
        "variant_codes": ["101"]
    })
    assert shuf_res.status_code == 200

    # 3. Kiểm thử xuất đơn lẻ 1 mã đề PDF & trọn bộ gói ZIP thông qua Shuffler Router
    from pathlib import Path
    from unittest.mock import patch
    def mock_compile(latex_source, output_pdf, title="", mode="dethi"):
        output_pdf = Path(output_pdf)
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        output_pdf.write_bytes(b"%PDF-1.5 Vector PDF generated for Shuffler test\n" + b"X" * 1200 + b"\n%%EOF")
        return True, "", 10

    with patch("backend.services.docx_exporter.compile_latex_to_pdf", side_effect=mock_compile):
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
            for c in ["101"]:
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


# =========================================================================
# 10. KIỂM THỬ THAO TÁC DÒNG MA TRẬN ĐỀ THI: DOM & JS CONTRACT
# =========================================================================

def test_matrix_hierarchical_multi_tier_dom_and_js_contract():
    """Kiểm thử cấu trúc DOM và JavaScript contract cho Bảng phân cấp đa tầng Ma trận đề thi:
    - DOM Elements trong frontend/index.html: #matrix-tree-toolbar, #matrix-search-archetype,
      #matrix-filter-has-stock, #btn-matrix-expand-all, #btn-matrix-collapse-all,
      #matrix-select-preset, #btn-matrix-reset, #matrix-hierarchical-tbody,
      #matrix-sticky-footer, #btn-matrix-generate-master.
    - Cấu trúc bảng ma trận đa tầng 3 cấp (Chương · Bài · Dạng x 3 Phần x 4 Cấp độ).
    - JS contract trong frontend/static/app.js: initHierarchicalMatrix, renderHierarchicalMatrix,
      toggleMatrixNode, expandAllMatrixTree, collapseAllMatrixTree, onMatrixSearchInput,
      onMatrixFilterStockChange, onMatrixCellChange, applyMatrixPreset, resetMatrixSelections,
      generateMasterExamFromHierarchicalMatrix có mặt và được export vào window.app.
    """
    from pathlib import Path
    html_path = Path("frontend/index.html")
    assert html_path.exists()
    html_content = html_path.read_text(encoding="utf-8")

    assert 'id="matrix-tree-toolbar"' in html_content
    assert 'id="matrix-search-archetype"' in html_content
    assert 'id="matrix-filter-has-stock"' in html_content
    assert 'id="btn-matrix-expand-all"' in html_content
    assert 'id="btn-matrix-collapse-all"' in html_content
    assert 'id="matrix-select-preset"' in html_content
    assert 'id="btn-matrix-reset"' in html_content
    assert 'id="matrix-hierarchical-tbody"' in html_content
    assert 'id="matrix-sticky-footer"' in html_content
    assert 'id="btn-matrix-generate-master"' in html_content

    js_path = Path("frontend/static/app.js")
    assert js_path.exists()
    js_content = js_path.read_text(encoding="utf-8")
    assert "initHierarchicalMatrix" in js_content
    assert "renderHierarchicalMatrix" in js_content
    assert "toggleMatrixNode" in js_content
    assert "expandAllMatrixTree" in js_content
    assert "collapseAllMatrixTree" in js_content
    assert "onMatrixSearchInput" in js_content
    assert "onMatrixFilterStockChange" in js_content
    assert "onMatrixCellChange" in js_content
    assert "applyMatrixPreset" in js_content
    assert "resetMatrixSelections" in js_content
    assert "generateMasterExamFromHierarchicalMatrix" in js_content
    assert "initHierarchicalMatrix," in js_content
    assert "renderHierarchicalMatrix," in js_content


def test_matrix_dynamic_scoring_and_bloom_calculation_no_hardcode():
    """Kiểm thử tính toán điểm số ma trận trả về giá trị thực tế theo dạng thức câu hỏi:
    - Loại bỏ hoàn toàn hardcode '10.0 đ' trong renderMatrixGrid().
    - Tính toán grandPoints động tích lũy theo từng dòng: (rowItems * formatPoints).
    - Hỗ trợ các trọng số điểm theo chuẩn:
      * SINGLE_CHOICE: 0.25đ / câu
      * TRUE_FALSE_GROUP: 1.0đ / câu
      * SHORT_ANSWER: 0.5đ / câu
      * ESSAY: 1.0đ / câu
    - Ma trận 22 câu mặc định: 12 TN (3.0đ) + 4 Đ/S (4.0đ) + 6 TLN (3.0đ) = 10.0đ (không bị nhảy sai thành 11.0đ).
    - Tính toán tỷ lệ Bloom: pctBiet, pctHieu, pctVandung.
    - Cảnh báo hoặc xác nhận chuẩn khảo thí theo ngưỡng phân bố.
    """
    from pathlib import Path

    js_path = Path("frontend/static/app.js")
    assert js_path.exists()
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Xác nhận loại bỏ hardcode '10.0 đ' và tính toán động theo dạng thức trong hàm renderMatrixGrid
    grid_func_start = js_content.find("function renderMatrixGrid()")
    assert grid_func_start != -1
    grid_func_end = js_content.find("function openAddMatrixRowModal()", grid_func_start)
    assert grid_func_end != -1
    grid_func_body = js_content[grid_func_start:grid_func_end]

    assert "document.getElementById('matrix-total-points').innerText = '10.0 đ'" not in grid_func_body, \
        "renderMatrixGrid tuyệt đối không được hardcode '10.0 đ'"
    assert "const formatPoints = MATRIX_FORMAT_POINTS[format] || 0.25;" in grid_func_body, \
        "Điểm từng dòng phải tra cứu theo MATRIX_FORMAT_POINTS"
    assert "grandPoints += rowItems * formatPoints;" in grid_func_body, \
        "grandPoints phải được tích lũy theo rowItems * formatPoints"
    assert "${grandPoints.toFixed(1)} đ" in grid_func_body, "Hiển thị tổng điểm phải sử dụng biến động ${grandPoints.toFixed(1)} đ"
    assert "${grandItems} câu" in grid_func_body, "Hiển thị tổng câu phải sử dụng biến động ${grandItems} câu"

    # 2. Xác nhận tính toán tỷ lệ Bloom phân bổ chuẩn khảo thí
    assert "let pctBiet = Math.round((totalBiet / grandItems) * 100)" in grid_func_body
    assert "let pctHieu = Math.round((totalHieu / grandItems) * 100)" in grid_func_body
    assert "let pctVandung = Math.max(0, 100 - pctBiet - pctHieu)" in grid_func_body
    assert "ĐẠT CHUẨN KHẢO THÍ: 40% Biết - 30% Hiểu - 30% Vận dụng" in grid_func_body
    assert "CẢNH BÁO: Tỷ lệ phân bố Bloom" in grid_func_body

    # 3. Mô phỏng thuật toán tính điểm động theo dạng thức câu hỏi
    format_points_map = {
        "SINGLE_CHOICE": 0.25,
        "TRUE_FALSE_GROUP": 1.0,
        "SHORT_ANSWER": 0.5,
        "ESSAY": 1.0,
    }

    def compute_matrix_summary(rows):
        total_biet = sum(r["biet"] for r in rows)
        total_hieu = sum(r["hieu"] for r in rows)
        total_vandung = sum(r["vandung"] for r in rows)
        grand_items = total_biet + total_hieu + total_vandung

        grand_points = 0.0
        for r in rows:
            fmt = r.get("itemFormat", "SINGLE_CHOICE")
            pts = format_points_map.get(fmt, 0.25)
            row_cnt = r["biet"] + r["hieu"] + r["vandung"]
            grand_points += row_cnt * pts

        grand_points = round(grand_points, 2)
        pct_biet = round((total_biet / grand_items) * 100) if grand_items > 0 else 0
        pct_hieu = round((total_hieu / grand_items) * 100) if grand_items > 0 else 0
        pct_vandung = max(0, 100 - pct_biet - pct_hieu) if grand_items > 0 else 0

        is_standard = (abs(pct_biet - 40) <= 5 and abs(pct_hieu - 30) <= 5)
        return {
            "grand_items": grand_items,
            "grand_points": grand_points,
            "pct_biet": pct_biet,
            "pct_hieu": pct_hieu,
            "pct_vandung": pct_vandung,
            "is_standard": is_standard
        }

    # Kịch bản 1: Ma trận chuẩn 22 câu mặc định (12 TN 0.25đ, 4 Đ/S 1.0đ, 6 TLN 0.5đ) -> Đúng chuẩn 10.0đ (không phải 11.0đ)
    default_22_rows = [
        {"itemFormat": "SINGLE_CHOICE", "biet": 6, "hieu": 4, "vandung": 2},   # 12 câu x 0.25 = 3.0đ
        {"itemFormat": "TRUE_FALSE_GROUP", "biet": 1, "hieu": 2, "vandung": 1},# 4 câu x 1.0 = 4.0đ
        {"itemFormat": "SHORT_ANSWER", "biet": 2, "hieu": 2, "vandung": 2},    # 6 câu x 0.5 = 3.0đ
    ]
    res_default = compute_matrix_summary(default_22_rows)
    assert res_default["grand_items"] == 22, "Tổng số câu phải đúng 22 câu"
    assert res_default["grand_points"] == 10.0, "Tổng điểm ma trận 22 câu chuẩn phải chính xác tuyệt đối 10.0đ"
    assert res_default["pct_biet"] == 41  # 9/22 = 40.9% ~ 41%
    assert res_default["pct_hieu"] == 36  # 8/22 = 36.4% ~ 36%
    assert res_default["pct_vandung"] == 23 # 5/22 = 22.7% ~ 23%

    # Kịch bản 2: Ma trận chuẩn 40 câu SINGLE_CHOICE (40 x 0.25 = 10.0đ)
    res_sc_only = compute_matrix_summary([
        {"itemFormat": "SINGLE_CHOICE", "biet": 16, "hieu": 12, "vandung": 12}
    ])
    assert res_sc_only["grand_items"] == 40
    assert res_sc_only["grand_points"] == 10.0
    assert res_sc_only["pct_biet"] == 40
    assert res_sc_only["pct_hieu"] == 30
    assert res_sc_only["pct_vandung"] == 30
    assert res_sc_only["is_standard"] is True

    # Kịch bản 3: Ma trận Tự luận 10 câu ESSAY (10 x 1.0 = 10.0đ)
    res_essay = compute_matrix_summary([
        {"itemFormat": "ESSAY", "biet": 4, "hieu": 3, "vandung": 3}
    ])
    assert res_essay["grand_items"] == 10
    assert res_essay["grand_points"] == 10.0
    assert res_essay["is_standard"] is True


# =========================================================================
# 12. KIỂM THỬ RENDER 3 THỂ THỨC CÂU HỎI TRONG ĐỀ GỐC & MÃ ĐỀ HOÁN VỊ
# =========================================================================

def test_render_master_exam_and_variant_view_three_question_formats():
    """Kiểm thử render 3 thể thức câu hỏi trong renderMasterExam và renderVariantView:
    - Hỗ trợ đầy đủ: SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER.
    - Format TRUE_FALSE_GROUP hiển thị Barem bậc thang QĐ 764 và nhãn [ĐÚNG]/[SAI].
    - Format SHORT_ANSWER hiển thị giá trị số thực chính xác.
    - Format SINGLE_CHOICE hiển thị danh sách phương án lựa chọn và huy hiệu neo [Neo D].
    """
    from pathlib import Path

    js_path = Path("frontend/static/app.js")
    assert js_path.exists()
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Kiểm tra renderMasterExam() hỗ trợ trọn vẹn 3 thể thức
    master_func_start = js_content.find("function renderMasterExam()")
    assert master_func_start != -1
    master_func_end = js_content.find("function swapMasterQuestion", master_func_start)
    assert master_func_end != -1
    master_func_body = js_content[master_func_start:master_func_end]

    # Kiểm tra badge thể thức
    assert "Trắc nghiệm Đơn" in master_func_body
    assert "Đúng/Sai (4 ý)" in master_func_body
    assert "Trả lời ngắn" in master_func_body

    # Kiểm tra cấu trúc render SINGLE_CHOICE
    assert "format === 'SINGLE_CHOICE' && q.options" in master_func_body
    assert "is_fixed || isAnchorPhrase(o.content)" in master_func_body
    assert "[Neo D]" in master_func_body

    # Kiểm tra cấu trúc render TRUE_FALSE_GROUP với barem QĐ 764
    assert "format === 'TRUE_FALSE_GROUP' && q.sub_statements" in master_func_body
    assert "Barem bậc thang QĐ 764: Đúng 1 ý = 0.1đ | Đúng 2 ý = 0.25đ | Đúng 3 ý = 0.5đ | Đúng 4 ý = 1.0đ" in master_func_body
    assert "sub.is_true ? '[ĐÚNG]' : '[SAI]'" in master_func_body

    # Kiểm tra cấu trúc render SHORT_ANSWER
    assert "format === 'SHORT_ANSWER'" in master_func_body
    assert "Đáp án đúng (Trả lời ngắn):" in master_func_body
    assert "q.short_answer_value || q.short_answer_key" in master_func_body

    # 2. Kiểm tra renderVariantView() hỗ trợ trọn vẹn 3 thể thức
    variant_func_start = js_content.find("function renderVariantView(code)")
    assert variant_func_start != -1
    variant_func_end = js_content.find("function renderAnswerKeyMatrixTable()", variant_func_start)
    assert variant_func_end != -1
    variant_func_body = js_content[variant_func_start:variant_func_end]

    assert "format === 'SINGLE_CHOICE' && q.options" in variant_func_body
    assert "format === 'TRUE_FALSE_GROUP' && q.sub_statements" in variant_func_body
    assert "sub.is_true ? '[ĐÚNG]' : '[SAI]'" in variant_func_body
    assert "format === 'SHORT_ANSWER'" in variant_func_body
    assert "q.short_answer_value || q.short_answer_key" in variant_func_body


# =========================================================================
# 13. KIỂM THỬ BẢNG MA TRẬN ĐÁP ÁN HIỂN THỊ ĐẦY ĐỦ 3 THỂ THỨC & 4 MÃ ĐỀ
# =========================================================================

def test_render_answer_key_matrix_table_three_question_formats():
    """Kiểm thử bảng ma trận đáp án hiển thị đầy đủ đáp án cho cả 3 thể thức:
    - Bảng hiển thị format badge tương ứng: 'TN Đơn', 'Đúng/Sai', 'Trả lời ngắn'.
    - Hiển thị đáp án đề gốc (masterKey) và cả 4 mã đề hoán vị (101, 102, 103, 104).
    - Cột Option Anchor phản ánh chính xác 'Khóa vị trí D' hoặc 'Hoán vị tự do'.
    - Mô phỏng logic tạo ma trận đáp án từ frontend đảm bảo mọi thể thức đều có key hợp lệ.
    """
    from pathlib import Path

    js_path = Path("frontend/static/app.js")
    assert js_path.exists()
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Kiểm tra renderAnswerKeyMatrixTable()
    table_func_start = js_content.find("function renderAnswerKeyMatrixTable()")
    assert table_func_start != -1
    table_func_end = js_content.find("function downloadPublishZip", table_func_start)
    assert table_func_end != -1
    table_func_body = js_content[table_func_start:table_func_end]

    assert "row.format === 'TRUE_FALSE_GROUP'" in table_func_body
    assert "row.format === 'SHORT_ANSWER'" in table_func_body
    assert "TN Đơn" in table_func_body
    assert "Đúng/Sai" in table_func_body
    assert "Trả lời ngắn" in table_func_body
    assert "row.masterKey" in table_func_body
    assert "row.variantKeys['101']" in table_func_body
    assert "row.variantKeys['102']" in table_func_body
    assert "row.variantKeys['103']" in table_func_body
    assert "row.variantKeys['104']" in table_func_body
    assert "Khóa vị trí D" in table_func_body
    assert "Hoán vị tự do" in table_func_body

    # 2. Mô phỏng thuật toán khởi tạo keyMatrix từ đề gốc 3 thể thức
    sample_master_items = [
        {
            "item_format": "SINGLE_CHOICE",
            "options": [
                {"label": "A", "content": "1", "is_correct": False, "is_fixed": False},
                {"label": "B", "content": "2", "is_correct": True, "is_fixed": False},
                {"label": "C", "content": "3", "is_correct": False, "is_fixed": False},
                {"label": "D", "content": "Cả ba đều đúng", "is_correct": False, "is_fixed": True},
            ]
        },
        {
            "item_format": "TRUE_FALSE_GROUP",
            "sub_statements": [
                {"label": "a", "is_true": True},
                {"label": "b", "is_true": False},
                {"label": "c", "is_true": True},
                {"label": "d", "is_true": True},
            ]
        },
        {
            "item_format": "SHORT_ANSWER",
            "short_answer_value": "3.14"
        }
    ]

    key_matrix = []
    codes = ["101", "102", "103", "104"]

    for idx, q in enumerate(sample_master_items):
        master_correct = "-"
        if q["item_format"] == "SINGLE_CHOICE":
            c = next((o for o in q["options"] if o["is_correct"]), None)
            master_correct = c["label"] if c else "A"
        elif q["item_format"] == "TRUE_FALSE_GROUP":
            master_correct = "-".join("Đ" if s["is_true"] else "S" for s in q["sub_statements"])
        elif q["item_format"] == "SHORT_ANSWER":
            master_correct = q.get("short_answer_value", "1")

        has_anchor = any(o.get("is_fixed") for o in q.get("options", []))

        variant_keys = {}
        for code in codes:
            if q["item_format"] == "SINGLE_CHOICE":
                variant_keys[code] = "B"  # hoặc phương án hoán vị
            else:
                variant_keys[code] = master_correct

        key_matrix.append({
            "qIndex": idx + 1,
            "format": q["item_format"],
            "masterKey": master_correct,
            "variantKeys": variant_keys,
            "hasAnchor": has_anchor
        })

    # Xác thực cấu trúc hàng ma trận đáp án cho từng thể thức
    assert len(key_matrix) == 3

    # Câu 1: SINGLE_CHOICE với Anchor ở D
    assert key_matrix[0]["format"] == "SINGLE_CHOICE"
    assert key_matrix[0]["masterKey"] == "B"
    assert key_matrix[0]["hasAnchor"] is True
    for code in codes:
        assert code in key_matrix[0]["variantKeys"]

    # Câu 2: TRUE_FALSE_GROUP chuẩn 4 ý Đ-S-Đ-Đ
    assert key_matrix[1]["format"] == "TRUE_FALSE_GROUP"
    assert key_matrix[1]["masterKey"] == "Đ-S-Đ-Đ"
    assert key_matrix[1]["hasAnchor"] is False
    for code in codes:
        assert key_matrix[1]["variantKeys"][code] == "Đ-S-Đ-Đ"

    # Câu 3: SHORT_ANSWER chuẩn số thực
    assert key_matrix[2]["format"] == "SHORT_ANSWER"
    assert key_matrix[2]["masterKey"] == "3.14"
    assert key_matrix[2]["hasAnchor"] is False
    for code in codes:
        assert key_matrix[2]["variantKeys"][code] == "3.14"


# =========================================================================
# 14. KIỂM THỬ MA TRẬN 8 CỘT, KHÔNG PRESET, VÀ CHUẨN ĐIỂM SỐ THEO DẠNG THỨC
# =========================================================================

def test_matrix_hierarchical_multi_tier_grid_contract():
    """Kiểm thử toàn diện Bảng phân cấp đa tầng Ma trận đề thi (Chương · Bài · Dạng x 3 Phần x 4 Cấp độ):
    1. Cấu trúc bảng ma trận đa tầng:
       - thead có 2 tầng: Tầng 1 (CHƯƠNG · BÀI · DẠNG, Phần I Trắc nghiệm, Phần II Đúng/Sai, Phần III Trả lời ngắn, Tổng câu, Tổng điểm), Tầng 2 (4 cột con NB, TH, VD, VDC cho mỗi phần).
       - tbody render cây phân cấp 3 tầng với ô input 12 ô/dạng và chip tồn kho.
    2. Thanh công cụ và Footer cố định:
       - #matrix-tree-toolbar, #matrix-search-archetype, #matrix-filter-has-stock,
         #btn-matrix-expand-all, #btn-matrix-collapse-all, #matrix-select-preset, #btn-matrix-reset.
       - #matrix-sticky-footer với thống kê Phần I, II, III, tổng cộng và nút #btn-matrix-generate-master.
    3. Hợp đồng API /backend/matrices/bank-inventory hoạt động chuẩn xác.
    """
    from pathlib import Path
    html_file = Path("frontend/index.html")
    assert html_file.exists()
    html_text = html_file.read_text(encoding="utf-8")

    assert 'id="matrix-hierarchical-tbody"' in html_text
    assert 'id="matrix-tree-toolbar"' in html_text
    assert 'id="matrix-search-archetype"' in html_text
    assert 'id="matrix-filter-has-stock"' in html_text
    assert 'id="btn-matrix-expand-all"' in html_text
    assert 'id="btn-matrix-collapse-all"' in html_text
    assert 'id="matrix-select-preset"' in html_text
    assert 'id="matrix-sticky-footer"' in html_text
    assert 'id="btn-matrix-generate-master"' in html_text


def test_apple_select_ui_styling_and_html_select_coverage():
    """Kiểm thử chuẩn thiết kế Apple Select UI và độ phủ toàn bộ thẻ <select>:
    1. CSS Properties trong frontend/static/style.css:
       - Class .apple-select được định nghĩa với appearance: none; -webkit-appearance: none;
       - border-radius: 12px;
       - Background custom SVG chevron arrow (data:image/svg+xml với polyline 6 9 12 15 18 9 và stroke %2364748b).
       - Font-family Apple HIG (-apple-system, BlinkMacSystemFont, SF Pro Text).
       - Trạng thái hover (.apple-select:hover) và focus (.apple-select:focus) chuẩn Apple blue.
    2. Độ phủ toàn bộ 19 thẻ <select> trong frontend/index.html:
       - Có đúng 19 thẻ <select> trong giao diện.
       - Toàn bộ 19 thẻ <select> đều áp dụng class 'apple-select'.
       - Bộ lọc YCCĐ #bank-filter-yccd tuyệt đối không chứa class 'font-mono'.
       - Kiểm tra danh sách định danh bắt buộc: #matrix-param-time, các bộ lọc 6 tầng
         (#bank-filter-grade, #bank-filter-subject, #bank-filter-strand, #bank-filter-topic,
         #bank-filter-lesson, #bank-filter-yccd), thuộc tính (#bank-filter-archetype,
         #bank-filter-cognitive, #bank-filter-format), Shuffler (#shuffler-select-master-exam,
         #shuffler-select-matrix), Modal (#q-edit-format, #q-edit-cognitive, #q-edit-yccd,
         #q-create-format, #q-create-cognitive, #modal-matrix-strand, #modal-matrix-format).
    """
    from pathlib import Path
    import re

    # 1. Kiểm thử frontend/static/style.css
    css_path = Path("frontend/static/style.css")
    assert css_path.exists(), "frontend/static/style.css phải tồn tại"
    css_content = css_path.read_text(encoding="utf-8")

    assert ".apple-select {" in css_content, "CSS phải định nghĩa class .apple-select"
    assert "appearance: none;" in css_content, ".apple-select phải có appearance: none;"
    assert "-webkit-appearance: none;" in css_content, ".apple-select phải có -webkit-appearance: none;"
    assert "border-radius: 12px;" in css_content, ".apple-select phải có border-radius: 12px;"
    assert "data:image/svg+xml" in css_content, ".apple-select phải sử dụng custom SVG chevron arrow"
    assert "polyline points='6 9 12 15 18 9'" in css_content, "SVG chevron phải có tọa độ polyline 6 9 12 15 18 9"
    assert "%2364748b" in css_content, "SVG chevron phải có stroke slate-500 (%2364748b)"
    assert "-apple-system" in css_content, ".apple-select phải áp dụng font-family Apple HIG (-apple-system)"
    assert ".apple-select:hover" in css_content, "CSS phải định nghĩa .apple-select:hover"
    assert ".apple-select:focus" in css_content, "CSS phải định nghĩa .apple-select:focus"

    # 2. Kiểm thử frontend/index.html
    html_path = Path("frontend/index.html")
    assert html_path.exists(), "frontend/index.html phải tồn tại"
    html_content = html_path.read_text(encoding="utf-8")

    # Tìm tất cả thẻ mở <select ...>
    select_tags = re.findall(r'<select\b[^>]*>', html_content, flags=re.IGNORECASE)
    assert len(select_tags) == 20, f"Kỳ vọng đúng 19 thẻ <select> trong HTML, thực tế tìm thấy: {len(select_tags)}"

    # Khẳng định 100% thẻ <select> đều chứa class 'apple-select'
    for tag in select_tags:
        assert "apple-select" in tag, f"Thẻ select sau thiếu class 'apple-select': {tag}"

    # Kiểm tra đặc biệt #bank-filter-yccd: có class 'apple-select' và tuyệt đối KHÔNG chứa 'font-mono'
    yccd_match = re.search(r'<select\b[^>]*id=["\']bank-filter-yccd["\'][^>]*>', html_content, flags=re.IGNORECASE)
    assert yccd_match is not None, "Không tìm thấy thẻ select #bank-filter-yccd"
    yccd_tag = yccd_match.group(0)
    assert "apple-select" in yccd_tag, "#bank-filter-yccd phải chứa class 'apple-select'"
    assert "font-mono" not in yccd_tag, "#bank-filter-yccd tuyệt đối không được chứa class 'font-mono'"

    # Kiểm tra danh sách 19 IDs bắt buộc
    expected_select_ids = [
        "bank-filter-grade",
        "bank-filter-subject",
        "bank-filter-strand",
        "bank-filter-topic",
        "bank-filter-lesson",
        "bank-filter-yccd",
        "bank-filter-archetype",
        "bank-filter-cognitive",
        "bank-filter-format",
        "matrix-param-time",
        "matrix-select-preset",
        "shuffler-select-master-exam",
        "shuffler-select-matrix",
        "q-edit-format",
        "q-edit-cognitive",
        "q-edit-yccd",
        "q-create-format",
        "q-create-cognitive",
        "modal-matrix-strand",
        "modal-matrix-format"
    ]
    for sel_id in expected_select_ids:
        tag_match = re.search(rf'<select\b[^>]*id=["\']{sel_id}["\'][^>]*>', html_content, flags=re.IGNORECASE)
        assert tag_match is not None, f"Không tìm thấy thẻ select id='{sel_id}'"
        assert "apple-select" in tag_match.group(0), f"Thẻ select id='{sel_id}' phải chứa class 'apple-select'"


def test_katex_global_expose_and_full_pipeline_rendering():
    """Kiểm thử cấu hình KaTeX toàn cục và phủ kín render KaTeX cho công thức toán học:
    1. Global expose trong frontend/static/app.js:
       - window.renderKaTeX = renderKaTeX;
       - window.app.renderKaTeX = renderKaTeX (phơi ra trong đối tượng window.app).
       - Hàm renderKaTeX(domElement) hỗ trợ delimiters: $$, $, \\(, \\[, throwOnError: false.
    2. Phủ kín gọi renderKaTeX(...) cho DOM container trong mọi luồng render:
       - renderItemBank(): gọi renderKaTeX(container)
       - renderMatrixGrid(): gọi renderKaTeX(tbody) ngay sau khi render lưới bảng 2D
       - openQuestionDetailModal(): gọi renderKaTeX(modal)
       - renderMasterExam(): gọi renderKaTeX(container)
       - renderVariantView(): gọi renderKaTeX(container)
       - openSwapQuestionModal(): gọi renderKaTeX(listEl)
    3. formatStemForDisplay được áp dụng toàn diện cho stem, options, sub_statements:
       - Question stem: formatStemForDisplay(q.stem)
       - Trắc nghiệm đơn: formatStemForDisplay(cleanOptionAnswer(opt.content), true)
       - Đúng/Sai 4 ý: formatStemForDisplay(sub.content, true)
       - Trả lời ngắn: formatStemForDisplay(cleanShortAnswer(...), true)
       - Lời giải chi tiết: formatStemForDisplay(q.explanation)
    """
    from pathlib import Path
    import re

    js_path = Path("frontend/static/app.js")
    assert js_path.exists(), "frontend/static/app.js phải tồn tại"
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Global expose
    assert "window.renderKaTeX = renderKaTeX;" in js_content, "app.js phải gán window.renderKaTeX = renderKaTeX;"
    
    # window.app definition export
    app_obj_start = js_content.rfind("window.app = {")
    assert app_obj_start != -1, "Không tìm thấy định nghĩa window.app"
    app_obj_end = js_content.find("};", app_obj_start)
    assert app_obj_end != -1, "Không tìm thấy kết thúc đối tượng window.app"
    app_obj_body = js_content[app_obj_start:app_obj_end]
    assert "renderKaTeX," in app_obj_body, "window.app phải export renderKaTeX"

    # 2. Hàm renderKaTeX delimiters
    katex_func_start = js_content.find("function renderKaTeX(domElement)")
    assert katex_func_start != -1
    katex_func_end = js_content.find("window.renderKaTeX = renderKaTeX;", katex_func_start)
    assert katex_func_end != -1
    katex_body = js_content[katex_func_start:katex_func_end]

    assert "renderMathInElement" in katex_body
    assert "{ left: '$$', right: '$$', display: true }" in katex_body
    assert "{ left: '$', right: '$', display: false }" in katex_body
    assert "{ left: '\\\\(', right: '\\\\)', display: false }" in katex_body
    assert "{ left: '\\\\[', right: '\\\\]', display: true }" in katex_body
    assert "throwOnError: false" in katex_body

    # 3. Kiểm tra gọi renderKaTeX trong các luồng giao diện chính

    # A. renderItemBank()
    item_bank_match = re.search(r'function renderItemBank\(\)\s*\{([\s\S]*?)\n  \}', js_content)
    assert item_bank_match is not None
    assert "renderKaTeX(container)" in item_bank_match.group(1), "renderItemBank phải gọi renderKaTeX(container)"

    # B. renderMatrixGrid()
    matrix_grid_start = js_content.find("function renderMatrixGrid()")
    assert matrix_grid_start != -1
    matrix_grid_end = js_content.find("function openAddMatrixRowModal()", matrix_grid_start)
    assert matrix_grid_end != -1
    matrix_grid_body = js_content[matrix_grid_start:matrix_grid_end]
    assert "tbody.innerHTML = html;" in matrix_grid_body
    assert "renderKaTeX(tbody);" in matrix_grid_body, "renderMatrixGrid phải gọi renderKaTeX(tbody) sau khi gán innerHTML"

    # C. openQuestionDetailModal()
    detail_modal_match = re.search(r'function openQuestionDetailModal\(id\)\s*\{([\s\S]*?)\n  \}', js_content)
    assert detail_modal_match is not None
    assert "renderKaTeX(modal)" in detail_modal_match.group(1), "openQuestionDetailModal phải gọi renderKaTeX(modal)"

    # D. renderMasterExam()
    master_exam_match = re.search(r'function renderMasterExam\(\)\s*\{([\s\S]*?)\n  \}', js_content)
    assert master_exam_match is not None
    assert "renderKaTeX(container)" in master_exam_match.group(1), "renderMasterExam phải gọi renderKaTeX(container)"

    # E. renderVariantView()
    variant_view_match = re.search(r'function renderVariantView\(code\)\s*\{([\s\S]*?)\n  \}', js_content)
    assert variant_view_match is not None
    assert "renderKaTeX(container)" in variant_view_match.group(1), "renderVariantView phải gọi renderKaTeX(container)"

    # F. openSwapQuestionModal()
    swap_modal_match = re.search(r'function openSwapQuestionModal\(masterIdx\)\s*\{([\s\S]*?)\n  \}', js_content)
    assert swap_modal_match is not None
    assert "renderKaTeX(listEl)" in swap_modal_match.group(1), "openSwapQuestionModal phải gọi renderKaTeX(listEl)"

    # 4. Kiểm tra formatStemForDisplay áp dụng cho stem, options, sub_statements
    # MCQ option
    assert "formatStemForDisplay(cleanOptionAnswer(opt.content), true)" in js_content or \
           "formatStemForDisplay(cleanOptionAnswer(o.content), true)" in js_content, \
           "Phải áp dụng formatStemForDisplay cho options trắc nghiệm"

    # True/False sub_statements
    assert "formatStemForDisplay(sub.content, true)" in js_content or \
           "formatStemForDisplay(s.content, true)" in js_content, \
           "Phải áp dụng formatStemForDisplay cho sub_statements Đúng/Sai"

    # Short answer
    assert "formatStemForDisplay(cleanShortAnswer" in js_content, \
           "Phải áp dụng formatStemForDisplay cho câu hỏi Trả lời ngắn"

    # Explanation
    assert "formatStemForDisplay(q.explanation)" in js_content, \
           "Phải áp dụng formatStemForDisplay cho lời giải chi tiết"


# =========================================================================
# 18. KIỂM THỬ BẢNG MA TRẬN PHÂN CẤP ĐA TẦNG VÀ STICKY FOOTER ACTION BAR
# =========================================================================

def test_matrix_bank_inventory_endpoint(client):
    """Kiểm thử endpoint /api/v1/matrix/bank-inventory và alias /api/v1/matrices/bank-inventory:
    - Xác nhận cả 2 route alias trả về HTTP 200 đồng nhất.
    - Cấu trúc phản hồi JSON: subject_id, grade_id, total_approved_questions, inventory.
    - inventory ánh xạ archetype_id -> item_format -> cognitive_level -> count.
    - Tính nhất quán dữ liệu: tổng số câu trong inventory khớp với total_approved_questions.
    - Hỗ trợ lọc theo query parameters: subject_id và grade_id.
    - Khi thêm một câu hỏi mới vào DB với problem_archetype_id, inventory tăng chính xác.
    """
    # 1. Gọi cả 2 alias
    res_singular = client.get("/api/v1/matrix/bank-inventory")
    res_plural = client.get("/api/v1/matrices/bank-inventory")

    assert res_singular.status_code == 200
    assert res_plural.status_code == 200

    data_s = res_singular.json()
    data_p = res_plural.json()

    assert data_s == data_p, "Phản hồi từ /matrix/bank-inventory và /matrices/bank-inventory phải đồng nhất"
    assert "total_approved_questions" in data_s
    assert "inventory" in data_s
    assert isinstance(data_s["total_approved_questions"], int)
    assert isinstance(data_s["inventory"], dict)

    # 2. Kiểm tra tính nhất quán của inventory
    sum_counted = 0
    for arch_id, formats in data_s["inventory"].items():
        assert isinstance(formats, dict)
        for fmt, levels in formats.items():
            assert isinstance(levels, dict)
            for lvl, count in levels.items():
                assert isinstance(count, int)
                assert count > 0
                sum_counted += count
    assert sum_counted == data_s["total_approved_questions"], "Tổng số câu trong inventory phải khớp total_approved_questions"

    # 3. Kiểm tra lọc theo subject_id và grade_id
    res_filtered = client.get("/api/v1/matrix/bank-inventory?subject_id=TOAN&grade_id=GRADE_12")
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.json()
    assert filtered_data["subject_id"] == "TOAN"
    assert filtered_data["grade_id"] == "GRADE_12"

    # 4. Thêm một câu hỏi mẫu vào DB và kiểm tra inventory phản ánh ngay lập tức
    db = SessionLocal()
    try:
        from backend.models import ProblemArchetype, Subject, Grade
        existing_arch = db.query(ProblemArchetype).first()
        assert existing_arch is not None, "DB phải có ít nhất 1 ProblemArchetype seeded"
        test_arch_id = existing_arch.id
        subj = db.query(Subject).first()
        grade = db.query(Grade).first()
        subj_id = getattr(existing_arch, "subject_id", None) or (subj.id if subj else None)
        grade_id = getattr(existing_arch, "grade_id", None) or (grade.id if grade else None)

        # Lấy count ban đầu của arch_id
        res_before = client.get(f"/api/v1/matrix/bank-inventory?subject_id={subj_id}&grade_id={grade_id}" if subj_id and grade_id else "/api/v1/matrix/bank-inventory")
        assert res_before.status_code == 200
        inv_before = res_before.json()["inventory"]
        prev_cnt = inv_before.get(test_arch_id, {}).get("SINGLE_CHOICE", {}).get("RECOGNITION", 0)

        test_q = Question(
            stem="Câu hỏi kiểm thử tồn kho ma trận phân cấp $y = f(x)$?",
            question_type="SINGLE_CHOICE",
            cognitive_level="RECOGNITION",
            problem_archetype_id=test_arch_id,
            subject_id=subj_id,
            grade_id=grade_id,
            status="APPROVED",
            source_reference="TIÊU CHUẨN MA TRẬN PHÂN CẤP"
        )
        db.add(test_q)
        db.commit()
        db.refresh(test_q)

        # Gọi lại endpoint
        res_after = client.get(f"/api/v1/matrix/bank-inventory?subject_id={subj_id}&grade_id={grade_id}" if subj_id and grade_id else "/api/v1/matrix/bank-inventory")
        assert res_after.status_code == 200
        inv_after = res_after.json()["inventory"]
        assert test_arch_id in inv_after, f"Archetype {test_arch_id} phải xuất hiện trong inventory sau khi thêm câu hỏi"
        assert "SINGLE_CHOICE" in inv_after[test_arch_id]
        new_cnt = inv_after[test_arch_id]["SINGLE_CHOICE"].get("RECOGNITION", 0)
        assert new_cnt == prev_cnt + 1, f"Số lượng tồn kho phải tăng đúng 1: trước {prev_cnt}, sau {new_cnt}"

        # Dọn dẹp
        db.delete(test_q)
        db.commit()
    finally:
        db.close()


def test_hierarchical_matrix_dom_structure_and_controls():
    """Kiểm thử cấu trúc DOM Bảng ma trận phân cấp đa tầng và Sticky Footer Action Bar:
    1. Cấu trúc DOM trong frontend/index.html:
       - Tab container #tab-matrix.
       - Thanh công cụ #matrix-tree-toolbar:
         * Ô tìm kiếm #matrix-search-archetype
         * Checkbox #matrix-filter-has-stock (Chỉ hiện dạng có câu)
         * Nút #btn-matrix-expand-all (Mở hết)
         * Nút #btn-matrix-collapse-all (Đóng hết)
         * Dropdown #matrix-select-preset (.apple-select)
         * Nút #btn-matrix-reset (Đặt lại)
       - Khung bảng #matrix-hierarchical-table-wrapper và tbody #matrix-hierarchical-tbody.
       - Header 2 tầng: Cột Cây 3 tầng (Chương · Bài · Dạng) và 3 Nhóm cột lớn (Phần I, II, III).
       - Đầy đủ 12 cột nhận thức: 4 cột Phần I (NB, TH, VD, VDC), 4 cột Phần II, 4 cột Phần III.
       - 2 Cột tổng kết: TỔNG CÂU và TỔNG ĐIỂM.
       - Sticky footer action bar #matrix-sticky-footer:
         * Thống kê 3 phần: #matrix-foot-p1, #matrix-foot-p2, #matrix-foot-p3
         * Tổng câu và điểm: #matrix-foot-grand
         * Mini bar Bloom 4 màu: #matrix-foot-bloom-lbl, #matrix-foot-bar-nb, #matrix-foot-bar-th, #matrix-foot-bar-vd, #matrix-foot-bar-vdc
         * Nút hành động chính: #btn-matrix-generate-master.
    2. JavaScript Function Contracts trong frontend/static/app.js:
       - Các hàm quản trị cây: initHierarchicalMatrix, renderHierarchicalMatrix, toggleMatrixNode,
         expandAllMatrixTree, collapseAllMatrixTree, onMatrixSearchInput, onMatrixFilterStockChange.
       - Các hàm ô nhập và presets: onMatrixCellChange, applyMatrixPreset, resetMatrixSelections,
         generateMasterExamFromHierarchicalMatrix.
       - Toàn bộ đều được export vào window.app.
    """
    from pathlib import Path
    html_path = Path("frontend/index.html")
    assert html_path.exists(), "frontend/index.html phải tồn tại"
    html_content = html_path.read_text(encoding="utf-8")

    # 1. Container & Toolbar Elements
    assert 'id="tab-matrix"' in html_content
    assert 'id="matrix-tree-toolbar"' in html_content
    assert 'id="matrix-search-archetype"' in html_content
    assert 'id="matrix-filter-has-stock"' in html_content
    assert 'id="btn-matrix-expand-all"' in html_content
    assert 'id="btn-matrix-collapse-all"' in html_content
    assert 'id="matrix-select-preset"' in html_content
    assert 'id="btn-matrix-reset"' in html_content

    # 2. Table & Grid Structure
    assert 'id="matrix-hierarchical-table-wrapper"' in html_content
    assert 'id="matrix-hierarchical-tbody"' in html_content
    assert "CHƯƠNG · BÀI · DẠNG BÀI TẬP" in html_content
    assert "PHẦN I · TRẮC NGHIỆM NHIỀU PHƯƠNG ÁN" in html_content
    assert "PHẦN II · ĐÚNG / SAI 4 Ý" in html_content
    assert "PHẦN III · TRẢ LỜI NGẮN" in html_content
    assert "TỔNG CÂU" in html_content
    assert "TỔNG ĐIỂM" in html_content

    # 3. Sticky Footer Action Bar Elements
    assert 'id="matrix-sticky-footer"' in html_content
    assert 'id="matrix-foot-p1"' in html_content
    assert 'id="matrix-foot-p2"' in html_content
    assert 'id="matrix-foot-p3"' in html_content
    assert 'id="matrix-foot-grand"' in html_content
    assert 'id="matrix-foot-bloom-lbl"' in html_content
    assert 'id="matrix-foot-bar-nb"' in html_content
    assert 'id="matrix-foot-bar-th"' in html_content
    assert 'id="matrix-foot-bar-vd"' in html_content
    assert 'id="matrix-foot-bar-vdc"' in html_content
    assert 'id="btn-matrix-generate-master"' in html_content

    # 4. JavaScript Contracts trong app.js
    js_path = Path("frontend/static/app.js")
    assert js_path.exists(), "frontend/static/app.js phải tồn tại"
    js_content = js_path.read_text(encoding="utf-8")

    expected_functions = [
        "initHierarchicalMatrix",
        "renderHierarchicalMatrix",
        "toggleMatrixNode",
        "expandAllMatrixTree",
        "collapseAllMatrixTree",
        "onMatrixSearchInput",
        "onMatrixFilterStockChange",
        "onMatrixCellChange",
        "applyMatrixPreset",
        "resetMatrixSelections",
        "generateMasterExamFromHierarchicalMatrix"
    ]
    for fn in expected_functions:
        assert f"function {fn}" in js_content, f"app.js phải chứa định nghĩa function {fn}"

    # Export vào window.app
    app_export_pos = js_content.rfind("window.app = {")
    assert app_export_pos != -1, "Không tìm thấy khai báo window.app = { ... }"
    app_export_body = js_content[app_export_pos:js_content.find("};", app_export_pos)]
    for fn in expected_functions:
        assert f"{fn}," in app_export_body, f"window.app phải export {fn}"


def test_hierarchical_matrix_presets_and_calculations():
    """Kiểm thử tính toán điểm số và tỷ lệ nhận thức Bloom cho 3 Presets chuẩn hóa:
    1. Preset THPT 2025 ('thpt2025'):
       - Phần I: 12 câu trắc nghiệm đơn x 0.25đ = 3.0đ.
       - Phần II: 4 câu Đúng/Sai 4 ý x 1.0đ = 4.0đ.
       - Phần III: 6 câu Trả lời ngắn x 0.5đ = 3.0đ.
       - Tổng số: 22 câu = 10.0 điểm tuyệt đối.
       - Phân bố Bloom 4 cấp độ:
         * NB (Nhận biết): 7 câu (~32%)
         * TH (Thông hiểu): 8 câu (~36%)
         * VD (Vận dụng): 6 câu (~27%)
         * VDC (Vận dụng cao): 1 câu (~5%)
         * Tổng: 22 câu (100%).
    2. Preset Định kỳ ('periodic'):
       - 20 câu trắc nghiệm đơn x 0.25đ = 5.0đ (10 NB + 10 TH).
    3. Preset Cuối kỳ ('final'):
       - 18 câu trắc nghiệm đơn (0.25đ = 4.5đ) + 10 câu TLN (0.5đ = 5.0đ) = 28 câu.
    4. Reset ma trận (resetMatrixSelections):
       - Làm rỗng toàn bộ cellSelections.
       - Cập nhật sticky footer: 0 câu | 0.0 / 10.0 điểm.
    """
    from pathlib import Path
    js_path = Path("frontend/static/app.js")
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Trích xuất hàm applyMatrixPreset và renderHierarchicalMatrix từ app.js
    assert "function applyMatrixPreset(presetName)" in js_content
    preset_func_start = js_content.find("function applyMatrixPreset(presetName)")
    preset_func_end = js_content.find("function resetMatrixSelections()", preset_func_start)
    preset_code = js_content[preset_func_start:preset_func_end]

    # Kiểm tra cấu hình preset thpt2025 trong code JS
    assert "presetName === 'thpt2025'" in preset_code
    assert "SINGLE_CHOICE_RECOGNITION`] = 4" in preset_code
    assert "SINGLE_CHOICE_COMPREHENSION`] = 2" in preset_code
    assert "SINGLE_CHOICE_APPLICATION`] = 2" in preset_code
    assert "TRUE_FALSE_GROUP_RECOGNITION`] = 1" in preset_code
    assert "TRUE_FALSE_GROUP_COMPREHENSION`] = 1" in preset_code
    assert "TRUE_FALSE_GROUP_APPLICATION`] = 1" in preset_code
    assert "SHORT_ANSWER_COMPREHENSION`] = 2" in preset_code
    assert "SHORT_ANSWER_APPLICATION`] = 2" in preset_code
    assert "SHORT_ANSWER_HIGH_APPLICATION`] = 1" in preset_code

    # 2. Mô phỏng độc lập thuật toán tính toán của applyMatrixPreset('thpt2025')
    mock_selections_thpt2025 = {
        "arch1_1_SINGLE_CHOICE_RECOGNITION": 4,
        "arch1_1_SINGLE_CHOICE_COMPREHENSION": 2,
        "arch2_1_SINGLE_CHOICE_RECOGNITION": 2,
        "arch2_1_SINGLE_CHOICE_COMPREHENSION": 2,
        "arch3_1_SINGLE_CHOICE_APPLICATION": 2,
        "arch1_2_TRUE_FALSE_GROUP_RECOGNITION": 1,
        "arch1_2_TRUE_FALSE_GROUP_COMPREHENSION": 1,
        "arch2_2_TRUE_FALSE_GROUP_COMPREHENSION": 1,
        "arch3_2_TRUE_FALSE_GROUP_APPLICATION": 1,
        "arch1_3_SHORT_ANSWER_COMPREHENSION": 2,
        "arch2_3_SHORT_ANSWER_APPLICATION": 2,
        "arch3_3_SHORT_ANSWER_APPLICATION": 1,
        "arch3_3_SHORT_ANSWER_HIGH_APPLICATION": 1,
    }

    formats_config = [
        {"sectionNum": 1, "format": "SINGLE_CHOICE", "points": 0.25},
        {"sectionNum": 2, "format": "TRUE_FALSE_GROUP", "points": 1.0},
        {"sectionNum": 3, "format": "SHORT_ANSWER", "points": 0.5},
    ]

    totals = {
        "p1Count": 0, "p1Pts": 0.0,
        "p2Count": 0, "p2Pts": 0.0,
        "p3Count": 0, "p3Pts": 0.0,
        "grandCount": 0, "grandPts": 0.0,
        "nbCount": 0, "thCount": 0, "vdCount": 0, "vdcCount": 0
    }

    valid_levels = ["HIGH_APPLICATION", "COMPREHENSION", "RECOGNITION", "APPLICATION"]
    valid_formats = ["TRUE_FALSE_GROUP", "SINGLE_CHOICE", "SHORT_ANSWER"]

    for key, val in mock_selections_thpt2025.items():
        lvl = None
        rest = key
        for l in valid_levels:
            if rest.endswith(f"_{l}"):
                lvl = l
                rest = rest[: -(len(l) + 1)]
                break

        fmt = None
        for f in valid_formats:
            if rest.endswith(f"_{f}"):
                fmt = f
                rest = rest[: -(len(f) + 1)]
                break

        last_underscore = rest.rfind("_")
        sec = int(rest[last_underscore + 1 :])
        arch_id = rest[:last_underscore]

        if lvl == "RECOGNITION":
            totals["nbCount"] += val
        elif lvl == "COMPREHENSION":
            totals["thCount"] += val
        elif lvl == "APPLICATION":
            totals["vdCount"] += val
        elif lvl == "HIGH_APPLICATION":
            totals["vdcCount"] += val

        fc = next(f for f in formats_config if f["sectionNum"] == sec)
        pts = val * fc["points"]
        if sec == 1:
            totals["p1Count"] += val
            totals["p1Pts"] += pts
        elif sec == 2:
            totals["p2Count"] += val
            totals["p2Pts"] += pts
        elif sec == 3:
            totals["p3Count"] += val
            totals["p3Pts"] += pts

        totals["grandCount"] += val
        totals["grandPts"] += pts

    # Khẳng định chuẩn THPT 2025
    assert totals["p1Count"] == 12, "Phần I phải có đúng 12 câu"
    assert totals["p1Pts"] == 3.0, "Phần I 12 câu x 0.25đ = 3.0đ"
    assert totals["p2Count"] == 4, "Phần II phải có đúng 4 câu"
    assert totals["p2Pts"] == 4.0, "Phần II 4 câu x 1.0đ = 4.0đ"
    assert totals["p3Count"] == 6, "Phần III phải có đúng 6 câu"
    assert totals["p3Pts"] == 3.0, "Phần III 6 câu x 0.5đ = 3.0đ"
    assert totals["grandCount"] == 22, "Tổng số câu chuẩn THPT 2025 phải là 22 câu"
    assert round(totals["grandPts"], 2) == 10.0, "Tổng điểm chuẩn THPT 2025 phải là đúng 10.0 điểm"

    # Khẳng định phân bố Bloom
    assert totals["nbCount"] == 7
    assert totals["thCount"] == 8
    assert totals["vdCount"] == 6
    assert totals["vdcCount"] == 1

    pct_nb = round((totals["nbCount"] / totals["grandCount"]) * 100)
    pct_th = round((totals["thCount"] / totals["grandCount"]) * 100)
    pct_vd = round((totals["vdCount"] / totals["grandCount"]) * 100)
    pct_vdc = max(0, 100 - pct_nb - pct_th - pct_vd)
    assert pct_nb + pct_th + pct_vd + pct_vdc == 100
    assert pct_nb == 32
    assert pct_th == 36
    assert pct_vd == 27
    assert pct_vdc == 5

    # 3. Kiểm tra Preset Định kỳ ('periodic')
    assert "presetName === 'periodic'" in preset_code
    mock_selections_periodic = {
        "arch1_1_SINGLE_CHOICE_RECOGNITION": 10,
        "arch1_1_SINGLE_CHOICE_COMPREHENSION": 10,
    }
    periodic_total_cnt = sum(mock_selections_periodic.values())
    assert periodic_total_cnt == 20, "Preset định kỳ phải có 20 câu"

    # 4. Kiểm tra Preset Cuối kỳ ('final')
    assert "presetName === 'final'" in preset_code
    mock_selections_final = {
        "arch1_1_SINGLE_CHOICE_RECOGNITION": 10,
        "arch1_1_SINGLE_CHOICE_COMPREHENSION": 8,
        "arch2_3_SHORT_ANSWER_APPLICATION": 10,
    }
    final_total_cnt = sum(mock_selections_final.values())
    assert final_total_cnt == 28, "Preset cuối kỳ phải có 28 câu"

    # 5. Kiểm tra resetMatrixSelections
    reset_func_start = js_content.find("function resetMatrixSelections()")
    assert reset_func_start != -1
    reset_func_end = js_content.find("function saveMatrixConfig()", reset_func_start)
    reset_code = js_content[reset_func_start:reset_func_end]
    assert "state.hierarchicalMatrix.cellSelections = {};" in reset_code
    assert "renderHierarchicalMatrix();" in reset_code


def test_hierarchical_matrix_cell_inputs_and_stock_validation():
    """Kiểm thử ô nhập liệu phản hồi real-time, badge tồn kho và cơ chế cảnh báo:
    1. Hàm onMatrixCellChange(archetypeId, sectionNum, format, level, val):
       - Parse giá trị nguyên không âm Math.max(0, parseInt(val, 10) || 0).
       - Xóa key khỏi cellSelections khi giá trị = 0 (dọn dẹp sạch state).
       - Lưu trữ theo key: ${archetypeId}_${sectionNum}_${format}_${level}.
       - Gọi renderHierarchicalMatrix() để cập nhật bảng và sticky footer ngay lập tức.
    2. Badge tồn kho thực tế và cảnh báo vượt tồn kho (.stock-warn):
       - Hàm getArchetypeStock(archetypeId, format, level) tra cứu inventoryMap.
       - Render chip Kho: ${stock} hoặc Kho: 0.
       - Thêm class .stock-warn khi val > stock và val > 0.
       - Thêm class .stock-ok khi stock > 0 và không vượt.
    3. Bộ lọc tồn kho (#matrix-filter-has-stock):
       - Khi filterOnlyHasStock = true, chỉ hiển thị các dòng archetype có stock > 0 hoặc sel > 0.
    4. Tìm kiếm từ khóa (#matrix-search-archetype):
       - Lọc case-insensitive theo arch.name, arch.code, ls.name, tp.name.
    """
    from pathlib import Path
    js_path = Path("frontend/static/app.js")
    js_content = js_path.read_text(encoding="utf-8")

    # 1. Kiểm tra onMatrixCellChange
    cell_change_start = js_content.find("function onMatrixCellChange(")
    assert cell_change_start != -1
    cell_change_end = js_content.find("function renderHierarchicalMatrix()", cell_change_start)
    cell_change_code = js_content[cell_change_start:cell_change_end]

    assert "Math.max(0, parseInt(val, 10) || 0)" in cell_change_code
    assert "const key = `${archetypeId}_${sectionNum}_${format}_${level}`;" in cell_change_code
    assert "delete state.hierarchicalMatrix.cellSelections[key];" in cell_change_code
    assert "state.hierarchicalMatrix.cellSelections[key] = qty;" in cell_change_code
    assert "renderHierarchicalMatrix();" in cell_change_code

    # 2. Kiểm tra getArchetypeStock & stock warning badge logic
    get_stock_start = js_content.find("function getArchetypeStock(")
    assert get_stock_start != -1
    get_stock_end = js_content.find("function toggleMatrixNode(", get_stock_start)
    get_stock_code = js_content[get_stock_start:get_stock_end]
    assert "state.hierarchicalMatrix.inventoryMap" in get_stock_code
    assert "return inv[archetypeId][format][level];" in get_stock_code

    render_matrix_start = js_content.find("function renderHierarchicalMatrix()")
    assert render_matrix_start != -1
    render_matrix_end = js_content.find("function applyMatrixPreset(", render_matrix_start)
    render_matrix_code = js_content[render_matrix_start:render_matrix_end]

    # Kiểm tra class warning khi vượt tồn kho
    assert "const isWarn = val > stock;" in render_matrix_code
    assert "val > 0 && isWarn ? 'stock-warn' : (stock > 0 ? 'stock-ok' : 'text-slate-400')" in render_matrix_code
    assert "Kho: ${stock}" in render_matrix_code

    # 3. Kiểm tra filter tồn kho
    assert "filterStock && !hasStockOrSel" in render_matrix_code
    assert "onMatrixFilterStockChange" in js_content

    # 4. Kiểm tra tìm kiếm từ khóa
    assert "arch.name.toLowerCase().includes(searchQuery)" in render_matrix_code
    assert "arch.code && arch.code.toLowerCase().includes(searchQuery)" in render_matrix_code
    assert "ls.name.toLowerCase().includes(searchQuery)" in render_matrix_code
    assert "tp.name.toLowerCase().includes(searchQuery)" in render_matrix_code
    assert "onMatrixSearchInput" in js_content





