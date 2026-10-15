# BÁO CÁO PHÂN RÃ CÔNG VIỆC VI MÔ & BẢN ĐỒ GITHUB PROJECT KANBAN (v2.0)
**Dự án: Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI Số hoá (QUESY)**  
**Căn cứ pháp lý:** Thông tư số 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT, Quyết định 764/QĐ-BGDĐT  
**Kỹ năng thực hiện:** `planning-and-task-breakdown` (SKILL.md)  
**Tập tin kế hoạch liên quan:** `tasks/plan.md`, `tasks/todo.md`  

---

## I. TỔNG QUAN TIẾN ĐỘ DỰ ÁN VI MÔ (ATOMIC PROGRESS DASHBOARD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 TIẾN ĐỘ PHÂN RÃ VI MÔ TOÀN BỘ HỆ THỐNG QUESY                 │
│  [███████████████████████████████████████████████████████░░░░░░░░] 72.4%    │
│                                                                             │
│  • Tổng số công việc vi mô (Micro-Tasks):  58 Tasks                         │
│  • Đã hoàn thành & Đã kiểm thử (Done):     42 Tasks (100% Cốt lõi) [x]      │
│  • Kế hoạch mở rộng (Roadmap / Backlog):   16 Tasks (Doanh nghiệp & Cloud)  │
│  • Tỷ lệ kiểm thử tự động (Test Suite):    39 / 39 Tests (100% Passed)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## II. BẢNG DỮ LIỆU IMPORT GITHUB PROJECT KANBAN (58 ATOMIC TASKS)

Bảng phân rã chi tiết từng chức năng nhỏ (Atomic Single Responsibility), sẵn sàng xuất ra file CSV để Import vào **GitHub Projects**:

