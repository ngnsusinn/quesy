# QUESY: NỀN TẢNG SỐ HÓA, QUẢN LÝ ĐỀ THI & DỰNG ĐỒ THỊ TOÁN HỌC TỰ ĐỘNG BẰNG AI

> **Giải pháp toàn diện giúp giáo viên và các tổ chức giáo dục giải quyết triệt để bài toán gõ lại đề thi thủ công, tự động dựng lại đồ thị vector sắc nét, chuẩn hóa công thức toán học, trộn đề thi an toàn không lỗi logic và xuất bản đề in ấn chuẩn mực chỉ trong vài giây.**

[![CI Test Suite](https://github.com/ngnsusinn/quesy/actions/workflows/ci.yml/badge.svg)](https://github.com/ngnsusinn/quesy/actions)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy-009688)
![Frontend](https://img.shields.io/badge/Frontend-Apple%20HIG%20SPA%20%2B%20TailwindCSS%20%2B%20KaTeX-000000)
![Tests](https://img.shields.io/badge/Pytest-55%2F55%20Passing-brightgreen)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 1. VẤN ĐỀ THỰC TẾ & GIẢI PHÁP ĐỘT PHÁ CỦA QUESY

Trong công tác biên soạn đề thi và quản lý ngân hàng câu hỏi, giáo viên và các hội đồng khảo thí thường xuyên đối mặt với 6 bài toán nan giải:

| # | Vấn đề & Nỗi đau thực tế | Giải pháp giải quyết của Quesy |
|---|---|---|
| **1** | **Gõ lại đề thi thủ công tốn hàng giờ:** Giáo viên mất 1.5 - 2 giờ để gõ lại một đề thi từ file PDF scan, ảnh chụp hoặc Word cũ; công thức MathType lỗi thời, vỡ font khi copy-paste. | **AI Ingestion & OCR Thông minh:** Tự động số hóa đa định dạng (PDF scan, ảnh chụp, DOCX), giải mã trực tiếp nhị phân MathType MTEF sang LaTeX chuẩn trong vài giây. |
| **2** | **Đồ thị & hình vẽ bị bỏ quên hoặc méo mó:** Các công cụ OCR thông thường chỉ đọc chữ thô, bỏ qua hình vẽ; hoặc khi vẽ đồ thị tiệm cận thì toạ độ vọt lên vô cực, làm méo xẹp tỷ lệ khung hình. | **Bộ Dựng Đồ Thị Vector SVG Tự Động (TikZ Engine):** Tự động nhận diện hàm bậc 3, hàm phân thức, hàm trùng phương và biên dịch sang vector SVG sắc nét; có cơ chế **Auto-clipping** tự khống chế khung hình cân đối, hỗ trợ đồ thị trong cả đề bài lẫn 4 đáp án A, B, C, D. |
| **3** | **Công thức toán học bị lỗi hiển thị (KaTeX Crashes):** Dấu ngoặc lệch cỡ, số thập phân bị hở khoảng cách, dấu gạch chéo tập hợp bị lỗi escape hiển thị chữ đỏ thô. | **Bộ Chuẩn Hóa Toán Học Tự Động:** Tự động chuẩn hóa dấu ngoặc kích thước động (`\left`/`\right`), phân số display `\dfrac`, vectơ `\overrightarrow`, số thập phân `{,}` trong đề và số sạch trong đáp án. |
| **4** | **Trộn đề làm vỡ logic câu hỏi:** Các phần mềm trộn đề cổ điển hoán vị đáp án khiến câu *"Cả A và B đều đúng"* nhảy lên vị trí A; bài đọc chung bị tách rời khỏi câu hỏi con; các phần thi bị đảo lộn. | **Động cơ Trộn Đề An Toàn (Safe Shuffling Engine):** Khóa neo phương án (Option Anchor - giữ các câu *"Cả A và B"* ở vị trí D), bảo toàn bài đọc chung (Passage Integrity), bảo toàn phân vùng (Section Integrity) và sinh ma trận đối chiếu đáp án tự động. |
| **5** | **Chấm điểm Đúng/Sai bậc thang phức tạp:** Cấu trúc trắc nghiệm Đúng/Sai 4 khẳng định có cơ chế tính điểm bậc thang (0.1, 0.25, 0.5, 1.0) dễ gây nhầm lẫn và sai sót lớn nếu chấm thủ công. | **Hệ Thống Tự Động Chấm Điểm & Quản Lý Lớp Học:** Chấm điểm tự động theo thuật toán bậc thang, quản lý danh sách học sinh, xuất/nhập bảng điểm Excel UTF-8 BOM và phân tích phổ điểm trực quan. |
| **6** | **Dàn trang in ấn Word mất nhiều công sức & lỗi mờ công thức:** Giáo viên phải tự căn lề, công thức toán xuất ra dạng ảnh PNG bị vỡ hạt, mờ nhòe, không mở sửa được bằng MathType, hoặc bảng số liệu bị lỗi đen khi xuất PDF. | **Xuất Bản Đa Định Dạng Khảo Thí Chuẩn In Ấn:** Tạo file Word `.docx` khổ A4 chuẩn với công thức **MathType 7.0 OLE Vector WMF** (nét căng tuyệt đối, click đúp mở MathType chỉnh sửa trực tiếp), **Word OMML native**, tự động nhận diện và chuyển đổi bảng LaTeX `\begin{array}` thành bảng Word `<w:tbl>` chống lỗi đen, xuất bản PDF in ấn và phiếu soi đáp án OMR đóng gói trong file ZIP. |

---

## 2. CÁC TÍNH NĂNG CỐT LÕI (CORE CAPABILITIES)

### 2.1. Số Hóa Đề Thi & Dựng Đồ Thị Vector Bằng AI
* **Đa nguồn tài liệu:** Tải lên tệp Word (`.docx`, `.doc`), tài liệu PDF scan nhiều trang hoặc chùm ảnh chụp bài thi.
* **Tích hợp AI đa nền tảng:** Kết nối linh hoạt Google Gemini, OpenAI GPT-4o, Anthropic Claude, OpenRouter hoặc sử dụng bộ quy tắc phân tích Offline cục bộ.
* **Bộ dựng đồ thị TikZ sang SVG:** Biên dịch trực tiếp mã nguồn hình học và hàm số sang đồ họa vector SVG sắc nét thông qua dịch vụ Kroki kèm bộ nhớ đệm ổ đĩa (`storage/tikz_cache/`), tải lại tức thì (0ms).
* **Auto-clipping chống méo tỷ lệ:** Tự động phát hiện phạm vi hệ trục toạ độ để khống chế biên độ vẽ hàm phân thức, đảm bảo đồ thị luôn hiển thị vuông vắn, rõ ràng.
* **Đồ thị trong đáp án:** Hỗ trợ hiển thị đồ thị độc lập trong từng phương án lựa chọn A, B, C, D dưới dạng thẻ trực quan.

### 2.2. Chuẩn Hóa Công Thức Toán Học Toàn Diện
* **Quy chuẩn 4 yếu tố toán học:**
  1. *Dấu ngoặc kích thước động:* Tự động bọc `\left(...\right)`, `\left[...\right]`, `\left\{...\right\}` (bảo vệ căn `\sqrt[...]` và text mode).
  2. *Số thập phân:* Tự động định dạng dấu phẩy `{,}` trong đề bài để KaTeX không tạo khoảng trống (ví dụ `15{,}25`), đồng thời giữ số sạch ở đáp án (`3,9`, `15,25`).
  3. *Phân số chuẩn:* Luôn chuyển sang `\dfrac` giúp công thức hiển thị thoáng đẹp.
  4. *Ký hiệu vectơ:* Chuẩn hóa thành `\overrightarrow{AB}` thay vì `\vec`.
* **Tự động sửa lỗi bảng số liệu:** Chuyển đổi môi trường `tabular` sang KaTeX `array` và tự động đóng thẻ `$$`.

### 2.3. Studio Hậu Kiểm Đối Chiếu Song Song (HITL Studio)
* **Giao diện tối giản Apple HIG:** Trải nghiệm cuộn mượt mà đơn trục, phản hồi vi mô xúc giác, font chữ Apple sans-serif đồng nhất.
* **Đối chiếu song song:** Cột trái xem tài liệu gốc (PDF, ảnh scan, Word), cột phải hiển thị danh sách câu hỏi điện tử tương ứng.
* **Thao tác 1-Click:** Chỉnh sửa nhanh công thức, đổi đáp án trắc nghiệm chỉ bằng một cú nhấp chuột, kiểm tra trùng lặp câu hỏi bằng AI Vector Cosine Similarity.
* **Tự động ẩn phân trang:** Giao diện tự động ẩn cụm chuyển trang khi tài liệu chỉ có 1 trang ảnh.

### 2.4. Động Cơ Trộn Đề Thi An Toàn (Safe Shuffling Engine)
* **Khóa neo vị trí (Option Anchor):** Tự động nhận diện và khóa cố định các phương án như *"Cả A và B đều đúng"*, *"Tất cả các ý trên đều sai"* tại vị trí cuối cùng (D), đảm bảo không bao giờ bị đảo lên A, B, C làm sai lệch đáp án.
* **Bảo toàn ngữ cảnh (Passage Integrity):** Các bài đọc chung và chùm câu hỏi liên quan luôn được giữ liền kề nhau trong mọi mã đề hoán vị.
* **Bảo toàn phân vùng (Section Integrity):** Câu hỏi chỉ hoán vị trong nội bộ từng phần thi, không xáo trộn cấu trúc bài thi.
* **Ma trận đối chiếu đáp án:** Tự động sinh bảng ánh xạ đáp án chéo giữa các mã đề để giáo viên chấm thi thuận tiện.

### 2.5. Xuất Bản & Chấm Điểm Chuyên Nghiệp
* **Word DOCX MathType 7.0 OLE Vector WMF:** Xuất bản tài liệu Word chuẩn A4 dọc (210 x 297 mm, lề 1.5 - 1.8 cm) với đối tượng OLE MathType (`Equation.DSMT4`) nhúng ảnh Vector WMF (`image/x-wmf`) chuẩn APM header. 100% công thức đạt chuẩn vector tuyệt đối (zero raster DIB, zero ký tự lỗi `?`), căn thẳng hàng tuyệt đối chân dòng (baseline alignment qua `w:position` khớp chuẩn xác theo `depth_pt`), tự động nâng cấp phân số sang `\dfrac` (cỡ chữ 11pt đầy đủ cho cả tử và mẫu), chuẩn hóa khoảng cách ký tự (kerning/spacing chuẩn MathType: giãn cách toán tử `=`, `+`, `-`, đệm giữa các nhân tử kề nhau, hỗ trợ ký hiệu đạo hàm `f'(x)` chuẩn Symbol `0xa2`), bảo toàn và dựng vector đa giác cho các dấu ngoặc co giãn (`\left`, `\right` ngoặc đơn, ngoặc vuông, ngoặc nhọn), đệm kerning chữ nghiêng tránh dính dấu ngoặc (`f(x)` -> `f\,(x)`), chuẩn hóa tập số `\mathbb{R}, \mathbb{Q}, \mathbb{Z}` sang Times New Roman Bold đứng chuẩn xác, lọc bỏ hoàn toàn các ký tự vô hình MathML (`\u2061` ApplyFunction, `\u2062` InvisibleTimes...), tắt gạch chân đỏ kiểm tra chính tả của Word (`w:hideSpellingErrors`, `w:noProof`), quy chuẩn font chữ chuẩn xác theo MathType/ISO (tên hàm `\sin`, `\cos`, `\tan`, `\cot` thẳng đứng Upright, biến số `x`, `y`, `a`, `b` in nghiêng Italic), stream CFB nhị phân DSMT7 chứa bản ghi `TeX Input Language` nguyên bản, **hỗ trợ click đúp mở MathType 7 client để chỉnh sửa 2 chiều mượt mà đồng bộ dữ liệu với Web**.
* **Word DOCX OMML Native:** Hỗ trợ xuất công thức toán bản địa của Microsoft Word (`<m:oMath>`) qua MathJax MathML và XSLT.
* **Tự động chuyển đổi bảng thống kê:** Tự động nhận diện mảng bảng số liệu ghép nhóm `\begin{array}` và chuyển đổi thành bảng Word chuẩn `<w:tbl>` có viền nét mảnh, loại bỏ triệt để hiện tượng hộp đen (black box) khi chuyển sang PDF.
* **MathJax Engine Persistent Worker:** Tích hợp tiến trình nền Node.js MathJax 3/4 xử lý công thức TeX phức tạp chỉ trong ~14 ms/công thức, bảo đảm tốc độ xuất đề siêu tốc.
* **Gói ấn phẩm ZIP:** Đóng gói trọn bộ đề thi các mã, file đáp án, lời giải chi tiết và phiếu soi đáp án trắc nghiệm OMR.
* **Quản lý bảng điểm:** Nhập/xuất danh sách học sinh và bảng điểm định dạng CSV/Excel UTF-8 BOM, tự động chấm điểm theo thang điểm bậc thang.
* **Offline PWA:** Ứng dụng hỗ trợ cài đặt PWA trên máy tính/điện thoại với cơ chế Network-First, sẵn sàng hoạt động cả khi mất kết nối mạng.

---

## 2. CẤU TRÚC THƯ MỤC DỰ ÁN

```
quesy/
├── backend/
│   ├── config.py              # Cấu hình môi trường (.env), AI keys & đường dẫn
│   ├── database.py            # Kết nối SQLAlchemy engine & session factory
│   ├── models.py              # ORM models (Taxonomy, Questions, Exams, Matrices, Classrooms, Students)
│   ├── schemas.py             # Pydantic v2 schemas xác thực dữ liệu chặt chẽ
│   ├── seed_data.py           # Bộ dữ liệu ngân hàng mẫu chuẩn TT 32 môn Toán 12
│   ├── main.py                # FastAPI app, CORS, SPA routes & mount tĩnh
│   ├── routers/
│   │   ├── taxonomy.py        # API cây kiến thức 6 tầng theo TT 32
│   │   ├── questions.py       # API CRUD câu hỏi, kiểm tra trùng lặp AI Vector
│   │   ├── digitize.py        # API Upload đề, AI Parsing pipeline & TikZ renderer
│   │   ├── matrix.py          # API thiết lập Ma trận đề thi 2 chiều
│   │   └── exams.py           # API sinh MasterExam, hoán vị mã đề an toàn, xuất ZIP & bảng điểm
│   └── services/
│       ├── ai_provider_service.py # Bộ tích hợp AI đa nền tảng (Gemini / OpenAI / Claude)
│       ├── ai_parser.py       # Pipeline bóc tách đề thi (DOCX/PDF/Image)
│       ├── mathjax_service.py # Dịch vụ MathJax TeX-to-MathML, SVG, PNG & baseline
│       ├── mathjax_worker.js  # Node.js persistent worker chạy MathJax 3/4 + Resvg
│       ├── tikz_renderer.py   # Dịch vụ biên dịch TikZ/PGFPlots sang SVG qua Kroki + Cache
│       ├── latex_converter.py # Giải mã MathType MTEF sang LaTeX & KaTeX sanitizer
│       ├── crop_service.py    # Auto-crop hình học/đồ thị lưu WebP
│       ├── tagging_service.py # AI Auto-tagging YCCĐ & Cosine similarity deduplication
│       ├── matrix_solver.py   # Thuật toán rút câu hỏi theo ma trận ràng buộc
│       ├── shuffling_engine.py# Trộn đề an toàn (Section, Passage, Option Anchor)
│       ├── excel_exporter.py  # Xuất nhập bảng điểm Excel/CSV UTF-8 BOM theo TT 22
│       └── docx_exporter.py   # Xuất bản Word MathType Vector WMF, OMML native & đóng gói ZIP
├── frontend/
│   ├── index.html             # Single Page Application (TailwindCSS, KaTeX, Lucide Icons)
│   ├── manifest.json          # PWA Web App Manifest
│   ├── sw.js                  # PWA Service Worker (Network-First Cache)
│   └── static/
│       ├── app.js             # State management, SPA router, HITL Studio, TikZ rendering
│       └── style.css          # Giao diện responsive Apple HIG & Emil Kowalski micro-interactions
├── docs/                      # Bộ tài liệu đặc tả kỹ thuật tiêu chuẩn phần mềm
│   ├── BRD_Exam_Management_AI_Digitization.md   # Business Requirements Document v2.0
│   ├── SRS_System_Requirements_Specification.md  # System Requirements Specification v2.0
│   ├── FRD_Functional_Requirements_Document.md   # Functional Requirements Document v2.0
│   ├── UC_Use_Case_Specifications.md            # Use Case Specifications v2.0
│   ├── NFR_Non_Functional_Requirements.md        # Non-Functional Requirements v2.0
│   ├── FS_Feasibility_Study_Report.md            # Feasibility Study & ROI Report v2.0
│   └── TEST_Test_Cases_Specification.md          # Test Cases Specification v2.0
├── tests/                     # 46 kịch bản kiểm thử tự động toàn diện (Pytest)
│   ├── test_taxonomy.py
│   ├── test_rules_shuffling.py
│   ├── test_deduplication.py
│   ├── test_docx_export.py
│   ├── test_api_endpoints.py
│   ├── test_api_contracts_and_negatives.py
│   ├── test_ai_pipeline.py
│   ├── test_cloud_vision_adapter.py
│   ├── test_excel_roster_import_export.py
│   ├── test_performance_budgets.py
│   ├── test_services.py
│   └── test_e2e_workflow.py
├── storage/                   # Thư mục lưu trữ tài nguyên
│   ├── uploads/               # File đề thi gốc tải lên
│   ├── assets/                # Ảnh đồ thị/hình học cắt ra dạng WebP
│   ├── tikz_cache/            # Bộ nhớ đệm vector SVG của đồ thị TikZ
│   └── exports/               # File đề Word và gói ZIP xuất bản
├── Dockerfile                 # Multi-stage production container
├── docker-compose.yml         # Container orchestration
└── start_server.py            # Script khởi động tự động (auto port discovery & kill busy port)
```

---

## 3. HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY

### 3.1. Cài Đặt Môi Trường
Yêu cầu **Python 3.10 trở lên** (Đã kiểm thử và tối ưu trên Python 3.13):

```bash
# Clone repository
git clone https://github.com/ngnsusinn/quesy.git
cd quesy

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

### 3.2. Cấu Hình Biến Môi Trường (Tùy chọn)
Tạo file `.env` tại thư mục gốc (tham khảo `.env.example`):
```env
# AI Provider (gemini, openai, anthropic, openrouter)
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash
AI_API_KEY=your_api_key_here
```
*Lưu ý: Nếu không cấu hình API Key, hệ thống vẫn hoạt động bình thường với bộ phân giải và xử lý cục bộ (Offline Rule Engine).*

### 3.3. Khởi Chạy Hệ Thống
Chạy script tự động phát hiện cổng và giải phóng cổng bận:

```bash
python start_server.py
```

Truy cập trên trình duyệt:
* **Ứng dụng Web Studio:** `http://127.0.0.1:8000` (hoặc `/digitize`, `/bank`, `/matrix`, `/shuffler`)
* **Tài liệu Swagger API:** `http://127.0.0.1:8000/docs`
* **Kiểm tra sức khỏe hệ thống:** `http://127.0.0.1:8000/health`

### 3.4. Chạy Bằng Docker
```bash
docker-compose up --build
```

---

## 4. BỘ KIỂM THỬ TỰ ĐỘNG (AUTOMATED TEST SUITE)

Hệ thống sở hữu bộ kiểm thử tự động toàn diện gồm **46 kịch bản kiểm thử (100% PASSED)**:

```bash
pytest -v
```

### Báo Cáo Kết Quả Kiểm Thử Thực Tế:
* `test_taxonomy.py`: Xác minh phân cấp cây kiến thức 6 tầng khoa học, chuẩn hóa theo năng lực và tuyệt đối độc lập, không bị ràng buộc bởi các bộ SGK riêng lẻ (PASS).
* `test_rules_shuffling.py`:
  * **RULE-01:** Kiểm thử toàn bộ 16 tổ hợp Đúng/Sai 4 khẳng định có tính điểm bậc thang (PASS).
  * **RULE-02:** Chạy 100 lần hoán vị mã đề, đảm bảo phương án *"Cả A và B đều đúng"* **luôn khóa ở vị trí D trong 100% mã đề** (PASS).
  * **RULE-03:** Đảm bảo câu hỏi chùm và đoạn văn ngữ cảnh không bị phân tách trong mọi mã đề (PASS).
* `test_ai_pipeline.py`: Kiểm thử chuyển đổi công thức LaTeX, giải mã MathType MTEF, 4 quy tắc toán học, render đồ thị vector TikZ SVG, bảo vệ text mode và tự động chuẩn hóa dấu ngoặc (PASS).
* `test_cloud_vision_adapter.py`: Kiểm thử tự động nhận diện AI Provider (Gemini / OpenAI / Claude) và chuẩn hóa cấu trúc JSON (PASS).
* `test_excel_roster_import_export.py`: Kiểm tra xuất nhập danh sách lớp học và bảng điểm CSV/Excel UTF-8 BOM chuẩn font tiếng Việt (PASS).
* `test_deduplication.py`: Xác minh thuật toán Cosine Similarity chặn lưu và cảnh báo khi câu hỏi trùng lặp $\ge 0.90$ (PASS).
* `test_docx_export.py`: Kiểm tra xuất file Word 2 cột với công thức toán OMML OpenXML bản địa (PASS).
* `test_performance_budgets.py`: Đảm bảo độ trễ phản hồi thuật toán dưới 200ms (PASS).
* `test_e2e_workflow.py`: Kiểm thử quy trình khép kín end-to-end từ số hóa, tạo ma trận, trộn đề, xuất bản và chấm điểm (PASS).

---

## 5. GIẤY PHÉP & ĐÓNG GÓP

* **Giấy phép:** Phát hành theo giấy phép MIT License mở, tự do sử dụng và triển khai cho giáo viên và các cơ sở giáo dục.
* **Đóng góp phát triển:** Mọi đóng góp về cải tiến thuật toán, bổ sung mẫu đồ thị TikZ hoặc báo lỗi đều được hoan nghênh qua GitHub Pull Requests và Issues.
