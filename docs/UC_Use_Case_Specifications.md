# TÀI LIỆU ĐẶC TẢ USE CASE (USE CASE SPECIFICATIONS - UC)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-UC-01  
- **Phiên bản:** 2.8 (Hoàn thiện Trợ lý Soạn thảo LaTeX: Tương phản Dark Mode WCAG 2.1 AA, Chuyển tiếp Log Lỗi XeTeX/Tectonic, Động cơ Fuzzy Diff & Inline Overlay trực tiếp trên Editor, Tối ưu Fast Prompt Dispatch)  
- **Mục tiêu tài liệu:** Đặc tả chi tiết các ca sử dụng (Use Cases) giải quyết bài toán số hóa đề thi, kiểm soát trùng lặp, dựng đồ thị vector SVG, trộn đề an toàn, xuất bản in ấn và trợ lý soạn đề AI Copilot trực tiếp.  
- **Ngày phát hành:** 2026-10-23
- **Tiêu chuẩn áp dụng:** RUP / Unified Modeling Language (UML)  

---

## 1. SƠ ĐỒ TỔNG THỂ USE CASE (SYSTEM USE CASE DIAGRAM)

```
                       ┌────────────────────────────────────────────────────────┐
                       │                     HỆ THỐNG QUESY                     │
                       └────────────────────────────────────────────────────────┘

     [Giáo viên] ──────────► (UC-01: Tải lên đề thi & AI Số hoá)
          │                                  ▲
          │                                  │ «include»
          │                                  │
          ├───────────────► (UC-02: Hậu kiểm câu hỏi & Gán mã YCCĐ) ◄─── [AI Worker]
          │                                  │
          │                                  │ «extend» (Nếu nghi ngờ trùng)
          │                                  ▼
          │                 (UC-03: So khớp & Cảnh báo Trùng lặp AI)
          │
          ├───────────────► (UC-05: Tìm kiếm theo YCCĐ & Dạng câu hỏi)
          │
          └───────────────► (UC-07: Sinh Đề thi từ Ma trận Ràng buộc YCCĐ)
                                             │
                                             │ «include»
                                             ▼
 [Tổ trưởng Chuyên môn] ──► (UC-06: Thiết lập Ma trận & Bản đặc tả YCCĐ)
          │                                  │
          ├───────────────► (UC-04: Quản trị Cây YCCĐ & Dạng Bài TT 32)
          │                                  │
          ├───────────────► (UC-08: Trộn Đề & Hoán vị An toàn)
          │                                  │
          │                                  ▼
          ├───────────────► (UC-09: Xuất bản Gói Đề thi Word 2 cột)
          │
          ├───────────────► (UC-10: Phân tích Khảo thí Hậu kiểm: p, D)
          │
          └───────────────► (UC-11: Soạn Đề Với Trợ Lý AI Copilot & Duyệt Diff Trực Tiếp)
```

---

## 2. DANH MỤC CÁC TÁC NHÂN (ACTORS CATALOG)

| Tác nhân (Actor) | Phân loại | Mô tả vai trò |
|:---|:---:|:---|
| **Giáo viên (Teacher)** | Con người | Tải đề gốc lên để AI bóc tách, chỉnh sửa nội dung trên Studio HITL, gán mã YCCĐ và dạng bài, biên tập câu hỏi, tạo đề kiểm tra cho lớp. |
| **Tổ trưởng Chuyên môn (Head of Dept)** | Con người | Thẩm định và duyệt câu hỏi vào ngân hàng chính thức, ban hành ma trận đề thi chung theo YCCĐ, giám sát xuất bản đề. |
| **Hệ thống AI Worker (AI Engine)** | Hệ thống | Tiến trình nền xử lý OCR, cắt ảnh đồ thị, gọi Vision LLM, parse công thức LaTeX, gợi ý auto-tagging mã YCCĐ và tính vector embedding. |
| **Quản trị viên (Super Admin)** | Con người | Quản trị người dùng, phân quyền, cấu hình hạ tầng và hạn mức tài nguyên AI. |