| ID | Issue Code | Tiêu đề Issue (Title) | Status | Milestone / Phase | Labels | Scope |
| :---: | :---: | :--- | :---: | :--- | :--- | :---: |
| **1** | `TS-01` | `[TAXONOMY] Định nghĩa ORM Model Grade & Subject` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `model`, `tt32` | XS |
| **2** | `TS-02` | `[TAXONOMY] Định nghĩa ORM Model ContentStrand & Topic` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `model`, `tt32` | XS |
| **3** | `TS-03` | `[TAXONOMY] Định nghĩa ORM Model Lesson & LearningOutcome (Mã YCCĐ)` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `model`, `yccd` | XS |
| **4** | `TS-04` | `[TAXONOMY] Định nghĩa ORM Model ProblemArchetype (Dạng câu hỏi)` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `model`, `archetype` | XS |
| **5** | `TS-05` | `[TAXONOMY] Pydantic Schemas cho Cây phân cấp lồng nhau` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `schema`, `pydantic` | XS |
| **6** | `TS-06` | `[TAXONOMY] API Endpoint GET /api/v1/taxonomy/tree` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `api`, `taxonomy` | S |
| **7** | `TS-07` | `[TAXONOMY] API Endpoints danh sách Môn học & Khối lớp` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `api`, `taxonomy` | XS |
| **8** | `TS-08` | `[TAXONOMY] Nạp dữ liệu hạt giống Toán 12 chuẩn TT 32` | **Done [x]** | `Phase 1: Taxonomy TT32` | `backend`, `seed`, `math12` | S |
| **9** | `TS-09` | `[TAXONOMY] Test kiểm tra cây 6 tầng & vắng mặt trường bộ sách` | **Done [x]** | `Phase 1: Taxonomy TT32` | `testing`, `compliance`, `tt32` | S |
| **10** | `IB-01` | `[ITEM-BANK] Định nghĩa ORM Models Question, Option, SubStatement` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `model`, `qd764` | S |
| **11** | `IB-02` | `[ITEM-BANK] Định nghĩa Enums ItemFormat cho 5 thể thức QĐ 764` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `enum`, `qd764` | S |
| **12** | `IB-03` | `[ITEM-BANK] Định nghĩa Enums CognitiveLevel theo 3 mức độ TT 32` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `enum`, `tt32` | S |
| **13** | `IB-04` | `[ITEM-BANK] Pydantic Validator cho câu hỏi Đúng/Sai 4 khẳng định` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `validator`, `pydantic` | XS |
| **14** | `IB-05` | `[ITEM-BANK] API POST /api/v1/questions tạo mới câu hỏi đa thể thức` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `api`, `crud` | S |
| **15** | `IB-06` | `[ITEM-BANK] API GET /api/v1/questions tra cứu, lọc & phân trang` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `api`, `crud` | S |
| **16** | `IB-07` | `[ITEM-BANK] API GET /api/v1/questions/{id} xem chi tiết câu hỏi` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `api`, `crud` | XS |
| **17** | `IB-08` | `[ITEM-BANK] API PUT /api/v1/questions/{id} cập nhật câu hỏi` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `api`, `crud` | S |
| **18** | `IB-09` | `[ITEM-BANK] API DELETE /api/v1/questions/{id} xóa an toàn (Idempotent)` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `api`, `crud` | XS |
| **19** | `DD-01` | `[DEDUP] Thuật toán chuẩn hóa chuỗi & tính Vector Cosine Similarity` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `algorithm`, `vector` | S |
| **20** | `DD-02` | `[DEDUP] Logic cảnh báo trùng ngưỡng 80% & chặn lưu ngưỡng 90%` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `algorithm`, `dedup` | S |
| **21** | `IB-10` | `[ITEM-BANK] Nạp hạt giống 54 câu hỏi Toán 12 định dạng mới 2025` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `backend`, `seed`, `exam2025` | S |
| **22** | `IB-11` | `[ITEM-BANK] Giao diện Bảng Ngân hàng câu hỏi render KaTeX` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `frontend`, `katex`, `ui` | S |
| **23** | `IB-12` | `[ITEM-BANK] Bộ lọc giao diện theo Môn, Lớp, Mức độ & YCCĐ` | **Done [x]** | `Phase 2: Item Bank & Dedup` | `frontend`, `filter`, `ux` | XS |
| **24** | `AI-01` | `[AI-INGEST] API POST /api/v1/digitize/upload nhận file đề thi` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `api`, `upload` | S |
| **25** | `AI-02` | `[AI-INGEST] Engine bóc tách văn bản PDF layout segmentation` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `pypdf`, `parsing` | S |
| **26** | `AI-03` | `[AI-INGEST] Engine bóc tách DOCX & dịch MathType sang LaTeX` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `docx`, `mathtype` | S |
| **27** | `AI-04` | `[AI-INGEST] Module chuẩn hóa công thức toán LaTeX KaTeX` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `regex`, `latex` | XS |
| **28** | `AI-05` | `[AI-INGEST] Engine nhận diện cấu trúc 3 phần đề thi 2025` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `nlp`, `structure` | S |
| **29** | `AI-06` | `[AI-INGEST] Bounding Box Image Cropper cắt ảnh đồ thị sang WebP` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `vision`, `pillow` | S |
| **30** | `AI-07` | `[AI-INGEST] Heuristic Auto-tagging gợi ý mức độ nhận thức & YCCĐ` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `backend`, `ai`, `tagging` | S |
| **31** | `UI-01` | `[HITL-STUDIO] Bố cục Studio hậu kiểm 2 cột đối xứng` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `frontend`, `hitl`, `layout` | S |
| **32** | `UI-02` | `[HITL-STUDIO] Thanh đo độ tin cậy AI (Confidence Barometer)` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `frontend`, `hitl`, `widget` | XS |
| **33** | `UI-03` | `[HITL-STUDIO] Cơ chế cuộn đồng bộ (Synchronized Scrolling)` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `frontend`, `interaction`, `scroll` | S |
| **34** | `UI-04` | `[HITL-STUDIO] Thao tác click trực tiếp đổi đáp án đúng trên thẻ` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `frontend`, `quick-edit`, `ux` | XS |
| **35** | `UI-05` | `[HITL-STUDIO] Modal soạn thảo công thức LaTeX với Live Preview KaTeX` | **Done [x]** | `Phase 3: AI Digitize & HITL` | `frontend`, `katex`, `modal` | S |
| **36** | `MX-01` | `[MATRIX] Định nghĩa ORM Models ExamMatrix và ExamMatrixItem` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `model`, `matrix` | S |
| **37** | `MX-02` | `[MATRIX] Pydantic Schemas cấu hình ma trận đề thi` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `schema`, `matrix` | XS |
| **38** | `MX-03` | `[MATRIX] API POST /api/v1/matrix tạo mới ma trận đề thi` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `api`, `matrix` | S |
| **39** | `MX-04` | `[MATRIX] API GET /api/v1/matrix & GET /api/v1/matrix/{id}` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `api`, `matrix` | XS |
| **40** | `MX-05` | `[MATRIX] Thuật toán kiểm tra số dư khả dụng trong ngân hàng` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `algorithm`, `inventory` | S |
| **41** | `MX-06` | `[MATRIX] Giao diện lưới cấu hình ma trận đề thi trên Web Studio` | **Done [x]** | `Phase 4: Matrix & Assembly` | `frontend`, `matrix`, `grid` | S |
| **42** | `EG-01` | `[ASSEMBLY] Định nghĩa ORM Models MasterExam và MasterExamItem` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `model`, `master` | S |
| **43** | `EG-02` | `[ASSEMBLY] Thuật toán sinh đề gốc ngẫu nhiên có trọng số theo ma trận` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `algorithm`, `solver` | S |
| **44** | `EG-03` | `[ASSEMBLY] Bộ lọc loại trừ câu hỏi đã thi trong N ngày (Cooldown)` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `algorithm`, `filter` | XS |
| **45** | `EG-04` | `[ASSEMBLY] API POST /api/v1/exams/generate sinh đề gốc tự động` | **Done [x]** | `Phase 4: Matrix & Assembly` | `backend`, `api`, `generate` | S |
| **46** | `SH-01` | `[SHUFFLER] Định nghĩa ORM Models ExamVariant và ExamVariantItem` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `model`, `variant` | S |
| **47** | `SH-02` | `[SHUFFLER] Thực thi RULE-01: Chấm điểm lũy tiến Đúng/Sai 4 bậc` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `grading`, `rule01` | S |
| **48** | `SH-03` | `[SHUFFLER] Thực thi RULE-02: Option Anchor Rule khóa đáp án vào D` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `algorithm`, `rule02` | S |
| **49** | `SH-04` | `[SHUFFLER] Thực thi RULE-03: Section Integrity & Passage Integrity` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `algorithm`, `rule03` | S |
| **50** | `SH-05` | `[SHUFFLER] Thực thi RULE-04: Tự động sinh Ma trận Ánh xạ Đáp án` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `algorithm`, `rule04` | S |
| **51** | `SH-06` | `[SHUFFLER] API POST /api/v1/exams/{id}/shuffle sinh các mã đề hoán vị` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `api`, `shuffler` | S |
| **52** | `SH-07` | `[SHUFFLER] Giao diện tab chuyển đổi xem trước từng mã đề (101-104)` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `frontend`, `ui`, `tabs` | S |
| **53** | `SH-08` | `[SHUFFLER] Giao diện bảng ma trận đáp án tổng hợp đối chiếu` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `frontend`, `ui`, `table` | XS |
| **54** | `AN-01` | `[ANALYTICS] API POST /api/v1/exams/{id}/analytics nhận bảng điểm thi` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `api`, `analytics` | S |
| **55** | `AN-02` | `[ANALYTICS] Thuật toán tính độ khó cổ điển p = R/N` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `algorithm`, `ctt` | XS |
| **56** | `AN-03` | `[ANALYTICS] Thuật toán tính độ phân biệt D = P_H - P_L (nhóm 27%)` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `algorithm`, `ctt` | S |
| **57** | `AN-04` | `[ANALYTICS] Tự động gắn cờ cảnh báo câu hỏi lỗi khi D < 0.20` | **Done [x]** | `Phase 5: Shuffling & Psychometrics` | `backend`, `qa`, `flagging` | XS |
| **58** | `EX-01` | `[EXPORT-DOCX] Dịch vụ tạo file Word OpenXML (.docx) chuẩn 2 cột` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `export`, `docx` | S |
| **59** | `EX-02` | `[EXPORT-DOCX] Tạo bảng phách thông tin thí sinh chuẩn Bộ GD&ĐT` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `docx`, `layout` | XS |
| **60** | `EX-03` | `[EXPORT-DOCX] Chuyển đổi công thức LaTeX sang OMML native trong Word` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `omml`, `math` | S |
| **61** | `EX-04` | `[EXPORT-PDF] Động cơ sinh PDF vector siêu tốc thuần Python (<100ms)` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `reportlab`, `pdf` | S |
| **62** | `EX-05` | `[EXPORT-PDF] Nạp font Times New Roman Unicode Windows cho ReportLab` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `unicode`, `fonts` | XS |
| **63** | `EX-06` | `[EXPORT-DOCX] Xuất bản tài liệu Hướng dẫn giải chi tiết (Word & PDF)` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `solution`, `export` | S |
| **64** | `EX-07` | `[EXPORT-CSV] Xuất bản Bảng đáp án tổng hợp (Word, PDF, CSV)` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `csv`, `matrix` | S |
| **65** | `EX-08` | `[EXPORT-DOCX] API GET /api/v1/exams/{id}/export-docx tải lẻ file Word` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `api`, `docx` | S |
| **66** | `EX-09` | `[EXPORT-PDF] API GET /api/v1/exams/{id}/export-pdf tải lẻ file PDF` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `api`, `pdf` | S |
| **67** | `EX-10` | `[EXPORT-ZIP] API GET /api/v1/exams/{id}/export-zip hỗ trợ all/docx/pdf` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `api`, `zip` | S |
| **68** | `EX-11` | `[FRONTEND] Cơ chế tải Blob Client-side dập tắt lỗi Unknown Server Error` | **Done [x]** | `Phase 6: Publishing & Operations` | `frontend`, `blob`, `download` | S |
| **69** | `SO-01` | `[SERVER] Script start_server.py tự động giải phóng socket cổng 8000` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `socket`, `devops` | S |
| **70** | `SO-02` | `[SERVER] Route /favicon.ico trả về HTTP 204 chống lỗi console` | **Done [x]** | `Phase 6: Publishing & Operations` | `backend`, `api`, `favicon` | XS |
| **71** | `SO-03` | `[FRONTEND] Bổ sung cache-buster ?v=... chống lưu cache script cũ` | **Done [x]** | `Phase 6: Publishing & Operations` | `frontend`, `cache-buster`, `html` | XS |
| **72** | `SO-04` | `[TESTING] Bộ test suite tự động 39 test cases bao phủ toàn diện` | **Done [x]** | `Phase 6: Publishing & Operations` | `testing`, `pytest`, `e2e` | M |
| **73** | `BL-01` | `[RBAC] CSDL quản lý Tài khoản, Vai trò (RBAC) & Đơn vị trường học` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `model`, `rbac` | S |
| **74** | `BL-02` | `[RBAC] Middleware xác thực JWT Token & Phân quyền thao tác API` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `jwt`, `security` | S |
| **75** | `BL-03` | `[RBAC] API Đăng nhập, Đăng xuất & Quản lý thông tin tài khoản` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `api`, `auth` | S |
| **76** | `BL-04` | `[RBAC] Giao diện phê duyệt câu hỏi dành riêng cho Tổ trưởng chuyên môn` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `frontend`, `approval`, `ui` | S |
| **77** | `BL-05` | `[CLOUD-AI] Adapter tích hợp Cloud Multimodal LLM (Gemini 1.5 / Claude)` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `ai`, `cloud` | S |
| **78** | `BL-06` | `[OCR] Adapter tích hợp DocTR/TrOCR mã nguồn mở cho chữ viết tay` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `ocr`, `doctr` | S |
| **79** | `BL-07` | `[CBT] CSDL & REST API Quản lý Ca thi trực tuyến (CBT Session)` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `model`, `cbt` | S |
| **80** | `BL-08` | `[CBT] Giao diện Học sinh làm bài thi trực tuyến với đồng hồ đếm ngược` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `frontend`, `cbt`, `student` | M |
| **81** | `BL-09` | `[CBT] WebSocket đồng bộ câu trả lời học sinh mỗi 15 giây` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `websocket`, `cbt` | S |
| **82** | `BL-10` | `[CBT] Module ghi nhận vi phạm thi cử (chuyển tab trình duyệt)` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `frontend`, `anti-cheat`, `cbt` | S |
| **83** | `BL-11` | `[OMR] Thuật toán OpenCV căn chỉnh 4 điểm mốc định vị phiếu thi 2025` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `opencv`, `omr` | S |
| **84** | `BL-12` | `[OMR] Thuật toán nhận diện điểm tô đen bút chì 2B trên phiếu OMR` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `opencv`, `grading` | S |
| **85** | `BL-13` | `[OMR] API nhận ảnh phiếu trắc nghiệm và trả về điểm số tự động` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `backend`, `api`, `omr` | S |
| **86** | `BL-14` | `[DEVOPS] Viết Multi-stage Dockerfile cho ứng dụng Quesy` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `devops`, `docker`, `container` | S |
| **87** | `BL-15` | `[DEVOPS] Viết file docker-compose.yml tích hợp Postgres & Redis` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `devops`, `docker-compose`, `postgres` | S |
| **88** | `BL-16` | `[DEVOPS] Thiết lập pipeline GitHub Actions CI tự động chạy kiểm thử` | **Todo [ ]** | `Phase 7: Enterprise Roadmap` | `devops`, `github-actions`, `ci` | XS |

