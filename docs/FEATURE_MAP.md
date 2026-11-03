# QUESY: BẢN ĐỒ TÍNH NĂNG & ĐIỂM CUỐI HỆ THỐNG (FEATURE MAP & ENDPOINT AUDIT)

> **Hệ thống:** Quesy - Trợ lý Khảo thí, Soạn đề & Số hóa Đề thi Chuẩn Quốc gia  
> **Căn cứ Khảo thí:** Thông tư 32/2018/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT (Định dạng Đề thi 2025 - 2026)  
> **Phiên bản:** v4.1  
> **Ngày lập báo cáo:** 03/11/2026  
> **Tài nguyên ảnh chụp giao diện:** Thư mục `docs/screenshots/` (21 tệp ảnh toàn diện)  
> **Tổng số API Endpoints backend:** 74 endpoints  
> **Tổng số nút và phần tử tương tác giao diện:** 206 phần tử  

---

## 1. TỔNG QUAN KIẾN TRÚC ĐIỀU HƯỚNG & GIAO DIỆN

Hệ thống Quesy được xây dựng theo kiến trúc Single Page Application (SPA). Toàn bộ giao diện tuân thủ triết lý Apple Human Interface Guidelines (HIG).

### 1.1. Bản Đồ Tuyến Đường Điều Hướng (SPA Route Map)

Mọi tuyến đường được xử lý thống nhất qua History API và Fallback Router tại backend:

| Tuyến đường URL | Tên màn hình / Phân hệ | ID Thẻ Chứa (Tab Pane) | Tiêu đề trang (Document Title) |
| :--- | :--- | :--- | :--- |
| `/` hoặc `/dashboard` | Tổng quan Khảo thí & Launchpad | `#tab-dashboard` | Quesy — Tổng quan Khảo thí |
| `/composer` hoặc `/soan-de` | Soạn đề LaTeX & AI Copilot | `#tab-composer` | Quesy — Soạn đề LaTeX (AI Copilot & Live PDF Preview) |
| `/digitize` hoặc `/digitize-test` | Số hóa Đề thi AI (HITL Studio) | Điều hướng vào `#tab-itembank` và mở Modal Nạp tệp | Quesy — Ngân hàng Câu hỏi Chuẩn hóa |
| `/bank` hoặc `/itembank` | Ngân hàng Câu hỏi Chuẩn hóa | `#tab-itembank` | Quesy — Ngân hàng Câu hỏi Chuẩn hóa |
| `/matrix` | Thiết lập Ma trận Đề thi 2D | `#tab-matrix` | Quesy — Ma trận Đề thi 2D |
| `/shuffler` | Sinh đề, Trộn đề & Khảo thí CTT | `#tab-shuffler` | Quesy — Sinh đề & Trộn đề (Vector PDF) |
| `/docs` | Tài liệu API tương tác Swagger | Giao diện FastAPI Swagger UI | QUESY Exam Management & AI Digitization API - Swagger UI |
| `/redoc` | Tài liệu API chuẩn ReDoc | Giao diện FastAPI ReDoc | QUESY Exam Management & AI Digitization API - ReDoc |

---

## 2. THANH ĐIỀU HƯỚNG CHUNG TOÀN ỨNG DỤNG (APPLE HEADER TOOLBAR)

Thanh Header được cố định tại đỉnh trang (`sticky top-0 z-40`). Chiều cao tiêu chuẩn 56px (Desktop 64px).

![Thanh Điều Hướng Header](screenshots/01_dashboard.png)

### Danh Sách Nút & Phần Tử Điều Hướng Header

| STT | Tên phần tử / Nhãn | Bộ chọn DOM (ID / Class) | Vị trí giao diện | Hành vi / Hàm xử lý | Điểm cuối API liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Logo Quesy 2026 | `.cursor-pointer` | Góc trên cùng bên trái | Gọi `app.navigateTo('/')` về trang chủ | `GET /dashboard` |
| 2 | Tab Tổng quan | `#nav-btn-dashboard` | Cụm tab trung tâm (vị trí 1) | Gọi `app.navigateTo('/dashboard')` | `GET /dashboard` |
| 3 | Tab Soạn đề | `#nav-btn-composer` | Cụm tab trung tâm (vị trí 2) | Gọi `app.navigateTo('/composer')` | `GET /composer` |
| 4 | Tab Ngân hàng câu hỏi | `#nav-btn-itembank` | Cụm tab trung tâm (vị trí 3) | Gọi `app.navigateTo('/bank')` | `GET /bank`, `GET /api/v1/questions` |
| 5 | Huy hiệu đếm số lượng | `#bank-count-badge` | Nằm trong `#nav-btn-itembank` | Hiển thị tổng số câu hỏi khả dụng trong ngân hàng | `GET /api/v1/questions/count` |
| 6 | Tab Ma trận đề | `#nav-btn-matrix` | Cụm tab trung tâm (vị trí 4) | Gọi `app.navigateTo('/matrix')` | `GET /matrix`, `GET /api/v1/matrices` |
| 7 | Tab Sinh & Trộn đề | `#nav-btn-shuffler` | Cụm tab trung tâm (vị trí 5) | Gọi `app.navigateTo('/shuffler')` | `GET /shuffler`, `GET /api/v1/exams` |
| 8 | Nút Đăng nhập | `#auth-guest-controls button:nth-child(1)` | Góc trên cùng bên phải | Mở hộp thoại xác thực `app.auth.openAuthModal('login')` | `POST /api/v1/auth/login` |
| 9 | Nút Đăng ký | `#auth-guest-controls button:nth-child(2)` | Góc trên cùng bên phải | Mở hộp thoại đăng ký `app.auth.openAuthModal('register')` | `POST /api/v1/auth/register` |
| 10 | Menu Tài khoản Giáo viên | `#auth-user-dropdown` | Góc trên cùng bên phải (khi đã login) | Hiển thị thông tin giáo viên và nút Đăng xuất | `POST /api/v1/auth/logout` |

---

## 3. MÀN HÌNH TỔNG QUAN KHẢO THÍ (`/dashboard`)

Màn hình điều khiển trung tâm (Dashboard Hub) cung cấp cái nhìn toàn diện về tài nguyên đề thi, 4 thẻ khởi chạy nhanh, tiêu điểm đề thi Quốc gia 2026 Mã 0101, và bảng giám sát bất biến khảo thí.

![Dashboard Tổng Quan](screenshots/01_dashboard.png)
![Dashboard Phần Cuộn Dưới](screenshots/01b_dashboard_scrolled.png)

### 3.1. Các Khu Vực Chức Năng Trên Màn Hình Dashboard

1. **Thanh tác vụ nhanh (Header Action Bar):** Nằm góc phải trên banner chào mừng.
2. **4 Thẻ Khởi chạy Nhanh (Apple Quick Action Cards):** Thiết kế dạng thẻ bo tròn sang trọng, hiệu ứng hover nhấc nổi.
3. **Tiêu điểm Đề thi Chuẩn Quốc gia 2026 (Mã 0101):** Khung thông tin nổi bật với 22 câu hỏi chuẩn cấu trúc (12 MCQ + 4 TF + 6 SA).
4. **Bảng Giám Sát Bất Biến Khảo Thí (Invariant Telemetry Audit):** Theo dõi 4 quy tắc an toàn khảo thí (Section Integrity, Passage Integrity, Option Anchor Lock, Key Mapping).
5. **Bảng Lịch Sử Đề Thi Đã Sinh (Recent Master Exams Table):** Danh sách các đề thi gần nhất kèm nút thao tác.

### 3.2. Danh Sách Chi Tiết Từng Nút & Thành Phần Tương Tác Trên Dashboard