---

## 3. ĐẶC TẢ CHI TIẾT TỪNG USE CASE

---

### UC-01: TẢI LÊN ĐỀ THI & KÍCH HOẠT AI SỐ HOÁ
- **Mã Use Case:** `UC-01`
- **Tên Use Case:** Tải lên đề thi và kích hoạt AI bóc tách
- **Tác nhân chính:** Giáo viên, Tổ trưởng chuyên môn
- **Tác nhân hỗ trợ:** AI Worker Service
- **Điều kiện tiên quyết:** Người dùng đã đăng nhập hệ thống thành công.

#### Luồng sự kiện chính (Main Success Scenario):
1. Người dùng chọn file đề thi từ máy tính (`.docx`, `.doc`, `.pdf` hoặc ảnh).
2. Người dùng chọn thông tin cơ bản: Môn học, Khối lớp (**không chọn bộ sách**).
3. Hệ thống kiểm tra dung lượng file ($\le 50$MB) và định dạng hợp lệ.
4. Hệ thống tải file lên S3 Storage và tạo bản ghi tiến trình (`job_id`).
5. Hệ thống gửi thông điệp vào Redis Queue và trả về màn hình chờ với thanh tiến trình.
6. AI Worker tiếp nhận job, thực hiện:
   - Trích xuất text và giải mã binary MathType MTEF sang chuỗi LaTeX chuẩn (với file Word).
   - Chuyển PDF/Ảnh sang 300 DPI, áp dụng OpenCV Deskew và Binarization.
   - Gọi Vision LLM nhận diện cấu trúc các phần (Phần I, II, III), câu hỏi, phương án, đáp án và lời giải.
   - Tự động cắt (Auto-crop) hình học không gian, đồ thị hàm số lưu vào S3.
   - **Gợi ý Auto-tagging:** Đề xuất Mạch nội dung, Chủ đề, Dạng câu hỏi, Mức độ tư duy và mã **Yêu cầu cần đạt (YCCĐ)** tương ứng theo Thông tư 32.
7. AI Worker cập nhật trạng thái `COMPLETED` và gửi thông báo qua WebSocket.
8. Giao diện tự động chuyển hướng người dùng sang màn hình Studio Hậu kiểm (UC-02).

---

### UC-02: HẬU KIỂM & GÁN MÃ YCCĐ TRÊN STUDIO HITL
- **Mã Use Case:** `UC-02`
- **Tên Use Case:** Hậu kiểm câu hỏi và gán mã YCCĐ trên Studio Human-in-the-Loop
- **Tác nhân chính:** Giáo viên
- **Điều kiện tiên quyết:** Job bóc tách AI đã hoàn tất (`COMPLETED`).

#### Luồng sự kiện chính:
1. Hệ thống hiển thị giao diện 2 cột:
   - Cột trái: Văn bản file gốc (PDF Viewer).
   - Cột phải: Danh sách câu hỏi bóc tách kèm nhãn độ tin cậy (Xanh / Vàng / Đỏ).
2. Người dùng duyệt từng câu hỏi:
   - Khi nhấp vào Câu 3 ở cột phải, cột trái tự động cuộn đến vị trí Câu 3 trên file gốc (**Synchronized Scrolling**).
   - Công thức Toán/Khoa học được render trực quan bằng KaTeX.
3. Người dùng kiểm tra và chỉnh sửa nhanh:
   - Nhấp vào [A], [B], [C], [D] để điều chỉnh đáp án đúng.
   - Nhấp đúp vào công thức để sửa mã LaTeX nếu cần.
4. Người dùng rà soát gợi ý AI Auto-tagging và chuẩn hóa phân loại:
   - Chọn: Mạch nội dung $\rightarrow$ Chủ đề $\rightarrow$ Bài học $\rightarrow$ **Yêu cầu cần đạt (YCCĐ - TT 32)** $\rightarrow$ **Dạng câu hỏi** $\rightarrow$ Mức độ nhận thức (Biết, Hiểu, Vận dụng).
