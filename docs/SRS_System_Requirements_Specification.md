# TÀI LIỆU YÊU CẦU HỆ THỐNG (SYSTEM REQUIREMENTS SPECIFICATION - SRS)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-SRS-01  
- **Phiên bản:** 2.7 (Tập trung hoàn thiện MathType 7.0 DSMT7 Native Stream, 100% Vector WMF & Bảo toàn chỉnh sửa 2 chiều)  
- **Tiêu chuẩn kỹ thuật áp dụng:** IEEE Std 830-1998 / ISO/IEC/IEEE 29148  
- **Nhiệm vụ trọng tâm:** Đặc tả hệ thống số hóa đề thi tự động, bộ dựng đồ thị vector SVG (TikZ), chuẩn hóa công thức KaTeX, thuật toán trộn đề an toàn (Safe Shuffling Engine), MathJax engine và xuất bản ấn phẩm Word MathType 7.0 OLE Vector WMF / OMML.  
- **Ngày phát hành:** 2026-10-21  
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
- **Kỹ sư AI & Backend:** Xây dựng OCR pipeline, dịch vụ biên dịch TikZ SVG, MathJax Persistent Engine và thuật toán hoán vị an toàn.
- **Kỹ sư Frontend:** Phát triển giao diện Studio Hậu kiểm (HITL) cuộn đồng bộ, hiển thị đồ thị SVG và render KaTeX thời gian thực.
- **Kỹ sư QA/QC:** Xây dựng ma trận kiểm thử tự động và tiêu chuẩn nghiệm thu (55/55 automated tests).

### 1.4. Phạm vi Sản phẩm & Bài toán Giải quyết (Product Scope)
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
- **Mô tả:** Thay thế hoàn toàn phân hệ số hóa ảnh/OCR cũ bằng phân hệ **Soạn đề** (LaTeX Exam Writing Workspace) mô phỏng thiết kế của `Noctorium` kết hợp gói lệnh khảo thí quốc gia `ex_test.sty` (v3.3). Cung cấp không gian làm việc 2 cột tích hợp (Split View Workspace):
  1. *Cột bên trái:*
     - *Khung trên:* Trình soạn thảo mã nguồn LaTeX Dark mode (`#141824`, bảo toàn màu nền khi click con trỏ focus, thanh cuộn mượt mà không kẹt `overflow-y: scroll`) với toolbar `MỚI`, `THÊM ▾` (7 template chuẩn `ex_test`), phím tắt hoàn tác (Undo/Redo), dọn dẹp, sao chép, đánh số dòng và hiển thị vị trí con trỏ.
     - *Thanh Banner Gợi ý Sửa đổi (Inline Diff Banner):* Hiển thị trực tiếp số dòng cần sửa, tự động cuộn và bôi đen vị trí cần thay thế trên editor, hiển thị trực quan khối so sánh `- old_text` (đỏ) và `+ new_text` (xanh), cho phép duyệt nhanh với 2 nút bấm **`[Đồng ý]`** và **`[Từ chối]`**.
     - *Khung dưới:* Trợ lý Soạn thảo AI Copilot hỗ trợ sinh câu hỏi trắc nghiệm Phần I, Đúng/Sai Phần II (QĐ 764), Trả lời ngắn Phần III, bảng biến thiên `tkz-tab`, đồ thị TikZ `\immini`.
  2. *Cột bên phải:*
     - *Thanh công cụ:* Tab `ẢNH` và `LỊCH SỬ`, công tắc chuyển đổi `LỜI GIẢI` (tự động đảo giữa in đề thi `[dethi]` và in đáp án `[loigiai]`), menu `XUẤT FILE ▾` (PDF, TeX, Ngân hàng, Copy).
     - *Bản xem trước Live Preview:* Hiển thị trực tiếp trang PDF biên dịch sắc nét từ Tectonic XeTeX Engine (Docker trên host ARM) hoặc Chromium Headless.
     - *Chân trang (Footer):* Nút bấm thanh ngang toàn chiều rộng nổi bật màu xanh dương **`BIÊN DỊCH`** (`#0071e3`).
  3. *Lưu trữ tự động (Local Persistence):* Tự động lưu bản nháp văn bản, lịch sử hội thoại và lịch sử biên dịch vào `localStorage` của trình duyệt.
  4. *Tích hợp Ngân hàng Câu hỏi (1-Click Save to Bank):* Tự động bóc tách và trích xuất câu hỏi từ cả 2 cú pháp: gói lệnh `ex_test` (`\begin{ex}`) và cú pháp truyền thống (`\textbf{Câu X.}`) sang các bản ghi ngân hàng câu hỏi chuẩn hóa (`questions` table).

