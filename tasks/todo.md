# Quesy Project: Master Micro-Task Breakdown & Checklist (v2.0)

> **Quy chuẩn kỹ năng:** Phân rã công việc vi mô (Atomic Task Breakdown) tuân thủ 100% `planning-and-task-breakdown` (SKILL.md). Mỗi task là 1 chức năng nhỏ, độc lập, có tiêu chí nghiệm thu rõ ràng, quy mô XS (1 file) hoặc S (1-2 files), tối đa M (3 files). Không có task XL.

---

## Phase 1: CSDL & Cây Kiến Thức Thông Tư 32/2018/TT-BGDĐT

### Task TS-01: [DONE] Định nghĩa ORM Model `Grade` & `Subject`
**Description:** Khai báo bảng `grades` (Khối lớp 10, 11, 12) và `subjects` (Môn học: Toán, Lý, Hóa, Sinh, Văn, Sử, Địa, Tiếng Anh) trong SQLAlchemy.
**Acceptance criteria:**
- [x] Bảng có các cột `id` (UUID), `code`, `name`, `created_at`.
- [x] Ràng buộc `code` là duy nhất (`unique=True`).
**Verification:** `python -c "from backend.models import Grade, Subject; print('OK')"`
**Dependencies:** None | **Files:** `backend/models.py` | **Scope:** XS (1 file)

### Task TS-02: [DONE] Định nghĩa ORM Model `ContentStrand` & `Topic`
**Description:** Khai báo bảng `content_strands` (Mạch nội dung TT 32) và `topics` (Chủ đề học tập) có khóa ngoại liên kết phân tầng.
**Acceptance criteria:**
- [x] `ContentStrand` thuộc `Subject` và `Grade`.
- [x] `Topic` thuộc `ContentStrand` với quan hệ cascade delete.
**Verification:** `python -c "from backend.models import ContentStrand, Topic; print('OK')"`
**Dependencies:** TS-01 | **Files:** `backend/models.py` | **Scope:** XS (1 file)

### Task TS-03: [DONE] Định nghĩa ORM Model `Lesson` & `LearningOutcome` (Mã YCCĐ TT 32)
**Description:** Khai báo bảng `lessons` (Bài học) và `learning_outcomes` (Yêu cầu cần đạt chuẩn Thông tư 32 kèm mã định danh chuẩn hóa e.g. `TOAN12.GT.01`).
**Acceptance criteria:**
- [x] Cột `code` lưu mã YCCĐ chuẩn hóa không trùng lặp.
- [x] Cột `description` lưu đầy đủ văn bản mô tả năng lực học sinh cần đạt.
**Verification:** `python -c "from backend.models import Lesson, LearningOutcome; print('OK')"`
**Dependencies:** TS-02 | **Files:** `backend/models.py` | **Scope:** XS (1 file)

### Task TS-04: [DONE] Định nghĩa ORM Model `ProblemArchetype` (Dạng câu hỏi)
**Description:** Khai báo bảng `problem_archetypes` nằm dưới YCCĐ để phân loại các dạng bài toán chuyên đề (e.g. *Đọc bảng biến thiên tìm cực trị*, *Cực trị hàm chứa tham số m*).
**Acceptance criteria:**
- [x] Khóa ngoại `learning_outcome_id` liên kết chặt chẽ với YCCĐ cha.
- [x] Cột `archetype_name` và `typical_method` lưu hướng dẫn phương pháp giải điển hình.
**Verification:** `python -c "from backend.models import ProblemArchetype; print('OK')"`
**Dependencies:** TS-03 | **Files:** `backend/models.py` | **Scope:** XS (1 file)

### Task TS-05: [DONE] Xây dựng Pydantic Schemas cho Cây Phân Cấp Lồng Nhau
**Description:** Khai báo cấu trúc dữ liệu Pydantic v2 phản ánh cấu trúc phân cấp lồng nhau từ Grade -> Subject -> Strand -> Topic -> Lesson -> Outcome -> Archetype.
**Acceptance criteria:**
- [x] Các schema lồng nhau hợp lệ với `from_attributes=True`.
- [x] Tuyệt đối không chứa bất kỳ trường nào liên quan đến "Bộ sách giáo khoa".
**Verification:** `python -c "from backend.schemas import TaxonomyTreeResponse; print('OK')"`
**Dependencies:** TS-04 | **Files:** `backend/schemas.py` | **Scope:** XS (1 file)

### Task TS-06: [DONE] API Endpoint `GET /api/v1/taxonomy/tree`
**Description:** Viết endpoint truy vấn và trả về toàn bộ cây kiến thức phân tầng dạng JSON lồng nhau phục vụ bộ lọc client.
**Acceptance criteria:**
- [x] Trả về mã HTTP 200 kèm cây danh mục hoàn chỉnh.
- [x] Hỗ trợ query params `subject_id` và `grade_id` để lọc nhánh nhanh.
**Verification:** `pytest tests/test_taxonomy.py`
**Dependencies:** TS-05 | **Files:** `backend/routers/taxonomy.py` | **Scope:** S (1 file)

### Task TS-07: [DONE] API Endpoints Danh sách Môn học & Khối lớp
**Description:** Cung cấp 2 API nhẹ `GET /api/v1/taxonomy/subjects` và `GET /api/v1/taxonomy/grades` để điền nhanh dropdown chọn lọc ở client.
**Acceptance criteria:**
- [x] Trả về danh sách môn học và khối lớp có trạng thái hoạt động.
**Verification:** `pytest tests/test_api_endpoints.py`
**Dependencies:** TS-01 | **Files:** `backend/routers/taxonomy.py` | **Scope:** XS (1 file)

### Task TS-08: [DONE] Nạp Dữ Liệu Hạt Giống Danh Mục Toán 12 Chuẩn Thông Tư 32
**Description:** Viết script nạp đầy đủ danh mục môn Toán 12 gồm 4 mạch nội dung, 8 chủ đề, các bài học và danh sách mã YCCĐ chuẩn Bộ GD&ĐT.
**Acceptance criteria:**
- [x] Nạp dữ liệu tự động khi CSDL chưa có dữ liệu danh mục.
- [x] Mã YCCĐ tuân thủ đúng cú pháp quy định (ví dụ `TOAN12.GT.01`, `TOAN12.HH.02`).
**Verification:** `pytest tests/test_taxonomy.py::test_yccd_code_format_validation`
**Dependencies:** TS-06 | **Files:** `backend/seed_data.py` | **Scope:** S (1 file)

### Task TS-09: [DONE] Automated Test Kiểm Tra Cây Danh Mục & Kiểm Tra Vắng Mặt Bộ Sách
**Description:** Viết unit test tự động xác nhận tính toàn vẹn 6 tầng phân cấp và khẳng định không có trường bộ sách giáo khoa thương mại.
**Acceptance criteria:**
- [x] Test `test_absence_of_textbook_edition_field` pass.
- [x] Test `test_taxonomy_6_level_hierarchy` pass.
**Verification:** `pytest tests/test_taxonomy.py`
**Dependencies:** TS-08 | **Files:** `tests/test_taxonomy.py` | **Scope:** S (1 file)

---

## Phase 2: Ngân Hàng Câu Hỏi & Động Cơ Chống Trùng Lặp

