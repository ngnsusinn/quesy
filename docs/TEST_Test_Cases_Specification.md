# TÀI LIỆU KỊCH BẢN KIỂM THỬ (TEST CASES SPECIFICATION)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-TEST-01  
- **Phiên bản:** 2.5 (Tập trung kiểm thử chức năng & Độ tin cậy giải pháp)  
- **Tiêu chuẩn kiểm thử:** IEEE 829 (Standard for Software Test Documentation)  
- **Tổng số kịch bản tự động hóa:** 46 Tests (100% Passed)  
- **Ngày lập:** 2026-10-18  
- **Môi trường áp dụng:** Staging & Production Verification (Pytest & CI)  

---

## 1. TỔNG QUAN KẾ HOẠCH KIỂM THỬ (TEST PLAN OVERVIEW)

### 1.1. Mục tiêu Kiểm thử
Xác minh toàn bộ tính năng của hệ thống Quesy đáp ứng chính xác các yêu cầu nghiệp vụ và giải quyết trọn vẹn các bài toán kỹ thuật thực tế:
1. Độ chính xác của AI bóc tách công thức Toán LaTeX, giải mã MathType MTEF, và biên dịch đồ thị vector SVG (TikZ/PGFPlots) có Auto-clipping.
2. Kiểm tra bộ 4 quy tắc chuẩn hóa toán học (ngoặc `\left`/`
ight`, số thập phân `{,}` trong đề và số sạch trong đáp án, phân số `\dfrac`, vectơ `\overrightarrow`).
3. Xác minh thể thức câu hỏi hiện đại: **Trắc nghiệm Đúng/Sai 4 khẳng định tính điểm bậc thang** và **Trắc nghiệm Trả lời ngắn**.
4. Thuật toán **Trộn đề An toàn (Safe Shuffling)**: Đảm bảo không tách rời câu hỏi chùm và luôn khóa cố định phương án *"Cả A và B đều đúng"* tại vị trí cuối cùng (D).
5. Chất lượng xuất bản file Word 2 cột với công thức native OMML và bảng điểm Excel UTF-8 BOM.

### 1.2. Thang đánh giá Kết quả (Test Result Status)
- **PASS:** Chức năng hoạt động chính xác theo đúng kết quả kỳ vọng.
- **FAIL:** Phát hiện sai lệch hoặc lỗi logic; cần mở Bug Ticket.
- **BLOCK:** Bị nghẽn bởi một lỗi khác, chưa thể thực hiện kiểm thử.

---

## 2. MA TRẬN PHỦ KIỂM THỬ (TRACEABILITY MATRIX)

| Test Suite ID | Nhóm Chức năng Kiểm thử | Yêu cầu Nghiệp vụ Liên quan | Số lượng Test Cases | Mức độ Ưu tiên |
|:---|:---|:---:|:---:|:---:|
| **TS-01** | Bóc tách AI, LaTeX & Auto-tagging YCCĐ | BR-01, FR-01, SRS-FEAT-01 | 6 | P0 (Must Have) |
| **TS-02** | Studio Hậu kiểm Đối chiếu (HITL Studio) | BR-01.5, FR-02, SRS-FEAT-02 | 4 | P0 (Must Have) |
| **TS-03** | Cây Kiến thức & Chuẩn YCCĐ (TT 32) | BR-02.1, FR-03, SRS-FEAT-03 | 4 | P0 (Must Have) |
| **TS-04** | Ngân hàng Câu hỏi & Định dạng 2025 | BR-02.4, FR-04, SRS-FEAT-04,05 | 5 | P0 / P1 |
| **TS-05** | Ma trận Đề thi theo YCCĐ & Sinh Đề | BR-03, BR-04.1, FR-05, FR-06.1 | 4 | P0 (Must Have) |
| **TS-06** | Động cơ Trộn Đề Hoán vị An toàn | BR-04.2, FR-06.2, SRS-FEAT-08 | 5 | P0 (Critical) |
| **TS-07** | Xuất bản File Word 2 Cột & In ấn | BR-05.1, FR-07, SRS-FEAT-09 | 4 | P0 (Must Have) |
| **TS-08** | Bảo mật, RBAC & Khảo thí Thống kê | BR-05.2, BR-06, FR-08 | 3 | P1 / P2 |
| **TS-09** | Soạn đề LaTeX AI & Live PDF (Tectonic) | FR-02.1, FR-02.2, NFR-COMP-02 | 4 | P0 (Must Have) |

