# TÀI LIỆU YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS SPECIFICATION - SRS)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-SRS-01  
- **Phiên bản:** 3.5 (Render KaTeX Toàn Diện Tại Ngân Hàng, Ma Trận Đề & Modals, Chuẩn Hóa Dropdown Box Apple HIG Unified Select .apple-select, Triệt Tiêu Lỗi Font Monospace & Khắc Phục Lỗi Hiển Thị Toán Học)  
- **Tiêu chuẩn kỹ thuật áp dụng:** IEEE Std 830-1998 / ISO/IEC/IEEE 29148  
- **Nhiệm vụ trọng tâm:** Đặc tả hệ thống số hóa đề thi tự động, hệ thống xác thực người dùng an toàn (PBKDF2/SHA256, JWT HS256, Google/GitHub OAuth, RBAC), phân hệ Ngân hàng câu hỏi hoàn thiện toàn diện (CRUD, xem chi tiết, sửa, xóa cascade, lọc 6 tầng TT 32, xuất PDF/CSV/LaTeX, nhập đề, kiểm tra trùng lặp AI >= 90%, badge counter sync), phân hệ Soạn đề tinh gọn tích hợp nút chuyên biệt "LƯU VÀO NGÂN HÀNG", phân hệ Ma trận đề thi 2D tương tác theo Thông tư 22/2021/TT-BGDĐT và Định dạng đề thi 2025 (Quyết định 764/QĐ-BGDĐT) với thư viện 3 Presets mẫu, đối soát tồn kho thời gian thực và xuất bản bản đặc tả (PDF/CSV/JSON), phân hệ Sinh & Trộn đề thi an toàn 4 nguyên tắc (Section Integrity, Passage Integrity, Option Anchor Rule 100%, Key Matrix), động cơ đổi câu hỏi đề gốc tương đương (In-Place Item Swap), đóng gói trọn bộ ấn phẩm khảo thí (.ZIP/.PDF), cơ chế biên dịch KaTeX toàn diện tại mọi điểm hiển thị toán học (Ngân hàng, Ma trận, Modals, Đề gốc, Đề hoán vị), và chuẩn hóa giao diện dropdown box Apple HIG (.apple-select) đồng bộ 100% typography sans-serif.
- **Ngày phát hành:** 2026-10-27  
- **Trạng thái:** Sẵn sàng triển khai & Vận hành sản xuất (Production Ready)

---

## 1. GIỚI THIỆU (INTRODUCTION)

### 1.1. Mục đích Tài liệu (Purpose)
Tài liệu này đặc tả chi tiết toàn bộ các yêu cầu kỹ thuật, kiến trúc hệ thống và hành vi dữ liệu cho nền tảng **Quesy**. Tài liệu đóng vai trò là cam kết kỹ thuật giữa Đội ngũ Phân tích Nghiệp vụ (BA), Kiến trúc sư Giải pháp (Solution Architect), Kỹ sư Phát triển (Devs) và Kỹ sư Đảm bảo Chất lượng (QA/QC).

### 1.2. Quy ước Tài liệu (Conventions)
- **BẮT BUỘC (SHALL / MUST):** Yêu cầu kỹ thuật tiên quyết phải đáp ứng (Priority P0).
- **NÊN CÓ (SHOULD):** Yêu cầu quan trọng cần có trong giai đoạn hiện tại (Priority P1).
- **CÓ THỂ (MAY):** Tính năng mở rộng nâng cao (Priority P2).
- Mọi công thức Toán/Khoa học được lưu trữ và truyền nhận dưới dạng chuỗi **LaTeX chuẩn**; render trên giao diện bằng **KaTeX**; xuất bản sang Word bằng **MathType 7.0 OLE Vector WMF** (hỗ trợ double-click edit), mã **OMML native**, hoặc **LaTeX raw**; đồ thị và hình học được biên dịch sang **Vector SVG** sắc nét.

### 1.3. Khách thể Sử dụng (Audience)
- **Product Owner & Quản trị Dự án:** Đánh giá phạm vi hệ thống.

### 1.4. Quy tắc Quản trị Git Workflow, Cổng Pre-Commit CI Gate & Cô Lập CI/CD (Mandatory CI/CD & Git Rules)
- **Cổng Pre-Commit CI Gate bắt buộc:** Trước khi thực hiện `git commit`, mã nguồn bắt buộc phải vượt qua toàn diện bài kiểm thử CI trên runner (100% test cases đạt). Tuyệt đối cấm commit mã nguồn khi CI test chưa đạt.
- **Vòng lặp sửa lỗi CI (CI Fix-and-Test Loop):** Nếu CI test không pass:
  `CI thất bại` → `Sửa lỗi code / Cập nhật test & cấu hình CI` → `Chạy lại test CI` → `Lặp lại quy trình` cho đến khi **PASS 100% CI MỚI ĐƯỢC PHÉP COMMIT**.
- **Đồng bộ CI liên tục (Continuous CI Synchronization):** Mỗi khi mã nguồn có cập nhật mới (dependencies trong `requirements.txt`/`package.json`, cấu hình font, biến môi trường, headless browser...), cấu hình CI workflow phải được cập nhật đồng bộ ngay lập tức để triệt tiêu mọi nguy cơ gây lỗi trên môi trường runner.
- **Cô lập CI tuyệt đối (Strict CI Isolation & Role Separation):**
  - Sub-Agent đảm nhận làm CI (Sub-Agent 3) tách biệt hoàn toàn với tất cả các sub-agents còn lại.
  - **Mọi sub-agent khác (Sub-Agent 1, Sub-Agent 2, Sub-Agent 4...) tuyệt đối KHÔNG ĐƯỢC PHÉP truy cập và đọc CI** (`.github/workflows/`).
  - Chỉ duy nhất Sub-Agent đảm nhận làm CI mới được phép đọc, viết, chỉnh sửa cấu hình CI/CD.
  - Sub-Agent CI có toàn quyền đọc và tiếp nhận thông tin từ các sub-agents khác để phục vụ việc đồng bộ CI.
- **Quy chuẩn Git, Pull Request First & Continuous PR Description Sync:**
  - **Quy tắc tạo PR trước khi commit (PR First Rule):** Khi bắt đầu triển khai hoặc có nhánh làm việc, BẮT BUỘC phải đảm bảo có Pull Request được mở trước trên GitHub (`gh pr create`). Tuyệt đối không commit khi chưa tồn tại Pull Request.
  - **Quy tắc cập nhật mô tả PR liên tục (Continuous PR Description Sync):** Nếu đang tồn tại 1 Pull Request trước khi commit thì mỗi khi thực hiện `git commit` và `git push`, BẮT BUỘC phải cập nhật lại nội dung (description / body) của Pull Request đó (`gh pr edit <PR_NUM> --body "..."`) để phản ánh chính xác trạng thái kỹ thuật, các thay đổi mới nhất và kết quả kiểm thử.
  - Mọi tác vụ phát triển tuân thủ nghiêm ngặt chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).

### 1.5. Đối tượng Sử dụng & Phân nhiệm Kỹ thuật (Audience & Roles)
- **Product Owner & Quản trị Dự án:** Đánh giá phạm vi hệ thống.
- **Kỹ sư AI & Backend:** Xây dựng OCR pipeline, dịch vụ biên dịch TikZ SVG, MathJax Persistent Engine và thuật toán hoán vị an toàn.
- **Kỹ sư Frontend:** Phát triển giao diện Studio Hậu kiểm (HITL) cuộn đồng bộ, hiển thị đồ thị SVG và render KaTeX thời gian thực.
- **Kỹ sư QA/QC & CI/CD (Độc quyền Sub-Agent 3):** Xây dựng ma trận kiểm thử tự động, độc quyền quản trị và cập nhật cấu hình CI/CD (`.github/workflows/`), thực thi cổng Pre-Commit CI Gate bảo đảm 100% tests vượt qua.

### 1.6. Phạm vi Sản phẩm & Bài toán Giải quyết (Product Scope)
Hệ thống phần mềm dịch vụ Web ứng dụng Trí tuệ Nhân tạo Đa phương thức nhằm:
1. **Giải quyết bài toán gõ lại đề thủ công:** Tiếp nhận tài liệu đề thi thô (.docx, .doc, .pdf scan, ảnh chụp), nhận diện layout, bóc tách công thức Toán/Khoa học sang LaTeX, tự động cắt ảnh đồ thị nén WebP, bóc tách đáp án và lời giải.
2. **Giải quyết bài toán dựng đồ thị hàm số & hình học:** Tự động phát hiện mã nguồn hình học và biên dịch sang vector SVG sắc nét; có cơ chế Auto-clipping khống chế tỷ lệ khung hình hàm phân thức có tiệm cận, hỗ trợ đồ thị trong cả đề bài và 4 phương án trắc nghiệm A, B, C, D.
3. **Giải quyết bài toán vỡ logic khi trộn đề:** Động cơ Safe Shuffling Engine khóa cố định phương án phụ thuộc vị trí ("Cả A và B") ở đáp án D, bảo toàn bài đọc chung ngữ cảnh và các câu hỏi con đi liền kề nhau.
4. **Giải quyết bài toán chấm điểm phức tạp:** Tự động chấm điểm dạng câu hỏi Đúng/Sai 4 khẳng định theo thang điểm bậc thang (0.1đ - 0.25đ - 0.5đ - 1.0đ) và quản lý bảng điểm Excel UTF-8 BOM.
5. **Giải quyết bài toán dàn trang in ấn & độ nét công thức:** Xuất bản đề thi Microsoft Word (.docx) chuẩn khổ A4 Portrait với công thức **MathType 7.0 OLE Vector WMF** (nét căng, click đúp mở MathType chỉnh sửa được ngay), **OMML native**, tự động chuyển đổi bảng thống kê `\begin{array}` thành bảng Word `<w:tbl>` chống lỗi đen, xuất PDF in ấn, phiếu soi đáp án OMR và đóng gói ZIP 1-click.

---

## 2. MÔ TẢ TỔNG QUAN HỆ THỐNG (OVERALL DESCRIPTION)

### 2.1. Phối cảnh Sản phẩm (Product Perspective)
Quesy là một hệ thống SaaS/On-premise độc lập, tương tác với Object Storage (S3/MinIO), hàng đợi Redis, dịch vụ Multimodal Vision LLM và cơ sở dữ liệu quan hệ PostgreSQL tích hợp `pgvector`.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        KIẾN TRÚC TỔNG THỂ HỆ THỐNG                     │
└────────────────────────────────────────────────────────────────────────┘
  [Client Web App] ◄──HTTPS/WSS──► [API Gateway / Reverse Proxy (Nginx)]
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
         [Core Application Service]                       [AI Parsing Engine Worker]
          (Node.js/NestJS / Go / FastAPI)                  (Python, PyMuPDF, OpenCV)
                       │                                               │
         ┌─────────────┼──────────────┐                                ▼
         ▼             ▼              ▼                    [Multimodal Vision LLM]
    [PostgreSQL]    [Redis Cache]   [MinIO/S3]             (Gemini / GPT-4o / Qwen)
    (pgvector,      (Task Queue)    (Images/Docs)                      │
     JSONB)                                                            │
         ▲                                                             │
         └───────────────── Webhook / Event Stream ────────────────────┘
```

### 2.2. Phân loại Người dùng (User Classes)
- **Super Admin:** Quản trị hạ tầng, cấp phát tài nguyên, giám sát log hệ thống.
- **Tổ trưởng Chuyên môn / Cán bộ Khảo thí:** Ban hành danh mục YCCĐ, duyệt ngân hàng câu hỏi, phê duyệt ma trận đề thi.
- **Giáo viên Bộ môn:** Tải đề số hóa, kiểm duyệt trên Studio HITL, tạo đề thi định kỳ cho học sinh.
- **Học sinh:** Tham gia làm bài thi trắc nghiệm trực tuyến hoặc tải tài liệu ôn tập theo YCCĐ.

### 2.3. Ràng buộc Thiết kế Kỹ thuật theo Thông tư 32/2018/TT-BGDĐT
- **Căn cứ đánh giá pháp lệnh:** CSDL bắt buộc phải quản lý bảng `learning_outcomes` (Yêu cầu cần đạt) làm thực thể trung tâm để liên kết câu hỏi và lập ma trận đề thi.
- **Không phân chia theo bộ sách:** Không tồn tại bảng hoặc trường dữ liệu `textbook_edition` trong taxonomy của ngân hàng câu hỏi.
- **Cấp độ nhận thức bám sát Bảng động từ TT 32:**
  - `RECOGNITION` (Biết): Nhận biết, nhớ lại (đọc, đếm, viết, làm quen, nhận dạng...).
  - `COMPREHENSION` (Hiểu): Diễn đạt theo ý hiểu cá nhân (mô tả, giải thích, thể hiện, sắp xếp...).
  - `APPLICATION` (Vận dụng): Vận dụng vào tình huống mới/giải quyết vấn đề (tính, vẽ, thực hiện, sử dụng, so sánh, phân biệt, lí giải, chứng minh, giải quyết vấn đề thực tiễn - bao gồm cả Vận dụng cao).
- **Hỗ trợ trọn vẹn 3 dạng thức trắc nghiệm mới theo Quyết định 764/QĐ-BGDĐT:**
  - Phần I: Trắc nghiệm 4 lựa chọn.
  - Phần II: Trắc nghiệm Đúng/Sai 4 khẳng định có tính điểm bậc thang.
  - Phần III: Trắc nghiệm Trả lời ngắn.

---

## 3. CÁC GIAO DIỆN NGOÀI CỦA HỆ THỐNG (EXTERNAL INTERFACES)

### 3.1. Giao diện Người dùng (User Interfaces)
- **UI-01 - Dashboard Khảo thí:** Tổng quan số lượng câu hỏi theo Mạch nội dung, YCCĐ và Dạng câu hỏi; tiến độ các job AI bóc tách.
- **UI-02 - AI Digitization Studio (HITL):** Giao diện chia 2 cột đối xứng:
  - Cột trái: PDF / Word Document Viewer có tính năng **Synchronized Scrolling**.
  - Cột phải: Danh sách câu hỏi bóc tách render KaTeX realtime, inline-editor sửa text/LaTeX, gán đáp án và phân loại nhanh theo cây YCCĐ.
- **UI-03 - Cây Kiến thức & Yêu cầu cần đạt (Taxonomy Explorer):** Quản lý cấu trúc 6 tầng theo TT 32.
- **UI-04 - Exam Matrix & Blueprint Builder:** Thiết lập ma trận 2 chiều theo YCCĐ, Dạng bài và Mức độ nhận thức.
- **UI-05 - Exam Paper Previewer:** Xem trước đề thi dạng 2 cột trước khi xuất file Word.

### 3.2. Giao diện Phần mềm & Dịch vụ Ngoài
- **Storage Service Interface:** S3-compatible API (MinIO / AWS S3) lưu trữ tài liệu gốc và ảnh cắt WebP.
- **AI Vision LLM Interface:** Kết nối qua RESTful/gRPC với Gemini 1.5 Flash/Pro, GPT-4o hoặc local Qwen2-VL.
- **Vector Search Engine:** `pgvector` thực hiện tìm kiếm tương đồng câu hỏi qua Cosine Similarity.
- **Export Converter Service:** Microservice Python (`python-docx`, `backend/services/mathjax_service.py`) xuất file Word MathType 7.0 OLE Vector WMF, OMML native và PDF in ấn.

---

## 4. ĐẶC TẢ TÍNH NĂNG HỆ THỐNG CHI TIẾT (SYSTEM FEATURES)

### 4.1. Phân hệ AI Ingestion & Bóc tách Đề thi (AI Parsing Pipeline)

#### SRS-FEAT-01: Nhận diện và Xử lý Bóc tách Tài liệu Đề thi
- **Mô tả:** Hệ thống tiếp nhận file đề thi và bóc tách thành danh sách câu hỏi có cấu trúc.
- **Đầu vào (Inputs):** File `.pdf`, `.docx`, `.doc`, `.png`, `.jpg`, dung lượng $\le 50$MB.
- **Xử lý (Processing):**
  1. Với DOCX/DOC: Trích xuất OLE MathType MTEF binary stream, chuyển đổi trực tiếp sang chuỗi LaTeX chuẩn.
  2. Với PDF/Ảnh scan: Chuyển đổi trang ảnh 300 DPI, áp dụng OpenCV Deskew (cân bằng góc nghiêng) và Binarization (khử nhiễu nền).
  3. Phân vùng layout: Header, Footer, Section I/II/III, Thân câu hỏi, Phương án, Hình vẽ, Bảng biểu.
  4. Gửi payload ảnh/văn bản kèm System Prompt đến Vision LLM để trích xuất JSON schema chuẩn.
  - Tích hợp bộ giải mã JSON chống lỗi thoát chuỗi LaTeX (`repair_llm_json`), tự động nhân đôi các dấu gạch chéo ngược TeX unescaped (`\dfrac`, `\left`, `\hline`, `\text`...) trong chuỗi JSON, đảm bảo tỷ lệ parse thành công tuyệt đối 100%, loại bỏ triệt để hiện tượng fallback sang câu hỏi template rỗng.
  5. Bounding Box Detection: Phát hiện hình học/đồ thị, thực hiện Auto Image Crop, nén WebP, lưu S3.
  6. Khớp nối bảng đáp án ở cuối đề thi với từng câu hỏi tương ứng.
- **Đầu ra (Outputs):** Bản ghi `AIDigitizeJob` chứa danh sách câu hỏi dạng JSON có status `EXTRACTED`.

#### SRS-FEAT-02: Studio Hậu kiểm Đối chiếu Song song (HITL Studio)
- **Mô tả:** Cho phép giáo viên kiểm duyệt, sửa chữa và xác nhận dữ liệu trước khi nhập vào ngân hàng chính thức.
- **Tính năng bắt buộc:**
  - Hiển thị chỉ số tin cậy (Confidence Score): Xanh ($\ge 95\%$), Vàng ($80 - 94\%$), Đỏ ($< 80\%$).
  - Đồng bộ cuộn trang (Synchronized Scrolling): Click câu hỏi bên phải, khung tài liệu bên trái tự động cuộn đến vị trí tương ứng.
  - Cho phép sửa nhanh công thức LaTeX, đổi đáp án chỉ bằng 1 click.
  - Phân loại nhanh: Gán Mạch nội dung, Chủ đề, Bài học, Yêu cầu cần đạt (YCCĐ), Dạng câu hỏi, và Mức độ nhận thức.
  - Nút "Lưu vào Ngân hàng": Tạo câu hỏi ở trạng thái `DRAFT` hoặc `PENDING_REVIEW`.

---

### 4.2. Phân hệ Quản lý Ngân hàng Câu hỏi Chuẩn hóa theo TT 32

#### SRS-FEAT-03: Cấu trúc Cây Phân loại theo Thông tư 32/2018/TT-BGDĐT
- **Mô tả:** Hệ thống tổ chức câu hỏi theo cây phân cấp kiến thức và chuẩn năng lực, **không phân chia theo bộ sách giáo khoa**.
- **Cấu trúc phân cấp bắt buộc:**
  $$\text{Cấp học / Khối lớp} \longrightarrow \text{Môn học} \longrightarrow \text{Mạch nội dung (Strand)} \longrightarrow \text{Chủ đề / Chuyên đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{Yêu\ cầu\ cần\ đạt\ (YCCĐ)} \longrightarrow \mathbf{Dạng\ câu\ hỏi}$$
- **Mã định danh YCCĐ:** Mỗi yêu cầu cần đạt được mã hóa chuẩn hóa (VD: `TOAN12.GT.01`, `VATLI11.CO.03`).
- **Dạng câu hỏi (Problem Archetype):** Danh mục chi tiết các dạng bài tập cụ thể thuộc từng YCCĐ nhằm chống lệch dạng khi trộn đề.

#### SRS-FEAT-04: Hỗ trợ Đa dạng Hình thức Câu hỏi (Bám sát Quyết định 764/QĐ-BGDĐT)
1. `SINGLE_CHOICE`: Trắc nghiệm 4 lựa chọn (A, B, C, D).
2. `TRUE_FALSE_GROUP`: Trắc nghiệm Đúng/Sai 4 khẳng định a, b, c, d độc lập (tính điểm bậc thang 0.1 - 0.25 - 0.5 - 1.0).
3. `SHORT_ANSWER`: Trắc nghiệm trả lời ngắn (điền số hoặc từ ngữ kèm dung sai $\pm \epsilon$).
4. `PASSAGE_GROUP`: Câu hỏi chùm (Một đoạn văn bản/ngữ liệu bài đọc cha và các câu hỏi con).
5. `ESSAY`: Câu hỏi tự luận kèm rubric tiêu chí chấm điểm.

#### SRS-FEAT-04a: Lưu Trữ Thực Tế & Nạp Bền Vững 100% CSDL SQLite Ngân Hàng Câu Hỏi (Persistent SQLite Item Bank)
- **Mô tả:** Đảm bảo toàn bộ ngân hàng câu hỏi được lưu trữ thực tế, toàn vẹn và bền vững trong CSDL SQLite (`storage/quesy.db`, 230+ câu hỏi chuẩn hóa).
- **Yêu cầu kỹ thuật:**
  1. *Khởi động và Nạp Dữ liệu Thực:* Khi khởi động server hoặc tải lại trang F5 trên client, hàm `fetchQuestionsFromDB()` truy vấn toàn bộ câu hỏi qua `GET /api/v1/questions?limit=1000` (không bị giới hạn mặc định 50 câu) để nạp đầy đủ danh sách thực tế vào `state.itemBank`.
  2. *Triệt Tiêu Hoàn Toàn Ghi Đè Dữ Liệu Giả (Zero Mock Overwrite):* Loại bỏ hoàn toàn việc gọi hàm nạp 12 câu hỏi mẫu giả lập (`seedInitialQuestions()`) sau khi đã nạp dữ liệu từ CSDL. Dữ liệu mock chỉ đóng vai trò dự phòng ngoại tuyến cực hạn (offline fallback) khi CSDL rỗng hoàn toàn hoặc mất kết nối mạng.
  3. *Đồng bộ Bền vững Sau Mọi Thao tác:* Mọi thao tác thêm mới câu hỏi (thủ công, import LaTeX), chỉnh sửa nội dung, xóa câu hỏi, hoặc lưu trực tiếp từ phân hệ Soạn đề (`POST /api/v1/composer/save-to-bank`) đều thực thi trực tiếp trên SQLite và tự động cập nhật ngay lập tức `state.itemBank` kèm số lượng badge thời gian thực.
  4. *Bảo toàn Qua Khởi động Lại Server:* File CSDL `storage/quesy.db` bảo toàn nguyên vẹn 100% dữ liệu qua mọi chu kỳ tắt/bật lại máy chủ (`force_reset=False` trong `backend/seed_data.py`).


#### SRS-FEAT-04b: Xuất bản PDF Đề thi Trực tiếp từ Số hóa AI theo Chuẩn LaTeX Thuần (LaTeX-grade Digitize PDF Publisher)
- **Mô tả:** Cho phép giáo viên xuất ngay bộ câu hỏi vừa được AI bóc tách ra tệp PDF chuẩn khảo thí quốc gia (`POST /api/v1/digitize/export-pdf` và `GET /api/v1/digitize/jobs/:job_id/export-pdf`).
- **Typography & Font Chuẩn $\LaTeX$:**
  - Sử dụng toàn diện font **Computer Modern Unicode (CMU Serif)**, loại bỏ hoàn toàn font Times New Roman văn phòng.
  - Công thức toán học render vector SVG trực tiếp qua persistent MathJax TeX daemon, ôm sát chân dòng (baseline) chuẩn xác, loại bỏ khoảng cách thừa trước dấu chấm/phẩy kết thúc câu.
- **Quy chuẩn in ấn:** Khổ giấy A4 Portrait (210 x 297 mm), lề trang 1.6 cm, dàn trang 1 cột với bảng đáp án thích ứng (4 cột / 2 cột / 1 cột), bảng thông tin thí sinh 3 cột chống rớt dòng, chân trang `Trang X - Mã đề thi Y`.
- **Tạm thời ẩn xuất Word:** Trên giao diện tab số hóa AI (HITL Studio), tạm thời ẩn các nút xuất file Word (.docx) để tập trung hoàn thiện và vận hành luồng xuất bản PDF chất lượng cao.

#### SRS-FEAT-04d: Phân hệ Soạn đề LaTeX Trực tiếp Tích hợp AI & Live PDF Preview (Noctorium & ex_test Architecture)
- **Mô tả:** Thay thế hoàn toàn phân hệ số hóa ảnh/OCR cũ bằng phân hệ **Soạn đề** (LaTeX Exam Writing Workspace) mô phỏng thiết kế của `Noctorium` kết hợp gói lệnh khảo thí quốc gia `ex_test.sty` (v3.3). Cung cấp không gian làm việc 2 cột tích hợp có khả năng kéo thả điều chỉnh kích thước linh hoạt (Resizable Split View Workspace):
  1. *Cột bên trái (Editor Pane):*
     - *Khung trên:* Trình soạn thảo mã nguồn LaTeX Dark mode (`#141824`, bảo toàn màu nền khi click con trỏ focus, thanh cuộn mượt mà không kẹt `overflow-y: scroll`) với toolbar `MỚI`, `THÊM ▾` (7 template chuẩn `ex_test`), phím tắt hoàn tác (Undo/Redo), dọn dẹp, sao chép, đánh số dòng và hiển thị vị trí con trỏ.
     - *Thanh Banner Gợi ý Sửa đổi (Inline Diff Banner):* Hiển thị trực tiếp số dòng cần sửa, tự động cuộn và bôi đen vị trí cần thay thế trên editor, hiển thị trực quan khối so sánh `- old_text` (đỏ) và `+ new_text` (xanh), cho phép duyệt nhanh với 2 nút bấm **`[Đồng ý]`** và **`[Từ chối]`**.
     - *Khung dưới:* Trợ lý Soạn thảo AI Copilot hỗ trợ sinh câu hỏi trắc nghiệm Phần I, Đúng/Sai Phần II (QĐ 764 chuẩn `\choiceTF[1]`), Trả lời ngắn Phần III, bảng biến thiên `tkz-tab`, đồ thị TikZ căn giữa `\begin{center}\begin{tikzpicture}...\end{tikzpicture}\end{center}`, hỗ trợ kéo thả thanh ngang hoặc biên trên để co giãn độ cao tùy ý.
  2. *Thanh Phân Tách Ngang (Horizontal Splitter):*
     - Nằm giữa Cột Trái và Cột Phải (`#composer-col-splitter`), hỗ trợ kéo thả chuột/cảm ứng để thay đổi tỷ lệ chiều ngang linh hoạt từ 25% đến 75% (mặc định 60% Left : 40% Right), ghi nhớ tỷ lệ vào `localStorage`.
  3. *Cột bên phải (Live Preview Pane):*
     - *Thanh công cụ:* Tab `ẢNH` và `LỊCH SỬ`, công tắc chuyển đổi `LỜI GIẢI` (tự động đảo giữa in đề thi `[dethi]` và in đáp án `[loigiai]`), menu `XUẤT FILE ▾` (PDF, TeX, Ngân hàng, Copy).
     - *Bản xem trước Live Preview:* Hiển thị trực tiếp trang PDF biên dịch sắc nét từ Tectonic XeTeX Engine (Docker trên host ARM) hoặc Chromium Headless.
     - *Chân trang (Footer):* Nút bấm thanh ngang toàn chiều rộng nổi bật màu xanh dương **`BIÊN DỊCH`** (`#0071e3`).
  4. *Lưu trữ tự động (Local Persistence):* Tự động lưu bản nháp văn bản, cấu hình tỷ lệ chia cột, độ cao trợ lý và kho lưu trữ lịch sử các phiên chat vào `localStorage` của trình duyệt.
  5. *Tích hợp Ngân hàng Câu hỏi (1-Click Save to Bank):* Tự động bóc tách và trích xuất câu hỏi từ cả 2 cú pháp: gói lệnh `ex_test` (`\begin{ex}`) và cú pháp truyền thống (`\textbf{Câu X.}`) sang các bản ghi ngân hàng câu hỏi chuẩn hóa (`questions` table).

