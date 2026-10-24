# TÀI LIỆU ĐẶC TẢ USE CASE (USE CASE SPECIFICATIONS - UC)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-UC-01  
- **Phiên bản:** 3.0 (Động cơ Thay thế Câu hỏi Thông minh Question Replacement Engine, Đồng bộ Chat-Editor An toàn & Quy tắc Git Workflow Tuyệt đối Không Tự Động Tạo PR)  
- **Mục tiêu tài liệu:** Đặc tả chi tiết các ca sử dụng (Use Cases) giải quyết bài toán số hóa đề thi, kiểm soát trùng lặp, dựng đồ thị vector SVG, trộn đề an toàn, xuất bản in ấn, trợ lý soạn đề AI Copilot trực tiếp, và quy chuẩn quản trị phát triển Git.  
- **Ngày phát hành:** 2026-10-24  
- **Tiêu chuẩn áp dụng:** RUP / Unified Modeling Language (UML)

---

## 1. SƠ ĐỒ TỔNG THỂ USE CASE (SYSTEM USE CASE DIAGRAM)

### 1.1. Quy tắc Quản trị Git Workflow & Không Tự Động Tạo Pull Request (Mandatory Git Rule)
- **Bắt buộc:** Mọi tác vụ phát triển, sửa lỗi và nâng cấp tính năng chỉ thực hiện `git commit` và `git push` lên nhánh remote repository.
- **TUYỆT ĐỐI KHÔNG TỰ ĐỘNG TẠO PULL REQUEST (`gh pr create`, API PR...)** hoặc tự động cập nhật vào Pull Request trừ khi Người dùng (User) có yêu cầu rõ ràng bằng lời nói (explicit user prompt). Mọi hành vi tự động tạo PR khi chưa có lệnh trực tiếp đều vi phạm quy chuẩn quản trị dự án.

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

### UC-11: SOẠN ĐỀ VỚI TRỢ LÝ AI COPILOT, KÉO THẢ RESIZE ĐA CHIỀU & DUYỆT DIFF TRÊN EDITOR
- **Mã Use Case:** `UC-11`
- **Tên Use Case:** Soạn thảo đề thi với Trợ lý AI Copilot, Kéo thả Resize Đa chiều, Quản lý Phiên sạch sẽ và Duyệt Diff độc quyền trên Editor
- **Tác nhân chính:** Giáo viên Bộ môn
- **Tác nhân hỗ trợ:** AI Copilot Service (`/api/v1/composer/chat`), Tectonic Compiler Engine
- **Điều kiện tiên quyết:** Người dùng truy cập phân hệ Soạn đề (`/composer`).

#### Luồng sự kiện chính (Main Success Scenario):
1. Người dùng soạn thảo mã LaTeX trên trình soạn thảo Dark mode (`#141824`). Mỗi phiên mới bắt đầu với màn hình chat sạch sẽ và lời chào mặc định từ Quesy Copilot.
2. Khi cần hỗ trợ chỉnh sửa (đổi font 11pt sang 12pt, sửa đáp án, vẽ bảng biến thiên, kiểm tra và sửa lỗi biên dịch):
   - Người dùng nhấp chuột vào Thanh Nhập Prompt AI thu gọn ở chân editor (`#composer-compact-bar`).
   - Ô nhập nhận focus bình thường (`cursor-text`), chữ hiển thị màu trắng sáng `#f8fafc` và con trỏ `#38bdf8` rõ nét trên nền tối Dark mode, **tuyệt đối không tự động mở full popup**, cho phép người dùng gõ hoặc dán nội dung yêu cầu mà không bị che khuất màn hình.
3. Người dùng nhấn phím **`Enter`** (hoặc nhấp chuột vào **Nút Gửi Mũi Tên Tròn**):
   - **Cơ chế Xóa Sạch Lạc Quan (Optimistic Input Reset $\le 0\text{ms}$):** Hệ thống lập tức xóa trắng cả 2 ô nhập (`compactInput.value = ''` và `chatInput.value = ''`), loại bỏ hoàn toàn hiện tượng text chat cũ còn kẹt trong ô nhập (Ảnh 1).
   - Giao diện phản hồi tức thì (Optimistic Fast Dispatch $\le 16$ms): mở bung full Popup Trợ lý Soạn thảo (`#composer-ai-popup`), ẩn thanh compact bar, đưa tin nhắn vào lịch sử phiên hiện tại và cuộn mượt đến đáy.
   - Nếu lần biên dịch trước đó gặp lỗi từ XeTeX/Tectonic, hệ thống tự động đính kèm `compile_error_log` vào payload gửi đến `POST /api/v1/composer/chat`.
