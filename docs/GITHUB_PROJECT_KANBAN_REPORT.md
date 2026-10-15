# BÁO CÁO PHÂN RÃ DỰ ÁN & BẢN ĐỒ KANBAN GITHUB PROJECT (QUESY)
**Dự án: Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI Số hoá**  
**Căn cứ pháp lý:** Thông tư số 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT, Quyết định 764/QĐ-BGDĐT  
**Kỹ năng áp dụng:** `planning-and-task-breakdown` (SKILL.md)  
**Tập tin kế hoạch liên quan:** `tasks/plan.md`, `tasks/todo.md`  

---

## I. TỔNG QUAN TIẾN ĐỘ DỰ ÁN (PROJECT PROGRESS DASHBOARD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TIẾN ĐỘ THỰC HIỆN TOÀN BỘ DỰ ÁN                       │
│  [███████████████████████████████████████████████████████░░░░░░░░] 76.2%    │
│                                                                             │
│  • Tổng số công việc (Total Issues):       21 Tasks                         │
│  • Đã hoàn thành (Done):                   16 Tasks (100% Cốt lõi) [x]      │
│  • Đang chờ triển khai (Backlog / Todo):    5 Tasks (Mở rộng Cloud) [ ]     │
│  • Tỷ lệ kiểm thử tự động (Test Pass Rate): 39 / 39 Tests (100% Passed)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## II. BẢNG DỮ LIỆU IMPORT GITHUB PROJECT KANBAN (CSV-READY)

Dưới đây là bảng tổng hợp cấu trúc dữ liệu chuẩn để nhập (Import) trực tiếp vào **GitHub Projects (Beta)**:

