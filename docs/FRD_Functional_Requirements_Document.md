# TÀI LIỆU ĐẶC TẢ CHỨC NĂNG (FUNCTIONAL REQUIREMENTS DOCUMENT - FRD)
**Dự án: Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-FRD-01  
- **Phiên bản:** 3.0 (Động cơ Thay thế Câu hỏi Thông minh Question Replacement Engine, Đồng bộ Chat-Editor An toàn & Quy tắc Git Workflow Tuyệt đối Không Tự Động Tạo PR)  
- **Mục tiêu đặc tả:** Mô tả chi tiết hành vi dữ liệu, giao diện người dùng, điều kiện biên, API endpoints và quy tắc logic giải quyết các bài toán gõ lại đề, dựng đồ thị vector SVG, trộn đề an toàn, xuất bản in ấn, trợ lý soạn thảo AI copilot thông minh, và quy chuẩn quản trị phát triển Git.  
- **Ngày phát hành:** 2026-10-24  
- **Trạng thái:** Hoàn thành đặc tả chi tiết & Sẵn sàng vận hành

---

## 1. TỔNG QUAN TÀI LIỆU

### 1.1. Mục đích
Tài liệu Đặc tả Chức năng (FRD) mô tả chi tiết luồng xử lý dữ liệu, giao diện người dùng, điều kiện biên, các API endpoints và quy tắc nghiệp vụ cho từng phân hệ trong hệ thống Quesy, giải quyết trực tiếp các khó khăn trong quy trình biên soạn và tổ chức kiểm tra đánh giá.

### 1.2. Quy tắc Quản trị Git Workflow & Không Tự Động Tạo Pull Request (Mandatory Git Rule)
- **Bắt buộc:** Mọi tác vụ phát triển, sửa lỗi và nâng cấp tính năng chỉ thực hiện `git commit` và `git push` lên nhánh remote repository.
- **TUYỆT ĐỐI KHÔNG TỰ ĐỘNG TẠO PULL REQUEST (`gh pr create`, API PR...)** hoặc tự động cập nhật vào Pull Request trừ khi Người dùng (User) có yêu cầu rõ ràng bằng lời nói (explicit user prompt). Mọi hành vi tự động tạo PR khi chưa có lệnh trực tiếp đều vi phạm quy chuẩn quản trị dự án.

### 1.3. Danh mục Phân hệ Chức năng
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

### 2.3. FR-02.1: Không Gian Soạn Thảo Đề Thi Phân Tách 2 Cột Co Giãn Linh Hoạt (Resizable Split Layout)
- **Màn hình liên quan:** `SCR-COMPOSER-STUDIO`
- **Bố cục không gian làm việc (Mặc định 60% : 40%, tùy biến 25% - 75%):**
  - **Cột bên trái (Editor Pane):**
    - *Khung trên:* Trình soạn thảo mã nguồn LaTeX Dark mode (`#141824`, bảo toàn màu nền khi click con trỏ focus) với toolbar `MỚI`, `THÊM ▾` (7 template chuẩn `ex_test`), các phím tắt `Undo`, `Redo`, `Xóa`, `Copy`, đánh số dòng (gutter), thanh trạng thái dòng/cột.
    - *Thanh Banner Duyệt Diff (`#composer-pending-diff-banner`):* Neo ngay trên vùng soạn thảo tại dòng cần thay đổi, hiển thị trực quan so sánh mã cũ và mới kèm 2 nút bấm `[Đồng ý]` / `[Từ chối]`.
    - *Khung dưới:* Thanh nhập Prompt thu gọn (Compact Pill Bar) và Trợ lý Soạn thảo AI (Copilot Popup) hỗ trợ sinh câu hỏi trắc nghiệm, Đúng/Sai QĐ 764, bảng biến thiên `tkz-tab` và đồ thị TikZ, kèm thanh kéo thả biên trên và pill handle tùy chỉnh độ cao.
  - **Thanh phân cách kéo thả ngang (`#composer-col-splitter`):**
    - Đặt giữa cột Editor và Live Preview, con trỏ dạng `cursor-col-resize`, cho phép người dùng kéo thả chuột hoặc chạm vuốt để co giãn tỷ lệ chiều rộng 2 cột linh hoạt từ 25% đến 75%.
  - **Cột bên phải (Preview Pane):**
    - *Thanh công cụ trên (Light mode):* Hai tab điều hướng `ẢNH` và `LỊCH SỬ`, công tắc chuyển đổi `LỜI GIẢI` (tự động chuyển đổi giữa chế độ in đề thi `[dethi]` và in lời giải `[loigiai]`), menu `XUẤT FILE ▾` (tải PDF, tải TeX, lưu Ngân hàng, sao chép mã).
    - *Khung giữa:* Bản xem trước PDF Trực tiếp (Live Preview) hiển thị PDF biên dịch sắc nét từ Tectonic XeTeX engine hoặc danh sách lịch sử các phiên bản.
    - *Chân trang (Footer):* Nút bấm toàn chiều rộng nổi bật màu xanh dương **`BIÊN DỊCH`** (`#0071e3`) kích hoạt biên dịch tài liệu tức thì.