### Task IB-01: [DONE] Định nghĩa ORM Models `Question`, `Option`, `SubStatement`
**Description:** Thiết kế các bảng CSDL lưu trữ nội dung câu hỏi, phương án lựa chọn và các khẳng định con theo Quyết định 764/QĐ-BGDĐT.
**Acceptance criteria:**
- [x] `Question` liên kết với `LearningOutcome` và `ProblemArchetype`.
- [x] `SubStatement` lưu 4 ý khẳng định độc lập cho thể thức Đúng/Sai.
**Verification:** `python -c "from backend.models import Question, Option, SubStatement; print('OK')"`
**Dependencies:** TS-04 | **Files:** `backend/models.py` | **Scope:** S (1 file)

### Task IB-02: [DONE] Định nghĩa Enums `ItemFormat` cho 5 Thể Thức Khảo Thí
**Description:** Khai báo enum chuẩn hóa `SINGLE_CHOICE`, `TRUE_FALSE_GROUP`, `SHORT_ANSWER`, `PASSAGE_GROUP`, `ESSAY`.
**Acceptance criteria:**
- [x] Enum tích hợp trong Pydantic và SQLAlchemy validation.
- [x] Trả về HTTP 422 khi nhận thể thức câu hỏi không hợp lệ.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py::test_negative_create_question_with_invalid_format_returns_422`
**Dependencies:** IB-01 | **Files:** `backend/models.py`, `backend/schemas.py` | **Scope:** S (2 files)

### Task IB-03: [DONE] Định nghĩa Enums `CognitiveLevel` Theo 3 Mức Độ Nhận Thức TT 32
**Description:** Khai báo enum 3 mức độ nhận thức chuẩn hóa Thông tư 32: `KNOWLEDGE` (Biết), `COMPREHENSION` (Hiểu), `APPLICATION` (Vận dụng).
**Acceptance criteria:**
- [x] Loại bỏ phân chia 4 mức độ cũ (gộp Vận dụng & Vận dụng cao thành Vận dụng).
- [x] Ràng buộc chặt chẽ trong model và schema.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py`
**Dependencies:** IB-01 | **Files:** `backend/models.py`, `backend/schemas.py` | **Scope:** S (2 files)

### Task IB-04: [DONE] Pydantic Validator cho Câu Hỏi Đúng/Sai 4 Khẳng Định
**Description:** Viết custom validator đảm bảo câu hỏi `TRUE_FALSE_GROUP` luôn có đúng 4 khẳng định a), b), c), d) và mỗi khẳng định có giá trị `is_true`.
**Acceptance criteria:**
- [x] Từ chối lưu và trả về HTTP 422 nếu số lượng khẳng định khác 4.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py`
**Dependencies:** IB-02 | **Files:** `backend/schemas.py` | **Scope:** XS (1 file)

### Task IB-05: [DONE] API `POST /api/v1/questions` Tạo Mới Câu Hỏi
**Description:** Endpoint tạo mới câu hỏi, tự động lưu options và sub_statements trong transaction nguyên tử.
**Acceptance criteria:**
- [x] Tạo câu hỏi thành công trả về HTTP 201 kèm ID định danh.
- [x] Hỗ trợ lưu thân câu hỏi có chứa công thức LaTeX và mã ảnh.
**Verification:** `pytest tests/test_api_endpoints.py::test_api_questions_crud`
**Dependencies:** IB-04 | **Files:** `backend/routers/questions.py` | **Scope:** S (1 file)

### Task IB-06: [DONE] API `GET /api/v1/questions` Tra Cứu, Lọc & Phân Trang
**Description:** Endpoint lấy danh sách câu hỏi hỗ trợ lọc đa tiêu chí: môn học, khối lớp, YCCĐ, mức độ nhận thức, thể thức và phân trang (`skip`, `limit`).
**Acceptance criteria:**
- [x] Phân trang mặc định 20 câu/trang.
- [x] Lọc chính xác theo query parameters.
**Verification:** `pytest tests/test_api_endpoints.py`
**Dependencies:** IB-05 | **Files:** `backend/routers/questions.py` | **Scope:** S (1 file)

### Task IB-07: [DONE] API `GET /api/v1/questions/{id}` Xem Chi Tiết Câu Hỏi
**Description:** Endpoint lấy thông tin chi tiết một câu hỏi bao gồm đầy đủ danh sách phương án, các ý đúng sai và lời giải chi tiết.
**Acceptance criteria:**
- [x] Trả về HTTP 404 có cấu trúc rõ ràng nếu ID không tồn tại.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py::test_negative_get_question_not_found_returns_consistent_error_shape`
**Dependencies:** IB-05 | **Files:** `backend/routers/questions.py` | **Scope:** XS (1 file)

### Task IB-08: [DONE] API `PUT /api/v1/questions/{id}` Cập Nhật Câu Hỏi
**Description:** Endpoint cho phép chỉnh sửa nội dung thân câu hỏi, đáp án, mức độ nhận thức và lời giải.
**Acceptance criteria:**
- [x] Cập nhật thành công trả về HTTP 200 kèm dữ liệu mới nhất.
**Verification:** `pytest tests/test_api_endpoints.py`
**Dependencies:** IB-07 | **Files:** `backend/routers/questions.py` | **Scope:** S (1 file)

