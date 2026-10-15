# Kế Hoạch Triển Khai Hệ Thống (Implementation Plan v2.0): Quesy System
*Chi tiết hóa phân rã vi mô (Atomic Granular Breakdown) theo chuẩn kỹ năng `planning-and-task-breakdown`*

## 1. Overview
Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI Số hoá (QUESY) là nền tảng số hóa đề thi và khảo thí chuẩn quốc gia tuân thủ 100% Thông tư 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (định dạng thi 2025). Hệ thống tích hợp toàn diện từ bóc tách OCR/AI tài liệu gốc, Studio hậu kiểm đối chiếu song song (HITL), ngân hàng câu hỏi phân tầng 6 cấp độ năng lực theo Yêu cầu cần đạt (YCCĐ), ma trận đề thi ma trận hóa tự động, động cơ sinh và trộn đề 4 nguyên tắc an toàn khảo thí, dịch vụ xuất bản in ấn OpenXML Word/PDF vector siêu tốc, cùng phân tích trắc lượng cổ điển (CTT).

## 2. Architecture Decisions
- **AD-01 (Taxonomy Independence):** Tuyệt đối không phân chia danh mục theo bộ sách giáo khoa thương mại. Cấu trúc cây kiến thức chuẩn hóa 6 tầng: Cấp học/Lớp $\rightarrow$ Môn học $\rightarrow$ Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ Yêu cầu cần đạt (YCCĐ), phân nhánh tới tầng Dạng câu hỏi (Problem Archetype).
- **AD-02 (2025 Assessment Standards):** Hỗ trợ đầy đủ 3 phần định dạng mới: Phần I (Trắc nghiệm 4 lựa chọn), Phần II (Đúng/Sai 4 ý chấm điểm lũy tiến 0.1 - 0.25 - 0.5 - 1.0 theo RULE-01), Phần III (Trả lời ngắn).
- **AD-03 (HITL Studio Verification):** Không tin tưởng 100% vào đầu ra thô của AI; bắt buộc có giao diện hậu kiểm song song (Side-by-side synchronized review) với thanh đo độ tin cậy và bộ soạn thảo công thức KaTeX trực tiếp.
- **AD-04 (Safe Shuffling Engine):** Trộn đề đảm bảo 4 nguyên tắc khảo thí: Section Integrity, Passage Integrity, Option Anchor Lock (cố định đáp án neo vào vị trí D), và tự động sinh Ma trận Ánh xạ Đáp án.
- **AD-05 (Resilient Document Publishing):** Xuất bản Word chuẩn OpenXML (.docx) 2 cột kèm công thức OMML native; xuất bản PDF vector siêu tốc thuần Python qua ReportLab (<100ms) nạp font Times New Roman Unicode từ Windows.
- **AD-06 (Classical Test Theory Analytics):** Tích hợp tính toán độ khó ($p$) và độ phân biệt ($D$), tự động gắn cờ câu hỏi có nguy cơ lỗi kỹ thuật khi $D < 0.20$.

---

## 3. Phased Micro-Task Index & Milestones

### Phase 1: Nền Tảng CSDL & Cây Kiến Thức Thông Tư 32 (Completed)
- [x] **TS-01:** ORM Model `Grade` & `Subject`
- [x] **TS-02:** ORM Model `ContentStrand` & `Topic`
- [x] **TS-03:** ORM Model `Lesson` & `LearningOutcome` (YCCĐ)
- [x] **TS-04:** ORM Model `ProblemArchetype` (Dạng câu hỏi)
- [x] **TS-05:** Pydantic Schemas cho Cây phân cấp lồng nhau
- [x] **TS-06:** API Endpoint `GET /api/v1/taxonomy/tree`
- [x] **TS-07:** API Endpoints tra cứu Môn học & Khối lớp
- [x] **TS-08:** Seed Data 6 tầng danh mục Toán 12 chuẩn TT 32
- [x] **TS-09:** Automated Test kiểm tra tính toàn vẹn danh mục & không có trường bộ sách

### Checkpoint 1: Nền tảng Danh mục Hoàn thành
- Toàn bộ cây danh mục phân cấp hoạt động độc lập, không phụ thuộc bộ sách giáo khoa.
- `pytest tests/test_taxonomy.py` đạt 100%.

