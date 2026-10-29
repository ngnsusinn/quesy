# TÀI LIỆU KỊCH BẢN KIỂM THỬ (TEST CASES SPECIFICATION)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-TEST-01  
- **Phiên bản:** 3.5 (Render KaTeX Toàn Diện Tại Ngân Hàng, Ma Trận Đề & Modals, Chuẩn Hóa Dropdown Box Apple HIG Unified Select .apple-select, Triệt Tiêu Lỗi Font Monospace & Khắc Phục Lỗi Hiển Thị Toán Học)  
- **Tiêu chuẩn kiểm thử:** IEEE 829 (Standard for Software Test Documentation)  
- **Tổng số kịch bản tự động hóa:** 215+ Tests (100% Passed)  
- **Ngày lập:** 2026-10-28  
- **Môi trường áp dụng:** Staging & Production Verification (Pytest & CI)

---

## 1. TỔNG QUAN KẾ HOẠCH KIỂM THỬ (TEST PLAN OVERVIEW)

### 1.1. Mục tiêu Kiểm thử
Xác minh toàn bộ tính năng của hệ thống Quesy đáp ứng chính xác các yêu cầu nghiệp vụ và giải quyết trọn vẹn các bài toán kỹ thuật thực tế:
1. Độ chính xác của AI bóc tách công thức Toán LaTeX, giải mã MathType MTEF, và biên dịch đồ thị vector SVG (TikZ/PGFPlots) có Auto-clipping.
2. Kiểm tra bộ 4 quy tắc chuẩn hóa toán học (ngoặc `\left`/`\right`, số thập phân `{,}` trong đề và số sạch trong đáp án, phân số `\dfrac`, vectơ `\overrightarrow`).
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
| **TS-04** | Ngân hàng Câu hỏi & Định dạng 2025 (Count, Export BOM, Import, Cascade) | BR-02.4, FR-04, SRS-FEAT-04,05 | 11 | P0 / P1 |
| **TS-05** | Ma trận Đề thi theo YCCĐ & Sinh Đề | BR-03, BR-04.1, FR-05, FR-06.1 | 4 | P0 (Must Have) |
| **TS-06** | Động cơ Trộn Đề Hoán vị An toàn | BR-04.2, FR-06.2, SRS-FEAT-08 | 5 | P0 (Critical) |
| **TS-07** | Xuất bản File Word 2 Cột & In ấn | BR-05.1, FR-07, SRS-FEAT-09 | 4 | P0 (Must Have) |
| **TS-08** | Bảo mật, RBAC & Khảo thí Thống kê | BR-05.2, BR-06, FR-08 | 3 | P1 / P2 |
| **TS-09** | Soạn đề LaTeX AI, Live PDF & Save-to-Bank 3 Thể Thức | FR-02.1, FR-02.2, NFR-COMP-02 | 118 | P0 (Must Have) |
| **TS-10** | Quản trị CI/CD & Cổng Pre-Commit Gate | NFR-DEV-01..06, TC-DEV-01..02 | 2 | P0 (Critical) |
| **TS-11** | Hệ Thống Xác Thực Auth (PBKDF2, JWT, OAuth Google/GitHub, RBAC) | BR-05.2, FR-08, AUTH-01 | 19 | P0 (Critical) |

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

### TEST SUITE 05: MA TRẬN ĐỀ THI 2D THEO YCCĐ & ĐỐI SOÁT TỒN KHO

#### TC-MATRIX-01: Thiết lập Lưới Ma trận 2D & Tải 3 Presets Chuẩn Hóa
- **Mô tả:** Kiểm tra khả năng tải và áp dụng chính xác 3 preset ma trận đề thi mẫu theo TT 22 & QĐ 764.
- **Các bước thực hiện:**
  1. Truy cập tab `#tab-matrix`.
  2. Bấm nút áp dụng lần lượt: `Preset 1 (Chuẩn TN THPT 2025)`, `Preset 2 (Kiểm tra Định kỳ)`, `Preset 3 (Kiểm tra Cuối kỳ)`.
- **Kết quả kỳ vọng:**
  - Preset 1: Điền đúng 34 câu, 10.0đ (12 TN đơn, 4 Đúng/Sai, 6 Trả lời ngắn), tỷ lệ Bloom đạt 40% Biết - 30% Hiểu - 30% Vận dụng.
  - Preset 2: Điền đúng 20 câu, 10.0đ (12 TN đơn, 4 Đúng/Sai, 4 Trả lời ngắn).
  - Preset 3: Điền đúng 28 câu, 10.0đ (16 TN đơn, 4 Đúng/Sai, 8 Trả lời ngắn).
  - Lưới ma trận render mượt mà, không gián đoạn giao diện.

#### TC-MATRIX-02: Tính toán Thời gian thực & Cảnh báo Tỷ lệ Bloom
- **Mô tả:** Kiểm tra cơ chế tự động tính tổng câu, tổng điểm từng dòng/cột và nhãn cảnh báo Bloom khi người dùng thay đổi giá trị ô ma trận.
- **Các bước thực hiện:**
  1. Thay đổi số lượng câu hỏi ở ô Biết thành 20 câu, Hiểu 2 câu, Vận dụng 2 câu.
- **Kết quả kỳ vọng:**
  - Tổng câu và tổng điểm các dòng/cột cập nhật tức thì.
  - Thanh tiến trình Bloom chuyển màu hổ phách kèm nhãn cảnh báo: "CẢNH BÁO: Tỷ lệ phân bố Bloom lệch so với chuẩn TT 22".

#### TC-MATRIX-03: Đối soát Tồn kho Thời gian thực (Live Inventory Checker)
- **Mô tả:** Kiểm tra tính năng đối soát số lượng câu hỏi thực tế trong CSDL Question Bank cho từng ô ma trận.
- **Các bước thực hiện:**
  1. Gọi API `POST /api/v1/matrix/{id}/check-availability` hoặc kích hoạt kiểm tra trên giao diện.
- **Kết quả kỳ vọng:**
  - Các ô có đủ câu hỏi APPROVED hiển thị badge xanh (`Kho: X/Y câu (Đủ)`).
  - Các ô thiếu câu hiển thị badge đỏ (`Kho: X/Y câu (Thiếu Z câu)`).
  - Trả về danh sách cảnh báo chi tiết các ô bị thiếu.

#### TC-MATRIX-04: Xuất bản Bản Đặc tả Ma trận Đề thi (PDF / CSV UTF-8 BOM / JSON)
- **Mô tả:** Kiểm tra endpoint xuất bản bản đặc tả ma trận đề thi.
- **Các bước thực hiện:**
  1. Gửi request `GET /api/v1/matrix/{id}/spec?format=json`.
  2. Gửi request `GET /api/v1/matrix/{id}/spec?format=csv`.
  3. Gửi request `GET /api/v1/matrix/{id}/spec?format=pdf`.
- **Kết quả kỳ vọng:**
  - Format JSON trả về cấu trúc ma trận, phân bổ YCCĐ và tồn kho.
  - Format CSV có chứa tiền tố UTF-8 BOM (`\ufeff`), mở bằng Excel tiếng Việt không bị lỗi font.
  - Format PDF trả về file Vector PDF chuẩn in ấn A4 Portrait gồm Khung ma trận 2D và Bảng đặc tả chi tiết.

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
  - Tỷ lệ Option Anchor Rule đạt 100%.

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

#### TC-SHUFFLE-03: Hoán đổi Câu hỏi Đề Gốc Tương đương (In-Place Question Swap Engine)
- **Mô tả:** Kiểm tra tính năng đổi một câu hỏi bất kỳ trong MasterExam sang một câu hỏi khác cùng YCCĐ từ ngân hàng câu hỏi.
- **Các bước thực hiện:**
  1. Chọn Câu 1 trong MasterExam.
  2. Gọi `GET /api/v1/exams/{master_id}/items/{item_id}/replacement-candidates`.
  3. Chọn một câu ứng viên và gọi `POST /api/v1/exams/{master_id}/items/{item_id}/swap`.
- **Kết quả kỳ vọng:**
  - Danh sách ứng viên trả về chỉ gồm các câu có cùng YCCĐ, cùng cognitive_level, cùng item_format và chưa có trong đề gốc.
  - API swap thành công, cập nhật câu hỏi mới vào MasterExamItem.
  - Các ExamVariant cũ tự động bị xóa bỏ để buộc người dùng trộn lại.

