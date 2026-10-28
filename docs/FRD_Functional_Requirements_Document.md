# TÀI LIỆU ĐẶC TẢ CHỨC NĂNG (FUNCTIONAL REQUIREMENTS DOCUMENT - FRD)
**Dự án: Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-FRD-01  
- **Phiên bản:** 3.4 (Hoàn thiện Toàn diện Phân hệ Ma trận Đề thi 2D theo TT 22 & QĐ 764, Thư viện Presets, Đối soát Tồn kho Thời gian thực, Xuất bản Bản Đặc tả & Động cơ Sinh & Trộn Đề An Toàn 4 Nguyên Tắc)  
- **Mục tiêu đặc tả:** Mô tả chi tiết hành vi dữ liệu, giao diện người dùng, điều kiện biên, API endpoints và quy tắc logic giải quyết các bài toán gõ lại đề, hệ thống xác thực người dùng an toàn (PBKDF2, JWT HS256, OAuth Google/GitHub), phân hệ Ngân hàng câu hỏi toàn diện (CRUD, Modals Apple HIG, lọc 6 tầng TT 32, xuất PDF/CSV/LaTeX, nhập đề, kiểm tra trùng lặp AI >= 90%, đồng bộ badge), phân hệ Soạn đề tinh gọn tích hợp nút chuyên biệt "LƯU VÀO NGÂN HÀNG", phân hệ Ma trận đề thi 2D tương tác theo Thông tư 22/2021/TT-BGDĐT và Định dạng đề thi 2025 (Quyết định 764/QĐ-BGDĐT) với thư viện 3 Presets mẫu, đối soát tồn kho thời gian thực và xuất bản bản đặc tả (PDF/CSV/JSON), phân hệ Sinh & Trộn đề thi an toàn 4 nguyên tắc (Section Integrity, Passage Integrity, Option Anchor Rule 100%, Key Matrix), động cơ đổi câu hỏi đề gốc tương đương (In-Place Item Swap) và đóng gói trọn bộ ấn phẩm khảo thí (.ZIP/.PDF).
- **Ngày phát hành:** 2026-10-27  
- **Trạng thái:** Hoàn thành đặc tả chi tiết & Sẵn sàng vận hành

---

## 1. TỔNG QUAN TÀI LIỆU

### 1.1. Mục đích
Tài liệu Đặc tả Chức năng (FRD) mô tả chi tiết luồng xử lý dữ liệu, giao diện người dùng, điều kiện biên, các API endpoints và quy tắc nghiệp vụ cho từng phân hệ trong hệ thống Quesy, giải quyết trực tiếp các khó khăn trong quy trình biên soạn và tổ chức kiểm tra đánh giá.

### 1.2. Quy tắc Quản trị Git Workflow, Cổng Pre-Commit CI Gate & Cô Lập CI/CD (Mandatory CI/CD & Git Rules)
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

### 1.3. Danh mục Phân hệ Chức năng
- **MOD-01:** Phân hệ Tiếp nhận & Số hóa Đề thi bằng AI (AI Ingestion & Parsing)
- **MOD-02:** Phân hệ Studio Hậu kiểm Đối chiếu Song song (HITL Review Studio)
- **MOD-03:** Phân hệ Bộ Dựng Đồ Thị Vector SVG & Chuẩn Hóa Toán Học (TikZ & LaTeX Sanitizer)
- **MOD-04:** Phân hệ Ngân hàng Câu hỏi & Vòng đời Toàn diện (Item Bank Management & Full CRUD)
- **MOD-05:** Phân hệ Ma trận Đề thi & Rút đề theo Ràng buộc (Exam Matrix & Solver)
- **MOD-06:** Phân hệ Động cơ Trộn Mã đề An toàn (Safe Shuffling Engine)
- **MOD-07:** Phân hệ Xuất bản Đề thi Word OMML & In ấn (Publishing & Export Service)
- **MOD-08:** Phân hệ Chấm điểm Bậc thang & Quản lý Bảng điểm (Grade & Roster Management)
- **MOD-09:** Phân hệ Xác thực Người dùng & Quản lý Phân quyền (Authentication, JWT & RBAC)
- **MOD-10:** Phân hệ Soạn đề LaTeX Trực tiếp & Lưu đề vào Ngân hàng (Composer & Bank Deep Ingestion)

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

### 2.4.1. FR-02.3: Thanh Nhập Prompt AI Thu Gọn, Con Trỏ Soạn Thảo Toàn Chiều (Full-Height Caret), Hiệu Ứng Nổi Bật Khi Focus (:focus-within Glow) & Cơ Chế Xóa Sạch Lạc Quan
- **Vị trí & Kiểu dáng:**
  - Thanh dạng viên thuốc (floating pill bar) neo tại chân khung soạn thảo LaTeX (`bottom-7`, căn giữa theo chiều ngang `left-1/2 -translate-x-1/2`, chiều rộng `w-[92%] max-w-xl`).
  - Giao diện Apple Glassmorphism: Nền bán trong suốt `#1c1c1f/95`, hiệu ứng mờ hậu cảnh `backdrop-blur-md`, viền tinh tế `border-white/15`, đổ bóng sâu `shadow-2xl`.
- **Quy tắc Tương tác & Kích hoạt 2 Trạng Thái:**
  1. *Trạng thái Nhập liệu Cục bộ (In-place Text Input) & Hiển thị Full Con Trỏ (Full-Height Caret):*
     - Khi người dùng nhấp chuột vào thanh hoặc trường nhập `#composer-compact-input`, con trỏ chuột duy trì dạng `cursor-text` và trường nhập nhận focus bình thường.
     - **Quy tắc bất biến:** Việc nhấp chuột vào thanh hoặc trường nhập **tuyệt đối không tự động mở full popup trợ lý**. Giáo viên có thể thoải mái click để nhập, chỉnh sửa, dán (paste) nội dung yêu cầu mà không bị che khuất không gian làm việc.
     - **Hiển thị Full Con Trỏ Soạn Thảo (Anti-Caret-Clipping):** Khắc phục triệt để lỗi con trỏ soạn thảo (caret) bị ăn mất hoặc cụt ngủn khi click vào ô input. Định nghĩa chiều cao và giãn dòng tường minh (`font-size: 13px; line-height: 20px; height: 24px; padding: 1px 0; box-sizing: border-box; caret-color: #c084fc;`), bảo đảm caret hiển thị trọn vẹn 100% chiều cao con trỏ nhấp nháy, không bị clipping do container `overflow` hay co kéo `line-height`.
  2. *Hiệu Ứng Nổi Bật Box Chat Khi Được Select (:focus-within Apple Neon Glow):*
     - Khi bất kỳ thành phần nào trong `#composer-ai-compact-bar` nhận focus (đặc biệt là `#composer-compact-input:focus`), toàn bộ khung thanh bar được kích hoạt trạng thái nổi bật tức thì qua pseudo-class `:focus-within`:
       + **Viền phát sáng (Border Highlight):** Chuyển từ viền mờ `border-white/15` sang viền tím neon đậm đà `border-color: rgba(168, 85, 247, 0.75)` (Apple Purple).
       + **Vòng sáng tỏa (Focus Ring & Glow):** Áp dụng `box-shadow: 0 0 0 3.5px rgba(168, 85, 247, 0.28), 0 16px 40px -6px rgba(0, 0, 0, 0.9)`.
       + **Nền kính sâu hơn:** `background-color: rgba(28, 28, 32, 0.98)` tách biệt rõ rệt khỏi editor.
       + **Phản hồi xúc giác vi mô (Micro-interaction):** Nhấc nhẹ `transform: translate(-50%, -1px) scale(1.005)`.
       + **Icon Sparkles:** Sáng rực rỡ với `filter: drop-shadow(0 0 6px rgba(192, 132, 252, 0.65))` và nút gửi chuyển sang tím neon đồng bộ.
  3. *Trạng thái Kích hoạt Mở rộng & Gửi Lệnh (Expansion & Dispatch Trigger):*
     - Chỉ khi người dùng thực hiện một trong hai hành động sau thì hệ thống mới kích hoạt mở bung full giao diện Popup Trợ lý Soạn thảo (`composer-ai-popup`):
       - Nhấn phím **`Enter`** (bắt sự kiện `keydown` -> `handleCompactInputKey`).
       - Nhấp chuột vào **Nút Gửi Mũi Tên Tròn** (nút màu trắng nền tròn với icon `arrow-up` -> `submitFromCompact`).
     - Khi mở rộng:
       - Popup Trợ lý trượt mượt mà từ đáy khung soạn thảo lên chiếm `56%` chiều cao (có thể phóng to `78%` hoặc toàn màn hình `92%`).
       - Thanh Compact Bar tạm thời ẩn (`hidden`) để nhường chỗ cho giao diện chat chuyên sâu.
       - Dữ liệu text trong Compact Input được tự động chuyển tiếp vào ô chat chính và xóa trắng ô thu gọn.
       - Nếu có nội dung text, hệ thống tự động kích hoạt tiến trình gửi yêu cầu `sendPrompt(text)` đến Backend, chèn tin nhắn người dùng vào lịch sử và hiển thị bong bóng loading `Trợ lý đang xử lý yêu cầu...`.
  4. *Cơ Chế Xóa Sạch Lạc Quan (Optimistic Dual-Input Reset & Event Decoupling):*
     - **Khắc phục lỗi:** Triệt tiêu hoàn toàn hiện tượng text chat cũ còn lưu kẹt trong ô nhập chat của trợ lý sau khi đã gửi đi (Ảnh 1).
     - **Thực thi đồng bộ tại $t = 0\text{ms}$:** Ngay khi sự kiện gửi được kích hoạt (`submitChat`, `submitFromCompact`, hoặc `sendPrompt`), hệ thống lập tức gán `chatInput.value = ''` và `compactInput.value = ''` đồng thời, không đợi phản hồi mạng hoặc kết thúc hiệu ứng mở popup.
     - **Tách bạch ngữ nghĩa `openAIPopup`:** `submitFromCompact()` chỉ gọi `this.openAIPopup('')` với chuỗi rỗng; tuyệt đối không truyền lại prompt vào `prefillPrompt` (loại bỏ lỗi gán ngược nội dung đã gửi vào `chatInput.value`). `prefillPrompt` chỉ được sử dụng khi giáo viên chủ động bấm chọn mẫu lệnh nhanh (`applyQuickPrompt`) để biên tập trước khi gửi.
     - Con trỏ nhập liệu duy trì sẵn sàng ở đầu ô nhập trống với caret tím neon `#c084fc` hoặc xanh Apple `#38bdf8`, sẵn sàng cho lượt chat tiếp theo.
  5. *Menu Mẫu Câu Lệnh Nhanh (Quick Actions):*
     - Nút dấu cộng `+` bên cạnh nút gửi cho phép mở menu popover danh mục prompt tiêu chuẩn (Tạo Header chuẩn Quốc gia 2 cột & mã đề, Tạo khung 3 Phần đề thi chuẩn Bộ GD&ĐT 2025, Đổi cỡ chữ 12pt, Sinh trắc nghiệm 4 lựa chọn, Sinh Đúng/Sai QĐ 764, Vẽ bảng biến thiên `tkz-tab`, Sửa cú pháp LaTeX).
     - Khi chọn một mẫu, hệ thống tự động mở popup và điền sẵn prompt vào ô chat.