4. Phía máy chủ AI Copilot phân tích yêu cầu cùng tài liệu hiện tại và log lỗi biên dịch (nếu có), chẩn đoán nguyên nhân và bóc tách toàn bộ đề xuất sửa đổi thành cấu trúc đa diff `ChatResponse(reply, diff, diffs)`:
   - Trường `diffs`: Danh sách toàn bộ các khối `DiffSuggestion(action, old_text, new_text, description)` trích xuất được (Ảnh 3).
   - Trường `diff`: Khối diff đầu tiên phục vụ tương thích ngược.
5. Phía trình duyệt tiếp nhận phản hồi:
   - Trong bubble chat của Trợ lý: Chỉ hiển thị lời văn giải thích ngắn gọn, phân tích nguyên nhân lỗi cú pháp hoặc hướng dẫn sư phạm dưới dạng markdown thuần túy. **Quy tắc bắt buộc:** Tuyệt đối KHÔNG hiển thị widget diff hay nút duyệt diff lặp lại bên trong bubble chat.
   - Trên vùng Code Editor: Khởi tạo cỗ máy trạng thái `pendingDiffs = diffs` và trỏ con trỏ `currentDiffIndex = 0`. Thuật toán định vị tìm chính xác dòng mã nguồn của đoạn `old_text` của diff hiện tại, tự động cuộn khung nhìn textarea đến đúng dòng đó và bôi đen vùng chọn. Đồng thời kích hoạt hiển thị khối so sánh diff song hành trên cả Top Banner và Inline Overlay:
     + Huy hiệu định vị động: Hiển thị viên thuốc `${currentDiffIndex + 1}/${pendingDiffs.length}` (thay thế số `1/1` tĩnh).
     + Bộ điều hướng tuần tự: Nút **`[< Trước]`** và nút **`[Sau >]`** cho phép lật qua lại giữa các đề xuất sửa đổi nếu có nhiều hơn 1 khối diff.
     + Hai nút thao tác đơn lẻ `[Keep / Đồng ý]` và `[Undo / Từ chối]` cho diff hiện hành.
     + Nút **`[Áp dụng tất cả] (Apply All)`**: Hiển thị nổi bật với nền xanh Apple khi `pendingDiffs.length > 1`.
6. Người dùng xem xét đề xuất sửa đổi và thực hiện thao tác trực tiếp trên Editor:
   - **Kịch bản 6a - Người dùng nhấn [Keep / Đồng ý] trên diff hiện tại:**
     1. Hệ thống kích hoạt Động cơ Thay thế Dòng mờ Đa tầng (6-Tier Fuzzy Line Replacement Engine): áp dụng đoạn mã mới của diff hiện tại.
     2. Loại bỏ diff này khỏi danh sách (`pendingDiffs.splice(currentDiffIndex, 1)`).
     3. Nếu hết diff (`pendingDiffs.length === 0`): Tự động đóng banner & overlay, tự động recompile `compile(true)` và hiển thị thông báo toast: *"Đã áp dụng thay đổi vào mã nguồn!"*.
     4. Nếu vẫn còn diff: Giữ nguyên giao diện, tự động chuyển trọng tâm hiển thị sang diff kế tiếp (`renderCurrentDiff()`), cuộn màn hình và bôi đen vị trí dòng tương ứng.
   - **Kịch bản 6b - Người dùng nhấn [Undo / Từ chối] trên diff hiện tại:**
     1. Hệ thống bỏ qua không áp dụng diff hiện tại, loại bỏ khỏi `pendingDiffs`.
     2. Nếu hết diff: Ẩn diff overlay và banner diff, hủy bỏ vùng bôi đen, đưa con trỏ về trạng thái bình thường.
     3. Nếu còn diff: Chuyển sang hiển thị diff kế tiếp.
   - **Kịch bản 6c - Người dùng nhấn [Áp dụng tất cả] (Apply All - Ảnh 3):**
     1. Hệ thống tự động duyệt qua toàn bộ $N$ khối diff trong `pendingDiffs` theo thứ tự từ trên xuống dưới.
     2. Áp dụng tuần tự toàn bộ các đoạn mã thay thế `(old_text, new_text)` vào buffer mã nguồn.
     3. Cập nhật mã nguồn mới vào editor một lần duy nhất, kích hoạt `compile(true)` để làm mới PDF ở cột Live Preview.
     4. Đóng toàn bộ banner & overlay diff (`dismissPendingDiffs()`).
     5. Hiển thị thông báo Toast thành công: *"Đã áp dụng toàn bộ N sửa đổi vào mã nguồn!"*.