#### TC-SHUFFLE-04: Bảo toàn Phân đoạn (Section Integrity)
- **Mô tả:** Kiểm tra các câu hỏi chỉ được đảo trong cùng một Phần theo QĐ 764.
- **Kết quả kỳ vọng:**
  - Phần I chỉ chứa câu SINGLE_CHOICE đảo thứ tự nội bộ.
  - Phần II chỉ chứa câu TRUE_FALSE_GROUP đảo thứ tự nội bộ.
  - Phần III chỉ chứa câu SHORT_ANSWER đảo thứ tự nội bộ.
  - Tuyệt đối không hoán vị câu hỏi khác phần sang nhau.

#### TC-SHUFFLE-05: Lập Ma trận Đáp án Tổng hợp & Đóng gói Ấn phẩm (.ZIP / .PDF)
- **Mô tả:** Kiểm tra xuất bản bảng ma trận đáp án và đóng gói tệp ZIP.
- **Các bước thực hiện:**
  1. Gọi `GET /api/v1/exams/{master_id}/key-matrix`.
  2. Gọi `GET /api/v1/exams/{master_id}/export-pdf?variant_code=101`.
  3. Gọi `GET /api/v1/exams/{master_id}/export-zip?format=pdf`.
- **Kết quả kỳ vọng:**
  - Bảng ma trận đáp án hiển thị đầy đủ đối chiếu giữa Đề gốc và 4 mã đề.
  - File PDF tải về có layout 2 cột rõ ràng, chuẩn font in ấn.
  - File ZIP giải nén có đầy đủ 5 thành phần: `De_{code}.pdf`, `LoiGiai_{code}.pdf`, `BangDapAn_TongHop.pdf`, `BangDapAn_TongHop.csv` (UTF-8 BOM), `Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`.

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

#### TC-COMP-07: Độ Tương Phản Màu Sắc Ô Nhập Chat & Compact Bar Trên Dark Mode
- **Mô tả:** Kiểm tra trường nhập liệu `#composer-compact-input` và `#composer-chat-input` hiển thị văn bản màu trắng sáng `#f8fafc` hoặc `#ffffff` và con trỏ caret màu xanh Apple `#38bdf8` trên nền tối, không bị rule toàn cục ghi đè thành chữ đen `#1d1d1f`.
- **Kết quả kỳ vọng:** Văn bản hiển thị rõ nét ngay khi gõ không cần bôi đen (select), tỷ lệ tương phản WCAG 2.1 AA đạt chuẩn.

#### TC-COMP-08: Chuyển Tiếp & Chẩn Đoán Log Lỗi Biên Dịch LaTeX (compile_error_log)
- **Mô tả:** Gửi yêu cầu biên dịch mã LaTeX lỗi cú pháp (`\badcommand`), nhận diện chuỗi log lỗi trả về, sau đó gửi prompt yêu cầu "sửa lỗi giúp tôi". Kiểm tra payload gửi tới `/api/v1/composer/chat` có trường `compile_error_log`.
- **Kết quả kỳ vọng:** AI Copilot nhận diện mã lỗi, chẩn đoán chính xác nguyên nhân, trả về khối diff sửa dòng lỗi để khắc phục triệt để.

#### TC-COMP-09: Động Cơ Thay Thế Dòng Mờ & Giao Diện Inline Diff Overlay Trên Editor
- **Mô tả:** Khi AI đề xuất diff sửa đổi, kiểm tra giao diện Inline Diff Overlay hiển thị trực tiếp tại đúng vị trí dòng mã nguồn trên textarea (khối đỏ `-`, khối xanh `+`, nút `Keep / Đồng ý` và `Undo / Từ chối`). Khi nhấn `[Đồng ý]`, kích hoạt 5-Tier Fuzzy Replacement Engine.
- **Kết quả kỳ vọng:** Mã nguồn được thay thế chuẩn xác 100%, không xuất hiện toast cảnh báo "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại", tự động kích hoạt `compile(true)`.

#### TC-COMP-10: Hiệu Năng Gửi Prompt, Xóa Sạch Lạc Quan (Optimistic Input Reset) & Box Chat Chuẩn Apple HIG
- **Mô tả:** Kiểm tra hành động nhấn Enter hoặc click nút gửi prompt từ cả thanh compact bar và popup chat:
  1. *Cơ chế Xóa Sạch Lạc Quan:* Ngay tại thời điểm kích hoạt gửi ($t = 0\text{ms}$), kiểm tra giá trị của cả `#composer-compact-input` và `#composer-chat-input` lập tức được xóa trắng (`value = ''`), loại bỏ triệt để hiện tượng lưu kẹt text cũ (Ảnh 1).
  2. Kiểm tra `submitFromCompact()` không truyền lại prompt đã gửi vào `prefillPrompt` của `openAIPopup()`, đảm bảo ô chat popup khi mở ra hoàn toàn sạch sẽ.
  3. Phản hồi optimistic UI lập tức ($\le 16$ms), ẩn compact bar và mở bung popup chat với hiệu ứng hardware transition mượt mà, cuộn mượt đến đáy và hiển thị typing indicator không giật khung hình.
- **Kết quả kỳ vọng:** Thao tác gửi tức thì không độ trễ, ô nhập rỗng ngay lập tức với con trỏ caret màu xanh Apple `#38bdf8` sẵn sàng nhận lệnh mới, 0 lỗi JavaScript màu đỏ trong Console DevTools.

#### TC-COMP-11: Tính Toàn Vẹn Của API Chat & Bóc Tách Diff Độc Lập Hiển Thị Frontend
- **Mô tả:** Kiểm tra API `/api/v1/composer/chat` bảo toàn tính toàn vẹn của cấu trúc `ChatResponse` (bao gồm `reply`, `diff`, `suggested_latex`). Cơ chế bóc tách diff (`extract_diff_from_text`) hoàn toàn phân tách giữa nội dung giải thích tự nhiên hiển thị trong luồng hội thoại chat và payload diff vận hành trên khung soạn thảo (`DiffSuggestion` với `old_text` và `new_text`).
- **Kết quả kỳ vọng:** Phản hồi API luôn trả về HTTP 200, trường `reply` nguyên vẹn nội dung đàm thoại cho chat bubble, trường `diff` chứa lát cắt mã nguồn chính xác khớp ký tự trong editor (`old_text` tồn tại trong buffer hiện tại) và mã thay thế `new_text` sạch sẽ (không chứa tiền tố đánh dấu `- ` hay `+ `). Xử lý an toàn các ký tự toán đặc biệt LaTeX, câu hỏi trắc nghiệm `\choice` đơn dòng và đa dòng, đổi cỡ chữ, và các tài liệu lớn (>25k ký tự) mà không gây lỗi máy chủ.

#### TC-COMP-12: Hiển Thị Đề Xuất Diff Độc Quyền Trên Khung Code Editor (Loại Bỏ Hoàn Toàn Diff Widget Trong Bubble Chat)
- **Mô tả:** Khi AI Copilot phản hồi một đề xuất diff thay đổi mã nguồn (ví dụ: đổi font size, sửa câu hỏi trắc nghiệm, sửa lỗi cú pháp):
  1. Kiểm tra bong bóng chat của Assistant (`#composer-chat-messages`): Chỉ hiển thị văn bản trả lời tự nhiên của AI; xác nhận **không xuất hiện phần tử widget diff** (`.diff-block-wrapper`, khối chứa nút "✔ Đồng ý áp dụng" và "✖ Từ chối" trong bong bóng chat).
  2. Kiểm tra vùng Code Editor (`#composer-editor-pane`): Xác nhận hiển thị chính xác khối diff thông qua Inline Diff Overlay (`#composer-inline-diff-overlay`) và/hoặc Top Diff Banner (`#composer-pending-diff-banner`) kèm 2 nút thao tác trực tiếp `[Keep / Đồng ý]` và `[Undo / Từ chối]`.
- **Kết quả kỳ vọng:** Khung chat sạch sẽ, không có widget diff trùng lặp gây rối mắt; toàn bộ thao tác duyệt diff được tập trung trực tiếp trên mã nguồn editor; khi bấm Keep/Undo trên editor thì diff biến mất và mã nguồn được cập nhật chính xác.