---

## III. SCRIPT SHELL BATCH TẠO ISSUES QUA GITHUB CLI (`gh`)

Để tự động nhập toàn bộ các công việc vi mô này vào GitHub Projects, bạn chỉ cần mở terminal và chạy:

```bash
# 1. Tạo các Milestone cho 7 Phase
gh milestone create --title "Phase 1: Taxonomy TT32" --description "CSDL & Cây kiến thức 6 tầng chuẩn TT 32"
gh milestone create --title "Phase 2: Item Bank & Dedup" --description "Ngân hàng câu hỏi 5 thể thức & Chống trùng lặp"
gh milestone create --title "Phase 3: AI Digitize & HITL" --description "Pipeline số hóa & Studio hậu kiểm đối chiếu song song"
gh milestone create --title "Phase 4: Matrix & Assembly" --description "Ma trận đề thi & Động cơ sinh đề gốc có trọng số"
gh milestone create --title "Phase 5: Shuffling & Psychometrics" --description "Động cơ trộn đề 4 nguyên tắc & Trắc lượng học CTT"
gh milestone create --title "Phase 6: Publishing & Operations" --description "Xuất bản in ấn đa định dạng Word/PDF & Vận hành"
gh milestone create --title "Phase 7: Enterprise Roadmap" --description "Multi-tenant RBAC, Online CBT, OMR & CI/CD"

# 2. Tạo nhanh các Issue cốt lõi đã hoàn thành (Done)
gh issue create --title "[TS-01] Định nghĩa ORM Model Grade & Subject" --milestone "Phase 1: Taxonomy TT32" --label "backend,model,tt32" --body "Đã hoàn thành trong backend/models.py."
gh issue create --title "[TS-02] Định nghĩa ORM Model ContentStrand & Topic" --milestone "Phase 1: Taxonomy TT32" --label "backend,model,tt32" --body "Đã hoàn thành trong backend/models.py."
gh issue create --title "[TS-03] Định nghĩa ORM Model Lesson & LearningOutcome" --milestone "Phase 1: Taxonomy TT32" --label "backend,model,yccd" --body "Đã hoàn thành trong backend/models.py."
gh issue create --title "[TS-04] Định nghĩa ORM Model ProblemArchetype" --milestone "Phase 1: Taxonomy TT32" --label "backend,model,archetype" --body "Đã hoàn thành trong backend/models.py."
gh issue create --title "[TS-06] API Endpoint GET /api/v1/taxonomy/tree" --milestone "Phase 1: Taxonomy TT32" --label "backend,api,taxonomy" --body "Đã hoàn thành trong backend/routers/taxonomy.py."
gh issue create --title "[IB-05] API POST /api/v1/questions tạo mới câu hỏi" --milestone "Phase 2: Item Bank & Dedup" --label "backend,api,crud" --body "Đã hoàn thành trong backend/routers/questions.py."
gh issue create --title "[DD-02] Logic cảnh báo trùng 80% & chặn lưu 90%" --milestone "Phase 2: Item Bank & Dedup" --label "backend,algorithm,dedup" --body "Đã hoàn thành trong backend/services/ai_parser.py."
gh issue create --title "[AI-03] Engine bóc tách Word DOCX & MathType sang LaTeX" --milestone "Phase 3: AI Digitize & HITL" --label "backend,docx,mathtype" --body "Đã hoàn thành trong backend/services/ai_parser.py."
gh issue create --title "[UI-03] Cơ chế cuộn đồng bộ Synchronized Scrolling" --milestone "Phase 3: AI Digitize & HITL" --label "frontend,interaction,scroll" --body "Đã hoàn thành trong frontend/static/app.js."
gh issue create --title "[SH-03] Thực thi RULE-02: Option Anchor Rule khóa vào D" --milestone "Phase 5: Shuffling & Psychometrics" --label "backend,algorithm,rule02" --body "Đã hoàn thành trong backend/services/shuffling_engine.py."
gh issue create --title "[EX-04] Động cơ sinh PDF vector siêu tốc ReportLab (<100ms)" --milestone "Phase 6: Publishing & Operations" --label "backend,reportlab,pdf" --body "Đã hoàn thành trong backend/services/docx_exporter.py."
gh issue create --title "[EX-11] Cơ chế tải Blob Client-side dập tắt lỗi tải file" --milestone "Phase 6: Publishing & Operations" --label "frontend,blob,download" --body "Đã hoàn thành trong frontend/static/app.js."
gh issue create --title "[SO-04] Bộ test suite tự động 39 test cases (100% Passed)" --milestone "Phase 6: Publishing & Operations" --label "testing,pytest,e2e" --body "Đã hoàn thành trong thư mục tests/."
```