### 2.4. FR-02.2: Tự Động Biên Dịch, Lưu Trữ Cục Bộ & Xuất Bản Đề Thi
- **Hành vi thao tác:**
  - **Tự động biên dịch (Auto-compile):** Tự động biên dịch sau khi ngừng gõ 800ms hoặc nhấn phím tắt `Ctrl+S` / `Cmd+S`.
  - **Lưu trữ tự động (Local Storage Persistence):** Tự động lưu bản nháp văn bản và hội thoại vào `localStorage`, khôi phục nguyên vẹn khi tải lại trang (F5).
  - **Nạp mẫu đề thi chuẩn:** Cung cấp sẵn các mẫu: Đề thi Chuẩn Quốc Gia 2025 (`ex_test` v3.3), Đề thi Chuẩn Thông tư 32 (3 phần), Chuyên đề Bảng biến thiên tkz-tab, Chuyên đề Hình học không gian TikZ, Tài liệu mới.
  - **Lưu vào Ngân hàng:** Trích xuất các câu hỏi từ mã LaTeX sang các bản ghi ngân hàng câu hỏi chuẩn hóa (`questions` table) chỉ với 1 click, hỗ trợ đồng thời cả cú pháp `ex_test` (`\begin{ex}`) và cú pháp truyền thống (`\textbf{Câu X.}`).
  - **Tải tệp PDF & .TEX:** Xuất bản tệp PDF vector-crisp 100% font CMU Serif và tệp nguồn LaTeX `.tex`.

### 2.4.1. FR-02.3: Thanh Nhập Prompt AI Thu Gọn, Cơ Chế Xóa Sạch Lạc Quan (Optimistic Input Reset) & Quy Chuẩn Màu Tương Phản Dark Mode
- **Vị trí & Kiểu dáng:**
  - Thanh dạng viên thuốc (floating pill bar) neo tại chân khung soạn thảo LaTeX (`bottom-7`, căn giữa theo chiều ngang `left-1/2 -translate-x-1/2`, chiều rộng `w-[92%] max-w-xl`).
  - Giao diện Apple Glassmorphism: Nền bán trong suốt `#1c1c1f/95`, hiệu ứng mờ hậu cảnh `backdrop-blur-md`, viền tinh tế `border-white/15`, đổ bóng sâu `shadow-2xl`.
- **Quy tắc Tương tác & Kích hoạt 2 Trạng Thái:**
  1. *Trạng thái Nhập liệu Cục bộ (In-place Text Input):*
     - Khi người dùng nhấp chuột vào thanh hoặc trường nhập `#composer-compact-input`, con trỏ chuột duy trì dạng `cursor-text` và trường nhập nhận focus bình thường.
     - **Quy tắc bất biến:** Việc nhấp chuột vào thanh hoặc trường nhập **tuyệt đối không tự động mở full popup trợ lý**. Giáo viên có thể thoải mái click để nhập, chỉnh sửa, dán (paste) nội dung yêu cầu mà không bị che khuất không gian làm việc.
  2. *Trạng thái Kích hoạt Mở rộng & Gửi Lệnh (Expansion & Dispatch Trigger):*
     - Chỉ khi người dùng thực hiện một trong hai hành động sau thì hệ thống mới kích hoạt mở bung full giao diện Popup Trợ lý Soạn thảo (`composer-ai-popup`):
       - Nhấn phím **`Enter`** (bắt sự kiện `keydown` -> `handleCompactInputKey`).
       - Nhấp chuột vào **Nút Gửi Mũi Tên Tròn** (nút màu trắng nền tròn với icon `arrow-up` -> `submitFromCompact`).
     - Khi mở rộng:
       - Popup Trợ lý trượt mượt mà từ đáy khung soạn thảo lên chiếm `56%` chiều cao (có thể phóng to `78%` hoặc toàn màn hình `92%`).
       - Thanh Compact Bar tạm thời ẩn (`hidden`) để nhường chỗ cho giao diện chat chuyên sâu.
       - Dữ liệu text trong Compact Input được tự động chuyển tiếp vào ô chat chính và xóa trắng ô thu gọn.
       - Nếu có nội dung text, hệ thống tự động kích hoạt tiến trình gửi yêu cầu `sendPrompt(text)` đến Backend, chèn tin nhắn người dùng vào lịch sử và hiển thị bong bóng loading `Trợ lý đang xử lý yêu cầu...`.
  3. *Cơ Chế Xóa Sạch Lạc Quan (Optimistic Dual-Input Reset & Event Decoupling):*
     - **Khắc phục lỗi:** Triệt tiêu hoàn toàn hiện tượng text chat cũ còn lưu kẹt trong ô nhập chat của trợ lý sau khi đã gửi đi (Ảnh 1).
     - **Thực thi đồng bộ tại $t = 0\text{ms}$:** Ngay khi sự kiện gửi được kích hoạt (`submitChat`, `submitFromCompact`, hoặc `sendPrompt`), hệ thống lập tức gán `chatInput.value = ''` và `compactInput.value = ''` đồng thời, không đợi phản hồi mạng hoặc kết thúc hiệu ứng mở popup.
     - **Tách bạch ngữ nghĩa `openAIPopup`:** `submitFromCompact()` chỉ gọi `this.openAIPopup('')` với chuỗi rỗng; tuyệt đối không truyền lại prompt vào `prefillPrompt` (loại bỏ lỗi gán ngược nội dung đã gửi vào `chatInput.value`). `prefillPrompt` chỉ được sử dụng khi giáo viên chủ động bấm chọn mẫu lệnh nhanh (`applyQuickPrompt`) để biên tập trước khi gửi.
     - Con trỏ nhập liệu duy trì sẵn sàng ở đầu ô nhập trống với caret xanh Apple `#38bdf8`, sẵn sàng cho lượt chat tiếp theo.
  4. *Menu Mẫu Câu Lệnh Nhanh (Quick Actions):*
     - Nút dấu cộng `+` bên cạnh nút gửi cho phép mở menu popover danh mục prompt tiêu chuẩn (Đổi cỡ chữ 12pt, Sinh trắc nghiệm 4 lựa chọn, Sinh Đúng/Sai QĐ 764, Vẽ bảng biến thiên `tkz-tab`, Sửa cú pháp LaTeX).
     - Khi chọn một mẫu, hệ thống tự động mở popup và điền sẵn prompt vào ô chat.
