# BẢN ĐỒ MÃ NGUỒN & KIẾN TRÚC HỆ THỐNG CHI TIẾT (QUESY SOURCE MAP)

> **Dự án:** Quesy - Nền tảng Quản trị Khảo thí, Soạn đề & Số hóa Đề thi Chuẩn Quốc gia  
> **Chuẩn Khảo thí:** Thông tư 32/2018/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT (Định dạng Đề thi 2025)  
> **Trạng thái mã nguồn:** Đạt 100% kiểm thử tự động (129/129 test cases PASSED)  
> **Cập nhật lần cuối:** Tháng 10/2026  

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE OVERVIEW)

Quesy được xây dựng theo kiến trúc **Module-based Monolith** kết hợp **External Compiling Microservices**, phân tách rõ ràng 4 tầng:
1. **Frontend Presentation & Micro-interaction Layer:** Single Page Application (SPA) điều hướng sạch (`/path`), tuân thủ Apple HIG và tương tác Emil Kowalski (phản hồi xúc giác 0.97, Dark Code Editor `#141824`, Live PDF Preview).
2. **API Gateway & Routing Layer:** FastAPI (Python 3.13) bất đồng bộ, tự động validate Pydantic V2 schemas, bảo toàn route SPA tránh lỗi 404 khi F5.
3. **Core Domain Services & Processing Pipelines:**
   - *Soạn đề & Biên dịch Hybrid:* `composer_service.py` kết nối Remote Tectonic XeTeX Engine Docker (host `armbian:8090`), gói lệnh chuẩn quốc gia `ex_test.sty` (v3.3.6), động cơ Canonical Preamble Injection (tự động nhúng ngầm fontspec, amsmath, tikz, tkz-tab, tcolorbox, xparse, ex_test v3.3, geometry A4), hỗ trợ ô soạn thảo tinh gọn Preamble-Free Question Editor, và AI Inline Diff Replacer.
   - *Số hóa 2-Pass AI Decoupled:* Tiền xử lý ảnh OpenCV/Pillow, phân đoạn layout, Pass 1 trích xuất văn bản/đáp án, Pass 2 dựng mã TikZ/Array song song.
   - *Xuất bản MathType OLE Word & CMU Serif PDF:* Dựng luồng nhị phân CFB MTEF v5 + ảnh vector WMF (APM header chuẩn) sửa 2 chiều trong Microsoft Word; chuyển đổi bảng biến thiên sang `<w:tbl>` native.
   - *Ma trận & Trộn đề An toàn:* Giải bài toán ma trận 2 chiều theo YCCĐ, hoán vị mã đề an toàn, tính điểm Đúng/Sai lũy tiến theo QĐ 764.
4. **Data Persistence & Storage Layer:**
   - Cơ sở dữ liệu: SQLite / PostgreSQL quản trị qua SQLAlchemy ORM (19 thực thể chuẩn hóa).
   - Hệ thống đĩa đệm (Storage): `storage/uploads/` (tệp đề thi), `storage/assets/` (hình ảnh trích xuất WebP), `storage/cache/mathjax/` (đệm WMF/SVG), `storage/cache/composer/` (đệm PDF biên dịch).

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TRÌNH DUYỆT NGƯỜI DÙNG (FRONTEND SPA)                           │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌────────────────────────┐  │
│  │   Soạn đề (Composer)    │  │   Ngân hàng câu hỏi     │  │   Số hóa AI (2-Pass)   │  │
│  │  - Dark Editor #141824  │  │  - Cây kiến thức 6 tầng │  │  - OpenCV Deskew/CLAHE │  │
│  │  - AI Inline Diff       │  │  - Xem trước KaTeX/TikZ │  │  - WebP Crop Assets    │  │
│  │  - Live PDF Preview     │  │  - Lọc YCCĐ / Mức độ    │  │  - Pass 1 & Pass 2     │  │
│  └───────────┬─────────────┘  └───────────┬─────────────┘  └───────────┬────────────┘  │
│              │                            │                            │               │
│  ┌───────────┴─────────────┐  ┌───────────┴─────────────┐              │               │
│  │   Ma trận đề (Matrix)   │  │   Trộn đề (Shuffler)    │              │               │
│  │  - 2 Chiều YCCĐ x Mức độ│  │  - Safe Shuffling       │              │               │
│  │  - Constraint Solver    │  │  - Chấm Đúng/Sai QĐ 764 │              │               │
│  └───────────┬─────────────┘  └───────────┬─────────────┘              │               │
└──────────────┼────────────────────────────┼────────────────────────────┼───────────────┘
               │ HTTP / JSON REST API       │                            │
┌──────────────▼────────────────────────────▼────────────────────────────▼───────────────┐
│                           FASTAPI BACKEND GATEWAY (CỔNG 8000)                          │
│   /api/v1/composer      /api/v1/taxonomy      /api/v1/questions      /api/v1/digitize  │
│   /api/v1/matrix        /api/v1/exams         /dashboard, /composer... (SPA Fallback)  │
└──────┬──────────────────┬─────────────────┬─────────────────┬──────────────────┬───────┘
       │                  │                 │                 │                  │
┌──────▼───────┐   ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐   ┌──────▼───────┐
│ COMPOSER     │   │ 2-PASS AI    │  │ DOCX EXPORT  │  │ LATEX PDF    │   │ MATRIX &     │
│ ENGINE       │   │ DIGITIZER    │  │ MATHTYPE OLE │  │ EXPORTER     │   │ SHUFFLER     │
│ - ex_test.sty│   │ - OpenCV     │  │ - CFB MTEF v5│  │ - CMU Serif  │   │ - QĐ 764     │
│ - Tectonic   │   │ - Crop WebP  │  │ - APM WMF    │  │ - Full dfrac │   │ - Anchoring  │
│ - Diff Repl. │   │ - Pass 1 & 2 │  │ - <w:tbl>    │  │ - Tight Pad  │   │ - Key Matrix │
└──────┬───────┘   └──────────────┘  └──────┬───────┘  └──────┬───────┘   └──────────────┘
       │                                    │                 │
       │                               ┌────▼─────────────────▼────┐
       │                               │ PERSISTENT MATHJAX WORKER │
       │                               │ - Node.js Daemon (IPC)    │
       │                               │ - ~14ms / equation        │
       │                               └───────────────────────────┘