---

### Phase 2: Ngân Hàng Câu Hỏi & Động Cơ Chống Trùng (Completed)
- [x] **IB-01:** ORM Models `Question`, `Option`, `SubStatement`
- [x] **IB-02:** Định nghĩa Enums `ItemFormat` cho 5 thể thức khảo thí QĐ 764
- [x] **IB-03:** Định nghĩa Enums `CognitiveLevel` (Biết, Hiểu, Vận dụng)
- [x] **IB-04:** Pydantic Validator cho câu hỏi Đúng/Sai 4 khẳng định
- [x] **IB-05:** API `POST /api/v1/questions` tạo mới câu hỏi đa thể thức
- [x] **IB-06:** API `GET /api/v1/questions` tra cứu, lọc và phân trang
- [x] **IB-07:** API `GET /api/v1/questions/{id}` xem chi tiết câu hỏi
- [x] **IB-08:** API `PUT /api/v1/questions/{id}` cập nhật nội dung câu hỏi
- [x] **IB-09:** API `DELETE /api/v1/questions/{id}` xóa câu hỏi an toàn (Idempotent)
- [x] **DD-01:** Thuật toán chuẩn hóa chuỗi và tính Cosine Similarity vector
- [x] **DD-02:** Logic kiểm tra trùng lặp ngưỡng 80% (cảnh báo) và 90% (chặn lưu)
- [x] **IB-10:** Nạp bộ hạt giống 54 câu hỏi Toán 12 định dạng mới 2025
- [x] **IB-11:** Giao diện Web hiển thị Ngân hàng câu hỏi KaTeX
- [x] **IB-12:** Bộ lọc giao diện theo Môn học, Khối lớp, Nhận thức, YCCĐ

### Checkpoint 2: Ngân hàng Câu hỏi & Chống trùng Hoàn thành
- Hỗ trợ đầy đủ 3 phần thi 2025 và cơ chế chống trùng lặp dữ liệu.
- `pytest tests/test_deduplication.py` & `pytest tests/test_api_endpoints.py` đạt 100%.

---

### Phase 3: Pipeline Số Hóa AI & Studio Hậu Kiểm HITL (Completed)
- [x] **AI-01:** API Upload tiếp nhận tài liệu đa định dạng (.docx, .pdf, .png, .jpg)
- [x] **AI-02:** Engine bóc tách văn bản PDF layout segmentation
- [x] **AI-03:** Engine bóc tách Word DOCX & dịch MathType sang LaTeX
- [x] **AI-04:** Module chuẩn hóa công thức toán KaTeX (`$...$`, `$$...$$`)
- [x] **AI-05:** Engine nhận diện cấu trúc 3 phần đề thi (Phần I, II, III)
- [x] **AI-06:** Bounding Box Image Cropper tự động cắt ảnh đồ thị sang WebP
- [x] **AI-07:** Heuristic Auto-tagging gợi ý mức độ nhận thức và mã YCCĐ
- [x] **UI-01:** Bố cục Studio 2 cột đối xứng (Văn bản gốc - Câu hỏi bóc tách)
- [x] **UI-02:** Thanh đo độ tin cậy AI (Confidence Barometer: Xanh, Vàng, Đỏ)
- [x] **UI-03:** Cơ chế Cuộn đồng bộ (Synchronized Scrolling) giữa 2 khung nhìn
- [x] **UI-04:** Thao tác click trực tiếp đổi đáp án đúng trên giao diện
- [x] **UI-05:** Modal biên tập nhanh công thức LaTeX với Live Preview KaTeX

### Checkpoint 3: Số hóa AI & Studio HITL Hoàn thành
- Giáo viên có thể kiểm soát và chỉnh sửa 100% nội dung AI bóc tách trước khi lưu kho.
- `pytest tests/test_ai_pipeline.py` đạt 100%.

---