| STT | Tên nút / Nhãn hiển thị | Bộ chọn DOM | Vị trí giao diện | Hành vi xử lý khi nhấn | Điểm cuối API kích hoạt |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Soạn đề LaTeX (AI) | `.btn-apple-primary` | Thanh tác vụ đỉnh phải | Chuyển sang phân hệ soạn đề: `app.openQuickAction('composer')` | `GET /composer` |
| 2 | Số hóa Đề thi | `.btn-apple-secondary` (vị trí 1) | Thanh tác vụ đỉnh phải | Chuyển đến ngân hàng và mở modal nạp tệp: `app.openQuickAction('digitize')` | `POST /api/v1/digitize/upload` |
| 3 | Xuất bản Đề thi | `.btn-apple-secondary` (vị trí 2) | Thanh tác vụ đỉnh phải | Chuyển sang phân hệ trộn và xuất bản: `app.openQuickAction('shuffler')` | `GET /shuffler` |
| 4 | Thẻ Khởi chạy Soạn Đề 2026 | `.apple-quick-card` (thẻ 1) | Lưới khởi chạy, cột 1 | Tải mẫu đề chuẩn 22 câu vào trình soạn thảo | `GET /api/v1/composer/templates` |
| 5 | Thẻ Số Hóa Đề Thi AI | `.apple-quick-card` (thẻ 2) | Lưới khởi chạy, cột 2 | Mở modal bóc tách tài liệu thông minh | `POST /api/v1/upload` |
| 6 | Thẻ Thiết Lập Ma Trận 2D | `.apple-quick-card` (thẻ 3) | Lưới khởi chạy, cột 3 | Điều hướng đến màn hình ma trận đa tầng: `app.openQuickAction('matrix')` | `GET /api/v1/matrices` |
| 7 | Thẻ Sinh & Trộn Đề Hoán Vị | `.apple-quick-card` (thẻ 4) | Lưới khởi chạy, cột 4 | Điều hướng đến động cơ hoán vị mã đề an toàn | `GET /api/v1/exams` |
| 8 | Mở trong Trình Soạn Đề | Nút xanh chính trên thẻ Mã 0101 | Cột phải thẻ Tiêu điểm Đề thi | Nạp cấu trúc đề 0101 vào Composer: `app.loadStandard2026Blueprint()` | `GET /composer` |
| 9 | Trộn sang các mã đề khác | Nút phụ trắng (vị trí 1) | Cột phải thẻ Tiêu điểm Đề thi | Chuyển sang tab trộn đề với đề gốc được chọn | `POST /api/v1/exams/shuffle` |
| 10 | Xem ma trận đề | Nút phụ trắng (vị trí 2) | Cột phải thẻ Tiêu điểm Đề thi | Chuyển sang tab ma trận để xem tỷ lệ phân bổ Bloom | `GET /api/v1/matrix` |
| 11 | Xem tất cả mã đề | Nút phụ ở tiêu đề bảng lịch sử | Đỉnh bảng lịch sử đề thi | Chuyển sang phân hệ Shuffler | `GET /shuffler` |
| 12 | Mở soạn thảo (Từng dòng) | Nút màu tím trong bảng | Cột thao tác của từng dòng đề thi | Mở đề thi tương ứng trong trình soạn thảo Composer | `GET /api/v1/composer/templates` |
| 13 | Trộn đề (Từng dòng) | Nút màu xám trong bảng | Cột thao tác của từng dòng đề thi | Chuyển sang Shuffler với mã đề tương ứng | `POST /api/v1/exams/{id}/shuffle` |
| 14 | Xem chi tiết (Từng dòng) | Nút xem chi tiết | Cột thao tác của từng dòng đề thi | Xem toàn bộ câu hỏi và đáp án chi tiết | `GET /api/v1/exams/{id}` |

---

## 4. MÀN HÌNH SOẠN ĐỀ LATEX & TRỢ LÝ AI COPILOT (`/composer` & `/soan-de`)

Không gian làm việc Split-View tỷ lệ chuẩn 6:4 (60% Cột trái Soạn thảo mã nguồn Dark Theme, 40% Cột phải Bản in PDF Vector sắc nét). Hệ thống nhúng ngầm gói lệnh quốc gia `ex_test.sty` v3.3.6, fontspec, TikZ, và tkz-tab.

![Composer Giao Diện Chính](screenshots/02_composer_main.png)
![Composer Trợ Lý AI Khảo Thí](screenshots/02b_composer_ai_assistant.png)
![Composer Menu Thêm Mẫu Đề](screenshots/02c_composer_templates_menu.png)

### 4.1. Cấu Trúc Hai Cột Không Gian Soạn Đề

```
┌────────────────────────────────────────────────────────┬────────────────────────────────────────────┐
│          CỘT TRÁI (60%): TRÌNH SOẠN THẢO MÃ NGUỒN      │     CỘT PHẢI (40%): LIVE VECTOR PDF        │
│ ┌────────────────────────────────────────────────────┐ │ ┌────────────────────────────────────────┐ │
│ │ Header: [MỚI] [THÊM ▾] [LỜI GIẢI] [XUẤT FILE ▾]    │ │ │ Floating: [Trang 1/1] [Zoom] [Biên dịch]│ │
│ ├────────────────────────────────────────────────────┤ │ ├────────────────────────────────────────┤ │
│ │ Inline Diff Overlay: [Keep] [Undo] [Áp dụng tất cả]│ │ │                                        │ │
│ ├────────────────────────────────────────────────────┤ │ │         PDF.js High-DPI Canvas         │ │
│ │ Gutter (Dòng) | Vùng nhập mã LaTeX (#141824)       │ │ │       Bản in Vector Chuẩn Bộ GD&ĐT     │ │
│ ├────────────────────────────────────────────────────┤ │ │                                        │ │
│ │ Status bar: Dòng 1, Cột 1 • Preamble tự động nhúng │ │ │                                        │ │
│ ├────────────────────────────────────────────────────┤ │ ├────────────────────────────────────────┤ │
│ │ Floating AI Prompt Bar: [✨ Chat AI] [📎 Ảnh] [Gửi] │ │ │ [BIÊN DỊCH (F5)]   [LƯU NGÂN HÀNG]     │ │
│ ├────────────────────────────────────────────────────┤ │ └────────────────────────────────────────┘ │
│ │ Pop-up Trợ lý Soạn thảo (Vertical Split View)      │ │                                            │
│ └────────────────────────────────────────────────────┘ │                                            │
└────────────────────────────────────────────────────────┴────────────────────────────────────────────┘
```

### 4.2. Danh Sách Chi Tiết Từng Nút & Thành Phần Trên Trình Soạn Đề