#### SRS-FEAT-04e: Thanh Nhập Prompt AI Thu Gọn, Con Trỏ Soạn Thảo Toàn Chiều (Full-Height Caret), Hiệu Ứng Nổi Bật Khi Focus (:focus-within Glow) & Cơ Chế Xóa Sạch Lạc Quan
- **Mô tả:** Cung cấp thanh nhập lệnh AI nhỏ gọn dạng viên thuốc (floating pill bar) neo tại chân khung soạn thảo (`bottom-7`, căn giữa `w-[92%] max-w-xl`, phong cách Apple Glassmorphism bo tròn viền bán trong suốt `#1c1c1f/95`), giữ không gian làm việc luôn tối giản và tập trung cao độ.
- **Hành vi tương tác và kích hoạt 2 trạng thái:**
  1. *Trạng thái Nhập liệu Cục bộ (In-place Typing) & Hiển thị Full Con Trỏ (Full-Height Caret):*
     - Khi người dùng nhấp chuột vào thanh hoặc trường nhập văn bản (`#composer-compact-input`), hệ thống chỉ kích hoạt focus con trỏ để gõ văn bản bình thường (`cursor-text`), **tuyệt đối không tự động bung mở modal/popup trợ lý** nhằm loại bỏ hoàn toàn hiện tượng che khuất màn hình gây gián đoạn mạch soạn thảo.
     - **Hiển thị Full Con Trỏ Soạn Thảo (Anti-Caret-Clipping):** Khắc phục triệt để lỗi con trỏ soạn thảo (caret) bị ăn mất hoặc cụt ngủn khi click vào ô input. Định nghĩa chiều cao và giãn dòng tường minh (`font-size: 13px; line-height: 20px; height: 24px; padding: 1px 0; box-sizing: border-box; caret-color: #c084fc;`), bảo đảm caret hiển thị trọn vẹn 100% chiều cao con trỏ nhấp nháy, không bị clipping do container `overflow` hay co kéo `line-height`.
  2. *Hiệu Ứng Nổi Bật Box Chat Khi Được Select (:focus-within Apple Neon Glow):*
     - Khi bất kỳ thành phần nào trong `#composer-ai-compact-bar` nhận focus (đặc biệt là `#composer-compact-input:focus`), toàn bộ khung thanh bar được kích hoạt trạng thái nổi bật tức thì qua pseudo-class `:focus-within`:
       + **Viền phát sáng (Border Highlight):** Chuyển từ viền mờ `border-white/15` sang viền tím neon đậm đà `border-color: rgba(168, 85, 247, 0.75)` (Apple Purple).
       + **Vòng sáng tỏa (Focus Ring & Glow):** Áp dụng `box-shadow: 0 0 0 3.5px rgba(168, 85, 247, 0.28), 0 16px 40px -6px rgba(0, 0, 0, 0.9)`.
       + **Nền kính sâu hơn:** `background-color: rgba(28, 28, 32, 0.98)` tách biệt rõ rệt khỏi editor.
       + **Phản hồi xúc giác vi mô (Micro-interaction):** Nhấc nhẹ `transform: translate(-50%, -1px) scale(1.005)`.
       + **Icon Sparkles:** Sáng rực rỡ với `filter: drop-shadow(0 0 6px rgba(192, 132, 252, 0.65))` và nút gửi chuyển sang tím neon đồng bộ.
  3. *Trạng thái Kích hoạt Mở rộng (Expansion & Dispatch Trigger):* Hệ thống chỉ mở bung toàn bộ giao diện Popup Trợ lý Soạn thảo (`composer-ai-popup`, độ cao mặc định 56%, có thể phóng to 78% hoặc 92%) khi xảy ra một trong hai điều kiện sau:
     - Người dùng nhấn phím **`Enter`** trong ô nhập liệu.
     - Người dùng nhấp chuột vào **Nút Gửi Mũi Tên Tròn** (`#composer-ai-compact-bar button` - icon `arrow-up`).
  4. *Cơ Chế Xóa Sạch Lạc Quan (Optimistic Dual-Input Reset & Event Decoupling):*
     - Khắc phục triệt để lỗi văn bản cũ còn lưu kẹt trong ô nhập chat của trợ lý sau khi đã gửi đi (Ảnh 1).
     - Ngay tại thời điểm kích hoạt gửi ($t = 0\text{ms}$ khi bắt sự kiện `submitChat`, `submitFromCompact`, hoặc `sendPrompt`), hệ thống đồng thời xóa sạch giá trị (`chatInput.value = ''` và `compactInput.value = ''`) TRƯỚC BẤT KỲ tác vụ bất đồng bộ hoặc render DOM nào.
     - Phân định rõ ngữ nghĩa hàm mở popup: Khi mở do gửi lệnh (`submitFromCompact`), gọi `openAIPopup('')` với tham số rỗng, không truyền lại chuỗi prompt đã gửi vào `prefillPrompt` (loại bỏ hoàn toàn cơ chế gán ngược `chatInput.value = prefillPrompt`). Chỉ khi người dùng bấm mẫu lệnh nhanh (`applyQuickPrompt`), chuỗi mẫu mới được điền vào ô nhập để biên tập.
     - Duy trì con trỏ phím (caret) sẵn sàng tại ô nhập rỗng với màu tím neon sáng `#c084fc` hoặc xanh Apple `#38bdf8`, sẵn sàng cho câu lệnh kế tiếp mà không cần xóa thủ công.
  5. *Chuyển tiếp Dữ liệu Liền mạch:* Khi được kích hoạt, chuỗi prompt được đẩy vào lịch sử phiên hiện tại, thanh thu gọn tạm thời ẩn đi, hiển thị chỉ báo AI đang phản hồi (`composer-typing-indicator`), và gửi yêu cầu bất đồng bộ đến endpoint `/api/v1/composer/chat`.
  6. *Menu Mẫu Lệnh Nhanh (Quick Actions Menu):* Biểu tượng dấu cộng `+` trên thanh compact mở menu ngữ cảnh cho phép chọn nhanh các tác vụ phổ biến: tạo Header đề thi chuẩn Quốc gia 2 cột & mã đề, tạo khung 3 Phần đề thi chuẩn Bộ GD&ĐT 2025, đổi cỡ chữ toàn tài liệu sang 12pt, tạo câu hỏi trắc nghiệm 4 lựa chọn, tạo câu hỏi Đúng/Sai 4 ý QĐ 764, vẽ bảng biến thiên `tkz-tab`, và kiểm tra/sửa cú pháp LaTeX.
- **Quy chuẩn Màu Tương Phản Dark Mode (WCAG 2.1 AA Compliant - Sửa lỗi chữ đen trên nền tối):*
  - Khắc phục triệt để lỗi chữ màu đen `#1d1d1f` bị chìm trên nền tối `#1c1c1f` / `#141824`.
  - Thiết lập design tokens bắt buộc với độ ưu tiên cao (`!important`) cho cả 2 trường nhập liệu `#composer-compact-input` và `#composer-chat-input`:
    - *Text Color:* `#f8fafc` (Slate-50) hoặc `#ffffff` xuyên suốt mọi trạng thái (default, hover, focus, active).
    - *Placeholder Color:* `rgba(226, 232, 240, 0.5)` (Slate-200 / 50%) phân biệt rõ ràng nhưng dịu mắt trên nền tối.
    - *Caret Color (Con trỏ nhập môn):* `#c084fc` (Purple-400) hoặc `#38bdf8` (Sky-400 / Apple Blue) định vị sắc nét vị trí con trỏ với chiều cao chuẩn 100%.
    - *Selection Color:* `::selection { background-color: rgba(59, 130, 246, 0.4); color: #ffffff; }`.
    - *Background & Borders:* Nền trong suốt `background-color: transparent !important`, loại bỏ toàn bộ viền trong, bóng hộp mặc định (`border: none !important; outline: none !important; box-shadow: none !important`).

#### SRS-FEAT-04f: Động Cơ Thay Thế Dòng Mờ Đa Tầng (Fuzzy Line Replacement Engine)
- **Mô tả:** Động cơ áp dụng đề xuất sửa đổi mã nguồn LaTeX đảm bảo tỷ lệ thành công tuyệt đối $\ge 99.5\%$, loại bỏ triệt để thông báo lỗi toast "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại" khi người dùng nhấn [Đồng ý] / [Apply].
- **Thuật toán Khớp Mờ 5 Tầng (5-Tier Resilient Line Matcher):**
  1. *Tầng 1 - Exact Substring Match:* Tìm kiếm nguyên bản `old_text` trong bộ đệm văn bản hiện hành `editor.value` (đồng bộ hai chiều với `this.currentLatex`).
  2. *Tầng 2 - Whitespace & Linebreak Normalization:* Chuẩn hóa toàn bộ ngắt dòng Windows CRLF (`
\n`) về Unix LF (`\n`), đồng thời loại bỏ khoảng trắng thừa cuối dòng (trailing spaces).
  3. *Tầng 3 - Indentation-Insensitive Match & Preserved Re-indent:* Phân rã khối văn bản thành từng dòng, bỏ qua thụt lề đầu dòng (leading indentation / tabs / spaces) để tìm kiếm khối dòng tương đồng; khi áp dụng `new_text`, tự động tái gán thụt lề ban đầu của mã nguồn để bảo toàn cấu trúc code thẩm mỹ.
  4. *Tầng 4 - Sliding Window Sequence Matcher:* Quét cửa sổ trượt $W \in [M - 2, M + 3]$ dòng quanh vị trí nghi vấn, tính toán tỷ lệ tương đồng ký tự qua thuật toán Levenshtein / Gestalt Pattern Matching; tự động chấp nhận thay thế khi độ tương đồng $\ge 0.60$.
  5. *Tầng 5 - Pinned Line Index & Range Replacement:* Sử dụng số thứ tự dòng (`lineNo`) và phạm vi chỉ số ký tự (`matchRange: [start, end]`) đã được xác định và ghim cố định từ bước hiển thị gợi ý `showPendingDiff()` để thay thế trực tiếp vào phạm vi đó nếu chuỗi văn bản đã bị biến đổi nhẹ.

#### SRS-FEAT-04g: Cơ Chế Chuyển Tiếp & Phân Tích Log Lỗi Biên Dịch LaTeX (Compile Error Forwarding & Diagnostics)
- **Mô tả:** Tự động thu thập toàn bộ nhật ký lỗi biên dịch (Compiler Error Log) từ động cơ XeTeX / Tectonic Docker (hoặc Local/Chromium engine) và chuyển tiếp trực tiếp vào ngữ cảnh hội thoại của Trợ lý AI Copilot.
- **Hành vi luồng dữ liệu:**
  1. Khi tiến trình biên dịch `POST /api/v1/composer/compile` thất bại (`data.success = false`), client trích xuất chuỗi thông báo lỗi `errMsg = data.error` và lưu trữ bền vững vào trạng thái `app.composer.lastCompileError`.
  2. Khi người dùng gửi câu hỏi tiếp theo (ví dụ: "Tại sao lỗi biên dịch?", "Sửa lỗi giúp tôi", hoặc bất kỳ lệnh nào trong lúc có lỗi), client tự động đính kèm trường `compile_error_log: this.lastCompileError` vào payload gửi tới `POST /api/v1/composer/chat`.
  3. Backend API (`composer.py`) chấp nhận `compile_error_log` (hỗ trợ cả alias tương thích ngược `compile_error`), trích xuất dòng báo lỗi TeX (ví dụ: `! Undefined control sequence`, `l.24 \badcommand`, `! Missing $ inserted`, `! LaTeX Error: Environment ex undefined`).
  4. AI Copilot được định hướng phân tích chính xác nguyên nhân lỗi cú pháp, tự động đối chiếu dòng mã nguồn bị lỗi trong `current_latex` và sinh ra khối đề xuất sửa đổi diff (dòng đỏ `-` là dòng lỗi, dòng xanh `+` là dòng sửa hoặc chú thích comment vô hiệu hóa) để giáo viên 1-click sửa lỗi ngay lập tức.
  5. Khi biên dịch thành công, hệ thống tự động reset `lastCompileError = null`, xóa sạch cờ cảnh báo lỗi.