#### SRS-FEAT-04e: Thanh Nhập Prompt AI Thu Gọn ở Chân Editor (Compact Floating AI Prompt Bar)
- **Mô tả:** Cung cấp thanh nhập lệnh AI nhỏ gọn dạng viên thuốc (floating pill bar) neo tại chân khung soạn thảo (`bottom-7`, căn giữa `w-[92%] max-w-xl`, phong cách Apple Glassmorphism bo tròn viền bán trong suốt `#1c1c1f/95`), giữ không gian làm việc luôn tối giản và tập trung cao độ.
- **Hành vi tương tác và kích hoạt 2 trạng thái:**
  1. *Trạng thái Nhập liệu Cục bộ (In-place Typing):* Khi người dùng nhấp chuột vào thanh hoặc trường nhập văn bản (`#composer-compact-input`), hệ thống chỉ kích hoạt focus con trỏ để gõ văn bản bình thường (`cursor-text`), **tuyệt đối không tự động bung mở modal/popup trợ lý** nhằm loại bỏ hoàn toàn hiện tượng che khuất màn hình gây gián đoạn mạch soạn thảo.
  2. *Trạng thái Kích hoạt Mở rộng (Expansion & Dispatch Trigger):* Hệ thống chỉ mở bung toàn bộ giao diện Popup Trợ lý Soạn thảo (`composer-ai-popup`, độ cao mặc định 56%, có thể phóng to 78% hoặc 92%) khi xảy ra một trong hai điều kiện sau:
     - Người dùng nhấn phím **`Enter`** trong ô nhập liệu.
     - Người dùng nhấp chuột vào **Nút Gửi Mũi Tên Tròn** (`#composer-ai-compact-bar button` - icon `arrow-up`).
  3. *Chuyển tiếp Dữ liệu Liền mạch:* Khi được kích hoạt, chuỗi prompt trong thanh thu gọn được tự động chuyển vào ô chat của Popup Trợ lý, thanh thu gọn tạm thời ẩn đi, hiển thị chỉ báo AI đang phản hồi (`composer-typing-indicator`), và gửi yêu cầu bất đồng bộ đến endpoint `/api/v1/composer/chat`.
  4. *Menu Mẫu Lệnh Nhanh (Quick Actions Menu):* Biểu tượng dấu cộng `+` trên thanh compact mở menu ngữ cảnh cho phép chọn nhanh các tác vụ phổ biến: đổi cỡ chữ toàn tài liệu sang 12pt, tạo câu hỏi trắc nghiệm 4 lựa chọn, tạo câu hỏi Đúng/Sai 4 ý QĐ 764, vẽ bảng biến thiên `tkz-tab`, và kiểm tra/sửa cú pháp LaTeX.

