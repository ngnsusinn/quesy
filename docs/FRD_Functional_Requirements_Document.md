# TÀI LIỆU ĐẶC TẢ CHỨC NĂNG (FUNCTIONAL REQUIREMENTS DOCUMENT - FRD)
**Dự án: Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-FRD-01  
- **Phiên bản:** 2.7 (Tập trung hoàn thiện MathType 7.0 DSMT7 Native Stream, 100% Vector WMF & Bảo toàn chỉnh sửa 2 chiều)  
- **Mục tiêu đặc tả:** Mô tả chi tiết hành vi dữ liệu, giao diện người dùng, điều kiện biên, API endpoints và quy tắc logic giải quyết các bài toán gõ lại đề, dựng đồ thị vector SVG, trộn đề an toàn và xuất bản in ấn.  
- **Ngày phát hành:** 2026-10-18  
- **Trạng thái:** Hoàn thành đặc tả chi tiết & Sẵn sàng vận hành  

---

## 1. TỔNG QUAN TÀI LIỆU

### 1.1. Mục đích
Tài liệu Đặc tả Chức năng (FRD) mô tả chi tiết luồng xử lý dữ liệu, giao diện người dùng, điều kiện biên, các API endpoints và quy tắc nghiệp vụ cho từng phân hệ trong hệ thống Quesy, giải quyết trực tiếp các khó khăn trong quy trình biên soạn và tổ chức kiểm tra đánh giá.

### 1.2. Danh mục Phân hệ Chức năng
- **MOD-01:** Phân hệ Tiếp nhận & Số hóa Đề thi bằng AI (AI Ingestion & Parsing)
- **MOD-02:** Phân hệ Studio Hậu kiểm Đối chiếu Song song (HITL Review Studio)
- **MOD-03:** Phân hệ Bộ Dựng Đồ Thị Vector SVG & Chuẩn Hóa Toán Học (TikZ & LaTeX Sanitizer)
- **MOD-04:** Phân hệ Ngân hàng Câu hỏi & Phân loại Dạng bài (Item Bank Management)
- **MOD-05:** Phân hệ Ma trận Đề thi & Rút đề theo Ràng buộc (Exam Matrix & Solver)
- **MOD-06:** Phân hệ Động cơ Trộn Mã đề An toàn (Safe Shuffling Engine)
- **MOD-07:** Phân hệ Xuất bản Đề thi Word OMML & In ấn (Publishing & Export Service)
- **MOD-08:** Phân hệ Chấm điểm Bậc thang & Quản lý Bảng điểm (Grade & Roster Management)

---

## 2. ĐẶC TẢ CHI TIẾT TỪNG PHÂN HỆ CHỨC NĂNG

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-01: PHÂN HỆ TIẾP NHẬN & SỐ HÓA ĐỀ THI BẰNG AI                     │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1. FR-01.1: Tải lên Tài liệu Đề thi (Document Upload)
- **Màn hình liên quan:** `SCR-UPLOAD`
- **Tác nhân:** Giáo viên, Tổ trưởng chuyên môn, Admin.
- **Dữ liệu đầu vào:**
  - File Đề thi: Định dạng `.docx`, `.doc`, `.pdf`, `.png`, `.jpg` ($\le 50$MB).
  - File Đáp án kèm theo (Tùy chọn): File đáp án rời hoặc tích hợp cuối đề.
  - Phân loại ban đầu: Môn học (Dropdown), Khối lớp (Dropdown) - **Không chọn bộ sách**.
- **Hành vi hệ thống:**
  1. Kiểm tra định dạng và dung lượng file hợp lệ.
  2. Tải file lên Object Storage (S3/MinIO): `uploads/{user_id}/{job_id}/source.ext`.
  3. Tạo bản ghi `ai_digitize_jobs` với trạng thái `PENDING`.
  4. Đẩy payload vào hàng đợi Redis Queue (`queue:ai_digitize`).
  5. Trả về `job_id` và ước lượng thời gian xử lý cho client.