5. Người dùng nhấn nút "Lưu toàn bộ vào Ngân hàng".
6. Hệ thống tạo các câu hỏi trong ngân hàng với trạng thái `DRAFT` và thông báo thành công.

---

### UC-03: PHÁT HIỆN & CẢNH BÁO TRÙNG LẶP CÂU HỎI BẰNG AI VECTOR
- **Mã Use Case:** `UC-03`
- **Tên Use Case:** So khớp và cảnh báo trùng lặp câu hỏi bằng AI Vector
- **Tác nhân:** Hệ thống (tự động)

#### Luồng sự kiện chính:
1. Hệ thống tính toán vector embedding cho nội dung thân câu hỏi.
2. Hệ thống truy vấn các câu hỏi trong cùng Môn học và Khối lớp có Cosine Similarity lớn nhất qua `pgvector`.
3. Nếu độ tương đồng $< 0.80$: Lưu bình thường.
4. Nếu độ tương đồng $\ge 0.90$:
   - Hệ thống bật Modal cảnh báo màu đỏ: *"Cảnh báo: Câu hỏi này trùng lặp 92% với câu hỏi [TOAN12-0452] đã có trong ngân hàng"*.
   - Hiển thị bảng so sánh đối đầu (Side-by-side) giữa câu hỏi mới và câu hỏi cũ trong kho.
5. Người dùng có 2 lựa chọn: "Hủy bỏ lưu" hoặc "Vẫn lưu (Câu hỏi biến thể)".

---

### UC-04: QUẢN TRỊ CÂY YCCĐ & DẠNG BÀI THEO THÔNG TƯ 32
- **Mã Use Case:** `UC-04`
- **Tên Use Case:** Quản lý Cây Yêu cầu cần đạt và Danh mục Dạng câu hỏi
- **Tác nhân chính:** Tổ trưởng Chuyên môn, Admin
- **Mô tả:** Thiết lập cấu trúc phân cấp kiến thức chuẩn hóa theo Thông tư 32/2018/TT-BGDĐT, **không phân chia theo bộ sách**.

