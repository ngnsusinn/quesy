# Kế Hoạch Triển Khai Hệ Thống Quesy (Teacher-Centric Implementation Plan v3.0)
*Hệ thống Trợ Lý Khảo Thí & Ngân Hàng Đề Thi Dành Riêng Cho Giáo Viên Cá Nhân*
*Căn cứ pháp lý: Thông tư 32/2018/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT (Định dạng đề thi 2025)*

## 1. Định Hướng & Phạm Vi Dự Án (Scope & Boundaries)
- **Đối tượng sử dụng duy nhất:** Giáo viên bộ môn (người dùng cá nhân độc lập). 
- **Không phân cấp quản trị:** Tuyệt đối không xây dựng các cấp quản trị phức tạp như Tổ trưởng chuyên môn duyệt đề, Ban giám hiệu, hay phân quyền trường học. Giáo viên toàn quyền biên soạn, lưu trữ, duyệt và sử dụng ngân hàng đề của chính mình.
- **Không có cổng thi trực tuyến cho học sinh:** Giai đoạn này không làm phân hệ học sinh đăng nhập thi trực tuyến (không có CBT Exam Taker, không có chống gian lận chuyển tab).
- **4 Trọng tâm nghiệp vụ cốt lõi:**
  1. **Ngân hàng câu hỏi & Cây kiến thức chuẩn:** Cây năng lực 6 tầng Thông tư 32 (không phân chia theo bộ sách) và 3 phần thi theo Quyết định 764/QĐ-BGDĐT.
  2. **Số hóa AI & OCR đề thi (HITL Studio):** Tự động bóc tách từ Word/PDF/Ảnh, trích xuất công thức KaTeX, cắt ảnh đồ thị WebP, đối chiếu song song và sửa nhanh công thức.
  3. **Tạo đề thi, Trộn đề & Xuất bản in ấn:** Ma trận đề thi bám sát YCCĐ, động cơ trộn đề an toàn 4 nguyên tắc (giữ nguyên câu chùm, khóa đáp án neo vào vị trí D, ma trận đáp án), xuất bản Word OpenXML (.docx) 2 cột OMML native và PDF vector siêu tốc ReportLab (<100ms).
  4. **Chấm thi & Thống kê điểm số giáo viên:** Chấm tự động qua ảnh chụp / webcam phiếu trả lời trắc nghiệm OMR 2025, nhập điểm nhanh theo danh sách lớp, phân tích trắc lượng học cổ điển (CTT: độ khó p, độ phân biệt D) và thống kê phổ điểm.

---

## 2. Quyết Định Kiến Trúc Cốt Lõi (Architecture Decisions)
- **AD-01 (Taxonomy Independence):** Không phân chia danh mục theo bộ sách giáo khoa thương mại. Phân tầng theo: Cấp học/Lớp -> Môn học -> Mạch nội dung -> Chủ đề -> Bài học -> Yêu cầu cần đạt (YCCĐ) -> Dạng câu hỏi (Problem Archetype).
- **AD-02 (2025 Assessment Standards):** Hỗ trợ đầy đủ 3 phần định dạng mới: Phần I (Trắc nghiệm 4 lựa chọn), Phần II (Đúng/Sai 4 ý chấm điểm lũy tiến 0.1 - 0.25 - 0.5 - 1.0 theo RULE-01), Phần III (Trả lời ngắn).
- **AD-03 (Single-User Teacher Studio):** Toàn bộ giao diện Web Studio được thiết kế tối ưu cho 1 giáo viên thao tác: không cần đăng nhập phức tạp, quản lý kho đề cá nhân nhanh chóng.
- **AD-04 (Safe Shuffling Engine):** Trộn đề đảm bảo 4 nguyên tắc khảo thí: Section Integrity, Passage Integrity, Option Anchor Lock (cố định đáp án neo vào vị trí D), và tự động sinh Ma trận Ánh xạ Đáp án.
- **AD-05 (Resilient Document Publishing):** Xuất bản Word chuẩn OpenXML (.docx) 2 cột kèm công thức OMML native; xuất bản PDF vector siêu tốc thuần Python qua ReportLab (<100ms) nạp font Times New Roman Unicode từ Windows.
- **AD-06 (Automated OMR Grading & Psychometrics):** Tích hợp thị giác máy tính OpenCV chấm tự động phiếu trắc nghiệm từ camera máy tính của giáo viên và tính toán chỉ số CTT (p, D).