### Task IB-09: [DONE] API `DELETE /api/v1/questions/{id}` Xóa Câu Hỏi (Idempotent)
**Description:** Endpoint xóa câu hỏi khỏi ngân hàng dữ liệu đảm bảo tính lũy nghiệm (idempotency).
**Acceptance criteria:**
- [x] Xóa lần đầu thành công trả về HTTP 200.
- [x] Xóa lại lần hai trả về HTTP 404 mà không gây lỗi server.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py::test_idempotency_delete_question`
**Dependencies:** IB-07 | **Files:** `backend/routers/questions.py` | **Scope:** XS (1 file)

### Task DD-01: [DONE] Thuật Toán Chuẩn Hóa Chuỗi & Tính Vector Cosine Similarity
**Description:** Viết module tiền xử lý văn bản, loại bỏ khoảng trắng thừa, chuẩn hóa ký hiệu toán LaTeX và tính khoảng cách Cosine giữa 2 vector câu hỏi.
**Acceptance criteria:**
- [x] Trả về giá trị similarity trong khoảng [0.0, 1.0].
**Verification:** `pytest tests/test_deduplication.py::test_cosine_similarity_math`
**Dependencies:** IB-01 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task DD-02: [DONE] Logic Cảnh Báo Trùng Ngưỡng 80% & Chặn Lưu Ngưỡng 90%
**Description:** Tích hợp kiểm tra trùng lặp tự động khi lưu câu hỏi: similarity 80-89% gắn cờ cảnh báo, >= 90% chặn lưu.
**Acceptance criteria:**
- [x] Phát hiện chính xác câu hỏi trùng lặp >= 90%.
**Verification:** `pytest tests/test_deduplication.py::test_rule_05_duplicate_flagging_threshold_090`
**Dependencies:** DD-01, IB-05 | **Files:** `backend/services/ai_parser.py`, `backend/routers/questions.py` | **Scope:** S (2 files)

### Task IB-10: [DONE] Nạp Hạt Giống 54 Câu Hỏi Toán 12 Định Dạng Mới 2025
**Description:** Nạp sẵn 54 câu hỏi chất lượng cao đầy đủ 3 phần thi theo định dạng 2025 vào CSDL SQLite phục vụ kiểm thử và demo.
**Acceptance criteria:**
- [x] Đầy đủ 3 phần thi: Trắc nghiệm 4 lựa chọn, Đúng/Sai, Trả lời ngắn.
**Verification:** `pytest tests/test_e2e_workflow.py`
**Dependencies:** IB-05 | **Files:** `backend/seed_data.py` | **Scope:** S (1 file)

### Task IB-11: [DONE] Giao Diện Bảng Ngân Hàng Câu Hỏi Render KaTeX
**Description:** Xây dựng bảng hiển thị câu hỏi trên Web Studio, tự động kích hoạt KaTeX render công thức toán học inline và block.
**Acceptance criteria:**
- [x] Công thức toán hiển thị vector sắc nét không bị vỡ font.
**Verification:** Browser check tại tab "Ngân hàng câu hỏi".
**Dependencies:** IB-06 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** S (2 files)

### Task IB-12: [DONE] Bộ Lọc Giao Diện Theo Môn, Lớp, Mức Độ & YCCĐ
**Description:** Gắn sự kiện thay đổi dropdown lọc câu hỏi tức thời ở frontend mà không cần tải lại toàn bộ trang.
**Acceptance criteria:**
- [x] Chọn mức độ "Biết", bảng lập tức lọc chỉ hiển thị câu hỏi mức độ Biết.
**Verification:** Browser check tương tác trực tiếp trên giao diện.
**Dependencies:** IB-11 | **Files:** `frontend/static/app.js` | **Scope:** XS (1 file)

---

## Phase 3: Pipeline Số Hóa AI & Studio Hậu Kiểm HITL

### Task AI-01: [DONE] API `POST /api/v1/digitize/upload` Tiếp Nhận File Đề Thi
**Description:** Endpoint nhận file tải lên (.docx, .pdf, .png, .jpg), kiểm tra dung lượng <= 50MB và lưu vào thư mục `storage/uploads/`.
**Acceptance criteria:**
- [x] Từ chối các định dạng không hỗ trợ với mã lỗi HTTP 400.
- [x] Trả về `job_id` để theo dõi tiến trình bóc tách.
**Verification:** `pytest tests/test_api_endpoints.py::test_api_upload_document`
**Dependencies:** None | **Files:** `backend/routers/digitize.py` | **Scope:** S (1 file)

### Task AI-02: [DONE] Engine Bóc Tách Văn Bản PDF Layout Segmentation
**Description:** Module đọc nội dung file PDF, phân tích layout tiêu đề đề thi, các phần thi và từng câu hỏi bằng PyPDF.
**Acceptance criteria:**
- [x] Tách chính xác thân câu hỏi và các phương án.
**Verification:** `pytest tests/test_ai_pipeline.py::test_pdf_parsing`
**Dependencies:** AI-01 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task AI-03: [DONE] Engine Bóc Tách File Word DOCX & Dịch MathType Sang LaTeX
**Description:** Quét cấu trúc tài liệu Word DOCX, bóc tách các đối tượng OLE MathType và dịch nhị phân sang mã LaTeX KaTeX.
**Acceptance criteria:**
- [x] Công thức nhúng trong văn bản Word được giữ nguyên vẹn dưới dạng `$..$`.
**Verification:** `pytest tests/test_ai_pipeline.py::test_ai_parser_pipeline`
**Dependencies:** AI-01 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task AI-04: [DONE] Module Chuẩn Hóa Công Thức Toán LaTeX KaTeX
**Description:** Viết các biểu thức chính quy chuẩn hóa các ký hiệu toán học phổ biến trong đề thi (phân số `\frac`, căn `\sqrt`, tích phân `\int`, giới hạn `\lim`).
**Acceptance criteria:**
- [x] Làm sạch cú pháp lỗi trước khi chuyển sang frontend KaTeX.
**Verification:** `pytest tests/test_ai_pipeline.py::test_latex_converter`
**Dependencies:** AI-03 | **Files:** `backend/services/ai_parser.py` | **Scope:** XS (1 file)

### Task AI-05: [DONE] Engine Nhận Diện Cấu Trúc 3 Phần Đề Thi 2025
**Description:** Tự động phát hiện ranh giới chuyển đổi giữa Phần I (4 lựa chọn), Phần II (Đúng/Sai), và Phần III (Trả lời ngắn).
**Acceptance criteria:**
- [x] Phân loại đúng thể thức `ItemFormat` cho từng câu hỏi bóc tách được.
**Verification:** `pytest tests/test_ai_pipeline.py`
**Dependencies:** AI-02, AI-03 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task AI-06: [DONE] Bounding Box Image Cropper Cắt Ảnh Đồ Thị Sang WebP
**Description:** Module tự động phát hiện tọa độ bounding box của hình vẽ/đồ thị, crop ảnh từ trang gốc và nén sang chuẩn WebP lưu vào `storage/assets/`.
**Acceptance criteria:**
- [x] Ảnh WebP có kích thước tối ưu (< 150KB).
- [x] Thân câu hỏi tự động được nhúng mã `[IMAGE:url]`.
**Verification:** `pytest tests/test_ai_pipeline.py::test_crop_service`
**Dependencies:** AI-02 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task AI-07: [DONE] Heuristic Auto-Tagging Gợi Ý Mức Độ Nhận Thức & Mã YCCĐ
**Description:** Dựa trên tập động cơ nhận thức của Thông tư 32 (nhận biết, giải thích, tính toán) để gợi ý mức độ nhận thức và mã YCCĐ tương ứng.
**Acceptance criteria:**
- [x] Gợi ý đúng mức độ nhận thức cho câu hỏi mẫu.
**Verification:** `pytest tests/test_ai_pipeline.py::test_tagging_service`
**Dependencies:** AI-05, TS-08 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task UI-01: [DONE] Bố Cục Studio Hậu Kiểm 2 Cột Đối Xứng
**Description:** Thiết kế giao diện chia đôi màn hình: bên trái hiển thị tài liệu đề thi gốc, bên phải hiển thị danh sách câu hỏi AI đã bóc tách.
**Acceptance criteria:**
- [x] Bố cục co giãn mượt mà, thanh cuộn độc lập cho 2 cột.
**Verification:** Browser visual inspection tại tab "Số hoá AI HITL Studio".
**Dependencies:** AI-01 | **Files:** `frontend/index.html` | **Scope:** S (1 file)

### Task UI-02: [DONE] Thanh Đo Độ Tin Cậy AI (Confidence Barometer)
**Description:** Hiển thị chỉ số độ tin cậy bóc tách cho từng câu hỏi với 3 dải màu trực quan (Xanh >= 95%, Vàng 80-94%, Đỏ < 80%).
**Acceptance criteria:**
- [x] Câu hỏi thiếu đáp án đúng hoặc công thức nghi ngờ tự động gắn nhãn cảnh báo đỏ.
**Verification:** Browser visual inspection trên danh sách câu hỏi bóc tách.
**Dependencies:** UI-01 | **Files:** `frontend/static/app.js` | **Scope:** XS (1 file)

### Task UI-03: [DONE] Cơ Chế Cuộn Đồng Bộ (Synchronized Scrolling)
**Description:** Sự kiện click vào thẻ câu hỏi ở cột bên phải tự động cuộn tài liệu gốc ở cột bên trái đến đúng vị trí tương ứng với độ trễ < 100ms.
**Acceptance criteria:**
- [x] Vùng văn bản gốc tương ứng được highlight nổi bật.
**Verification:** Browser check tương tác click câu hỏi trên Studio.
**Dependencies:** UI-01 | **Files:** `frontend/static/app.js` | **Scope:** S (1 file)

### Task UI-04: [DONE] Thao Tác Click Trực Tiếp Đổi Đáp Án Đúng
**Description:** Cho phép người dùng click trực tiếp vào ký tự phương án [A], [B], [C], [D] để đảo trạng thái đáp án đúng/sai ngay trên thẻ câu hỏi.
**Acceptance criteria:**
- [x] Thẻ câu hỏi cập nhật đáp án đúng tức thì không cần mở form chỉnh sửa phức tạp.
**Verification:** Browser check click đổi đáp án.
**Dependencies:** UI-01 | **Files:** `frontend/static/app.js` | **Scope:** XS (1 file)

### Task UI-05: [DONE] Modal Soạn Thảo Công Thức Toán LaTeX Với Live Preview KaTeX
**Description:** Cửa sổ popup mở ra khi nhấn vào nút biên tập công thức, cho phép gõ mã LaTeX và xem preview KaTeX hiển thị trực tiếp.
**Acceptance criteria:**
- [x] Công thức xem trước thay đổi tức thời theo từng phím gõ.
- [x] Nút "Áp dụng" cập nhật công thức mới vào thân câu hỏi.
**Verification:** Browser check mở modal và gõ công thức `\sqrt{x^2+1}`.
**Dependencies:** UI-01 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** S (2 files)

---

## Phase 4: Ma Trận Đề Thi & Động Cơ Sinh Đề

### Task MX-01: [DONE] Định nghĩa ORM Models `ExamMatrix` và `ExamMatrixItem`
**Description:** Khai báo bảng CSDL lưu trữ cấu hình ma trận đề thi: thông tin chung (tên kỳ thi, môn, khối lớp) và các ô ma trận chi tiết.
**Acceptance criteria:**
- [x] Mỗi ô ma trận (`ExamMatrixItem`) liên kết với YCCĐ, mức độ nhận thức, số câu và điểm số.
**Verification:** `python -c "from backend.models import ExamMatrix, ExamMatrixItem; print('OK')"`
**Dependencies:** TS-03 | **Files:** `backend/models.py` | **Scope:** S (1 file)

### Task MX-02: [DONE] Pydantic Schemas Cấu Hình Ma Trận Đề Thi
**Description:** Khai báo schema kiểm soát tính hợp lệ của ma trận: tổng điểm phải bằng 10.0, tổng số câu > 0.
**Acceptance criteria:**
- [x] Báo lỗi HTTP 422 nếu thiếu tiêu đề hoặc danh sách ô rỗng.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py::test_negative_matrix_creation_missing_required_title_returns_422`
**Dependencies:** MX-01 | **Files:** `backend/schemas.py` | **Scope:** XS (1 file)