---

## 3. DANH SÁCH KỊCH BẢN KIỂM THỬ CHI TIẾT (DETAILED TEST CASES)

---

### TEST SUITE 01: BÓC TÁCH AI, LATEX & AUTO-TAGGING YCCĐ

#### TC-OCR-01: Bóc tách file Word (.docx) chứa công thức MathType
- **Mô tả:** Kiểm tra khả năng trích xuất công thức MathType OLE từ file Word sang LaTeX.
- **Dữ liệu kiểm thử:** File `De_Toan_12_MathType.docx` gồm 50 câu trắc nghiệm chứa tích phân, đạo hàm, căn thức.
- **Các bước thực hiện:**
  1. Đăng nhập với tài khoản Giáo viên.
  2. Truy cập màn hình Tải đề thi (`SCR-UPLOAD`).
  3. Chọn file `De_Toan_12_MathType.docx`, chọn Môn Toán, Khối 12. Bấm "Bắt đầu bóc tách".
- **Kết quả kỳ vọng:**
  - Hệ thống tải file thành công, hiển thị thanh tiến trình.
  - Toàn bộ công thức MathType được giải mã chính xác sang chuỗi LaTeX chuẩn (ví dụ: `\int_{0}^{1} x e^x dx`).
  - Không xuất hiện tình trạng công thức bị rỗng hoặc biến thành ảnh mờ. Tỷ lệ nhận diện đúng công thức $\ge 95\%$.

#### TC-OCR-02: Bóc tách file PDF scanned & Tự động cắt ảnh hình học/đồ thị
- **Mô tả:** Kiểm tra khả năng nhận diện bố cục, chuyển đổi LaTeX và tự động cắt hình học trong file PDF scan.
- **Dữ liệu kiểm thử:** File `De_HinhHoc_Scan.pdf` có 5 câu chứa hình vẽ lăng trụ, chóp tứ giác và đồ thị hàm bậc 3.
- **Các bước thực hiện:**
  1. Tải lên file `De_HinhHoc_Scan.pdf`.
  2. Chờ AI Worker xử lý hoàn tất và chuyển sang màn hình HITL.
- **Kết quả kỳ vọng:**
  - AI phát hiện chính xác tọa độ các hình vẽ.
  - Cắt và lưu 5 file ảnh vào S3 định dạng WebP sắc nét, không bị cắt cụt đỉnh hình hoặc dính chữ thừa của câu hỏi.
  - Thân câu hỏi ở màn hình HITL hiển thị đúng thẻ ảnh tương ứng.

#### TC-OCR-04: Kiểm tra tính năng Gợi ý Auto-tagging Mã YCCĐ theo Thông tư 32
- **Mô tả:** Kiểm tra AI tự động phân tích ngữ nghĩa và đề xuất mã YCCĐ và Dạng câu hỏi.
- **Dữ liệu kiểm thử:** Câu hỏi: *"Tìm tất cả các giá trị của tham số $m$ để hàm số $y = x^3 - 3mx^2 + 4$ có 2 điểm cực trị..."*
- **Các bước thực hiện:**
  1. Bóc tách đề thi chứa câu hỏi trên.
  2. Xem trường gợi ý phân loại trên màn hình HITL.
- **Kết quả kỳ vọng:**
  - Hệ thống tự động gợi ý:
    - Mạch nội dung: *Số, Đại số và Một số yếu tố giải tích*
    - Chủ đề: *Ứng dụng đạo hàm để khảo sát hàm số*
    - Bài học: *Tính đơn điệu và cực trị của hàm số*
    - Mã YCCĐ: `TOAN12.GT.01`
    - Dạng câu hỏi: *Cực trị chứa tham số m*
    - Mức độ tư duy: *Vận dụng*

---

### TEST SUITE 02: STUDIO HẬU KIỂM ĐỐI CHIẾU (HITL STUDIO)

#### TC-HITL-01: Kiểm tra tính năng Cuộn đồng bộ (Synchronized Scrolling)
- **Mô tả:** Kiểm tra tương tác giữa khung xem file gốc và danh sách câu hỏi bóc tách.
- **Các bước thực hiện:**
  1. Mở màn hình HITL Studio với đề thi 50 câu.
  2. Nhấp chuột vào Card câu hỏi số 25 ở khung bên phải.