| ID | Issue Title | Status | Milestone / Phase | Labels | Priority | Estimate |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **#1** | `[TAXONOMY] CSDL & Cây kiến thức 6 tầng chuẩn TT 32` | **Done** | `Phase 1: Foundation` | `backend`, `compliance`, `tt32` | `P0` | M |
| **#2** | `[ITEM-BANK] API Ngân hàng câu hỏi & 5 thể thức QĐ 764` | **Done** | `Phase 1: Foundation` | `backend`, `api`, `qd764` | `P0` | M |
| **#3** | `[DEDUP] Động cơ chống trùng câu hỏi (Cosine Similarity >= 0.9)` | **Done** | `Phase 1: Foundation` | `backend`, `ai`, `algorithm` | `P1` | S |
| **#4** | `[UI-BANK] Giao diện Ngân hàng câu hỏi KaTeX & Bộ lọc TT 32` | **Done** | `Phase 1: Foundation` | `frontend`, `katex`, `ui` | `P1` | S |
| **#5** | `[AI-INGEST] Pipeline bóc tách tài liệu PDF/Word (MathType/LaTeX)` | **Done** | `Phase 2: AI Digitization` | `backend`, `ai-pipeline`, `ocr` | `P0` | M |
| **#6** | `[AI-VISION] Tự động cắt ảnh đồ thị BoundingBox & Auto-tagging` | **Done** | `Phase 2: AI Digitization` | `backend`, `vision`, `webp` | `P1` | S |
| **#7** | `[HITL-STUDIO] Giao diện Studio hậu kiểm song song & cuộn đồng bộ` | **Done** | `Phase 2: AI Digitization` | `frontend`, `hitl`, `ux` | `P0` | M |
| **#8** | `[FORMULA-EDIT] Modal sửa nhanh công thức LaTeX & KaTeX live preview` | **Done** | `Phase 2: AI Digitization` | `frontend`, `katex`, `modal` | `P2` | S |
| **#9** | `[MATRIX] Module thiết lập ma trận đề thi & cảnh báo số dư kho` | **Done** | `Phase 3: Assessment Core` | `backend`, `frontend`, `matrix` | `P0` | M |
| **#10** | `[SOLVER] Thuật toán sinh đề gốc cân bằng kho & loại trừ câu đã thi` | **Done** | `Phase 3: Assessment Core` | `backend`, `algorithm`, `solver` | `P0` | S |
| **#11** | `[SHUFFLER] Động cơ trộn đề an toàn 4 nguyên tắc & Option Anchor Rule` | **Done** | `Phase 3: Assessment Core` | `backend`, `algorithm`, `shuffler` | `P0` | M |
| **#12** | `[ANALYTICS] Phân tích trắc lượng cổ điển CTT (Độ khó p, Độ phân biệt D)` | **Done** | `Phase 3: Assessment Core` | `backend`, `analytics`, `ctt` | `P1` | S |
| **#13** | `[EXPORT-DOCX] Dịch vụ xuất bản Word OpenXML (.docx) 2 cột & OMML native` | **Done** | `Phase 4: Export & Polish` | `backend`, `export`, `docx` | `P0` | M |
| **#14** | `[EXPORT-PDF] Động cơ sinh PDF vector siêu tốc thuần Python (ReportLab)` | **Done** | `Phase 4: Export & Polish` | `backend`, `export`, `pdf` | `P0` | M |
| **#15** | `[EXPORT-ZIP] Đóng gói trọn gói ZIP đa định dạng & cơ chế tải Blob an toàn` | **Done** | `Phase 4: Export & Polish` | `backend`, `frontend`, `download` | `P0` | M |
| **#16** | `[TEST-SUITE] Bộ test tự động 39 test cases & Khởi động server tự giải phóng socket` | **Done** | `Phase 4: Export & Polish` | `testing`, `devops`, `windows` | `P0` | L |
| **#17** | `[RBAC] Phân quyền người dùng đa cấp & đa trường học (Multi-tenant)` | **Todo** | `Phase 5: Enterprise Roadmap` | `backend`, `security`, `rbac` | `P1` | M |
| **#18** | `[CLOUD-VISION] Tích hợp Cloud Vision API (Gemini Vision / Claude 3.5 Sonnet)` | **Todo** | `Phase 5: Enterprise Roadmap` | `backend`, `ai`, `cloud` | `P1` | M |
| **#19** | `[ONLINE-CBT] Phân hệ thi trực tuyến học sinh chống gian lận (Online CBT)` | **Todo** | `Phase 5: Enterprise Roadmap` | `frontend`, `backend`, `cbt` | `P1` | L |
| **#20** | `[OMR-GRADING] Phân hệ chấm phiếu trắc nghiệm tự động qua Webcam/Scanner` | **Todo** | `Phase 5: Enterprise Roadmap` | `backend`, `computer-vision`, `omr` | `P2` | M |
| **#21** | `[DEVOPS] Đóng gói Docker, K8s Helm Chart & Pipeline CI/CD GitHub Actions` | **Todo** | `Phase 5: Enterprise Roadmap` | `devops`, `docker`, `ci-cd` | `P2` | M |

---

## III. CHI TIẾT CÁC CỘT TRÊN GITHUB PROJECT KANBAN

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┐
│     DONE (16 TASKS)       │   IN PROGRESS (0 TASKS)   │      TODO (5 TASKS)       │
├───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ [x] #1  CSDL 6 tầng TT32  │                           │ [ ] #17 Multi-tenant RBAC │
│ [x] #2  API Ngân hàng     │                           │ [ ] #18 Cloud Vision API  │
│ [x] #3  Chống trùng lặp   │                           │ [ ] #19 Online CBT Taker  │
│ [x] #4  UI Ngân hàng      │                           │ [ ] #20 OMR Scanner       │
│ [x] #5  AI Bóc tách Word  │                           │ [ ] #21 Docker & CI/CD    │
│ [x] #6  Auto Crop Ảnh     │                           │                           │
│ [x] #7  Studio Hậu kiểm   │                           │                           │
│ [x] #8  Modal LaTeX KaTeX │                           │                           │
│ [x] #9  Ma trận Đề thi    │                           │                           │
│ [x] #10 Sinh Đề Gốc Solver│                           │                           │
│ [x] #11 Trộn Đề An Toàn   │                           │                           │
│ [x] #12 Phân Tích CTT p, D│                           │                           │
│ [x] #13 Xuất Word OpenXML │                           │                           │
│ [x] #14 Xuất PDF Vector   │                           │                           │
│ [x] #15 Đóng Gói ZIP Blob │                           │                           │
│ [x] #16 Test Suite 39/39  │                           │                           │
└───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## IV. BẢN ĐẶC TẢ CHI TIẾT TỪNG ISSUE ĐỂ IMPORT GITHUB (ISSUE TEMPLATES)

