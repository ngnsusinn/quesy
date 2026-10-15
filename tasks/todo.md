# Quesy Project: Master Task Breakdown & Checklist

> **Ghi chú chuẩn hóa:** Bản phân rã công việc tuân thủ 100% hướng dẫn kỹ năng `planning-and-task-breakdown` và quy chuẩn khảo thí Thông tư 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT, Quyết định 764/QĐ-BGDĐT.

---

## Phase 1: Nền Tảng Danh Mục & Ngân Hàng Câu Hỏi Chuẩn Thông Tư 32

### Task 01: [DONE] Thiết kế CSDL & Cây Phân Cấp Kiến Thức 6 Tầng Chuẩn Thông Tư 32
**Description:** Xây dựng mô hình dữ liệu quan hệ cho danh mục phân loại kiến thức theo chương trình GDPT 2018 gồm 6 tầng: Cấp học/Lớp $\rightarrow$ Môn học $\rightarrow$ Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ Yêu cầu cần đạt (YCCĐ) và tầng Dạng câu hỏi (Problem Archetype), tuyệt đối không phân chia theo bộ sách giáo khoa thương mại.

**Acceptance criteria:**
- [x] Mô hình CSDL có đầy đủ các thực thể: `Grade`, `Subject`, `ContentStrand`, `Topic`, `Lesson`, `LearningOutcome`, `ProblemArchetype`.
- [x] Không tồn tại bất kỳ trường thông tin hay khóa ngoại nào liên quan đến "Bộ sách" (`textbook_edition`).
- [x] Cung cấp đầy đủ REST API CRUD lấy cây danh mục phân cấp theo định dạng lồng nhau (nested tree).

**Verification:**
- [x] Tests pass: `pytest tests/test_taxonomy.py`
- [x] Build succeeds: `python -c "import backend.models"`
- [x] Manual check: Gọi `GET /api/v1/taxonomy/tree` trả về cây JSON 6 tầng chuẩn hóa.

**Dependencies:** None  
**Files likely touched:**
- `backend/models.py`
- `backend/schemas.py`
- `backend/routers/taxonomy.py`
**Estimated scope:** Medium (3 files)

---

### Task 02: [DONE] Xây Dựng API Quản Lý Ngân Hàng Câu Hỏi & 5 Thể Thức Khảo Thí
**Description:** Xây dựng hệ thống bảng dữ liệu và REST API quản lý câu hỏi hỗ trợ các thể thức khảo thí theo Quyết định 764/QĐ-BGDĐT: Trắc nghiệm 4 lựa chọn (`SINGLE_CHOICE`), Đúng/Sai 4 khẳng định (`TRUE_FALSE_GROUP`), Trả lời ngắn (`SHORT_ANSWER`), Câu hỏi chùm (`PASSAGE_GROUP`) và Tự luận (`ESSAY`).

**Acceptance criteria:**
- [x] Bảng `questions`, `options`, `sub_statements` liên kết toàn vẹn với `learning_outcomes` và `problem_archetypes`.
- [x] Thể thức Đúng/Sai lưu trữ 4 ý a), b), c), d) độc lập kèm trạng thái `is_true`.
- [x] Cung cấp các endpoint CRUD: `GET /api/v1/questions`, `POST /api/v1/questions`, `DELETE /api/v1/questions/{id}`.

**Verification:**
- [x] Tests pass: `pytest tests/test_api_endpoints.py::test_api_questions_crud`
- [x] Contract validation: `pytest tests/test_api_contracts_and_negatives.py`
- [x] Manual check: Tạo câu hỏi Đúng/Sai 4 khẳng định qua API trả về HTTP 201.

**Dependencies:** Task 01  
**Files likely touched:**
- `backend/models.py`
- `backend/schemas.py`
- `backend/routers/questions.py`
**Estimated scope:** Medium (3 files)

---