| STT | Tên nút / Phần tử | Bộ chọn DOM | Vị trí giao diện | Chức năng kỹ thuật & Hành vi | Điểm cuối API liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | MỚI | `button[onclick*="newDocument"]` | Header Editor, góc trái | Làm rỗng trình soạn thảo và đặt lại tài liệu trắng | Không gọi API |
| 2 | THÊM ▾ | `#btn-dropdown-them` | Header Editor, cạnh nút MỚI | Mở menu đổ xuống gồm 11 mẫu lệnh khảo thí chuẩn | `GET /api/v1/composer/templates` |
| 3 | Mẫu: Tiêu đề 2 Cột & Mã đề | `button[onclick*="header_quocgia"]` | Dropdown THÊM (Mục I.1) | Chèn khối tiêu đề chuẩn Bộ GD&ĐT và khung thí sinh | Không gọi API |
| 4 | Mẫu: Phần I (12 câu TN) | `button[onclick*="section_phan1"]` | Dropdown THÊM (Mục I.2) | Chèn tiêu đề Phần I và 12 câu trắc nghiệm 4 lựa chọn | Không gọi API |
| 5 | Mẫu: Phần II (4 câu Đ/S) | `button[onclick*="section_phan2"]` | Dropdown THÊM (Mục I.3) | Chèn tiêu đề Phần II và 4 câu Đúng/Sai 4 khẳng định | Không gọi API |
| 6 | Mẫu: Phần III (6 câu TLN) | `button[onclick*="section_phan3"]` | Dropdown THÊM (Mục I.4) | Chèn tiêu đề Phần III và 6 câu Trả lời ngắn | Không gọi API |
| 7 | Mẫu: Trọn bộ Đề thi Quốc Gia | `button[onclick*="dethi_quocgia_full"]` | Dropdown THÊM (Mục I.5) | Chèn toàn bộ đề thi chuẩn 2025 đầy đủ 3 phần | Không gọi API |
| 8 | Mẫu: Trắc nghiệm đơn | `button[onclick*="tracnghiem"]` | Dropdown THÊM (Mục II.1) | Chèn cú pháp `\begin{ex} ... \choice ... \end{ex}` | Không gọi API |
| 9 | Mẫu: Đúng / Sai | `button[onclick*="dungsai"]` | Dropdown THÊM (Mục II.2) | Chèn cú pháp `\choiceTF{...}{...}{...}{...}` | Không gọi API |
| 10 | Mẫu: Trả lời ngắn | `button[onclick*="traloingan"]` | Dropdown THÊM (Mục II.3) | Chèn cú pháp `\shortans{...}` | Không gọi API |
| 11 | Mẫu: Tự luận | `button[onclick*="tuluan"]` | Dropdown THÊM (Mục II.4) | Chèn cú pháp câu tự luận kèm lời giải chi tiết | Không gọi API |
| 12 | Mẫu: Hình TikZ | `button[onclick*="hinhtikz"]` | Dropdown THÊM (Mục II.5) | Chèn khung vẽ `\begin{tikzpicture} ... \end{tikzpicture}` | `POST /api/v1/digitize/render-tikz` |
| 13 | Mẫu: Hình cạnh chữ | `button[onclick*="hinhcanhchu"]` | Dropdown THÊM (Mục II.6) | Chèn bố cục hình bên phải, đề bài bên trái bằng minipage | Không gọi API |
| 14 | Mẫu: Lời giải chi tiết | `button[onclick*="loigiai"]` | Dropdown THÊM (Mục II.7) | Chèn khối môi trường `\loigiai{...}` chuẩn `ex_test` | Không gọi API |
| 15 | Công tắc LỜI GIẢI | `#composer-solution-toggle` | Header Editor, chính giữa | Chuyển đổi qua lại giữa tùy chọn `[dethi]` và `[loigiai]` | `POST /api/v1/composer/compile` |
| 16 | XUẤT FILE ▾ | `#btn-dropdown-export` | Header Editor, cạnh Lời giải | Mở menu xuất bản tài liệu đề thi | `GET /api/v1/composer/export` |
| 17 | Tải tệp PDF | `button[onclick*="downloadPdf"]` | Trong menu XUẤT FILE | Tải trực tiếp tệp PDF vector đã biên dịch | `GET /api/v1/composer/pdf/{id}.pdf` |
| 18 | Tải mã nguồn LaTeX | `button[onclick*="downloadTex"]` | Trong menu XUẤT FILE | Tải tệp mã nguồn độc lập `.tex` kèm Preamble đầy đủ | `POST /api/v1/composer/export` |
| 19 | Lưu vào Ngân hàng Câu hỏi | `button[onclick*="saveToBank"]` | Trong menu XUẤT FILE | Bóc tách từng câu hỏi từ mã LaTeX và lưu vào cơ sở dữ liệu | `POST /api/v1/composer/save-to-bank` |
| 20 | Hoàn tác (Undo) | `button[onclick*="undo"]` | Header Editor, góc phải | Quay lại trạng thái văn bản trước đó (Ctrl+Z) | Không gọi API |
| 21 | Làm lại (Redo) | `button[onclick*="redo"]` | Header Editor, góc phải | Khôi phục trạng thái văn bản vừa hoàn tác (Ctrl+Y) | Không gọi API |
| 22 | Xóa toàn bộ (Eraser) | `button[onclick*="clearEditor"]` | Header Editor, góc phải | Xóa toàn bộ văn bản đang soạn thảo | Không gọi API |
| 23 | Sao chép tất cả (Copy) | `button[onclick*="copyAll"]` | Header Editor, góc phải | Chép toàn bộ mã nguồn vào Clipboard máy tính | Không gọi API |
| 24 | Keep / Đồng ý gợi ý AI | `button[onclick*="applyCurrentDiff"]` | Banner Diff hoặc Overlay Inline | Áp dụng đoạn sửa đổi AI đề xuất vào đúng dòng hiện tại | Không gọi API |
| 25 | Undo / Từ chối gợi ý AI | `button[onclick*="skipCurrentDiff"]` | Banner Diff hoặc Overlay Inline | Bỏ qua gợi ý sửa đổi hiện tại | Không gọi API |
| 26 | Áp dụng tất cả gợi ý AI | `#composer-apply-all-btn` | Banner Diff hoặc Overlay Inline | Áp dụng đồng loạt tất cả các vị trí đề xuất của AI | Không gọi API |
| 27 | Gợi ý trước [<] | `button[onclick*="prevDiff"]` | Thanh điều hướng Diff | Di chuyển đến khối gợi ý sửa đổi liền trước | Không gọi API |
| 28 | Gợi ý kế tiếp [>] | `button[onclick*="nextDiff"]` | Thanh điều hướng Diff | Di chuyển đến khối gợi ý sửa đổi kế tiếp | Không gọi API |
| 29 | Ô nhập mã nguồn LaTeX | `#composer-editor-input` | Thân editor Cột trái | Khu vực nhập liệu mã nguồn với font JetBrains Mono | Không gọi API |
| 30 | Cột số dòng (Gutter) | `#composer-editor-gutter` | Cạnh trái ô soạn thảo | Hiển thị số thứ tự dòng và đồng bộ cuộn | Không gọi API |
| 31 | Ô nhập lệnh AI Copilot nhanh | `#composer-compact-input` | Thanh nổi dưới đáy Cột trái | Nhập câu lệnh yêu cầu AI sửa đổi, thêm câu hoặc vẽ TikZ | `POST /api/v1/composer/chat` |
| 32 | Đính kèm ảnh đề bài | `button[onclick*="compact-image"]` | Trong thanh nổi AI | Tải lên ảnh chụp đề bài để AI nhận diện và trích xuất | `POST /api/v1/composer/chat` |
| 33 | Menu mẫu lệnh AI nhanh (+) | `button[onclick*="toggleCompactQuickMenu"]` | Trong thanh nổi AI | Hiển thị danh mục câu lệnh prompt sư phạm dựng sẵn | Không gọi API |
| 34 | Nút Gửi lệnh AI (Mũi tên tròn) | `button[onclick*="submitFromCompact"]` | Trong thanh nổi AI | Gửi câu lệnh và ngữ cảnh sang AI Copilot xử lý | `POST /api/v1/composer/chat` |
| 35 | Nút Thu nhỏ Hộp Trợ lý | `button[onclick*="closeAIPopup"]` | Header Hộp Trợ lý AI | Ẩn giao diện chat trợ lý để mở rộng khung soạn thảo | Không gọi API |
| 36 | Con lăn thay đổi độ cao | `#composer-ai-resize-handle` | Đỉnh hộp Trợ lý AI | Kéo thả hoặc click để chuyển đổi độ cao hộp trợ lý | Không gọi API |
| 37 | Nút Lịch sử phiên chat | `#composer-ai-history-btn` | Header Hộp Trợ lý AI | Xem danh sách các cuộc hội thoại và can thiệp trước đó | Không gọi API |
| 38 | Nút Tạo phiên chat mới | `button[onclick*="newChat"]` | Header Hộp Trợ lý AI | Làm mới ngữ cảnh trợ lý | Không gọi API |
| 39 | Nút Xóa lịch sử chat | `button[onclick*="clearChat"]` | Header Hộp Trợ lý AI | Xóa toàn bộ hội thoại của phiên hiện tại | Không gọi API |
| 40 | Nút Toàn màn hình trợ lý | `button[onclick*="toggleAIPopupFullscreen"]`| Header Hộp Trợ lý AI | Mở rộng hộp trợ lý chiếm trọn cột trái | Không gọi API |
| 41 | Thanh trượt chia đôi cột | `#composer-split-resizer` | Giữa Cột trái và Cột phải | Kéo để chỉnh tỷ lệ độ rộng 2 cột (Nháy đúp để về 60:40) | Không gọi API |
| 42 | Trang trước (PDF) | `button[onclick*="prevPage"]` | Thanh nổi góc trên Cột phải | Lật về trang PDF phía trước | Không gọi API |
| 43 | Trang sau (PDF) | `button[onclick*="nextPage"]` | Thanh nổi góc trên Cột phải | Lật sang trang PDF kế tiếp | Không gọi API |
| 44 | Thu nhỏ xem trước (-) | `button[onclick*="zoomPreview(-0.1)"]` | Thanh nổi góc trên Cột phải | Thu nhỏ tỷ lệ hiển thị PDF | Không gọi API |
| 45 | Phóng to xem trước (+) | `button[onclick*="zoomPreview(0.1)"]` | Thanh nổi góc trên Cột phải | Phóng to tỷ lệ hiển thị PDF | Không gọi API |
| 46 | Tỷ lệ gốc (1:1) | `button[onclick*="resetZoom"]` | Thanh nổi góc trên Cột phải | Đặt lại mức thu phóng về 100% | Không gọi API |
| 47 | Vừa khung ngang (Fit Width) | `#composer-zoom-fit-btn` | Thanh nổi góc trên Cột phải | Tự động căn chỉnh chiều ngang vừa khít khung nhìn | Không gọi API |
| 48 | Biên dịch lại nhanh (Nút xoay) | `button[onclick*="compile(true)"]` | Thanh nổi góc trên Cột phải | Kích hoạt lại tiến trình biên dịch Tectonic XeTeX | `POST /api/v1/composer/compile` |
| 49 | Khung vẽ PDF Vector | `#composer-pdf-scroll-container` | Toàn bộ diện tích Cột phải | Hiển thị trang in sắc nét qua chuẩn vector canvas | `GET /api/v1/composer/pdf/{id}.pdf` |
| 50 | Nút BIÊN DỊCH chính | `#composer-compile-btn` | Đáy Cột phải (Nút xanh nổi bật) | Biên dịch tài liệu LaTeX sang PDF (Phím tắt: Ctrl+S) | `POST /api/v1/composer/compile` |
| 51 | Nút LƯU NGÂN HÀNG | `#btn-composer-save-to-bank` | Đáy Cột phải (Nút xanh lá) | Bóc tách toàn bộ câu hỏi trong văn bản nạp vào CSDL | `POST /api/v1/composer/save-to-bank` |

---

## 5. MÀN HÌNH NGÂN HÀNG CÂU HỎI CHUẨN HÓA (`/bank`)

Quản trị kho câu hỏi theo cây kiến thức chuẩn 6 tầng Thông tư 32/2018/TT-BGDĐT và 4 mức độ nhận thức của Quyết định 764/QĐ-BGDĐT.

![Ngân Hàng Câu Hỏi - Thẻ Chi Tiết](screenshots/03_bank_detailed.png)
![Ngân Hàng Câu Hỏi - Bảng Gọn](screenshots/03b_bank_compact.png)

### 5.1. Bố Cục Phân Hệ Ngân Hàng Câu Hỏi