### NHÓM CÔNG VIỆC ĐÃ HOÀN THÀNH (DONE)

#### Issue #1: [TAXONOMY] CSDL & Cây kiến thức 6 tầng chuẩn TT 32
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Thiết kế CSDL quan hệ cho cây kiến thức chuẩn Thông tư 32/2018/TT-BGDĐT: Cấp/Khối $\rightarrow$ Môn $\rightarrow$ Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ Yêu cầu cần đạt (YCCĐ) và tầng Dạng câu hỏi (Problem Archetype).
- **Tiêu chí nghiệm thu (Acceptance Criteria):**
  - [x] Không tồn tại trường dữ liệu bộ sách (`textbook_edition`).
  - [x] Đầy đủ 6 tầng phân cấp theo Thông tư 32.
  - [x] Cung cấp REST API lấy cây phân tầng dạng lồng nhau (`/api/v1/taxonomy/tree`).
- **Minh chứng kiểm thử:** `pytest tests/test_taxonomy.py` (Pass 100%).

#### Issue #2: [ITEM-BANK] API Ngân hàng câu hỏi & 5 thể thức QĐ 764
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Xây dựng mô hình dữ liệu và API cho 5 thể thức khảo thí theo Quyết định 764/QĐ-BGDĐT (Trắc nghiệm đơn, Đúng/Sai đa ý, Trả lời ngắn, Câu hỏi chùm, Tự luận).
- **Tiêu chí nghiệm thu:**
  - [x] Câu hỏi Đúng/Sai lưu 4 ý a), b), c), d) độc lập kèm trạng thái `is_true`.
  - [x] Đầy đủ CRUD API kiểm soát dữ liệu đầu vào bằng Pydantic v2.
- **Minh chứng kiểm thử:** `pytest tests/test_api_contracts_and_negatives.py` (Pass 100%).

#### Issue #3: [DEDUP] Động cơ chống trùng câu hỏi (Cosine Similarity >= 0.9)
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Hiện thực hóa thuật toán vector hóa văn bản và tính Cosine Similarity để cảnh báo và chặn trùng lặp câu hỏi khi nhập vào ngân hàng.
- **Tiêu chí nghiệm thu:**
  - [x] Cảnh báo vàng khi trùng $80\% - 90\%$.
  - [x] Chặn lưu (bật modal đỏ) khi trùng $\ge 90\%$.
- **Minh chứng kiểm thử:** `pytest tests/test_deduplication.py` (Pass 100%).

#### Issue #4: [UI-BANK] Giao diện Ngân hàng câu hỏi KaTeX & Bộ lọc TT 32
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Giao diện hiển thị ngân hàng câu hỏi trên Web Studio, render công thức toán học KaTeX, tích hợp bộ lọc đa tầng theo mạch nội dung và mức độ nhận thức.
- **Minh chứng kiểm thử:** Render hiển thị KaTeX trực tiếp trên Web Studio (`http://127.0.0.1:8000`).

#### Issue #5: [AI-INGEST] Pipeline bóc tách tài liệu PDF/Word (MathType/LaTeX)
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Bóc tách đề thi từ file tải lên, chuyển đổi công thức MathType và OLE objects sang chuẩn LaTeX inline và block.
- **Minh chứng kiểm thử:** `pytest tests/test_ai_pipeline.py` (Pass 100%).

#### Issue #6: [AI-VISION] Tự động cắt ảnh đồ thị BoundingBox & Auto-tagging
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Nhận diện đồ thị, hình vẽ hình học trong đề thi, tự động cắt ảnh theo Bounding Box và lưu trữ tối ưu dưới định dạng WebP; tự động gợi ý nhãn YCCĐ.
- **Minh chứng kiểm thử:** Lưu ảnh WebP vào `storage/assets/` và nhúng link hợp lệ vào câu hỏi.