### Task 03: [DONE] Xây Dựng Động Cơ Chống Trùng Lặp Câu Hỏi (Cosine Similarity)
**Description:** Hiện thực hóa thuật toán kiểm tra tương đồng ngữ nghĩa và công thức toán học giữa câu hỏi mới và toàn bộ câu hỏi trong ngân hàng dữ liệu để ngăn chặn trùng lặp đề thi.

**Acceptance criteria:**
- [x] Tính toán vector embedding văn bản câu hỏi và chuẩn hóa vector.
- [x] Tính khoảng cách Cosine Similarity giữa câu hỏi mới và kho câu hỏi.
- [x] Cảnh báo nếu tương đồng $\ge 80\%$, và chặn lưu nếu tương đồng $\ge 90\%$.

**Verification:**
- [x] Tests pass: `pytest tests/test_deduplication.py`
- [x] Manual check: Thử chèn một câu hỏi có nội dung giống 95% câu đã có, hệ thống phát hiện và cảnh báo chính xác.

**Dependencies:** Task 02  
**Files likely touched:**
- `backend/services/ai_parser.py`
- `backend/routers/questions.py`
**Estimated scope:** Small (2 files)

---

### Task 04: [DONE] Xây Dựng Giao Diện Web Quản Trị Ngân Hàng Câu Hỏi KaTeX
**Description:** Xây dựng giao diện Web Studio trực quan cho phép giáo viên tra cứu, tìm kiếm, lọc câu hỏi theo cây danh mục kiến thức Thông tư 32, xem công thức toán KaTeX hiển thị sắc nét và gắn nhãn câu hỏi.

**Acceptance criteria:**
- [x] Bảng câu hỏi hiển thị đầy đủ công thức toán KaTeX inline `$..$` và block `$$..$$`.
- [x] Bộ lọc đa tiêu chí: Môn học, Khối lớp, Mạch nội dung, Mức độ nhận thức (Biết, Hiểu, Vận dụng).
- [x] Hiển thị rõ ràng 3 thể thức câu hỏi của định dạng 2025.

**Verification:**
- [x] Browser check: Mở tab "Ngân hàng câu hỏi" trên trình duyệt `http://127.0.0.1:8000`.
- [x] Manual check: Thử chọn lọc Mức độ nhận thức "VẬN DỤNG", bảng chỉ hiển thị các câu tương ứng.

**Dependencies:** Task 01, Task 02  
**Files likely touched:**
- `frontend/index.html`
- `frontend/static/app.js`
**Estimated scope:** Small (2 files)

---

### Checkpoint 1: Foundation Milestone Completed
- [x] Đã nạp thành công bộ hạt giống 54 câu hỏi chuẩn hóa Thông tư 32 (`backend/seed_data.py`).
- [x] Toàn bộ các kiểm thử danh mục và hợp đồng dữ liệu pass 100%.

---

## Phase 2: Pipeline Tiếp Nhận & Studio Hậu Kiểm AI (HITL Studio)

### Task 05: [DONE] Xây Dựng Pipeline Bóc Tách Tài Liệu (AI Parsing Service)
**Description:** Xây dựng background worker bóc tách nội dung đề thi từ file PDF và Word DOCX, tự động trích xuất các công thức MathType/LaTeX và cấu trúc các phần trong đề thi.

**Acceptance criteria:**
- [x] Trích xuất văn bản có cấu trúc từ file PDF bằng PyPDF/OCR và DOCX qua python-docx.
- [x] Chuẩn hóa công thức toán sang định dạng LaTeX KaTeX (`$x^2 + y^2 = R^2$`).
- [x] Nhận diện và phân tách 3 phần: Phần I, Phần II (Đúng/Sai), Phần III (Trả lời ngắn).

**Verification:**
- [x] Tests pass: `pytest tests/test_ai_pipeline.py::test_pdf_parsing`
- [x] Tests pass: `pytest tests/test_ai_pipeline.py::test_latex_converter`

**Dependencies:** Task 02  
**Files likely touched:**
- `backend/services/ai_parser.py`
- `backend/routers/digitize.py`
**Estimated scope:** Medium (3 files)