- **Quy chuẩn Màu Tương Phản Dark Mode (Sửa lỗi chữ đen trên nền tối):**
  - Khắc phục triệt để lỗi chữ màu đen `#1d1d1f` bị chìm trên nền tối `#1c1c1f` / `#141824`.
  - Thiết lập design tokens bắt buộc với độ ưu tiên cao (`!important`) cho cả 2 trường nhập liệu `#composer-compact-input` và `#composer-chat-input`:
    - *Text Color:* `#f8fafc` (Slate-50) hoặc `#ffffff` xuyên suốt mọi trạng thái (default, hover, focus, active).
    - *Placeholder Color:* `rgba(226, 232, 240, 0.5)` (Slate-200 / 50%) phân biệt rõ ràng nhưng dịu mắt trên nền tối.
    - *Caret Color (Con trỏ nhập liệu):* `#38bdf8` (Sky-400 / Apple Blue) định vị sắc nét vị trí con trỏ.
    - *Selection Color:* `::selection { background-color: rgba(59, 130, 246, 0.4); color: #ffffff; }`.
    - *Background & Borders:* Nền trong suốt `background-color: transparent !important`, loại bỏ toàn bộ viền trong, bóng hộp mặc định (`border: none !important; outline: none !important; box-shadow: none !important`).

### 2.4.2. FR-02.4: Động Cơ Thay Thế Dòng Mờ Đa Tầng (Fuzzy Line Replacement Engine)
- **Mục tiêu Nghiệp vụ:** Khi giáo viên nhấn [Đồng ý áp dụng] / [Apply], hệ thống phải thay thế chuẩn xác đoạn mã nguồn được đề xuất với tỷ lệ thành công $\ge 99.5\%$, triệt tiêu hoàn toàn thông báo lỗi toast "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại".
- **Thuật toán Khớp Mờ 5 Tầng (5-Tier Resilient Line Matcher):**
  1. *Tầng 1 - Exact Substring Match:* Tìm kiếm nguyên bản `old_text` trong bộ đệm văn bản hiện hành `editor.value` (đồng bộ hai chiều với `this.currentLatex`).
  2. *Tầng 2 - Whitespace & Linebreak Normalization:* Chuẩn hóa toàn bộ ngắt dòng Windows CRLF (`
\n`) về Unix LF (`\n`), đồng thời loại bỏ khoảng trắng thừa cuối dòng (trailing spaces).
  3. *Tầng 3 - Indentation-Insensitive Match & Preserved Re-indent:* Phân rã khối văn bản thành từng dòng, bỏ qua thụt lề đầu dòng (leading indentation / tabs / spaces) để tìm kiếm khối dòng tương đồng; khi áp dụng `new_text`, tự động tái gán thụt lề ban đầu của mã nguồn để bảo toàn cấu trúc code thẩm mỹ.
  4. *Tầng 4 - Sliding Window Sequence Matcher:* Quét cửa sổ trượt $W \in [M - 2, M + 3]$ dòng quanh vị trí nghi vấn, tính toán tỷ lệ tương đồng ký tự qua thuật toán Levenshtein / Gestalt Pattern Matching; tự động chấp nhận thay thế khi độ tương đồng $\ge 0.60$.
  5. *Tầng 5 - Pinned Line Index & Range Replacement:* Sử dụng số thứ tự dòng (`lineNo`) và phạm vi chỉ số ký tự (`matchRange: [start, end]`) đã được xác định và ghim cố định từ bước hiển thị gợi ý `showPendingDiff()` để thay thế trực tiếp vào phạm vi đó nếu chuỗi văn bản đã bị biến đổi nhẹ.