### 2.2. FR-01.2: Pipeline Xử lý Bóc tách AI (AI Parsing Worker)
- **Tác nhân:** Background Worker Service (Python).
- **Quy trình xử lý:**
  1. **Bước 1 - Preprocessing:**
     - Nếu là DOCX/DOC: Quét toàn bộ OLE objects, trích xuất dòng nhị phân MathType MTEF và dịch trực tiếp sang mã LaTeX chuẩn (`$...$` inline, `$$...$$` block).
     - Nếu là PDF/Ảnh: Chuyển trang sang ảnh PNG 300 DPI, thực hiện cân bằng góc nghiêng (OpenCV Deskew) và khử bóng mờ (Binarization).
  2. **Bước 2 - Layout Segmentation:**
     - Tách Tiêu đề trường, Phần thi (Phần I, II, III), Nội dung câu, Phương án lựa chọn, Hình ảnh, Bảng biểu.
  3. **Bước 3 - Vision LLM Extraction & Auto-tagging:**
     - Gọi Multimodal LLM (Gemini 1.5 Flash / GPT-4o) kèm System Prompt ép khuôn JSON Schema.
     - Tự động nhận diện dạng câu hỏi: Trắc nghiệm 4 lựa chọn, Đúng/Sai 4 ý, Trả lời ngắn, Câu hỏi chùm.
     - **AI Gợi ý gán nhãn (Auto-tagging):** Phân tích ngữ cảnh câu hỏi, gợi ý Mạch nội dung, Chủ đề, Dạng câu hỏi, Mức độ nhận thức (Biết, Hiểu, Vận dụng), và mã **Yêu cầu cần đạt (YCCĐ)** tương ứng theo danh mục Thông tư 32.
  4. **Bước 4 - Auto Image Crop:**
     - Tự động cắt các vùng Bounding Box hình học, đồ thị, mạch điện, nén WebP và lưu vào S3: `assets/{job_id}/img_{uuid}.webp`.
     - Nhúng mã `[IMAGE:url]` vào thân câu hỏi.
  5. **Bước 5 - Key & Solution Matching:**
     - Quét bảng đáp án ở cuối đề, tự động map đáp án đúng vào thuộc tính `is_correct` của từng phương án.
  6. **Bước 6 - Hoàn tất:** Đổi trạng thái job sang `COMPLETED`, lưu JSON vào bảng tạm, bắn thông báo WebSocket tới Client.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-02: PHÂN HỆ STUDIO HẬU KIỂM ĐỐI CHIẾU SONG SONG (HITL STUDIO)      │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.3. FR-02.1: Không Gian Soạn Thảo Đề Thi Phân Tách 2 Cột (Noctorium & Open-Prism Split Layout)
- **Màn hình liên quan:** `SCR-COMPOSER-STUDIO`
- **Bố cục giao diện:**
  - **Cột bên trái (50%):**
    - *Khung trên:* Trình soạn thảo mã nguồn LaTeX (Dark mode) với toolbar `MỚI`, `GEMINI ▾`, `THÊM ▾` (7 template chuẩn `ex_test`), các phím tắt `Undo`, `Redo`, `Xóa`, `Copy`, đánh số dòng (gutter), và thanh trạng thái dòng/cột.
    - *Khung dưới:* Trợ lý Soạn thảo AI (Gemini Copilot) được bố trí ngay bên dưới khung soạn thảo với thanh gợi ý lệnh nhanh, hội thoại chat tương tác, 1-click chèn/thay thế mã và khung nhập liệu câu hỏi.
  - **Cột bên phải (50%):**
    - *Thanh công cụ trên (Light mode):* Hai tab điều hướng `ẢNH` và `LỊCH SỬ`, công tắc chuyển đổi `LỜI GIẢI` (tự động chuyển đổi giữa chế độ in đề thi `[dethi]` và in lời giải `[loigiai]`), menu `XUẤT FILE ▾` (tải PDF, tải TeX, lưu Ngân hàng, sao chép mã).
    - *Khung giữa:* Bản xem trước PDF Trực tiếp (Live Preview) hiển thị PDF biên dịch sắc nét từ Tectonic XeTeX engine hoặc danh sách lịch sử các phiên bản.
    - *Chân trang (Footer):* Nút bấm toàn chiều rộng nổi bật màu đỏ đô **`BIÊN DỊCH`** kích hoạt biên dịch tài liệu tức thì.