1. **Thanh tìm kiếm & Điều khiển bộ lọc:** Tìm kiếm toàn văn theo từ khóa, công thức LaTeX, mã câu hỏi hoặc mã YCCĐ.
2. **Ngăn Cây Kiến Thức 6 Tầng (Taxonomy Drawer):** Mạch nội dung -> Chủ đề -> Bài học -> Yêu cầu cần đạt (YCCĐ) -> Dạng bài tập (Problem Archetype).
3. **Bộ lọc nhanh định dạng (Format Pills):** Lọc theo Tất cả, Phần I, Phần II, Phần III, Tự luận.
4. **Bộ lọc mức độ nhận thức (Cognitive Level Pills):** Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao.
5. **Chế độ hiển thị kép:** Chuyển đổi linh hoạt giữa Dạng Thẻ KaTeX Chi Tiết và Dạng Bảng Gọn.
6. **Thẻ câu hỏi KaTeX:** Hiển thị công thức toán học sắc nét, 4 phương án hoặc 4 khẳng định Đúng/Sai, lời giải ẩn/hiện, và cụm nút thao tác độc lập trên từng câu.

### 5.2. Danh Sách Chi Tiết Từng Nút & Thành Phần Trên Ngân Hàng Câu Hỏi

| STT | Tên nút / Phần tử | Bộ chọn DOM | Vị trí giao diện | Chức năng kỹ thuật & Hành vi | Điểm cuối API liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Ô tìm kiếm câu hỏi | `#bank-search-input` | Thanh trên cùng bên trái | Tìm kiếm theo nội dung, mã YCCĐ, từ khóa công thức | `GET /api/v1/questions?q={query}` |
| 2 | Nút xóa tìm kiếm (✕) | `#bank-search-clear-btn` | Nằm trong ô tìm kiếm | Xóa nội dung tìm kiếm và tải lại toàn bộ danh sách | `GET /api/v1/questions` |
| 3 | Nút Cây kiến thức 6 tầng | `#btn-toggle-taxonomy-drawer` | Cạnh ô tìm kiếm | Bật/tắt ngăn lọc phân cấp 6 tầng Thông tư 32 | `GET /api/v1/taxonomy/tree` |
| 4 | Nút Đặt lại bộ lọc | `#btn-reset-bank-filters` | Cạnh nút Cây kiến thức | Đưa toàn bộ các tiêu chí lọc về trạng thái mặc định | `GET /api/v1/questions` |
| 5 | Lọc định dạng: Tất cả | `#pill-format-all` | Dải nút lọc định dạng (vị trí 1) | Hiển thị toàn bộ câu hỏi không phân biệt thể thức | `GET /api/v1/questions` |
| 6 | Lọc: Phần I (Trắc nghiệm) | `#pill-format-single_choice` | Dải nút lọc định dạng (vị trí 2) | Chỉ hiển thị câu trắc nghiệm 4 phương án chọn 1 | `GET /api/v1/questions?format=SINGLE_CHOICE` |
| 7 | Lọc: Phần II (Đúng/Sai) | `#pill-format-true_false_group`| Dải nút lọc định dạng (vị trí 3) | Chỉ hiển thị câu hỏi Đúng/Sai 4 khẳng định | `GET /api/v1/questions?format=TRUE_FALSE_GROUP` |
| 8 | Lọc: Phần III (Trả lời ngắn) | `#pill-format-short_answer` | Dải nút lọc định dạng (vị trí 4) | Chỉ hiển thị câu hỏi yêu cầu điền đáp số | `GET /api/v1/questions?format=SHORT_ANSWER` |
| 9 | Lọc: Tự luận | `#pill-format-essay` | Dải nút lọc định dạng (vị trí 5) | Hiển thị các bài tập tự luận truyền thống | `GET /api/v1/questions?format=ESSAY` |
| 10 | Lọc nhận thức: Tất cả | `#pill-cog-all` | Dải nút lọc nhận thức (vị trí 1) | Hiển thị tất cả các cấp độ nhận thức | `GET /api/v1/questions` |
| 11 | Lọc: Nhận biết | `#pill-cog-nb` | Dải nút lọc nhận thức (vị trí 2) | Lọc câu hỏi mức độ Nhận biết | `GET /api/v1/questions?cognitive_level=NHAN_BIET` |
| 12 | Lọc: Thông hiểu | `#pill-cog-th` | Dải nút lọc nhận thức (vị trí 3) | Lọc câu hỏi mức độ Thông hiểu | `GET /api/v1/questions?cognitive_level=THONG_HIEU` |
| 13 | Lọc: Vận dụng | `#pill-cog-vd` | Dải nút lọc nhận thức (vị trí 4) | Lọc câu hỏi mức độ Vận dụng | `GET /api/v1/questions?cognitive_level=VAN_DUNG` |
| 14 | Lọc: Vận dụng cao | `#pill-cog-vdc` | Dải nút lọc nhận thức (vị trí 5) | Lọc câu hỏi mức độ Vận dụng cao | `GET /api/v1/questions?cognitive_level=VAN_DUNG_CAO` |
| 15 | Xem dạng Thẻ chi tiết | `#bank-view-detailed` | Góc phải thanh điều khiển | Hiển thị câu hỏi dạng thẻ phong phú kèm KaTeX | Không gọi API |
| 16 | Xem dạng Bảng gọn | `#bank-view-compact` | Góc phải thanh điều khiển | Hiển thị câu hỏi dạng bảng quản trị dữ liệu | Không gọi API |
| 17 | Nút + Thêm Câu Hỏi | `button[onclick*="openCreateQuestionModal"]` | Góc trên cùng bên phải | Mở hộp thoại nhập câu hỏi thủ công đa thể thức | `POST /api/v1/questions` |
| 18 | Nút Nạp Đề Thi AI (Số hóa) | `button[onclick*="openImportQuestionModal"]` | Cạnh nút Thêm câu hỏi | Mở modal tiếp nhận văn bản LaTeX/Word để bóc tách | `POST /api/v1/questions/import` |
| 19 | Nút Xem chi tiết (Thẻ/Dòng) | `button[onclick*="openQuestionDetailModal"]`| Góc phải thẻ câu hỏi | Mở modal xem toàn văn câu hỏi, các ý, và đáp án chi tiết | `GET /api/v1/questions/{id}` |
| 20 | Nút Chỉnh sửa HITL (Thẻ/Dòng) | `button[onclick*="openQuestionEditorModal"]`| Cạnh nút Xem chi tiết | Mở giao diện biên tập câu hỏi với Live Preview KaTeX | `PUT /api/v1/questions/{id}` |
| 21 | Nút Xóa câu hỏi (Thẻ/Dòng) | `button[onclick*="deleteQuestion"]` | Nút thùng rác đỏ | Xóa câu hỏi khỏi cơ sở dữ liệu với xác nhận an toàn | `DELETE /api/v1/questions/{id}` |

---

## 6. MÀN HÌNH THIẾT LẬP MA TRẬN ĐỀ THI 2D (`/matrix`)

Công cụ thiết kế ma trận khảo thí đa chiều: 4 Mạch nội dung x 3 Phần cấu trúc đề 2025 x 4 Mức độ nhận thức Bloom. Tích hợp động cơ kiểm tra tồn kho ngân hàng thời gian thực.

![Ma Trận Đề Thi 2D](screenshots/04_matrix.png)

### 6.1. Đặc Tính Kỹ Thuật Của Ma Trận Đề Thi 2D

- **Kiểm tra số dư tồn kho thời gian thực (Real-time Bank Inventory):** Mỗi ô ma trận hiển thị số lượng câu hỏi yêu cầu kèm số dư khả dụng trong kho. Nếu thiếu câu hỏi, ô đổi sang màu đỏ và hiển thị chỉ số thiếu hụt.
- **Thanh tổng kết chân trang cố định (Sticky Summary Footer):** Tự động tính toán tổng số lượng câu hỏi, tổng điểm số, và đối chiếu với khung chuẩn cấu trúc Bộ GD&ĐT (22 câu, 10 điểm).

### 6.2. Danh Sách Chi Tiết Từng Nút & Phần Tử Trên Ma Trận Đề Thi