- **Quy chuẩn Màu Tương Phản Dark Mode (Sửa lỗi chữ đen trên nền tối):*
  - Khắc phục triệt để lỗi chữ màu đen `#1d1d1f` bị chìm trên nền tối `#1c1c1f` / `#141824`.
  - Thiết lập design tokens bắt buộc với độ ưu tiên cao (`!important`) cho cả 2 trường nhập liệu `#composer-compact-input` và `#composer-chat-input`:
    - *Text Color:* `#f8fafc` (Slate-50) hoặc `#ffffff` xuyên suốt mọi trạng thái (default, hover, focus, active).
    - *Placeholder Color:* `rgba(226, 232, 240, 0.5)` (Slate-200 / 50%) phân biệt rõ ràng nhưng dịu mắt trên nền tối.
    - *Caret Color (Con trỏ nhập liệu):* `#c084fc` (Purple-400) hoặc `#38bdf8` (Sky-400 / Apple Blue) định vị sắc nét vị trí con trỏ với chiều cao chuẩn 100%.
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

### 2.4.4. FR-02.6: Cơ Chế Chuyển Tiếp & Phân Tích Log Lỗi Biên Dịch LaTeX (Compile Error Forwarding & Line-Offset Diagnostics)
- **Mục tiêu:** Hỗ trợ giáo viên khắc phục lỗi cú pháp LaTeX / Tectonic tức thì mà không cần tự đọc log lỗi dòng lệnh phức tạp.
- **Luồng Dữ Liệu:**
  1. *Ghi nhận Lỗi Biên dịch:* Khi biên dịch `POST /api/v1/composer/compile` trả về lỗi (`success = false`), client tự động bắt lấy thông điệp lỗi `errMsg = data.error` và lưu trữ bền vững vào `app.composer.lastCompileError`.
  2. *Chuyển tiếp Tự động:* Khi người dùng gửi prompt kế tiếp (nhất là câu lệnh yêu cầu sửa lỗi như "sửa lỗi", "fix lỗi", "tại sao lỗi", hoặc nhấn nút SỬA LỖI), payload gửi đến `POST /api/v1/composer/chat` tự động đính kèm trường `compile_error: this.lastCompileError`.
  3. *Chẩn đoán & Sinh Diff Sửa Lỗi Phía Server:*
     - API `composer.py` trích xuất thông tin lỗi từ log (ví dụ: `error: document.tex:24: Undefined control sequence`, `! Missing $ inserted`, `l.24 ...`).
     - **Thuật toán ánh xạ dòng lỗi (Line-Offset Mapping):** Vì trình soạn thảo hoạt động ở chế độ Preamble-Free, hệ thống tự động tính dòng tương ứng trong editor `L_user = L_comp - 11` (với 11 dòng Canonical Preamble nhúng ngầm).
     - **Bộ Chẩn đoán Cục bộ 5 Nhóm Lỗi (Local Diagnostics Engine):**
       + *Nhóm 1 (No line here to end):* Phát hiện lỗi thừa `\\` sau các khối ngoặc nhọn `{...}` hoặc ở đầu dòng → Tự động xóa `\\`.
       + *Nhóm 2 (Undefined control sequence):* Tự động sửa các lệnh sai chính tả (`\ule` → `\rule`, `\choiceTFt` → `\choiceTF[1]`, `ight|` / `\night|` → `\right|`, `\fracc` → `\dfrac`, `\n` → xuống dòng thật).
       + *Nhóm 3 (Missing $ inserted):* Tự động bọc cặp dấu `$ ... $` quanh công thức toán học bị thiếu.
       + *Nhóm 4 (Missing \right. inserted):* Tự động hoàn thiện khối ngoặc co giãn `\left.` và `\right.`.
       + *Nhóm 5 (Environment undefined):* Tự động đề xuất bổ sung gói còn thiếu vào preamble.
     - AI Copilot tạo khối `diff` đề xuất phương án sửa: chỉ chứa dòng cũ và dòng mới để người dùng bấm **[Đồng ý]** là mã nguồn được cập nhật ngay lập tức.
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

### 2.4.12. FR-02.14: Động Cơ Thay Thế Câu Hỏi Thông Minh & Đồng Bộ Chat-Editor An Toàn (Question Replacement Engine & Safe Chat Sync)
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

### 2.4.13. FR-02.15: Phân Hệ Soạn Thảo Đề Thi Tinh Gọn Không Preamble & Động Cơ Nhúng Ngầm Canonical Preamble Injection (Preamble-Free Question Editor)
- **Mục tiêu:** Cung cấp trải nghiệm soạn thảo đề thi chuyên biệt, tối giản và thuận tiện nhất cho giáo viên. Người dùng chỉ cần soạn thảo nội dung đề thi và các câu hỏi chuẩn `ex_test.sty` (`\begin{ex}...\choice...\loigiai...\end{ex}`, `\choiceTF[1]`, `\shortans`, TikZ căn giữa, `tkz-tab`), hệ thống ngầm định tự động nhúng toàn bộ preamble chuẩn khảo thí quốc gia mà không yêu cầu người dùng phải gõ các lệnh `\documentclass`, `\usepackage`, hay `\begin{document}...\end{document}`. Mặc định toàn bộ đồ thị, hình học và bảng biến thiên đều được căn giữa, loại bỏ hoàn toàn `\immini` khỏi cấu trúc mặc định.
- **Quy tắc Kiến Trúc & Hành Vi:**
  1. *Định nghĩa Gói Lệnh Tiêu Chuẩn (Canonical Preamble Definition):*
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
     Trong đó `{mode}` được giải quyết động dựa trên cờ yêu cầu biên dịch:
     - `loigiai`: Hiển thị đầy đủ lời giải chi tiết và tô đậm/tô màu phương án đúng `\True`.
     - `dethi`: Ẩn toàn bộ lời giải và không đánh dấu đáp án đúng, tối ưu in đề cho học sinh.
  2. *Bộ Chuẩn Hóa Hai Chế Độ (Smart Dual-Mode Document Normalizer):*
     - **Chế độ Thân Câu Hỏi Thuần (Preamble-Free Question Body - Mặc định):**
       + Khi mã LaTeX nhận được không chứa chuỗi `\documentclass`:
       + Hệ thống tự động ghép: `CANONICAL_PREAMBLE.format(mode=mode) + "\n\\begin{document}\n" + body + "\n\\end{document}\n"`.
       + Tiến hành biên dịch thông qua Remote Tectonic API, Local Tectonic XeTeX, hoặc Headless Chromium Fallback.
     - **Chế độ Tài Liệu Đầy Đủ (Full Document - Tương Thích Ngược):**
       + Khi mã LaTeX nhận được đã chứa sẵn `\documentclass` (giáo viên dán toàn bộ file `.tex` hoàn chỉnh vào):
       + Hệ thống phát hiện và giữ nguyên cấu trúc, tự động thay thế `\usepackage{vietnam}` bằng `\usepackage{fontspec}`.
       + Đảm bảo các gói lệnh phụ thuộc của `ex_test` (`tcolorbox`, `xparse`, `tikz`, `tkz-tab`) được nạp trước `ex_test`.
       + Điều chỉnh option trên `\usepackage[...]{ex_test}` thành `[dethi]` hoặc `[loigiai]` theo cờ `mode` yêu cầu.
  3. *Hợp Đồng API Biên Dịch (`POST /api/v1/composer/compile`):*
     - Schema mở rộng:
       ```python
       class CompileRequest(BaseModel):
           latex_code: str = Field(..., description="Mã nguồn LaTeX (chỉ thân câu hỏi hoặc toàn bộ tài liệu)")
           title: str = Field("Đề Thi Soạn Thảo", description="Tiêu đề tài liệu")
           mode: Optional[str] = Field("loigiai", description="Chế độ xuất bản: 'loigiai' hoặc 'dethi'")
       ```
     - Cơ chế Khóa Cache: `code_hash = hashlib.md5(f"{clean_code}::{req.title}::{req.mode}".encode("utf-8")).hexdigest()`. Cho phép gạt chuyển đổi tức thì giữa đề thi và lời giải mà không bị đè cache.
  4. *Tương Tác Giao Diện Người Dùng (Frontend UI/UX):*
     - Vùng soạn thảo `#composer-editor-input`: Mặc định hiển thị mã đề thi mẫu sạch sẽ không preamble (bắt đầu bằng tiêu đề trường/kỳ thi và các khối `\begin{ex}`).
     - Huy hiệu Preamble ngầm: Hiển thị tooltip/indicator thông báo rõ ràng "Preamble tiêu chuẩn đã được nạp tự động (ex_test v3.3, tikz, tkz-tab, tcolorbox, A4)".
     - Nút công tắc `LỜI GIẢI` (`#composer-solution-toggle`):
       + Khi người dùng bật/tắt công tắc, hệ thống cập nhật trạng thái `this.showSolution` và xác định `mode = this.showSolution ? 'loigiai' : 'dethi'`.
       + Truyền `mode` trực tiếp vào payload gọi API `/composer/compile`.
       + Nếu người dùng sử dụng mã nguồn có sẵn `\usepackage[...]{ex_test}`, hệ thống vẫn đồng bộ cập nhật text trong editor; nếu là mã thuần không preamble, hệ thống giữ nguyên text của người dùng, không làm ô nhiễm mã nguồn.
     - Tác vụ `Tải mã nguồn TeX (.tex)`:
       + Khi người dùng chọn xuất file TeX, nếu mã nguồn đang ở dạng không preamble, hệ thống tự động bọc Canonical Preamble và `\begin{document}...\end{document}` trước khi tạo file tải xuống (`.tex`), đảm bảo giáo viên có thể mở và biên dịch độc lập ngay lập tức trên máy tính cá nhân.

