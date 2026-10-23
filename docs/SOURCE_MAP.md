# BẢN ĐỒ MÃ NGUỒN & KIẾN TRÚC HỆ THỐNG CHI TIẾT (QUESY SOURCE MAP)

> **Dự án:** Quesy - Nền tảng Quản trị Khảo thí, Soạn đề & Số hóa Đề thi Chuẩn Quốc gia  
> **Chuẩn Khảo thí:** Thông tư 32/2018/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT (Định dạng Đề thi 2025)  
> **Trạng thái mã nguồn:** Đạt 100% kiểm thử tự động (71/71 test cases PASSED)  
> **Cập nhật lần cuối:** Tháng 10/2026  

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE OVERVIEW)

Quesy được xây dựng theo kiến trúc **Module-based Monolith** kết hợp **External Compiling Microservices**, phân tách rõ ràng 4 tầng:
1. **Frontend Presentation & Micro-interaction Layer:** Single Page Application (SPA) điều hướng sạch (`/path`), tuân thủ Apple HIG và tương tác Emil Kowalski (phản hồi xúc giác 0.97, Dark Code Editor `#141824`, Live PDF Preview).
2. **API Gateway & Routing Layer:** FastAPI (Python 3.13) bất đồng bộ, tự động validate Pydantic V2 schemas, bảo toàn route SPA tránh lỗi 404 khi F5.
3. **Core Domain Services & Processing Pipelines:**
   - *Soạn đề & Biên dịch Hybrid:* `composer_service.py` kết nối Remote Tectonic XeTeX Engine Docker (host `armbian:8090`), gói lệnh chuẩn quốc gia `ex_test.sty` (v3.3.6), AI Inline Diff Replacer.
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
│   ├── test_composer.py               # Kiểm thử Soạn đề, Tectonic compile, AI Inline Diff (181 dòng)
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
    └── ci.yml                         # Quy trình CI/CD GitHub Actions trên Ubuntu runner (64 dòng)
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
| **POST** | `/api/v1/composer/compile` | Biên dịch mã LaTeX sang Live PDF Preview (Debounced) | `composer.py` |
| **POST** | `/api/v1/composer/chat` | AI Copilot hỗ trợ soạn thảo, đề xuất Smart Inline Diff | `composer.py` |
| **GET** | `/api/v1/composer/pdf/{doc_id}.pdf` | Stream trực tiếp tệp PDF xem trước | `composer.py` |
| **GET** | `/api/v1/composer/templates` | Danh mục mẫu đề thi chuẩn quốc gia (`ex_test.sty` v3.3) | `composer.py` |
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

### 5.1. Phân hệ Soạn đề LaTeX & Biên dịch Hybrid (Composer Subsystem)
```
[User gõ LaTeX / Chat AI] 
       │
       ├──> AI Chat -> Trả về DiffSuggestion (old_text -> new_text)
       │         └──> Editor bôi đen dòng cũ -> Banner Duyệt Diff -> [Đồng ý] -> Thay thế đúng 1 dòng
       │
       └──> Debounce 800ms -> Gửi POST /api/v1/composer/compile
                 │
                 ├──> [Tầng 1] Gọi Remote Tectonic Docker (http://armbian:8090/compile)
                 │         ├── Tự động nhúng ex_test.sty v3.3.6
                 │         ├── Tự động map fontspec (chống lỗi vietnam 8-bit)
                 │         └── Fallback giả lập ảnh 1x1 nếu thiếu asset
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
  - `app.composer`: Quản lý toàn bộ vòng đời soạn thảo đề thi, tỷ lệ ngang 6:4 (60% Code Editor, 40% Live Preview), Trợ lý soạn thảo dạng Bottom Sheet Popup đa trạng thái (Compact Floating Bar $\leftrightarrow$ Expanded History Panel), undo/redo stack, debounced compiler, AI copilot chat, inline diff review, toggle lời giải `[dethi]` $\leftrightarrow$ `[loigiai]`, và trình xem trước High-DPI Vector Canvas (PDF.js) đồng bộ 100% tỷ lệ thu phóng (Zoom Sync giữa nút bấm và Ctrl+Scroll).
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
| **CI / CD** | GitHub Actions | Runner `ubuntu-latest`, Python 3.13, Node 20, 100% test suite đạt 71/71 |

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

## 9. QUY TRÌNH PHÂN HÓA 4 AGENT CHUYÊN TRÁCH & VÒNG LẶP KIỂM THỬ THỰC TẾ

Hệ thống áp dụng nghiêm ngặt quy trình phát triển và kiểm thử phân hóa 4 Agent độc lập:
1. **Agent 1 - Analysis & Comprehension (Đọc hiểu & Mổ xẻ Dự án):** Phân tích kiến trúc, tài liệu, xác định phạm vi ảnh hưởng trước khi code.
2. **Agent 2 - Software Engineering & Coding (Lập trình Mã nguồn):** Hiện thực hóa tính năng, sửa bug, tuân thủ đúng phạm vi yêu cầu.
3. **Agent 3 - Test & Verification (Kiểm thử Chức năng Tự động):** Chạy kiểm thử tự động toàn diện `pytest` (71/71 PASSED).
4. **Agent 4 - Blind Test (Kiểm thử Mù & Đối chứng Thực tế trên Trình duyệt):**
   - Trực tiếp mở trình duyệt thật (`browser_exec`).
   - Thao tác thủ công toàn diện: gõ phím (`fill_input`), click chuột (`click_at_xy`), cuộn trang, chuyển đổi tab.
   - Chụp ảnh màn hình (capture screen) ghi lại bằng chứng trực quan.
   - Giám sát log máy chủ và bảng điều khiển `console.log` / `console.error` của trình duyệt.
   - **Định nghĩa "Lỗi" bao trùm 5 nhóm:**
     1. Lỗi logic nghiệp vụ & backend (API exception 500/422, sai điểm QĐ 764, treo port/process).
     2. Lỗi giao diện & layout (vỡ khung, kẹt cuộn textarea, tràn viền, responsive vỡ).
     3. Lỗi màu sắc & phong cách (sai mã màu chuẩn như nút BIÊN DỊCH `#0071e3`, lỗi biến đổi màu nền trắng khi focus dark mode).
     4. Lỗi tương tác & hành vi UX (thiếu phản hồi scale 0.97, thay thế nhầm code, kẹt popup).
     5. Lỗi console & tài nguyên (mọi `console.error` đỏ, 404 font/icon, xén nét toán học).
   - **Vòng lặp đóng:** `Coding -> Test -> Blind Test / Review -> Coding...` lặp lại cho đến khi hoàn thành 100% mọi yêu cầu mà không còn lỗi.