#### SRS-FEAT-04h: Giao Diện Trực Quan Hóa Diff Trực Tiếp Trên Ô Soạn Thảo (Inline Editor Diff Overlay / Banner Độc Quyền)
- **Mô tả:** Khi AI đề xuất sửa đổi/diff mã nguồn, hệ thống hiển thị trực quan khối so sánh Diff trực tiếp và độc quyền trên trình soạn thảo mã nguồn LaTeX (thông qua Inline Editor Diff Overlay tại đúng dòng bị ảnh hưởng và/hoặc Inline Diff Banner trên đỉnh editor). **Bắt buộc:** Tuyệt đối KHÔNG hiển thị widget diff trùng lặp trong bubble chat của Trợ lý để giữ không gian hội thoại gọn gàng, tinh tế và tập trung cao độ.
- **Cấu trúc & Trải nghiệm Trực quan:**
  1. *Khối Dòng Đỏ Xóa (`- <old_line>`):* Nền đỏ mờ `rgba(225, 29, 72, 0.15)` (`bg-rose-950/70`), viền trái đỏ tươi `border-l-4 border-rose-500`, văn bản đỏ `text-rose-300`, hiển thị chính xác nội dung dòng mã cũ kèm ký hiệu `-`.
  2. *Khối Dòng Xanh Thêm (`+ <new_line>`):* Nền xanh lục mờ `rgba(16, 185, 129, 0.15)` (`bg-emerald-950/70`), viền trái xanh ngọc `border-l-4 border-emerald-500`, văn bản xanh `text-emerald-300`, hiển thị chính xác nội dung dòng mã mới kèm ký hiệu `+`.
  3. *Thanh Điều Khiển Hành Động Nội Dòng (Inline Action Pill Bar):*
     - Nút **`[Keep / Đồng ý]`**: Icon checkmark, nền xanh dương `bg-blue-600 hover:bg-blue-500 text-white`, nhấp vào áp dụng ngay thay đổi qua Fuzzy Replacement Engine, tự động kích hoạt `compile(true)` và xóa bỏ overlay diff.
     - Nút **`[Undo / Từ chối]`**: Icon undo / dismiss, nền xám tối `bg-slate-700 hover:bg-slate-600 text-slate-200`, nhấp vào hủy bỏ gợi ý sửa đổi, khôi phục trạng thái con trỏ và giữ nguyên vẹn 100% mã nguồn.
  4. *Neo Tọa Độ & Đồng Bộ Cuộn:* Vị trí của Inline Overlay được neo theo tọa độ dòng nguồn trong editor (`top = (lineNo - 1) * lineHeight`), tự động cuộn đồng bộ mượt mà khi người dùng cuộn textarea editor.
  5. *Bubble Chat Tinh Gọn:* Khung tin nhắn Assistant chỉ hiển thị lời chào, giải thích ngắn gọn, phân tích lỗi cú pháp hoặc hướng dẫn sư phạm dưới dạng markdown thuần túy, không chèn các khối card `- / +` hay nút bấm duyệt diff lặp lại.

#### SRS-FEAT-04i: Tối Ưu Hóa Hiệu Năng Gửi Prompt & Tương Tác Box Chat Mượt Mà (Fast Prompt Dispatch & Smooth Micro-Interactions)
- **Mô tả:** Loại bỏ hoàn toàn độ trễ khi gửi prompt và bảo đảm giao diện hộp thoại Trợ lý AI vận hành mượt mà chuẩn 60 FPS theo triết lý Apple Human Interface Guidelines và tương tác xúc giác Emil Kowalski.
- **Tiêu chuẩn kỹ thuật:**
  1. *Phản Hồi Lập Tức (Optimistic UI & Instant Transition):* Khi người dùng nhấn `Enter` hoặc nhấp nút gửi, trong vòng $\le 16$ ms (1 frame), thanh compact input lập tức ẩn, nội dung tin nhắn được đẩy vào lịch sử hội thoại, khung chat cuộn mượt đến đáy (`behavior: 'smooth'`) và hiển thị bong bóng loading `Trợ lý đang xử lý yêu cầu...`.
  2. *Chuyển Động Hardware-Accelerated:* Hộp thoại Popup Trợ lý sử dụng thuộc tính CSS `transform: translate3d(0, 0, 0)`, `transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1)`, loại bỏ tình trạng giật cục (jank) khi co giãn chiều cao.
  3. *Tối Ưu DOM & Lucide Icon Parsing:* Thay vì quét toàn trang qua `lucide.createIcons()`, hệ thống chỉ gọi render icon cục bộ trong node tin nhắn mới, giảm thiểu 95% thời gian layout thrashing.
  4. *Non-blocking Async AI Request:* Kết nối Backend AI sử dụng `httpx.AsyncClient` bất đồng bộ với timeout linh hoạt 15s kèm cơ chế fallback quy tắc thông minh tức thì, triệt tiêu hiện tượng đóng băng socket hay nghẽn thread pool.

#### SRS-FEAT-04j: Quản Lý Khởi Tạo Phiên Chat Mới Sạch Sẽ & Ngăn Kéo Lưu Trữ Lịch Sử Phiên Cũ (Session Lifecycle & Clean Workspace)
- **Mô tả:** Tách biệt tuyệt đối giữa phiên làm việc hiện tại (Active Session) và kho lưu trữ lịch sử các phiên trước đó (Archived Chat Sessions).
- **Hành vi nghiệp vụ:**
  1. *Khởi đầu Sạch sẽ (Fresh Initial State):* Khi người dùng truy cập màn hình `/composer` hoặc khi mở một phiên mới, khung chat active luôn bắt đầu sạch sẽ với duy nhất 1 tin nhắn chào mặc định từ Trợ lý soạn thảo Quesy Copilot. Tuyệt đối không tự động nạp lại hàng loạt tin nhắn trao đổi cũ gây rối mắt.
  2. *Lưu trữ Tự động vào Kho Phiên Cũ:* Khi người dùng bắt đầu phiên mới (`newChat()`), nếu phiên hiện tại đã có tương tác (có $\ge 1$ tin nhắn người dùng), hệ thống tự động đóng gói toàn bộ hội thoại của phiên đó vào danh sách phiên lưu trữ trong `localStorage` (`quesy_composer_chat_sessions`).
  3. *Ngăn kéo Lịch sử (History Drawer / Panel):* Chỉ khi người dùng nhấp vào nút **`[Lịch sử]`** (`#composer-ai-history-btn`), hệ thống mới mở giao diện danh sách các phiên cũ. Mỗi mục hiển thị: thời gian tạo, câu lệnh đầu tiên làm tiêu đề, số lượng trao đổi. Người dùng có thể:
     - Nhấp vào một phiên cũ để xem lại hoặc tải lại các câu lệnh/mã nguồn đã thảo luận.
     - Bấm nút đóng để quay lại phiên hội thoại hiện tại.
     - Bấm nút dọn dẹp để xóa sạch kho lưu trữ lịch sử.

#### SRS-FEAT-04k: Kéo Thả Điều Chỉnh Độ Cao Linh Hoạt Box Trợ Lý Soạn Thảo (Vertical Drag Resize & Unified Single Pill Handle)
- **Mô tả:** Cho phép giáo viên tùy biến độ cao của Box Trợ lý Soạn thảo (`#composer-ai-popup`) một cách linh hoạt, mượt mà theo phương thẳng đứng bằng thao tác kéo chuột hoặc vuốt chạm cảm ứng.
- **Tiêu chuẩn tương tác & Giới hạn:**
  1. *Điểm chạm Kéo thả Hợp nhất (Unified Single Pill Handle):*
     - Hợp nhất hoàn toàn thanh kéo biên trên và thanh pill trong header thành **duy nhất 1 thanh ngang viên thuốc** (`#composer-ai-resize-handle`) đặt tại trung tâm header của popup trợ lý (giữa nút thu gọn bên trái và các nút tác vụ bên phải).
     - Loại bỏ dứt điểm thanh pill phụ trùng lặp bên ngoài đỉnh popup, tối ưu hóa diện tích hiển thị và tuân thủ chặt chẽ Apple Human Interface Guidelines cho modal bottom sheet.
     - Thanh pill hỗ trợ con trỏ chuột dạng `cursor-row-resize` / `cursor-ns-resize`, đổi màu tương tác xúc giác khi di chuột hoặc nhấn giữ (`group-hover:bg-slate-400 group-active:bg-purple-400`).
     - Hỗ trợ cả 2 phương thức điều khiển:
       + *Kéo thả liên tục:* Kéo chuột lên/xuống để co giãn chiều cao tùy ý.
       + *Nhấp chuột / Nhấp đúp (Click / Double-click Toggle):* Nhấp nhanh để chuyển đổi tức thì giữa độ cao mặc định (56%) và độ cao mở rộng (78%).
  2. *Cơ chế Kéo thả Liên tục (Continuous Drag Lifecycle):*
     - Bắt sự kiện `mousedown` / `touchstart` trên handle, ghi nhận tọa độ `startY` và độ cao ban đầu.
     - Lắng nghe `mousemove` / `touchmove` trên `window`: Tính toán độ chênh lệch `deltaY = startY - currentY` và cập nhật độ cao tức thì theo thời gian thực (60 FPS, tạm thời tắt transition CSS trong lúc kéo để triệt tiêu độ trễ).
     - Áp dụng bộ kẹp giới hạn an toàn (Clamping Bounds):
       + Chiều cao tối thiểu: $180\text{px}$ (hoặc $20\%$ khung editor) để đảm bảo luôn nhìn thấy thanh header và ô nhập lệnh.
       + Chiều cao tối đa: $92\%$ chiều cao khung editor để không bao giờ che lấp thanh công cụ trên cùng (`MỚI`, `THÊM ▾`, `LỜI GIẢI`, `XUẤT FILE`).
     - Khi `mouseup` / `touchend`: Kết thúc thao tác kéo, khôi phục lại hiệu ứng chuyển động và lưu chiều cao tùy chỉnh vào `localStorage` (`quesy_composer_ai_height`).

#### SRS-FEAT-04l: Thanh Phân Tách Kéo Thả Ngang 2 Cột Editor & Live Preview Chuẩn Apple HIG (#composer-split-resizer)
- **Mô tả:** Trang bị thanh chia cột tương tác (`#composer-split-resizer` / `#composer-col-splitter`) nằm giữa Cột Soạn thảo LaTeX (Left Pane) và Cột Live Preview (Right Pane), tái thiết kế chuẩn Apple Human Interface Guidelines với khoảng cách đệm thẩm mỹ, không đè sát viền box soạn thảo (Ảnh 2).
- **Cấu trúc & Tiêu chuẩn Kỹ thuật:**
  1. *Khoảng Cách Đệm & Vùng Âm Bản (Negative Space & Gutter Layout):*
     - Mở rộng rãnh phân cách công thái học với chiều rộng rãnh `w-3.5` (14px) hoặc `w-4` (16px), tích hợp khoảng đệm phân cách an toàn `mx-1` / `mx-1.5` giữa Cột Trái (`rounded-xl border border-[#272f42]`) và Cột Phải (`rounded-xl border border-black/[0.08]`).
     - Trục của thanh kéo luôn cách đều viền 2 card từ 6px đến 8px, loại bỏ hoàn toàn hiện tượng thanh kéo và quầng highlight hover bị chèn ép, đè dính hoặc lấn vào đường viền bo góc của box soạn thảo.
  2. *Thanh Cầm Viên Thuốc Apple HIG (Apple Capsule Grabber Handle):*
     - Trục viên thuốc: Chiều rộng $4\text{px}$ (`w-1`), chiều cao $36\text{px}$ (`h-9`), bo tròn hoàn toàn (`rounded-full`).
     - Trạng thái bình thường: Nền xám kim loại trung tính `bg-slate-300 dark:bg-[#34415e]` kết hợp viền mờ chống lóa, ẩn mình nhường chỗ cho nội dung chính (Deference principle).
     - Trạng thái di chuột (Hover): Tự động mở rộng nhẹ chiều cao (`group-hover:scale-y-110 group-hover:h-10`), đổi sang màu xanh Apple System Blue (`#0071e3`), tỏa quầng sáng vi mô `group-hover:shadow-[0_0_8px_rgba(0,113,227,0.35)]` với đường cong chuyển động mượt mà `cubic-bezier(0.16, 1, 0.3, 1)`.
     - Vùng hover mềm bao quanh: Thẻ chứa có hiệu ứng hover nhẹ `group-hover:bg-blue-500/[0.08]` bo góc `rounded-lg`, nằm gọn bên trong rãnh và không bao giờ chạm viền của 2 card lân cận.
     - Trạng thái kéo giữ (Active / Dragging): Phản hồi xúc giác Emil Kowalski co nhẹ `scale-95`, màu xanh đậm đà `bg-[#0071e3]`, kích hoạt con trỏ `cursor: col-resize` và class `.composer-resizing-h` trên toàn trang.
  3. *Quy trình Kéo thả Ngang (Horizontal Drag Lifecycle):*
     - Bắt sự kiện `mousedown` / `touchstart` trên resizer: Ghi nhận tọa độ `startX` và bề rộng container.
     - Lắng nghe `mousemove` / `touchmove` trên `window`: Tính toán bề rộng cột trái theo phần trăm `leftPercent = ((startWidth + (currentX - startX)) / containerWidth) * 100`.
     - Bộ kẹp giới hạn (Clamping Range): Tỷ lệ cột trái được giới hạn nghiêm ngặt từ $25\%$ đến $75\%$ (bảo đảm mỗi cột luôn rộng tối thiểu $320\text{px}$, không bị vỡ giao diện trên mọi kích thước màn hình).
     - Cơ chế chống gián đoạn (Pointer Shield): Tự động áp dụng `pointer-events: none` lên canvas/iframe xem trước PDF trong quá trình kéo chuột nhanh để loại bỏ hiện tượng giật con trỏ khi đi qua frame tài liệu.
     - Nhấp đúp chuột (`dblclick`): Khôi phục tức thì về tỷ lệ vàng mặc định 60% Left : 40% Right.
     - Tự động lưu cấu hình tỷ lệ vào `localStorage` (`quesy_composer_split_ratio`) và khôi phục chính xác khi giáo viên tải lại trang.

#### SRS-FEAT-04m: Tự Động Co Giãn PDF Theo Chiều Rộng Cột & Khung Cuộn Ngang An Toàn (PDF Auto Fit-to-Width & Horizontal Scroll Resiliency)
- **Mô tả:** Đảm bảo trang xem trước PDF luôn hiển thị toàn vẹn, tự động co giãn theo chiều rộng khung hiển thị (Preview Container) khi người dùng kéo thay đổi kích thước cột hoặc thay đổi kích thước cửa sổ trình duyệt, đồng thời hỗ trợ cuộn ngang linh hoạt loại bỏ hoàn toàn hiện tượng tràn viền và xén mất mép phải trang.
- **Tiêu chuẩn Kỹ thuật & Hành vi:**
  1. *Khung Cuộn Đa Chiều Linh Hoạt (`#composer-pdf-scroll-container`):*
     - Thay thế triệt để thuộc tính `overflow-x-hidden` bằng `overflow-x-auto` (kết hợp `overflow-y-auto`).
     - Bố cục vùng chứa trang `#composer-pdf-pages` với `min-w-full w-fit flex flex-col items-center space-y-3` và căn lề tự động an toàn cho các thẻ `.pdf-page-card`: Khi chiều rộng trang PDF nhỏ hơn bề rộng khung nhìn, trang được tự động căn giữa cân đối; khi chiều rộng trang PDF vượt quá bề rộng khung nhìn (do thu hẹp cột hoặc phóng to zoom), toàn bộ trang bắt đầu từ lề trái $x=0$ và thanh cuộn ngang xuất hiện trơn tru, bảo đảm không bao giờ mất thông tin hay xén nét ở lề phải.
  2. *Cơ Chế Tự Động Co Giãn Chiều Rộng (Auto Fit-to-Width Mechanism):*
     - Hệ thống duy trì cờ trạng thái `isAutoFit: true` theo mặc định khi tải tài liệu hoặc khi người dùng nhấp đặt lại tỷ lệ xem (nút `1:1` / `Fit Width`).
     - Trang bị `ResizeObserver` (kèm lắng nghe sự kiện `resize` của cửa sổ) giám sát kích thước khung xem trước (`#composer-preview-canvas` / `#composer-pdf-scroll-container`).
     - Khi bề rộng container thay đổi (do kéo thanh splitter `#composer-col-splitter`, mở rộng/thu gọn panel, hoặc đổi kích thước cửa sổ):
       + Nếu `isAutoFit === true`: Hệ thống tự động tính toán lại tỷ lệ phóng thu tối ưu:
         $$\text{fitZoom} = \max\left(0.3, \min\left(2.5, \frac{\text{availableWidth}}{\text{basePageWidth}}\right)\right)$$
         (với $\text{availableWidth} = \text{clientWidth} - 48\text{px}$ để bảo toàn khoảng đệm padding thẩm mỹ hai bên).
       + Cập nhật tức thì kích thước CSS hiển thị của thẻ trang và canvas (60 FPS trong lúc kéo), sau đó kích hoạt render lại vector sắc nét có chống rung (debounced 100ms).
     - Khi người dùng chủ động zoom thủ công (Ctrl+wheel hoặc bấm nút `+` / `-`), cờ `isAutoFit` được chuyển sang `false` để tôn trọng tỷ lệ xem người dùng đã chọn; khi đó thanh cuộn ngang `overflow-x-auto` đảm bảo người dùng có thể cuộn xem mọi góc của trang mà không bị cắt cụt.