#### TC-COMP-13: Quản Lý Khởi Tạo Phiên Chat Mới Sạch Sẽ & Tra Cứu Lịch Sử Phiên Cũ (Session Lifecycle & Clean Workspace)
- **Mô tả:** 
  1. Khi người dùng mở trang `/composer` hoặc nhấn nút "Bắt đầu hội thoại mới" (`newChat`): Kiểm tra khung chat active bắt đầu sạch sẽ với duy nhất 1 tin nhắn chào mặc định từ Quesy Copilot, không nạp lại tin nhắn từ phiên cũ.
  2. Kiểm tra nếu phiên trước đó đã có tin nhắn trao đổi, toàn bộ phiên đó được lưu trữ tự động vào mảng phiên cũ `quesy_composer_chat_sessions` trong `localStorage`.
  3. Khi nhấp nút **`[Lịch sử]`** (`#composer-ai-history-btn`), mở giao diện `#composer-ai-history-panel` hiển thị danh sách các phiên cũ kèm thời gian và tóm tắt prompt. Nhấp vào một phiên hoặc câu lệnh cũ sẽ điền nội dung vào ô nhập hoặc tải lại phiên cũ. Nhấp "✕ Đóng" quay lại phiên hiện tại.
- **Kết quả kỳ vọng:** Mỗi phiên mới luôn sạch sẽ tinh giản; lịch sử các phiên trước không bị mất mà được lưu trữ khoa học trong ngăn kéo Lịch sử.

#### TC-COMP-14: Kéo Thả Điều Chỉnh Độ Cao Linh Hoạt Box Trợ Lý Soạn Thảo (Vertical Drag Resize & Unified Single Pill Handle)
- **Mô tả:** Kiểm tra khả năng co giãn độ cao của Box Trợ lý Soạn thảo (`#composer-ai-popup`) theo phương thẳng đứng với thanh pill hợp nhất:
  1. Kiểm tra DOM và giao diện: Xác nhận **chỉ tồn tại duy nhất 1 thanh ngang viên thuốc** (`#composer-ai-resize-handle`) ở trung tâm header của popup trợ lý. Không còn thanh pill phụ bên trên mép popup.
  2. Thao tác nhấn giữ chuột (`mousedown`) trên thanh pill handle `#composer-ai-resize-handle` và kéo chuột lên/xuống (`mousemove`).
  3. Đo đạc chiều cao `style.height` của `#composer-ai-popup`: Độ cao thay đổi mượt mà theo thời gian thực (60 FPS, không gián đoạn), bị giới hạn trong khoảng an toàn $180\text{px}$ đến $92\%$ chiều cao khung editor.
  4. Kiểm tra nhấp chuột đơn (click) hoặc nhấp đúp (dblclick) vào pill handle khi không kéo: Chuyển đổi nhanh (toggle) độ cao giữa 56% và 78%.
  5. Sau khi kéo thả, tải lại trang (F5): Kiểm tra độ cao tùy chỉnh được khôi phục từ `localStorage` (`quesy_composer_ai_height`).
- **Kết quả kỳ vọng:** Giao diện tối giản chuẩn Apple HIG với duy nhất 1 thanh pill; co giãn độ cao trực quan mượt mà, không làm vỡ bố cục editor hay che khuất toolbar đỉnh.

#### TC-COMP-15: Kéo Thả Thanh Phân Tách Ngang 2 Cột Editor & Live Preview Chuẩn Apple HIG (#composer-split-resizer)
- **Mô tả:** Kiểm tra thanh phân tách ngang `#composer-split-resizer` (class `composer-col-splitter`) được tái thiết kế chuẩn Apple HIG với khoảng cách đệm thẩm mỹ, không đè sát viền box soạn thảo (Ảnh 2):
  1. *Kiểm tra Bố Cục & Khoảng Cách Đệm:* Rãnh phân tách có độ rộng công thái học `w-3.5` / `w-4` (14-16px) với lề `mx-1` / `mx-1.5`. Trục viên thuốc cách đều viền Cột Soạn thảo và Cột Live Preview từ 6px đến 8px, không chạm đè lên viền card bên cạnh.
  2. *Kiểm tra Kiểu Dáng Apple Capsule:* Vạch kéo có dạng viên thuốc `w-1 h-9 rounded-full bg-slate-300 dark:bg-[#34415e]`. Khi hover, đổi màu xanh Apple `#0071e3`, tỏa quầng sáng vi mô `shadow-[0_0_8px_rgba(0,113,227,0.35)]`, vạch mở rộng nhẹ `scale-y-110`. Vùng hover mềm bo góc `rounded-lg` nằm gọn trong rãnh đệm.
  3. *Kiểm tra Kéo Thả:* Nhấn giữ chuột (`mousedown`) và kéo sang trái/phải (`mousemove`): Chiều rộng cột trái (`#composer-left-col`) thay đổi mượt mà 60 FPS, tỷ lệ co giãn được giới hạn nghiêm ngặt trong khoảng $25\%$ đến $75\%$. Tấm chắn con trỏ `pointer-events: none` được kích hoạt trên canvas PDF.
  4. *Kiểm tra Nháy Đúp:* Nháy đúp chuột (`dblclick`) vào resizer lập tức đặt lại tỷ lệ vàng 60% Left : 40% Right và kích hoạt `fitToWidth(true)`.
  5. *Lưu Trữ Bền Vững:* Khi thả chuột (`mouseup`), tỷ lệ mới được lưu vào `localStorage` (`quesy_composer_split_ratio`). Tải lại trang (F5), tỷ lệ chia cột được bảo toàn nguyên vẹn.
- **Kết quả kỳ vọng:** Giao diện tinh tế chuẩn Apple HIG, khoảng cách đệm thông thoáng không dính viền, thao tác chia cột mượt mà 60 FPS, tỷ lệ phản hồi chính xác, 0 lỗi console.

#### TC-COMP-16: Tự Động Co Giãn PDF Theo Chiều Rộng Cột & Khung Cuộn Ngang An Toàn (PDF Auto Fit-to-Width & Horizontal Scroll Resiliency)
- **Mô tả:** Kiểm tra cơ chế tự động co giãn kích thước trang PDF khi chiều rộng cột thay đổi và tính năng cuộn ngang không xén lề phải:
  1. Biên dịch tài liệu mẫu LaTeX sang PDF.
  2. Kéo thanh splitter `#composer-col-splitter` sang phải để nới rộng cột Editor lên $75\%$ (thu hẹp cột Live Preview xuống $25\%$):
     - Xác nhận tỷ lệ hiển thị trang PDF tự động co nhỏ lại tương ứng với bề rộng cột khả dụng (`fitZoom`), các dòng chữ và công thức toán học co giãn đều đặn theo thời gian thực mà không bị tràn viền hay xén mất mép phải.
  3. Kiểm tra thuộc tính CSS của `#composer-pdf-scroll-container`:
     - Xác nhận thuộc tính cuộn là `overflow-x: auto` (không phải `overflow-x-hidden`).
  4. Thao tác phóng to tài liệu lên mức zoom cao ($150\% - 200\%$):
     - Xác nhận xuất hiện thanh cuộn ngang trơn tru.
     - Người dùng có thể cuộn ngang sang phải để xem trọn vẹn toàn bộ nội dung mép phải của tài liệu mà không bị cắt cụt.
  5. Nhấp nút `1:1` (hoặc `resetZoom`):
     - Hệ thống tự động căn khít chiều ngang tài liệu vừa vặn với kích thước cột preview hiện thời (`isAutoFit = true`).
- **Kết quả kỳ vọng:** Tài liệu PDF luôn co giãn linh hoạt theo độ rộng khung nhìn; $100\%$ nội dung hiển thị trọn vẹn không bị xén mép phải.