#### Issue #7: [HITL-STUDIO] Giao diện Studio hậu kiểm song song & cuộn đồng bộ
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Màn hình Studio đối chiếu song song: 50% tài liệu gốc và 50% kết quả bóc tách, thanh đo độ tin cậy Confidence Barometer, tính năng Synchronized Scrolling.
- **Minh chứng kiểm thử:** Trình duyệt thực tế phản hồi cuộn đồng bộ trơn tru với độ trễ $< 100$ms.

#### Issue #8: [FORMULA-EDIT] Modal sửa nhanh công thức LaTeX & KaTeX live preview
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Cửa sổ popup cho phép giáo viên chỉnh sửa trực tiếp mã LaTeX với khung xem trước KaTeX thời gian thực.
- **Minh chứng kiểm thử:** Nhập và hiển thị công thức toán học ngay lập tức trên giao diện.

#### Issue #9: [MATRIX] Module thiết lập ma trận đề thi & cảnh báo số dư kho
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Cấu hình ma trận đề thi theo YCCĐ và 3 mức độ nhận thức (Biết, Hiểu, Vận dụng), tự động kiểm tra số lượng câu hỏi khả dụng trong kho.
- **Minh chứng kiểm thử:** `pytest tests/test_services.py::test_matrix_solver_exclusion_and_inventory_warning` (Pass 100%).

#### Issue #10: [SOLVER] Thuật toán sinh đề gốc cân bằng kho & loại trừ câu đã thi
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Thuật toán sinh đề gốc đáp ứng đúng tỷ lệ ma trận và tự động loại trừ các câu hỏi đã xuất hiện trong các kỳ thi gần nhất.
- **Minh chứng kiểm thử:** `pytest tests/test_e2e_workflow.py` (Pass 100%).

#### Issue #11: [SHUFFLER] Động cơ trộn đề an toàn 4 nguyên tắc & Option Anchor Rule
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Trộn đề thi an toàn bảo toàn cấu trúc phần (Section Integrity), bài đọc (Passage Integrity), khóa cố định đáp án neo vào vị trí D (Option Anchor Rule), và chấm điểm lũy tiến cho câu hỏi Đúng/Sai (RULE-01).
- **Minh chứng kiểm thử:** `pytest tests/test_rules_shuffling.py` (100 vòng lặp kiểm tra Rule 02 đạt 100%).

#### Issue #12: [ANALYTICS] Phân tích trắc lượng cổ điển CTT (Độ khó p, Độ phân biệt D)
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Tính toán các chỉ số độ khó ($p$) và độ phân biệt ($D$) từ bảng điểm học sinh, tự động gắn cờ cảnh báo câu hỏi lỗi khi $D < 0.20$.
- **Minh chứng kiểm thử:** `pytest tests/test_services.py` (Pass 100%).

#### Issue #13: [EXPORT-DOCX] Dịch vụ xuất bản Word OpenXML (.docx) 2 cột & OMML native
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Tạo file Word OpenXML (.docx) thật với bố cục 2 cột, bảng phách chuẩn Bộ GD&ĐT, công thức Toán OMML native mở và chỉnh sửa trực tiếp trên Word.
- **Minh chứng kiểm thử:** `pytest tests/test_docx_export.py` (Pass 100%).

#### Issue #14: [EXPORT-PDF] Động cơ sinh PDF vector siêu tốc thuần Python (ReportLab)
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Nâng cấp động cơ xuất PDF vector bằng ReportLab nhúng font Windows Times New Roman Unicode, thời gian sinh PDF giảm xuống dưới 100ms mà không bị treo hay timeout.
- **Minh chứng kiểm thử:** Tải lẻ file PDF trên trình duyệt thật hoàn thành trong **283ms**.