---

### Task 06: [DONE] Pipeline Tự Động Cắt Ảnh Đồ Thị & Gợi Ý Gán Nhãn AI (Auto-tagging)
**Description:** Tự động phát hiện các vùng đồ thị, hình vẽ hình học trong tài liệu đề thi, tự động cắt ảnh theo bounding box lưu trữ dạng WebP tối ưu dung lượng và gợi ý gán nhãn YCCĐ.

**Acceptance criteria:**
- [x] Cắt ảnh chính xác theo tọa độ Bounding Box và lưu vào `storage/assets/{job_id}/img_{uuid}.webp`.
- [x] Trả về link ảnh nhúng trong thân câu hỏi `image_urls`.
- [x] AI gợi ý Mức độ nhận thức (Biết, Hiểu, Vận dụng) và mã YCCĐ tương ứng.

**Verification:**
- [x] Tests pass: `pytest tests/test_ai_pipeline.py::test_crop_service`
- [x] Tests pass: `pytest tests/test_ai_pipeline.py::test_tagging_service`

**Dependencies:** Task 05  
**Files likely touched:**
- `backend/services/ai_parser.py`
**Estimated scope:** Small (2 files)

---

### Task 07: [DONE] Xây Dựng Studio Hậu Kiểm Đối Chiếu Song Song (Side-by-Side Review)
**Description:** Xây dựng giao diện màn hình kép (50% tài liệu gốc - 50% câu hỏi đã bóc tách) kèm thanh đo độ tin cậy AI (Confidence Barometer) và tính năng cuộn đồng bộ (Synchronized Scrolling).

**Acceptance criteria:**
- [x] Giao diện chia 2 cột đối xứng mượt mà, responsive.
- [x] Cột đo độ tin cậy hiển thị 3 dải màu: Xanh ($\ge 95\%$), Vàng ($80-94\%$), Đỏ ($< 80\%$).
- [x] Thao tác click vào câu hỏi bên phải làm nổi bật vùng nội dung tương ứng bên trái.

**Verification:**
- [x] Browser check: Mở tab "Số hoá AI HITL Studio" trên trình duyệt, tải tài liệu mẫu và kiểm tra cuộn đồng bộ.
- [x] UI snapshot check: Bố cục render chuẩn CSS Tailwind.

**Dependencies:** Task 05, Task 06  
**Files likely touched:**
- `frontend/index.html`
- `frontend/static/app.js`
**Estimated scope:** Medium (2 files)

---

### Task 08: [DONE] Xây Dựng Modal Biên Tập Nhanh Công Thức Toán LaTeX & KaTeX Live
**Description:** Xây dựng cửa sổ popup biên tập nhanh cho phép giáo viên chỉnh sửa mã LaTeX với live preview KaTeX trực tiếp mà không cần tải lại trang.

**Acceptance criteria:**
- [x] Modal popup mở ra khi nhấn vào nút biên tập công thức trên từng câu hỏi hoặc phương án.
- [x] Gõ mã LaTeX đến đâu, khung preview KaTeX bên dưới hiển thị công thức vector đến đó theo thời gian thực.
- [x] Nút "Áp dụng" cập nhật ngay lập tức vào trạng thái câu hỏi trong phiên làm việc.

**Verification:**
- [x] Manual check: Mở modal công thức, nhập `\int_{0}^{1} x^2 dx = \frac{1}{3}`, công thức hiển thị đúng tức thì.

**Dependencies:** Task 07  
**Files likely touched:**
- `frontend/index.html`
- `frontend/static/app.js`
**Estimated scope:** Small (2 files)

---

### Checkpoint 2: AI Digitization Milestone Completed
- [x] Pipeline số hóa trọn vẹn từ file gốc đến bóc tách công thức, cắt ảnh đồ thị và đưa lên Studio hậu kiểm.
- [x] Bộ test `tests/test_ai_pipeline.py` hoàn thành 100% không có lỗi.

---