- **Kết quả kỳ vọng:**
  - Khung PDF bên trái tự động cuộn mượt mà đến trang chứa Câu 25.
  - Vùng văn bản của Câu 25 trên trang PDF được highlight viền màu xanh nhạt.
  - Thời gian phản hồi cuộn trang $< 100$ ms.

#### TC-HITL-02: Chỉnh sửa nhanh công thức LaTeX trực tiếp trên giao diện
- **Mô tả:** Kiểm tra tính năng sửa lỗi công thức toán học và live render KaTeX.
- **Các bước thực hiện:**
  1. Chọn Câu 3 đang có công thức `$y = x^2 + 2x$`.
  2. Nhấp đúp vào công thức, sửa chuỗi mã thành `$y = x^3 - 3x^2 + 4$`.
  3. Nhấn phím Enter hoặc nút "Lưu".
- **Kết quả kỳ vọng:**
  - Công thức được cập nhật ngay lập tức trên màn hình và render KaTeX chuẩn xác, không bị tải lại trang.

---

### TEST SUITE 03: CÂY KIẾN THỨC & CHUẨN YCCĐ (TT 32 VALIDATION)

#### TC-TAX-01: Kiểm tra Cấu trúc Phân cấp theo YCCĐ & Tuyệt đối Không có "Bộ sách"
- **Mô tả:** Xác minh cấu trúc dữ liệu và giao diện phân loại chuẩn hóa theo Thông tư 32/2018/TT-BGDĐT, hoàn toàn không xuất hiện trường "Bộ sách".
- **Các bước thực hiện:**
  1. Truy cập màn hình Quản lý Danh mục Kiến thức (`SCR-TAXONOMY`).
  2. Kiểm tra các trường dữ liệu và bộ lọc.
  3. Tạo một Dạng câu hỏi mới thuộc YCCĐ `TOAN12.GT.01`: *"Dạng bài toán thực tế tối ưu ứng dụng cực trị"*.
- **Kết quả kỳ vọng:**
  - Giao diện và API hoàn toàn **KHÔNG CÓ** trường "Bộ sách" (Cánh diều, Kết nối tri thức...).
  - Cấu trúc hiển thị 6 tầng: Cấp/Khối $\rightarrow$ Môn $\rightarrow$ Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ YCCĐ $\rightarrow$ Dạng câu hỏi.

#### TC-TAX-02: Kiểm tra 3 Cấp độ Tư duy theo Bảng Động từ TT 32
- **Mô tả:** Kiểm tra dropdown mức độ nhận thức bám sát Bảng động từ của Thông tư 32.
- **Kết quả kỳ vọng:** Dropdown hiển thị đúng 3 mức độ:
  - **Biết (Nhận biết):** Gợi ý động từ: đọc, đếm, viết, nhận dạng, nhận biết...
  - **Hiểu (Thông hiểu):** Gợi ý động từ: mô tả, giải thích, thể hiện, sắp xếp...
  - **Vận dụng:** Gợi ý động từ: tính, vẽ, thực hiện, so sánh, phân biệt, giải quyết vấn đề...

---

### TEST SUITE 04: NGÂN HÀNG CÂU HỎI & ĐỊNH DẠNG ĐỀ THI 2025

#### TC-BANK-01: Kiểm tra Quy tắc Tính điểm Đúng/Sai 4 khẳng định (RULE-01)
- **Mô tả:** Kiểm tra lưu trữ và chấm điểm câu hỏi Đúng/Sai 4 ý theo Quyết định 764/QĐ-BGDĐT.
- **Dữ liệu kiểm thử:** Câu hỏi có 4 ý a, b, c, d với đáp án chuẩn: a-Đúng, b-Đúng, c-Sai, d-Đúng.
- **Các kịch bản kiểm tra điểm số (Thang 1.0 điểm):**
  - Kịch bản 1: Học sinh trả lời đúng duy nhất ý a $\rightarrow$ Điểm nhận được: **0.1 điểm** (10%).
  - Kịch bản 2: Học sinh trả lời đúng ý a và b $\rightarrow$ Điểm nhận được: **0.25 điểm** (25%).
  - Kịch bản 3: Học sinh trả lời đúng ý a, b và d $\rightarrow$ Điểm nhận được: **0.5 điểm** (50%).
  - Kịch bản 4: Học sinh trả lời đúng cả 4 ý a, b, c, d $\rightarrow$ Điểm nhận được: **1.0 điểm** (100%).