#### SRS-FEAT-04n: Thuật Toán Phóng To / Thu Nhỏ Thông Minh Theo Điểm Neo Chuột & Trọng Tâm Viewport (Smart Zoom-to-Point & Center Anchor Engine)
- **Mô tả:** Triệt tiêu hoàn toàn lỗi giật cục hoặc trang bị nhảy về góc trên cùng bên trái $(0, 0)$ khi phóng to / thu nhỏ. Hệ thống trang bị thuật toán điều hướng zoom theo điểm neo tương đối (Adaptive Anchor Zooming) thông minh dựa trên ngữ cảnh tương tác.
- **Tiêu chuẩn Kỹ thuật & Thuật Toán:**
  1. *Phát Hiện & Xác Định Điểm Neo (Anchor Point Detection):*
     - **Chế độ 1 - Neo theo Vị trí Con trỏ Chuột (Cursor Anchor):** Khi thao tác zoom bằng cuộn chuột kết hợp phím bổ trợ (`Ctrl + Wheel` / `Cmd + Wheel`) và con trỏ chuột nằm bên trong vùng hiển thị PDF (`#composer-pdf-scroll-container`), điểm neo được gán chính xác bằng tọa độ con trỏ:
       $$x_v = \text{event.clientX}, \quad y_v = \text{event.clientY}$$
       Điểm nội dung tài liệu nằm ngay dưới con trỏ chuột được bảo toàn cố định tại đúng vị trí con trỏ sau khi phóng to / thu nhỏ.
     - **Chế độ 2 - Neo theo Trọng tâm Màn hình (Viewport Center Anchor):** Khi thao tác zoom bằng nút bấm trên thanh công cụ nổi (`+`, `-`) hoặc phím tắt bàn phím (con trỏ chuột nằm ngoài tài liệu PDF):
       $$x_v = \text{rect.left} + \frac{\text{rect.width}}{2}, \quad y_v = \text{rect.top} + \frac{\text{rect.height}}{2}$$
       Điểm trọng tâm chính giữa khung nhìn của giáo viên được giữ nguyên ở trung tâm màn hình, bảo đảm không bị trôi dạt sang bất kỳ góc nào.
  2. *Công Thức Bảo Toàn Tọa Độ Cuộn (Invariant Scroll Math):*
     - Bước 1: Tính độ dời tương đối của điểm neo so với khung nhìn container:
       $$dx = x_v - \text{rect.left}, \quad dy = y_v - \text{rect.top}$$
     - Bước 2: Xác định tọa độ điểm neo trong không gian nội dung trước khi zoom:
       $$X_{\text{content}} = \text{scrollLeft}_{\text{old}} + dx, \quad Y_{\text{content}} = \text{scrollTop}_{\text{old}} + dy$$
     - Bước 3: Chuẩn hóa tọa độ theo tỷ lệ nội dung:
       $$r_x = \frac{X_{\text{content}}}{\text{scrollWidth}_{\text{old}}}, \quad r_y = \frac{Y_{\text{content}}}{\text{scrollHeight}_{\text{old}}}$$
     - Bước 4: Cập nhật tỷ lệ `zoomLevel` mới, gán kích thước mới cho các thẻ trang và canvas trong DOM.
     - Bước 5: Cập nhật tức thời vị trí cuộn mới:
       $$\text{scrollLeft}_{\text{new}} = \text{round}(r_x \times \text{scrollWidth}_{\text{new}} - dx)$$
       $$\text{scrollTop}_{\text{new}} = \text{round}(r_y \times \text{scrollHeight}_{\text{new}} - dy)$$
  3. *Bảo Toàn Trạng Thái Khi Dựng Hình Lại (High-DPI Re-rendering Persistence):*
     - Cơ chế render lại trang canvas ở độ phân giải thực (`renderAllPages` với devicePixelRatio) chạy sau khoảng trễ debounce 100ms tự động lưu giữ và khôi phục giá trị `scrollTop` và `scrollLeft`, loại bỏ tuyệt đối hiện tượng chớp nháy hoặc nhảy góc $(0, 0)$.

#### SRS-FEAT-04o: Kiến Trúc Duyệt & Áp Dụng Đa Khối Diff AI (Multi-Diff Sequential Review & Batch Apply Engine)
- **Mô tả:** Cho phép AI Copilot phản hồi nhiều khối sửa đổi cùng một lúc trong một lượt trả lời (đổi font, sửa đáp án, chèn gói tikz, sửa lỗi cú pháp). Hệ thống hỗ trợ duyệt tuần tự từng sửa đổi (1/N, Trước/Sau, Keep/Undo) và cung cấp nút [Áp dụng tất cả] (Apply All) để hợp nhất toàn bộ các thay đổi vào mã nguồn chỉ với 1 thao tác (Ảnh 3).
- **Mô hình Dữ liệu Đa Khối Diff (Multi-Diff Contract):**
  - Mở rộng schema `ChatResponse`:
    ```python
    class ChatResponse(BaseModel):
        reply: str
        suggested_latex: Optional[str] = None
        diff: Optional[DiffSuggestion] = None  # Khối diff đầu tiên (tương thích ngược)
        diffs: Optional[List[DiffSuggestion]] = Field(default_factory=list, description="Danh sách toàn bộ các khối diff")
    ```
  - Thuật toán bóc tách đa khối `extract_all_diffs_from_text`: Quét toàn bộ các khối ````diff ... ````, các cặp `OLD: ... NEW: ...`, các khối `SEARCH / REPLACE`, các block replace và các câu lệnh thay thế nội dòng, loại bỏ trùng lặp và trả về danh sách `diffs: List[DiffSuggestion]`.
- **Cỗ Máy Trạng Thái Duyệt Tuần Tự & Hàng Loạt (Sequential & Batch State Machine):**
  - Trạng thái client: `pendingDiffs: []`, `currentDiffIndex: 0`, `pendingDiff: pendingDiffs[currentDiffIndex]`.
  - Hiển thị song hành trên cả Top Banner (`#composer-pending-diff-banner`) và Inline Overlay (`#composer-inline-diff-overlay`):
    1. *Huy hiệu Đếm Động (Dynamic Capsule Counter):* Thay thế huy hiệu tĩnh `1/1` bằng viên thuốc định vị `${currentDiffIndex + 1}/${pendingDiffs.length}` (ví dụ: `1/3`, `2/3`, `3/3`).
    2. *Bộ Điều Hướng Tuần Tự (Sequential Stepper `<` / `>`):*
       - Nút **`[< Trước]`** (`prevDiff()`): Di chuyển về diff trước đó, tự động cuộn màn hình và bôi đen vị trí dòng tương ứng trong editor. Tự động disable/mờ đi khi đang ở diff đầu tiên (`currentDiffIndex === 0`).
       - Nút **`[Sau >]`** (`nextDiff()`): Di chuyển tới diff kế tiếp. Tự động disable/mờ đi khi đang ở diff cuối cùng (`currentDiffIndex === pendingDiffs.length - 1`).
       - Cả hai nút tự động ẩn hoặc vô hiệu hóa khi tổng số diff $\le 1$.
    3. *Duyệt Từng Khối Sửa Đổi (Individual Accept / Reject):*
       - Nút **`[Keep / Đồng ý]`** (`applyCurrentDiff()`): Áp dụng diff hiện tại vào mã nguồn qua Động cơ Thay thế Mờ 6 Tầng (`applyDiffDirect`), loại bỏ diff khỏi `pendingDiffs`. Nếu hết diff, tự động đóng giao diện diff; nếu còn diff, tự động chuyển trọng tâm hiển thị sang diff kế tiếp và làm nổi bật dòng mới.
       - Nút **`[Undo / Từ chối]`** (`rejectCurrentDiff()`): Hủy bỏ diff hiện tại, loại bỏ khỏi `pendingDiffs` và chuyển sang diff kế tiếp (nếu có).
    4. *Áp Dụng Hàng Loạt (Batch Apply All):*
       - Nút **`[Áp dụng tất cả] (Apply All)`** (`applyAllPendingDiffs()`): Hiển thị nổi bật với nền xanh Apple (`bg-blue-600 hover:bg-blue-500 text-white font-bold`) khi `pendingDiffs.length > 1`.
       - Khi người dùng nhấn nút: Hệ thống tự động lặp qua toàn bộ danh sách `pendingDiffs` theo thứ tự xuất hiện, tuần tự áp dụng từng cặp `(old_text, new_text)` vào mã nguồn LaTeX qua thuật toán thay thế an toàn.
       - Cập nhật giá trị vào textarea editor và `currentLatex`, kích hoạt `compile(true)` một lần duy nhất, đóng toàn bộ banner/overlay diff và hiển thị thông báo toast: *\"Đã áp dụng toàn bộ N sửa đổi vào mã nguồn!\"*.

#### SRS-FEAT-04p: Động Cơ Thay Thế Câu Hỏi Thông Minh & Đồng Bộ Chat-Editor An Toàn (Question Replacement Engine & Safe Chat Sync)
- **Mô tả:** Hỗ trợ người dùng ra lệnh bằng ngôn ngữ tự nhiên để thay thế câu hỏi trong đề thi (ví dụ: *"Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"*, *"Thay thế câu 2 bằng câu khác"*, *"Sửa câu 3"*).
- **Hàm Bóc Tách Khối Câu Hỏi Thứ N (`find_question_block(current_latex, n)`):**
  1. *Định dạng Chuẩn `ex_test.sty`:* Quét toàn bộ các khối `\begin{ex}(?:\[[^\]]*\])?[\s\S]*?\end{ex}` trong `current_latex`. Khối thứ $n$ (1-indexed) được xác định chính xác theo thứ tự xuất hiện từ trên xuống dưới trong mã nguồn.
  2. *Định dạng Đánh Số Cổ Điển:* Nếu không tìm thấy cấu trúc `ex_test`, hệ thống đối sánh các nhãn đánh số `\textbf{Câu n.}`, `\textbf{Câu n:}`, hoặc `Câu n.` và bóc tách toàn bộ phần thân từ điểm bắt đầu nhãn này tới trước nhãn câu hỏi kế tiếp (`\textbf{Câu (n+1).}`, `\end{document}`, `\section*`) hoặc cuối văn bản.
  3. Trả về đúng lát cắt chuỗi nguyên bản (raw substring) của câu hỏi thứ $n$ có mặt trong `current_latex` để làm `old_text`.
- **Cơ Chế Gắn Kết Thông Minh (Smart Diff Binding):**
  1. Nhận diện ý định người dùng: Khi prompt chứa cụm từ biểu thị ý định thay thế câu thứ $n$ (ví dụ: `r'(?:thay thế|thay|đổi|sửa|chuyển|replace)\s*(?:cho\s+)?(?:câu|câu\s+hỏi|câu\s+số|bài|question)\s*(\d+)'`).
  2. Bóc tách câu hỏi mới: Lấy khối câu hỏi mới do AI sinh ra nằm trong ````latex ... ```` hoặc ````diff ... ````.
  3. Khắc phục hạn chế của `SequenceMatcher`: Khi câu hỏi mới khác hoàn toàn câu hỏi cũ (ví dụ câu cũ là đồ thị hàm số, câu mới là bài toán đơn điệu hàm số), `SequenceMatcher` sẽ có độ tương đồng $< 0.52$ và không tìm thấy vị trí thay thế. Cơ chế Smart Diff Binding chủ động liên kết:
     `old_text = find_question_block(current_latex, n)` và `new_text = clean_new_code`.
  4. Trả về đối tượng `DiffSuggestion(action="replace", old_text=old_text, new_text=new_text, description=f"Thay thế câu {n} bằng câu hỏi mới")`.
- **Cơ Chế Hiển Thị Chat Bubble An Toàn (Safe Chat Bubble Rendering):**
  1. *Nguyên tắc bảo toàn khối mã:* Tuyệt đối không ẩn/xóa khối mã nguồn trong bubble chat và không hiển thị badge *"Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn"* trừ khi diff THỰC SỰ tồn tại và hợp lệ (`diff && diff.old_text && currentLatex.includes(diff.old_text)`).
  2. *Fallback khi không có diff hợp lệ:* Nếu diff rỗng hoặc `old_text` không khớp vị trí trong editor:
     - Giữ nguyên khối code trong bubble chat.
     - Trang bị đầy đủ các nút bấm hành động: `[📥 Chèn vào con trỏ]` (`insertB64Code`), `[📋 Sao chép]` (`copyB64Code`), và `[🔄 Áp dụng thay thế]` (`replaceB64Code`).
     - Triệt tiêu hoàn toàn lỗi nuốt mất code trong chat bubble khi editor chưa nhận được diff.
- **Hỗ Trợ Động Cơ Dự Phòng Cục Bộ (Local Offline Fallback Generator):**
  - Khi không cấu hình AI Provider hoặc mạng gián đoạn, động cơ dự phòng nhận diện câu lệnh thay thế câu $n$ (ví dụ: "đơn điệu hàm số thay thế câu 1"), tự động sinh câu hỏi toán chuẩn `ex_test.sty` và bóc tách câu $n$ cũ để trả về `DiffSuggestion` hoàn chỉnh.

#### SRS-FEAT-04q: Hộp Soạn Thảo Đề Thi Tinh Gọn Không Preamble & Động Cơ Nhúng Ngầm Canonical Preamble Injection (Preamble-Free Question Editor)
- **Mô tả:** Tách biệt triệt để giữa phần Khai báo Gói Lệnh (Preamble) và Phần Thân Nội Dung Đề Thi (Exam Body). Giáo viên khi sử dụng phân hệ Soạn đề (`/composer`) chỉ cần tập trung viết nội dung đề thi và các câu hỏi chuẩn gói lệnh khảo thí quốc gia `ex_test.sty` (`\begin{ex}...\choice...\loigiai...\end{ex}`, `\choiceTF[1]`, `\shortans`, TikZ căn giữa, `tkz-tab`), hoàn toàn KHÔNG CẦN viết các dòng lệnh rườm rà như `\documentclass`, `\usepackage`, hay `\begin{document}...\end{document}`. Toàn bộ hình vẽ đồ thị và bảng biến thiên mặc định căn giữa, loại bỏ khuyến nghị `\immini` khỏi cấu trúc chuẩn.
- **Kiến trúc Nhúng Ngầm Preamble Chuẩn (Canonical Preamble Injection):**
  1. *Định nghĩa Preamble Chuẩn (Canonical Preamble Spec):*
     ```latex
     \documentclass[11pt,a4paper]{article}
     \usepackage{geometry}
     \geometry{a4paper, total={175mm,257mm}, left=18mm, top=18mm, right=18mm, bottom=18mm}
     \usepackage{fontspec}
     \usepackage{amsmath,amssymb}
     \usepackage{tikz,tkz-tab}
     \usepackage{tcolorbox}
     \tcbuselibrary{skins,breakable,xparse}
     \usepackage[{mode}]{ex_test}
     ```
     Trong đó `{mode}` được gán động là `dethi` (chế độ in đề thi, ẩn lời giải) hoặc `loigiai` (chế độ in đáp án & hướng dẫn giải chi tiết).
  2. *Bộ Chuẩn Hóa Tài Liệu Hai Chế Độ (Smart Dual-Mode Document Normalizer):*
     - Khi nhận mã nguồn từ editor, hệ thống tự động kiểm tra sự tồn tại của thẻ `\documentclass`:
       + **Nhánh 1 - Mã thuần câu hỏi (Preamble-Free Question Body - Mặc định):** Nếu không có `\documentclass`, hệ thống tự động tiêm Canonical Preamble, bọc phần thân trong `\begin{document}...\end{document}` trước khi chuyển tới Tectonic XeTeX hoặc Chromium Fallback.
       + **Nhánh 2 - Tài liệu toàn vẹn (Full Document - Tương thích ngược):** Nếu người dùng dán toàn bộ tài liệu TeX cũ có sẵn `\documentclass`, hệ thống giữ nguyên cấu trúc, tự động hiện đại hóa `vietnam` $\rightarrow$ `fontspec`, bổ sung các gói lệnh thiếu (`tcolorbox`, `xparse`, `tikz`, `tkz-tab`, `ex_test`) và đồng bộ option `[dethi]` / `[loigiai]` theo cờ chế độ được yêu cầu.
  3. *Điều Khiển Chế Độ Đề Thi / Lời Giải Không Phụ Thuộc Mã Nguồn Editor:*
     - API `POST /api/v1/composer/compile` bổ sung trường `mode: "loigiai" | "dethi"` (mặc định `"loigiai"`).
     - Khi người dùng gạt công tắc `LỜI GIẢI` trên thanh công cụ xem trước, hệ thống truyền cờ `mode` tương ứng. Động cơ tự động thay thế `[dethi]` thành `[loigiai]` trong Canonical Preamble ngầm, hoàn toàn không cần chỉnh sửa hoặc chèn ép thêm text vào ô soạn thảo của giáo viên.
     - Khóa đệm cache biên dịch được tạo từ `md5(latex_code + "::" + title + "::" + mode)` đảm bảo hai chế độ `[dethi]` và `[loigiai]` luôn có bản cache riêng biệt, tức thì và độc lập, không bị xung đột hiển thị.
  4. *Xuất Bản File TeX Hoàn Chỉnh (Full TeX Source Packaging on Export):*
     - Khi giáo viên nhấn menu `XUẤT FILE ▾` $\rightarrow$ `Tải mã nguồn TeX (.tex)`, nếu nội dung hiện tại là dạng tinh gọn không preamble, hệ thống tự động bọc Canonical Preamble đầy đủ và `\begin{document}...\end{document}` vào tệp tải về để đảm bảo tệp `.tex` có thể biên dịch thành công 100% ngay lập tức trên các trình soạn thảo TeX bên ngoài (TeXShop, TeXstudio, Overleaf).
  5. *Định Hướng Trợ Lý AI Copilot:*
     - Prompt hệ thống của Quesy Copilot được chỉ dẫn rõ: môi trường làm việc đã tích hợp sẵn Canonical Preamble của `ex_test.sty` v3.3. Khi giáo viên yêu cầu tạo câu hỏi, AI chỉ sinh phần thân câu hỏi `\begin{ex}...\end{ex}` và tiêu đề cần thiết, tuyệt đối không xuất các đoạn preamble thừa thãi làm ô nhiễm khung soạn thảo.