## Phase 3: Ma Trận Đề Thi & Động Cơ Trộn Đề An Toàn

### Task 09: [DONE] Xây Dựng Module Thiết Lập Bản Đặc Tả Ma Trận Đề Thi Theo YCCĐ
**Description:** Xây dựng module cấu hình ma trận đề thi chuẩn mực giáo dục theo trục dọc (Mạch nội dung $\rightarrow$ YCCĐ $\rightarrow$ Dạng bài) và trục ngang (3 mức độ nhận thức: Biết, Hiểu, Vận dụng), tích hợp cảnh báo số dư kho câu hỏi khả dụng.

**Acceptance criteria:**
- [x] Bảng cấu hình lưu trữ tỷ lệ điểm số và số lượng câu hỏi từng ô ma trận.
- [x] Kiểm tra và hiển thị tức thời số lượng câu hỏi thực tế đang có trong kho ứng với từng ô.
- [x] Cảnh báo nếu số lượng câu hỏi trong kho không đủ để sinh đề.

**Verification:**
- [x] Tests pass: `pytest tests/test_api_endpoints.py::test_api_matrix_creation`
- [x] Tests pass: `pytest tests/test_services.py::test_matrix_solver_exclusion_and_inventory_warning`

**Dependencies:** Task 01, Task 02  
**Files likely touched:**
- `backend/models.py`
- `backend/schemas.py`
- `backend/routers/matrix.py`
- `backend/services/matrix_solver.py`
**Estimated scope:** Medium (4 files)

---

### Task 10: [DONE] Xây Dựng Thuật Toán Sinh Đề Gốc Cân Bằng Kho & Loại Trừ Câu Đã Thi
**Description:** Xây dựng động cơ sinh đề gốc (`MasterExam`) sử dụng thuật toán chọn lọc ngẫu nhiên có trọng số đáp ứng đúng các ràng buộc của ma trận và tự động loại trừ các câu hỏi đã xuất hiện trong các kỳ thi gần nhất (cooldown).

**Acceptance criteria:**
- [x] Sinh ra đề gốc có đủ số lượng câu hỏi đúng theo tỷ lệ nhận thức và thể thức quy định.
- [x] Tự động loại trừ các câu hỏi nằm trong danh sách câu hỏi loại trừ (đã thi).
- [x] Trả về HTTP 400 kèm thông báo rõ ràng nếu kho câu hỏi không đủ đáp ứng ma trận.

**Verification:**
- [x] Tests pass: `pytest tests/test_api_contracts_and_negatives.py::test_negative_generate_exam_with_excessive_inventory_requirement_returns_400`
- [x] Tests pass: `pytest tests/test_e2e_workflow.py`

**Dependencies:** Task 09  
**Files likely touched:**
- `backend/services/matrix_solver.py`
- `backend/routers/exams.py`
**Estimated scope:** Small (2 files)

---

### Task 11: [DONE] Xây Dựng Động Cơ Trộn Đề Hoán Vị An Toàn (4 Quy Tắc Khảo Thí)
**Description:** Phát triển động cơ trộn đề chuyên dụng đảm bảo 4 nguyên tắc vàng trong khảo thí: (1) Section Integrity, (2) Passage Integrity, (3) Option Anchor Rule (khóa cố định các đáp án "Tất cả các ý trên" vào vị trí D), và (4) Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu giữa các mã đề.

**Acceptance criteria:**
- [x] Quy tắc chấm điểm lũy tiến RULE-01 cho câu hỏi Đúng/Sai (0.1, 0.25, 0.5, 1.0 điểm).
- [x] RULE-02: Phương án chứa từ khóa neo hoặc có cờ `is_fixed=True` luôn nằm ở vị trí D trong 100% các mã đề hoán vị.
- [x] RULE-03: Ngữ liệu bài đọc chung và các câu hỏi con luôn đi liền kề nhau.
- [x] Tự động sinh bảng ma trận đáp án đối chiếu giữa đề gốc và các mã đề hoán vị (101, 102, 103, 104).