#### Các luồng phụ (Alternate Flows):
- **Luồng 6d - Kéo thả thanh Splitter ngang điều chỉnh tỷ lệ 2 cột chuẩn Apple HIG (#composer-split-resizer - Ảnh 2):**
  1. Người dùng di chuột vào thanh phân cách `#composer-split-resizer` giữa cột Editor và Live Preview (con trỏ đổi thành `cursor-col-resize`). Thanh nằm trong rãnh đệm thông thoáng `w-3.5` / `w-4` với lề `mx-1` / `mx-1.5`, trục viên thuốc cách đều viền 2 card từ 6px đến 8px, không chạm đè lên viền của box soạn thảo.
  2. Vạch viên thuốc `w-1 h-9 rounded-full bg-slate-300 dark:bg-[#34415e]` chuyển màu xanh Apple System Blue `#0071e3`, quầng sáng vi mô tỏa nhẹ và vạch giãn nhẹ `scale-y-110`.
  3. Người dùng nhấn giữ và kéo chuột sang trái hoặc sang phải. Hệ thống kích hoạt phản hồi xúc giác `scale-95`, bật tấm chắn bảo vệ `pointer-events: none` trên khung PDF Preview, tính toán tỷ lệ bề rộng phần trăm cột trái theo thời gian thực (60 FPS) trong dải an toàn $25\% - 75\%$.
  4. Khi thả chuột, hệ thống cập nhật layout, kích hoạt `syncEditorScroll()`, tự động tính toán lại `fitToWidth(true)` và lưu tỷ lệ mới vào `localStorage` (`quesy_composer_split_ratio`).
  5. Nếu người dùng nháy đúp (`dblclick`) vào thanh splitter: Tỷ lệ 2 cột lập tức quay về tỷ lệ vàng mặc định 60% Left : 40% Right.
- **Luồng 6e - Kéo thả điều chỉnh độ cao Box Trợ lý Soạn thảo (Vertical Drag Resize & Single Pill Handle):**
  1. Người dùng di chuột vào thanh ngang viên thuốc duy nhất (`#composer-ai-resize-handle`) ở trung tâm header của popup trợ lý (hoặc viền trên).
  2. Người dùng nhấn giữ và kéo chuột/ngón tay lên trên (tăng chiều cao) hoặc xuống dưới (giảm chiều cao).
  3. Hệ thống tạm thời ngắt CSS transition, cập nhật độ cao liên tục trong phạm vi $180\text{px}$ (hoặc $20\%$) đến $92\%$ chiều cao khung editor.
  4. Khi thả chuột, hệ thống lưu độ cao tùy chỉnh vào `localStorage` (`quesy_composer_ai_height`). Nếu người dùng chỉ click nhanh hoặc nhấp đúp vào pill handle mà không kéo, hệ thống toggle nhanh giữa 56% và 78%.
- **Luồng 6f - Quản lý Phiên mới & Tra cứu Lịch sử Phiên cũ:**
  1. Khi người dùng muốn bắt đầu phiên thảo luận mới, nhấp vào nút `newChat` (icon reset xoay vòng): Phiên hiện tại (nếu có tin nhắn người dùng) được đóng gói và lưu trữ vào kho phiên cũ `quesy_composer_chat_sessions`. Khung chat active lập tức được dọn dẹp sạch sẽ và hiển thị lời chào ban đầu.
  2. Khi người dùng muốn xem lại các câu lệnh trước đó, nhấp vào nút **`[Lịch sử]`** (`#composer-ai-history-btn`): Khung chat tạm ẩn, mở ra panel danh sách lịch sử với đầy đủ các phiên cũ. Người dùng có thể nhấp vào một câu lệnh cũ để nạp lại vào ô nhập hoặc tải lại phiên cũ, sau đó bấm "✕ Đóng" để tiếp tục làm việc.
- **Luồng 6g - Tự động Co giãn Chiều rộng PDF & Cuộn Ngang An Toàn (Auto Fit-to-Width & Horizontal Scroll):**
  1. Khi người dùng kéo thanh splitter `#composer-split-resizer` làm thay đổi bề rộng Cột Xem Trước (Live Preview) hoặc đổi cỡ cửa sổ:
  2. Nếu hệ thống đang ở chế độ xem mặc định (`isAutoFit === true`), tỷ lệ `fitZoom` được tự động tính toán lại theo chiều rộng khả dụng (`clientWidth - 48px`), co giãn trực tiếp thẻ trang PDF và canvas theo thời gian thực (60 FPS trong lúc kéo), sau đó vẽ lại vector sắc nét (debounced 100ms).
  3. Khung cuộn `#composer-pdf-scroll-container` kích hoạt thuộc tính `overflow-x-auto`, khi kích thước trang vượt quá bề rộng khung nhìn, thanh cuộn ngang hiển thị trơn tru, cho phép giáo viên cuộn xem trọn vẹn lề phải tài liệu mà không bao giờ bị cắt xén.
- **Luồng 6h - Phóng to / Thu nhỏ Thông Minh theo Điểm Neo Chuột & Trọng Tâm Viewport (Smart Zoom-to-Point):**
  1. *Trường hợp A (Con trỏ nằm trên PDF):* Người dùng giữ `Ctrl` và lăn chuột (`wheel`): Hệ thống lấy chính xác tọa độ con trỏ chuột $(x_v, y_v)$ làm điểm neo, phóng to / thu nhỏ mà điểm nội dung ngay dưới con trỏ chuột được ghim bất biến, không bị trôi lệch.
  2. *Trường hợp B (Con trỏ nằm ngoài PDF hoặc bấm nút thanh công cụ):* Người dùng nhấp vào nút `+` hoặc `-` trên floating toolbar: Hệ thống lấy tâm điểm màn hình làm điểm neo, tài liệu phóng to / thu nhỏ đồng tâm từ chính giữa khung nhìn của giáo viên.
  3. Triệt tiêu hoàn toàn hiện tượng giật cục hoặc bị nhảy về góc trên cùng bên trái $(0, 0)$. Khôi phục ổn định tọa độ cuộn khi vẽ lại canvas ở độ phân giải thực.
- **Luồng 6i - Thay thế Câu hỏi Chuyên sâu qua Ngôn ngữ Tự nhiên & Bảo toàn Khối mã Chat Bubble (Question Replacement & Safe Sync):**
  1. Người dùng nhập câu lệnh yêu cầu thay thế câu hỏi cụ thể trong đề thi (ví dụ: *"Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"* hoặc *"Thay câu 2 bằng câu khác"*).
  2. Phía backend tiếp nhận yêu cầu, hàm `find_question_block(current_latex, n)` bóc tách chính xác khối mã LaTeX của câu hỏi thứ $n$ trong tài liệu hiện tại (chuẩn `ex_test.sty` hoặc nhãn `\textbf{Câu n.}`).
  3. Cơ chế Smart Diff Binding liên kết trực tiếp `old_text = câu_hỏi_cũ` và `new_text = câu_hỏi_mới` do AI hoặc local fallback sinh ra, bỏ qua hoàn toàn việc so sánh tương đồng chuỗi `SequenceMatcher` (vốn thất bại khi câu mới khác đề tài câu cũ).
  4. Phản hồi API trả về `diff` và `diffs` hợp lệ:
     - Trên editor: Kích hoạt Inline Diff Overlay và Top Banner tại đúng vị trí câu thứ $n$, bôi đen vùng mã cũ để giáo viên duyệt.
     - Trong chat bubble: Ẩn khối mã diff, hiển thị badge *"Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn"*.
  5. *Luồng ngoại lệ (Nếu diff rỗng hoặc câu hỏi N không tìm thấy trong editor):*
     - Hệ thống giữ nguyên vẹn khối mã nguồn LaTeX trong chat bubble.
     - Hiển thị 3 nút bấm tương tác: `[📥 Chèn vào con trỏ]`, `[📋 Sao chép]`, và `[🔄 Áp dụng thay thế]`.
     - Tuyệt đối không xóa nuốt mất mã của người dùng và không hiển thị badge gợi ý sai lệch.