- **Kết quả kỳ vọng:** Logic tính điểm trả về chính xác theo đúng thang điểm bậc thang của Bộ GD&ĐT.

#### TC-BANK-02: Kiểm tra Cơ chế Cảnh báo Trùng lặp bằng AI Vector
- **Mô tả:** Xác minh hệ thống phát hiện và chặn lưu câu hỏi trùng lặp qua `pgvector`.
- **Dữ liệu kiểm thử:** Ngân hàng đã có sẵn câu hỏi Q1: *"Tìm tập nghiệm của phương trình $\log_2(x - 1) = 3$."* Nhập câu mới Q2: *"Giải phương trình $\log_2(x - 1) = 3$ để tìm nghiệm $x$."*
- **Kết quả kỳ vọng:**
  - Độ tương đồng Cosine đo được $\ge 0.92$.
  - Hệ thống bật Modal cảnh báo trùng lặp màu đỏ: *"Cảnh báo: Phát hiện câu hỏi trùng lặp 92% với câu hỏi [TOAN-012]"*.
  - Hiển thị bảng so sánh đối đầu 2 câu hỏi và chặn lưu tự động cho đến khi người dùng xác nhận.

---

### TEST SUITE 06: ĐỘNG CƠ TRỘN ĐỀ HOÁN VỊ AN TOÀN (SAFE SHUFFLING ENGINE)

#### TC-SHUFFLE-01: Quy tắc Neo cố định Phương án (Option Anchor Rule - RULE-02)
- **Mô tả:** Đảm bảo các phương án chứa từ ngữ phụ thuộc vị trí ("Cả A và B", "Tất cả các ý trên") không bị đảo lên đầu câu.
- **Dữ liệu kiểm thử:** Câu hỏi có 4 lựa chọn: A: Phương án 1; B: Phương án 2; C: Phương án 3; D: *"Cả A và B đều đúng"* (`is_fixed = true`).
- **Các bước thực hiện:**
  1. Đưa câu hỏi trên vào Đề thi Gốc.
  2. Yêu cầu hệ thống sinh 4 mã đề hoán vị: 101, 102, 103, 104.
  3. Kiểm tra vị trí của nội dung *"Cả A và B đều đúng"* trong cả 4 mã đề.
- **Kết quả kỳ vọng:**
  - Trong toàn bộ 4 mã đề (101, 102, 103, 104), nội dung *"Cả A và B đều đúng"* **LUÔN NẰM Ở VỊ TRÍ D**.
  - Các phương án A, B, C được hoán vị ngẫu nhiên hợp lệ.

#### TC-SHUFFLE-02: Quy tắc Bảo toàn Toàn vẹn Câu hỏi Chùm (Passage Integrity - RULE-03)
- **Mô tả:** Đảm bảo đoạn văn ngữ liệu chung và các câu hỏi con luôn đi liền kề nhau sau khi trộn đề.
- **Dữ liệu kiểm thử:** Một bài đọc tiếng Anh (Passage P) gồm 4 câu hỏi con (C1, C2, C3, C4).
- **Các bước thực hiện:**
  1. Tạo đề thi chứa bài đọc P và 20 câu hỏi trắc nghiệm đơn khác.
  2. Thực hiện sinh 4 mã đề hoán vị.
  3. Kiểm tra số thứ tự của các câu hỏi con C1, C2, C3, C4 trong từng mã đề.
- **Kết quả kỳ vọng:**
  - Bài đọc P luôn xuất hiện ngay trước các câu con.
  - Các câu con luôn nằm ở các vị trí số thứ tự liên tiếp nhau (ví dụ: Câu 15, 16, 17, 18).
  - Không có bất kỳ câu hỏi đơn nào bị xen vào giữa cụm câu hỏi con của bài đọc P.

---

### TEST SUITE 07: XUẤT BẢN FILE WORD 2 CỘT & IN ẤN

#### TC-EXP-01: Kiểm tra Bố cục và Định dạng Công thức OMML trong file Word
- **Mô tả:** Đảm bảo file Word `.docx` xuất ra đạt chuẩn quy cách in ấn của Bộ GD&ĐT với công thức OMML.
- **Các bước thực hiện:**
  1. Chọn mã đề 101, chọn math_format="omml", bấm "Xuất bản file Word (.docx)".
  2. Mở file tải về trên Microsoft Word 2016 / 365.