#### TC-COMP-17: Thuật Toán Phóng To / Thu Nhỏ Thông Minh Theo Điểm Neo Chuột & Trọng Tâm Viewport (Smart Zoom-to-Point & Center Anchor)
- **Mô tả:** Kiểm tra thuật toán zoom-to-point thông minh, loại bỏ triệt để hiện tượng giật màn hình hoặc nhảy về góc trên cùng bên trái $(0, 0)$:
  1. *Kiểm tra Zoom theo Con trỏ Chuột (Cursor Anchor):*
     - Di chuyển con trỏ chuột đến một công thức toán cụ thể ở giữa trang PDF (ví dụ bảng biến thiên hoặc câu hỏi 2).
     - Giữ phím `Ctrl` (hoặc `Cmd`) và lăn chuột phóng to (`wheel delta < 0`):
     - Xác nhận điểm công thức toán đang nằm dưới con trỏ chuột được ghim cố định ngay dưới con trỏ, tài liệu phóng to xung quanh điểm này.
     - Tuyệt đối không có hiện tượng trang bị giật văng về góc $(0, 0)$.
  2. *Kiểm tra Zoom theo Trọng tâm Màn hình (Center Anchor):*
     - Di chuyển con trỏ chuột ra khỏi tài liệu PDF (ví dụ nhấp vào nút `+` hoặc `-` trên thanh công cụ nổi góc trên bên phải):
     - Nhấp nhiều lần vào nút `+` (phóng to) và `-` (thu nhỏ):
     - Xác nhận tài liệu phóng to / thu nhỏ đồng tâm từ chính giữa khung nhìn của người dùng (Viewport Center). Khung nhìn không bị lệch sang góc trái hay trôi dạt.
  3. *Kiểm tra Khôi phục Tọa độ Cuộn Khi Re-render:*
     - Sau khi dừng thao tác zoom 100ms, hàm `renderAllPages` vẽ lại canvas ở độ phân giải retina thực:
     - Xác nhận vị trí cuộn `scrollTop` và `scrollLeft` được bảo toàn ổn định, không xuất hiện hiện tượng chớp nháy hoặc nhảy giật vị trí cuộn.
- **Kết quả kỳ vọng:** Trải nghiệm phóng to / thu nhỏ mượt mà chuẩn Apple HIG; bảo toàn điểm neo chính xác tuyệt đối; 0 lỗi Console.

#### TC-COMP-18: Bóc Tách Đa Khối Diff (`extract_all_diffs_from_text`) & Hợp Đồng Schema API Đa Khối
- **Mô tả:** Kiểm tra khả năng trích xuất toàn bộ các khối diff khi AI trả về nhiều đề xuất thay đổi trong một lượt (ví dụ: đổi font size sang 12pt VÀ đổi đáp án câu trắc nghiệm VÀ sửa lỗi cú pháp):
  1. Gửi phản hồi chứa 2 hoặc nhiều khối ````diff ... ```` hoặc block replaces tới API và hàm `extract_all_diffs_from_text`.
  2. Kiểm tra `ChatResponse` trả về trường `diffs: List[DiffSuggestion]` có số lượng $N \ge 2$, trường `diff` lưu diff đầu tiên (`diffs[0]`) để giữ tương thích ngược.
  3. Kiểm tra tính toàn vẹn của từng đối tượng `DiffSuggestion` (`action`, `old_text`, `new_text`, `description`), xác nhận không bị xáo trộn nội dung giữa các khối.
- **Kết quả kỳ vọng:** API và hàm trích xuất nhận diện trọn vẹn 100% các khối diff trong nội dung trả về, 0 khối diff bị bỏ sót.

#### TC-COMP-19: Giao Diện Duyệt Tuần Tự Đa Diff (1/N Stepper, Keep/Undo) & Nút Áp Dụng Tất Cả (Apply All)
- **Mô tả:** Kiểm tra cỗ máy trạng thái và giao diện duyệt đa diff trên cả Top Banner và Inline Overlay (Ảnh 3):
  1. *Kiểm tra Bộ Đếm Động (Capsule Counter):* Huy hiệu định vị hiển thị chính xác `${currentDiffIndex + 1}/${pendingDiffs.length}` (ví dụ `1/3`, `2/3`, `3/3`), không còn hiển thị số `1/1` cứng.
  2. *Kiểm tra Điều Hướng Tuần Tự (Prev/Next Stepper):*
     - Click nút **`[Sau >]`**: Con trỏ `currentDiffIndex` tăng lên, editor tự động cuộn đến dòng của diff tiếp theo và bôi đen vị trí tương ứng. Nút `[Sau >]` bị disabled ở mục cuối.
     - Click nút **`[< Trước]`**: Nhảy lùi về diff trước đó. Bị disabled ở mục đầu tiên.
  3. *Kiểm tra Chấp nhận Từng Khối (`[Keep / Đồng ý]`):*
     - Click `[Keep]`: Diff hiện tại được áp dụng vào mã nguồn, loại bỏ khỏi `pendingDiffs`. Editor tự động chuyển sang diff kế tiếp trong danh sách.
  4. *Kiểm tra Từ chối Từng Khối (`[Undo / Từ chối]`):*
     - Click `[Undo]`: Bỏ qua diff hiện tại, chuyển sang diff kế tiếp mà không sửa đổi mã nguồn tại vị trí đó.
  5. *Kiểm tra [Áp Dụng Tất Cả] (`applyAllPendingDiffs` - Ảnh 3):*
     - Nút `[Áp dụng tất cả]` hiển thị nổi bật với nền xanh Apple khi `pendingDiffs.length > 1`.
     - Click `[Áp dụng tất cả]`: Hệ thống áp dụng tuần tự toàn bộ $N$ khối diff vào mã nguồn, cập nhật editor, kích hoạt `compile(true)` một lần duy nhất, đóng toàn bộ banner/overlay và hiển thị toast thông báo thành công.
- **Kết quả kỳ vọng:** Trải nghiệm duyệt đa diff mượt mà chuẩn Cursor/VS Code, điều hướng 1/N trực quan, áp dụng hàng loạt chính xác 100%, 0 lỗi Console.

#### TC-COMP-20: Bóc Tách Khối Câu Hỏi Thứ N trong LaTeX (`find_question_block`)
- **Mô tả:** Kiểm tra độ chính xác của hàm trích xuất câu hỏi thứ $n$ trên các tài liệu LaTeX thực tế:
  1. *Trường hợp chuẩn `ex_test.sty`:* Tài liệu gồm 5 khối `\begin{ex} ... \end{ex}`. Gọi `find_question_block(latex, 1)` trả về chính xác toàn bộ khối câu 1; gọi `find_question_block(latex, 3)` trả về chính xác khối câu 3.
  2. *Trường hợp chuẩn đánh số cổ điển:* Tài liệu sử dụng `\textbf{Câu 1.}`, `\textbf{Câu 2.}`. Hàm bóc tách chuẩn xác phạm vi câu tương ứng.
  3. *Trường hợp chỉ số vượt giới hạn:* Gọi câu thứ 10 trong tài liệu chỉ có 4 câu trả về `None` an toàn.
- **Kết quả kỳ vọng:** Lát cắt chuỗi trả về khớp 100% từng ký tự với vị trí trong `current_latex`, không gây lỗi ngoại lệ.

#### TC-COMP-21: Gắn Kết Diff Thông Minh Khi Thay Thế Câu Hỏi (Smart Diff Binding)
- **Mô tả:** Kiểm tra cơ chế tự động liên kết khi prompt yêu cầu thay thế câu hỏi (ví dụ: *"Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"* hoặc *"Thay câu 2 bằng câu khác"*):
  1. Gửi prompt thay thế câu 1 cùng tài liệu LaTeX mẫu có chứa Câu 1.
  2. Dù nội dung câu hỏi mới hoàn toàn khác biệt so với câu 1 cũ (khiến `SequenceMatcher` thông thường thất bại), hệ thống tự động gán `old_text = câu 1 cũ` và `new_text = câu mới`.
  3. `ChatResponse` trả về `diff` hợp lệ với mô tả *"Thay thế câu 1 bằng câu hỏi mới"*.
- **Kết quả kỳ vọng:** API trả về HTTP 200, trường `diff` và `diffs` chứa đúng lát cắt của câu 1 cũ, sẵn sàng hiển thị trên editor.

#### TC-COMP-22: Hiển Thị Chat Bubble An Toàn & Bảo Toàn Khối Mã Nguồn (Safe Chat Bubble Rendering)
- **Mô tả:** Kiểm tra logic render giao diện chat bubble (`formatAssistantContent`) trong cả 2 kịch bản có và không có diff:
  1. *Kịch bản có diff hợp lệ:* Giao diện ẩn khối diff trong chat bubble, gắn badge *"Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn"*, và kích hoạt banner/overlay trên editor.
  2. *Kịch bản không có diff hợp lệ (hoặc diff rỗng):* Giao diện KHÔNG ẩn khối mã, KHÔNG hiển thị badge giả tạo; hiển thị trọn vẹn khối mã LaTeX kèm 3 nút bấm tương tác: `[📥 Chèn vào con trỏ]`, `[📋 Sao chép]`, và `[🔄 Áp dụng thay thế]`.
- **Kết quả kỳ vọng:** 0% mã nguồn bị nuốt mất trong chat bubble; người dùng luôn có công cụ thao tác với mã được sinh ra.