### 2.4.3. FR-02.5: Giao Diện Trực Quan Hóa Diff Trực Tiếp Trên Ô Soạn Thảo (Inline Editor Diff Overlay / Banner Độc Quyền)
- **Mục tiêu:** Cung cấp trải nghiệm chỉnh sửa hiện đại tương đương Cursor / VS Code Copilot: hiển thị khối so sánh Diff trực quan trực tiếp tại đúng vị trí dòng mã nguồn cần sửa đổi trên trình soạn thảo. **Bắt buộc:** Tuyệt đối KHÔNG hiển thị widget diff trùng lặp trong bubble chat của Trợ lý để giữ không gian hội thoại tinh giản, trực quan.
- **Cấu trúc & Thành phần Giao diện:**
  1. *Khối Dòng Đỏ Xóa (`- <old_line>`):* Nền đỏ mờ `rgba(225, 29, 72, 0.15)` (`bg-rose-950/70`), viền trái đỏ tươi `border-l-4 border-rose-500`, văn bản đỏ `text-rose-300`, hiển thị chính xác nội dung dòng mã cũ kèm ký hiệu `-`.
  2. *Khối Dòng Xanh Thêm (`+ <new_line>`):* Nền xanh lục mờ `rgba(16, 185, 129, 0.15)` (`bg-emerald-950/70`), viền trái xanh ngọc `border-l-4 border-emerald-500`, văn bản xanh `text-emerald-300`, hiển thị chính xác nội dung dòng mã mới kèm ký hiệu `+`.
  3. *Thanh Điều Khiển Hành Động Hỗ Trợ Đa Diff (Multi-Diff Controls):*
     - **Viên thuốc Đếm Động (Dynamic Capsule Counter):** Hiển thị vị trí diff hiện thời trên tổng số diff (ví dụ: `1/3`, `2/3`, `3/3`), thay thế số tĩnh `1/1`.
     - **Bộ Điều Hướng Tuần Tự (Prev / Next Stepper):** Nút **`[< Trước]`** (`prevDiff()`) và nút **`[Sau >]`** (`nextDiff()`) cho phép chuyển đổi nhanh qua lại giữa các khối diff trong danh sách `pendingDiffs`. Tự động vô hiệu hóa/mờ khi ở biên hoặc khi chỉ có 1 diff duy nhất.
     - Nút **`[Keep / Đồng ý]`**: Icon checkmark, nền xanh dương `bg-blue-600 hover:bg-blue-500 text-white`, nhấp vào áp dụng ngay thay đổi qua Fuzzy Replacement Engine. Tự động loại bỏ diff này khỏi danh sách `pendingDiffs`; nếu còn diff thì chuyển sang diff tiếp theo, nếu hết thì tự động đóng overlay và kích hoạt `compile(true)`.
     - Nút **`[Undo / Từ chối]`**: Icon undo / dismiss, nền xám tối `bg-slate-700 hover:bg-slate-600 text-slate-200`, nhấp vào hủy bỏ gợi ý sửa đổi hiện tại và chuyển sang diff kế tiếp (nếu còn).
     - Nút **`[Áp dụng tất cả] (Apply All)`**: Hiển thị khi `pendingDiffs.length > 1` trên cả Top Banner và Inline Overlay với nền xanh Apple nổi bật, cho phép hợp nhất toàn bộ các khối diff được gợi ý vào mã nguồn trong một thao tác duy nhất.
  4. *Neo Tọa Độ & Đồng Bộ Cuộn:* Vị trí của Inline Overlay được neo theo tọa độ dòng nguồn trong editor (`top = (lineNo - 1) * lineHeight`), tự động cuộn đồng bộ mượt mà khi người dùng cuộn textarea editor.
  5. *Song Hành Cùng Banner Đỉnh:* Duy trì banner cố định trên đầu editor (`#composer-pending-diff-banner`) đóng vai trò thanh thông báo tổng quan với đầy đủ bộ đếm động, nút duyệt tuần tự, Keep/Undo và nút [Áp dụng tất cả], đồng bộ trạng thái 100% với Inline Overlay.
  6. *Quy Tắc Bubble Chat Thuần Túy:* Bubble chat của trợ lý chỉ hiển thị phản hồi lời văn (text explanation), hướng dẫn sư phạm hoặc phân tích nguyên nhân lỗi, hoàn toàn không chèn widget diff hay nút duyệt diff lặp lại.

### 2.4.4. FR-02.6: Cơ Chế Chuyển Tiếp & Phân Tích Log Lỗi Biên Dịch LaTeX (Compile Error Forwarding & Diagnostics)
- **Mục tiêu:** Hỗ trợ giáo viên khắc phục lỗi cú pháp LaTeX / Tectonic tức thì mà không cần tự đọc log lỗi dòng lệnh phức tạp.
- **Luồng Dữ Liệu:**
  1. *Ghi nhận Lỗi Biên dịch:* Khi biên dịch `POST /api/v1/composer/compile` trả về lỗi (`success = false`), client tự động bắt lấy thông điệp lỗi `errMsg = data.error` và lưu trữ bền vững vào `app.composer.lastCompileError`.
  2. *Chuyển tiếp Tự động:* Khi người dùng gửi prompt kế tiếp (nhất là câu lệnh yêu cầu sửa lỗi như "sửa lỗi", "tại sao lỗi"), payload gửi đến `POST /api/v1/composer/chat` tự động đính kèm trường `compile_error_log: this.lastCompileError`.
  3. *Chẩn đoán & Sinh Diff Sửa Lỗi Phía Server:*
     - API `composer.py` trích xuất thông tin lỗi từ log (ví dụ: `! Undefined control sequence \badcommand`, `! Missing $ inserted`, `l.18 ...`).
     - AI Copilot phân tích ngữ cảnh `current_latex`, khoanh vùng dòng mã gây lỗi, và tự động tạo khối `diff` đề xuất phương án sửa: thay thế bằng lệnh chuẩn, thêm gói lệnh thiếu vào preamble, hoặc đóng chú thích `%` để loại bỏ lỗi.
  4. *Thiết lập Lại Trạng Thái:* Khi bản biên dịch tiếp theo thành công, `lastCompileError` tự động reset về `null`.

### 2.4.5. FR-02.7: Tối Ưu Hóa Hiệu Năng Gửi Prompt & Box Chat Mượt Mà (Fast Prompt Dispatch & Smooth Chat Micro-Interactions)
- **Mục tiêu:** Loại bỏ hoàn toàn cảm giác giật, lag hoặc độ trễ khi thao tác trên thanh nhập lệnh và hộp thoại Trợ lý AI.
- **Tiêu chuẩn Kỹ thuật:**
  1. *Phản Hồi Lập Tức (Optimistic UI & Instant Transition):* Khi người dùng nhấn `Enter` hoặc nhấp nút gửi, trong vòng $\le 16$ ms (1 frame), thanh compact input lập tức ẩn, nội dung tin nhắn được đẩy vào lịch sử hội thoại, khung chat cuộn mượt đến đáy (`behavior: 'smooth'`) và hiển thị bong bóng loading `Trợ lý đang xử lý yêu cầu...`.
  2. *Chuyển Động Hardware-Accelerated:* Hộp thoại Popup Trợ lý sử dụng thuộc tính CSS `transform: translate3d(0, 0, 0)`, `transition: transform 200ms cubic-bezier(0.16, 1, 0.3, 1)`, loại bỏ tình trạng giật cục (jank) khi co giãn chiều cao.
  3. *Tối Ưu DOM & Lucide Icon Parsing:* Thay vì quét toàn trang qua `lucide.createIcons()`, hệ thống chỉ gọi render icon cục bộ trong node tin nhắn mới, giảm thiểu 95% thời gian layout thrashing.
  4. *Non-blocking Async AI Request:* Kết nối Backend AI sử dụng `httpx.AsyncClient` bất đồng bộ với timeout linh hoạt 15s kèm cơ chế fallback quy tắc thông minh tức thì, triệt tiêu hiện tượng đóng băng socket hay nghẽn thread pool.