#### SRS-FEAT-04f: Cơ Chế Trích Xuất & Hiển Thị Đề Xuất Sửa Đổi Trực Tiếp trên Editor (Smart Inline Diff Suggestion)
- **Mô tả:** Khi tương tác với Trợ lý Soạn thảo AI, mọi đề xuất điều chỉnh văn bản, thay thế tham số hoặc sửa đổi mã nguồn LaTeX đều được trích xuất thành đối tượng **`DiffSuggestion`** có cấu trúc, hiển thị trực quan ngay tại vị trí dòng mã nguồn cần thay đổi trên Editor thay vì ghi đè thô bạo hoặc lặp lại toàn bộ tài liệu dài dòng.
- **Luồng Xử Lý và Trích Xuất Diff Phía Backend (`composer.py`):**
  - AI Copilot được định hướng bằng System Prompt ép buộc chỉ trả về các khối thay đổi có cấu trúc kèm lời giải thích ngắn gọn bằng tiếng Việt.
  - Bộ bóc tách Diff Đa tầng (`extract_diff_from_text`) nhận diện tự động 5 định dạng đề xuất sửa:
    1. *Unified Diff Block:* Khối ````diff ... ```` chứa dòng trừ `- <old_line>` và dòng cộng `+ <new_line>`.
    2. *Search & Replace Block:* Chuẩn Aider/Open-Prism `<<<<<<< SEARCH ... ======= ... >>>>>>> REPLACE`.
    3. *Explicit OLD/NEW Block:* Định dạng nhãn `OLD: <text>` và `NEW: <text>`.
    4. *Heuristic Tham số Khảo thí:* Nhận diện yêu cầu đổi cỡ chữ (ví dụ: `11pt -> 12pt` tại `\documentclass`), chế độ lời giải (`[dethi] <-> [loigiai]`).
    5. *SequenceMatcher Diff:* So khớp mã khối mới với ngữ cảnh hiện tại bằng thuật toán so sánh chuỗi tương đối để trích xuất lát cắt thay thế tối thiểu.
  - Backend trả về payload `ChatResponse`:
    ```json
    {
      "reply": "Giải thích chi tiết về thay đổi...",
      "diff": {
        "action": "replace",
        "old_text": "\\documentclass[11pt,a4paper]{article}",
        "new_text": "\\documentclass[12pt,a4paper]{article}",
        "description": "Đổi cỡ chữ toàn tài liệu sang 12pt"
      }
    }
    ```
- **Hành vi Trực quan hóa & Thao tác trên Frontend Editor (`app.js`):**
  1. *Định vị & Cuộn dòng Tự động (Line Pinpointing & Auto-scroll):* Khi nhận được `diff`, client tìm kiếm chính xác vị trí của `old_text` trong bộ đệm LaTeX, xác định số thứ tự dòng (`lineNo`), tự động cuộn khung nhìn editor đến dòng đó (`scrollTop`), và kích hoạt bôi đen vùng chọn ký tự (`setSelectionRange`).
  2. *Banner Duyệt Diff Ngay trên Editor (`#composer-pending-diff-banner`):*
     - Huy hiệu nhận diện: Badge `GỢI Ý TẠI DÒNG [lineNo]` đi kèm mô tả ngắn gọn nội dung sửa đổi.
     - So sánh trực quan 2 màu: Dòng cũ cần xóa (`- old_text`) nền đỏ đậm `rose-950/70`, dòng mới cần thêm (`+ new_text`) nền xanh lục `emerald-950/70`.
     - Bộ đôi nút thao tác phê duyệt:
       - **`[Đồng ý]` (Accept):** Gọi hàm `applyPendingDiff()`, thực hiện thay thế chính xác dòng cũ bằng dòng mới trong biến trạng thái `this.currentLatex` và textarea, tự động kích hoạt biên dịch tức thì `compile(true)` để cập nhật Live PDF, hiển thị thông báo toast thành công và đóng banner diff.
       - **`[Từ chối]` (Reject):** Gọi hàm `rejectPendingDiff()`, đóng banner diff, đưa con trỏ về trạng thái soạn thảo thông thường mà không can thiệp hay làm biến đổi bất kỳ ký tự nào của mã nguồn.
  3. *Thẻ Diff Tương tác trong Lịch sử Chat:* Bên cạnh banner trên editor, tin nhắn phản hồi của AI trong khung chat cũng hiển thị thẻ Diff Card độc lập có đủ 2 nút `[Đồng ý]` / `[Từ chối]`, giúp giáo viên có thể xem lại và tái áp dụng đề xuất bất cứ lúc nào trong phiên làm việc.


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
| **SRS-FEAT-05** | Test tích hợp | Câu hỏi có cosine similarity $\ge 0.90$ phải kích hoạt chặn lưu và hiển thị modal cảnh báo trùng lặp. |
| **SRS-FEAT-08** | Unit Test thuật toán | Chạy 1.000 lần sinh mã đề hoán vị: $0\%$ câu hỏi chùm bị tách rời; $0\%$ phương án có cờ `is_fixed` bị đảo khỏi vị trí cố định. |
| **SRS-FEAT-09** | Thẩm định file đầu ra | Mở file `.docx` trên Microsoft Word: công thức hiển thị dạng MathType 7.0 OLE Vector WMF nét căng tuyệt đối, click đúp mở MathType 7 sửa được trực tiếp; bảng số liệu dạng native table không bị lỗi đen khi xuất PDF; khổ A4 dọc chuẩn. |
