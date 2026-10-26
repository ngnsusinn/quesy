# TÀI LIỆU YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS SPECIFICATION - SRS)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-SRS-01  
- **Phiên bản:** 3.1 (Phân hệ Soạn đề Tinh gọn Không Preamble Canonical Preamble Injection, Động cơ Thay thế Câu hỏi Thông minh Question Replacement Engine & Quy tắc Git Workflow Tuyệt đối Không Tự Động Tạo PR)  
- **Tiêu chuẩn kỹ thuật áp dụng:** IEEE Std 830-1998 / ISO/IEC/IEEE 29148  
- **Nhiệm vụ trọng tâm:** Đặc tả hệ thống số hóa đề thi tự động, phân hệ Soạn đề tinh gọn không cần khai báo preamble (Canonical Preamble Injection tự động nhúng fontspec, tikz, tkz-tab, tcolorbox, ex_test v3.3), bộ dựng đồ thị vector SVG (TikZ), chuẩn hóa công thức KaTeX, thuật toán trộn đề an toàn (Safe Shuffling Engine), MathJax engine, xuất bản ấn phẩm Word MathType 7.0 OLE Vector WMF / OMML, phân hệ Trợ lý Soạn thảo AI Copilot thông minh, và quy chuẩn quản trị phát triển Git.
- **Ngày phát hành:** 2026-10-24  
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
- **Quy chuẩn Git Commit & Push:** Mọi tác vụ phát triển, sửa lỗi và nâng cấp tính năng chỉ thực hiện `git commit` và `git push` lên nhánh remote repository.
- **TUYỆT ĐỐI KHÔNG TỰ ĐỘNG TẠO PULL REQUEST (`gh pr create`, API PR...)** hoặc tự động cập nhật vào Pull Request trừ khi Người dùng (User) có yêu cầu rõ ràng bằng lời nói (explicit user prompt). Mọi hành vi tự động tạo PR khi chưa có lệnh trực tiếp đều vi phạm quy chuẩn quản trị dự án.

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

### 4.3. Phân hệ Ma trận & Động cơ Sinh Đề (Matrix & Exam Engine)

#### SRS-FEAT-06: Bản Đặc tả Ma trận Đề thi theo YCCĐ (Test Blueprint)
- **Mô tả:** Định nghĩa cấu trúc đề thi theo ma trận 2 chiều:
  - Dòng: Danh sách Mạch nội dung $\rightarrow$ Yêu cầu cần đạt (YCCĐ) $\rightarrow$ Dạng câu hỏi.
  - Cột: 3 Mức độ nhận thức (Biết, Hiểu, Vận dụng) $\times$ Dạng thức câu hỏi.
  - Điểm số: Điểm quy định cho từng câu hỏi ở từng vị trí.

#### SRS-FEAT-07: Sinh Đề Gốc theo Ràng buộc (Constraint Satisfaction Solver)
- **Mô tả:** Tự động lấy câu hỏi từ ngân hàng thỏa mãn ma trận.
- **Ràng buộc:** Trạng thái câu hỏi là `APPROVED`; không nằm trong danh sách loại trừ (Exclusion list); đúng tỷ lệ YCCĐ và mức độ nhận thức.

#### SRS-FEAT-08: Thuật toán Trộn Đề & Hoán vị Mã đề An toàn (Safe Shuffling Engine)
- **Mô tả:** Sinh ra $N$ mã đề hoán vị (101, 102, 103, 104...) từ 1 đề gốc.
- **Quy tắc an toàn:**
  1. **Section Integrity:** Chỉ hoán vị câu hỏi trong cùng một Phần/Dạng thức (không trộn trắc nghiệm đơn sang phần đúng sai).
  2. **Passage Integrity:** Giữ nguyên cụm câu hỏi chùm; đoạn văn ngữ liệu luôn đi liền trước các câu con.
  3. **Option Anchor:** Nếu phương án có cờ `is_fixed = true` hoặc chứa nội dung nhạy cảm vị trí ("Cả A và B", "Tất cả các ý trên"), phương án này luôn bị khóa cố định ở vị trí cuối cùng (D).
  4. **Key Generator:** Tự động xuất ma trận hoán vị đáp án (Answer Key Matrix).

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
| **SRS-VERIF-CI** | Test CI Runner + Pre-Commit Gate | 100% test cases vượt qua trên môi trường CI runner (`pytest`, syntax check) trước khi commit; tuân thủ nghiêm ngặt nguyên tắc Strict CI Isolation (chỉ duy nhất Sub-Agent CI đọc/ghi CI, cấm các sub-agent khác truy cập đọc); vòng lặp sửa lỗi CI loop lặp lại cho đến khi pass mới commit. |