┌──────▼─────────────────────────────────────────────────┐
│       HẠ TẦNG BIÊN DỊCH TECTONIC DOCKER MICROSERVICE   │
│  - Host: armbian (Port 8090, http://armbian:8090/compile)│
│  - XeTeX Engine aarch64 + Persistent CTAN Cache        │
│  - Gói ex_test.sty v3.3.6 mount cố định               │
└────────────────────────────────────────────────────────┘
```

---

## 2. BẢN ĐỒ CÂY THƯ MỤC & FILE INVENTORY

Tổng số dòng mã nguồn (Lines of Code - LOC): **~26,000 dòng**.

```
quesy/
├── AGENTS.md                          # Quy chuẩn & standing rules dành cho Agent (37 dòng)
├── README.md                          # Tài liệu giới thiệu & năng lực cốt lõi hệ thống (274 dòng)
├── requirements.txt                   # Danh mục thư viện Python dependencies (23 dòng)
├── package.json                       # Cấu hình MathJax Node.js daemon (9 dòng)
├── pytest.ini                         # Cấu hình kiểm thử tự động pytest (4 dòng)
├── start_server.py                    # Trình khởi động server thông minh, auto-kill & failover port (138 dòng)
├── docker-compose.yml                 # Cấu hình triển khai Tectonic XeTeX container (17 dòng)
│
├── backend/                           # Mã nguồn lõi Backend (FastAPI, SQLAlchemy, Services)
│   ├── config.py                      # Cấu hình hệ thống, biến môi trường, đường dẫn storage (103 dòng)
│   ├── database.py                    # Kết nối DB Engine, SessionLocal, Dependency get_db (48 dòng)
│   ├── main.py                        # Khởi tạo FastAPI app, middleware CORS, mount SPA routes (204 dòng)
│   ├── models.py                      # 19 thực thể CSDL SQLAlchemy ORM chuẩn hóa (490 dòng)
│   ├── schemas.py                     # Pydantic V2 data validation schemas (597 dòng)
│   ├── seed_data.py                   # Bộ dữ liệu mẫu ngân hàng câu hỏi & cây TT 32 (1,122 dòng)
│   │
│   ├── routers/                       # Tầng Controller & API Endpoints
│   │   ├── composer.py                # API Soạn đề LaTeX, Tectonic compile, AI Diff Copilot (479 dòng)
│   │   ├── digitize.py                # API Số hóa đề thi 2-Pass, quản lý tiến trình, cắt ảnh (755 dòng)
│   │   ├── exams.py                   # API Tạo đề thi gốc, quản lý mã đề hoán vị, chấm thi (434 dòng)
│   │   ├── matrix.py                  # API Ma trận đặc tả đề thi theo YCCĐ (215 dòng)
│   │   ├── questions.py               # API Ngân hàng câu hỏi CRUD, preview công thức, lọc (387 dòng)
│   │   └── taxonomy.py                # API Cây phân cấp kiến thức 6 tầng theo TT 32 (445 dòng)
│   │
│   ├── services/                      # Tầng Domain Business Logic & Processing Engines
│   │   ├── ai_parser.py               # Engine số hóa đề thi thông minh (Pass 1 Text + Pass 2 TikZ) (918 dòng)
│   │   ├── ai_provider_service.py     # Adapter kết nối đa nhà cung cấp AI (Gemini, OpenAI...) (833 dòng)
│   │   ├── composer_service.py        # Dịch vụ biên dịch LaTeX Hybrid 3 tầng & bóc tách ex_test (955 dòng)
│   │   ├── crop_service.py            # Dịch vụ cắt và trích xuất ảnh đồ thị/bảng WebP (399 dòng)
│   │   ├── deduplication.py           # Dịch vụ kiểm soát trùng lặp câu hỏi qua Vector Similarity (97 dòng)
│   │   ├── docx_exporter.py           # Engine xuất bản Word MathType 7.0 OLE Vector WMF thuần Python (2,977 dòng)
│   │   ├── docx_export.py             # Dịch vụ tạo tài liệu Word bổ trợ (220 dòng)
│   │   ├── excel_exporter.py          # Xuất bản danh sách thí sinh và bảng điểm Excel (121 dòng)
│   │   ├── grading.py                 # Hàm tính điểm Đúng/Sai lũy tiến theo QĐ 764 (15 dòng)
│   │   ├── image_enhancer.py          # Tiền xử lý ảnh: Deskew OpenCV, CLAHE, Binarization (324 dòng)
│   │   ├── latex_converter.py         # Chuyển đổi công thức Toán, mảng Array sang TikZ tkz-tab (1,459 dòng)
│   │   ├── latex_pdf_exporter.py      # Xuất bản PDF chuẩn LaTeX 100% CMU Serif & dfrac đầy đủ (750 dòng)
│   │   ├── layout_segmenter.py        # Phân đoạn bố cục đề thi, nhận diện bảng và vùng hình ảnh (365 dòng)
│   │   ├── mathjax_service.py         # Client giao tiếp với persistent Node.js MathJax worker (249 dòng)
│   │   ├── mathjax_worker.js          # Persistent worker Node.js biên dịch TeX sang SVG/MTEF (192 dòng)
│   │   ├── matrix_solver.py           # Thuật toán thỏa mãn ràng buộc ma trận sinh đề (272 dòng)
│   │   ├── shuffling.py               # Quy tắc hoán vị câu hỏi an toàn (212 dòng)
│   │   ├── shuffling_engine.py        # Động cơ trộn mã đề hoàn chỉnh, neo đáp án, xuất ma trận key (296 dòng)
│   │   ├── tagging_service.py         # Gợi ý tự động gán nhãn YCCĐ & mức độ nhận thức (609 dòng)
│   │   └── tikz_renderer.py           # Render mã TikZ sang ảnh SVG standalone (303 dòng)
│   │
│   └── templates/
│       └── ex_test.sty                # Gói lệnh khảo thí chuẩn Việt Nam v3.3.6 (4,258 dòng)
│
├── frontend/                          # Giao diện Người dùng Web Client (SPA)
│   ├── index.html                     # Trang khung HTML5 duy nhất chứa 6 màn hình chức năng (1,499 dòng)
│   ├── manifest.json                  # Cấu hình PWA Web App Manifest (16 dòng)
│   ├── sw.js                          # Service Worker cache tĩnh (65 dòng)
│   └── static/
│       ├── app.js                     # Toàn bộ logic Client SPA, State Store, Event Handlers (4,991 dòng)
│       ├── style.css                  # Toàn bộ CSS giao diện, Apple HIG, Dark Code Editor (631 dòng)
│       └── fonts/                     # Thư mục font chữ dự án
│
├── docs/                              # Toàn bộ tài liệu chuẩn hóa kỹ thuật dự án
│   ├── SRS_System_Requirements_Specification.md     # Đặc tả Yêu cầu Hệ thống Phần mềm (270 dòng)
│   ├── FRD_Functional_Requirements_Document.md      # Tài liệu Đặc tả Yêu cầu Chức năng (282 dòng)
│   ├── BRD_Exam_Management_AI_Digitization.md       # Tài liệu Yêu cầu Nghiệp vụ (167 dòng)
│   ├── NFR_Non_Functional_Requirements.md           # Đặc tả Yêu cầu Phi Chức năng (117 dòng)
│   ├── TEST_Test_Cases_Specification.md             # Bộ hồ sơ 9 Test Suites kiểm thử tự động (264 dòng)
│   ├── UC_Use_Case_Specifications.md                # Đặc tả 8 Use Cases người dùng chuẩn (228 dòng)
│   ├── GUIDELINE_EX_TEST.md                         # Cẩm nang hướng dẫn soạn thảo ex_test.sty (187 dòng)
│   ├── FS_Feasibility_Study_Report.md               # Báo cáo Nghiên cứu Khả thi Kỹ thuật (139 dòng)
│   ├── GITHUB_PROJECT_KANBAN_REPORT.md              # Báo cáo tiến độ Kanban dự án (145 dòng)
│   ├── TEST_LOOP_COMPREHENSIVE_REPORT.md            # Báo cáo nghiệm thu kiểm thử hồi quy (110 dòng)
│   └── BAO_CAO_YEU_CAU_VA_CHUC_NANG_PHAN_MEM_QUESY.md # Báo cáo tổng thể yêu cầu phần mềm (331 dòng)
│
├── tests/                             # Bộ kiểm thử tự động toàn diện (Pytest Test Suite)
│   ├── factories.py                   # Factory dữ liệu giả lập cho test cases (143 dòng)
│   ├── test_ai_pipeline.py            # Kiểm thử pipeline AI bóc tách (548 dòng)
│   ├── test_api_contracts_and_negatives.py # Kiểm thử hợp đồng API & trường hợp biên âm tính (276 dòng)
│   ├── test_api_endpoints.py          # Kiểm thử các API endpoints cốt lõi (256 dòng)
│   ├── test_cloud_vision_adapter.py   # Kiểm thử adapter cloud vision (97 dòng)
│   ├── test_composer.py               # Kiểm thử Soạn đề, Tectonic compile, AI Inline Diff, Chat API Contract (1550+ dòng)
│   ├── test_deduplication.py          # Kiểm thử lọc trùng câu hỏi (84 dòng)
│   ├── test_digitize_2pass.py         # Kiểm thử pipeline 2-Pass số hóa (273 dòng)
│   ├── test_digitize_docx_export.py   # Kiểm thử xuất Word từ dữ liệu số hóa (91 dòng)
│   ├── test_docx_export.py            # Kiểm thử xuất bản Word chuẩn MathType OLE (112 dòng)
│   ├── test_e2e_workflow.py           # Kiểm thử luồng khép kín End-to-End từ đề thi đến chấm điểm (251 dòng)
│   ├── test_excel_roster_import_export.py # Kiểm thử nạp/xuất danh sách thí sinh Excel (54 dòng)
│   ├── test_math_format_export.py     # Kiểm thử định dạng toán học OMML/MathType (85 dòng)
│   ├── test_mathjax_service.py        # Kiểm thử persistent worker MathJax (86 dòng)
│   ├── test_performance_budgets.py    # Kiểm nghiệm ngân sách thời gian xử lý < 10s (112 dòng)
│   ├── test_rules_shuffling.py        # Kiểm thử quy tắc hoán vị mã đề an toàn (187 dòng)
│   ├── test_services.py               # Kiểm thử các dịch vụ xử lý ảnh & layout (465 dòng)
│   ├── test_taxonomy.py               # Kiểm thử cây kiến thức 6 tầng TT 32 (175 dòng)
│   └── comprehensive_loop_test.py     # Script kiểm thử vòng lặp toàn diện (664 dòng)
│
└── .github/workflows/
    └── ci.yml                         # Quy trình CI/CD GitHub Actions trên Ubuntu runner (Strict CI Isolation: Độc quyền Sub-Agent 3, cấm các Sub-Agent khác đọc/ghi)
```

---

## 3. BẢN ĐỒ CƠ SỞ DỮ LIỆU & QUAN HỆ THỰC THỂ (ERD MAP)

Hệ thống quản lý **19 thực thể** chia thành 4 nhóm nghiệp vụ:

### 3.1. Nhóm Cây Kiến Thức (Taxonomy - Chuẩn TT 32/2018)
1. **`Subject` (Môn học):** Mã môn (`TOAN`, `VATLI`...), tên môn, trạng thái.
2. **`Grade` (Khối lớp):** Cấp học, khối (`10`, `11`, `12`).
3. **`Strand` (Mạch nội dung):** Đại số & Giải tích, Hình học & Đo lường, Thống kê & Xác suất...
4. **`Topic` (Chủ đề / Chuyên đề):** Ứng dụng đạo hàm, Tọa độ không gian...
5. **`Lesson` (Bài học):** Đơn vị bài học cụ thể.
6. **`LearningOutcome` (YCCĐ):** Yêu cầu cần đạt chuẩn quốc gia (`TOAN12.GT.01`).
7. **`ProblemArchetype` (Dạng câu hỏi):** Dạng bài toán cụ thể gắn dưới YCCĐ.

### 3.2. Nhóm Ngân Hàng Câu Hỏi & Số Hóa
8. **`Question` (Câu hỏi):**
   - Loại câu hỏi: `MULTIPLE_CHOICE` (Phần I), `TRUE_FALSE` (Phần II), `SHORT_ANSWER` (Phần III), `ESSAY` (Tự luận).
   - Nội dung LaTeX, lời giải, hình ảnh trích xuất (`[IMAGE:url]`), độ khó (`KNOW`, `UNDERSTAND`, `APPLY`).
   - Khóa ngoại liên kết `learning_outcome_id`, `archetype_id`.
9. **`QuestionOption` (Phương án trắc nghiệm):** Nhãn (`A`, `B`, `C`, `D`), nội dung LaTeX, cờ `is_correct`, cờ `is_fixed` (chống xáo trộn phương án vị trí cố định).
10. **`SubStatement` (Khẳng định Đúng/Sai - QĐ 764):** Khẳng định (`a`, `b`, `c`, `d`), cờ `is_correct`, giải thích chi tiết `itemch`.
11. **`AIDigitizeJob` (Tiến trình số hóa):** Trạng thái (`PENDING`, `PROCESSING`, `EXTRACTED`, `FAILED`), điểm tự tin `confidence_score`, tệp nguồn, danh sách câu hỏi bóc tách JSON tạm thời.

### 3.3. Nhóm Ma Trận & Đề Thi
12. **`ExamMatrix` (Ma trận đề thi):** Tên ma trận, khối lớp, môn học, thời gian làm bài, tổng điểm.
13. **`ExamMatrixItem` (Chi tiết ô ma trận):** Chỉ định YCCĐ, dạng câu hỏi, mức độ nhận thức, dạng thức trắc nghiệm và số lượng câu/điểm số.
14. **`MasterExam` (Đề thi gốc):** Đề thi chính thức được sinh từ ma trận hoặc nhập từ bên ngoài.
15. **`MasterExamItem` (Câu hỏi trong đề gốc):** Thứ tự câu hỏi trong đề gốc.
16. **`ExamVariant` (Mã đề hoán vị):** Mã đề (ví dụ: `101`, `102`, `103`, `104`), ma trận đáp án `key_matrix`.
17. **`ExamVariantItem` (Chi tiết câu hỏi mã đề):** Thứ tự câu hỏi hoán vị và thứ tự đảo các phương án trắc nghiệm.

### 3.4. Nhóm Khảo Thí & Đánh Giá
18. **`Classroom` (Lớp học / Phòng thi):** Quản lý danh sách lớp.
19. **`Student` (Thí sinh & Điểm số):** Họ tên, SBD, mã đề đã làm, điểm số Phần I, II (lũy tiến), III, và tổng điểm.

---

## 4. BẢN ĐỒ API ENDPOINTS (API ROUTE MATRIX)

| Phương thức | Đường dẫn API | Chức năng nghiệp vụ | Router Module |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/composer/compile` | Biên dịch mã LaTeX sang Live PDF Preview (hỗ trợ Preamble-Free Question Editor, Canonical Preamble Injection, mode: dethi/loigiai) | `composer.py` |
| **POST** | `/api/v1/composer/chat` | AI Copilot hỗ trợ soạn thảo, chẩn đoán log lỗi biên dịch LaTeX (compile_error_log), đề xuất Smart Inline Diff | `composer.py` |
| **GET** | `/api/v1/composer/pdf/{doc_id}.pdf` | Stream trực tiếp tệp PDF xem trước | `composer.py` |
| **GET** | `/api/v1/composer/templates` | Danh mục mẫu đề thi chuẩn quốc gia (`ex_test.sty` v3.3) | `composer.py` |
| **POST/GET** | `/api/v1/composer/export` | Xuất file .tex độc lập hoàn chỉnh có canonical preamble chuẩn in ấn | `composer.py` |
| **POST** | `/api/v1/composer/save-to-bank` | Trích xuất 1-Click câu hỏi `\begin{ex}` sang Ngân hàng | `composer.py` |
| **POST** | `/api/v1/digitize/upload-document`| Tải lên tệp đề thi (PDF, DOCX, Ảnh) chạy pipeline số hóa | `digitize.py` |
| **POST** | `/api/v1/digitize/upload-test`| Tải lên kiểm thử nhanh luồng 2-Pass Decoupled AI | `digitize.py` |
| **GET** | `/api/v1/digitize/jobs/{job_id}` | Lấy trạng thái, tiến độ thời gian thực (0-100%) và kết quả | `digitize.py` |
| **GET** | `/api/v1/digitize/assets/{file}` | Phục vụ tệp ảnh cắt trích xuất (WebP/JPEG) | `digitize.py` |
| **POST** | `/api/v1/digitize/commit-to-bank`| Xác nhận lưu câu hỏi sau hậu kiểm vào Ngân hàng | `digitize.py` |
| **GET** | `/api/v1/questions` | Tra cứu, tìm kiếm, lọc câu hỏi theo cây kiến thức | `questions.py` |
| **POST** | `/api/v1/questions` | Thêm mới câu hỏi thủ công | `questions.py` |
| **PUT** | `/api/v1/questions/{id}` | Chỉnh sửa nội dung câu hỏi, phương án, khẳng định Đ/S | `questions.py` |
| **DELETE**| `/api/v1/questions/{id}` | Xóa câu hỏi khỏi ngân hàng | `questions.py` |
| **GET** | `/api/v1/taxonomy/tree` | Lấy toàn bộ cây kiến thức phân cấp 6 tầng theo TT 32 | `taxonomy.py` |
| **POST** | `/api/v1/matrix` | Tạo ma trận đặc tả đề thi theo YCCĐ | `matrix.py` |
| **POST** | `/api/v1/matrix/{id}/generate` | Thuật toán sinh đề thi gốc từ ma trận | `matrix.py` |
| **POST** | `/api/v1/exams/{id}/shuffle` | Hoán vị $N$ mã đề an toàn, xuất phiếu soi đáp án | `exams.py` |
| **POST** | `/api/v1/exams/{id}/export-pdf` | Xuất bản file PDF vector 100% CMU Serif / Times New Roman | `exams.py` |
| **GET**  | `/api/v1/exams/{id}/export-zip` | Đóng gói trọn bộ ấn phẩm PDF (Đề, Lời giải, Barem, Phiếu OMR) | `exams.py` |

---

## 5. BẢN ĐỒ CÁC SUBSYSTEM & PROCESSING PIPELINES

### 5.1. Phân hệ Soạn đề LaTeX, AI Copilot & Biên dịch Hybrid (Composer Subsystem)

#### 5.1.1. Luồng Tương tác Trợ lý AI: Compact Prompt Bar & Inline Diff Suggestion
```
[GIÁO VIÊN SOẠN THẢO TRÊN LATEX EDITOR]
       │
       ▼
[Compact Floating AI Prompt Bar ở chân editor (#composer-ai-compact-bar)]
  - Dark Mode Contrast Tokens: text #f8fafc (trắng), caret #38bdf8 (xanh Apple), placeholder slate-400
  - Click vào thanh -> Chỉ focus ô nhập, giữ nguyên text cursor, KHÔNG mở popup
  - Giáo viên gõ/dán prompt tùy ý
       │
       ├──> Nhấn ENTER hoặc click Nút Gửi (Icon mũi tên tròn arrow-up)
       │         │
       │         ▼
       │    [KÍCH HOẠT MỞ RỘNG GIAO DIỆN FULL TRỢ LÝ SOẠN THẢO (OPTIMISTIC FAST DISPATCH)]
       │    - Mở bung bottom sheet popup (#composer-ai-popup, height 56% / 78% / 92% qua hardware transition)
       │    - Ẩn thanh compact bar, đồng bộ text vào ô chat chính trong <= 16ms
       │    - Hiển thị hiệu ứng loading (composer-typing-indicator)
       │         │
       │         ▼
       │    [GỬI REQUEST POST /api/v1/composer/chat]
       │    - Payload: { message, current_latex, compile_error_log, history }
       │    - Chuyển tiếp tự động `lastCompileError` từ lần compile XeTeX/Tectonic gần nhất
       │         │
       │         ▼
       │    [FASTAPI BACKEND: composer.py & composer_service.py]
       │    - Phân tích ngữ cảnh LaTeX + Log lỗi biên dịch + System Prompt ex_test.sty
       │    - extract_diff_from_text: Bóc tách khối diff (unified diff, search/replace, old/new, syntax diagnostics)
       │    - Đóng gói ChatResponse { reply, diff: DiffSuggestion(action, old_text, new_text, description) }
       │         │
       │         ▼
       │    [FRONTEND CLIENT: app.js -> showPendingDiff(diff)]
       │    1. Line Pinpointing: Tìm vị trí old_text -> Tính toán số dòng lineNo & lưu pinnedRange
       │    2. Scrolling & Selection: Cuộn editor textarea đến đúng dòng, bôi đen old_text
       │    3. Đồng thời hiển thị 2 cấp độ trực quan:
       │       - Cấp 1: Banner tổng quan trên đỉnh editor (#composer-pending-diff-banner)
       │       - Cấp 2: Inline Editor Diff Overlay / Widget trực tiếp ngay tại vị trí dòng mã nguồn:
       │                [- old_text] nền đỏ rose / [+ new_text] nền xanh emerald
       │                [Keep / Đồng ý] & [Undo / Từ chối] ngay tại dòng
       │    4. Khi bấm [Đồng ý] / [Apply]:
       │       - Kích hoạt Động cơ Thay thế Dòng Mờ (5-Tier Fuzzy Line Replacement Engine)
       │       - So khớp chuẩn hóa ngắt dòng, bỏ qua thụt lề, quét cửa sổ trượt, thay thế theo pinnedRange
       │       - Bảo đảm tỷ lệ thành công 100%, triệt tiêu lỗi "Không tìm thấy dòng cũ tương ứng"
       │       - Đóng diff overlay/banner, tự động gọi compile(true)
       │
       └──> Khi sửa mã xong -> Debounce 800ms -> Gửi POST /api/v1/composer/compile (latex_code, title, mode)
                 │
                 ├──> [Smart Dual-Mode Document Normalizer]
                 │         ├── Nếu KHÔNG CÓ \documentclass: Tiêm Canonical Preamble (fontspec, tikz, tkz-tab, tcolorbox, ex_test[mode], A4)
                 │         └── Nếu ĐÃ CÓ \documentclass: Bảo toàn cấu trúc, chuẩn hóa fontspec & đồng bộ option [mode]
                 │
                 ├──> [Tầng 1] Remote Tectonic Docker (http://armbian:8090/compile)
                 │         ├── Tự động nhúng ex_test.sty v3.3.6
                 │         ├── Tự động map fontspec (chống lỗi vietnam 8-bit)
                 │         └── Nếu lỗi: Trả về compile_error_log -> Client lưu vào lastCompileError
                 │
                 ├──> [Tầng 2] Local Tectonic CLI (nếu server Tectonic ngoại mạng gián đoạn)
                 │
                 └──> [Tầng 3] Chromium Headless + MathJax SVG + TikZ Renderer
                           │
                           └──> Trả về PDF Vector `%PDF-` -> Stream lên Live Preview Pane (PDF.js Canvas)
```

### 5.2. Phân hệ Xuất bản Đề thi Thuần Vector PDF (Tectonic XeTeX & ReportLab Engine)
```
[Dữ liệu câu hỏi LaTeX / Mã đề hoán vị]
       │
       ├──> Tạo tài liệu mẫu LaTeX / HTML5 ReportLab chuẩn khổ A4 Portrait, lề 1.5-1.8 cm
       │
       ├──> Động cơ biên dịch vector PDF (Tectonic XeTeX Engine trên Docker container ARM)
       │         ├── Dàn trang tự động 2 cột chuẩn đề thi THPT Quốc gia (QĐ 764/QĐ-BGDĐT)
       │         ├── Xử lý công thức Toán học chuẩn LaTeX và hình vẽ đồ thị vector
       │         └── Barem chấm điểm trắc nghiệm lũy tiến (0.1đ - 0.25đ - 0.5đ - 1.0đ)
       │
       └──> Đóng gói tệp nén ZIP trọn bộ đề thi:
                 ├── Đề thi các mã đề hoán vị (De_101.pdf, De_102.pdf, ...)
                 ├── Hướng dẫn giải chi tiết từng mã đề (LoiGiai_101.pdf, ...)
                 ├── Bảng ma trận đáp án đối chiếu (BangDapAn_TongHop.pdf & .csv)
                 └── Phiếu trả lời trắc nghiệm chuẩn Bộ GD&ĐT (Phieu_Tra_Loi_Trac_Nghiem_2025.pdf)
```

### 5.3. Phân hệ Số hóa 2-Pass Decoupled AI Pipeline
```
[Tệp Đề Thi Tải Lên (PDF / Ảnh)]
       │
       ├──> [Pre-processing] OpenCV Deskew + CLAHE Binarization + Nâng phân giải 200 DPI
       │
       ├──> [Layout Segmentation] Bóc tách Header, Tiêu đề phần, Bounding Boxes đồ thị/bảng
       │         │
       │         └──> Cắt ảnh tự động -> Nén WebP lưu tại storage/assets/ -> Nhúng [IMAGE:uuid]
       │
       ├──> [AI Pass 1 - Text & Answers] Vision LLM bóc tách văn bản câu hỏi, phương án, đáp án
       │
       ├──> [AI Pass 2 - Diagram Code] Dựng mã TikZ / Array song song cho từng khối hình ảnh
       │
       └──> [Auto-tagging & Deduplication] Gợi ý YCCĐ, kiểm tra trùng lặp Cosine Similarity >= 0.90
```

---

## 6. BẢN ĐỒ GIAO DIỆN CLIENT (FRONTEND ARCHITECTURE)

- **Mô hình Single Page Application (SPA):** Điều hướng thuần Client-side trên `frontend/static/app.js` thông qua đối tượng toàn cục `app`:
  - `app.navigate(route)`: Chuyển đổi trạng thái hiển thị giữa các view mà không tải lại trang (`history.pushState`).
  - `app.composer`: Quản lý toàn bộ vòng đời soạn thảo đề thi:
    + *Không gian làm việc co giãn linh hoạt & Split Resizer Chuẩn Apple HIG:* Thanh phân tách ngang `#composer-split-resizer` (class `composer-col-splitter`) được tái thiết kế chuẩn Apple HIG với khoảng cách đệm công thái học `w-3.5` / `w-4` và lề an toàn `mx-1` / `mx-1.5`, trục viên thuốc `w-1 h-9 rounded-full bg-slate-300 dark:bg-[#34415e]` cách đều viền card 6-8px, không đè sát viền box soạn thảo (Ảnh 2). Hỗ trợ kéo thả chuột/cảm ứng tùy biến tỷ lệ từ 25% đến 75% (nháy đúp về 60:40, lưu `quesy_composer_split_ratio`). Khung xem trước PDF tự động co giãn (`fitToWidth`) theo chiều rộng khả dụng trong thời gian thực khi kéo splitter, kết hợp vùng cuộn `overflow-x-auto` loại bỏ triệt để hiện tượng xén mép phải.
    + *Thanh Nhập Lệnh Thu Gọn & Cơ Chế Xóa Sạch Lạc Quan (Optimistic Input Reset):* Thanh dạng viên thuốc neo tại chân editor (`#composer-ai-compact-bar`) với độ tương phản chuẩn WCAG 2.1 AA (chữ trắng `#f8fafc`, caret `#38bdf8`). Click chuột chỉ để gõ text bình thường, nhấn Enter hoặc bấm nút gửi mới bung popup trợ lý. Hệ thống thực hiện xóa sạch lập tức cả 2 ô nhập (`compactInput.value = ''` và `chatInput.value = ''`) tại $t = 0\text{ms}$ khi gửi lệnh, triệt tiêu hoàn toàn lỗi text cũ còn kẹt trong ô nhập (Ảnh 1).
    + *Trợ lý Soạn thảo AI Hợp nhất (Unified Single Pill Handle):* Box trợ lý `#composer-ai-popup` trang bị duy nhất 1 thanh pill ngang `#composer-ai-resize-handle` tại trung tâm header (loại bỏ hoàn toàn thanh pill phụ bên trên mép popup), hỗ trợ kéo thả thay đổi độ cao mượt mà theo phương đứng (Vertical Drag Resize, dải an toàn 180px - 92%, lưu `quesy_composer_ai_height`) và nhấp đúp/nhấp nhanh toggle 56% / 78%.
    + *Thuật toán Phóng to / Thu nhỏ Thông minh (Smart Zoom-to-Point Engine):* Thay thế zoom cứng (0, 0) bằng thuật toán neo thông minh: tự động neo chính xác theo vị trí con trỏ chuột (`Cursor Anchor`) khi cuộn `Ctrl+Wheel` trên tài liệu, hoặc neo theo trọng tâm khung nhìn (`Center Anchor`) khi nhấn nút `+` / `-` trên thanh công cụ nổi, bảo toàn tọa độ cuộn khi render lại vector canvas sắc nét (High-DPI PDF.js).
    + *Quản lý Phiên Sạch sẽ & Ngăn kéo Lịch sử:* Mỗi phiên mới bắt đầu sạch sẽ với tin nhắn chào mặc định từ Quesy Copilot; các phiên cũ được lưu trữ vào kho `quesy_composer_chat_sessions` và mở xem lại khi người dùng bấm nút "Lịch sử".
    + *Kiến Trúc Duyệt & Áp Dụng Đa Khối Diff (Multi-Diff 1/N, Apply All):* Loại bỏ hoàn toàn widget diff trùng lặp trong bubble chat của trợ lý; toàn bộ giao diện so sánh `- old_text` / `+ new_text` được hiển thị tập trung trên Editor (Inline Diff Overlay và Top Banner). Hỗ trợ bóc tách đa khối diff (`diffs: List[DiffSuggestion]`), hiển thị bộ đếm động `${currentDiffIndex + 1}/${pendingDiffs.length}`, điều hướng tuần tự (`[< Trước]` / `[Sau >]`), duyệt chấp nhận/từ chối từng khối, và nút **`[Áp dụng tất cả] (Apply All)`** để hợp nhất toàn bộ các thay đổi vào mã nguồn chỉ với 1 cú click (Ảnh 3).
    + *Các tính năng cốt lõi khác:* Động cơ thay thế mờ 6 tầng (6-Tier Fuzzy Line Matcher), undo/redo stack, debounced compiler, AI copilot chat, toggle lời giải `[dethi]` <-> `[loigiai]`, và trình xem trước High-DPI Vector Canvas (PDF.js) đồng bộ 100% tỷ lệ thu phóng.
  - `app.bank`: Quản lý tìm kiếm câu hỏi, cây bộ lọc 6 tầng, preview công thức toán KaTeX.
  - `app.matrix`: Quản lý ma trận đề thi 2 chiều, phân bổ số lượng câu theo mức độ nhận thức.
  - `app.shuffler`: Quản lý thuật toán xáo trộn đề, tạo mã đề hoán vị và xuất bản tài liệu.
  - `app.digitize`: Quản lý tải lên, theo dõi tiến trình WebSocket/Polling (0-100%) và màn hình đối chiếu song song HITL.

---

## 7. QUY CHUẨN MÔI TRƯỜNG & HẠ TẦNG TRIỂN KHAI

| Môi trường | Thành phần | Chi tiết cấu hình |
| :--- | :--- | :--- |
| **Local Dev** | Python Runtime | Python 3.13 (`C:\Users\ngnsusinn\AppData\Local\Programs\Python\Python313\python.exe`) |
| **Local Dev** | Node.js Worker | Node.js v20+ điều hành `backend/services/mathjax_worker.js` |
| **Local Dev** | Web Server | FastAPI / Uvicorn lắng nghe cổng 8000 (auto-failover sang 8001 nếu cổng bận) |
| **Server Deploy** | Tectonic Docker | Microservice `tectonic-compiler-api` trên host `armbian:8090` |
| **Server Deploy** | Cache CTAN | Volume mount `/root/.cache/tectonic` lưu trữ vĩnh viễn 43MB packages |
| **CI / CD** | GitHub Actions | Runner `ubuntu-latest`, Python 3.13, Node 20. Cổng kiểm soát Pre-Commit CI Gate bắt buộc (100% pass CI mới được commit), nguyên tắc Strict CI Isolation (độc quyền Sub-Agent 3, cấm các sub-agent khác đọc/ghi), và vòng lặp sửa lỗi CI Loop. |

---

## 8. HƯỚNG DẪN MỞ RỘNG & PHÁT TRIỂN TIẾP THEO

1. **Bổ sung mẫu câu hỏi mới vào Composer:**
   - Thêm khai báo template trong `composer.py` (`ComposerTemplateResponse`).
   - Thêm nút chèn trong dropdown `THÊM ▾` trên `frontend/index.html`.
   - Cập nhật parser bóc tách câu hỏi tương ứng trong `backend/services/composer_service.py`.
2. **Nâng cấp gói lệnh `ex_test.sty`:**
   - Cập nhật tệp `backend/templates/ex_test.sty`.
   - Đẩy tệp lên container Tectonic trên server `armbian`: `/root/tectonic-docker/ex_test.sty` và restart container.
3. **Mở rộng nhà cung cấp AI:**
   - Cấu hình thêm provider trong `backend/services/ai_provider_service.py` (hỗ trợ OpenAI, Gemini, OpenRouter, DeepSeek qua chuẩn OpenAI-compatible API).

---

## 9. QUY TRÌNH KÍCH HOẠT 4 SUB-AGENT ĐỒNG THỜI CHO MỖI YÊU CẦU TÍNH NĂNG

Mỗi lệnh yêu cầu về tính năng mới, nâng cấp hoặc sửa đổi hệ thống bắt buộc phải kích hoạt 4 Sub-Agent chạy đồng thời (song song qua `delegate_task`), tuyệt đối không chạy đơn luồng tuần tự:
1. **Sub-Agent 1 - Analysis, Specs & Docs:** Phân tích kiến trúc, rà soát tác động, đồng bộ toàn bộ tài liệu kỹ thuật (`SRS`, `FRD`, `BRD`, `NFR`, `SOURCE_MAP.md`, `README.md`). **Quy tắc cô lập CI:** Tuyệt đối KHÔNG ĐƯỢC PHÉP truy cập và đọc tệp cấu hình CI/CD (`.github/workflows/`).
2. **Sub-Agent 2 - Software Engineering & Coding:** Hiện thực hóa tính năng, lập trình backend/frontend, tuân thủ Apple HIG và thiết kế hệ thống. **Quy tắc cô lập CI:** Tuyệt đối KHÔNG ĐƯỢC PHÉP truy cập và đọc tệp cấu hình CI/CD (`.github/workflows/`). Chủ động cung cấp thông tin cập nhật mã nguồn/thư viện cho Sub-Agent 3.
3. **Sub-Agent 3 - Automated Test & CI/CD Verification (Độc quyền CI/CD):**
   - **Strict CI Isolation:** Là sub-agent DUY NHẤT được phép truy cập, đọc, viết, chỉnh sửa toàn bộ cấu hình CI/CD (`.github/workflows/`). Hoàn toàn tách biệt với các sub-agents còn lại.
   - **Tiếp nhận thông tin một chiều:** Có toàn quyền đọc và tiếp nhận thông tin từ Sub-Agent 1, Sub-Agent 2, Sub-Agent 4 để cập nhật CI đồng bộ theo code mới, loại bỏ nguy cơ lỗi trên runner.
   - **Kiểm thử tự động & Quản lý Cổng Pre-Commit Gate:** Viết mới/cập nhật test cases `pytest`, chạy toàn bộ test suite. Quản lý vòng lặp sửa lỗi CI (CI Loop) và chỉ cho phép commit khi 100% test cases vượt qua trên CI.
4. **Sub-Agent 4 - E2E Browser Blind Test & UI/UX Audit:** Mở trình duyệt thật qua `browser_exec`, thao tác thủ công (`fill_input`, `click_at_xy`), chụp màn hình, kiểm tra console log/error, đối chiếu toàn diện 5 nhóm khuyết tật phần mềm. **Quy tắc cô lập CI:** Tuyệt đối KHÔNG ĐƯỢC PHÉP truy cập và đọc tệp cấu hình CI/CD (`.github/workflows/`).

- **Định nghĩa "Lỗi" bao trùm 5 nhóm:**
  1. Lỗi logic nghiệp vụ & backend (API exception 500/422, sai điểm QĐ 764, treo port/process).
  2. Lỗi giao diện & layout (vỡ khung, kẹt cuộn textarea, tràn viền, responsive vỡ).
  3. Lỗi màu sắc & phong cách (sai mã màu chuẩn như nút BIÊN DỊCH `#0071e3`, lỗi biến đổi màu nền trắng khi focus dark mode).
  4. Lỗi tương tác & hành vi UX (thiếu phản hồi scale 0.97, thay thế nhầm code, kẹt popup).
  5. Lỗi console & tài nguyên (mọi `console.error` đỏ, 404 font/icon, xén nét toán học).
- **Vòng lặp đóng & Cổng Pre-Commit CI (CI Loop & Review Loop):**
  - Parent Agent nhận kết quả đồng thời từ 4 Sub-Agent, thẩm định chéo.
  - **Bắt buộc Pass CI trước khi commit:** Nếu CI test không pass:
    `CI thất bại` → `Sub-Agent 2 sửa code / Sub-Agent 3 cập nhật CI & test` → `Sub-Agent 3 test lại CI` → `Lặp lại quy trình` cho đến khi **PASS 100% CI MỚI ĐƯỢC COMMIT**.
  - Nếu Sub-Agent 3 hoặc Sub-Agent 4 phát hiện bất kỳ lỗi nào trong 5 nhóm trên:
    `Phát hiện lỗi` → `Sub-Agent 2 sửa` → `Sub-Agent 3 test` → `Sub-Agent 4 blind test` cho đến khi hoàn thành 100% mọi yêu cầu mà không còn lỗi.
- **Cơ chế Chống Tái Diễn Lỗi (Anti-Regression Shield cho Sub-Agent 4):**
  - Mọi phản ánh, đề xuất báo lỗi của người dùng về Frontend/Backend tự động được trích xuất thành tiêu chí kiểm thử đối chứng bắt buộc nạp vào prompt của Sub-Agent 4:
    1. *Tiêu chí 1 (Dark Mode Input Contrast):* Kiểm tra màu chữ `#composer-compact-input` và `#composer-chat-input` phải là màu trắng sáng `#f8fafc` hoặc `#ffffff` nổi bật trên nền tối `#1c1c1f`, không bị màu đen `#1d1d1f` chìm nghỉm, con trỏ caret màu xanh Apple `#38bdf8`.
    2. *Tiêu chí 2 (Compile Error Forwarding):* Cố ý tạo lỗi cú pháp LaTeX (ví dụ: `\badcommand`), biên dịch thất bại -> gửi prompt yêu cầu "sửa lỗi giúp tôi" -> AI Copilot tiếp nhận log lỗi `compile_error_log` và xuất diff sửa đúng dòng lỗi.
    3. *Tiêu chí 3 (Fuzzy Diff Replacement & Inline Overlay):* Bấm [Đồng ý áp dụng] / [Apply] thành công 100%, không xuất hiện toast "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại". Giao diện diff hiển thị trực quan trực tiếp tại vị trí dòng mã nguồn trên ô soạn thảo (dòng đỏ -, dòng xanh +, nút Keep/Đồng ý và Undo/Từ chối).
    4. *Tiêu chí 4 (Fast Dispatch & Smooth Chat):* Gửi prompt từ compact input hoặc chat input phản hồi tức thì không bị delay, chuyển động mở popup và cuộn tin nhắn mượt mà chuẩn 60 FPS, không có lỗi JavaScript màu đỏ trong console.
    5. *Tiêu chí 5 (Question Replacement & Smart Diff Binding):* Khi gửi prompt thay thế câu hỏi (ví dụ: *"Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"*), hệ thống tự động bóc tách câu 1 (`find_question_block`), gán diff chính xác lên editor, hiển thị banner và overlay mà không phụ thuộc vào `SequenceMatcher`.
    6. *Tiêu chí 6 (Safe Chat Bubble Rendering & Zero Code Loss):* Nếu không có diff hoặc diff không khớp, khối code LaTeX không được ẩn mất khỏi chat bubble; hiển thị đầy đủ 3 nút hành động `[📥 Chèn vào con trỏ]`, `[📋 Sao chép]`, và `[🔄 Áp dụng thay thế]`, tuyệt đối không nuốt mất mã của người dùng.
  - Sub-Agent 4 bắt buộc phải thao tác trực tiếp trên trình duyệt thật (`browser_exec`), chụp ảnh màn hình và đối chứng thực tế để bảo đảm các lỗi trên không tái phát trước khi nghiệm thu.

---

## 10. QUY TRÌNH QUẢN TRỊ PHIÊN BẢN & GIT WORKFLOW (STRICT PRE-COMMIT CI GATE, COMMIT & PUSH ONLY)

- **Cổng Kiểm Soát Bắt Buộc Trước Khi Commit (Pre-Commit CI Gate):**
  - **Bắt buộc:** Trước khi thực hiện `git commit`, mã nguồn bắt buộc phải vượt qua toàn diện bài kiểm thử CI trên runner (`pytest`, syntax check, môi trường tương đương CI). Tuyệt đối cấm commit khi CI test chưa pass 100%.
  - **Vòng lặp sửa lỗi CI (CI Fix-and-Test Loop):** Nếu CI test không pass:
    `CI thất bại` → `Sub-Agent 2 sửa code / Sub-Agent 3 cập nhật CI & test` → `Sub-Agent 3 chạy lại CI test` → `Lặp lại quy trình` cho đến khi **100% PASS CI mới được phép thực hiện commit**.
- **Quy trình Commit & Push:**
  1. Sau khi 100% test cases vượt qua trên CI, thực hiện `git commit` tuân thủ chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).
  2. Thực hiện `git push` lên nhánh làm việc (remote branch).
- **TUYỆT ĐỐI KHÔNG TỰ ĐỘNG TẠO/CẬP NHẬT PULL REQUEST:**
  - Nghiêm cấm các sub-agent tự ý chạy lệnh `gh pr create` hoặc gọi GitHub REST API để mở Pull Request.
  - Nghiêm cấm tự động cập nhật hoặc đẩy vào Pull Request có sẵn trừ khi Người dùng (User) yêu cầu bằng lời nói rõ ràng, cụ thể.
- **Dọn dẹp tiến trình:** Bắt buộc diệt sạch các tiến trình nền (uvicorn cổng 8000, Node.js persistent worker, subprocess) sau khi kết thúc lượt phản hồi.