### Phase 4: Ma Trận Đề Thi & Động Cơ Sinh Đề (Completed)
- [x] **MX-01:** ORM Models `ExamMatrix` và `ExamMatrixItem`
- [x] **MX-02:** Pydantic Schema cho cấu hình ma trận đề thi
- [x] **MX-03:** API `POST /api/v1/matrix` tạo mới ma trận đề thi
- [x] **MX-04:** API `GET /api/v1/matrix` danh sách ma trận
- [x] **MX-05:** Thuật toán kiểm tra số dư khả dụng (Inventory Checker)
- [x] **MX-06:** Giao diện lưới cấu hình ma trận đề thi trên Web Studio
- [x] **EG-01:** ORM Models `MasterExam` và `MasterExamItem`
- [x] **EG-02:** Thuật toán sinh đề gốc có trọng số đáp ứng ràng buộc ma trận
- [x] **EG-03:** Bộ lọc loại trừ câu hỏi đã thi trong $N$ ngày gần nhất (Cooldown list)
- [x] **EG-04:** API `POST /api/v1/exams/generate` sinh đề gốc tự động

### Checkpoint 4: Ma trận & Động cơ Sinh đề Hoàn thành
- Đề gốc sinh ra tuân thủ 100% tỷ lệ điểm và thể thức ma trận quy định.
- `pytest tests/test_services.py` đạt 100%.

---

### Phase 5: Trộn Đề An Toàn & Phân Tích Khảo Thí CTT (Completed)
- [x] **SH-01:** ORM Models `ExamVariant` và `ExamVariantItem`
- [x] **SH-02:** Thực thi RULE-01: Chấm điểm lũy tiến Đúng/Sai (0.1, 0.25, 0.5, 1.0đ)
- [x] **SH-03:** Thực thi RULE-02: Option Anchor Rule khóa cố định đáp án neo vào vị trí D
- [x] **SH-04:** Thực thi RULE-03: Section Integrity & Passage Integrity
- [x] **SH-05:** Thực thi RULE-04: Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu
- [x] **SH-06:** API `POST /api/v1/exams/{id}/shuffle` sinh các mã đề hoán vị
- [x] **SH-07:** Giao diện tab chuyển đổi xem trước từng mã đề (101, 102, 103, 104)
- [x] **SH-08:** Giao diện bảng ma trận đáp án tổng hợp đối chiếu
- [x] **AN-01:** API `POST /api/v1/exams/{id}/analytics` tiếp nhận bảng điểm thi
- [x] **AN-02:** Thuật toán tính độ khó $p = R/N$
- [x] **AN-03:** Thuật toán tính độ phân biệt $D = P_H - P_L$ (nhóm 27% cao - 27% thấp)
- [x] **AN-04:** Tự động gắn cờ cảnh báo câu hỏi lỗi khi $D < 0.20$

### Checkpoint 5: Trộn đề An toàn & Khảo thí Hoàn thành
- Không phát sinh quy luật lộ đáp án cho học sinh; bảng ma trận đáp án chính xác tuyệt đối.
- `pytest tests/test_rules_shuffling.py` đạt 100%.

---

### Phase 6: Xuất Bản Đa Định Dạng & Vận Hành Hệ Thống (Completed)
- [x] **EX-01:** Dịch vụ tạo file Word OpenXML (.docx) chuẩn 2 cột
- [x] **EX-02:** Tạo bảng phách thông tin thí sinh chuẩn Bộ GD&ĐT trong file Word
- [x] **EX-03:** Chuyển đổi công thức LaTeX sang OMML native `<m:oMath>` trong Word
- [x] **EX-04:** Động cơ sinh PDF vector siêu tốc thuần Python bằng ReportLab (<100ms)
- [x] **EX-05:** Nạp font Times New Roman Unicode Windows (`times.ttf`) cho ReportLab
- [x] **EX-06:** Xuất bản tài liệu Hướng dẫn giải chi tiết (Word & PDF)
- [x] **EX-07:** Xuất bản Bảng đáp án tổng hợp các mã đề (Word, PDF, CSV)
- [x] **EX-08:** API `GET /api/v1/exams/{id}/export-docx` (Tải lẻ file Word)
- [x] **EX-09:** API `GET /api/v1/exams/{id}/export-pdf` (Tải lẻ file PDF)
- [x] **EX-10:** API `GET /api/v1/exams/{id}/export-zip` hỗ trợ `format=all|docx|pdf`
- [x] **EX-11:** Cơ chế tải Blob Client-side dập tắt lỗi *Failed - Unknown server error*
- [x] **SO-01:** Script `start_server.py` tự động phát hiện và giải phóng socket cổng 8000
- [x] **SO-02:** Route `/favicon.ico` trả về HTTP 204 chống lỗi console
- [x] **SO-03:** Bổ sung cache-buster `?v=...` chống lưu cache script cũ trên trình duyệt
- [x] **SO-04:** Bộ test suite tự động 39 test cases bao phủ toàn diện hệ thống