**Verification:**
- [x] Tests pass: `pytest tests/test_rules_shuffling.py` (chạy 100 vòng lặp kiểm thử Rule 02).
- [x] Tests pass: `pytest tests/test_performance_budgets.py::test_perf_budget_shuffling_engine`

**Dependencies:** Task 10  
**Files likely touched:**
- `backend/services/shuffling_engine.py`
- `backend/routers/exams.py`
**Estimated scope:** Medium (3 files)

---

### Task 12: [DONE] Xây Dựng Thuật Toán Phân Tích Chất Lượng Câu Hỏi Hậu Kiểm (CTT: p, D)
**Description:** Xây dựng module trắc lượng học cổ điển tính toán độ khó thực tế ($p$) và độ phân biệt ($D$) của từng câu hỏi từ kết quả thi của học sinh, gắn cờ cảnh báo câu hỏi lỗi nếu $D < 0.20$.

**Acceptance criteria:**
- [x] Tính toán đúng chỉ số độ khó $p = R/N$ ($0 \le p \le 1$).
- [x] Tính toán đúng độ phân biệt $D = P_H - P_L$ dựa trên nhóm $27\%$ điểm cao nhất và $27\%$ điểm thấp nhất.
- [x] Gắn cờ cảnh báo `QUESTION_DEFECTIVE` khi $D < 0.20$.

**Verification:**
- [x] Tests pass: `pytest tests/test_api_endpoints.py`
- [x] Tests pass: `pytest tests/test_services.py`

**Dependencies:** Task 11  
**Files likely touched:**
- `backend/services/analytics.py`
- `backend/routers/exams.py`
**Estimated scope:** Small (2 files)

---

### Checkpoint 3: Assessment Core Milestone Completed
- [x] Động cơ sinh đề và trộn mã đề an toàn vận hành hoàn hảo với cả 4 nguyên tắc khảo thí.
- [x] Toàn bộ test suite `test_rules_shuffling.py` và `test_services.py` đạt 100%.

---

## Phase 4: Xuất Bản In Ấn Đa Định Dạng & Kiểm Thử Toàn Diện

### Task 13: [DONE] Dịch Vụ Xuất Bản Microsoft Word OpenXML (.docx) Chuẩn Khảo Thí
**Description:** Xây dựng dịch vụ kết xuất đề thi ra file Word OpenXML (.docx) chuẩn quốc tế, bố cục 2 cột chuyên nghiệp tiết kiệm giấy in, bảng phách thông tin thí sinh và công thức Toán OMML native.

**Acceptance criteria:**
- [x] File sinh ra là tệp nén OpenXML ZIP hợp lệ, không phải file văn bản thuần.
- [x] Bố cục 2 cột (`w:cols num="2"`) chuẩn hóa cho các trang nội dung thi.
- [x] Khung thông tin Sở/Trường, bài thi, mã đề và bảng điền số báo danh chuẩn quy cách.

**Verification:**
- [x] Tests pass: `pytest tests/test_docx_export.py`
- [x] Manual check: Mở trực tiếp các file `De_101.docx`, `LoiGiai_101.docx` trên Microsoft Word không có bất kỳ thông báo lỗi file nào.

**Dependencies:** Task 11  
**Files likely touched:**
- `backend/services/docx_exporter.py`
- `backend/routers/exams.py`
**Estimated scope:** Medium (3 files)

---

### Task 14: [DONE] Động Cơ Xuất Bản PDF Vector Siêu Tốc Thuần Python (ReportLab Unicode)
**Description:** Phát triển động cơ sinh đề thi PDF vector siêu tốc thuần Python sử dụng thư viện ReportLab, nhúng font chuẩn Times New Roman Unicode của Windows (`times.ttf`), tối ưu hóa thời gian sinh PDF xuống dưới 100ms mà không bị treo hay timeout.