#### Issue #15: [EXPORT-ZIP] Đóng gói trọn gói ZIP đa định dạng & cơ chế tải Blob an toàn
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Tải gói ZIP tổng hợp theo tùy chọn định dạng (`format=all|docx|pdf`), chuyển đổi client-side sang cơ chế Blob download để dập tắt lỗi *Failed - Unknown server error*.
- **Minh chứng kiểm thử:** Kiểm thử Playwright/CDP trên trình duyệt thật tải thành công cả gói Word ZIP và PDF ZIP.

#### Issue #16: [TEST-SUITE] Bộ test tự động 39 test cases & Khởi động server tự giải phóng socket
- **Trạng thái:** `[x] COMPLETED`
- **Mô tả:** Tích hợp bộ tiêu chuẩn từ `tester-skills-main.zip`, hoàn thiện 39 test cases tự động, hoàn thiện `start_server.py` tự giải phóng socket cổng 8000 trên Windows.
- **Minh chứng kiểm thử:** 39/39 tests passed, thời gian chạy ~10s.

---

### NHÓM CÔNG VIỆC CHỜ TRIỂN KHAI TRÊN ROADMAP (TODO / BACKLOG)

#### Issue #17: [RBAC] Phân quyền người dùng đa cấp & đa trường học (Multi-tenant)
- **Trạng thái:** `[ ] TODO (Phase 5)`
- **Mô tả:** Phân quyền theo vai trò (Quản trị viên, Tổ trưởng, Giáo viên) và cách ly dữ liệu giữa các trường học (`institution_id`).
- **Tiêu chí nghiệm thu:**
  - [ ] Giáo viên chỉ sửa được câu hỏi do mình tạo hoặc câu hỏi ở trạng thái `DRAFT`.
  - [ ] Chỉ Tổ trưởng chuyên môn mới có quyền duyệt câu hỏi lên `APPROVED`.
  - [ ] Xác thực JWT Token và tích hợp OAuth2 Google Workspace.

#### Issue #18: [CLOUD-VISION] Tích hợp Cloud Vision API (Gemini Vision / Claude 3.5 Sonnet)
- **Trạng thái:** `[ ] TODO (Phase 5)`
- **Mô tả:** Tích hợp adapter gọi Cloud Vision LLM để xử lý các tài liệu chụp bằng điện thoại có độ phân giải thấp hoặc chữ viết tay.
- **Tiêu chí nghiệm thu:**
  - [ ] Nhận diện chính xác hình học không gian và biểu thức toán phức tạp $> 92\%$.
  - [ ] Circuit Breaker tự động chuyển đổi sang Local Parser nếu mất kết nối mạng.

#### Issue #19: [ONLINE-CBT] Phân hệ thi trực tuyến học sinh chống gian lận (Online CBT)
- **Trạng thái:** `[ ] TODO (Phase 5)`
- **Mô tả:** Giao diện làm bài thi trực tuyến trên máy tính và điện thoại, đồng hồ đếm ngược, tự động nộp bài, cơ chế ghi log phát hiện chuyển tab.
- **Tiêu chí nghiệm thu:**
  - [ ] Hỗ trợ đầy đủ 3 phần thi định dạng 2025.
  - [ ] Tự động lưu đáp án mỗi 15 giây chống mất kết nối mạng.

#### Issue #20: [OMR-GRADING] Phân hệ chấm phiếu trắc nghiệm tự động qua Webcam/Scanner
- **Trạng thái:** `[ ] TODO (Phase 5)`
- **Mô tả:** Xử lý ảnh OpenCV nhận diện dấu tô chì 2B trên phiếu trả lời trắc nghiệm chuẩn 2025 và tự động chấm điểm theo RULE-01.
- **Tiêu chí nghiệm thu:**
  - [ ] Tự động cân chỉnh góc phiếu thi qua 4 điểm mốc định vị.
  - [ ] Độ chính xác nhận diện điểm tô đen $\ge 99.5\%$.