---

## 3. Phân Kỳ Triển Khai Micro-Tasks (7 Phases)

### Phase 1: CSDL & Cây Kiến Thức Thông Tư 32 (Hoàn thành)
- [x] **TS-01:** ORM Model `Grade` & `Subject`
- [x] **TS-02:** ORM Model `ContentStrand` & `Topic`
- [x] **TS-03:** ORM Model `Lesson` & `LearningOutcome` (YCCĐ)
- [x] **TS-04:** ORM Model `ProblemArchetype` (Dạng câu hỏi)
- [x] **TS-05:** Pydantic Schemas cho Cây phân cấp lồng nhau
- [x] **TS-06:** API Endpoint `GET /api/v1/taxonomy/tree`
- [x] **TS-07:** API Endpoints tra cứu Môn học & Khối lớp
- [x] **TS-08:** Seed Data 6 tầng danh mục Toán 12 chuẩn TT 32
- [x] **TS-09:** Automated Test kiểm tra cây 6 tầng & vắng mặt trường bộ sách

### Phase 2: Ngân Hàng Câu Hỏi & Động Cơ Chống Trùng (Hoàn thành)
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

### Phase 3: Pipeline Số Hóa AI & Studio Hậu Kiểm HITL (Hoàn thành)
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

### Phase 4: Ma Trận Đề Thi & Động Cơ Sinh Đề (Hoàn thành)
- [x] **MX-01:** ORM Models `ExamMatrix` và `ExamMatrixItem`
- [x] **MX-02:** Pydantic Schema cho cấu hình ma trận đề thi
- [x] **MX-03:** API `POST /api/v1/matrix` tạo mới ma trận đề thi
- [x] **MX-04:** API `GET /api/v1/matrix` danh sách ma trận
- [x] **MX-05:** Thuật toán kiểm tra số dư khả dụng (Inventory Checker)
- [x] **MX-06:** Giao diện lưới cấu hình ma trận đề thi trên Web Studio
- [x] **EG-01:** ORM Models `MasterExam` và `MasterExamItem`
- [x] **EG-02:** Thuật toán sinh đề gốc có trọng số đáp ứng ràng buộc ma trận
- [x] **EG-03:** Bộ lọc loại trừ câu hỏi đã thi trong N ngày gần nhất (Cooldown list)
- [x] **EG-04:** API `POST /api/v1/exams/generate` sinh đề gốc tự động

### Phase 5: Trộn Đề An Toàn & Khảo Thí CTT (Hoàn thành)
- [x] **SH-01:** ORM Models `ExamVariant` và `ExamVariantItem`
- [x] **SH-02:** Thực thi RULE-01: Chấm điểm lũy tiến Đúng/Sai (0.1, 0.25, 0.5, 1.0đ)
- [x] **SH-03:** Thực thi RULE-02: Option Anchor Rule khóa cố định đáp án neo vào vị trí D
- [x] **SH-04:** Thực thi RULE-03: Section Integrity & Passage Integrity
- [x] **SH-05:** Thực thi RULE-04: Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu
- [x] **SH-06:** API `POST /api/v1/exams/{id}/shuffle` sinh các mã đề hoán vị
- [x] **SH-07:** Giao diện tab chuyển đổi xem trước từng mã đề (101, 102, 103, 104)
- [x] **SH-08:** Giao diện bảng ma trận đáp án tổng hợp đối chiếu
- [x] **AN-01:** API `POST /api/v1/exams/{id}/analytics` tiếp nhận bảng điểm thi
- [x] **AN-02:** Thuật toán tính độ khó p = R/N
- [x] **AN-03:** Thuật toán tính độ phân biệt D = P_H - P_L (nhóm 27% cao - 27% thấp)
- [x] **AN-04:** Tự động gắn cờ cảnh báo câu hỏi lỗi khi D < 0.20