### Task MX-03: [DONE] API `POST /api/v1/matrix` Tạo Mới Ma Trận Đề Thi
**Description:** Endpoint nhận payload cấu hình ma trận và lưu vào CSDL.
**Acceptance criteria:**
- [x] Lưu trữ thành công trả về HTTP 201 kèm ID ma trận.
**Verification:** `pytest tests/test_api_endpoints.py::test_api_matrix_creation`
**Dependencies:** MX-02 | **Files:** `backend/routers/matrix.py` | **Scope:** S (1 file)

### Task MX-04: [DONE] API `GET /api/v1/matrix` & `GET /api/v1/matrix/{id}`
**Description:** Endpoints tra cứu danh sách các bản đặc tả ma trận đề thi và chi tiết từng ô cấu hình.
**Acceptance criteria:**
- [x] Trả về đầy đủ danh sách các ô ma trận kèm thông tin YCCĐ.
**Verification:** `pytest tests/test_api_endpoints.py`
**Dependencies:** MX-03 | **Files:** `backend/routers/matrix.py` | **Scope:** XS (1 file)

### Task MX-05: [DONE] Thuật Toán Kiểm Tra Số Dư Khả Dụng Trong Ngân Hàng (Inventory Checker)
**Description:** Hàm quét ngân hàng câu hỏi đối chiếu với từng ô trong ma trận, kiểm tra số câu hỏi khả dụng (`status='APPROVED'`).
**Acceptance criteria:**
- [x] Trả về danh sách cảnh báo thiếu hụt nếu số câu trong kho nhỏ hơn yêu cầu.
**Verification:** `pytest tests/test_services.py::test_matrix_solver_exclusion_and_inventory_warning`
**Dependencies:** MX-03, IB-05 | **Files:** `backend/services/matrix_solver.py` | **Scope:** S (1 file)

### Task MX-06: [DONE] Giao Diện Lưới Cấu Hình Ma Trận Đề Thi
**Description:** Xây dựng bảng ma trận trên tab "Ma trận đề thi" hiển thị trực quan các ô cấu hình và cảnh báo số dư kho bằng màu sắc.
**Acceptance criteria:**
- [x] Hiển thị tổng điểm và tổng số câu tính toán tự động ở chân bảng.
**Verification:** Browser inspection tại tab "Ma trận đề thi".
**Dependencies:** MX-04, MX-05 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** S (2 files)

### Task EG-01: [DONE] Định nghĩa ORM Models `MasterExam` và `MasterExamItem`
**Description:** Khai báo bảng lưu trữ đề thi gốc được sinh ra từ ma trận: tiêu đề, tổng điểm, danh sách câu hỏi gốc theo thứ tự.
**Acceptance criteria:**
- [x] Lưu thứ tự câu hỏi gốc `order_index` và điểm số từng câu.
**Verification:** `python -c "from backend.models import MasterExam, MasterExamItem; print('OK')"`
**Dependencies:** MX-01, IB-01 | **Files:** `backend/models.py` | **Scope:** S (1 file)

### Task EG-02: [DONE] Thuật Toán Sinh Đề Gốc Chọn Lọc Ngẫu Nhiên Có Trọng Số
**Description:** Động cơ chọn lọc câu hỏi ngẫu nhiên đáp ứng chính xác số lượng câu hỏi từng ô ma trận, ưu tiên câu hỏi có chỉ số phân biệt cao.
**Acceptance criteria:**
- [x] Đề gốc sinh ra có đủ số lượng câu hỏi và tỷ lệ điểm quy định.
**Verification:** `pytest tests/test_e2e_workflow.py`
**Dependencies:** EG-01, MX-05 | **Files:** `backend/services/matrix_solver.py` | **Scope:** S (1 file)

### Task EG-03: [DONE] Bộ Lọc Loại Trừ Câu Hỏi Đã Thi Trong N Ngày Gần Nhất (Cooldown)
**Description:** Nhận danh sách câu hỏi cần loại trừ (`excluded_question_ids`) và đảm bảo thuật toán không chọn lại các câu hỏi này.
**Acceptance criteria:**
- [x] 100% câu hỏi trong danh sách loại trừ không xuất hiện trong đề thi mới sinh.
**Verification:** `pytest tests/test_services.py::test_matrix_solver_exclusion_and_inventory_warning`
**Dependencies:** EG-02 | **Files:** `backend/services/matrix_solver.py` | **Scope:** XS (1 file)

### Task EG-04: [DONE] API `POST /api/v1/exams/generate` Sinh Đề Gốc Tự Động
**Description:** Endpoint nhận `matrix_id` và kích hoạt thuật toán sinh đề gốc, lưu vào bảng `master_exams`.
**Acceptance criteria:**
- [x] Trả về HTTP 404 nếu `matrix_id` không tồn tại.
- [x] Trả về HTTP 400 nếu kho câu hỏi không đủ đáp ứng ma trận.
- [x] Trả về HTTP 201 kèm thông tin đề gốc khi sinh thành công.
**Verification:** `pytest tests/test_api_contracts_and_negatives.py::test_negative_generate_exam_with_nonexistent_matrix_returns_404`
**Dependencies:** EG-03 | **Files:** `backend/routers/exams.py` | **Scope:** S (1 file)