| STT | Tên nút / Phần tử | Bộ chọn DOM | Vị trí giao diện | Chức năng kỹ thuật & Hành vi | Điểm cuối API liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Ô nhập tên ma trận | `#matrix-param-name` | Thanh tham số trên cùng | Đặt tên định danh cho ma trận đề thi | `POST /api/v1/matrices` |
| 2 | Bộ chọn thời gian thi | `#matrix-param-time` | Cạnh ô nhập tên | Chọn thời lượng (45 phút, 50 phút, 90 phút) | Không gọi API |
| 3 | Nút Thêm Dòng Ma Trận | `button[onclick*="openAddMatrixRowModal"]` | Góc trên bên phải lưới | Mở modal bổ sung yêu cầu kiến thức mới vào ma trận | Không gọi API |
| 4 | Nút Lưu Bản Thảo | `button[onclick*="saveMatrixConfig"]` | Thanh tác vụ trên | Lưu cấu hình ma trận hiện tại vào cơ sở dữ liệu | `POST /api/v1/matrices` |
| 5 | Ô nhập số lượng từng ô | `input.matrix-cell-input` | Từng ô giao giữa YCCĐ và Mức độ | Điều chỉnh số lượng câu hỏi cho cell tương ứng | `POST /api/v1/matrix/check-availability` |
| 6 | Nút Xóa dòng ma trận | `button.matrix-delete-row-btn` | Cột cuối cùng của từng hàng | Loại bỏ hàng chỉ tiêu kiến thức ra khỏi ma trận | Không gọi API |
| 7 | Nút Sinh Đề Gốc từ Ma Trận | `#btn-matrix-generate-exam` | Nằm tại thanh Sticky Footer | Kích hoạt thuật toán rút đề ngẫu nhiên có trọng số | `POST /api/v1/exams/generate` |
| 8 | Huy hiệu đếm Phần I | `#matrix-footer-part1-count` | Sticky Footer, cụm thống kê | Hiển thị tổng số câu và điểm số Phần I (chuẩn 12 câu) | Không gọi API |
| 9 | Huy hiệu đếm Phần II | `#matrix-footer-part2-count` | Sticky Footer, cụm thống kê | Hiển thị tổng số câu và điểm số Phần II (chuẩn 4 câu) | Không gọi API |
| 10 | Huy hiệu đếm Phần III | `#matrix-footer-part3-count` | Sticky Footer, cụm thống kê | Hiển thị tổng số câu và điểm số Phần III (chuẩn 6 câu) | Không gọi API |
| 11 | Huy hiệu tổng điểm số | `#matrix-footer-total-score` | Sticky Footer, cụm thống kê | Cảnh báo trạng thái cân bằng điểm số (chuẩn 10.0 điểm) | Không gọi API |

---

## 7. MÀN HÌNH SINH ĐỀ, TRỘN ĐỀ & KHẢO THÍ CTT (`/shuffler`)

Phân hệ hoán vị đề thi an toàn tuyệt đối, tuân thủ 4 nguyên tắc bảo toàn khảo thí và cung cấp công cụ trắc lượng học CTT cùng chấm thi OMR tự động.

![Sinh Đề & Trộn Đề Hoán Vị](screenshots/05_shuffler.png)

### 7.1. Bốn Nguyên Tắc Hoán Vị Bất Biến (Invariant Permutation Rules)

1. **RULE-01 (Chấm điểm Đúng/Sai lũy tiến):** Tính điểm 4 khẳng định theo thang chuẩn Bộ GD&ĐT (1 ý: 0.1đ; 2 ý: 0.25đ; 3 ý: 0.5đ; 4 ý: 1.0đ).
2. **RULE-02 (Khóa cố định vị trí đáp án neo - Option Anchor Rule):** Tự động phát hiện các phương án phụ thuộc vị trí ("Tất cả các đáp án trên", "Cả A và B đều đúng") để khóa cố định tại vị trí D.
3. **RULE-03 (Bảo toàn phân vùng đề thi - Section & Passage Integrity):** Tuyệt đối không xáo trộn câu hỏi giữa các Phần I, II, III. Các câu hỏi chùm đọc hiểu giữ nguyên cụm ngữ liệu.
4. **RULE-04 (Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu):** Sinh ma trận hoán vị 2 chiều phục vụ công tác thanh tra khảo thí và chấm thi tự động.

### 7.2. Danh Sách Chi Tiết Từng Nút & Phần Tử Trên Phân Hệ Trộn Đề

| STT | Tên nút / Phần tử | Bộ chọn DOM | Vị trí giao diện | Chức năng kỹ thuật & Hành vi | Điểm cuối API liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | Bộ chọn Đề thi gốc | `#shuffler-select-master-exam` | Thanh cấu hình đỉnh trái | Chọn đề thi gốc muốn hoán vị | `GET /api/v1/exams` |
| 2 | Bộ chọn Ma trận nguồn | `#shuffler-select-matrix` | Cạnh bộ chọn đề gốc | Chọn ma trận để sinh đề mới nếu cần | `GET /api/v1/matrices` |
| 3 | Nút ⚡ Sinh Đề Gốc | `#btn-shuffler-gen-matrix` | Cạnh bộ chọn ma trận | Rút đề thi gốc ngẫu nhiên từ ma trận đã chọn | `POST /api/v1/exams/generate` |
| 4 | Nút Đồng bộ từ Ma trận | `#btn-shuffler-sync-matrix` | Thanh tác vụ trên | Nạp lại cấu hình ma trận mới nhất từ tab Matrix | `GET /api/v1/matrix/{id}` |
| 5 | Checkbox Loại trừ 30 ngày | `#shuffler-exclude-30d` | Thanh tùy chọn | Loại bỏ các câu hỏi đã xuất hiện trong đề thi 30 ngày qua | `POST /api/v1/exams/generate` |
| 6 | Nút 🔀 Trộn Đề An Toàn | `#btn-trigger-shuffle` | Góc phải thanh điều khiển | Khởi chạy thuật toán hoán vị 4 mã đề (101, 102, 103, 104) | `POST /api/v1/exams/{id}/shuffle` |
| 7 | Tab Mã đề 101, 102, 103, 104 | `.variant-tab-btn` | Dải tab xem trước mã đề | Chuyển đổi xem nội dung và thứ tự câu hỏi từng mã đề | Không gọi API |
| 8 | Nút Thay thế câu hỏi Split-View | `button[onclick*="openSwapQuestionModal"]` | Trên từng câu hỏi ở tab đề gốc | Mở modal tìm câu hỏi tương đương thay thế | `POST /api/v1/exams/{id}/items/{item_id}/swap` |
| 9 | Nút Tải Đề thi PDF | `button[onclick*="downloadVariantPdf"]` | Thanh xuất bản | Tải tệp PDF của mã đề đang hiển thị | `GET /api/v1/exams/{id}/export-pdf` |
| 10 | Nút Tải Hướng dẫn giải PDF | `button[onclick*="downloadSolutionPdf"]`| Thanh xuất bản | Tải tệp hướng dẫn giải chi tiết chuẩn LaTeX | `GET /api/v1/exams/{id}/export-pdf?with_solution=true` |
| 11 | Nút Tải Trọn Bộ Gói ZIP | `#btn-download-full-zip` | Nút xuất bản chính (màu chàm) | Đóng gói toàn bộ 4 đề thi, đáp án, và phiếu OMR sang tệp `.zip` | `GET /api/v1/exams/{id}/export-zip` |
| 12 | Nút Phân tích Điểm số CTT | `button[onclick*="submitExamAnalytics"]` | Khung Trắc lượng học CTT | Tính toán độ khó $p$ và độ phân biệt $D$ từ danh sách điểm | `POST /api/v1/exams/{id}/analytics` |

---

## 8. HỆ THỐNG CÁC HỘP THOẠI & MODAL CHUYÊN DỤNG (9 MODALS)

Tất cả các modal được thiết kế chuẩn Apple Modal Sheet với lớp phủ nền làm mờ `backdrop-blur-xs` và đóng gói độc lập.

### 8.1. Modal Xác Thực & Phân Quyền (`#auth-modal`)

![Modal Đăng Nhập](screenshots/06_modal_auth_login.png)
![Modal Đăng Ký](screenshots/06b_modal_auth_register.png)

- **Mục đích:** Đăng nhập và đăng ký tài khoản giáo viên với JWT Token hoặc OAuth (Google, GitHub).
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Nằm góc phải trên, gọi `app.auth.closeAuthModal()`.
  2. Tab Đăng nhập (`#auth-tab-login`): Kích hoạt giao diện đăng nhập.
  3. Tab Đăng ký (`#auth-tab-register`): Kích hoạt giao diện đăng ký tài khoản mới.
  4. Ô Họ và tên (`#auth-input-fullname`): Chỉ hiển thị ở tab Đăng ký.
  5. Ô Địa chỉ Email (`#auth-input-email`): Nhập email tài khoản.
  6. Ô Mật khẩu (`#auth-input-password`): Nhập mật khẩu bảo mật.
  7. Nút Hành Động Chính (`#auth-submit-btn`): Gửi yêu cầu đăng nhập hoặc đăng ký tới API `POST /api/v1/auth/login` hoặc `POST /api/v1/auth/register`.
  8. Nút Đăng nhập qua Google: Kích hoạt luồng OAuth `POST /api/v1/auth/oauth/google`.
  9. Nút Đăng nhập qua GitHub: Kích hoạt luồng OAuth `POST /api/v1/auth/oauth/github`.

---

### 8.2. Modal Nạp Đề Thi Số Hóa AI (`#question-import-modal`)

![Modal Nạp Đề Thi AI](screenshots/07_modal_question_import.png)

- **Mục đích:** Nạp nhanh danh sách câu hỏi dạng văn bản thô hoặc mã nguồn LaTeX vào Ngân hàng câu hỏi.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc phải trên.
  2. Khung nhập mã nguồn (`#import-latex-textarea`): Textarea chứa mã nguồn `\begin{ex} ... \end{ex}`.
  3. Nút Hủy: Đóng modal và hủy thao tác.
  4. Nút Tiến hành Nhập vào Ngân hàng: Gọi hàm `app.submitImportQuestions()`, kích hoạt API `POST /api/v1/questions/import`.