#### SRS-FEAT-04r: Cấu Trúc Header Đề Thi 2 Cột Chuẩn Quốc Gia (0.38/0.58 Căn Giữa), Khung Mã Đề, 3 Phân Vùng Section textbf/textit & Tự Động Nhận Diện Số Lượng Câu Hỏi (Bộ GD&ĐT 2025)
- **Mô tả:** Cung cấp mẫu mã nguồn LaTeX và các công cụ chèn nhanh cấu trúc đề thi chuẩn Quốc gia theo quy cách Bộ Giáo dục & Đào tạo (Áp dụng từ Kỳ thi Tốt nghiệp THPT 2025). Cho phép giáo viên chèn ngay lập tức từ thanh công cụ `THÊM ▾`, gọi qua menu Gợi ý tác vụ AI, hoặc ra lệnh trực tiếp bằng ngôn ngữ tự nhiên cho AI Copilot. Tích hợp động cơ tự động đếm câu hỏi và cập nhật số lượng câu của từng phần theo thời gian thực.
- **Quy cách Cấu trúc Đề thi Chuẩn Quốc gia 2025:**
  1. *Header 2 Cột Đối Xứng Minipage (Tỉ lệ 0.38/0.58, Căn Giữa Cả 2 Bên, Bỏ Nét Liền Trên):*
     - Bố cục 2 cột cân đối bằng môi trường `minipage` chuẩn LaTeX:
       + Cột trái (độ rộng `0.38\textwidth`, căn giữa `\centering`):
         ```latex
         \noindent
         \begin{minipage}[t]{0.38\textwidth}
           \centering
           \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
           \textbf{TRƯỜNG THPT ...}\\
           \textbf{ĐỀ CHÍNH THỨC}
         \end{minipage}
         ```
       + Cột phải (độ rộng `0.58\textwidth`, căn giữa `\centering`):
         ```latex
         \hfill
         \begin{minipage}[t]{0.58\textwidth}
           \centering
           \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
           \textbf{MÔN: TOÁN}\\
           \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
         \end{minipage}
         ```
     - Tương thích 100% cả khi biên dịch qua Tectonic XeTeX engine lẫn Chromium HTML Vector preview engine.
  2. *Dòng Thông Tin Thí Sinh & Hộp Khung Mã Đề (Chỉ Giữ Nét Liền Đơn Phía Dưới):*
     - Bỏ hoàn toàn nét kẻ ngang `\rule` ở phía trên; chỉ duy trì một nét liền đơn duy nhất ở phía dưới dòng thông tin thí sinh:
       ```latex
       \vspace{0.25cm}
       \noindent
       Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
       \vspace{0.1cm}
       \noindent\rule{\textwidth}{0.5pt}
       \vspace{0.3cm}
       ```
  3. *3 Phân Vùng Section Đề Thi Chuẩn Bộ GD&ĐT 2025 (Thay \section* bằng \textbf + \textit):*
     - Loại bỏ hoàn toàn lệnh `\section*{...}` để tránh chiếm dụng khoảng cách dọc quá lớn và lệch chuẩn văn bản hành chính; thay bằng cặp lệnh chuẩn `\noindent\textbf{PHẦN ...} \textit{...}`:
     - **PHẦN I (Trắc nghiệm nhiều phương án lựa chọn):**
       `\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}`
       Chứa các câu hỏi trắc nghiệm chuẩn lệnh `\begin{ex} ... \choice{A}{\True B}{C}{D} ... \end{ex}`.
     - **PHẦN II (Trắc nghiệm Đúng/Sai 4 khẳng định, QĐ 764/QĐ-BGDĐT):**
       `\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}`
       Chứa các câu hỏi trắc nghiệm Đúng/Sai với lệnh `\choiceTF[1]` (tham số `[1]` bắt buộc ép 4 khẳng định a, b, c, d hiển thị theo **1 cột dọc duy nhất**, mỗi ý 1 dòng, không chia 4 cột hay 2 cột; tuyệt đối không thêm `\\` sau các dấu ngoặc nhọn `{}`) và barem bậc thang `\begin{itemchoice}\itemch...\end{itemchoice}`.
     - **PHẦN III (Trắc nghiệm trả lời ngắn):**
       `\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}`
       Chứa các câu hỏi điền kết quả số/phân số với lệnh `\shortans`.
  4. *Thuật Toán Tự Động Nhận Diện Số Lượng Câu Hỏi Từng Phần (Two-Tier Section Question Count Sync):*
     - Hệ thống vận hành cơ chế đồng bộ số lượng câu hỏi hai tầng (Dual-tier Synchronization):
       + **Backend Tier (`composer_service.py` - `sync_section_question_counts(latex_code: str) -> str`):**
         * Phân tách mã nguồn thành các block Phần I, Phần II, Phần III qua regex `PHẦN\s+(I{1,3}|IV|V|[1-9])\b`.
         * Đếm số câu hỏi trong từng phần theo thứ tự ưu tiên: Ưu tiên 1 phát hiện các môi trường `\begin{ex}`, `\begin{bt}`, `\begin{vd}` (`re.findall(r'\\begin\{(?:ex|bt|vd)\}', sec_content)`); Ưu tiên 2 (khi không dùng ex_test) bóc tách tiêu đề hướng dẫn ra khỏi phần thân (`clean_body`), đếm các câu đánh số kinh điển `\textbf{Câu \d+}` hoặc đầu dòng `Câu \d+[\.:]` nhằm ngăn chặn tuyệt đối lỗi đếm nhầm "câu 1" trong chuỗi hướng dẫn "từ câu 1 đến câu X".
         * Nếu `count > 0`: Tự động thay thế mẫu `[Tt]ừ\s+câu\s+1\s+đến\s+câu\s+\d+` thành `từ câu 1 đến câu {count}`.
         * Tự động kích hoạt trước khi gửi mã sang Tectonic XeTeX engine, Chromium HTML Preview, hoặc xuất file `.tex`.
       + **Frontend Tier (`app.js` - `syncSectionQuestionCounts(latexCode)`):**
         * Tự động đồng bộ nội dung trực tiếp trên textarea của editor khi người dùng bấm nút **BIÊN DỊCH** (hoặc `Ctrl+S` / `Cmd+S`), sau thời gian gõ debounce (800ms), hoặc khi nhấn Xuất/Sao chép mã.
  5. *Tích Hợp Giao Diện Người Dùng (UI Integration):*
     - Dropdown menu `THÊM ▾` trên thanh công cụ của Editor phân chia thành 2 nhóm rõ rệt:
       + Nhóm *CẤU TRÚC ĐỀ THI QUỐC GIA 2025*: Header 2 Cột & Mã đề (0.38/0.58), Phần I (12 câu - tự động đếm), Phần II (4 câu QĐ 764 - tự động đếm), Phần III (6 câu ngắn - tự động đếm), và Trọn bộ Đề thi Quốc Gia.
       + Nhóm *MẪU LỆNH EX_TEST*: Trắc nghiệm, Đúng/Sai, Trả lời ngắn, Tự luận, Hình TikZ, Hình cạnh chữ, Lời giải.
     - AI Copilot (`POST /api/v1/composer/chat`) cập nhật `system_prompt` và các phản hồi mẫu (fallback) tự động xuất định dạng Header 0.38/0.58 căn giữa và các Section chuẩn `\noindent\textbf{PHẦN ...}` `\textit{...}`.
  6. *Động Cơ Render HTML/PDF Hỗ Trợ Đầy Đủ Các Lệnh:*
     - Engine `compile_latex_source_to_html` trong `composer_service.py` bổ sung bộ phân giải cho:
       + `\begin{minipage}[t]{...} ... \end{minipage}` chuyển đổi tỉ lệ `0.38\textwidth` $\rightarrow$ `38.0%` và `0.58\textwidth` $\rightarrow$ `58.0%` responsive flexbox/inline-block CSS.
       + `\centering` bên trong `minipage` tự động thiết lập `text-align: center;` cho khối hiển thị.
       + `\noindent\textbf{...}` và `\textit{...}` chuyển đổi thành thẻ `<strong>` và `<em>` tương ứng chuẩn HTML5.
       + `\rule{...}{...}` $\rightarrow$ Thẻ divider đường kẻ đen mảnh (`<hr>`).
       + `\dotfill` $\rightarrow$ Thẻ co giãn đường chấm dotted baseline.
       + `\framebox{...}` / `\fbox{...}` $\rightarrow$ Khung viền đen 1.5px bọc mã đề.
       + **Kiến trúc Pipeline Tránh Lỗi Over-Escaping:** Các macro layout (`minipage`, `hfill`, `rule`, `dotfill`, `framebox`, `fbox`) và khối `loigiai` được phân giải trực tiếp trên `final_body` **SAU** khi bước bóc tách đoạn văn và render công thức toán `render_math_html` hoàn tất. Cơ chế này bảo vệ các thẻ HTML thực tế (`<div>`, `<span>`, `<hr>`) không bị chuyển hóa nhầm thành text thô đã escape (`&lt;div...&gt;`, `&lt;span...&gt;`). Regex `\rule` chuẩn hóa tuyệt đối với `r'\\\\rule\\{([^}]+)\\}\\{([^}]+)\\}'`.

#### SRS-FEAT-04s: Trợ Lý AI Chẩn Đoán Lỗi Biên Dịch LaTeX Thông Minh & Ánh Xạ Dòng Lỗi Preamble-Free (AI Compiler Error Diagnostics & Line-Offset Mapping)
- **Mô tả:** Hệ thống hỗ trợ giáo viên tự động đọc, phân tích và sửa lỗi biên dịch TeX/XeTeX/Tectonic trong phân hệ Soạn đề (`/composer`).
- **Luồng Dữ Liệu Khép Kín:**
  1. *Lưu trữ Log Lỗi:* Khi biên dịch `POST /api/v1/composer/compile` thất bại (`success = false`), client tự động ghi nhận chuỗi log lỗi đầy đủ vào `app.composer.lastCompileError`.
  2. *Chuyển tiếp Tự động sang Trợ Lý AI:* Khi người dùng gửi prompt yêu cầu (hoặc kích hoạt từ menu AI "SỬA LỖI"), payload gửi đến `POST /api/v1/composer/chat` tự động truyền trường `compile_error`.
  3. *Động Cơ Chẩn Đoán Log Lỗi Hai Tầng:*
     - **Tầng LLM:** System prompt huấn luyện AI Copilot đọc hiểu cấu trúc log TeX, trích xuất số dòng và nguyên nhân lỗi, phản hồi phân tích ngắn gọn kèm khối ```diff``` sửa lỗi chính xác.
     - **Tầng Cục Bộ (Local Diagnostic Engine - `diagnose_compile_error`):** Hoạt động độc lập và tức thì kể cả khi offline hoặc AI Provider chưa cấu hình:
       + *Trích xuất số dòng compiler:* Regex bóc tách số dòng `L_comp` từ các thông báo lỗi Tectonic/XeTeX (`error: document.tex:(\d+):`, `l\.(\d+)`).
       + *Tính toán độ lệch dòng (Preamble Line Offset):* Với tài liệu Preamble-Free, hệ thống tự động trừ đi 11 dòng preamble chuẩn: `L_user = L_comp - 11` để định vị chính xác 100% dòng lỗi trên màn hình của người dùng.
       + *Phân tích 5 nhóm lỗi kinh điển:*
         1. `There's no line here to end`: Thừa dấu `\\` sau ngoặc nhọn `{...}` hoặc ở đầu dòng → Tự động xóa `\\`.
         2. `Undefined control sequence`: Nhận diện các lệnh gõ sai phổ biến (`\ule` → `\rule`, `\choiceTFt` → `\choiceTF[1]`, `ight|` / `\night|` → `\right|`, `\fracc` → `\dfrac`, `\n` → xuống dòng thực).
         3. `Missing $ inserted`: Ký hiệu toán học ngoài môi trường math → Tự động bọc cặp dấu `$ ... $`.
         4. `Missing \right. inserted` hoặc `Extra }, or forgotten \right`: Mất cân bằng cặp `\left.` và `\right.` → Hoàn thiện khối ngoặc.
         5. `Environment undefined` / Thiếu gói lệnh: Tự động đề xuất bổ sung gói vào preamble hoặc sửa tên môi trường.
       + *Trả về `ChatResponse(reply, diff)`:* Chứa phân tích nguyên nhân và khối diff chuẩn để người dùng bấm **[Đồng ý]** là mã nguồn được cập nhật ngay lập tức.

#### SRS-FEAT-04t: Quy Chuẩn Mẫu Câu Hỏi Đúng/Sai \choiceTF[1] 1 Cột Thẳng Đứng & Rà Soát Toàn Diện Mẫu Lệnh Form Mẫu
- **Mô tả:** Đảm bảo toàn bộ các biểu mẫu đề thi trong hệ thống (Menu `THÊM ▾`, `EX_TEST_TEMPLATES`, `SNIPPETS`, `TEMPLATES`, và bộ render HTML) tuân thủ 100% chuẩn mực khảo thí và không chứa lỗi cú pháp TeX.
- **Quy Chuẩn Định Dạng Đúng/Sai (`\choiceTF[1]`):**
  1. *Ép buộc 1 Cột Duy Nhất:* Tham số `[1]` là bắt buộc đối với lệnh `\choiceTF[1]`. Bốn khẳng định a), b), c), d) luôn hiển thị thẳng hàng dọc từ trên xuống dưới (chiếm 100% chiều rộng mỗi dòng), không chia thành 2 cột hay 4 cột.
  2. *Cú pháp Chuẩn Tuyệt Đối:*
     ```latex
     \begin{ex}
     Nội dung câu hỏi... Xét tính đúng/sai của các khẳng định sau:
     \choiceTF[1]
     {\True Khẳng định a đúng.}
     {Khẳng định b sai.}
     {\True Khẳng định c đúng.}
     {Khẳng định d sai.}
     \begin{loigiai}
     \begin{itemchoice}
     \itemch Đúng. Giải thích ý a.
     \itemch Sai. Giải thích ý b.
     \itemch Đúng. Giải thích ý c.
     \itemch Sai. Giải thích ý d.
     \end{itemchoice}
     \end{loigiai}
     \end{ex}
     ```
  3. *Tuyệt đối không chứa `\\`:* Cấm hoàn toàn dấu `\\` sau các dấu ngoặc nhọn `{...}`.
  4. *Khử Lỗi Chuỗi Ký Tự Newline (`\n`) trong JavaScript:* Toàn bộ các template string trong frontend JavaScript dùng dòng mới thực tế thay vì ký tự escape `\\n`, loại bỏ triệt để hiện tượng XeTeX sinh lỗi `\n{}` hoặc `There's no line here to end`.
  5. *Đồng bộ Bộ Render HTML Preview (`compile_latex_source_to_html`):* Bộ render HTML chuyển đổi `\choiceTF[1]` thành 4 hàng dọc `display: block; width: 100%; margin-bottom: 4px;` kèm nhãn a), b), c), d) và trạng thái đúng/sai.