### 2.4.14. FR-02.16: Cấu Trúc Header 2 Cột Căn Giữa (0.38/0.58), Section textbf/textit & Tự Động Nhận Diện Số Lượng Câu Hỏi Từng Phần
- **Mục tiêu Nghiệp vụ:** Cung cấp bộ khung cấu trúc đề thi chính thức chuẩn hóa theo mẫu mới nhất của Bộ Giáo dục & Đào tạo (Kỳ thi Tốt nghiệp THPT 2025). Tối ưu hóa tỷ lệ 2 cột minipage (0.38\textwidth bên trái và 0.58\textwidth bên phải, căn giữa `\centering` cả 2 bên), loại bỏ đường kẻ liền trên và chỉ giữ đường nét liền đơn dưới thông tin thí sinh. Loại bỏ hoàn toàn `\section*{...}`, thay thế bằng định dạng in đậm `\noindent\textbf{PHẦN ...}` và in nghiêng `\textit{...}`. Đồng thời tích hợp thuật toán đồng bộ hai tầng (Two-Tier Sync) tự động nhận diện số lượng câu hỏi và cập nhật câu hướng dẫn của từng phần.
- **Quy cách Chi tiết Cấu trúc Đề thi Chuẩn Quốc Gia 2025:**
  1. *Header 2 Cột Đối Xứng Minipage (Tỉ lệ 0.38/0.58, Căn Giữa Cả 2 Cột):*
     - Cột Trái (độ rộng `0.38\textwidth`, căn giữa nội dung):
       ```latex
       \noindent
       \begin{minipage}[t]{0.38\textwidth}
         \centering
         \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
         \textbf{TRƯỜNG THPT ...}\\
         \textbf{ĐỀ CHÍNH THỨC}
       \end{minipage}
       ```
     - Cột Phải (độ rộng `0.58\textwidth`, căn giữa nội dung):
       ```latex
       \hfill
       \begin{minipage}[t]{0.58\textwidth}
         \centering
         \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
         \textbf{MÔN: TOÁN}\\
         \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
       \end{minipage}
       ```
  2. *Hàng Thông Tin Thí Sinh & Khung Mã Đề (Chỉ Giữ Nét Liền Đơn Phía Dưới):*
     - Bỏ hoàn toàn đường nét liền `\rule{\textwidth}{0.5pt}` phía trên dòng thông tin thí sinh.
     - Duy trì khoảng đệm dọc `\vspace{0.25cm}`, dòng thông tin thí sinh kèm khung mã đề `\framebox`, khoảng đệm `\vspace{0.1cm}`, và đường nét liền đơn `\rule{\textwidth}{0.5pt}` phía dưới:
       ```latex
       \vspace{0.25cm}
       \noindent
       Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
       \vspace{0.1cm}
       \noindent\rule{\textwidth}{0.5pt}
       \vspace{0.3cm}
       ```
  3. *3 Phân Vùng Section Khảo Thí Chuẩn Bộ GD&ĐT 2025 (Thay \section* bằng \textbf + \textit):*
     - **PHẦN I (Trắc nghiệm nhiều lựa chọn):**
       ```latex
       \noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}
       ```
     - **PHẦN II (Trắc nghiệm Đúng/Sai 4 khẳng định theo QĐ 764):**
       ```latex
       \noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}
       ```
     - **PHẦN III (Trắc nghiệm trả lời ngắn):**
       ```latex
       \noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}
       ```
  4. *Thuật Toán Tự Động Nhận Diện Số Lượng Câu Hỏi Từng Phần (Two-Tier Dynamic Sync):*
     - **Backend Tier (`backend/services/composer_service.py`):**
       + Hàm `sync_section_question_counts(latex_code: str) -> str`:
         * Tìm vị trí bắt đầu các phần bằng regex: `(?:^|\n)\s*(?:\\noindent\s*)?(?:\\textbf\{|\\section\*?\{)?\s*PHẦN\s+(I{1,3}|IV|V|[1-9])\b` (cờ `re.IGNORECASE`).
         * Tách nội dung văn bản thành các block tương ứng với từng phần.
         * Đếm số câu hỏi trong từng phần:
           - Ưu tiên 1 (chuẩn gói `ex_test.sty`): `len(re.findall(r'\\begin\{(?:ex|bt|vd)\}', sec_content))`.
           - Ưu tiên 2 (cú pháp kinh điển): Loại bỏ chuỗi hướng dẫn (tránh đếm nhầm "câu 1" / "câu 12" trong "từ câu 1 đến câu X"), sau đó đếm `\textbf{Câu \d+}` hoặc các câu đặt ở đầu dòng `(?:^|\n)\s*(?:\\noindent\s*)?(?:Câu|Bài)\s*\d+[\.:]`.
         * Nếu `count > 0`: Thay thế mẫu `([Tt]ừ\s+câu\s+1\s+đến\s+câu\s+)\d+` thành `\g<1>{count}` (giới hạn `count=1` trên câu hướng dẫn).
         * Tích hợp tự động vào `ensure_full_latex_document`, endpoint `compile`, và các luồng export TeX.
     - **Frontend Tier (`frontend/static/app.js`):**
       + Hàm `syncSectionQuestionCounts(latexCode)`:
         * Ánh xạ chính xác giải thuật backend trên client bằng ES6 JavaScript.
         * Tự động đồng bộ nội dung trên ô soạn thảo `#composer-editor-input` khi người dùng bấm nút **BIÊN DỊCH** (`app.composer.compile(true)`), khi nhấn tổ hợp phím tắt `Ctrl+S` / `Cmd+S`, khi kết thúc thời gian debounce gõ phím (800ms), hoặc khi nhấn tải file TeX (`downloadTex`).
  5. *Tích Hợp Giao Diện Menu THÊM ▾ & Quick Actions:*
     - Giao diện dropdown `THÊM ▾` trên thanh công cụ cập nhật:
       + Nhóm *CẤU TRÚC ĐỀ THI QUỐC GIA 2025*: Header 2 Cột Căn Giữa (0.38/0.58), Phần I (Trắc nghiệm nhiều phương án - Tự động đếm), Phần II (Đúng/Sai QĐ 764 - Tự động đếm), Phần III (Trả lời ngắn - Tự động đếm), Trọn bộ Đề thi Quốc Gia.
       + Nhóm *MẪU LỆNH EX_TEST*: Trắc nghiệm, Đúng/Sai, Trả lời ngắn, Tự luận, Hình TikZ, Hình cạnh chữ, Lời giải.
     - Quick Action Menu (`#composer-compact-quick-menu`) và AI Prompt Handling (`system_prompt` và fallback) cập nhật cú pháp Header và Section mới.
  6. *Động Cơ Render HTML/PDF Hỗ Trợ Đầy Đủ Các Lệnh:*
     - Xử lý mượt mà trên cả Tectonic XeTeX engine lẫn Chromium HTML fallback:
       + Chuyển đổi `\begin{minipage}[t]{0.38\textwidth}` thành thẻ div inline-block có `width: 38.0%` và `text-align: center;`.
       + Chuyển đổi `\begin{minipage}[t]{0.58\textwidth}` thành thẻ div inline-block có `width: 58.0%` và `text-align: center;`.
       + Chuyển đổi `\noindent\textbf{...}` và `\textit{...}` thành `<strong>` và `<em>` tương ứng chuẩn HTML5.
       + Biên dịch `\rule{...}{...}` thành đường kẻ divider ngang (`<hr>`).
       + Biên dịch `\dotfill` thành đường kẻ chấm co giãn linh hoạt.
       - Biên dịch `\framebox` / `\fbox` thành thẻ viền chữ nhật bao quanh mã đề.

       ### 2.4.15. FR-02.17: Quy Chuẩn Mẫu Câu Hỏi Đúng/Sai \choiceTF[1] Dàn 1 Cột Thẳng Đứng & Rà Soát Toàn Diện Mẫu Lệnh Form Mẫu
       - **Mục tiêu Nghiệp vụ:** Loại bỏ hoàn toàn tình trạng các ý câu hỏi Đúng/Sai bị co cụm thành 2 cột hoặc 4 cột ngang; chuẩn hóa toàn diện 100% mẫu lệnh trong menu `THÊM ▾` và kho biểu mẫu hệ thống.
       - **Quy Cách Chi Tiết:**
       1. *Lệnh `\choiceTF[1]` Ép 1 Cột Thẳng Đứng:*
       - Khẳng định a), b), c), d) bắt buộc phải nằm trên 4 dòng riêng biệt dọc theo chiều đứng (mỗi ý 1 dòng, độ rộng 100%), không chia thành 2 cột hay 4 cột.
       - Tham số `[1]` trong `\choiceTF[1]` là bắt buộc đối với gói lệnh `ex_test.sty` v3.3 để kích hoạt `\extest@choiceFixedStart{1}`.
       - Tuyệt đối cấm sử dụng `\\` sau các dấu đóng ngoặc nhọn `{...}` (nguyên nhân gây lỗi TeX `There's no line here to end`).
       2. *Cấu Trúc Khảo Thí Chuẩn:*
       ```latex
       \begin{ex}
       Cho hàm số... Xét tính đúng/sai của các khẳng định sau:
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
       3. *Loại Bỏ Lỗi Escape Newline Chuỗi (`\n`) Trong Template Frontend:*
       - Sửa toàn bộ các mẫu `tracnghiem`, `dungsai`, `traloingan`, `tuluan`, `hinhtikz`, `hinhcanhchu`, `loigiai` trong `EX_TEST_TEMPLATES` từ chuỗi escape `\n` thành ký tự dòng mới thực tế trong template string JavaScript.
       - Sửa lỗi lệnh nội bộ `\choiceTFt` thành `\choiceTF[1]`.
       - Sửa macro `\loigiai{...}` thành môi trường chuẩn `\begin{loigiai} ... \end{loigiai}`.
       - Sửa lỗi gõ nhầm `\nule` thành `\rule{\textwidth}{0.5pt}` trong `dethi_quocgia_full`.
       4. *Đồng Bộ Bộ Render HTML Preview (`compile_latex_source_to_html`):*
       - Bộ render HTML nhận diện `\choiceTF[1]` (hoặc `\choiceTF`), bóc tách 4 đối số `{...}` và cờ `\True`.
       - Hiển thị thành 4 khối div dạng danh sách dọc (`width: 100%; display: block; margin-bottom: 4px;`) kèm nhãn a), b), c), d) và biểu tượng [Đ] / [S] chuẩn khảo thí.

       ### 2.4.16. FR-02.18: Trợ Lý AI Copilot Đa Phương Tiện: Đính Kèm, Dán Clipboard (Ctrl+V) & Kéo Thả Phân Tích Hình Ảnh (Multi-Modal Image Input & Visual Reasoning)
       - **Mô tả Chức năng:** Cung cấp trải nghiệm nhập liệu đa phương tiện toàn diện trong phân hệ Soạn đề (`/composer`). Giáo viên có thể gửi hình ảnh chụp đề thi, đồ thị hàm số, bảng biến thiên, hình học không gian hoặc bản nháp viết tay cho Trợ lý AI Copilot thông qua 3 phương thức: Nút đính kèm ảnh (Image picker), Dán ảnh từ bộ nhớ tạm (Clipboard Paste qua `Ctrl+V` / `Cmd+V`), hoặc Kéo thả trực tiếp tệp ảnh (Drag & Drop) vào vùng chat.
       - **Chi Tiết Giao Diện & Tương Tác Vi Mô (Apple HIG):**
         1. *Đính kèm từ Thanh Compact (#composer-ai-compact-bar):*
            - Bổ sung nút bấm icon ảnh `image` tinh tế.
            - Khi người dùng dán ảnh (`Ctrl+V`) trong lúc con trỏ ở `#composer-compact-input` hoặc chọn file ảnh qua nút: Giao diện tự động mở bung popup trợ lý lớn (`#composer-ai-popup`), chuyển con trỏ sang ô nhập chat lớn `#composer-chat-input`, đưa ảnh vào mảng `attachedImages` và hiển thị khay thumbnail.
         2. *Khay Thumbnail Đính Kèm (#composer-attached-images-container):*
            - Nằm bên trong `#composer-chat-input-container`, ngay phía trên textarea `#composer-chat-input`.
            - Hiển thị hàng ngang các thẻ thumbnail (54px x 54px, bo góc `rounded-xl`, viền mờ `border-white/15`, ảnh `object-cover`).
            - Nút xóa ảnh tròn 18px x 18px ở góc trên bên phải (✕): hover đỏ, phản hồi xúc giác co nhẹ `active:scale-90`.
            - Khi nhấp vào thumbnail (ngoài nút xóa): Kích hoạt Modal Phóng to Lightbox (`#composer-image-lightbox`) với nền tối mờ `backdrop-blur-sm`, phím `Esc` hoặc nhấp nền để đóng nhanh.
         3. *Thanh Công Cụ Chat Lớn (#composer-chat-input-container):*
            - Cạnh nút `+` (Quick Actions), bổ sung nút icon ảnh đính kèm kèm tooltip hướng dẫn.
            - Hỗ trợ sự kiện kéo thả tệp (`dragover`, `dragleave`, `drop`): Kích hoạt viền tím sáng `border-purple-500/80` và nền sáng tím nhẹ khi kéo tệp ảnh qua vùng nhập.
         4. *Bong Bóng Tin Nhắn Người Dùng (#composer-chat-messages):*
            - Render trực tiếp danh sách ảnh đính kèm bên trong bubble chat của user dạng thumbnail bo góc `rounded-lg`, nhấp để xem lightbox phóng to.
            - Lưu trữ mảng Base64 Data URL vào lịch sử phiên (`quesy_composer_chat_sessions`).
       - **Đặc Tả Hợp Đồng Backend & Xử Lý Đa Phương Tiện:**
         1. Bổ sung trường `images: Optional[List[str]] = Field(default_factory=list)` vào schema `ChatRequest` và `ChatMessage`.
         2. Khi gọi OpenAI/Gemini/OpenRouter: Tự động chuyển đổi payload thành cấu trúc message đa phương tiện: `[{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": data_url}}]`.
         3. System prompt chuyên sâu: Định hướng mô hình nhận diện đề bài, chuyển đổi công thức toán học chuẩn Thông tư 32, tái tạo đồ thị và hình học bằng mã TikZ, tái tạo bảng biến thiên bằng `tkz-tab`, bao bọc chuẩn `ex_test.sty`.
         4. Động cơ Local Fallback: Khi mất mạng hoặc không có API key ngoại vi, hệ thống nhận diện từ khóa (đồ thị, bảng biến thiên, tikz, giải bài) và trả về mã nguồn LaTeX/TikZ hoàn chỉnh phù hợp ngữ cảnh kèm diff để người dùng áp dụng trực tiếp.

       ### 2.4.17. FR-02.19: Cơ Chế Dynamic Adaptive Compilation Timeout Cho Đề Thi Quy Mô Lớn & Trợ Lý AI Chẩn Đoán Tối Ưu Hóa TikZ (Dynamic Adaptive Compilation Timeout & TikZ Optimization Copilot)
       - **Mô tả Chức năng:** Nâng cấp động cơ biên dịch LaTeX Hybrid và Trợ lý AI Copilot của phân hệ Soạn đề (`/composer`) nhằm xử lý triệt để các sự cố quá thời gian biên dịch (Compilation timed out) khi soạn thảo các đề thi chuẩn Quốc gia quy mô lớn (ví dụ: Đề thi THPT Việt Đức 2026-2027 với ~24.000 ký tự, 12 câu trắc nghiệm đơn, 4 câu đúng/sai QĐ 764, 6 câu trả lời ngắn, chứa hơn 10 hình TikZ/tkz-tab và đồ thị phân thức/bậc ba nhiều nhánh có tham số `samples=100`).
       - **Đặc Tả Thuật Toán Tính Timeout Động Phích Thích Ứng (Dynamic Adaptive Compilation Timeout):**
         1. *Định tuyến & Bóc tách Độ phức tạp:*
            - Hàm phụ trợ `compute_compilation_timeout(latex_source: str) -> int` được gọi trước khi dispatch payload sang Docker microservice hoặc Local Tectonic subprocess.
            - `tikz_count = len(re.findall(r'\\begin\{(?:tikzpicture|tkzTab)\}|\\tkzTabInit', latex_source, re.IGNORECASE))`
            - `code_len = len(latex_source)`
            - Công thức chuẩn hóa:
              $$\text{calc\_timeout} = \max\left(60, \min\left(240, 45 + 10 \times \text{tikz\_count} + \left\lfloor \frac{\text{code\_len}}{250} 
ight
floor 
ight)
ight)$$
         2. *Truyền nhận Endpoint & Thiết Lập Socket Mạng:*
            - Trong `compile_with_remote_tectonic_api`: Đóng gói `payload = json.dumps({"latex_code": sanitized_latex, "timeout_s": calc_timeout}).encode("utf-8")`.
            - Thiết lập `urllib.request.urlopen(req, timeout=calc_timeout + 15)` bảo đảm socket client không ngắt trước container khi xử lý các đề thi nặng.
            - Trong `compile_with_tectonic`: Gán `subprocess.run(cmd, ..., timeout=calc_timeout)` và bắt ngoại lệ `subprocess.TimeoutExpired` trả về thông báo lỗi rõ ràng.
       - **Đặc Tả Chẩn Đoán Lỗi Timeout & Đề Xuất Diff Tối Ưu Hóa TikZ (AI Copilot):**
         1. *Phát hiện Lỗi Timeout:*
            - Trong `diagnose_compile_error`, khi `compile_error` chứa các cụm từ `"compilation timed out"`, `"timed out"`, hoặc `"quá thời gian cho phép"`.
         2. *Phản Hồi & Hướng Dẫn:*
            - Giải thích nguyên nhân gốc rễ: Đề thi lớn chứa nhiều khối TikZ phức tạp với tham số mật độ điểm mẫu cao `samples=100`.
            - Thông báo hệ thống đã tự động gia hạn thời gian biên dịch tối đa lên tới $\text{calc\_timeout}$ giây (tối đa 240s).
            - Gợi ý tối ưu hóa: Đề xuất chuyển `samples=100` xuống `samples=50` (hoặc `samples=60`). Giải thích rõ đường cong vector A4 chỉ cần 50 điểm Bézier là đạt độ trơn mịn hoàn hảo, giảm 50% thời gian tính toán toạ độ của XeTeX.
         3. *Trích Xuất DiffSuggestion:*
            - Quét tìm tất cả các dòng chứa `samples=100` (hoặc `samples=\d+` với giá trị $\ge 80$).
            - Sinh danh sách `diffs: List[DiffSuggestion]` thay thế tương ứng bằng `samples=50`, kèm `diff = diffs[0]` để người dùng thao tác duyệt từng diff hoặc click [Áp dụng tất cả] trên thanh công cụ editor.
       - **Đặc Tả Trải Nghiệm Giao Diện Người Dùng (Frontend UX):**
         1. Khi bấm `Biên dịch` (`compile()` trong `app.js`):
            - Nếu phát hiện đề thi lớn (`this.currentLatex.length > 10000 || tikzCount >= 4`), nhãn `#composer-status-text` hiển thị: `"Đang biên dịch đề thi lớn (nhiều hình TikZ)..."`.
            - Bật Progressive Status Timer (5s: *"Đang xử lý hình vẽ TikZ & tính toán toạ độ..."*; 15s: *"Đang kết xuất các trang PDF vector qua XeTeX..."*; 35s: *"Đang hoàn tất biên dịch đề thi quy mô lớn..."*), triệt tiêu cảm giác treo màn hình.
            - Hủy timer dọn dẹp sạch sẽ trong khối `finally`.

       ### 2.4.18. FR-02.20: Cơ Chế Chống Nhân Đôi Ảnh Đính Kèm Khi Dán Clipboard (Clipboard Paste Deduplication & Event Isolation)
       - **Mô tả Chức năng:** Khắc phục triệt để hiện tượng khi người dùng nhấn `Ctrl+V` (hoặc `Cmd+V`) để dán ảnh chụp vào ô nhập liệu (`#composer-chat-input`), một ảnh bị nhân đôi thành hai ảnh đính kèm trên khay thumbnail (`#composer-attached-images-container`) và hiển thị hai lần thông báo toast.
       - **Nguyên nhân Kỹ thuật:** Ô nhập liệu `#composer-chat-input` nằm lồng bên trong container `#composer-chat-input-container`. Cả hai phần tử đều được đăng ký listener cho sự kiện `paste`. Khi người dùng dán ảnh, sự kiện kích hoạt trên `#composer-chat-input`, tuy đã gọi `e.preventDefault()` để cản dán chuỗi thô nhưng thiếu `e.stopPropagation()`, dẫn đến sự kiện tiếp tục nổi bọt (event bubbling) lên container cha. Container cha tiếp tục xử lý và đọc lại cùng một tệp từ clipboard, kích hoạt hàm `addAttachedImage` lần thứ hai liên tiếp.
       - **Đặc Tả Kỹ Thuật & Giải Pháp Đa Tầng (Multi-layer Defense):**
         1. *Cô lập Sự kiện (Event Propagation Isolation):*
            - Trong listener của sự kiện `paste` tại `setupPasteAndDropListeners()`, khi phát hiện mục `item.type.startsWith('image/')`:
              Bắt buộc gọi đồng thời cả hai lệnh:
              ```javascript
              e.preventDefault();
              e.stopPropagation();
              ```
            - Tách biệt rõ ràng đối tượng lắng nghe: Không gán sự kiện `paste` thừa thãi trên container nếu các phần tử con nhập liệu bên trong đã được gán trực tiếp.
         2. *Cờ Khởi Tạo Đơn Lần (Idempotent Listener Binding Guard):*
            - Trang bị cờ bảo vệ `this._pasteListenersBound = true` tại `setupPasteAndDropListeners()`. Nếu hàm bị gọi lại do chuyển đổi view hoặc khởi tạo lại component, listener sẽ không bị gán lặp thêm lần nào nữa.
         3. *Cơ Chế Khử Trùng Lặp & Giảm Tải (Debounce & Content Deduplication):*
            - Trong hàm `addAttachedImage(dataUrl, name)`:
              * Tạo chữ ký ảnh ngắn gọn: `imgSig = dataUrl.slice(0, 120) + '_' + dataUrl.length`.
              * Nếu chữ ký trùng với chữ ký của ảnh vừa thêm trong vòng 500ms (`Date.now() - this._lastPastedTime < 500`), lập tức bỏ qua (silent return), không thêm vào mảng và không bắn toast kép.
              * Kiểm tra mảng hiện tại: Nếu `this.attachedImages.some(img => img.dataUrl === dataUrl)`, từ chối thêm trùng.

       ### 2.4.19. FR-02.21: Chuẩn Hóa Cấu Trúc Khảo Thí Quốc Gia 2025: Reset Thứ Tự Câu Hỏi Về 1 Ở Mỗi Phần (\setcounter{ex}{0}) & Loại Bỏ Triệt Để Thẻ \large Ở Tiêu Đề Phần
       - **Mô tả Chức năng:** Đảm bảo toàn bộ tài liệu đề thi môn Toán và KHTN được soạn thảo trên Quesy Composer tuân thủ 100% quy chuẩn đề thi tốt nghiệp THPT theo Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT:
         1. *Đánh số câu hỏi từng phần:* PHẦN I gồm 12 câu (Câu 1 đến Câu 12); PHẦN II (Đúng/Sai) bắt đầu lại từ Câu 1 đến Câu 4; PHẦN III (Trả lời ngắn) bắt đầu lại từ Câu 1 đến Câu 6.
         2. *Chuẩn hóa Typography tiêu đề phần:* Loại bỏ hoàn toàn cỡ chữ `\large`, `\Large` gây giãn nở khoảng cách dọc bất thường và làm vỡ tỷ lệ trang in chuẩn A4.
       - **Đặc Tả Kỹ Thuật Lệnh Reset Bộ Đếm Câu Hỏi (\setcounter{ex}{0}):**
         1. Trong gói lệnh chuẩn `ex_test.sty` (v3.3), môi trường câu hỏi `\begin{ex}` được định nghĩa qua `\newtheorem{ex}{\nameex}` với counter nội tại là `ex`.
         2. Khi hết PHẦN I, nếu không có lệnh can thiệp, counter `ex` sẽ tiếp tục đếm lên 13, 14... Lệnh chuẩn xác theo TeX/LaTeX để đưa số thứ tự câu hỏi về 1 là:
            ```latex
            \setcounter{ex}{0}
            ```
            (Khi gặp `\begin{ex}` đầu tiên của phần mới, counter `ex` tăng từ 0 lên 1 và hiển thị chuẩn xác **"Câu 1."**).
         3. *Tự động chèn & bảo toàn (Automatic Injection & Enforcement):*
            - Hàm `ensure_full_latex_document` và `sync_section_question_counts` trong `composer_service.py` tự động quét các ranh giới phần (`PHẦN II`, `PHẦN III`, `PHẦN IV`...). Nếu sau tiêu đề phần chưa có lệnh `\setcounter{ex}{0}`, hệ thống tự động chèn ngay sau dòng tiêu đề / hướng dẫn `\textit{...}`.
            - Đồng bộ hóa trong bộ phân giải HTML Preview (`compile_latex_source_to_html`): Khi gặp tiêu đề phần mới, reset biến đếm câu hỏi hiển thị về 1.
            - Cập nhật 100% các mẫu đề thi (`TEMPLATES` ở backend, `EX_TEST_TEMPLATES` ở frontend, snippets và các mẫu fallback của AI Copilot).
       - **Đặc Tả Chuẩn Hóa Tiêu Đề Phần (Stripping \large):**
         1. Cú pháp chuẩn duy nhất được phép sử dụng cho tiêu đề phân đoạn đề thi:
            ```latex
            \noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}
            \noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}
            \setcounter{ex}{0}
            \noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}
            \setcounter{ex}{0}
            ```
         2. Bộ lọc tiền xử lý tự động bóc tách và loại bỏ mọi thẻ `\large`, `\Large`, `\LARGE` bên trong hoặc bao quanh tiêu đề phần (`\textbf{\large PHẦN...}`, `{\large\textbf{PHẦN...}}`, `\large\textbf{PHẦN...}`, `\section*{\large PHẦN...}`).
         3. `system_prompt` của AI Copilot nghiêm cấm tuyệt đối việc sử dụng `\large` trong tiêu đề phần.

       ### 2.4.20. FR-02.22: Kiến Trúc Biên Dịch Nhanh Đa Tầng Cho Soạn Thảo Đề Thi (Multi-tier Fast & Incremental Compilation: Focus Mode, Instant Preview & Draft Mode)
       - **Mô tả Chức năng:** Giải quyết triệt để vấn đề thời gian phản hồi khi giáo viên chỉnh sửa mã nguồn LaTeX trên giao diện Soạn đề (`/composer`). Thay vì mỗi lần sửa đổi dù nhỏ (đổi 1 chữ, sửa 1 số, đổi phương án) đều phải chờ 40s - 65s để XeTeX/Tectonic biên dịch lại toàn bộ 22 câu và 10 hình vẽ TikZ, hệ thống cung cấp giải pháp tăng tốc đa tầng linh hoạt:
       - **Chi Tiết Kiến Trúc 3 Tầng Tăng Tốc:**
         1. *Tầng 1: Chế độ Xem trước Tức thì HTML/SVG (Instant Live Preview - Phản hồi 0.2s):*
            - Khi người dùng đang nhập liệu hoặc chỉnh sửa mã câu hỏi, thay vì gọi tiến trình XeTeX nặng nề, hệ thống tự động kích hoạt bộ chuyển đổi tức thì `compile_latex_source_to_html`:
              * Công thức toán được kết xuất trực tiếp bằng MathJax/KaTeX trong 50ms.
              * Các đồ thị TikZ đã được lưu vào bộ nhớ đệm Disk Cache (khóa MD5 mã TikZ) từ các lượt trước được tải lại ngay lập tức trong 10ms mà không cần vẽ lại; chỉ duy nhất hình vẽ đang bị chỉnh sửa mới phải gọi `render_tikz_to_svg` (0.8s).
              * Kết quả hiển thị mượt mà trên khung xem trước, cho phép giáo viên kiểm tra ngay nội dung vừa gõ với độ trễ gần như bằng 0.
            - Giao diện trang bị nút công tắc chuyển đổi: `[Xem trước Tức thì (0.2s)]` và `[Xuất bản PDF (XeTeX)]`.
         2. *Tầng 2: Tính năng Biên dịch Nhanh Câu Đang Sửa / Phân Đoạn (Focus / Partial Question Quick Compile - Phản hồi 1.5s):*
            - **Khái niệm:** Cho phép giáo viên biên dịch riêng câu hỏi hoặc phân đoạn đang tập trung chỉnh sửa thành định dạng PDF vector chuẩn xác để xem trước ngay lập tức mà không phải chờ các câu hỏi khác.
            - **Cơ chế Hoạt động:**
              * Client tự động phát hiện vị trí con trỏ trong ô soạn thảo (`findCurrentQuestionAtCursor`) hoặc nhận diện đoạn văn bản đang được người dùng bôi đen (selection).
              * Tách riêng khối câu hỏi đó (`\begin{ex} ... \end{ex}`) và bọc nhanh vào Canonical Preamble tiêu chuẩn.
              * Gửi yêu cầu biên dịch tới API `POST /api/v1/composer/compile` với cờ `focus_mode: true` (hoặc bọc sẵn câu hỏi độc lập).
              * XeTeX/Tectonic chỉ biên dịch duy nhất 1 câu hỏi (kèm tối đa 1 hình vẽ TikZ của câu đó) -> Hoàn tất trong **1.0 đến 1.8 giây**!
              * Kết quả PDF được hiển thị ngay trên khung xem trước với nhãn chỉ báo thời gian trực quan.
            - **Phím tắt & Nút bấm:** Nút tia chớp `⚡ BIÊN DỊCH CÂU NÀY` cạnh nút BIÊN DỊCH, phím tắt `Ctrl+Shift+S` (hoặc `Cmd+Shift+S`).
         3. *Tầng 3: Chế độ Biên dịch Nhanh Nháp (Draft / Fast Compile Mode - Giảm 70% thời gian biên dịch toàn đề):*
            - Khi người dùng bật tùy chọn **`Chế độ Nháp (Draft Mode)`**:
              * Backend tự động tiền xử lý mã nguồn: Thay thế tham số `samples` của tất cả các lệnh vẽ đồ thị TikZ (`plot (...)`) xuống mức an toàn `samples=35` (thay vì 80 - 100).
              * Bỏ qua các lượt biên dịch pass thứ 2/thứ 3 không bắt buộc khi tài liệu không dùng tham chiếu chéo `\pageref`.
              * Thời gian biên dịch toàn bộ đề thi 22 câu giảm mạnh từ 65s xuống chỉ còn **12 - 18 giây**, đẩy nhanh đáng kể chu kỳ rà soát đề thi trước khi xuất bản bản in chính thức.

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

### 2.8.1. FR-04.3: Hệ Thống Thao Tác CRUD Hoàn Chỉnh & Modals Chuẩn Apple HIG
Hệ thống cung cấp trọn vẹn 4 thao tác CRUD trên giao diện web `/bank`:
1. **Thêm mới câu hỏi (+ Thêm câu hỏi thủ công - `#question-create-modal`):**
   - Hỗ trợ đầy đủ 3 thể thức QĐ 764:
     + *Trắc nghiệm đơn (SINGLE_CHOICE):* 4 phương án A, B, C, D; chọn 1 đáp án đúng (radio); cờ khóa neo phương án D (`is_fixed`).
     + *Đúng / Sai 4 khẳng định (TRUE_FALSE_GROUP):* 4 khẳng định a, b, c, d độc lập; mỗi khẳng định có switch chọn ĐÚNG / SAI và ô nhập lời giải con.
     + *Trả lời ngắn (SHORT_ANSWER):* Ô nhập kết quả đúng (số hoặc chuỗi) và dung sai tính toán $\pm \epsilon$.
   - Tích hợp thanh công cụ chèn nhanh ký hiệu toán học (`\dfrac{a}{b}`, `\sqrt{x}`, `\overrightarrow{u}`, TikZ BBT tkz-tab, đồ thị).
   - Vùng xem trước KaTeX Live Preview thời gian thực cho thân câu hỏi và lời giải.
   - Nút `🔍 Kiểm tra Trùng lặp AI`: So khớp tức thì với CSDL qua `POST /api/v1/questions/check-duplicate`.
   - Nút `✨ Gợi ý YCCĐ bằng AI`: Tự động nhận diện môn, lớp, đề xuất mã YCCĐ qua `POST /api/v1/questions/auto-tag`.
   - Gửi request `POST /api/v1/questions` để lưu vào CSDL; tự động làm mới danh sách và cập nhật badge số lượng.
2. **Xem chi tiết câu hỏi (`#question-detail-modal`):**
   - Mở khi người dùng click vào thẻ câu hỏi hoặc nút "Xem chi tiết".
   - Hiển thị đầy đủ công thức toán KaTeX chất lượng cao, đồ thị TikZ SVG độc lập, bảng biến thiên chuẩn xác.
   - Thể hiện barem tính điểm bậc thang chi tiết theo Quyết định 764/QĐ-BGDĐT.
   - Cây phân cấp chuẩn 6 tầng (Lớp, Môn, Mạch, Chủ đề, Bài học, Mã YCCĐ) và chỉ số khảo thí $p, D$.
   - Nút chuyển tiếp nhanh sang chế độ Chỉnh sửa hoặc Xóa.
3. **Chỉnh sửa câu hỏi (`#question-edit-modal`):**
   - Điền sẵn toàn bộ dữ liệu hiện tại của câu hỏi.
   - Cho phép cập nhật linh hoạt nội dung stem, phương án, khẳng định con, đáp án ngắn, YCCĐ, mức độ nhận thức, lời giải chi tiết.
   - Gửi request `PUT /api/v1/questions/{id}` cập nhật nguyên tử vào CSDL.
4. **Xóa câu hỏi (`#question-delete-modal`):**
   - Hộp thoại cảnh báo xác nhận xóa rõ ràng, phòng ngừa thao tác nhầm lẫn.
   - Gửi request `DELETE /api/v1/questions/{id}`, xóa triệt để cascade trong bảng `question_options` và `sub_statements`.
   - Cập nhật tức thì giao diện loại bỏ câu hỏi khỏi danh sách, tự động giảm số lượng trên `#bank-count-badge`.

### 2.8.2. FR-04.4: Bộ Lọc Cây Kiến Thức 6 Tầng Cascading & Bộ Lọc Thứ Cấp
1. **Bộ Lọc Cây Kiến Thức 6 Tầng Chuẩn Thông tư 32/2018/TT-BGDĐT:**
   - 6 dropdown xếp tầng đồng bộ động (cascading):
     + *Tầng 1 (Grade):* Lớp 10, Lớp 11, Lớp 12.
     + *Tầng 2 (Subject):* Toán học, Vật lí, Hóa học, Sinh học...
     + *Tầng 3 (Strand):* Mạch nội dung theo TT 32 (ví dụ: Số & Đại số, Hình học & Đo lường, Thống kê & Xác suất, Thực hành trải nghiệm).
     + *Tầng 4 (Topic):* Chủ đề / Chuyên đề học tập.
     + *Tầng 5 (Lesson):* Bài học cụ thể.
     + *Tầng 6 (Learning Outcome):* Mã YCCĐ chuẩn quốc gia (e.g. `TOAN12.GT.01`).
   - Tuyệt đối không phân chia theo bất kỳ bộ sách giáo khoa thương mại nào.
2. **Bộ Lọc Thứ Cấp Đa Chiều:**
   - Dạng câu hỏi (Problem Archetype).
   - Mức độ nhận thức: Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao.
   - Thể thức câu hỏi: Trắc nghiệm đơn, Đúng/Sai 4 ý, Trả lời ngắn.
   - Tìm kiếm từ khóa: Nhập từ khóa văn bản hoặc công thức toán học với cơ chế tìm kiếm thời gian thực debounce 300ms.

### 2.8.3. FR-04.5: Xuất Bản Danh Sách Câu Hỏi Ngân Hàng (Vector PDF, CSV UTF-8 BOM, LaTeX)
- **Endpoint:** `POST /api/v1/questions/export` (hoặc `GET /api/v1/questions/export`)
- **Tham số:** `format: "pdf" | "csv" | "latex"`, `question_ids: Optional[List[str]]`, tiêu chí lọc (môn, lớp, YCCĐ, mức độ).
- **Định dạng kết xuất:**
  1. *PDF Vector In ấn (`format="pdf"`):* Khổ A4 dọc, lề 1.5 cm, font chữ Times New Roman / CMU Serif, hiển thị sắc nét công thức toán và đồ thị vector TikZ, đi kèm barem đáp án và hướng dẫn giải.
  2. *CSV UTF-8 BOM (`format="csv"`):* Bắt buộc ghi ký tự đánh dấu Byte Order Mark (`\ufeff`) ở đầu luồng dữ liệu, bảo đảm mở trực tiếp trên Microsoft Excel tiếng Việt không bao giờ bị lỗi font mojibake.
  3. *LaTeX thuần (`format="latex"`):* Tệp `.tex` chuẩn gói lệnh `ex_test.sty` với các khối `\begin{ex}` sẵn sàng biên dịch trực tiếp bằng Tectonic XeTeX.

### 2.8.4. FR-04.6: Nhập Câu Hỏi Hàng Loạt Vào Ngân Hàng
- **Endpoint:** `POST /api/v1/questions/import`
- **Phương thức nhập:**
  1. *Tải lên tệp:* Tệp văn bản `.tex`, `.json`, hoặc `.csv`.
  2. *Dán trực tiếp văn bản:* Dán đoạn mã đề thi LaTeX chứa các câu hỏi `\begin{ex}` hoặc `\textbf{Câu X.}`.
- **Xử lý:**
  - Hệ thống tự động bóc tách các câu hỏi thành danh sách cấu trúc Question/Option/SubStatement.
  - Tự động gọi `suggest_auto_tagging` gán nhãn môn, lớp và YCCĐ nếu thiếu.
  - Kiểm tra phát hiện trùng lặp AI và trả về kết quả số lượng câu nạp thành công.

### 2.8.5. FR-04.7: Đồng Bộ Huy Hiệu Số Lượng Ngân Hàng (#bank-count-badge) & Lưu Trữ Bền Vững SQLite 100%
- **Lưu Trữ Thực Tế & Bền Vững 100% CSDL SQLite:**
  * Toàn bộ câu hỏi được lưu trữ trong CSDL SQLite `storage/quesy.db` (230+ câu hỏi chuẩn hóa).
  * Khi tải ứng dụng hoặc F5, client thực hiện `fetchQuestionsFromDB()` với `limit=1000` nạp trọn vẹn dữ liệu từ SQLite vào `state.itemBank`.
  * Tuyệt đối không gọi `seedInitialQuestions()` làm mất dữ liệu SQLite sau khi fetch. Dữ liệu tĩnh chỉ dùng khi CSDL hoàn toàn rỗng hoặc offline.
- **Đồng Bộ Badge Thời Gian Thực:**
  * Badge hiển thị số lượng câu hỏi trên thanh điều hướng (`#bank-count-badge`) và bộ đếm trong Dashboard phản ánh chính xác số lượng câu hỏi thực tế trong CSDL SQLite.
  * Tự động kích hoạt truy vấn `GET /api/v1/questions` và cập nhật số hiển thị sau mỗi thao tác: Thêm mới câu hỏi, Chỉnh sửa, Xóa, Nhập tệp, hoặc Lưu đề từ Composer.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-05: MA TRẬN ĐỀ THI & BẢN ĐẶC TẢ KHẢO THÍ (EXAM MATRIX BUILDER)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.9. FR-05.1: Thiết lập Bản Đặc tả Ma trận Đề thi theo YCCĐ & Thư viện Presets
- **Màn hình:** `SCR-MATRIX-BUILDER` (Route: `/matrix`, tab: `#tab-matrix`)
- **Căn cứ pháp lý:** Thông tư 22/2021/TT-BGDĐT và Định dạng đề thi 2025 (Quyết định 764/QĐ-BGDĐT).
- **Thông số chung:** Tên kỳ thi, Khối lớp & Môn học, Thời gian làm bài (45, 50, 90 phút), Thang điểm tổng (10.0đ).
- **Thư viện Ma trận Mẫu (Exam Matrix Presets):**
  1. *Preset 1 - Chuẩn Tốt nghiệp THPT 2025 (34 câu, 10.0đ, 90 phút):*
     - Phần I: 12 câu trắc nghiệm đơn $\times$ 0.25đ = 3.0đ.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0đ (áp dụng barem lũy tiến QĐ 764).
     - Phần III: 6 câu Trả lời ngắn $\times$ 0.5đ = 3.0đ.
     - Tỷ lệ phân bổ chuẩn: 40% Biết (3.0đ) - 30% Hiểu (3.5đ) - 30% Vận dụng (3.5đ).
  2. *Preset 2 - Kiểm tra Định kỳ / Giữa kỳ (20 câu, 10.0đ, 50-60 phút):*
     - Phần I: 12 câu trắc nghiệm đơn $\times$ 0.25đ = 3.0đ.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0đ.
     - Phần III: 4 câu Trả lời ngắn $\times$ 0.75đ = 3.0đ.
     - Tỷ lệ phân bổ: ~50% Biết, 30% Hiểu, 20% Vận dụng.
  3. *Preset 3 - Kiểm tra Cuối kỳ (28 câu, 10.0đ, 90 phút):*
     - Phần I: 16 câu trắc nghiệm đơn $\times$ 0.25đ = 4.0đ.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0đ.
     - Phần III: 8 câu Trả lời ngắn $\times$ 0.25đ = 2.0đ.
     - Tỷ lệ phân bổ: 40% Biết, 35% Hiểu, 25% Vận dụng.
- **Lưới Ma trận 2D Tương tác & Quản lý Dòng động (Interactive 2D Matrix Grid & Dynamic Rows):**
  - Trục dọc: Phân cấp theo Mạch nội dung -> Yêu cầu cần đạt (YCCĐ) -> Dạng câu hỏi (Problem Archetype) -> Thể thức câu hỏi (`SINGLE_CHOICE`, `TRUE_FALSE_GROUP`, `SHORT_ANSWER`).
  - Trục ngang: 3 Cột nhận thức: Biết (Nhận biết), Hiểu (Thông hiểu), Vận dụng.
  - **Quản lý Dòng động (Dynamic Rows):** Nút `+ Thêm dòng YCCĐ vào Ma trận` cho phép bổ sung hàng mới từ danh mục YCCĐ; nút xóa dòng (`trash-2`) trên mỗi hàng hỗ trợ xóa nhanh.
  - **Tính toán Điểm số Thời gian thực (Zero Hardcoded Scoring):**
    * Điểm số từng dòng tính toán thực tế: `rowPoints = (biet * p_biet + hieu * p_hieu + vandung * p_vandung)`.
    * Điểm toàn ma trận = tổng điểm các dòng; tổng số câu = tổng số câu các dòng (tuyệt đối không hardcode '10.0đ').
  - **Thanh tiến trình phân bổ Bloom Thời gian thực:** Tự động tính toán `% Biết`, `% Hiểu`, `% Vận dụng` từ số lượng câu thực tế (không hardcode tỷ lệ cố định), hiển thị nhãn cảnh báo trực quan: Đạt chuẩn khảo thí khi tỷ lệ tiệm cận chuẩn của từng preset (dung sai $\pm 5\%$).
- **Đối soát Tồn kho Câu hỏi Thời gian thực (Live Inventory Checker):**
  - Kết nối trực tiếp cơ sở dữ liệu Question Bank thông qua API kiểm tra tồn kho hoặc đối soát trực tiếp `state.itemBank`.
  - Từng ô ma trận hiển thị trạng thái tồn kho thực tế qua chip trực quan:
    * *Đủ câu:* Chip xanh lá `bg-emerald-50 text-emerald-700 border-emerald-200`, ví dụ: `Kho: 15 / Cần: 5`.
    * *Cảnh báo thiếu câu:* Chip đỏ `bg-rose-50 text-rose-700 border-rose-200 font-bold`, ví dụ: `Kho: 2 / Cần: 5 (Thiếu 3 câu)` kèm icon cảnh báo.
  - Cảnh báo toàn ma trận: Hiển thị tổng số câu thiếu và danh sách các ô thiếu câu trước khi sinh đề.
- **API Hợp đồng Ma trận Đề thi:**
  - `POST /api/v1/matrix` (alias `/api/v1/matrices`): Lưu và ban hành ma trận đề thi.
  - `GET /api/v1/matrix` (alias `/api/v1/matrices`): Danh sách ma trận.
  - `GET /api/v1/matrix/{id}` (alias `/api/v1/matrices/{id}`): Chi tiết ma trận.
  - `POST /api/v1/matrix/{id}/check-availability` & `POST /api/v1/matrix/check-availability`: Kiểm tra tồn kho câu hỏi.
  - `GET /api/v1/matrix/{id}/spec` (alias `/api/v1/matrices/{id}/spec`): Xuất bản bản đặc tả ma trận đề thi:
    * `format=json`: Trả về JSON bản đặc tả chi tiết.
    * `format=csv`: File CSV mã hóa UTF-8 BOM (`\ufeff`) tương thích 100% Microsoft Excel tiếng Việt.
    * `format=pdf`: File Vector PDF A4 Portrait gồm Khung ma trận 2D và Bảng đặc tả chi tiết.
- **Nút Hành động "Khởi Tạo Đề Thi Gốc & Sang Trộn Đề":**
  - Tự động lưu cấu hình ma trận hiện tại, gọi API `POST /api/v1/exams/generate` và chuyển người dùng sang tab Trộn đề (`#tab-shuffler`).

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-06: ĐỘNG CƠ SINH ĐỀ & TRỘN MÃ ĐỀ AN TOÀN (SHUFFLING ENGINE)        │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.10. FR-06.1: Đề Thi Gốc (Master Exam), Thanh Nguồn Đề Gốc & Đổi Câu Tương Đương (In-Place Item Swap)
- **Màn hình:** `SCR-SHUFFLER` (Route: `/shuffler`, tab: `#tab-shuffler` - Bước 1)
- **Thanh Nguồn Đề Thi Gốc & Nhập từ Ma Trận (Master Exam Source Toolbar):**
  * Tích hợp thanh công cụ trực quan phía trên danh sách câu hỏi:
    + *Menu Chọn Đề Gốc Đã Lưu:* Thẻ `<select id="shuffler-select-master-exam">` nạp danh sách đề thi gốc có sẵn từ API `GET /api/v1/exams`. Khi chuyển đổi, client gọi `GET /api/v1/exams/{id}` nạp lại toàn bộ câu hỏi.
    + *Menu Chọn Ma Trận Đề:* Thẻ `<select id="shuffler-select-matrix">` nạp danh sách ma trận đặc tả từ API `GET /api/v1/matrix`.
    + *Nút Hành Động Sinh Đề Gốc:* Nút bấm **`⚡ Sinh Đề Gốc từ Ma Trận Này`** (`#btn-generate-from-matrix`) kích hoạt API `POST /api/v1/exams/generate` với `matrix_id` đã chọn, tự động lắp ghép câu hỏi từ ngân hàng thỏa mãn ma trận và nạp ngay vào Shuffler.
    + *Nút Đồng Bộ Ma Trận Hiện Tại:* Nút bấm **`🔄 Đồng bộ từ Ma trận hiện tại`** lấy cấu hình ma trận đang chỉnh sửa trong tab `/matrix` để tạo đề gốc.
    + *Thanh Thẻ Thông Tin Đề Gốc:* Hiển thị Tên đề, Môn học, Khối lớp, Thời gian thi, Tổng số câu hỏi và Thang điểm 10.0đ.
- **Thuật toán Sinh Đề Gốc theo Ràng buộc Ma trận (CSP Solver):**
  - **Đầu vào:** `matrix_id`, `title`, cờ `exclude_30d` (loại trừ câu hỏi đã thi trong 30 ngày qua), `allow_partial`.
  - **Xử lý:** Lọc câu hỏi `status = 'APPROVED'`, `is_defective == False` từ CSDL; ưu tiên câu hỏi có độ phân biệt $D \ge 0.3$ và độ khó cân đối $p \approx 0.55$.
  - **Đầu ra:** Bản ghi `master_exams` và danh sách `master_exam_items` phân theo 3 phần (Phần I: TN đơn, Phần II: Đúng/Sai, Phần III: Trả lời ngắn).
- **Hiển thị Đề thi Gốc Đầy đủ Cả 3 Thể thức (Circular 32 & Decision 764):**
  - Hiển thị đầy đủ thân câu hỏi, công thức toán KaTeX và đồ thị vector TikZ SVG.
  - Render trực quan 3 thể thức câu hỏi:
    * *Phần I (Trắc nghiệm đơn):* 4 phương án A, B, C, D; phương án đúng nổi bật bằng nền xanh lá viền xanh lá; nhãn `[Neo D]` nếu cố định.
    * *Phần II (Đúng/Sai 4 khẳng định):* 4 khẳng định con a, b, c, d có nhãn `[ĐÚNG]` (xanh) hoặc `[SAI]` (đỏ) kèm barem bậc thang QĐ 764 (0.1đ - 0.25đ - 0.5đ - 1.0đ).
    * *Phần III (Trả lời ngắn):* Ô đáp án số nổi bật (`Đáp số: <giá trị>`) với nhãn Phần III (0.5đ/câu).
  - Hiển thị nhãn thể thức, mã câu hỏi, mã YCCĐ và cờ Option Anchor nếu có phương án mỏ neo.
- **Động cơ Đổi Câu hỏi Khác (In-Place Question Swap Engine):**
  - Nút "Đổi câu khác" công thái học (hover, scale 0.97, icon `refresh-cw`).
  - Modal đổi câu hỗ trợ xem trước đầy đủ cả 3 thể thức câu hỏi của các ứng viên trước khi giáo viên chọn.
  - **Hợp đồng API:**
    * `GET /api/v1/exams/{master_id}/items/{item_id}/replacement-candidates`: Trả về danh sách câu hỏi ứng viên cùng YCCĐ, cùng mức độ Bloom, cùng thể thức, trạng thái APPROVED, không bị defective, loại trừ câu hỏi đang có trong đề gốc.
    * `POST /api/v1/exams/{master_id}/items/{item_id}/swap`:
      - Payload: `{"replacement_question_id": Optional[str]}` (nếu rỗng, tự động chọn câu tối ưu nhất).
      - Cập nhật `question_id` của `MasterExamItem`.
      - Tự động xóa các `ExamVariant` cũ để bắt buộc trộn lại.
      - Trả về `MasterExamItem` mới đã cập nhật.

### 2.11. FR-06.2: Thuật toán Trộn Đề Hoán vị An toàn 4 Nguyên Tắc & Ma Trận Đáp Án
- **Màn hình:** `SCR-SHUFFLER` (Route: `/shuffler`, tab: `#tab-shuffler` - Bước 2)
- **Đầu vào:** `master_exam_id`, danh sách mã đề cần tạo (`variant_codes: ["101", "102", "103", "104"]`).
- **4 Nguyên tắc An toàn Tuyệt đối (QĐ 764/QĐ-BGDĐT):**
  1. *Section Integrity (Bảo toàn phân đoạn):* Câu hỏi chỉ được hoán vị trong cùng một Phần / Thể thức (Phần I chỉ đảo trong Phần I, Phần II trong Phần II, Phần III trong Phần III).
  2. *Passage Integrity (Bảo toàn câu hỏi chùm / ngữ liệu):* Ngữ liệu bài đọc chung và các câu hỏi con đi kèm được gom thành một khối nguyên tử (Atomic Block); khi hoán vị, toàn bộ khối nguyên tử di chuyển cùng nhau; các câu hỏi con luôn nằm liền kề ngay sau ngữ liệu.
  3. *Option Anchor Rule (Khóa mỏ neo phương án):* Tự động phát hiện phương án có `is_fixed = True` hoặc chứa từ khóa mỏ neo vị trí ("Cả A và B", "Cả hai đáp án", "Tất cả các đáp án trên", "Tất cả các ý trên", "Không có đáp án nào"...). **BẮT BUỘC KHÓA CỐ ĐỊNH phương án này tại vị trí cuối cùng (Vị trí D)** trong mọi mã đề hoán vị; chỉ hoán vị tự do các phương án còn lại (A, B, C). Đảm bảo tỷ lệ xác minh Option Anchor Rule đạt 100%.
  4. *Key Matrix Generator (Ma trận đáp án đối chiếu):* Tự động sinh bảng ma trận đối chiếu đáp án chéo giữa đề gốc và các mã đề hoán vị (101, 102, 103, 104...).
- **Xem trước Mã đề & Xác minh Option Anchor:**
  - Segmented control Apple HIG chuyển tab mượt mà giữa các mã đề (Mã 101, 102, 103, 104).
  - Khung xem trước câu hỏi hiển thị đầy đủ cả 3 thể thức (Trắc nghiệm đơn hoán vị, Đúng/Sai 4 khẳng định, Trả lời ngắn).
  - Huy hiệu xác minh Option Anchor Rule: `Option Anchor Rule: ĐẠT 100% (Khóa cố định tại vị trí D)`.
  - Hiển thị nhãn `[Neo D]` bên cạnh phương án mỏ neo.
  - **Bảng Ma trận Ánh xạ Đáp án (Answer Key Matrix):** Hiển thị trực quan đáp án đối chiếu giữa Đề gốc và 4 mã đề hoán vị (A, B, C, D cho Phần I; chuỗi 4 khẳng định Đ/S cho Phần II; số thực cho Phần III), cột trạng thái Anchor rõ nét.
  - Tải nhanh PDF của từng mã đề đang chọn (`Tải PDF Mã {code}`) và tải trọn gói ZIP.

---

```
┌────────────────────────────────────────────────────────────────────────┐
│ MOD-07: XUẤT BẢN ĐỀ THI ĐA ĐỊNH DẠNG & ĐÓNG GÓI (.ZIP)                │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.12. FR-07.1: Xuất bản Đề thi Đơn lẻ & Đóng gói Trọn gói Ấn phẩm Khảo thí (.ZIP) Thuần Vector PDF LaTeX
- **Động Cơ Biên Dịch Thuần Vector PDF LaTeX (Tectonic XeTeX Engine):**
  * Tích hợp thống nhất cùng kiến trúc biên dịch của phân hệ Soạn đề (`/composer`): Hàm `generate_variant_latex(variant, is_solution)` tự động chuyển hóa mô hình `ExamVariant` thành tài liệu LaTeX chuẩn Bộ GD&ĐT (gói lệnh `ex_test.sty` v3.3).
  * Quy cách mã LaTeX sinh tự động (`generate_variant_latex`):
    - **Header 2 Cột Canonical:** Khối Header chuẩn mẫu khảo thí quốc gia: `\noindent`, `\begin{minipage}[t]{0.38\textwidth}\centering ... \end{minipage}`, `\hfill`, `\begin{minipage}[t]{0.58\textwidth}\centering ... \end{minipage}` (tuyệt đối không bọc ngoài bằng `\begin{center}` để tránh Overfull `\hbox` và thụt lề sai lệch).
    - **Dòng thông tin thí sinh & Đường kẻ đơn:** `\noindent Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \framebox{\textbf{Mã đề: ...}}` kèm khoảng trống co giãn an toàn, phân cách duy nhất bằng đường nét liền mảnh `\noindent
ule{\textwidth}{0.5pt}`.
    - **Phần I (Nhiều phương án lựa chọn):** Môi trường `\begin{ex}` kết hợp `\choice{A}{B}{C}{D}`, tự động lột bỏ nhãn thừa (`A. `, `B. `), khoanh đáp án đúng `\True ` khi `is_solution=True`.
    - **Phần II (Đúng/Sai bậc thang QĐ 764):** Môi trường `\begin{ex}` kết hợp `\choiceTF[1]`. **BẮT BUỘC BỌC MỌI KHẲNG ĐỊNH CON TRONG CẶP NGOẶC NHỌN `{{\True ...}}` HOẶC `{{...}}`**, tự động đệm (padding) đủ 4 khẳng định `{}` nếu câu hỏi thiếu ý, lột bỏ tiền tố nhãn thừa (`a) `, `b) `), chèn `\setcounter{ex}{0}` reset bộ đếm về 1. Triệt tiêu hoàn toàn lỗi nuốt nhầm token và vỡ cú pháp `Missing $ inserted`.
    - **Phần III (Trả lời ngắn):** Môi trường `\begin{ex}` kết hợp `\shortans{...}`, chèn `\setcounter{ex}{0}` reset bộ đếm về 1.
    - **Tự động làm sạch an toàn ký tự gạch dưới `_` qua `sanitize_latex_for_xetex`:** Tự động quét toàn bộ `stem`, `option.content`, `sub.content`, `explanation` và escape các dấu `_` nằm ngoài chế độ toán học thành `\_`, bảo toàn nguyên vẹn 100% cú pháp subscript `$x_1$`, `$\lim_{x \to 0}$` và các khối lệnh TikZ/Array, ngăn chặn triệt để lỗi biên dịch XeTeX `Missing $ inserted`.
  * **Xuất bản đề thi và lời giải qua Tectonic XeTeX Engine:**
    - `generate_variant_pdf(variant, output_pdf)`: Biên dịch qua `compile_latex_to_pdf` với `mode="dethi"`.
    - `generate_solution_pdf(variant, output_pdf)`: Biên dịch trực tiếp qua `compile_latex_to_pdf` với `mode="loigiai"`, tự động hiển thị đáp án tô màu và khối lời giải chi tiết `\begin{loigiai}` kèm barem tính điểm bậc thang.
    - Loại bỏ hoàn toàn sự phụ thuộc vào ReportLab fallback thô sơ gây lỗi font tiếng Việt và công thức text thô; chỉ sử dụng fallback Chromium CMU Serif vector khi môi trường Tectonic gặp sự cố hạ tầng.
- **Tải file PDF Đơn lẻ cho từng Mã đề:**
  - API: `GET /api/v1/exams/{master_id}/export-pdf?variant_code={code}`.
  - Xuất trực tiếp file `De_Thi_Ma_{code}.pdf` chuẩn Vector PDF A4 Portrait 2 cột sắc nét theo quy cách Bộ GD&ĐT.
- **Tải Trọn Gói Ấn Phẩm Đề Thi (.ZIP):**
  - API: `GET /api/v1/exams/{master_id}/export-zip?format=pdf`.\n  - Tự động đóng gói và tải xuống file zip chứa đầy đủ 5 thành phần:
    1. `De_{code}.pdf` cho toàn bộ các mã đề hoán vị (101, 102, 103, 104): Layout 2 cột, tiêu đề chuẩn Bộ GD&ĐT, font CMU Serif / Times, công thức toán vector sắc nét 100% biên dịch qua LaTeX engine.
    2. `LoiGiai_{code}.pdf` cho toàn bộ các mã đề hoán vị: Hướng dẫn giải chi tiết từng bước kèm barem chấm điểm bậc thang QĐ 764 biên dịch qua LaTeX engine.
    3. `BangDapAn_TongHop.pdf`: Bảng ma trận đối chiếu đáp án tổng hợp định dạng PDF in ấn.
    4. `BangDapAn_TongHop.csv`: Bảng ma trận đáp án định dạng CSV có ký tự UTF-8 BOM (`\ufeff`) tương thích 100% Microsoft Excel tiếng Việt.
    5. `Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`: Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR Bộ GD&ĐT 2025.
- **Định dạng in ấn & Khổ giấy:**
  - Khổ chuẩn quốc gia: **A4 Portrait (210 x 297 mm)**, lề trang 1.5 cm - 1.8 cm, font Times New Roman / CMU Serif 11pt, giãn dòng 1.15.
  - Header chuẩn: Tên trường/sở, môn thi, mã đề thi, bảng điền số báo danh và phách.
- **Công thức Toán đa định dạng (`math_format`):**
  - **`mathtype` (Mặc định):** Nhúng đối tượng **MathType 7.0 OLE Object Vector WMF** (`image/x-wmf` với APM header, root CLSID `{0002CE03-0000-0000-C000-000000000046}`, stream `Equation Native` chứa MTEF v5 DSMT7 và bản ghi `TeX Input Language`). Căn thẳng hàng chân dòng (baseline alignment qua `w:position` khớp chuẩn xác theo `depth_pt` của WMF), tự động nâng cấp phân số sang `\dfrac` (cỡ chữ 11pt đầy đủ cho cả tử và mẫu), chuẩn hóa khoảng cách ký tự (kerning/spacing chuẩn MathType: giãn cách toán tử `=`, `+`, `-`, đệm giữa các nhân tử kề nhau, hỗ trợ ký hiệu đạo hàm `f'(x)` chuẩn Symbol `0xa2`), bảo toàn và dựng vector đa giác cho các dấu ngoặc co giãn (`\left`, `
ight` ngoặc đơn, ngoặc vuông, ngoặc nhọn), đệm kerning chữ nghiêng tránh dính dấu ngoặc (`f(x)` -> `f\,(x)`), chuẩn hóa tập số `\mathbb{R}, \mathbb{Q}, \mathbb{Z}` sang Times New Roman Bold đứng chuẩn xác, tắt gạch chân đỏ kiểm tra chính tả của Word (`w:hideSpellingErrors`, `w:noProof`), chuẩn hóa typographic style (tên hàm `\sin`, `\cos`, `\tan`, `\cot` thẳng đứng Upright, biến số in nghiêng Italic), chuẩn hóa embellishment vectơ (`\vec`, `\overrightarrow`), áp dụng typeface `0x82` bảo toàn toàn bộ dấu ngoặc `[`, `]`, `(`, `)`, `{`, `}` trong MathType, đạt độ nét vector tuyệt đối 100% không bị fallback DIB mờ hay lỗi dấu `?` ở mọi mức zoom, **cho phép click đúp mở MathType 7 client để chỉnh sửa trực tiếp 2 chiều đồng bộ tuyệt đối với Web**.
  - **`omml`:** Phương trình bản địa Microsoft Word (`<m:oMath>`) chuyển đổi từ TeX qua MathJax MathML và XSLT.
  - **`latex`:** Giữ nguyên mã nguồn LaTeX bọc trong cặp `${...}$`.
- **Tự động chuyển đổi bảng dữ liệu thống kê (`\begin{array}`):**
  - Tự động nhận diện mảng bảng phân phối tần số ghép nhóm hoặc bảng biến thiên trong đề thi.
  - Dựng thành bảng Microsoft Word thực tế (`<w:tbl>`) căn giữa, có viền nét mảnh (`border sz="4"`), loại bỏ triệt để hiện tượng hộp đen (black box) khi xuất sang PDF.
- **Dịch vụ MathJax Persistent Worker:**
  - Chạy tiến trình nền Node.js xử lý MathJax 3/4 với bộ gói TeX đầy đủ (`input/tex-full`), thời gian sinh ~14 ms/công thức.

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
- **Mô tả:** Tiếp nhận yêu cầu prompt từ giáo viên (từ thanh compact hoặc chat popup), phân tích cùng ngữ cảnh LaTeX hiện tại, nhật ký lỗi biên dịch (nếu có) và danh sách hình ảnh đính kèm (base64 Data URL), bóc tách đề xuất sửa đổi thành cấu trúc `DiffSuggestion` để hiển thị trên editor.
- **Content-Type:** `application/json`
- **Request Body Payload:**
  ```json
  {
    "message": "Trích xuất bài toán từ ảnh và vẽ lại đồ thị hàm số bằng TikZ",
    "current_latex": "\\begin{ex}\nCho hàm số $y = f(x)$...\n\\end{ex}",
    "compile_error": null,
    "compile_error_log": null,
    "images": [
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
    ],
    "history": [
      {
        "role": "user",
        "content": "Chào trợ lý",
        "images": []
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
    "reply": "Dựa trên hình ảnh bạn cung cấp, đây là bài toán nhận diện đồ thị hàm số bậc ba $y = x^3 - 3x + 1$. Tôi đề xuất thêm khối câu hỏi chuẩn `ex_test.sty` kèm mã dựng đồ thị TikZ nét đen căn giữa chuẩn in ấn:\n\n```diff\n+ \\begin{ex}\n+ Cho hàm số $y = x^3 - 3x + 1$ có đồ thị như hình vẽ bên dưới.\n+ \\begin{center}\n+ \\begin{tikzpicture}[scale=0.5, font=\\footnotesize, >=stealth]\n+   \\draw[->] (-2.5,0) -- (2.5,0) node[right] {$x$};\n+   \\draw[->] (0,-2) -- (0,4) node[above] {$y$};\n+   \\node[below left] at (0,0) {$O$};\n+   \\draw[thick, black, smooth, samples=50, domain=-2.1:2.1] plot (\\x, {(\\x)^3 - 3*(\\x) + 1});\n+ \\end{tikzpicture}\n+ \\end{center}\n+ Số điểm cực trị của hàm số là:\n+ \\choice\n+ {0}\n+ {\\True 2}\n+ {1}\n+ {3}\n+ \\begin{loigiai}\n+ Đồ thị hàm số có 2 điểm cực trị tại $x = -1$ và $x = 1$.\n+ \\end{loigiai}\n+ \\end{ex}\n```\n\nBấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để chèn câu hỏi này.",
    "suggested_latex": null,
    "diff": {
      "action": "insert",
      "old_text": "",
      "new_text": "\\begin{ex}\nCho hàm số $y = x^3 - 3x + 1$ có đồ thị như hình vẽ bên...\n\\end{ex}",
      "description": "Thêm câu hỏi đồ thị hàm số bậc ba tái tạo từ ảnh bằng TikZ"
    },
    "diffs": [
      {
        "action": "insert",
        "old_text": "",
        "new_text": "\\begin{ex}\nCho hàm số $y = x^3 - 3x + 1$ có đồ thị như hình vẽ bên...\n\\end{ex}",
        "description": "Thêm câu hỏi đồ thị hàm số bậc ba tái tạo từ ảnh bằng TikZ"
      }
    ]
  }
  ```
- **Mô tả chi tiết Schema `DiffSuggestion`:**
  - `action` (`string`, required): Kiểu tác động (`replace` = thay thế đoạn mã hiện có; `insert` = chèn đoạn mã mới vào vị trí con trỏ).
  - `old_text` (`string`, required): Đoạn mã LaTeX cũ cần tìm và thay thế trong tài liệu hiện tại.
  - `new_text` (`string`, required): Đoạn mã LaTeX mới thay thế tương ứng.
  - `description` (`string`, required): Chuỗi tóm tắt mục đích sửa đổi để hiển thị trên huy hiệu banner editor.
- **Mô tả chi tiết Trường `images`:**
  - Danh sách chuỗi Data URL Base64 (`data:image/{png|jpeg|webp|gif};base64,...`), hỗ trợ tải lên nhiều ảnh bài toán/đồ thị trong một lượt hỏi. Phía máy chủ tự động chuyển tiếp tới LLM đa phương tiện hoặc kích hoạt động cơ nhận diện cục bộ.

### 3.4. API Lưu Đề Soạn Thảo Vào Ngân Hàng Câu Hỏi
- **Endpoint:** `POST /api/v1/composer/save-to-bank`
- **Mô tả:** Trích xuất toàn bộ câu hỏi từ mã LaTeX đang soạn thảo (cú pháp `ex_test.sty` `\begin{ex}` và cú pháp cổ điển `\textbf{Câu X.}`), tự động nhận diện môn học, khối lớp, chạy `suggest_auto_tagging` gán nhãn YCCĐ chuẩn TT 32, lưu nguyên vẹn TikZ, BBT `tkz-tab`, đáp án và lời giải vào CSDL.
- **Request Body Payload:**
  ```json
  {
    "latex_code": "\\begin{ex}\nCho hàm số $y=f(x)$...\n\\choice\n{A}\n{\\True B}\n{C}\n{D}\n\\begin{loigiai}\nLời giải...\n\\end{loigiai}\n\\end{ex}",
    "subject_id": "toan",
    "grade_id": "12"
  }
  ```
- **Response Payload (`200 OK`):**
  ```json
  {
    "success": true,
    "total_saved": 22,
    "counts": {
      "single_choice": 12,
      "true_false": 4,
      "short_answer": 6
    },
    "message": "Đã lưu thành công 22 câu hỏi vào Ngân hàng câu hỏi (12 Trắc nghiệm đơn, 4 Đúng/Sai 4 ý, 6 Trả lời ngắn)."
  }
  ```

### 3.5. API Xác Thực Người Dùng (Auth Endpoints)
- **1. Đăng ký Tài khoản:**
  - `POST /api/v1/auth/register`
  - Request: `{"email": "teacher@school.edu.vn", "password": "secure_password", "full_name": "Nguyễn Văn A", "role": "TEACHER"}`
  - Response (`201 Created`): `{"access_token": "jwt_token...", "token_type": "bearer", "user": {"id": "uuid", "email": "...", "full_name": "...", "role": "TEACHER"}}`
- **2. Đăng nhập Tài khoản:**
  - `POST /api/v1/auth/login`
  - Request: `{"email": "teacher@school.edu.vn", "password": "secure_password"}`
  - Response (`200 OK`): `{"access_token": "jwt_token...", "token_type": "bearer", "user": {"id": "uuid", "email": "...", "full_name": "...", "role": "TEACHER"}}`
- **3. Thông tin Người dùng Hiện tại:**
  - `GET /api/v1/auth/me`
  - Header: `Authorization: Bearer <token>`
  - Response (`200 OK`): `{"id": "uuid", "email": "...", "full_name": "...", "role": "TEACHER", "avatar_url": null, "created_at": "..."}`
- **4. Đăng nhập Mạng xã hội OAuth (Google / GitHub):**
  - `POST /api/v1/auth/oauth/google` & `POST /api/v1/auth/oauth/github`
  - Request: `{"token": "oauth_token", "email": "...", "name": "...", "avatar_url": "..."}`
  - Response (`200 OK`): `{"access_token": "jwt_token...", "token_type": "bearer", "user": {...}}`
- **5. Đăng xuất:**
  - `POST /api/v1/auth/logout`
  - Response (`200 OK`): `{"message": "Logged out successfully"}`

### 3.6. API Xuất & Nhập Ngân Hàng Câu Hỏi
- **1. Xuất Câu hỏi:**
  - `POST /api/v1/questions/export`
  - Request: `{"format": "pdf" | "csv" | "latex", "question_ids": ["uuid-1", "uuid-2"], "grade_id": "12", "subject_id": "toan"}`
  - Response: File download stream (PDF binary `%PDF-1.4`, CSV stream có UTF-8 BOM `\ufeff`, hoặc tệp `.tex`).
- **2. Nhập Câu hỏi:**
  - `POST /api/v1/questions/import`
  - Request: `{"source_type": "latex" | "json" | "csv", "content": "\\begin{ex}...\\end{ex}"}`
  - Response (`200 OK`): `{"success": true, "imported_count": 10, "message": "Đã nhập thành công 10 câu hỏi vào Ngân hàng"}`
- **3. Số Lượng Thống Kê Huy Hiệu:**
  - `GET /api/v1/questions/count`
  - Response (`200 OK`): `{"total": 54, "single_choice": 32, "true_false": 12, "short_answer": 10}`