---

### 8.3. Modal Thêm Câu Hỏi Thủ Công (`#question-create-modal`)

![Modal Thêm Câu Hỏi Thủ Công](screenshots/08_modal_question_create.png)

- **Mục đích:** Cho phép giáo viên biên soạn câu hỏi mới trực tiếp vào ngân hàng theo chuẩn Thông tư 32.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc trên bên phải.
  2. Bộ chọn Thể thức câu hỏi (`#q-create-format`): Trắc nghiệm 4 lựa chọn (Phần I), Đúng/Sai (Phần II), Trả lời ngắn (Phần III), Tự luận.
  3. Bộ chọn Cấp độ nhận thức (`#q-create-cognitive`): Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao.
  4. Ô nhập Nội dung câu hỏi (`#q-create-stem`): Textarea hỗ trợ nhập công thức KaTeX `$ ... $`.
  5. Khu vực Phương án lựa chọn / Ý Đúng-Sai: Sinh động tương ứng với thể thức đã chọn.
  6. Ô nhập Hướng dẫn giải chi tiết (`#q-create-explanation`): Nhập lời giải từng bước.
  7. Nút Lưu Vào Ngân Hàng: Kích hoạt API `POST /api/v1/questions`.

---

### 8.4. Modal Xem Chi Tiết Câu Hỏi KaTeX (`#question-detail-modal`)

![Modal Chi Tiết Câu Hỏi](screenshots/09_modal_question_detail.png)

- **Mục đích:** Hiển thị toàn văn câu hỏi với công thức toán học sắc nét, các phương án đáp án, lời giải và thẻ siêu dữ liệu.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc trên bên phải.
  2. Thân hiển thị câu hỏi KaTeX: Render tự động các biểu thức toán học.
  3. Cụm thẻ siêu dữ liệu: Hiển thị Thể thức, Cấp độ nhận thức, Mã YCCĐ Thông tư 32.
  4. Nút Xóa câu hỏi (`#q-detail-btn-delete`): Xóa câu hỏi khỏi ngân hàng (`DELETE /api/v1/questions/{id}`).
  5. Nút Chỉnh sửa (`#q-detail-btn-edit`): Chuyển sang Modal Chỉnh sửa HITL Review (`PUT /api/v1/questions/{id}`).
  6. Nút Đóng chân trang: Thoát khỏi chế độ xem chi tiết.

---

### 8.5. Modal Chỉnh Sửa Câu Hỏi HITL Review (`#question-editor-modal`)

![Modal Chỉnh Sửa HITL](screenshots/10_modal_question_editor.png)

- **Mục đích:** Môi trường Human-in-the-Loop cho phép giáo viên tinh chỉnh từng ký tự, công thức KaTeX, đổi đáp án đúng và cập nhật YCCĐ.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc trên bên phải.
  2. Bộ chọn Định dạng (`#q-edit-format`): Cập nhật thể thức khảo thí.
  3. Bộ chọn Mức độ nhận thức (`#q-edit-cognitive`): Cập nhật mức độ Bloom.
  4. Bộ chọn YCCĐ (`#q-edit-yccd`): Gán lại mã YCCĐ chuẩn Thông tư 32.
  5. Thanh công cụ ký hiệu toán học nhanh: Các nút chèn nhanh phân số `\dfrac{a}{b}`, căn bậc hai `\sqrt{x}`, số mũ `x^2`, tích phân `\int_a^b`.
  6. Ô biên tập thân câu hỏi (`#q-edit-stem`): Textarea có tính năng xem trước KaTeX thời gian thực.
  7. Khung xem trước KaTeX thời gian thực (`#q-edit-stem-preview`): Tự động render khi gõ.
  8. Cụm chỉnh sửa 4 phương án lựa chọn: Bao gồm ô chọn đáp án đúng và ô sửa nội dung từng phương án.
  9. Ô biên tập lời giải (`#q-edit-explanation`): Textarea kèm khung xem trước.
  10. Nút Lưu Thay Đổi: Gửi dữ liệu cập nhật tới API `PUT /api/v1/questions/{id}`.

---

### 8.6. Modal Thay Thế Câu Hỏi Split-View (`#swap-question-modal`)

![Modal Thay Thế Câu Hỏi](screenshots/11_modal_swap_question.png)

- **Mục đích:** Hỗ trợ kiểm định và thay thế câu hỏi trong đề thi bằng câu hỏi tương đương từ ngân hàng hoặc AI tạo mới.
- **Các phần tử tương tác:**
  1. Nút Đóng: Góc trên bên phải.
  2. Khung đối chiếu song song: Bên trái hiển thị câu hỏi hiện tại, bên phải hiển thị câu hỏi ứng viên thay thế.
  3. Nút Chọn câu này để thay thế: Gửi yêu cầu thay thế tới API `POST /api/v1/exams/{master_id}/items/{item_id}/swap`.
  4. Nút Đóng chân trang: Hủy bỏ thay thế.

---

### 8.7. Modal Biên Tập Nhanh Công Thức LaTeX (`#latex-editor-modal`)

![Modal Biên Tập LaTeX](screenshots/12_modal_latex_editor.png)

- **Mục đích:** Cung cấp bàn phím ảo toán học để giáo viên nhập nhanh các công thức toán phức tạp.
- **Các phần tử tương tác:**
  1. Nút Đóng: Góc trên bên phải.
  2. Thanh nút ký hiệu toán học: 12 nút bấm chèn nhanh các cấu trúc LaTeX thông dụng (`\dfrac`, `\sqrt`, `\int`, `\vec`, `\alpha`, `\beta`, `\infty`, `\le`, `\ge`).
  3. Ô nhập mã LaTeX (`#modal-latex-input`): Nhập trực tiếp mã nguồn toán.
  4. Khung xem trước KaTeX thời gian thực (`#modal-latex-preview-box`): Hiển thị kết quả trực quan ngay dưới ô nhập.
  5. Nút Chèn Công Thức: Điền công thức vào vị trí con trỏ của trường đang chỉnh sửa.

---

### 8.8. Modal Cảnh Báo Trùng Lặp AI Vector (`#duplicate-warning-modal`)

![Modal Cảnh Báo Trùng Lặp](screenshots/13_modal_duplicate_warning.png)

- **Mục đích:** Cảnh báo tự động khi thuật toán pgvector phát hiện câu hỏi mới nạp có độ tương đồng Cosine Similarity $\ge 80\%$ với câu hỏi đã có.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc trên bên phải.
  2. Thẻ hiển thị câu hỏi mới: Hiển thị nội dung câu hỏi đang nạp.
  3. Thẻ hiển thị câu hỏi đã có trong kho: Hiển thị nội dung câu hỏi trùng lặp trong cơ sở dữ liệu.
  4. Huy hiệu tỷ lệ tương đồng: Cảnh báo mức độ trùng lặp (ví dụ: `92.4%`).
  5. Nút Hủy bỏ lưu: Từ chối nạp câu hỏi trùng để giữ sạch ngân hàng đề.
  6. Nút Vẫn lưu (Xác nhận là biến thể): Chấp nhận ghi đè lưu câu hỏi dưới dạng biến thể độc lập.

---

### 8.9. Modal Thêm Dòng Ma Trận Đề Thi (`#add-matrix-row-modal`)

![Modal Thêm Dòng Ma Trận](screenshots/14_modal_add_matrix_row.png)

- **Mục đích:** Bổ sung một hàng chỉ tiêu năng lực mới vào bảng ma trận đề thi.
- **Các phần tử tương tác:**
  1. Nút Đóng (✕): Góc trên bên phải.
  2. Bộ chọn Mạch nội dung (`#modal-matrix-strand`): Số & Đại số, Hình học, Thống kê & Xác suất.
  3. Ô nhập Mã YCCĐ (`#modal-matrix-yccd`): Điền mã chuẩn hóa (ví dụ: `TOAN12.GT.05`).
  4. Ô nhập Dạng câu hỏi (`#modal-matrix-archetype`): Điền tên dạng toán.
  5. Bộ chọn Thể thức thi (`#modal-matrix-format`): Trắc nghiệm 4 lựa chọn, Đúng/Sai, Trả lời ngắn.
  6. Các ô nhập số lượng cho từng mức độ nhận thức:
     - Ô Nhận biết (`#modal-matrix-biet`).
     - Ô Thông hiểu (`#modal-matrix-hieu`).
     - Ô Vận dụng (`#modal-matrix-vandung`).
  7. Nút Thêm vào Ma trận: Đưa dòng cấu hình mới vào lưới ma trận và cập nhật tổng kết.

---

## 9. MÀN HÌNH TÀI LIỆU API BACKEND (SWAGGER & REDOC)

FastAPI tự động sinh tài liệu chuẩn OpenAPI 3.1 cho toàn bộ 74 endpoints.

![Swagger UI](screenshots/15_api_swagger_docs.png)
![ReDoc](screenshots/16_api_redoc.png)