### 2.4. FR-02.2: Tự Động Biên Dịch, Lưu Trữ Cục Bộ & Xuất Bản Đề Thi
- **Hành vi thao tác:**
  - **Tự động biên dịch (Auto-compile):** Tự động biên dịch sau khi ngừng gõ 800ms hoặc nhấn phím tắt `Ctrl+S` / `Cmd+S`.
  - **Lưu trữ tự động (Local Storage Persistence):** Tự động lưu bản nháp văn bản và hội thoại vào `localStorage`, khôi phục nguyên vẹn khi tải lại trang (F5).
  - **Nạp mẫu đề thi chuẩn:** Cung cấp sẵn các mẫu: Đề thi Chuẩn Quốc Gia 2025 (`ex_test` v3.3), Đề thi Chuẩn Thông tư 32 (3 phần), Chuyên đề Bảng biến thiên tkz-tab, Chuyên đề Hình học không gian TikZ, Tài liệu mới.
  - **Lưu vào Ngân hàng:** Trích xuất các câu hỏi từ mã LaTeX sang các bản ghi ngân hàng câu hỏi chuẩn hóa (`questions` table) chỉ với 1 click, hỗ trợ đồng thời cả cú pháp `ex_test` (`\begin{ex}`) và cú pháp truyền thống (`\textbf{Câu X.}`).
  - **Tải tệp PDF & .TEX:** Xuất bản tệp PDF vector-crisp 100% font CMU Serif và tệp nguồn LaTeX `.tex`.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-03: PHÂN HỆ CÂY KIẾN THỨC & YÊU CẦU CẦN ĐẠT (TAXONOMY THEO TT 32)  │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.5. FR-03.1: Quản trị Cây Phân cấp Chuẩn hóa theo Thông tư 32/2018/TT-BGDĐT
- **Mô tả:** Hệ thống chuẩn hóa cây phân loại kiến thức và năng lực thống nhất toàn quốc, **tuyệt đối không phân chia theo bộ sách giáo khoa**.
- **Cấu trúc phân cấp 6 tầng:**
  1. **Cấp học / Khối lớp (Grade):** Lớp 10, Lớp 11, Lớp 12...
  2. **Môn học (Subject):** Toán học, Vật lí, Hoá học, Sinh học, Ngữ văn, Lịch sử, Địa lí, Tiếng Anh...
  3. **Mạch nội dung (Content Strand):** Các mạch kiến thức lớn được quy định trong Thông tư 32 (Ví dụ Môn Toán: *Mạch 1: Số, Đại số và Một số yếu tố giải tích*; *Mạch 2: Hình học và Đo lường*; *Mạch 3: Thống kê và Xác suất*; *Mạch 4: Hoạt động thực hành và trải nghiệm*).
  4. **Chủ đề / Chuyên đề học tập (Topic / Elective Module):** Ví dụ: Ứng dụng đạo hàm, Khối đa diện, Di truyền phân tử...
  5. **Bài học / Đơn vị kiến thức (Lesson):** Đơn vị bài giảng cụ thể.
  6. **Yêu cầu cần đạt (YCCĐ - Learning Outcome):** Mã định danh và nội dung chuẩn hóa theo Thông tư 32 (Ví dụ: `TOAN12.GT.01`: *"Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị hàm số"*).
- **Tầng Dạng câu hỏi (Problem Archetype):** Dưới mỗi YCCĐ, cho phép định nghĩa các Dạng bài tập chuyên đề cụ thể (Ví dụ: *Dạng 1: Đọc đồ thị hàm số tìm cực trị*, *Dạng 2: Cực trị hàm đa thức chứa tham số $m$*, *Dạng 3: Bài toán tối ưu thực tiễn*).

### 2.6. FR-03.2: Chuẩn hóa 3 Mức độ Nhận thức theo Bảng Động từ TT 32
- **Biết (Nhận biết):** Nhận biết và nhớ lại thông tin đã tiếp nhận (Động từ: *Đọc, đếm, viết, làm quen, nhận dạng, nhận biết*).
- **Hiểu (Thông hiểu):** Diễn đạt theo ý hiểu cá nhân (Động từ: *Mô tả, giải thích, thể hiện, sắp xếp*).
- **Vận dụng:** Vận dụng vào tình huống mới hoặc giải quyết vấn đề (Động từ: *Tính, vẽ, thực hiện, sử dụng, vận dụng, so sánh, phân biệt, lí giải, chứng minh, giải quyết vấn đề thực tiễn* - bao gồm cả Vận dụng cao).

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-04: PHÂN HỆ NGÂN HÀNG CÂU HỎI & VÒNG ĐỜI (ITEM BANK MANAGEMENT)   │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.7. FR-04.1: Quản lý các Dạng thức Khảo thí (Bám sát Quyết định 764/QĐ-BGDĐT)
Hệ thống hỗ trợ 5 thể thức khảo thí:
1. **`SINGLE_CHOICE` (Trắc nghiệm đơn 4 lựa chọn):** 1 đáp án đúng duy nhất.
2. **`TRUE_FALSE_GROUP` (Trắc nghiệm Đúng/Sai 4 khẳng định):**
   - 1 Thân câu hỏi chung.
   - 4 Khẳng định con a), b), c), d) độc lập, mỗi ý lưu giá trị `is_true: true/false`.
   - **Quy tắc tính điểm bậc thang:** Đúng 1 ý = 0.1đ; Đúng 2 ý = 0.25đ; Đúng 3 ý = 0.5đ; Đúng cả 4 ý = 1.0đ.