### 2.4.6. FR-02.8: Kéo Thả Điều Chỉnh Độ Cao Box Trợ Lý Soạn Thảo (Vertical Drag Resize & Unified Single Pill Handle)
- **Mục tiêu:** Cho phép giáo viên thay đổi chiều cao của Popup Trợ lý Soạn thảo (`#composer-ai-popup`) một cách trực quan, mượt mà theo phương đứng với duy nhất một điểm chạm kéo thả chuẩn Apple HIG.
- **Hành vi tương tác:**
  1. *Điểm chạm hợp nhất (Unified Single Pill Handle):* Toàn bộ thao tác kéo thả và nhấp đổi độ cao được tích hợp vào **duy nhất 1 thanh ngang viên thuốc** (`#composer-ai-resize-handle`) đặt tại trung tâm header của popup trợ lý. Loại bỏ hoàn toàn thanh pill phụ bên trên mép popup, tránh trùng lặp thị giác.
  2. *Sự kiện kéo thả:* Bắt `mousedown`/`touchstart` trên `#composer-ai-resize-handle`, theo dõi `mousemove`/`touchmove` trên toàn màn hình, cập nhật chiều cao `newHeight = startHeight + (startY - currentY)` trong thời gian thực (60 FPS, tạm ngắt transition).
  3. *Bộ kẹp an toàn (Clamping):* Giới hạn chiều cao từ $180\text{px}$ (hoặc $20\%$ khung editor) đến $92\%$ chiều cao khung editor, tránh làm ẩn header công cụ.
  4. *Ghi nhớ thiết lập:* Lưu chiều cao vào `localStorage` (`quesy_composer_ai_height`) để khôi phục cho các lần làm việc tiếp theo.
  5. *Tương thích nhấp đúp:* Nhấp chuột đơn (click) hoặc nhấp đúp (dblclick) vào thanh pill handle không kéo thả hỗ trợ chuyển đổi nhanh (toggle) độ cao giữa 56% và 78%.

### 2.4.7. FR-02.9: Quản Lý Khởi Tạo Phiên Chat Mới Sạch Sẽ & Ngăn Kéo Lịch Sử Phiên Cũ (Session Lifecycle & Clean Workspace)
- **Mục tiêu:** Đảm bảo mỗi phiên làm việc mới luôn có không gian hội thoại gọn gàng, khởi đầu sạch sẽ với lời chào mặc định, đồng thời lưu trữ đầy đủ các phiên cũ vào ngăn kéo Lịch sử.
- **Hành vi nghiệp vụ:**
  1. *Khởi đầu Sạch sẽ (Fresh Initial State):* Khi mở trang `/composer` hoặc nhấn nút "Bắt đầu hội thoại mới" (`newChat`), khung chat active chỉ hiển thị 1 tin nhắn chào mặc định từ Quesy Copilot, không nạp lại lịch sử chat của các phiên trước đó.
  2. *Lưu trữ Phiên Cũ Tự động:* Khi bắt đầu phiên mới, nếu phiên hiện tại có $\ge 1$ tin nhắn người dùng, hệ thống tự động lưu trữ phiên này vào mảng `quesy_composer_chat_sessions` trong `localStorage`.
  3. *Bảng Lịch Sử Phiên Cũ (History Panel):* Khi người dùng nhấn nút **`[Lịch sử]`** (`#composer-ai-history-btn`), hiển thị danh sách các phiên cũ với timestamp, tóm tắt câu lệnh và số lượng trao đổi. Người dùng có thể xem lại câu lệnh cũ, tải lại phiên hoặc xóa sạch lịch sử.

### 2.4.8. FR-02.10: Thanh Phân Tách Kéo Thả Ngang 2 Cột Editor & Live Preview Chuẩn Apple HIG (#composer-split-resizer)
- **Mục tiêu:** Cho phép người dùng tùy ý phân bổ tỷ lệ chiều rộng giữa Cột Mã Nguồn (Editor) và Cột Xem Trước (Live Preview) với thiết kế thanh kéo tinh tế chuẩn Apple Human Interface Guidelines, khoảng cách đệm thẩm mỹ không đè sát viền box soạn thảo (Ảnh 2).
- **Hành vi tương tác:**
  1. *Cấu trúc & Khoảng cách Đệm (Gutter Spacing):*
     - Thanh kéo `#composer-split-resizer` (class `composer-col-splitter`) nằm trong rãnh riêng biệt có độ rộng công thái học `w-3.5` (14px) hoặc `w-4` (16px), tích hợp khoảng đệm biên `mx-1` / `mx-1.5`.
     - Tuyệt đối không để vạch kéo hay hiệu ứng hover chạm đè hoặc dính sát vào đường viền bo góc của Cột Soạn thảo (`rounded-xl border border-[#272f42]`) hay Cột Xem trước (`rounded-xl border border-black/[0.08]`).
  2. *Thanh Cầm Viên Thuốc Apple HIG (Apple Capsule Grabber Handle):*
     - Vạch viên thuốc trung tâm: `w-1 h-9 rounded-full bg-slate-300 dark:bg-[#34415e]` mang phong cách Apple Deference.
     - Hover feedback: Tự động chuyển màu xanh Apple `#0071e3`, kéo dài nhẹ `scale-y-110`, quầng sáng vi mô `group-hover:shadow-[0_0_8px_rgba(0,113,227,0.35)]`. Vùng hover mềm bao quanh bo góc `rounded-lg`, nằm lọt lòng trong rãnh đệm.
     - Active feedback: Co nhẹ `scale-95` khi nhấn giữ (phản hồi xúc giác Emil Kowalski), bật cờ `.composer-resizing-h` trên toàn trang.
  3. *Sự kiện kéo thả:* Bắt sự kiện chuột/cảm ứng, tính toán tỷ lệ bề rộng cột trái `leftPercent` từ $25\%$ đến $75\%$ tổng chiều rộng container.
  4. *Tấm chắn con trỏ (Pointer Shield):* Bật `pointer-events: none` trên vùng xem trước PDF để ngăn chặn con trỏ bị bắt nhầm vào canvas/iframe khi kéo chuột nhanh.
  5. *Khôi phục Tỷ lệ Mặc định:* Nháy đúp chuột (`dblclick`) vào resizer lập tức đặt lại tỷ lệ 60:40 và kích hoạt `fitToWidth(true)`.
  6. *Lưu trữ cấu hình:* Lưu tỷ lệ vào `localStorage` (`quesy_composer_split_ratio`) và áp dụng ngay khi khởi tạo ứng dụng.

