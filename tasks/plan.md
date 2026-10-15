# Kế Hoạch Triển Khai Hệ Thống (Implementation Plan): Quesy System

## Overview
Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI Số hoá (QUESY) là nền tảng khảo thí chuẩn quốc gia tuân thủ 100% Thông tư 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (định dạng thi 2025). Hệ thống tích hợp toàn diện từ bóc tách OCR/AI tài liệu gốc, Studio hậu kiểm đối chiếu song song (HITL), ngân hàng câu hỏi phân tầng 6 cấp độ năng lực theo Yêu cầu cần đạt (YCCĐ), ma trận đề thi ma trận hóa tự động, động cơ sinh và trộn đề 4 nguyên tắc an toàn khảo thí, dịch vụ xuất bản in ấn OpenXML Word/PDF vector siêu tốc, cùng phân tích trắc lượng cổ điển (CTT).

## Architecture Decisions
- **AD-01 (Taxonomy Independence):** Tuyệt đối không phân chia danh mục theo bộ sách giáo khoa thương mại. Cấu trúc cây kiến thức chuẩn hóa 6 tầng: Cấp học/Lớp $\rightarrow$ Môn học $\rightarrow$ Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ Yêu cầu cần đạt (YCCĐ), phân nhánh tới tầng Dạng câu hỏi (Problem Archetype).
- **AD-02 (2025 Assessment Standards):** Hỗ trợ đầy đủ 3 phần định dạng mới: Phần I (Trắc nghiệm 4 lựa chọn), Phần II (Đúng/Sai 4 ý chấm điểm lũy tiến 0.1 - 0.25 - 0.5 - 1.0 theo RULE-01), Phần III (Trả lời ngắn).
- **AD-03 (HITL Studio Verification):** Không tin tưởng 100% vào đầu ra thô của AI; bắt buộc có giao diện hậu kiểm song song (Side-by-side synchronized review) với thanh đo độ tin cậy và bộ soạn thảo công thức KaTeX trực tiếp.
- **AD-04 (Safe Shuffling Engine):** Trộn đề đảm bảo 4 nguyên tắc khảo thí: Section Integrity, Passage Integrity, Option Anchor Lock (cố định đáp án neo vào vị trí D), và tự động sinh Ma trận Ánh xạ Đáp án.
- **AD-05 (Resilient Document Publishing):** Xuất bản Word chuẩn OpenXML (.docx) 2 cột kèm công thức OMML native; xuất bản PDF vector siêu tốc thuần Python qua ReportLab (<100ms) nạp font Times New Roman Unicode từ Windows.
- **AD-06 (Classical Test Theory Analytics):** Tích hợp tính toán độ khó ($p$) và độ phân biệt ($D$), tự động gắn cờ câu hỏi có nguy cơ lỗi kỹ thuật khi $D < 0.20$.

---

## Phased Task Index & Milestones

### Phase 1: Nền Tảng Danh Mục & Ngân Hàng Câu Hỏi Chuẩn Thông Tư 32 (Completed)
- [x] **Task 01:** Thiết kế lược đồ CSDL & Cây kiến thức 6 tầng + Dạng câu hỏi (TT 32)
- [x] **Task 02:** Xây dựng API Quản trị Ngân hàng câu hỏi & 5 thể thức khảo thí (QĐ 764)
- [x] **Task 03:** Xây dựng Thuật toán Chống trùng lặp câu hỏi (Cosine Similarity $\ge 0.90$)
- [x] **Task 04:** Xây dựng Giao diện Web Quản trị Ngân hàng Câu hỏi & Bộ lọc Danh mục

### Checkpoint 1: Foundation Completed
- [x] Seed thành công 54 câu hỏi Toán 12 chuẩn định dạng 2025.
- [x] API Contract validation & schema tests đạt 100%.

---

