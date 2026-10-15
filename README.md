# QUESY: HỆ THỐNG QUẢN LÝ ĐỀ THI & NGÂN HÀNG CÂU HỎI TÍCH HỢP AI SỐ HOÁ

> **Chuẩn hóa 100% theo Thông tư số 32/2018/TT-BGDĐT (Chương trình GDPT 2018), Thông tư số 22/2021/TT-BGDĐT và Quyết định số 764/QĐ-BGDĐT (Định dạng đề thi tốt nghiệp THPT từ năm 2025).**

---

## 1. TỔNG QUAN HỆ THỐNG

**Quesy** là hệ sinh thái khảo thí thông minh phục vụ công tác quản lý đề thi và ngân hàng câu hỏi chuẩn hóa đánh giá năng lực:
1. **AI Ingestion & Parsing:** Tự động số hóa đề thi từ file Word (`.docx`), PDF hoặc ảnh scan, giải mã nhị phân MathType sang chuỗi **LaTeX chuẩn**, tự động phát hiện Bounding Box đồ thị hàm số và hình học không gian để auto-crop nén WebP.
2. **Cây Kiến thức 6 Tầng Chuẩn hóa:** Bám sát Thông tư 32/2018/TT-BGDĐT:
   $$\text{Cấp/Khối} \longrightarrow \text{Môn học} \longrightarrow \text{Mạch nội dung} \longrightarrow \text{Chủ đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{YCCĐ\ (Yêu\ cầu\ cần\ đạt)} \longrightarrow \mathbf{Dạng\ câu\ hỏi}$$
   *Tuyệt đối không phân chia theo bộ sách giáo khoa.*
3. **Studio Hậu kiểm Đối chiếu Song song (HITL):** Màn hình 2 cột (Viewer tài liệu gốc bên trái $\leftrightarrow$ Card câu hỏi KaTeX bên phải), hỗ trợ **Synchronized Scrolling**, gợi ý AI Auto-tagging YCCĐ, sửa nhanh công thức và đổi đáp án chỉ bằng 1 click.
4. **Hỗ trợ Đầy đủ Định dạng Đề thi Mới (Format 2025):**
   - Phần I: Trắc nghiệm 4 lựa chọn (A, B, C, D).
   - Phần II: Trắc nghiệm Đúng/Sai 4 khẳng định có **tính điểm bậc thang** (RULE-01: Đúng 1 ý = 0.1đ; 2 ý = 0.25đ; 3 ý = 0.5đ; 4 ý = 1.0đ).
   - Phần III: Trắc nghiệm Trả lời ngắn.
   - Thể thức Câu hỏi chùm (Passage-based) và Tự luận (Essay).
5. **Thuật toán Trộn Đề An Toàn (Safe Shuffling Engine):**
   - **Section Integrity:** Chỉ hoán vị trong từng phần thi.
   - **Passage Integrity:** Giữ nguyên bài đọc chung và các câu con liên tiếp.
   - **Option Anchor (RULE-02):** Khóa cố định các phương án chứa "Cả A và B", "Tất cả các ý trên" ở vị trí cuối cùng (D).
   - Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu giữa các mã đề hoán vị.
6. **Xuất bản Đa Định dạng:** Tạo file Word `.docx` 2 cột chuẩn mẫu in ấn của Bộ GD&ĐT với công thức Toán dạng **Microsoft Word OMML native**, đi kèm phiếu soi đáp án OMR và file lời giải chi tiết đóng gói trong file ZIP.

---

## 2. KIẾN TRÚC KỸ THUẬT

```
quesy/
├── backend/
│   ├── config.py              # Cấu hình môi trường và đường dẫn lưu trữ
│   ├── database.py            # Kết nối SQLAlchemy engine & session factory
│   ├── models.py              # ORM models (Taxonomy 6 tầng, Questions, Exams, Matrices, Jobs)
│   ├── schemas.py             # Pydantic v2 schemas xác thực dữ liệu vào/ra
│   ├── seed_data.py           # Dữ liệu mẫu chuẩn Thông tư 32 môn Toán 12
│   ├── main.py                # FastAPI app với CORS, Static mounts & Routers
│   ├── routers/
│   │   ├── taxonomy.py        # API cây kiến thức 6 tầng theo TT 32
│   │   ├── questions.py       # API CRUD câu hỏi, kiểm tra trùng lặp AI Vector
│   │   ├── digitize.py        # API Upload đề, AI Parsing pipeline & commit
│   │   ├── matrix.py          # API thiết lập Ma trận đề thi 2 chiều
│   │   └── exams.py           # API sinh MasterExam, hoán vị mã đề an toàn, xuất ZIP & analytics
│   └── services/
│       ├── ai_parser.py       # Pipeline bóc tách đề thi (DOCX/PDF/Image)
│       ├── latex_converter.py # Giải mã MathType MTEF sang LaTeX, KaTeX sanitizer
│       ├── crop_service.py    # Auto-crop hình học/đồ thị lưu WebP
│       ├── tagging_service.py # AI Auto-tagging YCCĐ & Cosine similarity deduplication
│       ├── matrix_solver.py   # Rút câu hỏi theo ma trận ràng buộc YCCĐ
│       ├── shuffling_engine.py# Trộn đề an toàn (Section, Passage, Option Anchor)
│       └── docx_exporter.py   # Xuất bản Word 2 cột OMML & đóng gói ZIP
├── frontend/
│   ├── index.html             # Single Page Application (TailwindCSS, KaTeX, Lucide Icons)
│   └── static/
│       ├── app.js             # State management, API integration, HITL Studio, Matrix Builder
│       └── style.css          # Giao diện responsive chuyên nghiệp
├── docs/                      # Bộ tài liệu đặc tả kỹ thuật v2.0
│   ├── BRD_Exam_Management_AI_Digitization.md  # Business Requirements Document v2.0
│   ├── SRS_System_Requirements_Specification.md # System Requirements Specification v2.0
│   ├── FRD_Functional_Requirements_Document.md  # Functional Requirements Document v2.0
│   ├── UC_Use_Case_Specifications.md           # Use Case Specifications v2.0
│   ├── NFR_Non_Functional_Requirements.md       # Non-Functional Requirements v2.0
│   ├── FS_Feasibility_Study_Report.md           # Feasibility Study & ROI Report v2.0
│   └── TEST_Test_Cases_Specification.md         # Test Cases Specification v2.0
├── tests/                     # 24 kịch bản kiểm thử tự động (Pytest)
│   ├── test_taxonomy.py
│   ├── test_rules_shuffling.py
│   ├── test_deduplication.py
│   ├── test_docx_export.py
│   ├── test_api_endpoints.py
│   ├── test_ai_pipeline.py
│   └── test_services.py
├── storage/                   # Thư mục lưu trữ tài nguyên
│   ├── uploads/               # File đề thi gốc tải lên
│   ├── assets/                # Ảnh đồ thị/hình học cắt ra dạng WebP
│   └── exports/               # File đề Word và gói ZIP xuất bản
└── start_server.py            # Script khởi động trọn gói hệ thống
```

---

## 3. HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG

### 3.1. Cài đặt Môi trường
Hệ thống sử dụng Python 3.10+ (Đã kiểm thử và chạy ổn định trên Python 3.13):

```bash
pip install fastapi uvicorn python-docx pydantic jinja2 python-multipart pytest httpx pypdf Pillow
```

### 3.2. Khởi động Hệ thống
Chạy lệnh duy nhất để tự động khởi tạo bảng CSDL, nạp dữ liệu mẫu Thông tư 32 và khởi động máy chủ Web:

```bash
python start_server.py
```

Sau khi khởi động:
- **Ứng dụng Web Studio:** Mở trình duyệt truy cập `http://127.0.0.1:8000`
- **Tài liệu Swagger API:** `http://127.0.0.1:8000/docs`
- **Kiểm tra sức khỏe hệ thống (Health Check):** `http://127.0.0.1:8000/health`

---

## 4. CHẠY KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUITE)

Hệ thống đi kèm **24 kịch bản kiểm thử tự động (100% PASS)** bao phủ toàn bộ các quy tắc nghiệp vụ cốt lõi:

```bash
pytest -v
```

Kết quả kiểm thử thực tế:
- `test_taxonomy.py`: Xác minh cấu trúc 6 tầng, mã YCCĐ, và tuyệt đối **không tồn tại trường "Bộ sách"** (PASS).
- `test_rules_shuffling.py`:
  - **RULE-01:** Kiểm thử toàn bộ 16 tổ hợp Đúng/Sai 4 ý tính điểm bậc thang (PASS).
  - **RULE-02:** Chạy 100 lần hoán vị mã đề, đảm bảo phương án "Cả A và B đều đúng" **luôn khóa ở vị trí D trong 100% mã đề** (PASS).
  - **RULE-03:** Đảm bảo câu hỏi chùm và bài đọc không bị phân tách trong mọi mã đề (PASS).
- `test_deduplication.py`: Xác minh thuật toán Cosine Similarity chặn lưu và cảnh báo khi câu hỏi trùng lặp $\ge 0.90$ (PASS).
- `test_docx_export.py`: Kiểm tra xuất file Word 2 cột với công thức toán và header chuẩn (PASS).
- `test_ai_pipeline.py`: Kiểm thử chuyển đổi LaTeX, trích xuất hình học và auto-tagging (PASS).
- `test_api_endpoints.py`: Kiểm thử tích hợp toàn bộ API qua FastAPI TestClient (PASS).