3. **`SHORT_ANSWER` (Trắc nghiệm trả lời ngắn):** Thân câu hỏi + chuỗi kết quả (số hoặc chữ) kèm dung sai sai số tính toán $\pm \epsilon$.
4. **`PASSAGE_GROUP` (Câu hỏi chùm / Ngữ liệu đọc hiểu):** 1 Ngữ liệu cha + Danh sách câu hỏi con liên kết.
5. **`ESSAY` (Tự luận):** Thân câu hỏi + Rubric tiêu chí chấm điểm chi tiết.

### 2.8. FR-04.2: Cơ chế Chống Trùng lặp Câu hỏi bằng AI Vector Search
- Tính vector embedding 1536 chiều cho thân câu hỏi.
- So sánh Cosine Distance trong `pgvector` với các câu hỏi cùng Môn/Lớp:
  - Similarity $< 0.80$: Lưu bình thường.
  - $0.80 \le \text{Similarity} < 0.90$: Hiển thị cảnh báo vàng "Câu hỏi tương tự".
  - $\text{Similarity} \ge 0.90$: Bật Modal đỏ chặn lưu: *"Cảnh báo: Trùng lặp 92% với câu hỏi [TOAN12-0452] trong ngân hàng"* kèm bảng so sánh đối đầu trước khi cho phép lưu.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-05: MA TRẬN ĐỀ THI & BẢN ĐẶC TẢ KHẢO THÍ (EXAM MATRIX BUILDER)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.9. FR-05.1: Thiết lập Bản Đặc tả Ma trận Đề thi theo YCCĐ
- **Màn hình:** `SCR-MATRIX-BUILDER`
- **Thông số chung:** Tên kỳ thi, Khối lớp, Môn học, Thời gian làm bài (phút), Thang điểm tổng (10.0).
- **Lưới Ma trận (Matrix Grid):**
  - Trục dọc: Danh sách Mạch nội dung $\rightarrow$ Yêu cầu cần đạt (YCCĐ) $\rightarrow$ Dạng câu hỏi.
  - Trục ngang: 3 Cấp độ nhận thức (Biết, Hiểu, Vận dụng) $\times$ Dạng thức câu hỏi.
  - Mỗi ô cấu hình: Số lượng câu hỏi + Điểm số cho mỗi câu.
- **Tự động tính toán & Cảnh báo:**
  - Tổng số câu và tỷ lệ % điểm (ví dụ: $40\%$ Biết - $30\%$ Hiểu - $30\%$ Vận dụng; $70\%$ Trắc nghiệm - $30\%$ Tự luận).
  - Hiển thị chỉ báo **"Số dư khả dụng trong Ngân hàng"** bên cạnh số lượng yêu cầu để cảnh báo thiếu câu hỏi.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-06: ĐỘNG CƠ SINH ĐỀ & TRỘN MÃ ĐỀ AN TOÀN (SHUFFLING ENGINE)        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.10. FR-06.1: Thuật toán Sinh Đề Gốc theo Ràng buộc Ma trận
- **Đầu vào:** Ma trận đề thi ID + Danh sách loại trừ (các câu đã thi trong 30 ngày qua).
- **Xử lý:** Quét các câu hỏi đạt `status = 'APPROVED'`, lấy mẫu ngẫu nhiên có trọng số ưu tiên câu hỏi có chỉ số khảo thí tốt ($p, D$).
- **Đầu ra:** Bản ghi `master_exams` và danh sách `master_exam_items`.

### 2.11. FR-06.2: Thuật toán Trộn Đề Hoán vị An toàn (Safe Shuffling Engine)
- **Đầu vào:** `master_exam_id`, Số lượng mã đề cần tạo (101, 102, 103, 104).
- **4 Nguyên tắc An toàn Tuyệt đối:**
  1. **Section Integrity:** Chỉ đảo thứ tự câu hỏi trong cùng một Phần.
  2. **Passage Integrity:** Ngữ liệu bài đọc chung và các câu hỏi con luôn đi liền kề nhau.
  3. **Option Anchor Rule:** Phương án chứa "Cả A và B", "Tất cả các ý trên", "Không có đáp án nào" hoặc cờ `is_fixed = true` bắt buộc **khóa cố định ở vị trí cuối cùng (D)**.
  4. **Key Generator:** Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu giữa đề gốc và các mã đề hoán vị.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-07: XUẤT BẢN ĐỀ THI ĐA ĐỊNH DẠNG (PUBLISHING SERVICE)              │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.12. FR-07.1: Xuất bản Microsoft Word (.docx) Chuẩn Khảo thí & MathType OLE