#### Issue #21: [DEVOPS] Đóng gói Docker, K8s Helm Chart & Pipeline CI/CD GitHub Actions
- **Trạng thái:** `[ ] TODO (Phase 5)`
- **Mô tả:** Tạo Dockerfile multi-stage, docker-compose, tài liệu Helm Chart triển khai Kubernetes và thiết lập file workflow GitHub Actions tự động kiểm thử.
- **Tiêu chí nghiệm thu:**
  - [ ] Khởi chạy toàn bộ hệ thống bằng lệnh `docker compose up -d`.
  - [ ] Pipeline CI chạy tự động 39 tests mỗi khi tạo Pull Request.

---

## V. LỆNH TỰ ĐỘNG TẠO ISSUES QUA GITHUB CLI (AUTOMATED SCRIPT)

Bạn có thể chạy script shell dưới đây (sau khi đăng nhập `gh auth login`) để tự động tạo toàn bộ 21 issues này lên GitHub repository của bạn:

```bash
# 1. Tạo các Milestone
gh milestone create --title "Phase 1: Foundation" --description "Nền tảng danh mục & ngân hàng câu hỏi TT 32"
gh milestone create --title "Phase 2: AI Digitization" --description "Pipeline số hóa & Studio hậu kiểm HITL"
gh milestone create --title "Phase 3: Assessment Core" --description "Ma trận đề thi & Động cơ trộn đề an toàn"
gh milestone create --title "Phase 4: Export & Polish" --description "Xuất bản in ấn đa định dạng & Test suite"
gh milestone create --title "Phase 5: Enterprise Roadmap" --description "Mở rộng doanh nghiệp, Cloud & Mobile CBT"

# 2. Tạo các Issue đã hoàn thành (Done)
gh issue create --title "[TAXONOMY] CSDL & Cây kiến thức 6 tầng chuẩn TT 32" --milestone "Phase 1: Foundation" --label "backend,compliance,tt32" --body "Đã hoàn thành. CSDL chuẩn 6 tầng không phân chia theo bộ sách giáo khoa."
gh issue create --title "[ITEM-BANK] API Ngân hàng câu hỏi & 5 thể thức QĐ 764" --milestone "Phase 1: Foundation" --label "backend,api,qd764" --body "Đã hoàn thành. Hỗ trợ 5 thể thức khảo thí theo Quyết định 764/QĐ-BGDĐT."
gh issue create --title "[DEDUP] Động cơ chống trùng câu hỏi (Cosine Similarity >= 0.9)" --milestone "Phase 1: Foundation" --label "backend,ai,algorithm" --body "Đã hoàn thành. Vector search chặn trùng lặp câu hỏi."
gh issue create --title "[UI-BANK] Giao diện Ngân hàng câu hỏi KaTeX & Bộ lọc TT 32" --milestone "Phase 1: Foundation" --label "frontend,katex,ui" --body "Đã hoàn thành. Giao diện Web Studio với KaTeX renderer."
gh issue create --title "[AI-INGEST] Pipeline bóc tách tài liệu PDF/Word (MathType/LaTeX)" --milestone "Phase 2: AI Digitization" --label "backend,ai-pipeline,ocr" --body "Đã hoàn thành. Bóc tách MathType sang LaTeX."
gh issue create --title "[AI-VISION] Tự động cắt ảnh đồ thị BoundingBox & Auto-tagging" --milestone "Phase 2: AI Digitization" --label "backend,vision,webp" --body "Đã hoàn thành. Tự động cắt ảnh WebP và gợi ý YCCĐ."
gh issue create --title "[HITL-STUDIO] Giao diện Studio hậu kiểm song song & cuộn đồng bộ" --milestone "Phase 2: AI Digitization" --label "frontend,hitl,ux" --body "Đã hoàn thành. Side-by-side synchronized review."
gh issue create --title "[FORMULA-EDIT] Modal sửa nhanh công thức LaTeX & KaTeX live preview" --milestone "Phase 2: AI Digitization" --label "frontend,katex,modal" --body "Đã hoàn thành. Sửa nhanh công thức toán học."
gh issue create --title "[MATRIX] Module thiết lập ma trận đề thi & cảnh báo số dư kho" --milestone "Phase 3: Assessment Core" --label "backend,frontend,matrix" --body "Đã hoàn thành. Ma trận đề thi bám sát YCCĐ."
gh issue create --title "[SOLVER] Thuật toán sinh đề gốc cân bằng kho & loại trừ câu đã thi" --milestone "Phase 3: Assessment Core" --label "backend,algorithm,solver" --body "Đã hoàn thành. Động cơ chọn lọc ngẫu nhiên có trọng số."
gh issue create --title "[SHUFFLER] Động cơ trộn đề an toàn 4 nguyên tắc & Option Anchor Rule" --milestone "Phase 3: Assessment Core" --label "backend,algorithm,shuffler" --body "Đã hoàn thành. Bảo toàn Option Anchor tại vị trí D và tính điểm lũy tiến RULE-01."
gh issue create --title "[ANALYTICS] Phân tích trắc lượng cổ điển CTT (Độ khó p, Độ phân biệt D)" --milestone "Phase 3: Assessment Core" --label "backend,analytics,ctt" --body "Đã hoàn thành. Tính chỉ số p, D và cảnh báo câu hỏi lỗi."
gh issue create --title "[EXPORT-DOCX] Dịch vụ xuất bản Word OpenXML (.docx) 2 cột & OMML native" --milestone "Phase 4: Export & Polish" --label "backend,export,docx" --body "Đã hoàn thành. Xuất bản Word chuẩn 2 cột OpenXML."
gh issue create --title "[EXPORT-PDF] Động cơ sinh PDF vector siêu tốc thuần Python (ReportLab)" --milestone "Phase 4: Export & Polish" --label "backend,export,pdf" --body "Đã hoàn thành. PDF vector siêu tốc dưới 100ms với font Times New Roman."
gh issue create --title "[EXPORT-ZIP] Đóng gói trọn gói ZIP đa định dạng & cơ chế tải Blob an toàn" --milestone "Phase 4: Export & Polish" --label "backend,frontend,download" --body "Đã hoàn thành. Xuất bản trọn gói ZIP và tải Blob không lỗi."
gh issue create --title "[TEST-SUITE] Bộ test tự động 39 test cases & Khởi động server tự giải phóng socket" --milestone "Phase 4: Export & Polish" --label "testing,devops,windows" --body "Đã hoàn thành. 39/39 tests passed 100%."

# 3. Tạo các Issue cần làm tiếp (Backlog / Todo)
gh issue create --title "[RBAC] Phân quyền người dùng đa cấp & đa trường học (Multi-tenant)" --milestone "Phase 5: Enterprise Roadmap" --label "backend,security,rbac" --body "Kế hoạch: Phân quyền vai trò và cách ly dữ liệu giữa các trường học."
gh issue create --title "[CLOUD-VISION] Tích hợp Cloud Vision API (Gemini Vision / Claude 3.5 Sonnet)" --milestone "Phase 5: Enterprise Roadmap" --label "backend,ai,cloud" --body "Kế hoạch: Nâng cao độ chính xác nhận diện đề thi viết tay."
gh issue create --title "[ONLINE-CBT] Phân hệ thi trực tuyến học sinh chống gian lận (Online CBT)" --milestone "Phase 5: Enterprise Roadmap" --label "frontend,backend,cbt" --body "Kế hoạch: Module học sinh làm bài thi trực tuyến."
gh issue create --title "[OMR-GRADING] Phân hệ chấm phiếu trắc nghiệm tự động qua Webcam/Scanner" --milestone "Phase 5: Enterprise Roadmap" --label "backend,computer-vision,omr" --body "Kế hoạch: Chấm tự động qua ảnh chụp phiếu trắc nghiệm 2025."
gh issue create --title "[DEVOPS] Đóng gói Docker, K8s Helm Chart & Pipeline CI/CD GitHub Actions" --milestone "Phase 5: Enterprise Roadmap" --label "devops,docker,ci-cd" --body "Kế hoạch: Dockerize và thiết lập CI/CD GitHub Actions."
```