#### TC-COMP-23: Biên Dịch Đề Thi Tinh Gọn Không Preamble (Preamble-Free ex_test Body)
- **Mô tả:** Gửi yêu cầu biên dịch `POST /api/v1/composer/compile` với nội dung `latex_code` chỉ chứa các câu hỏi `\begin{ex}...\end{ex}` chuẩn `ex_test.sty`, hoàn toàn không có `\documentclass` hay `\usepackage`.
- **Kết quả kỳ vọng:** HTTP 200, phản hồi `success: true`, sinh tệp PDF hợp lệ với đầy đủ font CMU Serif, đồ thị TikZ và bảng biến thiên `tkz-tab` nhờ cơ chế Canonical Preamble Injection ngầm định.

#### TC-COMP-24: Động Cơ Điều Khiển Chế Độ Đề Thi / Lời Giải ([dethi] vs [loigiai]) Qua API Mode Flag
- **Mô tả:** Kiểm tra tham số `mode` trong `CompileRequest`:
  1. Gửi cùng một đoạn mã câu hỏi với `mode = "loigiai"`: Xác nhận file PDF sinh ra hiển thị nội dung môi trường `\begin{loigiai}`.
  2. Gửi với `mode = "dethi"`: Xác nhận file PDF sinh ra ẩn toàn bộ lời giải và không đánh dấu đáp án `\True`.
  3. Kiểm tra khóa băm cache: `code_hash` của hai chế độ khác nhau hoàn toàn, không xảy ra xung đột hay trả về kết quả cache sai chế độ.
- **Kết quả kỳ vọng:** Chuyển đổi chính xác 100% giữa 2 chế độ mà không cần sửa đổi mã nguồn của người dùng.

#### TC-COMP-25: Tính Tương Thích Ngược Với Tài Liệu Toàn Phần Chứa \documentclass
- **Mô tả:** Gửi mã nguồn LaTeX hoàn chỉnh (chứa `\documentclass[11pt,a4paper]{article}`, `\usepackage{fontspec}`, `\begin{document}...\end{document}`) tới endpoint `/api/v1/composer/compile`.
- **Kết quả kỳ vọng:** Hệ thống phát hiện `\documentclass`, tự động kích hoạt nhánh Full Document Parser, bảo toàn các gói lệnh tùy chỉnh, tự động bổ sung gói thiếu nếu có dùng `ex_test`, biên dịch thành công 100% ra PDF.

#### TC-COMP-26: Xuất Bản Mã Nguồn TeX Tự Động Đóng Gói Preamble Chuẩn (Full TeX Packaging)
- **Mô tả:** Kiểm tra logic xuất bản mã nguồn `.tex` khi người dùng nhấn "Tải mã nguồn TeX": Nếu mã hiện thời trên editor không chứa `\documentclass`, hệ thống tự động bọc Canonical Preamble và `\begin{document}...\end{document}` trước khi xuất file.
- **Kết quả kỳ vọng:** File `.tex` tải xuống độc lập, tự chứa đầy đủ preamble, có thể mở và biên dịch XeLaTeX thành công ngay trên TeXLive / Overleaf mà không bị thiếu gói lệnh.

#### TC-COMP-27: Tích Hợp AI Provider Gemini (Google v1beta OpenAI Compatibility) & Cơ Chế Dự Phòng Fallback
- **Mô tả:** Kiểm tra Composer Chat API `/api/v1/composer/chat` khi `provider` được cấu hình là `"gemini"`.
  1. Xác nhận endpoint gọi chính xác tới `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions`.
  2. Xác nhận khả năng bóc tách khối diff (thay thế dòng/đổi tiêu đề/câu hỏi) từ phản hồi chuẩn Google Gemini.
  3. Xác nhận xử lý an toàn, tự động kích hoạt Offline Rule-based Fallback khi `AI_API_KEY` rỗng (môi trường CI runner) hoặc khi mạng gặp sự cố.
- **Kết quả kỳ vọng:** HTTP 200, phản hồi có cấu trúc hợp lệ (`reply`, `diff`, `diffs`), 100% test cases pass trên cả runner CI và máy dev cục bộ.

#### TC-COMP-28: Kiểm Thử Toàn Diện Bộ Form Mẫu Menu THÊM & Biểu Mẫu TEMPLATES Không Lỗi Cú Pháp (Full Template Suite Zero-Error Compilation)
- **Mô tả:** Kiểm tra toàn bộ 12 form mẫu trong menu `THÊM ▾` (`EX_TEST_TEMPLATES`) và toàn bộ các biểu mẫu trong backend `TEMPLATES`:
  1. Xác nhận không còn lỗi chuỗi escape `\n` trong JavaScript template strings; chèn vào editor xuống dòng thực tế sạch sẽ, không sinh lệnh `\n{}` làm lỗi XeTeX.
  2. Xác nhận mẫu `dethi_quocgia_full` sửa sạch lỗi `\rule` (không còn `\nule`), `\choiceTF[1]` (không còn `\choiceTF` thừa `\\` và số 5 vô nghĩa).
  3. Xác nhận mẫu `dungsai` dùng lệnh chuẩn `\choiceTF[1]`, loại bỏ lệnh nội bộ `\choiceTFt` và thay `\loigiai{...}` bằng `\begin{loigiai}...\end{loigiai}`.
  4. Xác nhận mẫu `ex_test_standard_exam` sửa triệt để lỗi `\right|_0^2` (không còn mất chữ r thành `ight|_0^2`).
  5. Biên dịch thử nghiệm lần lượt từng form mẫu qua engine Tectonic XeTeX / Chromium.
- **Kết quả kỳ vọng:** 100% form mẫu biên dịch thành công (`success = true`), không phát sinh bất kỳ lỗi TeX nào.

#### TC-COMP-29: Kiểm Thử Cơ Chế AI Copilot Đọc Log Lỗi Biên Dịch, Ánh Xạ Dòng Lỗi Preamble-Free & Tự Động Sinh Diff Sửa Lỗi (Compile Error Reading, Line Offset & Syntax Repair)
- **Mô tả:** Kiểm tra khả năng tiếp nhận và xử lý chuỗi `compile_error` của AI Copilot:
  1. Gửi request `POST /api/v1/composer/chat` với payload chứa `compile_error` kèm câu lệnh "fix lỗi" hoặc "sửa lỗi giúp tôi".
  2. Kiểm tra bộ chẩn đoán `diagnose_compile_error`:
     - Bóc tách chính xác số dòng lỗi `L_comp` từ log compiler (`error: document.tex:(\d+):` hoặc `l\.(\d+)`).
     - Ánh xạ chính xác vị trí dòng trong editor không preamble: `L_user = L_comp - 11`.
     - Phân tích chuẩn xác 5 nhóm lỗi kinh điển: `There's no line here to end` (xóa `\\`), `Undefined control sequence` (`\ule` -> `\rule`, `\choiceTFt` -> `\choiceTF[1]`, `ight|` -> `\right|`), `Missing $ inserted` (bọc `$`), `Missing \right.`, và `Environment undefined`.
  3. Kiểm tra phản hồi `ChatResponse`: trường `reply` giải thích nguyên nhân rõ ràng và trường `diff` chứa lát cắt thay thế chính xác dòng lỗi trong tài liệu hiện tại.
- **Kết quả kỳ vọng:** AI Copilot đọc hiểu log lỗi 100%, trả về khối diff chính xác khớp vị trí dòng trong editor, bấm [Đồng ý] sửa dứt điểm lỗi biên dịch.

#### TC-COMP-30: Kiểm Thử Chuẩn Mực Câu Hỏi Đúng/Sai \choiceTF[1] Dàn 1 Cột Thẳng Đứng (True/False Single-Column 100% Width & Trailing Backslash Prohibition)
- **Mô tả:** Kiểm tra quy chuẩn câu hỏi Đúng/Sai theo chuẩn Thông tư 32 & QĐ 764:
  1. Toàn bộ mã nguồn câu hỏi Đúng/Sai sử dụng lệnh `\choiceTF[1]` với tham số `[1]` bắt buộc.
  2. Xác nhận tuyệt đối không có dấu `\\` sau các dấu ngoặc nhọn `{...}` của các khẳng định.
  3. Kiểm tra bộ render HTML preview (`compile_latex_source_to_html`): 4 khẳng định a), b), c), d) hiển thị thành 4 hàng riêng biệt, mỗi hàng chiếm 100% chiều rộng (không chia 2 cột hay 4 cột) kèm nhãn a), b), c), d) và biểu tượng [Đ]/[S].