- **Swagger UI (`/docs`):** Cho phép tương tác, chạy thử nghiệm trực tiếp từng API (Try it out) kèm token xác thực Bearer JWT.
- **ReDoc (`/redoc`):** Giao diện tài liệu chuyên sâu 3 cột, hiển thị chi tiết schemas, tham số, mã lỗi HTTP và ví dụ phản hồi JSON.

---

## 10. BẢN ĐỒ CHI TIẾT 74 ENDPOINTS REST API BACKEND

Dưới đây là bảng tổng mục 74 điểm cuối API backend, phân loại theo Router và liên kết với các thành phần frontend:

### 10.1. Nhóm API Xác Thực Người Dùng (Auth Router - 6 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Đăng ký tài khoản giáo viên mới | `auth.register` | Modal Xác Thực (Tab Đăng ký) |
| `POST` | `/api/v1/auth/login` | Đăng nhập tài khoản, cấp JWT token | `auth.login` | Modal Xác Thực (Tab Đăng nhập) |
| `GET` | `/api/v1/auth/me` | Lấy thông tin tài khoản hiện hành | `auth.get_current_user` | Khởi tạo Header (`app.auth.init`) |
| `POST` | `/api/v1/auth/logout` | Đăng xuất và hủy phiên làm việc | `auth.logout` | Menu Tài khoản giáo viên Header |
| `POST` | `/api/v1/auth/oauth/google` | Đăng nhập liên kết tài khoản Google | `auth.oauth_google` | Nút Google trong Modal Xác thực |
| `POST` | `/api/v1/auth/oauth/github` | Đăng nhập liên kết tài khoản GitHub | `auth.oauth_github` | Nút GitHub trong Modal Xác thực |

### 10.2. Nhóm API Soạn Đề & Biên Dịch LaTeX (Composer Router - 8 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/composer/compile` | Biên dịch toàn văn LaTeX sang PDF | `composer.compile_latex` | Nút BIÊN DỊCH (`#composer-compile-btn`) |
| `POST` | `/api/v1/composer/compile-partial` | Biên dịch một trích đoạn câu hỏi | `composer.compile_partial` | Live Preview từng câu hỏi |
| `GET` | `/api/v1/composer/pdf/{doc_id}.pdf`| Stream tệp PDF phục vụ xem trước | `composer.stream_pdf` | PDF.js Viewer Cột phải |
| `POST` | `/api/v1/composer/chat` | Trợ lý AI Copilot gợi ý sửa đề & TikZ | `composer.copilot_chat` | Hộp Trợ lý AI & Thanh Prompt nổi |
| `GET` | `/api/v1/composer/templates` | Lấy danh mục 11 mẫu đề thi chuẩn | `composer.get_templates` | Dropdown THÊM trên Header Editor |
| `POST` | `/api/v1/composer/export` | Xuất mã nguồn standalone `.tex` | `composer.export_tex` | Menu XUẤT FILE -> Tải mã nguồn |
| `GET` | `/api/v1/composer/export` | Tải mã nguồn `.tex` qua GET | `composer.export_tex_get` | Liên kết tải tệp trực tiếp |
| `POST` | `/api/v1/composer/save-to-bank` | Bóc tách LaTeX lưu vào Ngân hàng | `composer.save_to_bank` | Nút LƯU NGÂN HÀNG đáy Editor |

### 10.3. Nhóm API Số Hóa & Trích Xuất AI 2-Pass (Digitize Router - 11 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/digitize/upload` | Tiếp nhận tài liệu đề thi (.pdf/.docx/.png) | `digitize.upload_document` | Thẻ Số Hóa Đề Thi / Modal Nạp Tệp |
| `POST` | `/api/v1/digitize/upload-test` | Endpoint kiểm thử tải lên | `digitize.upload_test` | Kiểm thử tự động |
| `POST` | `/api/v1/upload` | Upload đề thi trực tiếp | `main.direct_upload_endpoint`| API tích hợp bên thứ ba |
| `GET` | `/api/v1/digitize/jobs/{job_id}` | Kiểm tra trạng thái tiến trình bóc tách | `digitize.get_job_status` | Vòng lặp thăm dò tiến độ HITL |
| `GET` | `/api/v1/digitize/jobs/{job_id}/preview` | Xem trước ảnh phân đoạn layout trang | `digitize.preview_job` | Khung nhìn văn bản gốc HITL |
| `GET` | `/api/v1/digitize/jobs/{job_id}/files/{filename}` | Tải tệp tạm phục vụ bóc tách | `digitize.serve_job_file` | Khung đối chiếu tài liệu gốc |
| `GET` | `/api/v1/digitize/assets/{filename}` | Lấy ảnh hình vẽ/đồ thị đã crop WebP | `digitize.get_cropped_asset` | Thẻ câu hỏi có chứa hình minh họa |
| `POST` | `/api/v1/digitize/render-tikz` | Biên dịch trích đoạn TikZ sang SVG | `digitize.render_tikz` | Trình biên soạn hình học TikZ |
| `POST` | `/api/v1/digitize/jobs/{job_id}/commit` | Lưu các câu hỏi đã duyệt vào Ngân hàng | `digitize.commit_job` | Nút Phê duyệt Đề thi HITL |
| `POST` | `/api/v1/digitize/export-pdf` | Xuất bản đề thi vừa số hóa sang PDF | `digitize.export_pdf` | Nút Xuất PDF sau số hóa |
| `GET` | `/api/v1/digitize/jobs/{job_id}/export-pdf` | Tải PDF của tiến trình số hóa | `digitize.export_job_pdf` | Tải về kết quả số hóa |

### 10.4. Nhóm API Quản Lý & Hoán Vị Đề Thi (Exams Router - 11 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/exams` | Lấy danh sách các đề thi gốc đã tạo | `exams.list_master_exams` | Dropdown chọn đề gốc tại Shuffler |
| `GET` | `/api/v1/exams/{master_id}` | Lấy chi tiết đề gốc và các biến thể | `exams.get_master_exam` | Tab xem trước mã đề hoán vị |
| `POST` | `/api/v1/exams/generate` | Sinh đề gốc tự động từ ma trận | `exams.generate_master_exam` | Nút Sinh Đề Gốc tại Matrix & Shuffler |
| `POST` | `/api/v1/exams/shuffle` | Hoán vị đề thi trực tiếp | `exams.shuffle_direct` | Động cơ hoán vị nhanh |
| `POST` | `/api/v1/exams/{master_id}/shuffle` | Sinh các mã đề hoán vị (101 - 104) | `exams.shuffle_master_exam`| Nút 🔀 Trộn Đề An Toàn |
| `GET` | `/api/v1/exams/{master_id}/key-matrix` | Lấy bảng ma trận đáp án đối chiếu | `exams.get_key_matrix` | Bảng ma trận đáp án tổng hợp |
| `GET` | `/api/v1/exams/{master_id}/items/{item_id}/replacement-candidates` | Tìm câu hỏi tương đương thay thế | `exams.get_replacements` | Modal Thay Thế Câu Hỏi Split-View |
| `POST` | `/api/v1/exams/{master_id}/items/{item_id}/swap` | Hoán đổi câu hỏi trong đề gốc | `exams.swap_item` | Nút Xác nhận thay thế trong Modal |
| `GET` | `/api/v1/exams/{master_id}/export-pdf` | Xuất bản đề thi từng mã đề sang PDF | `exams.export_pdf` | Nút Tải Đề thi PDF |
| `GET` | `/api/v1/exams/{master_id}/export-zip` | Xuất trọn bộ ZIP ấn phẩm khảo thí | `exams.export_zip` | Nút Tải Trọn Bộ Gói ZIP |
| `POST` | `/api/v1/exams/{master_id}/analytics` | Phân tích trắc lượng học CTT (p, D) | `exams.analyze_exam` | Khung phân tích điểm số CTT |

### 10.5. Nhóm API Thiết Lập Ma Trận Đề Thi (Matrices Router - 18 Endpoints)