---

## Phase 5: Trộn Đề An Toàn & Phân Tích Khảo Thí CTT

### Task SH-01: [DONE] Định nghĩa ORM Models `ExamVariant` và `ExamVariantItem`
**Description:** Khai báo bảng lưu trữ các mã đề thi hoán vị (101, 102, 103, 104), vị trí câu hỏi mới và ánh xạ phương án hoán vị.
**Acceptance criteria:**
- [x] Lưu ánh xạ hoán vị phương án `option_mapping` (JSON e.g. `{"A":"B", "B":"C", ...}`).
**Verification:** `python -c "from backend.models import ExamVariant, ExamVariantItem; print('OK')"`
**Dependencies:** EG-01 | **Files:** `backend/models.py` | **Scope:** S (1 file)

### Task SH-02: [DONE] Thực thi RULE-01: Chấm Điểm Lũy Tiến Câu Hỏi Đúng/Sai
**Description:** Hiện thực hóa logic chấm điểm 4 bậc của Bộ GD&ĐT cho câu hỏi Đúng/Sai: đúng 1 ý = 0.1đ, đúng 2 ý = 0.25đ, đúng 3 ý = 0.5đ, đúng cả 4 ý = 1.0đ.
**Acceptance criteria:**
- [x] Kiểm thử toàn bộ 16 tổ hợp trả lời của học sinh cho kết quả điểm số chuẩn xác.
**Verification:** `pytest tests/test_rules_shuffling.py::test_rule_01_progressive_grading_all_16_combinations`
**Dependencies:** SH-01 | **Files:** `backend/services/shuffling_engine.py` | **Scope:** S (1 file)

### Task SH-03: [DONE] Thực thi RULE-02: Option Anchor Rule Khóa Cố Định Đáp Án Neo Vào Vị Trí D
**Description:** Phát hiện các phương án chứa từ khóa neo ("Tất cả các đáp án trên", "Không có đáp án nào") hoặc có cờ `is_fixed=True`, đảm bảo khi xáo trộn phương án này LUÔN nằm ở vị trí D.
**Acceptance criteria:**
- [x] Trong 100 vòng lặp xáo trộn ngẫu nhiên, phương án neo nằm ở vị trí D đạt tỷ lệ 100%.
**Verification:** `pytest tests/test_rules_shuffling.py::test_rule_02_option_anchor_100_iterations`
**Dependencies:** SH-01 | **Files:** `backend/services/shuffling_engine.py` | **Scope:** S (1 file)

### Task SH-04: [DONE] Thực thi RULE-03: Section Integrity & Passage Integrity
**Description:** Ràng buộc đảo câu hỏi: chỉ đảo thứ tự câu hỏi trong cùng một phần thi; các câu hỏi con của câu hỏi chùm luôn đi liền kề ngay sau ngữ liệu bài đọc.
**Acceptance criteria:**
- [x] Không bao giờ có câu hỏi Phần I bị đảo sang Phần II hoặc Phần III.
- [x] Ngữ liệu chùm không bị tách rời khỏi câu hỏi con trong mọi mã đề hoán vị.
**Verification:** `pytest tests/test_rules_shuffling.py::test_rule_03_passage_integrity_in_all_variants`
**Dependencies:** SH-01 | **Files:** `backend/services/shuffling_engine.py` | **Scope:** S (1 file)

### Task SH-05: [DONE] Thực thi RULE-04: Tự Động Sinh Ma Trận Ánh Xạ Đáp Án
**Description:** Tự động tính toán đáp án đúng mới của từng mã đề thi hoán vị tương ứng với câu hỏi gốc trong đề master, tạo bảng tra đáp án tổng hợp.
**Acceptance criteria:**
- [x] Tạo ma trận đáp án 2 chiều (Câu hỏi x Mã đề thi).
**Verification:** `pytest tests/test_services.py::test_answer_key_mapping_matrix`
**Dependencies:** SH-02, SH-03 | **Files:** `backend/services/shuffling_engine.py` | **Scope:** S (1 file)

### Task SH-06: [DONE] API `POST /api/v1/exams/{id}/shuffle` Sinh Các Mã Đề Hoán Vị
**Description:** Endpoint kích hoạt động cơ sinh 4 mã đề hoán vị chuẩn (101, 102, 103, 104) từ đề master.
**Acceptance criteria:**
- [x] Trả về danh sách 4 mã đề kèm ma trận đáp án tổng hợp.
**Verification:** `pytest tests/test_api_endpoints.py::test_api_variant_shuffling`
**Dependencies:** SH-05 | **Files:** `backend/routers/exams.py` | **Scope:** S (1 file)

### Task SH-07: [DONE] Giao Diện Tab Chuyển Đổi Xem Trước Từng Mã Đề
**Description:** Xây dựng các tab nút bấm [Mã 101], [Mã 102], [Mã 103], [Mã 104] cho phép giáo viên xem trước nội dung đảo đề của từng mã.
**Acceptance criteria:**
- [x] Chuyển đổi tab mượt mà, hiển thị đúng thứ tự câu và đáp án của mã đề đang chọn.
**Verification:** Browser check chuyển tab mã đề trên Web Studio.
**Dependencies:** SH-06 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** S (2 files)

### Task SH-08: [DONE] Giao Diện Bảng Ma Trận Đáp Án Tổng Hợp Đối Chiếu
**Description:** Bảng hiển thị đáp án tổng hợp tất cả các mã đề thi đối chiếu với đề gốc trên Web Studio.
**Acceptance criteria:**
- [x] Hiển thị rõ ràng đáp án từng câu hỏi của cả 4 mã đề.
**Verification:** Browser visual inspection tại tab "Trộn đề & Xuất bản".
**Dependencies:** SH-07 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** XS (1 file)

### Task AN-01: [DONE] API `POST /api/v1/exams/{id}/analytics` Tiếp Nhận Bảng Điểm Thi
**Description:** Endpoint nhận bảng điểm chấm thi của học sinh theo từng câu hỏi để thực hiện phân tích trắc lượng học cổ điển (CTT).
**Acceptance criteria:**
- [x] Nhận danh sách điểm số của học sinh và kiểm tra hợp lệ.
**Verification:** `pytest tests/test_e2e_workflow.py`
**Dependencies:** SH-06 | **Files:** `backend/routers/exams.py` | **Scope:** S (1 file)

### Task AN-02: [DONE] Thuật Toán Tính Độ Khó Cổ Điển $p = R/N$
**Description:** Hàm tính tỷ lệ học sinh làm đúng câu hỏi trên tổng số thí sinh tham gia làm bài thi.
**Acceptance criteria:**
- [x] Chỉ số $p$ luôn nằm trong đoạn [0.0, 1.0].
**Verification:** `pytest tests/test_services.py`
**Dependencies:** AN-01 | **Files:** `backend/services/analytics.py` | **Scope:** XS (1 file)