- **Kết quả kỳ vọng:** Bố cục đề thi chuẩn mực, 1 cột thẳng đứng rõ ràng, không vỡ layout trên cả bản in PDF và xem trước HTML.

#### TC-COMP-31: Đính Kèm, Dán Clipboard (Ctrl+V) & Kéo Thả Ảnh vào Trợ Lý AI Copilot (Client-Side Image Attachment & UX)
- **Mô tả:** Kiểm tra các phương thức nhập ảnh vào giao diện AI Copilot trên trình duyệt:
  1. *Đính kèm từ Compact Bar:* Nhấp nút icon ảnh hoặc dán ảnh clipboard (`Ctrl+V`) vào `#composer-compact-input`: Kiểm tra hệ thống tự động mở bung popup lớn `#composer-ai-popup`, đưa ảnh vào khay thumbnail `#composer-attached-images-container` và focus vào ô chat lớn `#composer-chat-input`.
  2. *Đính kèm từ Chat Popup:* Nhấp nút đính kèm ảnh trên toolbar của chat card, chọn 1 hoặc nhiều ảnh (`.png`, `.jpg`, `.webp`); hoặc nhấn `Ctrl+V` dán ảnh chụp màn hình; hoặc kéo thả file ảnh vào vùng chat (kiểm tra class viền sáng tím `.composer-drag-over`).
  3. *Tương tác Khay Thumbnail:* Mỗi ảnh hiển thị card bo góc tròn với kích thước 54px x 54px; nhấp nút (✕) gỡ bỏ ảnh thành công; nhấp vào ảnh mở modal Lightbox xem phóng to; bấm Esc hoặc click nền đóng Lightbox.
  4. *Render Bubble Chat & Reset Ô Nhập:* Khi bấm gửi, khay thumbnail được xóa sạch, bong bóng chat của user hiển thị tin nhắn kèm các ảnh đính kèm; lưu trữ bền vững vào lịch sử phiên `localStorage`.
- **Kết quả kỳ vọng:** Thao tác dán/upload/xóa ảnh mượt mà 60 FPS, không lỗi console, đúng chuẩn Apple HIG và vi tương tác Emil Kowalski.
- **Tự động hóa Pytest:** Đã được kiểm thử tự động tại `tests/test_composer.py::test_composer_multimodal_frontend_dom_elements`, `test_composer_multimodal_frontend_app_js_methods_and_flow`, và `test_composer_multimodal_css_styling`.

#### TC-COMP-32: Tính Toàn Vẹn Hợp Đồng API Chat Đa Phương Tiện (Multimodal Payload & Pydantic Schema)
- **Mô tả:** Kiểm tra schema và phản hồi của endpoint `POST /api/v1/composer/chat`:
  1. Gửi request có trường `images` chứa danh sách chuỗi Data URL Base64 (`data:image/png;base64,...`).
  2. Kiểm tra Pydantic model `ChatRequest` và `ChatMessage` tiếp nhận trường `images` mà không phát sinh lỗi validation 422.
  3. Kiểm tra tính tương thích ngược khi request không có trường `images` (mặc định rỗng `[]`), hệ thống vẫn xử lý bình thường.
- **Kết quả kỳ vọng:** API trả về mã trạng thái `200 OK`, bảo toàn cấu trúc `ChatResponse(reply, diff, diffs, suggested_latex)`.
- **Tự động hóa Pytest:** Đã được kiểm thử tự động tại `tests/test_composer.py::test_composer_pydantic_models_images_field` và `test_composer_chat_api_multimodal_empty_images_backward_compatibility`.

#### TC-COMP-33: Trợ Lý AI Phân Tích Hình Ảnh (TikZ / Bảng Biến Thiên) & Động Cơ Dự Phòng Offline Fallback
- **Mô tả:** Kiểm tra khả năng xử lý hình ảnh của AI Copilot:
  1. *Khi có AI Provider (Online Multi-modal):* Payload gửi tới external provider được đóng gói dưới dạng mảng các block `[{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img}}]`. AI nhận diện đề bài, xuất mã câu hỏi `ex_test.sty` và khối dựng đồ thị TikZ nét đen hoặc bảng biến thiên `tkz-tab`.
  2. *Khi ở chế độ Offline / Local Fallback (hoặc mất mạng):* Gửi request kèm `images` và prompt yêu cầu tạo đồ thị/bảng biến thiên/giải toán: Hệ thống nhận diện sự hiện diện của ảnh, phản hồi lời giải thích đã nhận ảnh thành công và tạo khối mã LaTeX/TikZ hoàn chỉnh để giáo viên chèn hoặc duyệt diff trực tiếp.
- **Kết quả kỳ vọng:** Không bao giờ ném lỗi 500 khi xử lý ảnh; cả 2 chế độ online và offline fallback đều cung cấp mã nguồn LaTeX/TikZ hợp lệ cho người dùng.
- **Tự động hóa Pytest:** Đã được kiểm thử tự động tại `tests/test_composer.py::test_composer_chat_api_multimodal_offline_fallback`, `test_composer_chat_api_multimodal_mocked_ai_single_image`, `test_composer_chat_api_multimodal_mocked_ai_multiple_images_and_history`, và `test_composer_chat_api_multimodal_mocked_ai_diff_extraction`.

#### TC-COMP-34: Tính Toán Dynamic Adaptive Compilation Timeout Cho Đề Thi Lớn
- **Mô tả:** Kiểm tra hàm tính toán timeout động `compute_compilation_timeout(latex_source: str)`:
  1. *Đề thi nhỏ/rỗng (0 TikZ, < 1000 ký tự):* Timeout trả về mức chặn dưới $60$ giây.
  2. *Đề thi trung bình (3 TikZ, 8.000 ký tự):* Tính đúng $45 + 3 \times 10 + 8000 // 250 = 107$ giây.
  3. *Đề thi lớn chuẩn THPT Việt Đức (~24.000 ký tự, 11 TikZ/tkz-tab):* Tính toán chạm mức chặn trên an toàn $240$ giây.
  4. *Đóng gói payload & socket:* Payload gửi sang Remote Tectonic Docker API có `timeout_s = calc_timeout`, socket `urlopen` có `timeout = calc_timeout + 15`.
- **Kết quả kỳ vọng:** Hàm tính toán chính xác 100%, trả về giá trị nguyên nằm trong đoạn $[60, 240]$.
- **Tự động hóa Pytest:** Được kiểm thử tự động tại `tests/test_composer.py::test_composer_compute_compilation_timeout_adaptive_scaling` và `test_composer_compile_large_viet_duc_exam_pdf_success`.

#### TC-COMP-35: Trợ Lý AI Chẩn Đoán Lỗi Timeout & Đề Xuất Diff Tối Ưu Hóa TikZ (samples=100 -> samples=50)
- **Mô tả:** Kiểm tra chẩn đoán lỗi của `diagnose_compile_error`:
  1. Khi nhận chuỗi lỗi `compile_error` chứa `"Lỗi Tectonic API: Compilation timed out"` hoặc `"timed out"`.
  2. Mã nguồn hiện tại chứa các khối đồ thị TikZ với `samples=100`.
  3. AI Copilot phân tích rõ nguyên nhân do đề thi lớn có nhiều hình vẽ TikZ phức tạp, thông báo hệ thống đã tự động gia hạn thời gian biên dịch.
  4. Đồng thời sinh `DiffSuggestion` và `diffs` đề xuất chuyển đổi `samples=100` thành `samples=50` để tăng tốc độ biên dịch lên gấp đôi.
- **Kết quả kỳ vọng:** `diagnose_compile_error` trả về `ChatResponse` với `diff` hợp lệ thay thế `samples=100` thành `samples=50`, kèm danh sách `diffs` đầy đủ cho toàn bộ các đồ thị có mẫu dày.
- **Tự động hóa Pytest:** Được kiểm thử tự động tại `tests/test_composer.py::test_composer_diagnose_compile_error_timeout_and_samples_optimization`.