### 2.4.9. FR-02.11: Tự Động Co Giãn PDF Theo Chiều Rộng Cột & Khung Cuộn Ngang An Toàn (PDF Auto Fit-to-Width & Horizontal Scroll Resiliency)
- **Mục tiêu:** Đảm bảo trang tài liệu PDF tự động co giãn theo chiều ngang khi kích thước khung preview thay đổi và cho phép cuộn ngang an toàn, không xén mất mép phải trang.
- **Hành vi tương tác & Đặc tả:**
  1. *Khung cuộn an toàn (#composer-pdf-scroll-container):*
     - Áp dụng `overflow-x-auto overflow-y-auto` thay thế cho `overflow-x-hidden`.
     - Vùng chứa trang `#composer-pdf-pages` (`min-w-full w-fit flex flex-col items-center space-y-3`) kết hợp căn giữa an toàn cho `.pdf-page-card` (`mx-auto`).
     - Khi kích thước trang vượt quá khung nhìn, tài liệu bắt đầu từ lề trái $x=0$, thanh cuộn ngang hiển thị đầy đủ, không bao giờ bị xén mất lề phải.
  2. *Cơ chế Auto Fit-to-Width:*
     - Lắng nghe biến đổi kích thước khung preview qua `ResizeObserver`.
     - Khi người dùng kéo thanh splitter `#composer-col-splitter` hoặc đổi cỡ cửa sổ trình duyệt: nếu `isAutoFit === true`, hệ thống tự động tính toán lại tỷ lệ `fitZoom = (containerWidth - 48) / basePageWidth` và co giãn thẻ trang/canvas mượt mà theo thời gian thực (60 FPS trong lúc kéo), sau đó kích hoạt vẽ lại vector sắc nét (debounced 100ms).
     - Khi người dùng zoom thủ công, chuyển `isAutoFit = false`. Khi nhấn `resetZoom()` (1:1), bật lại `isAutoFit = true` và tự động căn khít chiều ngang.

### 2.4.10. FR-02.12: Thuật Toán Phóng To / Thu Nhỏ Thông Minh Theo Điểm Neo Chuột & Trọng Tâm Viewport (Smart Zoom-to-Point & Center Anchor Engine)
- **Mục tiêu:** Khắc phục triệt để lỗi tài liệu PDF bị giật về góc trên cùng bên trái $(0, 0)$ khi thực hiện thao tác zoom.
- **Thuật toán & Cơ chế:**
  1. *Xác định điểm neo linh hoạt:*
     - *Mode 1 (Cursor Anchor):* Khi zoom bằng cuộn chuột (`Ctrl + Wheel`) và con trỏ nằm trên vùng xem trước PDF, lấy tọa độ con trỏ chuột $(x_v, y_v) = (\text{e.clientX}, \text{e.clientY})$ làm điểm neo cố định. Điểm ảnh tài liệu tại con trỏ giữ nguyên vị trí dưới đầu chuột.
     - *Mode 2 (Center Anchor):* Khi zoom bằng nút bấm `+` / `-` trên thanh công cụ nổi hoặc phím tắt (con trỏ nằm ngoài tài liệu), lấy chính giữa khung nhìn làm điểm neo: $(x_v, y_v) = (\text{rect.left} + \text{width}/2, \text{rect.top} + \text{height}/2)$. Trọng tâm màn hình đang quan sát được giữ nguyên.
  2. *Công thức cuộn tỷ lệ:*
     - Ghi nhận tỷ lệ tọa độ nội dung trước khi đổi zoom: $r_x = (\text{scrollLeft} + dx) / \text{scrollWidth}$, $r_y = (\text{scrollTop} + dy) / \text{scrollHeight}$.
     - Cập nhật tỷ lệ phóng thu `zoomLevel` mới trong khoảng $[0.4, 2.5]$, gán kích thước mới cho các thẻ trang trong DOM.
     - Cập nhật ngay tọa độ cuộn: $\text{scrollLeft} = \text{round}(r_x \times \text{scrollWidth}_{\text{new}} - dx)$, $\text{scrollTop} = \text{round}(r_y \times \text{scrollHeight}_{\text{new}} - dy)$.
  3. *Chống rung khi render lại:* Lưu giữ và phục hồi tọa độ cuộn khi `renderAllPages()` chạy lại với devicePixelRatio, đảm bảo không có bất kỳ hiện tượng nhảy giật khung hình nào.

### 2.4.11. FR-02.13: Cơ Chế Bóc Tách Đa Khối Diff & Duyệt Hàng Loạt (Multi-Diff Extraction & Sequential / Batch State Machine)
- **Mục tiêu Nghiệp vụ:** Cho phép AI Copilot đề xuất nhiều thay đổi đồng thời trong một phản hồi (ví dụ: đổi font, sửa đáp án, vẽ hình TikZ, sửa lỗi biên dịch) và hỗ trợ giáo viên duyệt từng sửa đổi (1/N, Trước/Sau, Keep/Undo) hoặc áp dụng toàn bộ chỉ với 1 cú click (Ảnh 3).
- **Đặc tả Schema Hợp Đồng API (`/api/v1/composer/chat`):**
  - **Mô hình Dữ liệu Đa Diff:**
    ```python
    class DiffSuggestion(BaseModel):
        action: str = Field("replace", description="'replace' or 'insert'")
        old_text: str = Field(..., description="Đoạn mã LaTeX cũ cần tìm để thay thế")
        new_text: str = Field(..., description="Đoạn mã LaTeX mới cần đưa vào")
        description: str = Field("", description="Tóm tắt ngắn gọn mục đích sửa đổi")

    class ChatResponse(BaseModel):
        reply: str
        suggested_latex: Optional[str] = None
        diff: Optional[DiffSuggestion] = None  # Khối diff đầu tiên (tương thích ngược)
        diffs: Optional[List[DiffSuggestion]] = Field(default_factory=list, description="Danh sách toàn bộ các khối diff")
    ```
- **Thuật toán Bóc Tách Đa Khối (`extract_all_diffs_from_text`):**
  1. *Backend Python & Frontend JS song hành:* Duyệt tìm toàn bộ các mẫu đề xuất thay đổi:
     - Toàn bộ các khối ````diff ... ```` qua regex lặp (`re.finditer` / `matchAll`).
     - Toàn bộ các khối `OLD: ... NEW: ...` hoặc `CŨ: ... MỚI: ...`.
     - Toàn bộ các khối `SEARCH / REPLACE` (Aider standard format).
     - Toàn bộ các khối `Thay thế: ```latex ... ``` bằng: ```latex ... ``` `.
     - Các câu lệnh nội dòng `Thay thế `A` bằng `B``.
     - Đổi font chữ và đổi đáp án trắc nghiệm `\choice`.
  2. *Khử trùng lặp (Deduplication):* Loại bỏ các khối diff trùng `old_text` hoặc có `old_text == new_text`.
  3. *Tương thích ngược:* Luôn gán `diff = diffs[0]` nếu `diffs` không rỗng.
- **Quy Trình Duyệt & Cỗ Máy Trạng Thái (State Machine):**
  - Trạng thái client: `pendingDiffs: []`, `currentDiffIndex: 0`, `pendingDiff: pendingDiffs[currentDiffIndex]`.
  - Giao diện Hiển thị Kép (Top Banner `#composer-pending-diff-banner` & Inline Overlay `#composer-inline-diff-overlay`):
    * **Huy hiệu Đếm Động (Dynamic Capsule Counter):** Thay thế số `1/1` cứng bằng viên thuốc hiển thị `${currentDiffIndex + 1}/${pendingDiffs.length}` (ví dụ: `1/3`, `2/3`, `3/3`).
    * **Bộ Điều Hướng Tuần Tự (Prev / Next Stepper):**
      - Nút **`[< Trước]`** (`prevDiff()`): Di chuyển về diff trước đó, tự động cuộn màn hình và bôi đen vị trí dòng tương ứng. Tự động disable/mờ khi `currentDiffIndex === 0`.
      - Nút **`[Sau >]`** (`nextDiff()`): Di chuyển tới diff kế tiếp. Tự động disable/mờ khi `currentDiffIndex === pendingDiffs.length - 1`.
      - Tự động ẩn hoặc vô hiệu hóa khi `pendingDiffs.length <= 1`.
    * **Nút `[Keep / Đồng ý]` (`applyCurrentDiff()`):**
      - Áp dụng diff hiện tại vào mã nguồn qua Động cơ Thay thế Mờ 6 Tầng (`applyDiffDirect`).
      - Loại bỏ diff này khỏi danh sách (`pendingDiffs.splice(currentDiffIndex, 1)`).
      - Nếu hết diff: Tự động đóng banner/overlay, hiển thị toast thành công và recompile PDF.
      - Nếu còn diff: Tự động chuyển trọng tâm hiển thị sang diff kế tiếp trong danh sách (`renderCurrentDiff()`).
    * **Nút `[Undo / Từ chối]` (`rejectCurrentDiff()`):**
      - Bỏ qua diff hiện tại không áp dụng, loại bỏ khỏi `pendingDiffs`.
      - Nếu hết diff: Tự động đóng banner/overlay.
      - Nếu còn diff: Hiển thị diff tiếp theo.
    * **Nút `[Áp dụng tất cả] (Apply All)` (`applyAllPendingDiffs()`):**
      - Hiển thị nổi bật với nền xanh Apple (`bg-blue-600 hover:bg-blue-500 text-white font-bold`) khi `pendingDiffs.length > 1`.
      - Duyệt qua toàn bộ danh sách `pendingDiffs` theo thứ tự từ trên xuống dưới, lần lượt áp dụng từng cặp `(old_text, new_text)` vào mã nguồn LaTeX.
      - Cập nhật giá trị một lần vào textarea editor và `this.currentLatex`.
      - Kích hoạt biên dịch lại PDF (`compile(true)`).
      - Đóng sạch sẽ banner và overlay (`dismissPendingDiffs()`).
      - Hiển thị Toast thông báo: *\"Đã áp dụng thành công toàn bộ N sửa đổi!\"*.

### 2.4.11. FR-02.13: Động Cơ Thay Thế Câu Hỏi Thông Minh & Đồng Bộ Chat-Editor An Toàn (Question Replacement Engine & Safe Chat Sync)
- **Mục tiêu:** Cho phép giáo viên ra lệnh thay thế câu hỏi trong đề thi qua ngôn ngữ tự nhiên (như *"Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"*, *"Thay câu 2 bằng câu khác"*, *"Sửa câu 3"*), tự động định vị đúng vị trí câu hỏi cũ trong LaTeX, tạo diff chính xác lên editor và bảo toàn giao diện chat bubble không bị nuốt mất code.
- **Quy trình xử lý chi tiết:**
  1. *Hàm bóc tách câu hỏi thứ N (`find_question_block(current_latex, n)`):*
     - Hỗ trợ chuẩn `ex_test.sty`: Trích xuất danh sách các khối `\begin{ex}(?:\[[^\]]*\])?[\s\S]*?\end{ex}` và lấy phần tử thứ `n - 1`.
     - Hỗ trợ chuẩn đánh số `\textbf{Câu N.}` hoặc `Câu N:`: Cắt lát từ vị trí bắt đầu nhãn câu $n$ đến trước nhãn câu tiếp theo hoặc thẻ kết thúc tài liệu.
     - Trả về chính xác chuỗi LaTeX nguyên bản của câu $n$ đang tồn tại trong editor để làm `old_text`.
  2. *Cơ chế gắn kết thông minh (Smart Diff Binding):*
     - Nhận diện các mẫu câu lệnh thay thế câu hỏi: `r'(?:thay thế|thay|đổi|sửa|chuyển|replace)\s*(?:cho\s+)?(?:câu|câu\s+hỏi|câu\s+số|bài|question)\s*(\d+)'`.
     - Lấy câu hỏi mới từ khối ````latex ... ```` hoặc ````diff ... ```` do AI hoặc động cơ fallback sinh ra.
     - Tự động gán `old_text = find_question_block(current_latex, n)` và `new_text = clean_new_code`.
     - Giải quyết triệt để vấn đề `SequenceMatcher` không tìm thấy old slice do câu hỏi mới khác biệt hoàn toàn về ngữ nghĩa/chủ đề toán học.
  3. *Cơ chế hiển thị Chat Bubble an toàn (Safe Chat Bubble Rendering):*
     - Cờ `hasDiff` chỉ kích hoạt khi `diff && diff.old_text && currentLatex.includes(diff.old_text.trim())`.
     - Nếu diff hợp lệ: Ẩn khối diff trong chat bubble, hiển thị badge *"Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn"*, chuyển diff tới editor banner/overlay.
     - Nếu KHÔNG có diff hợp lệ (hoặc diff rỗng): Giữ nguyên khối code trong chat bubble, hiển thị đầy đủ 3 nút thao tác:
       + `[📥 Chèn vào con trỏ]` (`insertB64Code`)
       + `[📋 Sao chép]` (`copyB64Code`)
       + `[🔄 Áp dụng thay thế]` (`replaceB64Code`)
     - Tuyệt đối không xóa code và không gắn badge chuyển diff giả tạo nếu editor chưa nhận được diff.
  4. *Động cơ Dự phòng Cục bộ (Local Fallback Generator):*
     - Nhận diện câu lệnh thay thế câu $n$ khi không có AI Provider kết nối.
     - Tự động sinh câu hỏi Toán THPT chuẩn `ex_test.sty` (đơn điệu hàm số, bảng biến thiên, cực trị) kèm lời giải chi tiết và tạo khối `DiffSuggestion` khớp đúng câu $n$ trong tài liệu hiện tại.

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

### 3.3. API Trợ Lý Soạn Thảo & Đề Xuất Sửa Đổi Diff (AI Copilot Chat Endpoint)
- **Endpoint:** `POST /api/v1/composer/chat`
- **Mô tả:** Tiếp nhận yêu cầu prompt từ giáo viên (từ thanh compact hoặc chat popup), phân tích cùng ngữ cảnh LaTeX hiện tại, bóc tách đề xuất sửa đổi thành cấu trúc `DiffSuggestion` để hiển thị trên editor.
- **Content-Type:** `application/json`
- **Request Body Payload:**
  ```json
  {
    "message": "Đổi cỡ chữ toàn tài liệu sang 12pt",
    "current_latex": "\\documentclass[11pt,a4paper]{article}\n\\usepackage{fontspec}\n\\begin{document}\n\\end{document}",
    "history": [
      {
        "role": "user",
        "content": "Chào trợ lý"
      },
      {
        "role": "assistant",
        "content": "Chào bạn! Tôi có thể hỗ trợ gì cho đề thi của bạn?"
      }
    ]
  }
  ```
- **Response Payload (`200 OK`):**
  ```json
  {
    "reply": "Tôi đề xuất thay đổi cỡ chữ toàn tài liệu từ `11pt` sang `12pt` tại dòng khai báo `\\documentclass`:\n\n```diff\n- \\documentclass[11pt,a4paper]{article}\n+ \\documentclass[12pt,a4paper]{article}\n```\n\nBấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này.",
    "suggested_latex": null,
    "diff": {
      "action": "replace",
      "old_text": "\\documentclass[11pt,a4paper]{article}",
      "new_text": "\\documentclass[12pt,a4paper]{article}",
      "description": "Đổi cỡ chữ toàn tài liệu sang 12pt"
    }
  }
  ```
- **Mô tả chi tiết Schema `DiffSuggestion`:**
  - `action` (`string`, required): Kiểu tác động (`replace` = thay thế đoạn mã hiện có; `insert` = chèn đoạn mã mới vào vị trí con trỏ).
  - `old_text` (`string`, required): Đoạn mã LaTeX cũ cần tìm và thay thế trong tài liệu hiện tại.
  - `new_text` (`string`, required): Đoạn mã LaTeX mới thay thế tương ứng.
  - `description` (`string`, required): Chuỗi tóm tắt mục đích sửa đổi để hiển thị trên huy hiệu banner editor.