**Acceptance criteria:**
- [x] Nạp trực tiếp font Windows Unicode: `times.ttf`, `timesbd.ttf`, `timesi.ttf`.
- [x] Tốc độ sinh 1 file PDF $\le 100$ms (giảm hơn 200 lần so với giải pháp gọi tiến trình Word COM).
- [x] Hiển thị sắc nét tiếng Việt có dấu, định dạng 3 phần thi, phương án lựa chọn và khung phách.
- [x] Hỗ trợ tải lẻ trực tiếp: `GET /api/v1/exams/{id}/export-pdf?variant_code=101`.

**Verification:**
- [x] Tests pass: `pytest tests/test_performance_budgets.py::test_perf_budget_docx_and_zip_export`
- [x] Browser check: Tải file PDF từ trình duyệt trong 283ms và mở hiển thị vector sắc nét.

**Dependencies:** Task 13  
**Files likely touched:**
- `backend/services/docx_exporter.py`
- `backend/routers/exams.py`
**Estimated scope:** Medium (3 files)

---

### Task 15: [DONE] Đóng Gói Xuất Bản Trọn Gói ZIP Đa Định Dạng & Cơ Chế Tải Blob
**Description:** Xây dựng API và giao diện cho phép tải gói ZIP tổng hợp theo tùy chọn định dạng (`format=all`, `format=docx`, `format=pdf`), bao gồm đầy đủ các mã đề, hướng dẫn giải chi tiết và ma trận đáp án; nâng cấp client-side sang cơ chế Blob download để loại bỏ lỗi ngắt kết nối trình duyệt.

**Acceptance criteria:**
- [x] Endpoint `GET /api/v1/exams/{id}/export-zip` hỗ trợ tham số `format=all|docx|pdf`.
- [x] File ZIP chứa đầy đủ: các file đề thi, file hướng dẫn giải chi tiết, file bảng đáp án tổng hợp (Word/PDF/CSV).
- [x] Frontend sử dụng `fetch()` + `URL.createObjectURL(blob)` kiểm tra mã phản hồi HTTP trước khi lưu, dập tắt triệt để thông báo *Failed - Unknown server error* trên Chrome.

**Verification:**
- [x] Real Browser CDP: Tải thành công gói Word ZIP và PDF ZIP trong Web Studio với Toast thông báo trạng thái.
- [x] Automated check: Giải nén gói zip kiểm tra toàn vẹn đủ 10 file nội dung.

**Dependencies:** Task 13, Task 14  
**Files likely touched:**
- `backend/services/docx_exporter.py`
- `backend/routers/exams.py`
- `frontend/static/app.js`
- `frontend/index.html`
**Estimated scope:** Medium (4 files)

---

### Task 16: [DONE] Xây Dựng Bộ Test Suite Tự Động Toàn Diện & Xử Lý Tiến Trình Windows
**Description:** Tích hợp bộ kỹ năng kiểm thử chuyên sâu (tester-skills), xây dựng 39 bài test tự động bao quát toàn bộ hợp đồng API, trường hợp biên tiêu cực, ngân sách hiệu năng và kịch bản E2E; hoàn thiện script `start_server.py` tự động phát hiện và giải phóng socket cổng 8000.

**Acceptance criteria:**
- [x] 39/39 test cases tự động chạy qua `pytest` đạt tỉ lệ pass 100%.
- [x] Script `start_server.py` tự động kiểm tra `WinError 10048`, tìm PID chiếm dụng và giải phóng cổng.
- [x] Thêm route `/favicon.ico` trả về HTTP 204 để triệt tiêu lỗi 404 trên console trình duyệt.

**Verification:**
- [x] Command verification: Chạy `pytest` $\rightarrow$ 39 passed in ~10s.
- [x] Server start verification: Chạy `python start_server.py` khởi động trơn tru không xung đột cổng.

**Dependencies:** Task 01 through Task 15  
**Files likely touched:**
- `start_server.py`
- `backend/main.py`
- `tests/*`
**Estimated scope:** Large (8+ files)

---