### Task AN-03: [DONE] Thuật Toán Tính Độ Phân Biệt $D = P_H - P_L$
**Description:** Phân chia thí sinh thành 2 nhóm: 27% điểm cao nhất ($P_H$) và 27% điểm thấp nhất ($P_L$), tính hiệu số tỷ lệ đúng $D$.
**Acceptance criteria:**
- [x] Chỉ số $D$ phản ánh chính xác khả năng phân loại học sinh khá giỏi của câu hỏi.
**Verification:** `pytest tests/test_services.py`
**Dependencies:** AN-02 | **Files:** `backend/services/analytics.py` | **Scope:** S (1 file)

### Task AN-04: [DONE] Tự Động Gắn Cờ Cảnh Báo Câu Hỏi Lỗi Khi $D < 0.20$
**Description:** Cảnh báo các câu hỏi có độ phân biệt kém ($D < 0.20$) hoặc độ phân biệt âm ($D < 0$) nghi ngờ đáp án sai hoặc đề thi có bẫy kỹ thuật.
**Acceptance criteria:**
- [x] Bổ sung cờ `QUESTION_DEFECTIVE` trong báo cáo phân tích trả về.
**Verification:** `pytest tests/test_services.py`
**Dependencies:** AN-03 | **Files:** `backend/services/analytics.py` | **Scope:** XS (1 file)

---

## Phase 6: Xuất Bản Đa Định Dạng & Vận Hành Hệ Thống

### Task EX-01: [DONE] Dịch Vụ Tạo File Word OpenXML (.docx) Chuẩn 2 Cột
**Description:** Xây dựng hàm `generate_variant_docx` sử dụng `python-docx` tạo cấu trúc OpenXML chuẩn 2 cột (`w:cols num="2"`).
**Acceptance criteria:**
- [x] File sinh ra là tệp nén OpenXML ZIP hợp lệ mở được trực tiếp trên Word.
**Verification:** `pytest tests/test_docx_export.py`
**Dependencies:** SH-01 | **Files:** `backend/services/docx_exporter.py` | **Scope:** S (1 file)

### Task EX-02: [DONE] Tạo Bảng Phách Thông Tin Thí Sinh Chuẩn Bộ GD&ĐT Trong File Word
**Description:** Thêm phần đầu đề thi gồm: Tên trường/Sở, tên bài thi, mã đề thi, thời gian làm bài và bảng điền số báo danh, số phách.
**Acceptance criteria:**
- [x] Bảng thông tin kẻ viền chuẩn mực khảo thí, cố định ở đầu trang 1.
**Verification:** `pytest tests/test_docx_export.py`
**Dependencies:** EX-01 | **Files:** `backend/services/docx_exporter.py` | **Scope:** XS (1 file)

### Task EX-03: [DONE] Chuyển Đổi Công Thức LaTeX Sang OMML Native Trong File Word
**Description:** Tích hợp hàm chuyển đổi cú pháp toán học sang mã XML `<m:oMath>` để công thức hiển thị dạng vector sắc nét trong Word.
**Acceptance criteria:**
- [x] Công thức toán có thể nhấp chuột vào chỉnh sửa trực tiếp bằng Equation Editor của Word.
**Verification:** `pytest tests/test_docx_export.py`
**Dependencies:** EX-01 | **Files:** `backend/services/docx_exporter.py` | **Scope:** S (1 file)

### Task EX-04: [DONE] Động Cơ Sinh PDF Vector Siêu Tốc Thuần Python Bằng ReportLab (<100ms)
**Description:** Viết module `generate_pdf_reportlab` sinh file PDF vector thuần Python, loại bỏ hoàn toàn việc gọi tiến trình Word COM bên ngoài.
**Acceptance criteria:**
- [x] Thời gian sinh 1 tệp đề thi PDF <= 100ms (giảm từ 20s xuống 35ms).
- [x] Đầy đủ 3 phần thi, phân chia cột và khung phách.
**Verification:** `pytest tests/test_performance_budgets.py::test_perf_budget_docx_and_zip_export`
**Dependencies:** SH-01 | **Files:** `backend/services/docx_exporter.py` | **Scope:** S (1 file)

### Task EX-05: [DONE] Nạp Font Times New Roman Unicode Windows (`times.ttf`) Cho ReportLab
**Description:** Đăng ký font hệ thống Windows (`times.ttf`, `timesbd.ttf`, `timesi.ttf`) vào ReportLab `pdfmetrics` để hỗ trợ tiếng Việt có dấu 100%.
**Acceptance criteria:**
- [x] Đề thi PDF hiển thị sắc nét toàn bộ dấu tiếng Việt không bị lỗi font hoặc ô vuông.
**Verification:** Kiểm thử hiển thị file PDF vector trên trình duyệt.
**Dependencies:** EX-04 | **Files:** `backend/services/docx_exporter.py` | **Scope:** XS (1 file)

### Task EX-06: [DONE] Xuất Bản Tài Liệu Hướng Dẫn Giải Chi Tiết (Word & PDF)
**Description:** Viết hàm xuất bản tài liệu lời giải chi tiết cho từng mã đề thi hoán vị theo định dạng cả Word (.docx) và PDF (.pdf).
**Acceptance criteria:**
- [x] Hiển thị rõ ràng đáp án chuẩn và phần giải thích từng câu hỏi.
**Verification:** `pytest tests/test_services.py::test_docx_export_and_zip_package`
**Dependencies:** EX-01, EX-04 | **Files:** `backend/services/docx_exporter.py` | **Scope:** S (1 file)

### Task EX-07: [DONE] Xuất Bản Bảng Đáp Án Tổng Hợp Các Mã Đề (Word, PDF, CSV)
**Description:** Viết hàm xuất bản bảng đáp án tổng hợp đối chiếu tất cả các mã đề thi ra cả 3 định dạng: `.docx`, `.pdf`, `.csv` (UTF-8 BOM).
**Acceptance criteria:**
- [x] File CSV có thể mở trực tiếp trên Excel tiếng Việt không bị lỗi font.
**Verification:** `pytest tests/test_services.py::test_docx_export_and_zip_package`
**Dependencies:** EX-01, EX-04 | **Files:** `backend/services/docx_exporter.py` | **Scope:** S (1 file)

### Task EX-08: [DONE] API `GET /api/v1/exams/{id}/export-docx` (Tải Lẻ File Word)
**Description:** Endpoint xuất và trả về trực tiếp file Word `.docx` của một mã đề thi cụ thể (ví dụ Mã 101).
**Acceptance criteria:**
- [x] Tự động fallback về đề thi khả dụng nếu ID gửi lên là `default` hoặc không tồn tại.
- [x] Header `Content-Disposition` trả về attachment filename rõ ràng.
**Verification:** Real Browser CDP check: tải thành công `De_Thi_Ma_101.docx`.
**Dependencies:** EX-01 | **Files:** `backend/routers/exams.py` | **Scope:** S (1 file)

### Task EX-09: [DONE] API `GET /api/v1/exams/{id}/export-pdf` (Tải Lẻ File PDF)
**Description:** Endpoint xuất và trả về trực tiếp file PDF vector của một mã đề thi cụ thể trong thời gian dưới 300ms.
**Acceptance criteria:**
- [x] Trả về file PDF với `Content-Type: application/pdf`.
**Verification:** Real Browser CDP check: tải thành công `De_Thi_Ma_101.pdf` (283ms).
**Dependencies:** EX-04, EX-05 | **Files:** `backend/routers/exams.py` | **Scope:** S (1 file)