- **Kết quả kỳ vọng:**
  - Tiêu đề trường, mã đề, bảng phách căn chỉnh lề chuẩn xác khổ A4 Portrait.
  - Công thức Toán học hiển thị dưới dạng **Word Equation native (OMML `<m:oMath>`)**, có thể click chuột vào chỉnh sửa trực tiếp, chữ nét vector, không bị vỡ hạt như hình ảnh bitmap.

#### TC-EXP-02: Kiểm tra Xuất bản MathType 7.0 OLE Object Vector WMF & Bảo toàn Chỉnh sửa 2 Chiều
- **Mô tả:** Đảm bảo 100% công thức toán nhúng đối tượng OLE chuẩn MathType 7.0 DSMT7, đạt độ nét vector tuyệt đối (loại bỏ hoàn toàn raster DIB) và mở sửa được 2 chiều trong MathType client không gặp lỗi OLE activation hay popup cảnh báo thiếu ứng dụng server.
- **Các bước thực hiện:**
  1. Xuất file Word với tham số `math_format="mathtype"`.
  2. Dùng automation PowerShell Word COM kiểm tra thuộc tính các shape:
     `$doc.InlineShapes.Item(1).OLEFormat.ProgID` và thực thi `$shape.OLEFormat.Open()`.
- **Kết quả kỳ vọng:**
  - `InlineShape.Type = 1` (wdInlineShapeEmbeddedOLEObject).
  - `OLEFormat.ProgID = "Equation.DSMT4"`, `ClassType = "Equation.DSMT4"`.
  - Hình ảnh đại diện mang định dạng Vector WMF (`image/x-wmf`) chuẩn APM header, 100% vector thuần (0 file chứa bản ghi raster DIB `0x0b41`).
  - Stream `Equation Native` chứa MTEF v5 định dạng DSMT7 với bản ghi `TeX Input Language` lưu chuỗi LaTeX gốc, chuẩn hóa embellishment toán tử vectơ, và sử dụng typeface `0x82` bảo toàn đầy đủ các dấu ngoặc `[`, `]`, `(`, `)`, `{`, `}` khi mở MathType.
  - Lệnh `OLEFormat.Open()` thực thi thành công, cửa sổ MathType 7 mở ra hiển thị công thức chính xác đồng bộ với nội dung LaTeX trên Web (ví dụ $A = [5; 8)$ hiển thị đầy đủ cả dấu ngoặc `[` và `)` trong MathType), không xuất hiện popup lỗi server application hay hiển thị chữ "A" cô lập.

#### TC-EXP-03: Tự động chuyển đổi bảng dữ liệu thống kê LaTeX sang Word Table
- **Mô tả:** Đảm bảo mảng bảng thống kê `\begin{array}` được chuyển thành bảng Word native `<w:tbl>`, không phát sinh lỗi ô đen (black box) khi xuất sang PDF.
- **Các bước thực hiện:**
  1. Đề thi chứa câu hỏi thống kê với bảng ghép nhóm (như Câu 2 đề Nghệ An).
  2. Xuất sang Word và convert sang PDF qua Word COM / máy in ảo.
- **Kết quả kỳ vọng:**
  - Bảng hiển thị dạng bảng Word thực tế căn giữa, có viền nét mảnh (`border sz="4"`).
  - Xuất sang PDF hiển thị nền trắng chữ đen sắc nét, hoàn toàn không có ô chữ nhật đen che khuất.

#### TC-EXP-04: Kiểm thử Hiệu năng & Ổn định Dịch vụ MathJax Engine
- **Mô tả:** Đo kiểm tốc độ sinh công thức và bộ nhớ đệm qua Persistent Worker Node.js.
- **Các bước thực hiện:**
  1. Chạy test suite `test_performance_budgets.py::test_perf_budget_docx_and_zip_export`.
  2. Kiểm tra bộ nhớ đệm đĩa cứng `storage/cache/mathjax/` và RAM LRU.
- **Kết quả kỳ vọng:**
  - Thời gian xử lý trung bình $< 20\text{ ms}$/công thức.
  - Toàn bộ gói đề thi 4 mã đề kèm đáp án sinh xong trong $< 5\text{ giây}$ (ngân sách NFR $< 10\text{ giây}$).