#### Luồng sự kiện chính:
1. Người dùng chọn Môn học và Khối lớp cần quản lý.
2. Người dùng xem cây cấu trúc 6 tầng:
   $$\text{Môn/Lớp} \longrightarrow \text{Mạch nội dung} \longrightarrow \text{Chủ đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{Yêu\ cầu\ cần\ đạt\ (YCCĐ)} \longrightarrow \mathbf{Dạng\ câu\ hỏi}$$
3. Người dùng có thể:
   - Thêm / Sửa / Xóa một Mạch nội dung theo CT GDPT 2018.
   - Thêm / Sửa / Xóa danh mục Yêu cầu cần đạt (YCCĐ) kèm mã chuẩn (VD: `TOAN12.GT.01`).
   - Thêm / Sửa / Xóa các **Dạng câu hỏi chi tiết** thuộc từng YCCĐ (VD: *Dạng 1: Đọc đồ thị tìm cực trị*, *Dạng 2: Cực trị chứa tham số m*).
4. Hệ thống kiểm tra ràng buộc toàn vẹn: Không cho phép xóa một YCCĐ hoặc Dạng bài nếu đang có câu hỏi liên kết trong ngân hàng.
5. Hệ thống lưu cấu trúc và đồng bộ lên toàn bộ bộ lọc trong hệ thống.

---

### UC-06: THIẾT LẬP MA TRẬN & BẢN ĐẶC TẢ ĐỀ THI THEO YCCĐ
- **Mã Use Case:** `UC-06`
- **Tên Use Case:** Thiết lập Ma trận Đề thi & Bản đặc tả theo YCCĐ
- **Tác nhân chính:** Tổ trưởng Chuyên môn, Giáo viên
- **Căn cứ:** Thông tư 22/2021/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT

#### Luồng sự kiện chính:
1. Người dùng nhập thông số chung: Tên kỳ thi, Môn học, Khối lớp, Thời gian làm bài (VD: 90 phút), Thang điểm tổng (10.0).
2. Hệ thống tải cây kiến thức và dựng lưới ma trận 2 chiều:
   - Trục dòng: Danh sách Mạch nội dung $\rightarrow$ Yêu cầu cần đạt (YCCĐ) $\rightarrow$ Dạng câu hỏi.
   - Trục ngang: 3 Cấp độ nhận thức (Biết, Hiểu, Vận dụng) $\times$ Thể thức câu hỏi (Trắc nghiệm đơn, Đúng/Sai 4 ý, Trả lời ngắn, Tự luận).
3. Người dùng nhập số lượng câu cần lấy vào từng ô ma trận.
4. Hệ thống tự động tính toán tổng số câu, tỷ lệ % điểm theo mức độ tư duy ($40\%$ Biết - $30\%$ Hiểu - $30\%$ Vận dụng), và hiển thị chỉ báo "Số dư khả dụng trong Bank".
5. Người dùng nhấn "Lưu và Ban hành Ma trận".

---

### UC-07: SINH ĐỀ THI TỰ ĐỘNG TỪ MA TRẬN RÀNG BUỘC YCCĐ
- **Mã Use Case:** `UC-07`
- **Tên Use Case:** Sinh Đề thi từ Ma trận Ràng buộc YCCĐ
- **Tác nhân chính:** Giáo viên, Tổ trưởng Chuyên môn

#### Luồng sự kiện chính:
1. Người dùng chọn Ma trận đề thi cần sử dụng.
2. Người dùng thiết lập ràng buộc loại trừ: Loại trừ các câu hỏi đã xuất hiện trong bài thi gần nhất của khối/lớp trong vòng 30 ngày qua.
3. Người dùng nhấn nút "Khởi tạo Đề thi Gốc".
4. Hệ thống kích hoạt thuật toán Constraint Satisfaction Solver:
   - Quét ngân hàng, lọc các câu hỏi đạt `status = 'APPROVED'` khớp đúng mã YCCĐ, Dạng câu hỏi và Mức độ nhận thức.
   - Kiểm tra toàn vẹn câu hỏi chùm (Passage-based): Giữ nguyên bài đọc chung và toàn bộ câu con đi kèm.
5. Hệ thống hiển thị Đề thi Gốc (Master Exam) vừa sinh ra để người dùng rà soát nội dung.
6. Cho phép bấm "Đổi câu khác" (hệ thống tự động bốc câu hỏi khác cùng mã YCCĐ, cùng dạng bài, cùng mức độ Bloom để thay thế).
7. Người dùng nhấn "Xác nhận Đề thi Gốc".

---

### UC-08: TRỘN ĐỀ & HOÁN VỊ MÃ ĐỀ AN TOÀN
- **Mã Use Case:** `UC-08`
- **Tên Use Case:** Trộn đề và hoán vị mã đề an toàn
- **Tác nhân chính:** Giáo viên, Tổ trưởng chuyên môn

#### Luồng sự kiện chính:
1. Người dùng chọn số lượng mã đề hoán vị cần tạo (VD: 4 mã đề: 101, 102, 103, 104).
2. Người dùng nhấn nút "Bắt đầu Trộn đề".
3. Động cơ Shuffling Engine thực thi 4 quy tắc an toàn:
   - **Quy tắc phân vùng:** Chỉ đảo thứ tự câu trong từng Phần riêng biệt.
   - **Quy tắc câu chùm:** Neo bài đọc chung và các câu con liên quan liền kề nhau.
   - **Quy tắc neo phương án (Option Anchor):** Khóa cố định các phương án chứa "Cả A và B", "Tất cả các ý trên" ở vị trí cuối cùng (D).
   - Hoán vị ngẫu nhiên các phương án còn lại.
4. Hệ thống tạo ra 4 bản ghi mã đề thi độc lập kèm theo **Ma trận Ánh xạ Đáp án** (Answer Key Matrix).
5. Hệ thống chuyển sang màn hình xuất bản tài liệu (UC-09).

---

### UC-09: XUẤT BẢN GÓI ĐỀ THI WORD (.DOCX) MATHTYPE OLE / OMML & BAREM
- **Mã Use Case:** `UC-09`
- **Tên Use Case:** Xuất bản Gói Đề thi Word chuẩn mẫu in (MathType OLE Vector WMF / OMML) và Barem
- **Tác nhân chính:** Giáo viên, Cán bộ in sao đề

#### Luồng sự kiện chính:
1. Người dùng chọn mẫu template Word và định dạng công thức (`mathtype`, `omml`, hoặc `latex`).
2. Người dùng nhấn "Xuất gói In ấn (.ZIP)".
3. Hệ thống tạo các file:
   - $N$ file đề thi Word (`.docx`) khổ A4 Portrait, công thức toán dạng **MathType 7.0 OLE Vector WMF** (100% vector thuần nét căng, stream DSMT7 TeX Input Language, click đúp mở MathType 7 để chỉnh sửa 2 chiều mượt mà không lỗi) hoặc **OMML native**, tự động chuyển đổi bảng thống kê `\begin{array}` thành bảng Word native `<w:tbl>`.
   - File Bảng ma trận đáp án tổng hợp các mã đề (Excel/CSV UTF-8 BOM + PDF).
   - File Hướng dẫn giải chi tiết từng mã đề.
   - File Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR.
4. Hệ thống đóng gói thành 1 file ZIP và bắt đầu tải xuống máy người dùng.

---

### UC-10: PHÂN TÍCH KHẢO THÍ HẬU KIỂM (p, D)
- **Mã Use Case:** `UC-10`
- **Tên Use Case:** Phân tích Chỉ số Chất lượng Câu hỏi Hậu kiểm
- **Tác nhân chính:** Tổ trưởng Chuyên môn, Phòng Khảo thí

#### Luồng sự kiện chính:
1. Sau kỳ thi, người dùng tải lên file Excel kết quả làm bài của học sinh (gồm mã học sinh, mã đề, đáp án chọn cho từng câu).
2. Hệ thống chấm điểm tự động và tính toán:
   - Độ khó thực nghiệm $p$ của từng câu hỏi.
   - Độ phân biệt $D$ giữa nhóm điểm cao và nhóm điểm thấp.
   - Thống kê tỷ lệ chọn các phương án nhiễu A, B, C, D.
3. Hệ thống cập nhật các chỉ số này vào bảng `question_metrics` trong ngân hàng câu hỏi.
4. Hệ thống gắn cờ cảnh báo đối với các câu hỏi có $D < 0.2$ để Hội đồng bộ môn đánh giá và loại bỏ khỏi ngân hàng.

---

### UC-11: SOẠN ĐỀ VỚI TRỢ LÝ AI COPILOT & DUYỆT DIFF TRỰC TIẾP
- **Mã Use Case:** `UC-11`
- **Tên Use Case:** Soạn thảo đề thi với Trợ lý AI Copilot, Thanh Compact Prompt Bar và Duyệt Diff trực tiếp trên Editor
- **Tác nhân chính:** Giáo viên Bộ môn
- **Tác nhân hỗ trợ:** AI Copilot Service (`/api/v1/composer/chat`), Tectonic Compiler Engine
- **Điều kiện tiên quyết:** Người dùng truy cập phân hệ Soạn đề (`/composer`).

#### Luồng sự kiện chính (Main Success Scenario):
1. Người dùng soạn thảo mã LaTeX trên trình soạn thảo Dark mode (`#141824`).
2. Khi cần hỗ trợ chỉnh sửa (đổi font 11pt sang 12pt, sửa đáp án, vẽ bảng biến thiên, kiểm tra và sửa lỗi biên dịch):
   - Người dùng nhấp chuột vào Thanh Nhập Prompt AI thu gọn ở chân editor (`#composer-compact-bar`).
   - Ô nhập nhận focus bình thường (`cursor-text`), chữ hiển thị màu trắng sáng `#f8fafc` và con trỏ `#38bdf8` rõ nét trên nền tối Dark mode, **tuyệt đối không tự động mở full popup**, cho phép người dùng gõ hoặc dán nội dung yêu cầu mà không bị che khuất màn hình.
3. Người dùng nhấn phím **`Enter`** (hoặc nhấp chuột vào **Nút Gửi Mũi Tên Tròn**):
   - Giao diện phản hồi tức thì (Optimistic Fast Dispatch $\le 16$ms): mở bung full Popup Trợ lý Soạn thảo (`#composer-ai-popup`), ẩn thanh compact bar, đưa tin nhắn vào lịch sử và cuộn mượt đến đáy.
   - Nếu lần biên dịch trước đó gặp lỗi từ XeTeX/Tectonic, hệ thống tự động đính kèm `compile_error_log` vào payload gửi đến `POST /api/v1/composer/chat`.
4. Phía máy chủ AI Copilot phân tích yêu cầu cùng tài liệu hiện tại và log lỗi biên dịch (nếu có), chẩn đoán nguyên nhân và bóc tách đề xuất sửa đổi thành cấu trúc `DiffSuggestion(action, old_text, new_text, description)`.
5. Phía trình duyệt tiếp nhận phản hồi:
   - Thuật toán định vị tìm chính xác dòng mã nguồn của đoạn `old_text` trong editor, tự động cuộn khung nhìn textarea đến đúng dòng đó và bôi đen vùng chọn.
   - Đồng thời hiển thị 2 tầng giao diện trực quan:
     + Banner Gợi ý Sửa đổi (Inline Diff Banner) trên đỉnh editor: huy hiệu số dòng `GỢI Ý TẠI DÒNG [lineNo]`.
     + Giao diện Diff Nội Dòng (Inline Editor Diff Overlay / Widget) ngay tại đúng vị trí dòng mã nguồn trên textarea: khối dòng đỏ xóa `- old_text` và khối dòng xanh thêm `+ new_text` kèm hai nút điều khiển trực tiếp `[Keep / Đồng ý]` và `[Undo / Từ chối]`.
6. Người dùng xem xét đề xuất sửa đổi và có 2 lựa chọn thao tác trực tiếp:
   - **Kịch bản 6a - Người dùng nhấn [Keep / Đồng ý]:**
     1. Hệ thống kích hoạt Động cơ Thay thế Dòng mờ Đa tầng (5-Tier Fuzzy Line Replacement Engine): so khớp chuỗi chuẩn hóa, bỏ qua thụt lề, quét cửa sổ trượt hoặc thay thế theo phạm vi dòng đã ghim `pinnedRange`.
     2. Đảm bảo thay thế thành công 100%, triệt tiêu hoàn toàn lỗi toast "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại".
     3. Hệ thống tự động kích hoạt biên dịch tức thì `compile(true)` để làm mới tệp PDF Live Preview ở cột đối diện.
     4. Ẩn diff overlay & banner diff, hiển thị thông báo toast thành công: *"Đã áp dụng thay đổi vào mã nguồn!"*.
   - **Kịch bản 6b - Người dùng nhấn [Undo / Từ chối]:**
     1. Hệ thống ẩn diff overlay và banner diff, hủy bỏ vùng bôi đen, đưa con trỏ về trạng thái bình thường.
     2. Toàn bộ mã nguồn tài liệu được giữ nguyên vẹn 100% không bị thay đổi.
7. Người dùng có thể tiếp tục trò chuyện hoặc tái áp dụng đề xuất từ thẻ Diff Card lưu trong lịch sử chat bất kỳ lúc nào.