- **Định dạng in ấn & Khổ giấy:**
  - Khổ chuẩn quốc gia: **A4 Portrait (210 x 297 mm)**, lề trang 1.5 cm - 1.8 cm, font Times New Roman 11pt, giãn dòng 1.15.
  - Header chuẩn: Tên trường/sở, môn thi, mã đề thi, bảng điền số báo danh và phách.
- **Công thức Toán đa định dạng (`math_format`):**
  - **`mathtype` (Mặc định):** Nhúng đối tượng **MathType 7.0 OLE Object Vector WMF** (`image/x-wmf` với APM header, root CLSID `{0002CE03-0000-0000-C000-000000000046}`, stream `Equation Native` chứa MTEF v5 DSMT7 và bản ghi `TeX Input Language`). Căn thẳng hàng chân dòng (baseline alignment qua `w:position` khớp chuẩn xác theo `depth_pt` của WMF), tự động nâng cấp phân số sang `\dfrac` (cỡ chữ 11pt đầy đủ cho cả tử và mẫu), chuẩn hóa khoảng cách ký tự (kerning/spacing chuẩn MathType: giãn cách toán tử `=`, `+`, `-`, đệm giữa các nhân tử kề nhau, hỗ trợ ký hiệu đạo hàm `f'(x)` chuẩn Symbol `0xa2`), bảo toàn và dựng vector đa giác cho các dấu ngoặc co giãn (`\left`, `\right` ngoặc đơn, ngoặc vuông, ngoặc nhọn), đệm kerning chữ nghiêng tránh dính dấu ngoặc (`f(x)` -> `f\,(x)`), chuẩn hóa tập số `\mathbb{R}, \mathbb{Q}, \mathbb{Z}` sang Times New Roman Bold đứng chuẩn xác, tắt gạch chân đỏ kiểm tra chính tả của Word (`w:hideSpellingErrors`, `w:noProof`), chuẩn hóa typographic style (tên hàm `\sin`, `\cos`, `\tan`, `\cot` thẳng đứng Upright, biến số in nghiêng Italic), chuẩn hóa embellishment vectơ (`\vec`, `\overrightarrow`), áp dụng typeface `0x82` bảo toàn toàn bộ dấu ngoặc `[`, `]`, `(`, `)`, `{`, `}` trong MathType, đạt độ nét vector tuyệt đối 100% không bị fallback DIB mờ hay lỗi dấu `?` ở mọi mức zoom, **cho phép click đúp mở MathType 7 client để chỉnh sửa trực tiếp 2 chiều đồng bộ tuyệt đối với Web**.
  - **`omml`:** Phương trình bản địa Microsoft Word (`<m:oMath>`) chuyển đổi từ TeX qua MathJax MathML và XSLT.
  - **`latex`:** Giữ nguyên mã nguồn LaTeX bọc trong cặp `${...}$`.
- **Tự động chuyển đổi bảng dữ liệu thống kê (`\begin{array}`):**
  - Tự động nhận diện mảng bảng phân phối tần số ghép nhóm hoặc bảng biến thiên trong đề thi.
  - Dựng thành bảng Microsoft Word thực tế (`<w:tbl>`) căn giữa, có viền nét mảnh (`border sz="4"`), loại bỏ triệt để hiện tượng hộp đen (black box) khi xuất sang PDF.
- **Dịch vụ MathJax Persistent Worker:**
  - Chạy tiến trình nền Node.js xử lý MathJax 3/4 với bộ gói TeX đầy đủ (`input/tex-full`), thời gian sinh ~14 ms/công thức.
- **Gói ZIP xuất bản:**
  - $N$ file đề thi Word (`De_101.docx`, `De_102.docx`...).
  - File Hướng dẫn giải chi tiết từng mã đề (`LoiGiai_101.docx`...).
  - File Bảng đáp án tổng hợp các mã đề (Excel/CSV UTF-8 BOM + PDF).
  - File Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-08: KHẢO THÍ & ĐÁNH GIÁ NĂNG LỰC HẬU KIỂM (ITEM ANALYTICS)         │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.13. FR-08.1: Phân tích Chất lượng Câu hỏi Hậu kiểm