#### TC-COMP-34: Kiểm Thử Chống Nhân Đôi Ảnh Đính Kèm Khi Dán Clipboard (Ctrl+V Paste Event Isolation & Debounce)
- **Mô tả:** Kiểm tra hành vi dán ảnh clipboard (`Ctrl+V` / `Cmd+V`) vào ô chat `#composer-chat-input`:
  1. Kích hoạt sự kiện `paste` với một ảnh giả lập (Data URL) tại `#composer-chat-input`.
  2. Xác nhận `e.stopPropagation()` được gọi để chặn sự kiện nổi bọt lên container `#composer-chat-input-container`.
  3. Kiểm tra mảng `app.composer.attachedImages`: chỉ có **duy nhất 1 phần tử ảnh** được thêm vào.
  4. Kiểm tra DOM khay thumbnail `#composer-attached-images-container`: hiển thị đúng 1 chip thumbnail, không nhân đôi thành 2 ảnh.
  5. Thử nghiệm dán liên tiếp 2 lần cùng 1 ảnh trong < 500ms: Xác nhận cơ chế Debounce & Deduplication loại bỏ ảnh thứ hai, thông báo toast chỉ bắn duy nhất 1 lần.
- **Kết quả kỳ vọng:** 1 ảnh dán chỉ sinh ra duy nhất 1 ảnh đính kèm, triệt tiêu hoàn toàn lỗi nhân đôi.

#### TC-COMP-35: Kiểm Thử Chuẩn Hóa Cấu Trúc Khảo Thí Quốc Gia 2025: Reset Thứ Tự Câu Hỏi Về 1 (\setcounter{ex}{0}) & Loại Bỏ Thẻ \large Ở Tiêu Đề Phần
- **Mô tả:** Kiểm tra logic tiền xử lý và biên dịch đề thi có nhiều phần (PHẦN I, PHẦN II, PHẦN III):
  1. Gửi mã LaTeX đề thi 3 phần chuẩn Quốc gia tới `ensure_full_latex_document` và `sync_section_question_counts`:
     - Kiểm tra tại vị trí bắt đầu PHẦN II và PHẦN III, hệ thống tự động chèn lệnh `\setcounter{ex}{0}` nếu tài liệu chưa có.
     - Kiểm tra nếu tiêu đề có thẻ `\large` (ví dụ `\textbf{\large PHẦN I...}` hoặc `\large\textbf{PHẦN II...}`), hệ thống tự động bóc bỏ `\large`, đưa về chuẩn `\noindent\textbf{PHẦN ...}`.
  2. Kiểm tra biên dịch qua `compile_latex_source_to_html`:
     - Xác nhận số thứ tự câu hỏi ở PHẦN II được reset về Câu 1 (không phải Câu 13).
     - Xác nhận số thứ tự câu hỏi ở PHẦN III được reset về Câu 1 (không phải Câu 17).
  3. Kiểm tra các template trong `composer_service.py` (`TEMPLATES`) và `app.js` (`EX_TEST_TEMPLATES`): Xác nhận đã chứa sẵn `\setcounter{ex}{0}` ở PHẦN II, PHẦN III và không chứa thẻ `\large`.
- **Kết quả kỳ vọng:** Đề thi hiển thị đúng thứ tự câu hỏi bắt đầu từ Câu 1 ở mỗi phần và typography tiêu đề phần đồng nhất 12pt in đậm.

#### TC-COMP-36: Kiểm Thử Giải Pháp Biên Dịch Nhanh Đa Tầng (Focus Partial Compile, Instant Preview & Draft Mode)
- **Mô tả:** Kiểm tra các cơ chế tăng tốc biên dịch:
  1. *Focus Partial Compile:* Gửi yêu cầu biên dịch riêng 1 câu hỏi tại con trỏ tới `/api/v1/composer/compile-partial` (hoặc `/compile` với `focus_mode=True`), xác nhận tài liệu được bọc preamble tối giản, biên dịch thành công PDF trong < 2.0 giây.
  2. *Instant Live Preview (HTML):* Gọi `compile_latex_source_to_html`, xác nhận công thức toán và đồ thị TikZ được chuyển đổi mượt mà, tái sử dụng Disk Cache của các hình không đổi trong < 200ms.
  3. *Draft Mode Compile:* Gửi yêu cầu biên dịch toàn bộ tài liệu nặng kèm `draft_mode=True`, xác nhận backend tự động tối ưu `samples=35` cho các đường cong TikZ, hoàn thành biên dịch toàn bộ 22 câu trong < 20 giây.
- **Kết quả kỳ vọng:** Các chế độ biên dịch nhanh hoạt động ổn định, giảm đáng kể thời gian chờ đợi của giáo viên khi soạn thảo.
- **Mô tả:** Rà soát và xác thực hành vi của các agent và quy trình CI/CD:
  1. Chỉ thực hiện `git commit` và `git push` lên nhánh remote đang làm việc.
  2. Tuyệt đối không tự động kích hoạt `gh pr create` hoặc các API tương đương để tạo mới hay cập nhật Pull Request khi người dùng chưa ra lệnh trực tiếp bằng lời nói.
- **Kết quả kỳ vọng:** Tuân thủ 100% quy định quản trị phiên bản; ngăn ngừa tình trạng spam Pull Request không mong muốn.

#### TC-DEV-02: Cổng Kiểm Soát Pre-Commit CI Gate, Cô Lập CI Tuyệt Đối & Vòng Lặp Sửa Lỗi (CI Governance & Strict Isolation)
- **Mô tả:** Kiểm tra quy trình thực thi CI/CD và phân định vai trò giữa các Sub-Agents:
  1. *Cổng Pre-Commit CI Gate:* Bắt buộc chạy toàn bộ bài kiểm thử CI trên runner (`pytest`, syntax check) và đạt 100% test cases PASSED trước khi thực hiện `git commit`. Nghiêm cấm commit khi CI chưa pass.
  2. *Vòng lặp sửa lỗi CI (CI Loop):* Nếu CI test thất bại, kích hoạt vòng lặp: sửa code/test/CI -> chạy lại CI cho đến khi 100% test cases đạt mới cho phép commit.
  3. *Nguyên tắc Cô lập CI Tuyệt đối (Strict CI Isolation):* Sub-Agent phụ trách CI (Sub-Agent 3) độc quyền đọc, viết, chỉnh sửa cấu hình CI/CD (`.github/workflows/`); cấm mọi sub-agent khác (Sub-Agent 1, 2, 4...) truy cập và đọc CI; Sub-Agent CI tiếp nhận thông tin từ các sub-agents khác để cập nhật CI đồng bộ ngay khi code có thay đổi.
- **Kết quả kỳ vọng:** 100% cam kết chất lượng mã nguồn trước khi commit vào kho lưu trữ; ngăn chặn lỗi môi trường runner và rò rỉ phân quyền giữa các sub-agents.

---

### TEST SUITE 11: HỆ THỐNG XÁC THỰC NGƯỜI DÙNG AUTH, PBKDF2, JWT & PHÂN QUYỀN RBAC (AUTH-01)

#### TC-AUTH-01: Băm mật khẩu PBKDF2-HMAC-SHA256 & So khớp An toàn
- **Mô tả:** Kiểm tra hàm `hash_password` tạo chuỗi băm chuẩn `pbkdf2:sha256:600000$<salt_b64>$<hash_b64>` với salt ngẫu nhiên 32 bytes; kiểm tra `verify_password` kháng tấn công timing qua `hmac.compare_digest`.
- **Kết quả kỳ vọng:** 2 lần băm cùng mật khẩu cho ra 2 chuỗi khác nhau; xác thực mật khẩu đúng trả về True, sai/rỗng/hỏng trả về False.

#### TC-AUTH-02: Sinh và Giải mã JSON Web Token (JWT HS256)
- **Mô tả:** Kiểm tra `create_access_token` cấu trúc 3 phần `header.payload.signature` với thuật toán HMAC-SHA256; `decode_access_token` xác minh chữ ký và thời hạn hiệu lực (exp).
- **Kết quả kỳ vọng:** Token hợp lệ giải mã ra payload chính xác; token bị can thiệp chữ ký, token hết hạn hoặc format sai trả về `None`.

#### TC-AUTH-03: Đăng ký Tài khoản Mới (POST /api/v1/auth/register)
- **Mô tả:** Kiểm tra luồng đăng ký với email, mật khẩu >= 6 ký tự, họ tên, vai trò; kiểm tra bắt lỗi email trùng (400) và mật khẩu quá ngắn (422).
- **Kết quả kỳ vọng:** Đăng ký thành công trả về 201 Created + access_token + user profile; trùng email trả về 400 "Email already registered".