### Phase 6: Xuất Bản Đa Định Dạng & Vận Hành Hệ Thống (Hoàn thành)
- [x] **EX-01:** Dịch vụ tạo file Word OpenXML (.docx) chuẩn 2 cột
- [x] **EX-02:** Tạo bảng phách thông tin thí sinh chuẩn Bộ GD&ĐT trong file Word
- [x] **EX-03:** Chuyển đổi công thức LaTeX sang OMML native trong Word
- [x] **EX-04:** Động cơ sinh PDF vector siêu tốc thuần Python bằng ReportLab (<100ms)
- [x] **EX-05:** Nạp font Times New Roman Unicode Windows (`times.ttf`) cho ReportLab
- [x] **EX-06:** Xuất bản tài liệu Hướng dẫn giải chi tiết (Word & PDF)
- [x] **EX-07:** Xuất bản Bảng đáp án tổng hợp các mã đề (Word, PDF, CSV)
- [x] **EX-08:** API `GET /api/v1/exams/{id}/export-docx` (Tải lẻ file Word)
- [x] **EX-09:** API `GET /api/v1/exams/{id}/export-pdf` (Tải lẻ file PDF)
- [x] **EX-10:** API `GET /api/v1/exams/{id}/export-zip` hỗ trợ `format=all|docx|pdf`
- [x] **EX-11:** Cơ chế tải Blob Client-side dập tắt lỗi *Failed - Unknown server error*
- [x] **EX-12:** Xuất bản Mẫu Phiếu trả lời trắc nghiệm OMR 2025 trắng (.pdf) đính kèm trong gói ZIP
- [x] **SO-01:** Script `start_server.py` tự động phát hiện và giải phóng socket cổng 8000
- [x] **SO-02:** Route `/favicon.ico` trả về HTTP 204 chống lỗi console
- [x] **SO-03:** Bổ sung cache-buster `?v=...` chống lưu cache script cũ trên trình duyệt
- [x] **SO-04:** Bộ test suite tự động 39 test cases bao phủ toàn diện hệ thống

### Phase 7: Phân Hệ Chấm Thi Giáo Viên & Mở Rộng Trợ Lý OCR (Roadmap / Backlog)
- [x] **GM-01:** ORM Model `Classroom` & `StudentRoster` (Quản lý danh sách lớp của giáo viên)
- [ ] **GM-02:** Bảng nhập điểm nhanh dạng lưới câu hỏi x học sinh trên Web Studio
- [x] **GM-03:** Nhập / Xuất bảng điểm lớp học từ file Excel (.xlsx / .csv)
- [ ] **GM-04:** Module OMR: Thuật toán OpenCV căn chỉnh 4 mốc định vị góc phiếu thi 2025
- [ ] **GM-05:** Module OMR: Nhận diện điểm tô chì 2B cho Phần I (A,B,C,D), Phần II (Đ/S), Phần III (Tô số)
- [ ] **GM-06:** API `POST /api/v1/grading/scan-omr` nhận ảnh phiếu thi và chấm tự động theo mã đề
- [ ] **GM-07:** Giao diện chấm thi trực tiếp bằng Camera / Webcam máy tính của giáo viên
- [ ] **GM-08:** Biểu đồ thống kê phân phổ điểm lớp học (Histogram, Điểm TB, Độ lệch chuẩn)
- [x] **AI-08:** Adapter kết nối Cloud Vision API (Gemini 1.5 / Claude) cho đề viết tay / ảnh mờ
- [ ] **AI-09:** Adapter DocTR cục bộ hỗ trợ OCR offline không cần mạng internet
- [x] **PK-01:** Hỗ trợ chế độ Web Ngoại tuyến (Offline PWA / Service Worker) trên trình duyệt
- [x] **PK-02:** Viết Multi-stage Dockerfile & docker-compose cho máy tính giáo viên
- [x] **PK-03:** Thiết lập pipeline GitHub Actions CI tự động chạy kiểm thử khi PR/Push