### Task EX-10: [DONE] API `GET /api/v1/exams/{id}/export-zip` Hỗ Trợ `format=all|docx|pdf`
**Description:** Endpoint đóng gói trọn gói toàn bộ các mã đề, lời giải và ma trận đáp án vào 1 tệp ZIP duy nhất theo tùy chọn định dạng.
**Acceptance criteria:**
- [x] `format=docx`: Gói chỉ chứa Word và CSV.
- [x] `format=pdf`: Gói chỉ chứa PDF và CSV.
- [x] `format=all`: Gói chứa đầy đủ cả Word, PDF và CSV.
**Verification:** `pytest tests/test_performance_budgets.py::test_perf_budget_docx_and_zip_export`
**Dependencies:** EX-06, EX-07 | **Files:** `backend/routers/exams.py`, `backend/services/docx_exporter.py` | **Scope:** S (2 files)

### Task EX-11: [DONE] Cơ Chế Tải Blob Client-Side Dập Tắt Lỗi *Failed - Unknown Server Error*
**Description:** Nâng cấp các hàm tải file client-side (`downloadPublishZip`, `downloadActiveVariantPdf`, `downloadActiveVariantDocx`) sang mô hình `fetch()` + `URL.createObjectURL(blob)`.
**Acceptance criteria:**
- [x] Kiểm tra `response.ok` trước khi kích hoạt lưu file.
- [x] Hiển thị Toast thông báo trạng thái tải trực quan theo thời gian thực.
**Verification:** Real Browser CDP test: toàn bộ các nút tải đều thành công không còn lỗi ngắt kết nối.
**Dependencies:** EX-08, EX-09, EX-10 | **Files:** `frontend/static/app.js` | **Scope:** S (1 file)

### Task SO-01: [DONE] Script `start_server.py` Tự Động Giải Phóng Socket Cổng 8000
**Description:** Nâng cấp script khởi động hệ thống tự kiểm tra lỗi `WinError 10048`, tra cứu PID chiếm dụng qua netstat và giải phóng cổng trước khi khởi chạy uvicorn.
**Acceptance criteria:**
- [x] Khởi động mượt mà không bao giờ bị nghẽn cổng trên Windows.
**Verification:** Chạy `python start_server.py` thành công.
**Dependencies:** None | **Files:** `start_server.py` | **Scope:** S (1 file)

### Task SO-02: [DONE] Route `/favicon.ico` Trả Về HTTP 204 Chống Lỗi Console
**Description:** Bổ sung endpoint xử lý yêu cầu favicon của trình duyệt trả về mã HTTP 204 No Content.
**Acceptance criteria:**
- [x] Console trình duyệt không còn xuất hiện dòng đỏ lỗi 404 favicon.
**Verification:** Real Browser CDP check: không có lỗi 404 favicon.
**Dependencies:** None | **Files:** `backend/main.py` | **Scope:** XS (1 file)

### Task SO-03: [DONE] Bổ Sung Cache-Buster `?v=...` Chống Lưu Cache Script Cũ
**Description:** Thêm chuỗi phiên bản `static/app.js?v=2.0.3` vào thẻ script trong `frontend/index.html` để trình duyệt luôn nạp mã nguồn JavaScript mới nhất.
**Acceptance criteria:**
- [x] Trình duyệt tải phiên bản script mới nhất mà không cần yêu cầu người dùng xóa cache thủ công.
**Verification:** Browser inspection xác nhận file `app.js?v=2.0.3` được nạp.
**Dependencies:** EX-11 | **Files:** `frontend/index.html` | **Scope:** XS (1 file)

### Task SO-04: [DONE] Bộ Test Suite Tự Động 39 Test Cases Bao Phủ Toàn Diện Hệ Thống
**Description:** Tích hợp bộ tiêu chuẩn từ `tester-skills-main.zip`, hoàn thiện 39 bài kiểm thử bao phủ toàn diện: Hợp đồng API, trường hợp biên, ngân sách hiệu năng và kịch bản E2E.
**Acceptance criteria:**
- [x] 39/39 test cases pass 100% trong thời gian ~10 giây.
**Verification:** `pytest`
**Dependencies:** Toàn bộ các tasks từ TS-01 đến EX-11 | **Files:** `tests/*` | **Scope:** M (3 files)

---

## Phase 7: Mở Rộng Doanh Nghiệp & Đám Mây (Future Roadmap / Backlog)

### Task BL-01: [ ] CSDL Quản Lý Tài Khoản, Vai Trò (RBAC) & Đơn Vị Trường Học
**Description:** Khai báo bảng `users`, `roles`, `institutions` hỗ trợ mô hình Multi-tenant cách ly dữ liệu giữa các trường học.
**Acceptance criteria:**
- [ ] Bảng `users` có trường `institution_id`, `role_id` và mật khẩu băm bcrypt.
**Verification:** `python -c "from backend.models import User, Institution; print('OK')"`
**Dependencies:** TS-01 | **Files:** `backend/models.py` | **Scope:** S (1 file)

### Task BL-02: [ ] Middleware Xác Thực JWT Token & Phân Quyền Thao Tác API
**Description:** Viết middleware giải mã JWT token trong header `Authorization: Bearer <token>`, trích xuất thông tin người dùng và phân quyền theo vai trò.
**Acceptance criteria:**
- [ ] Trả về HTTP 401 nếu token không hợp lệ hoặc hết hạn.
- [ ] Trả về HTTP 403 nếu tài khoản không đủ quyền thực hiện thao tác.
**Verification:** `pytest tests/test_auth_middleware.py`
**Dependencies:** BL-01 | **Files:** `backend/auth.py`, `backend/main.py` | **Scope:** S (2 files)