### Checkpoint 4: Production Export & Testing Milestone Completed
- [x] Toàn bộ 16 tác vụ cốt lõi đã hoàn tất, đạt 100% tiêu chí nghiệm thu.
- [x] Hệ thống vận hành ổn định trên môi trường máy chủ Windows và đã kiểm chứng thành công trên Real Browser.

---

## Phase 5: Mở Rộng Doanh Nghiệp & Đám Mây (Future Roadmap / Backlog)

### Task 17: [ ] Tích Hợp Phân Quyền Người Dùng Đa Cấp & Đa Trường Học (Multi-Tenant RBAC)
**Description:** Mở rộng hệ thống quản lý danh tính và phân quyền theo mô hình RBAC (Role-Based Access Control) cho các đối tượng: Quản trị viên Sở/Phòng GD&ĐT, Hiệu trưởng, Tổ trưởng bộ môn, Giáo viên bộ môn và Cán bộ khảo thí, hỗ trợ dữ liệu cách ly theo trường học (Multi-tenancy).

**Acceptance criteria:**
- [ ] Phân quyền chặt chẽ: Giáo viên chỉ chỉnh sửa câu hỏi do mình biên soạn hoặc câu hỏi ở trạng thái `DRAFT`; Tổ trưởng bộ môn duyệt câu hỏi lên `APPROVED`.
- [ ] Xác thực bằng JWT Token kèm hỗ trợ Single Sign-On (OAuth2 Google / Microsoft Azure AD).
- [ ] Cô lập dữ liệu giữa các trường học thông qua trường `institution_id`.

**Verification:**
- [ ] Tests pass: `pytest tests/test_rbac_permissions.py`
- [ ] Manual check: Giáo viên không thể duyệt câu hỏi hoặc chỉnh sửa đề thi của tổ chuyên môn khác.

**Dependencies:** Task 02, Task 16  
**Files likely touched:**
- `backend/models.py`
- `backend/auth.py`
- `backend/routers/auth.py`
- `backend/routers/questions.py`
**Estimated scope:** Medium (4 files)

---

### Task 18: [ ] Tích Hợp Multimodal Vision Cloud API (Gemini Vision / Claude 3.5 Sonnet / DocTR)
**Description:** Tích hợp trực tiếp các API thị giác máy tính cao cấp (Google Gemini 1.5 Pro Vision, Anthropic Claude 3.5 Sonnet) và pipeline DocTR mã nguồn mở để nâng cao tỷ lệ nhận diện chữ viết tay, hình học không gian phức tạp và công thức mờ từ ảnh chụp điện thoại.

**Acceptance criteria:**
- [ ] Bổ sung adapter `CloudVisionParser` cho phép cấu hình API Key linh hoạt qua biến môi trường.
- [ ] Nhận diện chính xác hình học không gian và biểu thức tích phân 2 lớp với độ tin cậy $> 92\%$.
- [ ] Cơ chế Circuit Breaker tự động chuyển đổi sang Local Parser nếu Cloud API bị nghẽn mạng hoặc hết hạn mức.

**Verification:**
- [ ] Tests pass: `pytest tests/test_vision_llm_adapters.py`
- [ ] Manual check: Tải lên ảnh chụp đề thi chụp nghiêng bằng điện thoại, hệ thống tự nắn thẳng và bóc tách đầy đủ.

**Dependencies:** Task 05, Task 06  
**Files likely touched:**
- `backend/services/ai_parser.py`
- `backend/config.py`
**Estimated scope:** Medium (3 files)

---

### Task 19: [ ] Phân Hệ Thi Trực Tuyến Học Sinh (Online CBT Exam Taker) & Chống Gian Lận
**Description:** Xây dựng phân hệ giao diện làm bài thi trực tuyến trên máy tính/điện thoại cho học sinh (Computer-Based Testing) với đồng hồ đếm ngược, tự động nộp bài khi hết giờ, xáo trộn câu hỏi ngẫu nhiên và cơ chế cảnh báo khi chuyển tab.