- **Đầu vào:** Bảng điểm học sinh theo từng câu hỏi của kỳ thi.
- **Hệ thống tính toán:**
  - **Độ khó thực nghiệm ($p$):** Tỷ lệ học sinh làm đúng ($p = R/N$).
  - **Độ phân biệt ($D$):** Chênh lệch tỷ lệ đúng giữa nhóm 27% điểm cao nhất và nhóm 27% điểm thấp nhất ($D = P_H - P_L$).
  - **Cảnh báo chất lượng:** Nếu $D < 0.2$, hệ thống gắn cờ cảnh báo `QUESTION_DEFECTIVE` để Hội đồng bộ môn thẩm định lại.

---

## 3. THIẾT KẾ ĐẶC TẢ API CỐT LÕI (CORE API CONTRACTS)

### 3.1. API Lưu Câu hỏi vào Ngân hàng (Gắn chuẩn YCCĐ theo TT 32)
- **Endpoint:** `POST /api/v1/questions`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "subject_id": "uuid-math-01",
    "grade_id": "uuid-grade-12",
    "strand_id": "uuid-strand-giai-tich",
    "topic_id": "uuid-topic-ham-so",
    "lesson_id": "uuid-lesson-cuc-tri",
    "learning_outcome_id": "uuid-yccd-toan12-gt-01",
    "problem_archetype_id": "uuid-archetype-cuc-tri-chua-m",
    "cognitive_level": "APPLICATION",
    "item_format": "SINGLE_CHOICE",
    "stem": "Cho hàm số $y = x^3 - 3mx^2 + 4$. Tìm tất cả các giá trị của tham số $m$ để hàm số có 2 điểm cực trị nằm về 2 phía trục tung.",
    "options": [
      { "label": "A", "content": "$m > 0$", "is_correct": true, "is_fixed": false },
      { "label": "B", "content": "$m < 0$", "is_correct": false, "is_fixed": false },
      { "label": "C", "content": "$m = 0$", "is_correct": false, "is_fixed": false },
      { "label": "D", "content": "Không có giá trị $m$ thỏa mãn", "is_correct": false, "is_fixed": true }
    ],
    "explanation": "Đạo hàm $y' = 3x^2 - 6mx = 3x(x - 2m)$. Để cực trị nằm về 2 phía thì tích 2 nghiệm hoành độ cực trị âm...",
    "source_reference": "Đề Khảo sát THPT 2024"
  }
  ```
- **Response:** `201 Created`

### 3.2. API Lưu Câu hỏi Đúng/Sai 4 ý (Quyết định 764/QĐ-BGDĐT)
- **Endpoint:** `POST /api/v1/questions`
- **Request Body Payload:**
  ```json
  {
    "subject_id": "uuid-math-01",
    "grade_id": "uuid-grade-12",
    "learning_outcome_id": "uuid-yccd-toan12-gt-01",
    "problem_archetype_id": "uuid-archetype-doc-do-thi",
    "cognitive_level": "COMPREHENSION",
    "item_format": "TRUE_FALSE_GROUP",
    "stem": "Cho hàm số $y = f(x)$ xác định và liên tục trên $\\mathbb{R}$, có đồ thị như hình vẽ bên.",
    "image_urls": ["https://storage.quesy.edu.vn/assets/img_graph_01.webp"],
    "sub_statements": [
      { "label": "a", "content": "Hàm số đồng biến trên khoảng $(-\\infty; -1)$ và $(1; +\\infty)$.", "is_true": true, "explanation": "Quan sát đồ thị hàm số đi lên từ trái sang phải..." },
      { "label": "b", "content": "Điểm cực tiểu của đồ thị hàm số là $(1; -2)$.", "is_true": true, "explanation": "Tọa độ điểm đáy là $(1; -2)$." },
      { "label": "c", "content": "Giá trị lớn nhất của hàm số trên $\\mathbb{R}$ bằng $2$.", "is_true": false, "explanation": "Hàm số tiến ra $+\\infty$ nên không có GTLN trên R." },
      { "label": "d", "content": "Phương trình $f(x) = m$ có đúng 3 nghiệm phân biệt khi $-2 < m < 2$.", "is_true": true, "explanation": "Đường thẳng $y=m$ cắt đồ thị tại 3 điểm khi $-2 < m < 2$." }
    ]
  }
  ```
- **Response:** `201 Created`