Hệ thống hỗ trợ cả định dạng số nhiều (`/matrices`) và số ít (`/matrix`) để tương thích tối đa với các phiên bản client:

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/matrices` & `/api/v1/matrix` | Lấy danh sách ma trận đề thi | `matrix.list_matrices` | Dropdown chọn ma trận |
| `POST` | `/api/v1/matrices` & `/api/v1/matrix` | Tạo mới cấu hình ma trận đề thi | `matrix.create_matrix` | Nút Lưu Bản Thảo tại tab Matrix |
| `GET` | `/api/v1/matrices/{id}` & `/api/v1/matrix/{id}` | Lấy chi tiết cấu hình một ma trận | `matrix.get_matrix` | Mở ma trận để chỉnh sửa |
| `PUT` | `/api/v1/matrices/{id}` & `/api/v1/matrix/{id}` | Cập nhật cấu hình ma trận | `matrix.update_matrix` | Cập nhật chỉ tiêu số lượng các ô |
| `DELETE` | `/api/v1/matrices/{id}` & `/api/v1/matrix/{id}` | Xóa bỏ một ma trận khỏi hệ thống | `matrix.delete_matrix` | Nút Xóa ma trận |
| `GET` | `/api/v1/matrices/{id}/spec` & `.../matrix/{id}/spec` | Lấy thông số kỹ thuật lưới ma trận | `matrix.get_matrix_spec` | Nạp dữ liệu vào lưới 2D |
| `GET` | `/api/v1/matrices/bank-inventory` & `.../matrix/bank-inventory` | Lấy số liệu tồn kho câu hỏi | `matrix.get_bank_inventory` | Hiển thị tồn kho từng ô ma trận |
| `POST` | `/api/v1/matrices/check-availability` & `.../matrix/...` | Kiểm tra độ khả dụng câu hỏi | `matrix.check_availability` | Cảnh báo thiếu hụt thời gian thực |
| `POST` | `/api/v1/matrices/{id}/check-availability` & `...` | Kiểm tra khả dụng cho ma trận cụ thể | `matrix.check_matrix_avail` | Đánh giá tính khả thi trước khi sinh đề |

### 10.6. Nhóm API Ngân Hàng Câu Hỏi (Questions Router - 10 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/questions` | Truy vấn, tìm kiếm và phân trang câu hỏi | `questions.list_questions` | Danh sách câu hỏi tab Item Bank |
| `POST` | `/api/v1/questions` | Tạo mới câu hỏi thủ công | `questions.create_question` | Modal Thêm Câu Hỏi Thủ Công |
| `GET` | `/api/v1/questions/count` | Lấy tổng số lượng câu hỏi khả dụng | `questions.get_count` | Huy hiệu đếm câu hỏi trên Header |
| `GET` | `/api/v1/questions/{question_id}` | Lấy chi tiết toàn văn một câu hỏi | `questions.get_question` | Modal Xem Chi Tiết Câu Hỏi |
| `PUT` | `/api/v1/questions/{question_id}` | Cập nhật nội dung câu hỏi sau HITL | `questions.update_question` | Modal Chỉnh Sửa HITL Review |
| `DELETE` | `/api/v1/questions/{question_id}` | Xóa câu hỏi khỏi cơ sở dữ liệu | `questions.delete_question` | Nút Thùng Rác Đỏ trên từng câu hỏi |
| `POST` | `/api/v1/questions/check-duplicate` | Kiểm tra trùng lặp bằng Cosine Similarity | `questions.check_duplicate` | Modal Cảnh Báo Trùng Lặp AI |
| `POST` | `/api/v1/questions/auto-tag` | Gợi ý tự động mức độ Bloom và YCCĐ | `questions.auto_tag` | Tiến trình gán nhãn tự động |
| `POST` | `/api/v1/questions/import` | Nạp hàng loạt câu hỏi từ LaTeX/Text | `questions.import_questions` | Modal Nạp Đề Thi Số Hóa AI |
| `POST` | `/api/v1/questions/export` | Xuất toàn bộ ngân hàng sang file | `questions.export_questions` | Xuất dữ liệu sao lưu |

### 10.7. Nhóm API Cây Kiến Thức Thông Tư 32 (Taxonomy Router - 15 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/taxonomy/tree` | Lấy toàn bộ cây phân cấp 6 tầng lồng nhau | `taxonomy.get_tree` | Ngăn Cây Kiến Thức 6 Tầng |
| `GET` | `/api/v1/taxonomy/subjects` | Danh sách môn học (Toán, Lý, Hóa, Sinh) | `taxonomy.list_subjects` | Dropdown chọn Môn học |
| `POST` | `/api/v1/taxonomy/subjects` | Tạo môn học mới | `taxonomy.create_subject` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/grades` | Danh sách khối lớp (Lớp 10, 11, 12) | `taxonomy.list_grades` | Dropdown chọn Khối lớp |
| `POST` | `/api/v1/taxonomy/grades` | Tạo khối lớp mới | `taxonomy.create_grade` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/strands` | Danh sách mạch nội dung Thông tư 32 | `taxonomy.list_strands` | Bộ lọc Mạch nội dung |
| `POST` | `/api/v1/taxonomy/strands` | Tạo mạch nội dung mới | `taxonomy.create_strand` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/topics` | Danh sách chủ đề học tập | `taxonomy.list_topics` | Bộ lọc Chủ đề |
| `POST` | `/api/v1/taxonomy/topics` | Tạo chủ đề học tập mới | `taxonomy.create_topic` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/lessons` | Danh sách bài học | `taxonomy.list_lessons` | Bộ lọc Bài học |
| `POST` | `/api/v1/taxonomy/lessons` | Tạo bài học mới | `taxonomy.create_lesson` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/learning-outcomes` | Danh sách Yêu cầu cần đạt (YCCĐ) | `taxonomy.list_outcomes` | Bộ lọc mã YCCĐ |
| `POST` | `/api/v1/taxonomy/learning-outcomes` | Tạo mã YCCĐ mới | `taxonomy.create_outcome` | Quản trị danh mục |
| `GET` | `/api/v1/taxonomy/problem-archetypes`| Danh sách dạng bài tập chuyên đề | `taxonomy.list_archetypes` | Bộ lọc Dạng bài |
| `POST` | `/api/v1/taxonomy/problem-archetypes`| Tạo dạng bài tập chuyên đề mới | `taxonomy.create_archetype`| Quản trị danh mục |

### 10.8. Nhóm API Kiểm Tra Sức Khỏe & Gốc Hệ Thống (Health & Root - 3 Endpoints)

| Phương thức | Đường dẫn API | Tóm tắt chức năng | Hàm xử lý backend | Nơi gọi tại Frontend |
| :---: | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Kiểm tra tình trạng kết nối máy chủ | `main.health_check` | Giám sát hạ tầng |
| `GET` | `/api/v1/health` | Kiểm tra tình trạng máy chủ và chuẩn khảo thí | `main.health_check` | Giám sát tích hợp |
| `GET` | `/api` | Cung cấp thông tin phiên bản và URL tài liệu | `main.api_root` | Khám phá dịch vụ |

---

## 11. BẢNG MA TRẬN ÁNH XẠ NGUỒN GỐC (TRACEABILITY MATRIX)

Bảng đối chiếu khép kín giữa Nhu cầu Khảo thí, Giao diện người dùng, Tệp mã nguồn và Điểm cuối API:

| Phân hệ nghiệp vụ | Thành phần Giao diện (UI Element) | Tệp Frontend quản lý | Tệp Backend xử lý | Điểm cuối REST API |
| :--- | :--- | :--- | :--- | :--- |
| **Soạn thảo chuẩn** | Editor Dark Mode `#141824` | `frontend/static/app.js` | `backend/services/composer_service.py` | `POST /api/v1/composer/compile` |
| **Trợ lý AI Copilot**| Khung Chat Trợ lý AI Khảo thí | `frontend/static/app.js` | `backend/routers/composer.py` | `POST /api/v1/composer/chat` |
| **Bảo toàn Invariant**| Động cơ hoán vị 4 mã đề | `frontend/static/app.js` | `backend/services/shuffling_engine.py` | `POST /api/v1/exams/{id}/shuffle` |
| **Chống trùng lặp** | Cảnh báo trùng lặp $\ge 90\%$ | `frontend/index.html` | `backend/services/deduplication.py` | `POST /api/v1/questions/check-duplicate`|
| **Cây kiến thức TT32**| Bộ lọc phân cấp 6 tầng | `frontend/static/app.js` | `backend/routers/taxonomy.py` | `GET /api/v1/taxonomy/tree` |
| **Kiểm tra tồn kho** | Lưới ma trận 2D thời gian thực | `frontend/static/app.js` | `backend/routers/matrix.py` | `POST /api/v1/matrix/check-availability`|
| **Đóng gói ZIP** | Xuất trọn bộ ấn phẩm khảo thí | `frontend/static/app.js` | `backend/services/vector_pdf_exporter.py`| `GET /api/v1/exams/{id}/export-zip` |
| **Chấm thi OMR** | Chấm tự động phiếu trả lời | `frontend/static/app.js` | `backend/services/omr_grader.py` | `POST /api/v1/exams/{id}/analytics` |

---

## 12. TỔNG KẾT VẬN HÀNH & HƯỚNG DẪN KIỂM CHỨNG

1. **Khởi động hệ thống:**
   ```bash
   # Cách 1: Khởi động qua script quản lý tự động giải phóng port
   python start_server.py --host 127.0.0.1 --port 8000

   # Cách 2: Khởi động trực tiếp với Uvicorn
   uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```
2. **Kiểm tra sức khỏe hệ thống (Health Check):**
   ```bash
   curl -s http://127.0.0.1:8000/api/v1/health
   # Kết quả mong đợi: {"status":"healthy","service":"quesy-api","version":"2.0.0",...}
   ```
3. **Mở tài liệu API trực quan:**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`
4. **Kho ảnh minh chứng giao diện:** Toàn bộ 21 ảnh chụp màn hình độ phân giải cao được lưu trữ tại `docs/screenshots/`.