### Phase 2: Pipeline Tiếp Nhận & Studio Hậu Kiểm AI (HITL Studio) (Completed)
- [x] **Task 05:** Xây dựng Engine Bóc tách Tài liệu (DOCX MathType & PDF Layout Extractor)
- [x] **Task 06:** Pipeline Tự động Cắt Hình ảnh / Đồ thị & Gợi ý Gán nhãn AI (Auto-tagging)
- [x] **Task 07:** Xây dựng Giao diện Studio Hậu kiểm Đối chiếu Song song (Side-by-Side Review)
- [x] **Task 08:** Xây dựng Modal Biên tập Nhanh Công thức Toán LaTeX & KaTeX Live Preview

### Checkpoint 2: AI Digitization Completed
- [x] Luồng số hóa tài liệu hoạt động mượt mà với Synchronized Scroll và Confidence Barometer.
- [x] Trích xuất công thức và hình vẽ webp chính xác.

---

### Phase 3: Ma Trận Đề Thi & Động Cơ Trộn Đề An Toàn (Completed)
- [x] **Task 09:** Xây dựng Module Thiết lập Bản đặc tả & Ma trận Đề thi theo YCCĐ
- [x] **Task 10:** Xây dựng Thuật toán Sinh Đề Gốc Cân bằng Kho & Loại trừ Câu đã thi
- [x] **Task 11:** Xây dựng Động cơ Trộn Đề Hoán vị An toàn (4 Quy tắc Khảo thí An toàn)
- [x] **Task 12:** Xây dựng Thuật toán Phân tích Chất lượng Câu hỏi Hậu kiểm (CTT: $p, D$)

### Checkpoint 3: Assessment Core Completed
- [x] Đạt 100% trong 100 lần lặp kiểm thử bảo toàn Option Anchor Rule.
- [x] Sinh bảng ma trận đáp án đối chiếu chính xác cho 4 mã đề (101, 102, 103, 104).

---

### Phase 4: Xuất Bản In Ấn Đa Định Dạng & Kiểm Thử Toàn Diện (Completed)
- [x] **Task 13:** Dịch vụ Xuất bản Word OpenXML (.docx) 2 cột chuẩn Bộ GD&ĐT
- [x] **Task 14:** Động cơ Xuất bản PDF Vector Siêu tốc ReportLab Unicode Times New Roman
- [x] **Task 15:** Đóng gói Xuất bản Trọn gói ZIP Đa định dạng (Word, PDF, Đáp án CSV)
- [x] **Task 16:** Xây dựng Bộ Kiểm Thử Tự Động Toàn Diện (Test Suite 39 Cases)

### Checkpoint 4: Production Export & Testing Completed
- [x] 39/39 test cases PASSED (100%).
- [x] Kiểm thử trình duyệt thực tế (Real Browser CDP): Tải lẻ PDF/Word và tải trọn gói ZIP thành công.

---

### Phase 5: Mở Rộng Doanh Nghiệp & Đám Mây (Future Roadmap / Backlog)
- [ ] **Task 17:** Tích hợp Phân quyền Người dùng Đa cấp & Đa trường học (Multi-tenant RBAC)
- [ ] **Task 18:** Tích hợp Multimodal Vision Cloud API (Gemini Vision / Claude 3.5 Sonnet / DocTR)
- [ ] **Task 19:** Phân hệ Thi Trực Tuyến Học Sinh (Online CBT Exam Taker) & Chống gian lận
- [ ] **Task 20:** Phân hệ Chấm Phiếu Trả lời Trắc nghiệm Tự động OMR qua Webcam / Scanner
- [ ] **Task 21:** Đóng gói Docker, K8s Helm Chart & Thiết lập CI/CD GitHub Actions

### Checkpoint 5: Enterprise Cloud Readiness
- [ ] Đạt chuẩn bảo mật OWASP Top 10 và khả năng chịu tải 50,000 thí sinh đồng thời.

---

## Risks and Mitigations

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