### Task BL-03: [ ] API Đăng Nhập, Đăng Xuất & Quản Lý Thông Tin Tài Khoản
**Description:** Cung cấp các endpoint `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.
**Acceptance criteria:**
- [ ] Đăng nhập thành công trả về JWT access token và refresh token.
**Verification:** `pytest tests/test_auth_api.py`
**Dependencies:** BL-02 | **Files:** `backend/routers/auth.py` | **Scope:** S (1 file)

### Task BL-04: [ ] Giao Diện Phê Duyệt Câu Hỏi Dành Riêng Cho Tổ Trưởng Chuyên Môn
**Description:** Xây dựng màn hình danh sách câu hỏi ở trạng thái `PENDING_REVIEW` cho phép Tổ trưởng chuyên môn bấm "Phê duyệt" chuyển sang `APPROVED` hoặc "Yêu cầu chỉnh sửa".
**Acceptance criteria:**
- [ ] Chỉ người dùng có vai trò `SUBJECT_LEADER` hoặc `ADMIN` mới nhìn thấy nút phê duyệt.
**Verification:** Browser check giao diện với tài khoản Tổ trưởng.
**Dependencies:** BL-03, IB-06 | **Files:** `frontend/index.html`, `frontend/static/app.js` | **Scope:** S (2 files)

### Task BL-05: [ ] Adapter Tích Hợp Cloud Multimodal LLM (Gemini 1.5 Pro / Claude 3.5 Sonnet)
**Description:** Viết class adapter `CloudVisionAdapter` kết nối Google Gemini API và Anthropic Claude API để xử lý ảnh đề thi phức tạp hoặc chữ viết tay.
**Acceptance criteria:**
- [ ] Tự động chuyển đổi sang Local Parser nếu không có kết nối internet hoặc hết quota API.
**Verification:** `pytest tests/test_cloud_vision_adapter.py`
**Dependencies:** AI-01 | **Files:** `backend/services/ai_parser.py`, `backend/config.py` | **Scope:** S (2 files)

### Task BL-06: [ ] Adapter Tích Hợp DocTR/TrOCR Mã Nguồn Mở Cho Chữ Viết Tay
**Description:** Tích hợp mô hình OCR mã nguồn mở DocTR chạy trực tiếp trên GPU/CPU máy chủ nội bộ để nhận diện tài liệu scan mà không gửi dữ liệu ra ngoài internet.
**Acceptance criteria:**
- [ ] Nhận diện chính xác văn bản tiếng Việt viết tay >= 85%.
**Verification:** `pytest tests/test_doctr_local.py`
**Dependencies:** AI-02 | **Files:** `backend/services/ai_parser.py` | **Scope:** S (1 file)

### Task BL-07: [ ] CSDL & REST API Quản Lý Ca Thi Trực Tuyến (CBT Session)
**Description:** Khai báo bảng `cbt_exams`, `cbt_candidates`, `cbt_submissions` và các API mở/đóng ca thi, sinh mã dự thi ngẫu nhiên cho học sinh.
**Acceptance criteria:**
- [ ] Mỗi thí sinh được gán ngẫu nhiên 1 mã đề hoán vị trong ca thi.
**Verification:** `pytest tests/test_cbt_management.py`
**Dependencies:** SH-06, BL-01 | **Files:** `backend/models.py`, `backend/routers/cbt.py` | **Scope:** S (2 files)

### Task BL-08: [ ] Giao Diện Học Sinh Làm Bài Thi Trực Tuyến Với Đồng Hồ Đếm Ngược
**Description:** Xây dựng trang web thi độc lập (`cbt_taker.html`) hiển thị câu hỏi, bộ đếm ngược thời gian thi, và thanh tiến độ hoàn thành các câu hỏi.
**Acceptance criteria:**
- [ ] Tự động nộp bài khi thời gian đếm ngược về 00:00.
**Verification:** Browser visual inspection tại trang làm bài thi học sinh.
**Dependencies:** BL-07 | **Files:** `frontend/cbt_taker.html`, `frontend/static/cbt_app.js` | **Scope:** M (2 files)

### Task BL-09: [ ] WebSocket Đồng Bộ Câu Trả Lời Học Sinh Mỗi 15 Giây
**Description:** Kết nối WebSocket hai chiều giữa trình duyệt thí sinh và máy chủ, tự động lưu câu trả lời mỗi 15 giây chống mất bài khi mất mạng.
**Acceptance criteria:**
- [ ] Khi rớt mạng, lưu tạm vào LocalStorage và tự động đồng bộ lại khi có mạng trở lại.
**Verification:** Giả lập ngắt mạng trong quá trình thi và kiểm tra phục hồi bài làm.
**Dependencies:** BL-08 | **Files:** `backend/routers/cbt.py`, `frontend/static/cbt_app.js` | **Scope:** S (2 files)

### Task BL-10: [ ] Module Ghi Nhận Vi Phạm Thi Cử (Chuyển Tab Trình Duyệt)
**Description:** Bắt sự kiện `visibilitychange` và `window.onblur`, đếm số lần học sinh chuyển tab hoặc mở ứng dụng khác và gửi cảnh báo về màn hình giám thị.
**Acceptance criteria:**
- [ ] Hiển thị thông báo cảnh báo thí sinh và ghi log vi phạm vào CSDL.
**Verification:** Browser check: bấm Alt+Tab, hệ thống ghi nhận vi phạm.
**Dependencies:** BL-08 | **Files:** `frontend/static/cbt_app.js`, `backend/models.py` | **Scope:** S (2 files)

### Task BL-11: [ ] Thuật Toán OpenCV Căn Chỉnh 4 Điểm Mốc Định Vị Phiếu Trắc Nghiệm 2025
**Description:** Viết module xử lý ảnh OpenCV tự động tìm 4 dấu mốc vuông ở 4 góc của phiếu trả lời trắc nghiệm, thực hiện phép biến đổi phối cảnh (Perspective Transform) để nắn thẳng ảnh chụp.
**Acceptance criteria:**
- [ ] Nắn thẳng chính xác ảnh chụp bị nghiêng tối đa 30 độ.
**Verification:** `pytest tests/test_omr_alignment.py`
**Dependencies:** None | **Files:** `backend/services/omr_engine.py` | **Scope:** S (1 file)

### Task BL-12: [ ] Thuật Toán Nhận Diện Điểm Tô Đen Bút Chì 2B Trên Phiếu OMR
**Description:** Quét ngưỡng sáng tối (Adaptive Thresholding) tại các tọa độ ô tròn đáp án để phát hiện ô nào được thí sinh tô đen bút chì 2B cho cả 3 phần thi.
**Acceptance criteria:**
- [ ] Độ chính xác nhận diện điểm tô đen đạt >= 99.5%.
**Verification:** `pytest tests/test_omr_bubble_detection.py`
**Dependencies:** BL-11 | **Files:** `backend/services/omr_engine.py` | **Scope:** S (1 file)

### Task BL-13: [ ] API Nhận Ảnh Phiếu Trắc Nghiệm Và Trả Về Điểm Số Tự Động
**Description:** Endpoint `POST /api/v1/omr/grade` nhận ảnh phiếu thi, gọi module OMR chấm điểm theo mã đề và trả về bảng điểm chi tiết của thí sinh.
**Acceptance criteria:**
- [ ] Tự động áp dụng quy tắc chấm lũy tiến RULE-01 cho Phần II.
**Verification:** `pytest tests/test_omr_api.py`
**Dependencies:** BL-12, SH-02 | **Files:** `backend/routers/grading.py` | **Scope:** S (1 file)

### Task BL-14: [ ] Viết Multi-Stage Dockerfile Cho Ứng Dụng Quesy
**Description:** Viết file `Dockerfile` gồm build stage và runtime stage nhỏ gọn, bảo mật với tài khoản non-root user và cài đặt đầy đủ các gói phụ thuộc.
**Acceptance criteria:**
- [ ] Build thành công Docker image với dung lượng < 600MB.
**Verification:** `docker build -t quesy-app:latest .`
**Dependencies:** SO-01 | **Files:** `Dockerfile`, `.dockerignore` | **Scope:** S (2 files)

### Task BL-15: [ ] Viết File `docker-compose.yml` Tích Hợp Postgres & Redis
**Description:** Khai báo cấu hình `docker-compose.yml` khởi chạy ứng dụng cùng cơ sở dữ liệu PostgreSQL (kèm extension `pgvector`) và Redis Cache.
**Acceptance criteria:**
- [ ] Lệnh `docker compose up -d` khởi động toàn bộ dịch vụ và vượt qua healthcheck.
**Verification:** `docker compose config`
**Dependencies:** BL-14 | **Files:** `docker-compose.yml` | **Scope:** S (1 file)

### Task BL-16: [ ] Thiết Lập Pipeline GitHub Actions CI Tự Động Chạy Kiểm Thử Khi PR/Push
**Description:** Tạo file workflow `.github/workflows/ci.yml` tự động thiết lập môi trường Python, cài đặt dependencies và chạy toàn bộ 39 bài test tự động mỗi khi có code mới.
**Acceptance criteria:**
- [ ] Workflow chạy tự động và báo trạng thái xanh khi toàn bộ test cases pass.
**Verification:** Kiểm tra tab Actions trên GitHub repository.
**Dependencies:** SO-04 | **Files:** `.github/workflows/ci.yml` | **Scope:** XS (1 file)