### Checkpoint 6: Xuất bản & Ổn định Vận hành Hoàn thành
- Tải file lẻ và trọn gói ZIP thành công trên Real Browser; 39/39 tests passed trong ~10s.

---

### Phase 7: Mở Rộng Doanh Nghiệp & Đám Mây (Future Roadmap / Backlog)
- [ ] **BL-01:** CSDL Quản lý Tài khoản, Vai trò (RBAC) và Đơn vị trường học (Multi-tenant)
- [ ] **BL-02:** Middleware Xác thực JWT Token & Phân quyền thao tác API
- [ ] **BL-03:** API Đăng nhập, Đăng xuất, Refresh Token & Đổi mật khẩu
- [ ] **BL-04:** Giao diện Phê duyệt câu hỏi dành riêng cho Tổ trưởng chuyên môn
- [ ] **BL-05:** Adapter tích hợp Cloud Multimodal LLM (Gemini 1.5 Pro / Claude 3.5 Sonnet)
- [ ] **BL-06:** Adapter tích hợp DocTR/TrOCR mã nguồn mở cho chữ viết tay
- [ ] **BL-07:** CSDL & REST API Quản lý Ca thi trực tuyến (CBT Session)
- [ ] **BL-08:** Giao diện Học sinh làm bài thi trực tuyến với đồng hồ đếm ngược
- [ ] **BL-09:** WebSocket đồng bộ câu trả lời học sinh mỗi 15 giây
- [ ] **BL-10:** Module ghi nhận vi phạm thi cử (chuyển tab trình duyệt, mất tiêu điểm)
- [ ] **BL-11:** Thuật toán OpenCV căn chỉnh 4 điểm mốc định vị phiếu trắc nghiệm 2025
- [ ] **BL-12:** Thuật toán nhận diện điểm tô đen bút chì 2B trên phiếu OMR
- [ ] **BL-13:** API nhận ảnh phiếu trắc nghiệm và trả về điểm số tự động
- [ ] **BL-14:** Viết Dockerfile đa tầng (Multi-stage build) cho Backend & Frontend
- [ ] **BL-15:** Viết file `docker-compose.yml` tích hợp Postgres & Redis
- [ ] **BL-16:** Thiết lập pipeline GitHub Actions CI tự động chạy kiểm thử khi PR/Push

---

## 4. Risks and Mitigations

| Rủi ro (Risk) | Mức độ | Biện pháp giảm thiểu (Mitigation) |
| :--- | :---: | :--- |
| **Lỗi định dạng khi in ấn Word/PDF trên các máy tính khác nhau** | Cao | Sử dụng cấu trúc OpenXML chuẩn và ReportLab nhúng trực tiếp font Unicode Times New Roman có sẵn trên Windows. |
| **Đụng độ cổng mạng Socket 10048 trên Windows** | Trung bình | Tích hợp script `start_server.py` tự động quét phát hiện tiến trình cũ và giải phóng socket trước khi lắng nghe. |
| **Trùng lặp câu hỏi làm loãng ngân hàng đề** | Trung bình | Triển khai Cosine Similarity $\ge 0.90$ chặn lưu câu hỏi trùng lặp ngay từ bước hậu kiểm HITL. |
| **Học sinh phát hiện quy luật đáp án khi đảo đề** | Cao | Thực thi nghiêm ngặt 4 quy tắc an toàn trộn đề, cố định các đáp án "Tất cả các ý trên" vào vị trí D. |

---

## Open Questions
1. Nhà trường có yêu cầu kết nối SSO với Hệ sinh thái ngành giáo dục (vnEdu / SMAS / Google Workspace for Education) ở giai đoạn tiếp theo không?
2. Có kế hoạch triển khai máy chủ GPU tại chỗ (On-Premise) để chạy mô hình OCR mã nguồn mở (như DocTR/TrOCR) thay vì gọi Cloud API không?