#### SRS-FEAT-04u: Trợ Lý AI Copilot Đa Phương Tiện: Đính Kèm, Dán Clipboard (Ctrl+V) & Kéo Thả Phân Tích Hình Ảnh (Multi-Modal Image Input, Clipboard Paste & Visual Reasoning)
- **Mô tả:** Mở rộng năng lực phân hệ Soạn đề (`/composer`) cho phép giáo viên tải lên hình ảnh trực tiếp qua nút đính kèm, kéo thả tệp ảnh (Drag & Drop), hoặc dán ảnh trực tiếp từ bộ nhớ tạm (Clipboard Paste qua `Ctrl+V` / `Cmd+V`) vào thanh prompt thu gọn (`#composer-compact-input`) hoặc ô chat lớn (`#composer-chat-input`) để Trợ lý AI Copilot phân tích đề bài, trích xuất LaTeX, vẽ lại đồ thị hàm số và bảng biến thiên TikZ.
- **Quy chuẩn Tương tác Người dùng & Giao diện (Apple HIG & Emil Kowalski):**
  1. *Đính kèm từ Compact Bar:*
     - Thanh compact bar trang bị nút biểu tượng hình ảnh (`<i data-lucide="image"></i>`), nhấp vào sẽ kích hoạt hộp thoại chọn file ảnh ẩn (`#composer-compact-image-input`, `accept="image/*"`).
     - Khi dán ảnh (`Ctrl+V`) hoặc chọn file từ compact bar: Hệ thống tự động chuyển tiếp ảnh vào danh sách đính kèm, mở bung popup trợ lý lớn (`#composer-ai-popup`), chuyển tiêu điểm focus vào `#composer-chat-input`, hiển thị chip thumbnail ảnh và giữ nguyên trải nghiệm liền mạch.
  2. *Đính kèm & Dán trên Khung Chat Popup:*
     - Khung chat lớn trang bị nút đính kèm ảnh tinh tế trong toolbar con cạnh nút `+` (Quick Actions) kèm input file ẩn (`#composer-chat-image-input`).
     - Hỗ trợ sự kiện dán ảnh (`paste` event) trực tiếp trên `#composer-chat-input` và toàn bộ khung chat: Trích xuất tự động `image/*` từ clipboard dạng Base64 Data URL (`data:image/...;base64,...`).
     - Hỗ trợ kéo thả ảnh (Drag & Drop): Khi kéo file ảnh vào vùng chat, khung viền chuyển hiệu ứng highlight tím sáng `border-purple-500/80 bg-purple-500/10` (active dropzone), thả file sẽ tự động nạp ảnh vào khay đính kèm.
  3. *Khay Hiển Thị Thumbnail Đính Kèm (#composer-attached-images-container):*
     - Nằm ngay phía trên ô nhập liệu `#composer-chat-input`.
     - Mỗi ảnh được hiển thị dưới dạng card thumbnail bo góc tròn `rounded-xl`, kích thước 54px x 54px, viền mờ `border-white/15`, ảnh bên trong `object-cover`.
     - Góc trên bên phải thumbnail trang bị nút xóa (✕) với vi tương tác co nhẹ `active:scale-90`, hover chuyển đỏ.
     - Nhấp trực tiếp vào thumbnail mở Modal Xem trước Phóng to (Image Lightbox) với nền mờ `backdrop-blur-sm` mà không làm gián đoạn luồng soạn thảo.
  4. *Hiển thị Tin nhắn Phía Người Dùng (#composer-chat-messages):*
     - Khi tin nhắn được gửi đi, bong bóng chat của user hiển thị đồng thời văn bản câu hỏi và các thumbnail ảnh đính kèm (bo góc `rounded-lg`, click mở lightbox phóng to).
     - Lịch sử phiên (`quesy_composer_chat_sessions`) lưu trữ đồng bộ mảng ảnh `images`.
- **Hợp Đồng API & Xử Lý Phía Máy Chủ (`POST /api/v1/composer/chat`):**
  1. *Cập nhật Schema Request:* Bổ sung trường `images: Optional[List[str]] = Field(default_factory=list)` vào cả `ChatRequest` và `ChatMessage`.
  2. *Cấu trúc Message Đa Phương Tiện (Multi-Modal LLM Formatting):*
     - Khi kết nối nhà cung cấp AI bên ngoài (OpenAI GPT-4o, Google Gemini Flash, OpenRouter): Đóng gói payload user content thành mảng các khối đối tượng:
       `[{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_base64_data_url}}]`.
  3. *Định hướng System Prompt & Năng lực Phân tích Ảnh:*
     - Nhận diện đề thi, bảng biến thiên, đồ thị hàm số (bậc ba, phân thức, bậc bốn), hình học không gian hoặc chữ viết tay trong ảnh.
     - Tái tạo đồ thị hàm số và hình học thành mã TikZ căn giữa (`\begin{center}\begin{tikzpicture}...\end{tikzpicture}\end{center}`), loại bỏ hoàn toàn việc dùng `\immini` làm mặc định để chống méo mó bố cục và tràn viền.
     - Tái tạo bảng biến thiên bằng gói `tkz-tab` (`\tkzTabInit...`) căn giữa.
     - Đóng gói câu hỏi chuẩn `ex_test.sty` (`\begin{ex}...\choice / \choiceTF[1] / \shortans...\loigiai...\end{ex}`), Phần II tuyệt đối không gõ tiền tố `a)`, `b)`.
  4. *Động Cơ Dự Phòng Cục Bộ (Local/Offline Fallback Engine):*
     - Khi AI ngoại vi không khả dụng hoặc mất mạng, hệ thống phát hiện cờ có ảnh `images`, đối chiếu từ khóa ngữ cảnh yêu cầu (đồ thị, bảng biến thiên, tikz, giải bài) và trả về khối mã nguồn LaTeX/TikZ mẫu hoàn chỉnh kèm khối diff và lời giải thích rõ ràng.

#### SRS-FEAT-04v: Cơ Chế Dynamic Adaptive Compilation Timeout Cho Đề Thi Quy Mô Lớn & Trợ Lý AI Chẩn Đoán Tối Ưu Hóa TikZ (Dynamic Adaptive Compilation Timeout & TikZ Optimization Copilot)
- **Bối cảnh & Bài toán Kỹ thuật:**
  - Đề thi khảo thí hoàn chỉnh (12 câu Phần I, 4 câu Phần II, 6 câu Phần III - ví dụ Đề kiểm tra giữa kỳ I THPT Việt Đức 2026-2027) có quy mô văn bản lớn (~24.000 ký tự, 6 trang PDF vector A4) và chứa nhiều hình vẽ TikZ, bảng biến thiên `tkz-tab`, đặc biệt là các đồ thị hàm phân thức và hàm bậc ba với mật độ lấy mẫu cao `samples=100` trong 4 phương án lựa chọn.
  - Trước đây hệ thống gán cứng timeout cố định (`timeout_s: 60` tại `compile_with_remote_tectonic_api` và `timeout=45` tại `compile_with_tectonic`). Trên máy chủ ARM (`armbian:8090`), tiến trình biên dịch XeTeX trọn vẹn mất 67.68 giây, dẫn tới việc container Tectonic ngắt tiến trình và ném lỗi HTTP 504 `{"detail": "Compilation timed out"}`.
- **Giải pháp Kỹ thuật & Luồng Xử Lý:**
  1. *Thuật toán Tính Timeout Động Phích Thích Ứng (Dynamic Adaptive Compilation Timeout):*
     - Trước khi gửi lệnh biên dịch, hệ thống tự động bóc tách và phân tích độ phức tạp của mã nguồn LaTeX qua hàm `compute_compilation_timeout(latex_source: str) -> int`:
       + `tikz_count`: Đếm tổng số khối môi trường TikZ và bảng biến thiên (`\begin{tikzpicture}`, `\begin{tkzTab}`, `\tkzTabInit`).
       + `code_len`: Tổng độ dài ký tự của mã nguồn LaTeX sau khi chuẩn hóa.
       + Công thức tính toán timeout động:
         $$\text{calc\_timeout} = \max\left(60, \min\left(240, 45 + 10 \times \text{tikz\_count} + \left\lfloor \frac{\text{code\_len}}{250} 
ight
floor 
ight)
ight)$$
     - Truyền `timeout_s: calc_timeout` vào payload JSON gửi sang Remote Tectonic Docker API (`http://armbian:8090/compile`).
     - Thiết lập timeout mạng cho socket HTTP `urllib.request.urlopen` là $\text{calc\_timeout} + 15$ giây để dự phòng độ trễ truyền gói tin mạng (network jitter buffer).
     - Áp dụng $\text{calc\_timeout}$ cho cờ `timeout` của tiến trình con `subprocess.run` khi biên dịch với Local Tectonic engine (`compile_with_tectonic`).
  2. *Trợ Lý AI Copilot Chẩn Đoán Lỗi Timeout & Tự Động Sinh Diff Tối Ưu TikZ:*
     - Khi gặp thông điệp lỗi biên dịch chứa `"Compilation timed out"`, `"timed out"`, hoặc `"quá thời gian cho phép"`, hàm `diagnose_compile_error` tự động kích hoạt chẩn đoán chuyên biệt:
       + Xác định nguyên nhân gốc: Đề thi có quy mô lớn chứa nhiều hình vẽ TikZ phức tạp với tham số tính toán toạ độ giải tích dày đặc (`samples=100`).
       + Thông báo hệ thống: Quesy đã tự động nâng ngưỡng timeout biên dịch lên tới $\text{calc\_timeout}$ giây (tối đa 240s) theo cơ chế thích ứng.
       + Khuyến nghị tối ưu hóa kỹ thuật: Đề xuất chuyển đổi các thông số `samples=100` thành `samples=50` (hoặc `samples=60`). Trên khổ A4 tiêu chuẩn, mật độ 50 điểm lấy mẫu đã tạo nên đường cong Bézier trơn mịn tuyệt đối cho in ấn vector $1200\text{ DPI}$, đồng thời giảm 50% khối lượng tính toán giải tích của XeTeX, giúp tăng tốc độ biên dịch lên gấp đôi.
       + Trích xuất danh sách `diffs` (`List[DiffSuggestion]`): Định vị toàn bộ các dòng chứa `samples=100` trong mã nguồn và sinh khối diff đề xuất thay thế sang `samples=50`, cho phép người dùng click "Đồng ý" (Apply) hoặc "Áp dụng tất cả" (Apply All) trực tiếp trên khung soạn thảo.
  3. *Thông Báo Tiến Trình Biên Dịch Đề Thi Lớn (Progressive Status Feedback):*
     - Trên giao diện Frontend (`app.js`), khi biên dịch tài liệu lớn (`code_len > 10000` hoặc $\ge 4$ khối TikZ), nhãn trạng thái `#composer-status-text` lập tức hiển thị `"Đang biên dịch đề thi lớn (nhiều hình TikZ)..."`.
     - Kích hoạt đồng hồ tiến trình đa nấc (Progressive Status Timer: 5s, 15s, 35s) cập nhật thông điệp thời gian thực (ví dụ: *"Đang xử lý hình vẽ TikZ & tính toán toạ độ..."*, *"Đang kết xuất các trang PDF vector qua XeTeX..."*), triệt tiêu hoàn toàn cảm giác giao diện bị đơ/treo khi biên dịch tài liệu nặng.

#### SRS-FEAT-04w: Chuẩn Hóa Căn Giữa Đồ Thị Toán Học, Bảng Biến Thiên & Bảng Biểu (Centered Diagrams Invariant) & Loại Bỏ Hoàn Toàn Khuyến Nghị `\immini`
- **Bối cảnh & Vấn đề Kỹ thuật:**
  - Trước đây, `system_prompt` của AI Copilot khuyến nghị sử dụng `\immini{Văn bản câu hỏi}{Mã hình TikZ}` khiến mô hình AI tự động bao bọc tất cả hình ảnh, đồ thị sang góc phải. Khi người dùng tải ảnh đề thi hoặc tạo câu hỏi, đồ thị bị co ép lệch một bên, văn bản và 4 phương án bị ép dạt sang mép trái, đồng thời việc lồng `\choice` vào trong `\immini` gây xung đột hộp TeX (`Missing }`, `box overflow`).
  - Hơn nữa, việc thiếu quy chuẩn căn lề minipage trong tiêu đề đề thi khiến AI sinh Header chia đôi `0.5\textwidth` mỗi bên, thiếu `\centering` cột trái, thiếu `\hfill`, thiếu dòng thí sinh `\dotfill` kèm khung mã đề `\framebox{\textbf{Mã đề: ...}}`, và câu hỏi Đúng/Sai Phần II sinh thiếu tham số `[1]` (`\choiceTF` thay vì `\choiceTF[1]`) đồng thời gõ nhầm tiền tố `a)`, `b)` vào nội dung khẳng định gây lỗi hiển thị lặp `a) a)`, `b) b)`.
- **Đặc tả Giải pháp & Quy chuẩn Bắt buộc (Centered Diagrams Invariant):**
  1. *Mặc định Căn Giữa 100% (Centered Layout):*
     - Toàn bộ đồ thị hàm số TikZ, hình học không gian TikZ, bảng biến thiên `tkz-tab` và bảng biểu thống kê BẮT BUỘC PHẢI ĐƯỢC ĐẶT Ở CHÍNH GIỮA bằng môi trường `\begin{center}\begin{tikzpicture}...\end{tikzpicture}\end{center}`.
     - Vị trí: Đặt ngay bên dưới phần dẫn đề bài (stem) và ở phía trên các phương án lựa chọn `\choice` / `\choiceTF[1]` / `\shortans`.
     - Tuyệt đối loại bỏ khuyến nghị `\immini` khỏi toàn bộ system prompt và template mẫu.
  2. *Chuẩn hóa Header 2 Cột Bộ GD&ĐT 2025:*
     - Minipage trái `0.38\textwidth` căn giữa `\centering`; Minipage phải `0.58\textwidth` căn giữa `\centering`; phân cách bằng `\hfill`.
     - Dòng thông tin thí sinh: `Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: ...}}`.
     - Duy nhất 1 đường nét liền đơn `\noindent\rule{\textwidth}{0.5pt}` dưới thông tin thí sinh.
     - Tiêu đề Section in đậm & in nghiêng: `\noindent\textbf{PHẦN ...} \textit{...}` (không dùng `\large` hay `\section*`).
  3. *Chuẩn hóa Phần II Đúng/Sai:*
     - Bắt buộc dùng `\choiceTF[1]`, khẳng định chiếm 100% độ rộng 1 cột.
     - Tuyệt đối không gõ tiền tố `a)`, `b)`, `c)`, `d)` trong khẳng định để tránh lặp nhãn kép.
  4. *Tối ưu hóa Lấy Mẫu TikZ:* Mặc định `samples=50` hoặc `samples=60` trên mọi đồ thị hàm số để bảo đảm biên dịch siêu tốc.

#### SRS-FEAT-04x: Cơ chế Chống Nhân Đôi Ảnh Đính Kèm Khi Dán Clipboard (Clipboard Paste Deduplication & Event Isolation)
- **Mô tả:** Loại bỏ hoàn toàn lỗi nhân đôi ảnh chụp khi giáo viên dán ảnh (`Ctrl+V` / `Cmd+V`) vào ô chat trợ lý (`#composer-chat-input`).
- **Xử lý Kỹ thuật Đa tầng:**
  1. *Ngắt lan truyền sự kiện (Event Propagation Stop):* Bổ sung `e.stopPropagation()` song hành cùng `e.preventDefault()` trong listener dán ảnh tại `setupPasteAndDropListeners()`, triệt tiêu hoàn toàn sự kiện nổi bọt lên container cha `#composer-chat-input-container`.
  2. *Cờ Idempotent Binding Guard:* Bổ sung `this._pasteListenersBound` ngăn chặn việc gán trùng lặp nhiều lần các bộ lắng nghe sự kiện khi khởi tạo lại phân hệ Soạn đề.
  3. *Debounce & Trùng Lặp Chữ Ký Ảnh (Image Signature Deduplication):* Tại hàm `addAttachedImage`, kiểm tra chữ ký ảnh kết hợp timestamp: nếu cùng một ảnh được gửi liên tiếp trong khoảng thời gian < 500ms hoặc đã có trong danh sách đính kèm, hệ thống lập tức từ chối và không thêm lặp.

#### SRS-FEAT-04y: Chuẩn Hóa Cấu Trúc Khảo Thí Quốc Gia 2025: Reset Thứ Tự Câu Hỏi Về 1 Ở Mỗi Phần (\setcounter{ex}{0}) & Loại Bỏ Triệt Để Thẻ \large Ở Tiêu Đề Phần
- **Mô tả:** Đảm bảo toàn bộ tài liệu đề thi môn Toán và KHTN được xuất bản chuẩn Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT:
  1. *Reset bộ đếm câu hỏi:* PHẦN I gồm 12 câu trắc nghiệm (Câu 1 đến Câu 12); PHẦN II (Đúng/Sai) bắt đầu lại từ Câu 1 đến Câu 4; PHẦN III (Trả lời ngắn) bắt đầu lại từ Câu 1 đến Câu 6.
  2. *Lệnh chuẩn LaTeX:* Đặt `\setcounter{ex}{0}` ngay sau tiêu đề/hướng dẫn của PHẦN II và PHẦN III.
  3. *Tự động hóa toàn diện:* `composer_service.py` (`ensure_full_latex_document`, `sync_section_question_counts`) tự động phát hiện ranh giới phần và chèn `\setcounter{ex}{0}` nếu tài liệu chưa có; đồng thời bộ phân giải HTML preview cũng reset counter về 1.
  4. *Loại bỏ triệt để `\large`:* Bộ tiền xử lý tự động làm sạch mọi thẻ `\large`, `\Large`, `\LARGE` bên trong hoặc bao quanh tiêu đề phần, bảo toàn kích thước font chữ 12pt in đậm chuẩn mực `\noindent\textbf{PHẦN ...}` `\textit{...}`.

#### SRS-FEAT-04z: Kiến Trúc Biên Dịch Nhanh Đa Tầng Cho Soạn Thảo Đề Thi (Focus Mode, Instant Preview & Draft Mode)
- **Mô tả:** Giải quyết triệt để vấn đề thời gian chờ khi sửa đổi mã nguồn LaTeX bằng kiến trúc tăng tốc biên dịch đa tầng:
  1. *Tầng 1: Chế độ Xem trước Tức thì HTML/SVG (Instant Live HTML Preview - 0.2s):* Tự động chuyển đổi sang giao diện xem trước HTML/SVG qua `compile_latex_source_to_html` với bộ đệm Disk Cache TikZ theo mã MD5 (0.01s cho hình không đổi) và MathJax/KaTeX (0.05s).
  2. *Tầng 2: Biên dịch Nhanh Câu Đang Sửa / Phân Đoạn (Focus / Partial Question Quick Compile - 1.5s):* Cho phép giáo viên biên dịch riêng khối câu hỏi hiện tại tại vị trí con trỏ hoặc đoạn văn bản bôi đen thành PDF vector trong 1.0 - 1.8 giây qua nút bấm `⚡ BIÊN DỊCH CÂU NÀY` hoặc phím tắt `Ctrl+Shift+S`.
  3. *Tầng 3: Chế độ Biên dịch Nhanh Nháp (Draft Mode - 15s):* Giảm `samples=35` cho toàn bộ đồ thị TikZ khi bật cờ `draft_mode`, cắt giảm 70% thời gian biên dịch tài liệu lớn từ 65s xuống 15s.

#### SRS-FEAT-05: Kiểm soát Trùng lặp bằng AI Vector Embeddings
- **Mô tả:** Chống trùng lặp câu hỏi trong kho ngân hàng.
- **Xử lý:** Tính toán vector embedding (`text-embedding-3-small` hoặc `bge-m3`), so sánh Cosine Distance trong `pgvector`.
- **Logic:** Nếu Cosine Similarity $\ge 0.90$, hệ thống chặn lưu tự động và bật popup so sánh 2 câu hỏi.

---

### 4.3. Phân hệ Ma trận & Động cơ Sinh & Trộn Đề (Matrix & Safe Exam Engine)

#### SRS-FEAT-06: Bản Đặc tả Ma trận Đề thi 2D theo YCCĐ & 4 Dạng thức Câu hỏi (Interactive 2D Matrix Blueprint)
- **Mô tả:** Định nghĩa cấu trúc đề thi theo ma trận 2 chiều chuẩn hóa theo Thông tư 22/2021/TT-BGDĐT và Định dạng đề thi 2025 (Quyết định 764/QĐ-BGDĐT).
- **Yêu cầu kỹ thuật:**
  1. *Thiết kế Header Card & Công thái học Chuẩn Apple HIG:*
     - Loại bỏ hoàn toàn cụm nút Preset cứng khỏi thanh tiêu đề nhằm ngăn chặn hiện tượng tràn lề, co cụm và vỡ layout responsive.
     - Tái cấu trúc thanh tham số: Tên bài thi, Khối lớp & Môn học, Thời lượng thi, Thang điểm tổng (10.0đ), Nút Lưu & Ban hành Ma trận, Xuất bản PDF/CSV.
     - Chuyển nút **`Thêm dòng YCCĐ`** (`#btn-add-matrix-row`) về thanh công cụ của bảng ma trận, chuẩn hóa hiển thị duy nhất 1 icon plus tinh tế (khắc phục triệt để lỗi lặp `+ +`).
  2. *Lưới Ma trận 2D Tương tác & Quản lý Dòng động (Interactive 2D Grid & Dynamic Row Management):*
     - Dòng: Phân nhóm theo Mạch nội dung -> Yêu cầu cần đạt (YCCĐ) -> Dạng câu hỏi (Problem Archetype) -> Dạng thức câu hỏi (`SINGLE_CHOICE`, `TRUE_FALSE_GROUP`, `SHORT_ANSWER`, `ESSAY`).
     - Cột:
       * Cột 1: Mạch Nội dung & YCCĐ / Dạng bài (sticky left).
       * Cột 2: Dạng thức câu hỏi (Dropdown select: Trắc nghiệm 4 LC 0.25đ, Đúng/Sai 4 ý 1.0đ, Trả lời ngắn 0.5đ, Tự luận 1.0đ).
       * Cột 3: 1. Nhận biết (Biết).
       * Cột 4: 2. Thông hiểu (Hiểu).
       * Cột 5: 3. Vận dụng (VD).
       * Cột 6: Tổng câu (`biet + hieu + vandung`).
       * Cột 7: Tổng điểm (`Tổng câu * formatPoints`).
       * Cột 8: Thao tác (Xóa dòng).
     - Ô nhập liệu nhận thức: Cho phép nhập số lượng câu hỏi cần lấy cho từng ô (Biết, Hiểu, Vận dụng).
     - **Quản lý Dòng Động (Dynamic Rows) & Modal Thêm dòng:** Cho phép giáo viên bấm nút `Thêm dòng YCCĐ` mở Modal `#add-matrix-row-modal` để chọn Mạch nội dung, YCCĐ, Dạng bài, Dạng thức câu hỏi (`#modal-matrix-format`) và cơ số điểm nhận thức.
     - **Tính toán Điểm số Thời gian thực Theo Dạng thức Câu hỏi (Real-Time Scoring by Item Format):**
       * Điểm số từng dòng: `rowPoints = (Number(row.biet) + Number(row.hieu) + Number(row.vandung)) * MATRIX_FORMAT_POINTS[row.itemFormat]`.
       * Điểm từng mức độ nhận thức:
         + `totalPointsBiet = sum(row.biet * MATRIX_FORMAT_POINTS[row.itemFormat])`.
         + `totalPointsHieu = sum(row.hieu * MATRIX_FORMAT_POINTS[row.itemFormat])`.
         + `totalPointsVandung = sum(row.vandung * MATRIX_FORMAT_POINTS[row.itemFormat])`.
       * Điểm toàn ma trận được tính bằng tổng thực tế các dòng: `totalPoints = sum(rowPoints) = totalPointsBiet + totalPointsHieu + totalPointsVandung`.
       * Cân bằng chuẩn 10.0đ (loại bỏ hoàn toàn lỗi hiển thị lệch 11.0đ).
     - **Thanh đo lường Bloom Thực tế:** Tự động tính tỷ lệ phần trăm nhận thức chính xác:
       * `% Biết = round(totalBiet / grandItems * 100)`
       * `% Hiểu = round(totalHieu / grandItems * 100)`
       * `% Vận dụng = max(0, 100 - %Biết - %Hiểu)`
       * Tuyệt đối không hardcode tỷ lệ Bloom theo số câu cố định. Cảnh báo màu hổ phách nếu độ lệch vượt quá $\pm 5\%$ so với tỷ lệ chuẩn 40% Biết - 30% Hiểu - 30% Vận dụng.
  3. *Đối soát Tồn kho Thời gian thực & Cảnh báo Thiếu câu (Live Inventory Checker & Deficit Alert):*
     - Hệ thống kết nối cơ sở dữ liệu câu hỏi thực tế qua API `POST /api/v1/matrix/{id}/check-availability` hoặc đối soát trực tiếp với ngân hàng câu hỏi `state.itemBank`.
     - Với mỗi ô ma trận, đếm số câu hỏi có `status = 'APPROVED'` và `is_defective == False` khớp YCCĐ, mức độ và thể thức.
     - Hiển thị badge trực quan công thái học:
       * Đủ câu: Chip xanh lá `bg-emerald-50 text-emerald-700 border-emerald-200` (`Kho: X / Cần: Y`).
       * Thiếu câu: Chip cảnh báo đỏ `bg-rose-50 text-rose-700 border-rose-200 font-bold` (`Kho: X / Cần: Y (Thiếu Z câu)`) kèm icon cảnh báo.
     - Tổng hợp cảnh báo toàn ma trận: Hiển thị danh sách ô thiếu câu và tổng số câu cần bổ sung vào Ngân hàng.
  4. *API Quản lý & Xuất bản Bản đặc tả Ma trận:*
     - Hỗ trợ cả 2 tiền tố route song song: `/api/v1/matrix` và `/api/v1/matrices`.
     - `POST /api/v1/matrix`: Lưu và ban hành ma trận vào CSDL.
     - `GET /api/v1/matrix`: Danh sách các ma trận đã ban hành.
     - `GET /api/v1/matrix/{id}`: Chi tiết bản đặc tả ma trận.
     - `GET /api/v1/matrix/{id}/spec`: Xuất bản bản đặc tả ma trận đề thi ra 3 định dạng (`format=json`, `format=csv`, `format=pdf`):
       * `json`: Payload chi tiết cấu trúc ma trận và thống kê tồn kho.
       * `csv`: File bảng tính CSV có gắn mã ký tự UTF-8 BOM (`\ufeff`) hiển thị chuẩn tiếng Việt trên Excel.
       * `pdf`: Bản đặc tả in ấn A4 Portrait chuẩn quy cách Bộ GD&ĐT gồm Khung Ma trận phân bổ 2D và Bảng Đặc tả chi tiết từng câu hỏi.
     - Nút "Khởi Tạo Đề Thi Gốc & Sang Trộn Đề": Lưu ma trận hiện tại, gọi API sinh đề gốc từ ma trận và chuyển mượt sang Tab Trộn đề.

#### SRS-FEAT-07: Động cơ Sinh Đề Gốc theo Ràng buộc Ma trận (CSP Solver) & Đổi Câu Tương Đương (In-Place Item Swap)
- **Mô tả:** Tự động giải bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problem - CSP) để rút câu hỏi từ ngân hàng thành Đề Thi Gốc (Master Exam) và hỗ trợ giáo viên thẩm định, đổi câu hỏi linh hoạt.
- **Yêu cầu kỹ thuật:**
  1. *Thuật toán Rút Đề Gốc:*
     - Khớp chính xác từng ô ma trận theo YCCĐ, Dạng câu hỏi, Cấp độ nhận thức và Thể thức câu hỏi.
     - Kiểm tra tồn kho trước khi rút đề; ném ngoại lệ `InsufficientInventoryError` kèm báo cáo chi tiết nếu thiếu câu và cờ `allow_partial = False`.
     - Ràng buộc loại trừ: Loại bỏ các câu hỏi đã xuất hiện trong danh sách loại trừ hoặc các đề thi trong 30 ngày qua khi được kích hoạt.
     - Trọng số trắc lượng học (Psychometric Weighting): Ưu tiên câu hỏi có độ phân biệt tốt ($D \ge 0.3$) và độ khó cân đối ($p \approx 0.55$).
     - Đề gốc được lưu vào CSDL (`MasterExam` và `MasterExamItem`) phân theo 3 phần: Phần I (TN đơn), Phần II (Đúng/Sai), Phần III (Trả lời ngắn).
  2. *Hiển thị Đề thi Gốc Đầy đủ Cả 3 Thể thức Câu hỏi (Circular 32 & Decision 764):*
     - API `POST /api/v1/exams/generate` và `GET /api/v1/exams/{master_id}` trả về đầy đủ thân câu hỏi (`stem`), phương án trắc nghiệm (`options`), các khẳng định con (`sub_statements`), câu trả lời ngắn, mã YCCĐ, đồ thị TikZ SVG và KaTeX preview.
     - **Hiển thị trực quan 3 thể thức chuẩn:**
       * *Phần I - Trắc nghiệm 4 lựa chọn (SINGLE_CHOICE):* Lưới 4 phương án A, B, C, D; làm nổi bật phương án đúng bằng màu xanh lá (`bg-emerald-50 text-emerald-900 border-emerald-300 font-bold`); hiển thị badge `[Neo D]` nếu có mỏ neo vị trí.
       * *Phần II - Trắc nghiệm Đúng/Sai (TRUE_FALSE_GROUP):* 4 khẳng định con a, b, c, d với nhãn rõ nét `[ĐÚNG]` (xanh lá) hoặc `[SAI]` (đỏ) kèm barem chấm bậc thang QĐ 764 (1 ý = 0.1đ, 2 ý = 0.25đ, 3 ý = 0.5đ, 4 ý = 1.0đ).
       * *Phần III - Trắc nghiệm Trả lời ngắn (SHORT_ANSWER):* Hộp đáp số nổi bật (`Đáp án: <giá trị số>`) với định dạng số chuẩn và barem 0.5đ/câu.
     - Hiển thị badge Option Anchor nếu câu hỏi chứa phương án phụ thuộc vị trí.
  3. *Động cơ Đổi Câu hỏi Khác (In-Place Question Swap Engine):*
     - `GET /api/v1/exams/{master_id}/items/{item_id}/replacement-candidates`: Tìm kiếm các câu hỏi thay thế tiềm năng từ CSDL Question Bank:
       * Cùng mã YCCĐ (`learning_outcome_id`).
       * Cùng mức độ nhận thức (`cognitive_level`).
       * Cùng thể thức câu hỏi (`item_format`).
       * Trạng thái `status = 'APPROVED'` và `is_defective == False`.
       * Loại trừ tất cả các câu hỏi đang có mặt trong đề gốc.
     - Nút "Đổi câu khác" công thái học (hover mượt mà, scale 0.97, icon `refresh-cw`). Modal đổi câu hỗ trợ xem trước đầy đủ cả 3 thể thức của các ứng viên trước khi giáo viên xác nhận chọn.
     - `POST /api/v1/exams/{master_id}/items/{item_id}/swap`: Thay thế câu hỏi chỉ định trong đề gốc bằng câu hỏi mới; tự động xóa các mã đề hoán vị cũ (`ExamVariant`) để yêu cầu trộn lại, bảo toàn tính nhất quán tuyệt đối.
  4. *Thanh Công Cụ Nguồn Đề Thi Gốc & Nhập từ Ma Trận Khảo Thí (Master Exam Source Toolbar):*
     - Bố trí trực tiếp ở đầu tab `#tab-shuffler` ngay dưới thanh tiến trình:
       * *Chọn Đề Gốc Đã Có:* Dropdown danh sách các đề thi gốc đã lưu trong hệ thống (`GET /api/v1/exams`). Khi người dùng chọn, tải thông tin và câu hỏi tương ứng.
       * *Tạo Đề Gốc từ Ma Trận Khảo Thí:* Dropdown danh sách ma trận (`GET /api/v1/matrix`) kèm nút bấm **`⚡ Sinh Đề Gốc từ Ma Trận Này`** (`POST /api/v1/exams/generate`), cho phép sinh đề gốc trực tiếp từ phân hệ Trộn Đề mà không cần thao tác trung gian.
       * *Đồng bộ Ma Trận Hiện Tại:* Nút bấm **`🔄 Đồng bộ từ Ma trận hiện tại`** cho phép đồng bộ ngay cấu hình ma trận đang mở trong Matrix Studio.
       * *Thẻ Thông Tin Tổng Quan (Meta Bar):* Hiển thị trực quan Tên đề thi, Môn học, Khối lớp, Thời gian làm bài, Tổng số câu hỏi, Thang điểm 10.0đ và cơ cấu 3 phần.
     - **Hiển thị Mã đề Hoán vị Đầy đủ 3 Thể thức (Variant View):**
       * Khi xem các mã đề hoán vị (101, 102, 103, 104), hệ thống hiển thị chính xác toàn bộ nội dung của cả 3 thể thức theo thứ tự hoán vị của từng mã đề.
     - **Bảng Ma Trận Đáp Án Đối Chiếu (Answer Key Matrix):**
       * Lập bảng so sánh đáp án đối chiếu giữa Đề Gốc và 4 mã đề hoán vị: hiển thị ký tự (A, B, C, D) cho Phần I, chuỗi 4 khẳng định Đ/S cho Phần II, và giá trị số cho Phần III; kèm cột trạng thái mỏ neo Option Anchor.

#### SRS-FEAT-08: Thuật toán Trộn Đề & Hoán vị Mã đề An toàn (Safe Shuffling Engine)
- **Mô tả:** Sinh ra 4 mã đề hoán vị chuẩn (101, 102, 103, 104) từ Đề thi Gốc, tuân thủ nghiêm ngặt 4 nguyên tắc khảo thí an toàn.
- **4 Nguyên tắc An toàn Tuyệt đối:**
  1. **Section Integrity (Bảo toàn phân đoạn):** Chỉ hoán vị câu hỏi trong cùng một Phần / Thể thức (Phần I chỉ đảo trong Phần I; Phần II chỉ đảo trong Phần II; Phần III chỉ đảo trong Phần III).
  2. **Passage Integrity (Bảo toàn câu hỏi chùm / ngữ liệu):** Ngữ liệu bài đọc chung và các câu hỏi con đi kèm được gom thành một khối nguyên tử (Atomic Block); khi hoán vị, toàn bộ khối nguyên tử di chuyển cùng nhau; các câu hỏi con luôn nằm liền kề ngay sau ngữ liệu.
  3. **Option Anchor Rule (Khóa mỏ neo phương án):** Tự động phát hiện phương án có `is_fixed = True` hoặc chứa từ khóa mỏ neo vị trí ("Cả A và B", "Cả hai đáp án", "Tất cả các đáp án trên", "Tất cả các ý trên", "Không có đáp án nào"...). **BẮT BUỘC KHÓA CỐ ĐỊNH phương án này tại vị trí cuối cùng (Vị trí D)** trong mọi mã đề hoán vị; chỉ hoán vị tự do các phương án còn lại (A, B, C). Đảm bảo tỷ lệ xác minh Option Anchor Rule đạt 100%.
  4. **Key Matrix Generator (Ma trận đáp án đối chiếu):** Tự động lập bảng ma trận đối chiếu đáp án chéo giữa đề gốc và 4 mã đề hoán vị (cho cả 3 thể thức: ký tự đáp án cho Phần I, chuỗi đúng/sai cho Phần II, giá trị số cho Phần III).
- **Xem trước Mã đề & Đóng gói Xuất bản Ấn phẩm Thuần Vector PDF LaTeX (Tectonic XeTeX Engine):**
  - Tab xem trước từng mã đề (Mã 101, 102, 103, 104) với huy hiệu xác minh Option Anchor Rule đạt 100%.
  - Bảng ma trận đáp án tổng hợp (Answer Key Matrix Table).
  - **Xuất Bản Thuần Vector PDF LaTeX Chuẩn Quốc Gia (Tectonic XeTeX Engine):**
    * Loại bỏ hoàn toàn engine PDF đơn giản/ReportLab gây lỗi font tiếng Việt và công thức text thô, thay thế 100% bằng kiến trúc biên dịch LaTeX thuần túy chuẩn Quốc gia (`ex_test.sty` v3.3) qua Tectonic XeTeX Engine (kết hợp Chromium CMU Serif vector fallback) — đồng nhất tuyệt đối với phân hệ Soạn đề (`/composer`).
    * Mã nguồn LaTeX được tổng hợp tự động (`generate_variant_latex`):
      - Header 2 cột canonical cân đối: `\noindent`, `\begin{minipage}[t]{0.38\textwidth}\centering ... \end{minipage}`, `\hfill`, `\begin{minipage}[t]{0.58\textwidth}\centering ... \end{minipage}` (tuyệt đối không bọc ngoài bằng `\begin{center}`).
      - Dòng thông tin thí sinh `Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \framebox{\textbf{Mã đề: ...}}` và đường kẻ đơn duy nhất `\noindent
ule{\textwidth}{0.5pt}`.
      - Phần I: `\choice` 4 phương án hoán vị an toàn, làm sạch nhãn tiền tố thừa.
      - Phần II: `\choiceTF[1]` BẮT BUỘC bọc từng khẳng định con trong cặp ngoặc nhọn `{{\True ...}}` hoặc `{{...}}`, tự động padding đủ 4 khẳng định, kèm `\setcounter{ex}{0}` reset bộ đếm về 1.
      - Phần III: `\shortans` kèm `\setcounter{ex}{0}` reset bộ đếm về 1.
      - Tích hợp hàm làm sạch `sanitize_latex_for_xetex`: Tự động tìm và escape toàn bộ ký tự gạch dưới `_` nằm ngoài chế độ toán học thành `\_`, bảo toàn nguyên vẹn cú pháp subscript `$x_1$` trong math mode và các khối TikZ, triệt tiêu vĩnh viễn lỗi biên dịch `Missing $ inserted`.
    * Tải file PDF độc lập cho từng mã đề (`GET /api/v1/exams/{master_id}/export-pdf?variant_code={code}`): Kết xuất file `De_Thi_Ma_{code}.pdf` chuẩn Vector PDF LaTeX sắc nét.
    * Tải trọn gói ấn phẩm đề thi (.ZIP) (`GET /api/v1/exams/{master_id}/export-zip?format=pdf`): Đóng gói đầy đủ `De_{code}.pdf` (chế độ `[dethi]`), `LoiGiai_{code}.pdf` (chế độ `[loigiai]` với barem chấm bậc thang trong `\begin{loigiai}` và `\begin{itemchoice}`), `BangDapAn_TongHop.pdf`, `BangDapAn_TongHop.csv` (UTF-8 BOM), và `Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`.

---

### 4.4. Phân hệ Xuất bản & Đánh giá Khảo thí (Publisher & Analytics)

#### SRS-FEAT-09: Xuất bản Đề thi Word (.docx) Chuẩn Mẫu In & MathType OLE
- **Mô tả:** Tạo file Word chuẩn A4 dọc (210 x 297 mm, lề 1.5 - 1.8 cm) chuẩn quy cách Bộ GD&ĐT.
- **Yêu cầu kỹ thuật:**
  - Header chuẩn trường/kỳ thi/mã đề/bảng phách.
  - Công thức Toán được nhúng dạng **MathType 7.0 OLE Object Vector WMF** (`image/x-wmf` với APM header, CLSID `{0002CE03-0000-0000-C000-000000000046}`, ProgID `Equation.DSMT4`, stream `Equation Native` chứa MTEF v5 DSMT7 và bản ghi `TeX Input Language`). Lọc sạch các ký tự vô hình MathML (`\u2061` ApplyFunction...), chuẩn hóa embellishment vectơ (`\vec`, `\overrightarrow`), áp dụng typeface `0x82` bảo toàn toàn bộ dấu ngoặc `[`, `]`, `(`, `)`, `{`, `}` khi mở MathType, căn thẳng hàng chân dòng (baseline alignment qua `w:position` khớp chuẩn xác theo `depth_pt` của WMF), tự động nâng cấp phân số sang `\dfrac` (cỡ chữ 11pt đầy đủ cho tử và mẫu), chuẩn hóa khoảng cách ký tự (kerning/spacing chuẩn MathType: giãn cách toán tử `=`, `+`, `-`, đệm giữa các nhân tử kề nhau, hỗ trợ ký hiệu đạo hàm `f'(x)` chuẩn Symbol `0xa2`), bảo toàn và dựng vector đa giác cho các dấu ngoặc co giãn (`\left`, `\right` ngoặc đơn, ngoặc vuông, ngoặc nhọn), đệm kerning chữ nghiêng tránh dính dấu ngoặc (`f(x)` -> `f\,(x)`), chuẩn hóa tập số `\mathbb{R}, \mathbb{Q}, \mathbb{Z}` sang Times New Roman Bold đứng, tắt gạch chân đỏ kiểm tra chính tả của Word (`w:hideSpellingErrors`, `w:noProof`), **cho phép click đúp mở MathType 7 để chỉnh sửa trực tiếp 2 chiều không lỗi**, hoặc định dạng **OMML native (`<m:oMath>`)**.
  - **100% Vector WMF:** Toàn bộ công thức toán học được chuẩn hóa tiền xử lý qua MathTextParser (chế độ toán `$..$` ưu tiên, quy chuẩn tên hàm `\sin`, `\cos`, `\tan`, `\cot` thẳng đứng Upright và biến số in nghiêng Italic, xử lý `\setminus`, `\mid`, `\mathbb` thành glyphs chuẩn), loại bỏ 100% fallback raster DIB mờ hạt và triệt tiêu lỗi hiển thị dấu `?`.
  - Tự động phát hiện và chuyển đổi mảng bảng số liệu ghép nhóm `\begin{array}` sang bảng Microsoft Word `<w:tbl>`, loại bỏ hiện tượng ô đen khi xuất sang PDF.
  - Đi kèm file hướng dẫn giải chi tiết và phiếu soi đáp án OMR.

#### SRS-FEAT-10: Thống kê Khảo thí Hậu kiểm (Item Psychometrics)
- **Mô tả:** Tự động tính toán các chỉ số chất lượng câu hỏi khi có điểm thi:
  - Độ khó thực nghiệm: $p = \frac{\text{Số học sinh đúng}}{\text{Tổng số học sinh dự thi}}$.
  - Độ phân biệt: $D = P_H - P_L$ (Nhóm $27\%$ điểm cao trừ nhóm $27\%$ điểm thấp).
  - Cảnh báo các câu hỏi lỗi ($D < 0.2$) để loại khỏi ngân hàng.

#### SRS-FEAT-11: Hệ Thống Xác Thực & Quản Lý Danh Tính Người Dùng (Authentication, JWT & OAuth)
- **Mô tả:** Cung cấp hệ thống đăng ký, đăng nhập an toàn bảo vệ tài nguyên đề thi và ngân hàng câu hỏi, phân quyền người dùng theo vai trò RBAC (Role-Based Access Control).
- **Yêu cầu kỹ thuật:**
  1. *Thực thể `User` (`backend/models.py`):* Các trường bắt buộc gồm `id` (UUIDv4), `email` (unique, index), `hashed_password` (nullable cho tài khoản mạng xã hội), `full_name`, `role` (`ADMIN`, `TEACHER`, `STUDENT`), `avatar_url`, `oauth_provider` (`local`, `google`, `github`), `oauth_id`, `is_active` (boolean default True), `created_at`, `updated_at`.
  2. *Mật khẩu An toàn:* Áp dụng thuật toán băm chuẩn PBKDF2-HMAC-SHA256 với 600.000 vòng lặp và muối ngẫu nhiên (salt 32 bytes) thông qua thư viện chuẩn Python `hashlib`, không phụ thuộc thư viện biên dịch C bên ngoài.
  3. *Mã hóa Token JWT HS256:* Sinh và kiểm tra JWT an toàn với thuật toán HS256, thời hạn sống 7 ngày (86.400 * 7 giây), payload chuẩn chứa `sub` (User ID), `email`, `role`, `name`, `exp`. Tích hợp dependency `get_current_user` và `get_current_active_user` bảo vệ các route nhạy cảm.
  4. *API Router Xác thực (`backend/routers/auth.py`):*
     - `POST /api/v1/auth/register`: Đăng ký tài khoản mới với email, mật khẩu (tối thiểu 6 ký tự), họ tên và vai trò (`TEACHER` / `STUDENT`).
     - `POST /api/v1/auth/login`: Xác thực thông tin đăng nhập, trả về `access_token`, `token_type: "bearer"` và thông tin hồ sơ `user`.
     - `GET /api/v1/auth/me`: Truy vấn thông tin người dùng hiện tại dựa trên header `Authorization: Bearer <token>`.
     - `POST /api/v1/auth/oauth/google` & `POST /api/v1/auth/oauth/github`: Xử lý đăng nhập mạng xã hội OAuth 2.0 (Google, GitHub), tự động cấp phát hoặc liên kết tài khoản tương ứng.
     - `POST /api/v1/auth/logout`: Đăng xuất và dọn dẹp phiên làm việc.
  5. *Giao diện Apple HIG & Quản lý Trạng thái:*
     - Header Navbar: Hiển thị cặp nút `[Đăng nhập]` và `[Đăng ký]` khi chưa đăng nhập; hiển thị Avatar, Tên, Role badge và Menu popup Tài khoản kèm nút `Đăng xuất` khi đã đăng nhập.
     - Modal Xác thực (`#auth-modal`): Chuyển đổi mượt mà giữa Tab Đăng nhập và Tab Đăng ký; nút đăng nhập nhanh tài khoản giáo viên/admin thử nghiệm; nút OAuth Google và GitHub trực quan.
     - Lưu trữ Token tại `localStorage.getItem('quesy_auth_token')`, tự động đính kèm vào mọi request API gửi tới backend.

#### SRS-FEAT-12: Phân Hệ Ngân Hàng Câu Hỏi Khảo Thí Toàn Diện (Item Bank Full CRUD, 6-Tier Cascade TT 32, Modals, Import/Export & Badge Sync)
- **Mô tả:** Phân hệ quản lý ngân hàng câu hỏi chuẩn hóa toàn diện đáp ứng đầy đủ Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT.
- **Yêu cầu kỹ thuật:**
  1. *Bộ Lọc Cây Kiến Thức 6 Tầng Cascading:* 
     - Lọc phân cấp tuần tự: Cấp học / Khối lớp (`grade`) $
ightarrow$ Môn học (`subject`) $
ightarrow$ Mạch nội dung TT 32 (`strand`) $
ightarrow$ Chủ đề (`topic`) $
ightarrow$ Bài học (`lesson`) $
ightarrow$ Yêu cầu cần đạt (`yccd`).
     - Khi chọn cấp cha, các dropdown cấp con tự động cập nhật danh mục tương ứng.
  2. *Bộ Lọc Thứ Cấp Đa Chiều:*
     - Dạng câu hỏi (Problem Archetype), Mức độ nhận thức (Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao), Thể thức khảo thí (Trắc nghiệm đơn, Đúng/Sai 4 ý, Trả lời ngắn), Tìm kiếm từ khóa theo thân câu hỏi hoặc mã YCCĐ với cơ chế debounce 300ms.
  3. *Hệ thống CRUD & Modals Chuẩn Apple HIG:*
     - **Modal Thêm Mới (+ Thêm thủ công - `#question-create-modal`):** Hỗ trợ đủ 3 thể thức QĐ 764, công cụ chèn nhanh ký hiệu toán học, live KaTeX preview, chọn mức độ nhận thức, mã YCCĐ, đáp án đúng (radio chọn đáp án đúng cho MCQ, switch Đúng/Sai từng ý cho TF, ô nhập số và dung sai cho Short Answer), lời giải chi tiết. Tích hợp nút kiểm tra trùng lặp AI và gợi ý tag AI trước khi lưu.
     - **Modal Xem Chi Tiết (`#question-detail-modal`):** Hiển thị trực quan toàn bộ thân câu hỏi, công thức toán KaTeX, đồ thị TikZ SVG, bảng biến thiên, các phương án lựa chọn, barem tính điểm bậc thang QĐ 764 (0.1đ - 0.25đ - 0.5đ - 1.0đ), cây phân loại 6 tầng và chỉ số thống kê $p, D$.
     - **Modal Sửa Câu Hỏi (`#question-edit-modal`):** Tải đầy đủ thông tin câu hỏi hiện tại, cho phép chỉnh sửa nội dung, phương án, khẳng định đúng/sai, dung sai, YCCĐ, cập nhật tức thì vào CSDL qua `PUT /api/v1/questions/{id}`.
     - **Chức Năng Xóa Câu Hỏi:** Hộp thoại xác nhận an toàn, thực hiện xóa cascade các options và sub-statements liên quan qua `DELETE /api/v1/questions/{id}`, tự động làm mới giao diện và cập nhật huy hiệu số lượng.
  4. *Xuất & Nhập Dữ Liệu Ngân Hàng:*
     - **Xuất Dữ Liệu (`POST /api/v1/questions/export`):** Xuất toàn bộ hoặc danh sách câu hỏi đã lọc ra:
       * PDF Vector: Định dạng A4 chuẩn in ấn, font CMU Serif/Times, chia 2 cột đối xứng hoặc 1 cột rõ ràng kèm đáp án và lời giải.
       * CSV UTF-8 BOM: Tương thích 100% Microsoft Excel tiếng Việt trên Windows (không lỗi font mojibake).
       * LaTeX `.tex`: Mã nguồn chuẩn gói lệnh `ex_test.sty` với các khối `\begin{ex}` sẵn sàng biên dịch.
     - **Nhập Dữ Liệu (`POST /api/v1/questions/import`):** Nhập câu hỏi từ tệp văn bản hoặc dán trực tiếp mã LaTeX / JSON, tự động bóc tách các câu hỏi, kiểm tra tính hợp lệ và thêm vào ngân hàng.
  5. *Đồng Bộ Huy Hiệu Số Lượng (#bank-count-badge):* Badge đếm số lượng câu hỏi trên thanh điều hướng (`#bank-count-badge`) luôn tự động đồng bộ theo thời gian thực với tổng số câu hỏi thực tế trong CSDL sau mỗi thao tác Thêm, Sửa, Xóa, Nhập, hoặc Lưu từ Composer.

#### SRS-FEAT-13: Nút Chuyên Biệt "LƯU VÀO NGÂN HÀNG" & Động Cơ Trích Xuất Đa Thể Thức Từ Soạn Đề Composer Vào Ngân Hàng
- **Mô tả:** Trong phân hệ Soạn đề (`/composer`), tích hợp nút bấm chuyên biệt nổi bật **`📥 LƯU VÀO NGÂN HÀNG`** trực tiếp trên thanh công cụ và nâng cấp toàn diện API `POST /api/v1/composer/save-to-bank`.
- **Yêu cầu kỹ thuật:**
  1. *Nút Bấm Chuyên Biệt:* Neo trực tiếp trên thanh công cụ của Editor cạnh menu Xuất file, biểu tượng database nổi bật màu ngọc emerald hoặc gradient xanh Apple, kích hoạt thao tác lưu 1-click mà không cần mở dropdown ẩn.
  2. *Động Cơ Bóc Tách Đa Thể Thức:*
     - Hỗ trợ toàn diện cú pháp gói lệnh quốc gia `ex_test.sty` (`\begin{ex} ... \end{ex}`) và cú pháp truyền thống (`\textbf{Câu X.}`).
     - Trích xuất chính xác 3 thể thức câu hỏi:
       * Phần I: Trắc nghiệm đơn `\choice{A}{B}{C}{D}` (phát hiện cờ `\True` để gán `is_correct = True`).
       * Phần II: Đúng/Sai 4 khẳng định `\choiceTF[1]{a}{b}{c}{d}` (phát hiện cờ `\True` để gán `is_true = True` cho từng khẳng định độc lập).
       * Phần III: Trả lời ngắn `\shortans{giá_trị}` hoặc `\SA{giá_trị}` (lưu đáp án ngắn và dung sai).
     - Giữ nguyên vẹn thân câu hỏi (stem), các khối TikZ vẽ đồ thị, hình học không gian, và bảng biến thiên `tkz-tab`.
     - Bóc tách toàn vẹn khối lời giải chi tiết `\begin{loigiai} ... \end{loigiai}`.
  3. *Tự Động Gắn Nhãn AI & Xác Định Khối Lớp/Môn Học:*
     - Tự động nhận diện môn học và khối lớp từ tiêu đề văn bản (Header minipage).
     - Áp dụng `suggest_auto_tagging` để đề xuất mã YCCĐ theo Thông tư 32 cho các câu hỏi chưa được gán nhãn thủ công.
  4. *Phản Hồi Thống Kê Chi Tiết & Đồng Bộ Badge:*
     - Trả về payload JSON chi tiết số lượng câu hỏi lưu thành công theo từng thể thức (`counts: { single_choice, true_false, short_answer }`, `total_saved`).
     - Tự động cập nhật số đếm trên badge `#bank-count-badge` và làm mới dữ liệu tab Ngân hàng câu hỏi ngay lập tức.

#### SRS-FEAT-14: Cơ Chế Biên Dịch KaTeX Toàn Diện & Chuẩn Hóa Công Thức Toán Toàn Hệ Thống
- **Mô tả:** Triệt tiêu hoàn toàn lỗi hiển thị văn bản thô `$ ... $` của công thức toán học (`$y = \dfrac{x_1 - 1}{x + 1}$`, `$D = \mathbb{R} \setminus \{-1\}$`, `$x = -1$`, `$y = 1$`, `$x \neq -1$`) trên tất cả các thẻ câu hỏi và bảng ma trận.
- **Yêu cầu kỹ thuật:**
  1. *Expose Toàn Cục Hàm `renderKaTeX`:* Hàm `renderKaTeX(domElement)` phải được phơi ra phạm vi toàn cục (`window.renderKaTeX = renderKaTeX;` và `window.app.renderKaTeX = renderKaTeX;`), đảm bảo các lệnh gọi từ modal hoặc component bên ngoài luôn thực thi thành công.
  2. *Bao Phủ Điểm Kết Xuất KaTeX (Render Coverage):*
     - **Bảng Ngân hàng Câu hỏi (`renderItemBank`):** Gọi `renderKaTeX(container)` sau khi kết xuất danh sách card câu hỏi; đồng thời chuẩn hóa toàn bộ các lựa chọn `opt.content` và khẳng định `sub.content` qua `formatStemForDisplay(..., true)`.
     - **Lưới Ma trận Đề thi 2D (`renderMatrixGrid`):** Bắt buộc gọi `renderKaTeX(tbody)` sau khi nạp HTML bảng, đảm bảo các ký hiệu toán học trong tên Dạng bài (Problem Archetype, ví dụ: `$m$`, `$Oxyz$`, `$f(x)$`) được biên dịch sắc nét.
     - **Modal Xem Chi Tiết Câu Hỏi (`openQuestionDetailModal`):** Chuẩn hóa toàn diện thân câu hỏi (`formatStemForDisplay(q.stem)`), phương án trắc nghiệm (`formatStemForDisplay(cleanOptionAnswer(opt.content), true)`), khẳng định Đúng/Sai (`formatStemForDisplay(sub.content, true)`), kết quả trả lời ngắn, và lời giải chi tiết (`formatStemForDisplay(q.explanation)`). Gọi `renderKaTeX(modal)` ngay khi modal mở.
     - **Phân hệ Sinh & Trộn Đề (`renderMasterExam`, `renderVariantView`, `openSwapQuestionModal`):** Chuẩn hóa và biên dịch KaTeX cho toàn bộ các đề mục câu hỏi, phương án lựa chọn và các ý khẳng định con.
  3. *Chuẩn Hóa Ký Hiệu Toán Học Trước Khi Render:* Mọi nội dung câu hỏi và đáp án phải được tiền xử lý qua `formatStemForDisplay` và `formatLatexRules` (xử lý phân số `\dfrac`, tập hợp `\setminus`, số thập phân `{,}`, ngoặc kích thước động `\left`/`
ight`, và đồ thị TikZ vector SVG).

#### SRS-FEAT-15: Chuẩn Hóa Giao Diện Dropdown Box Chuẩn Apple HIG (.apple-select) & Triệt Tiêu Lỗi Font Monospace
- **Mô tả:** Đồng bộ hóa 100% diện mạo các ô chọn dropdown (Select boxes) trên toàn bộ ứng dụng theo tiêu chuẩn Apple Human Interface Guidelines (HIG), loại bỏ nút mũi tên xám thô mặc định của hệ điều hành và triệt tiêu lỗi font chữ monospace không đồng nhất.
- **Yêu cầu kỹ thuật:**
  1. *Xây Dựng Class CSS Chuẩn `.apple-select`:*
     - Triệt tiêu mũi tên mặc định của hệ điều hành: `appearance: none; -webkit-appearance: none; -moz-appearance: none;`.
     - Tích hợp biểu tượng mũi tên chevron vector SVG tinh tế màu slate-500 (`stroke='%2364748b'`) căn giữa lề phải (`right 0.75rem center`, kích thước `14px 14px`).
     - Bo góc mềm mại `border-radius: 12px`, padding công thái học `0.45rem 2.2rem 0.45rem 0.75rem`.
     - Đường viền mờ tinh tế `border: 1px solid rgba(0, 0, 0, 0.12)`, nền trắng `#ffffff`, đổ bóng vi mô `box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04)`.
     - Hiệu ứng Focus Apple Blue: Viền `#0071e3`, quầng hào quang nhẹ `box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15)`, chuyển động mượt mà `120ms cubic-bezier(0.2, 0, 0, 1)`.
  2. *Triệt Tiêu Hoàn Toàn Lỗi Font Monospace Trên Dropdown Bộ Lọc:*
     - Loại bỏ hoàn toàn class `font-mono` tại ô chọn **"6. Yêu cầu cần đạt"** (`#bank-filter-yccd`), đưa typography về font sans-serif chuẩn Apple (`-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", system-ui, sans-serif`), đồng nhất 100% với 5 box chọn còn lại.
  3. *Khắc Phục Lỗi Dropdown Thời Gian Làm Bài Ma Trận Đề (`#matrix-param-time`):*
     - Áp dụng class `apple-select w-full text-xs` cho ô chọn Thời gian làm bài (`#matrix-param-time`), đảm bảo chiều cao, góc bo 12px, padding và đường viền khớp hoàn hảo với các ô input text bên cạnh (`#matrix-param-name`).
  4. *Áp Dụng Đồng Bộ Toàn Hệ Thống:*
     - Toàn bộ 19 thẻ `<select>` tĩnh trong `frontend/index.html` và 3 thẻ `<select>` sinh động trong `frontend/static/app.js` (gồm dropdown dạng thức câu hỏi trong bảng ma trận 2D `updateMatrixRowFormat` và HITL taxonomy selectors) bắt buộc phải tích hợp class `.apple-select`.

---

## 5. THIẾT KẾ CƠ SỞ DỮ LIỆU LOGIC (LOGICAL DATA MODEL)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MÔ HÌNH THỰC THỂ CƠ SỞ DỮ LIỆU CỐT LÕI              │
└────────────────────────────────────────────────────────────────────────┘

  [subjects] 1 ──── N [grades] 1 ──── N [strands] (Mạch nội dung TT 32)
                                            │ 1
                                            ▼ N
                                      [topics] (Chủ đề / Chuyên đề)
                                            │ 1
                                            ▼ N
                                      [lessons] (Bài học)
                                            │ 1
                                            ▼ N
                                [learning_outcomes] (YCCĐ - TT 32)
                                            │ 1
                                            ▼ N
                                [problem_archetypes] (Dạng câu hỏi)
                                            │ 1
                                            ▼ N
                                       [questions]
                                            │
               ┌────────────────────────────┼───────────────────────────┐
               │ 1                          │ 1                         │ 1
               ▼ N                          ▼ N                         ▼ N
       [question_options]          [sub_questions]            [question_versions]
       (A, B, C, D)                (Câu hỏi con)              (Audit History)

  [exam_matrices] 1 ──── N [matrix_items] (Gắn liền với YCCĐ & Dạng bài)
         │ 1
         ▼ N
    [master_exams] 1 ──── N [master_exam_items] ──► [questions]
         │ 1
         ▼ N
   [exam_variants] (Mã đề 101, 102...)
         │ 1
         ▼ N
 [exam_variant_items] (Vị trí hoán vị & Mapping đáp án)
```

---

## 6. MA TRẬN PHÂN CHIA TRÁCH NHIỆM KỸ THUẬT (SYSTEM VERIFICATION MATRIX)

| Mã Tính năng | Phương thức Kiểm tra | Tiêu chuẩn Nghiệm thu Kỹ thuật (Acceptance Criteria) |
|:---|:---:|:---|
| **SRS-FEAT-01** | Test tự động + Đo kiểm | Bóc tách file DOCX/PDF 50 câu trong $< 180$ giây; tỷ lệ parse đúng công thức LaTeX $\ge 90\%$. |
| **SRS-FEAT-03** | Test chức năng | Cho phép tạo cây 6 tầng theo TT 32; **tuyệt đối không tồn tại trường "Bộ sách"** trong schema; liên kết chuẩn mã YCCĐ. |
| **SRS-FEAT-04** | Unit Test logic điểm | Chấm điểm câu Đúng/Sai 4 ý: Đúng 1 ý = 0.1đ; 2 ý = 0.25đ; 3 ý = 0.5đ; 4 ý = 1.0đ. |
| **SRS-FEAT-04e** | E2E Browser Test | Click chuột vào Compact Bar chân editor: con trỏ focus ô nhập text bình thường, không mở popup. Nhấn Enter hoặc nút mũi tên: mở bung full popup trợ lý và gửi prompt. |
| **SRS-FEAT-04f** | Test tự động + UI Test | Phản hồi sửa đổi từ AI trích xuất thành đối tượng `DiffSuggestion`, định vị đúng dòng trên editor, hiển thị banner so sánh đỏ/xanh; nhấn [Đồng ý] thay thế chuẩn xác dòng code và kích hoạt recompile; nhấn [Từ chối] hủy bỏ an toàn không làm biến đổi mã nguồn. |
| **SRS-FEAT-04p** | Test tự động + Blind Test | Bóc tách chính xác khối câu hỏi thứ N (`find_question_block`); prompt thay thế câu N liên kết đúng diff; nếu diff hợp lệ chuyển tới editor, nếu rỗng bảo tồn trọn vẹn code trong chat bubble kèm 3 nút hành động (không nuốt code). |
| **SRS-FEAT-04u** | E2E Browser Test + Test tự động | Kiểm thử upload tệp ảnh, paste ảnh clipboard (Ctrl+V) trên cả compact bar và chat popup; hiển thị thumbnail preview kèm nút xóa (✕); mở lightbox phóng to; gửi request `POST /api/v1/composer/chat` kèm payload `images: [data_url]`; AI phản hồi mã TikZ / `ex_test.sty` từ hình ảnh đề bài. |
| **SRS-FEAT-04v** | Test tự động + Đo kiểm | Tính toán timeout động $\text{calc\_timeout} \in [60, 240]$ dựa trên TikZ count và code length; socket timeout $\text{calc\_timeout} + 15$s; biên dịch trọn vẹn đề thi THPT Việt Đức 2026-2027 (~24k ký tự, 11 TikZ, 6 trang PDF) thành công không bị timeout 504; AI Copilot chẩn đoán lỗi timeout và gợi ý diff `samples=50` chính xác. |
| **SRS-FEAT-05** | Test tích hợp | Câu hỏi có cosine similarity $\ge 0.90$ phải kích hoạt chặn lưu và hiển thị modal cảnh báo trùng lặp. |
| **SRS-FEAT-08** | Unit Test thuật toán | Chạy 1.000 lần sinh mã đề hoán vị: $0\%$ câu hỏi chùm bị tách rời; $0\%$ phương án có cờ `is_fixed` bị đảo khỏi vị trí cố định. |
| **SRS-FEAT-09** | Thẩm định file đầu ra | Mở file `.docx` trên Microsoft Word: công thức hiển thị dạng MathType 7.0 OLE Vector WMF nét căng tuyệt đối, click đúp mở MathType 7 sửa được trực tiếp; bảng số liệu dạng native table không bị lỗi đen khi xuất PDF; khổ A4 dọc chuẩn. |
| **SRS-FEAT-11** | Test tự động + UI Test | Đăng ký, đăng nhập tài khoản mật khẩu (PBKDF2/SHA256 băm an toàn); cấp JWT HS256 chuẩn; hỗ trợ OAuth Google/GitHub; phân quyền RBAC (`TEACHER`, `ADMIN`, `STUDENT`); lưu token `quesy_auth_token` và đồng bộ header Authorization. |
| **SRS-FEAT-12** | Test chức năng + UI Test | Thực thi đầy đủ CRUD câu hỏi; mở Modal Thêm mới, Modal Chi tiết, Modal Sửa, Xóa câu hỏi; lọc 6 tầng TT 32 cascading chuẩn; xuất danh sách ra PDF vector / CSV UTF-8 BOM / LaTeX; nhập câu hỏi; cập nhật ngay số lượng badge `#bank-count-badge`. |
| **SRS-FEAT-13** | Test tích hợp + E2E | Nút chuyên biệt `📥 LƯU VÀO NGÂN HÀNG` trên toolbar Composer trích xuất trọn vẹn câu hỏi trắc nghiệm đơn, đúng/sai QĐ 764, trả lời ngắn, TikZ, BBT, lời giải chi tiết; tự động gắn tag YCCĐ AI; trả về chi tiết số lượng câu theo từng thể thức và cập nhật tức thì `#bank-count-badge`. |
| **SRS-FEAT-14** | E2E Browser Test + UI Test | 100% công thức toán học (`$y = \dfrac{x_1 - 1}{x + 1}$`, `$D = \mathbb{R} \setminus \{-1\}$`, `$x = -1$`, `$y = 1$`, `$x \neq -1$`) trên thẻ câu hỏi Ngân hàng, Ma trận đề, Modal Chi tiết, Đề gốc và Đề hoán vị được biên dịch KaTeX sắc nét; không còn sót bất kỳ chuỗi văn bản thô `$ ... $` nào. |
| **SRS-FEAT-15** | UI Audit + Cross-browser Test | 100% dropdown select áp dụng class `.apple-select` với icon chevron SVG slate-500, bo góc 12px, không còn mũi tên xám thô OS; ô chọn `#matrix-param-time` đồng bộ kích thước và viền với các input bên cạnh; ô `#bank-filter-yccd` xóa sạch class `font-mono` và hiển thị font sans-serif đồng nhất. |
| **SRS-VERIF-CI** | Test CI Runner + Pre-Commit Gate | 100% test cases vượt qua trên môi trường CI runner (`pytest`, syntax check) trước khi commit; tuân thủ nghiêm ngặt nguyên tắc Strict CI Isolation (chỉ duy nhất Sub-Agent CI đọc/ghi CI, cấm các sub-agent khác truy cập đọc); vòng lặp sửa lỗi CI loop lặp lại cho đến khi pass mới commit. |