**Acceptance criteria:**
- [ ] Giao diện làm bài thi thân thiện với học sinh, tương thích mọi thiết bị di động.
- [ ] Hỗ trợ đầy đủ 3 phần trắc nghiệm mới (chọn 1, đúng/sai, điền kết quả ngắn).
- [ ] Cơ chế tự động lưu bài làm mỗi 15 giây qua WebSocket/LocalStorage chống mất bài khi mất mạng.
- [ ] Ghi log hành vi thí sinh: số lần rời màn hình thi, số lần chuyển tab trình duyệt.

**Verification:**
- [ ] Tests pass: `pytest tests/test_cbt_engine.py`
- [ ] Manual check: Giả lập ngắt kết nối mạng giữa chừng, câu trả lời của thí sinh vẫn được giữ nguyên vẹn.

**Dependencies:** Task 11, Task 17  
**Files likely touched:**
- `frontend/cbt_taker.html`
- `frontend/static/cbt_app.js`
- `backend/routers/cbt.py`
**Estimated scope:** Large (5 files)

---

### Task 20: [ ] Phân Hệ Chấm Phiếu Trả Lời Trắc Nghiệm Tự Động OMR Qua Webcam / Scanner
**Description:** Xây dựng module xử lý ảnh thị giác máy tính OpenCV nhận diện và chấm điểm tự động phiếu trả lời trắc nghiệm theo mẫu mới năm 2025 thông qua máy quét tài liệu hoặc camera điện thoại/webcam.

**Acceptance criteria:**
- [ ] Căn chỉnh phiếu thi tự động qua 4 điểm mốc định vị góc (Corner Fiducials Detection).
- [ ] Nhận diện chính xác vị trí tô đen bút chì $2B$ cho cả 3 phần: Phần I (A,B,C,D), Phần II (Đ/S), Phần III (Tô số).
- [ ] Áp dụng đúng quy tắc chấm lũy tiến RULE-01 cho Phần II và xuất bảng điểm trực tiếp vào module CTT Analytics.

**Verification:**
- [ ] Tests pass: `pytest tests/test_omr_grading.py`
- [ ] Manual check: Quét ảnh chụp 10 phiếu thi mẫu, tỷ lệ nhận diện đúng dấu tô đen đạt $\ge 99.5\%$.

**Dependencies:** Task 11, Task 12  
**Files likely touched:**
- `backend/services/omr_engine.py`
- `backend/routers/grading.py`
**Estimated scope:** Medium (4 files)

---

### Task 21: [ ] Đóng Gói Docker Container, K8s Helm Chart & CI/CD GitHub Actions
**Description:** Xây dựng quy trình DevOps chuẩn hóa: viết Dockerfile đa tầng (Multi-stage build), docker-compose liên kết SQLite/PostgreSQL + Redis, tài liệu triển khai Kubernetes Helm Chart và pipeline GitHub Actions tự động kiểm thử.

**Acceptance criteria:**
- [ ] `Dockerfile` đóng gói ứng dụng với dung lượng tối ưu, non-root user.
- [ ] `docker-compose.yml` khởi động toàn bộ dịch vụ (API Backend, Web Frontend, Background Worker) chỉ với 1 lệnh `docker compose up -d`.
- [ ] File `.github/workflows/ci.yml` tự động chạy 39 test cases trên mỗi lệnh git push hoặc Pull Request.

**Verification:**
- [ ] Terminal check: Chạy `docker compose config` hợp lệ.
- [ ] CI run: Pipeline GitHub Actions hoàn thành với trạng thái xanh (Passed).

**Dependencies:** Task 16  
**Files likely touched:**
- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
**Estimated scope:** Medium (3 files)

---

### Checkpoint 5: Enterprise Cloud Readiness (Planned)
- [ ] Hệ thống triển khai thành công trên môi trường cụm đám mây (Kubernetes/Docker).
- [ ] Đạt chuẩn bảo mật và kiểm thử chịu tải đáp ứng kỳ thi quy mô lớn.