#### TC-AUTH-04: Đăng nhập Hệ thống (POST /api/v1/auth/login)
- **Mô tả:** Kiểm tra đăng nhập với email và mật khẩu; kiểm tra sai mật khẩu (401), email không tồn tại (401) và tài khoản bị vô hiệu hóa `is_active=False` (403).
- **Kết quả kỳ vọng:** Đăng nhập đúng trả về 200 OK + JWT access_token; sai mật khẩu/email trả về 401 "Invalid email or password"; tài khoản inactive trả về 403.

#### TC-AUTH-05: Lấy Thông tin Tài khoản (GET /api/v1/auth/me)
- **Mô tả:** Kiểm tra dependency `get_current_active_user` với Bearer token hợp lệ, token giả mạo và không đính kèm header.
- **Kết quả kỳ vọng:** Token hợp lệ trả về đúng user profile (200); token giả mạo hoặc thiếu Authorization header trả về 401 Unauthorized.

#### TC-AUTH-06: Đăng nhập OAuth Google & GitHub
- **Mô tả:** Kiểm tra callback OAuth tạo tài khoản mới nếu chưa tồn tại, cập nhật avatar_url và full_name nếu đã tồn tại, phát hành JWT token.
- **Kết quả kỳ vọng:** Trả về 200 OK kèm access_token và profile người dùng liên kết đúng nhà cung cấp (`google`, `github`).

#### TC-AUTH-07: Đăng xuất & Tài khoản Mặc định Seeded
- **Mô tả:** Kiểm tra endpoint POST `/api/v1/auth/logout`; kiểm tra đăng nhập thành công với 2 tài khoản seeded: `teacher@quesy.vn` / `quesy123456` (role TEACHER) và `admin@quesy.vn` / `admin123456` (role ADMIN).
- **Kết quả kỳ vọng:** Logout trả về 200 {"success": True}; cả 2 tài khoản mặc định đăng nhập thành công 100%.

#### TC-AUTH-08: Phân quyền Vai trò RBAC (require_role)
- **Mô tả:** Kiểm tra dependency phân quyền `require_role("ADMIN")` và `require_role("TEACHER")`.
- **Kết quả kỳ vọng:** Admin truy cập được mọi vai trò; user thường truy cập tài nguyên Admin bị từ chối 403 "Required role: ADMIN".

---

### TS-09: KIỂM THỬ RENDER KATEX TOÀN DIỆN & GIAO DIỆN APPLE SELECT (.apple-select)

#### TC-KATEX-01: Biên Dịch KaTeX Toàn Diện Trên Thẻ Câu Hỏi Ngân Hàng (Ảnh 1 Verification)
- **Mô tả:** Mở màn hình Ngân hàng câu hỏi (`/bank`), tải các câu hỏi Đúng/Sai (TRUE_FALSE_GROUP) và Trắc nghiệm đơn chứa công thức phức tạp (`$y = \dfrac{x_1 - 1}{x + 1}$`, `$D = \mathbb{R} \setminus \{-1\}$`, `$x = -1$`, `$y = 1$`, `$x \neq -1$`).
- **Thao tác:** Khởi tạo `renderItemBank()`, kiểm tra DOM các thẻ câu hỏi và các khẳng định con (a, b, c, d).
- **Kết quả kỳ vọng:** Các phần tử chứa lớp `.katex` hoặc `.katex-html` được render hoàn hảo, $0\%$ chuỗi thô `$ ... $` còn sót lại trên giao diện.

#### TC-KATEX-02: Biên Dịch KaTeX Trong Bảng Ma Trận Đề 2D (`renderMatrixGrid`)
- **Mô tả:** Mở màn hình Ma trận đề (`/matrix`), thêm hoặc tải dòng ma trận có Dạng bài chứa ký hiệu toán học (`row.archetypeName`: `$m$`, `$Oxyz$`, `$f(x)$`).
- **Thao tác:** Kiểm tra phần tử `#matrix-grid-tbody` sau khi chạy `renderMatrixGrid()`.
- **Kết quả kỳ vọng:** Hàm `renderKaTeX(tbody)` được thực thi tự động, các ký hiệu toán học hiển thị trực quan dưới dạng ký tự toán sắc nét, không hiển thị text thô.

#### TC-KATEX-03: Biên Dịch KaTeX Toàn Diện Trong Modal Xem Chi Tiết Câu Hỏi (`openQuestionDetailModal`)
- **Mô tả:** Click nút "Xem chi tiết" của một câu hỏi bất kỳ để mở `#question-detail-modal`.
- **Thao tác:** Kiểm tra `window.renderKaTeX` tồn tại (không `undefined`), và toàn bộ thân câu hỏi, phương án A-D, khẳng định con a-d, kết quả trả lời ngắn, và hướng dẫn giải được biên dịch KaTeX chuẩn xác.
- **Kết quả kỳ vọng:** Modal mở ra mượt mà, KaTeX render tức thì $\le 50$ms, không có lỗi console error.

#### TC-UI-SELECT-01: Kiểm Thử Giao Diện Dropdown Box Apple HIG Unified Select (.apple-select)
- **Mô tả:** Kiểm tra toàn bộ 19 thẻ `<select>` tĩnh trong `frontend/index.html` và dynamic select trong `frontend/static/app.js`.
- **Thao tác:** Thanh tra CSS Computed Styles trên DevTools cho thẻ `select.apple-select`.
- **Kết quả kỳ vọng:**
  * Mũi tên mặc định của hệ điều hành bị ẩn triệt để (`appearance: none`).
  * Có icon SVG chevron slate-500 `#64748b` căn lề phải.
  * Bo góc mềm mại đúng `12px` (`border-radius: 12px`).
  * Padding chuẩn `0.45rem 2.2rem 0.45rem 0.75rem`.
  * Khi focus hiển thị viền xanh Apple `#0071e3` kèm quầng sáng `box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15)`.

#### TC-UI-SELECT-02: Kiểm Thử Đồng Bộ Kích Thước Dropdown Thời Gian Làm Bài (`#matrix-param-time` - Ảnh 2)
- **Mô tả:** Kiểm tra ô chọn "Thời gian làm bài" (`#matrix-param-time`) trên thanh cấu hình Ma trận đề thi (`#tab-matrix`).
- **Thao tác:** So sánh chiều cao (`height` / `computed bounding rect`), góc bo, viền và padding của `#matrix-param-time` với ô input text bên cạnh (`#matrix-param-name`).
- **Kết quả kỳ vọng:** Kích thước chiều cao khớp 100%, bo góc 12px đồng nhất, không còn mũi tên xám thô mặc định của hệ điều hành.

#### TC-UI-SELECT-03: Triệt Tiêu Lỗi Font Monospace Trên Dropdown Bộ Lọc (`#bank-filter-yccd` - Ảnh 3)
- **Mô tả:** Kiểm tra ô chọn "6. Yêu cầu cần đạt" (`#bank-filter-yccd`) trong thanh bộ lọc Ngân hàng câu hỏi (`#tab-bank`).
- **Thao tác:** Đọc thuộc tính `className` và computed `font-family` của `#bank-filter-yccd`.
- **Kết quả kỳ vọng:** Hoàn toàn không còn class `font-mono`; font chữ hiển thị chuẩn sans-serif Apple HIG (`-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", system-ui, sans-serif`), đồng nhất 100% với 5 dropdown taxonomy còn lại.

---

## 4. TIÊU CHÍ ĐÓNG GIAI ĐOẠN KIỂM THỬ (TEST EXIT CRITERIA)

Dự án chỉ được nghiệm thu bàn giao khi:
1. **$100\%$** Test Cases thuộc mức độ ưu tiên **P0 (Must Have / Critical)** đạt trạng thái **PASS**.
2. **$\ge 95\%$** Test Cases thuộc mức độ ưu tiên **P1** đạt trạng thái **PASS**.
3. **Không còn bất kỳ Bug nào ở mức độ Blocker hoặc Critical** (đặc biệt là các lỗi về hoán vị mã đề, tính điểm Đúng/Sai lũy tiến, hoặc sai lệch công thức toán).
4. **Không còn lỗi Frontend & Giao diện:** Giao diện đồng nhất màu sắc chuẩn thương hiệu (nút BIÊN DỊCH `#0071e3`), textarea cuộn mượt mà không kẹt, bảo toàn nền tối `#141824` khi focus.
5. **Không còn lỗi Console & Mạng:** Bảng điều khiển DevTools `console.error` sạch sẽ, không có lỗi 404 tài nguyên mạng (font, ảnh, icon).
6. File Word `.docx` in thử thực tế trên máy in laser đạt độ rõ nét sư phạm.