---

### TEST SUITE 09: SOẠN ĐỀ LATEX AI & BIÊN DỊCH LIVE PDF (OPEN-PRISM & TECTONIC DOCKER)

#### TC-COMP-01: Lấy danh mục Đề thi mẫu chuẩn Khảo thí TT 32
- **Mô tả:** Kiểm tra API cung cấp đầy đủ các mẫu LaTeX chuẩn: đề thi 3 phần TT32, bảng biến thiên tkz-tab, hình học không gian TikZ.
- **Kết quả kỳ vọng:** HTTP 200, trả về danh sách template đầy đủ cấu trúc LaTeX hợp lệ.

#### TC-COMP-02: Biên dịch trực tiếp sang PDF vector qua Tectonic Engine
- **Mô tả:** Kiểm tra khả năng biên dịch tài liệu LaTeX chứa tiếng Việt có dấu, MathJax và bảng biến thiên `tkz-tab` thành file PDF vector nguyên bản qua Tectonic Engine (Docker microservice / local / Chromium fallback).
- **Kết quả kỳ vọng:** HTTP 200, header `Content-Type: application/pdf`, dung lượng file $> 1000$ bytes, magic header `%PDF`.

#### TC-COMP-03: Trợ lý AI Soạn thảo LaTeX (Copilot Chat & Smart Diff Suggestion)
- **Mô tả:** Kiểm tra trợ lý AI sinh mã LaTeX cho câu hỏi khảo sát hàm số, bảng biến thiên `tkz-tab`, và cơ chế Smart Diff Replacement đề xuất thay thế cục bộ văn bản (ví dụ đổi cỡ chữ 11pt sang 12pt).
- **Kết quả kỳ vọng:** AI phản hồi mã LaTeX tự chứa hoặc khối diff có cấu trúc (`DiffSuggestion` với `old_text` và `new_text`), hỗ trợ 1-click chèn vào editor hoặc duyệt thay thế cục bộ qua banner.

#### TC-COMP-04: Trích xuất 1-Click từ LaTeX sang Ngân hàng Câu hỏi
- **Mô tả:** Kiểm tra parser bóc tách các câu hỏi `\textbf{Câu X.}` và cú pháp `ex_test.sty` (`\begin{ex}`) sang schema Question/QuestionOption/SubStatement của Quesy.
- **Kết quả kỳ vọng:** Đọc và lưu đúng số lượng câu hỏi vào DB với trạng thái `DRAFT`.

#### TC-COMP-05: Bảo toàn Giao diện Dark Editor khi Focus con trỏ
- **Mô tả:** Kiểm tra textarea `#composer-editor-input` duy trì đúng nền tối `#141824` và chữ sáng khi nhận focus, không bị rule CSS toàn cục làm biến đổi sang nền trắng.
- **Kết quả kỳ vọng:** Màu nền giữ nguyên `#141824`, không lóa trắng mắt giáo viên khi gõ văn bản.

#### TC-COMP-06: Nút Biên dịch Xanh Dương Chuẩn Khảo thí
- **Mô tả:** Kiểm tra thanh nút tác vụ `BIÊN DỊCH` dưới đáy giao diện hiển thị màu xanh dương (`#0071e3`) kích hoạt biên dịch tức thì khi click.
- **Kết quả kỳ vọng:** Nút hiển thị màu xanh dương chuẩn, kích hoạt compile và phản hồi trạng thái loading.

---

## 4. TIÊU CHÍ ĐÓNG GIAI ĐOẠN KIỂM THỬ (TEST EXIT CRITERIA)

Dự án chỉ được nghiệm thu bàn giao khi:
1. **$100\%$** Test Cases thuộc mức độ ưu tiên **P0 (Must Have / Critical)** đạt trạng thái **PASS**.
2. **$\ge 95\%$** Test Cases thuộc mức độ ưu tiên **P1** đạt trạng thái **PASS**.
3. **Không còn bất kỳ Bug nào ở mức độ Blocker hoặc Critical** (đặc biệt là các lỗi về hoán vị mã đề, tính điểm Đúng/Sai lũy tiến, hoặc sai lệch công thức toán).
4. File Word `.docx` in thử thực tế trên máy in laser đạt độ rõ nét sư phạm.
