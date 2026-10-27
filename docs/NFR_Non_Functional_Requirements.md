# TÀI LIỆU YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFR)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-NFR-01  
- **Phiên bản:** 3.3 (Hoàn thiện Toàn diện Ngân hàng Câu hỏi CRUD & Import/Export, Hệ thống Xác thực Auth JWT/OAuth & Động cơ Lưu Đề từ Soạn thảo vào Ngân hàng)  
- **Tiêu chuẩn áp dụng:** ISO/IEC 25010 (Software Product Quality Model)  
- **Mục tiêu kỹ thuật:** Thiết lập các tiêu chuẩn hiệu năng bóc tách AI, hệ thống xác thực an toàn (PBKDF2/SHA256, JWT HS256, OAuth 2.0), tốc độ trích xuất lưu đề từ Composer vào Ngân hàng (<= 1.5s), độ trễ truy vấn lọc ngân hàng câu hỏi 6 tầng (P95 <= 150ms), tính năng soạn đề tinh gọn không preamble với động cơ tiêm ngầm Canonical Preamble Injection (ex_test v3.3, tikz, tkz-tab, tcolorbox, A4), tốc độ biên dịch đồ thị vector SVG, độ sắc nét vector WMF của công thức toán, khả năng mở sửa MathType 2 chiều không lỗi OLE activation, độ tương phản chuẩn WCAG 2.1 AA cho Dark Mode, độ trễ tương tác optimistic prompt dispatch, kéo thả resizer/splitter 60 FPS mượt mà, độ tin cậy của thuật toán thay thế dòng mờ, tính toàn vẹn của khối mã trong chat bubble (không nuốt code), quy tắc kiểm soát quản trị Git Workflow (không tự động tạo PR), độ bảo mật dữ liệu đề thi và tính sẵn sàng cao.
- **Ngày phát hành:** 2026-10-24

---

## 1. TỔNG QUAN VỀ TIÊU CHUẨN CHẤT LƯỢNG

Tài liệu này xác định các tiêu chuẩn kỹ thuật phi chức năng (NFR) cho hệ thống **Quesy** nhằm đảm bảo sản phẩm vận hành với hiệu năng cao, độ bảo mật tối đa đối với dữ liệu đề thi, tính sẵn sàng liên tục trong các kỳ thi cao điểm, và trải nghiệm người dùng tối ưu.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MÔ HÌNH CHẤT LƯỢNG HỆ THỐNG (ISO 25010)             │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Performance Efficiency (Hiệu năng & Độ trễ)                         │
│ 2. Security & Exam Confidentiality (Bảo mật & Tính Cơ mật Đề thi)       │
│ 3. Reliability & Availability (Độ tin cậy & Tính Sẵn sàng)             │
│ 4. Scalability & Capacity (Khả năng Mở rộng & Sức chứa)                │
│ 5. Usability & Accessibility (Khả năng Sử dụng & Trải nghiệm)          │
│ 6. Maintainability & Portability (Khả năng Bảo trì & Chuyển giao)     │
│ 7. Compliance & Data Protection (Tuân thủ Pháp lý & Bảo vệ Dữ liệu)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. HIỆU NĂNG & ĐỘ TRỄ (PERFORMANCE EFFICIENCY)

### 2.1. Tốc độ Xử lý Bóc tách AI (AI OCR & Parsing Latency)
- **NFR-PERF-01 (Thời gian bóc tách trang văn bản):** Thời gian xử lý trung bình của tiến trình AI cho một trang đề thi chuẩn (chứa văn bản và công thức toán học) không được vượt quá **5 giây/trang**.
- **NFR-PERF-02 (Thời gian bóc tách toàn bộ đề thi):** Một đề thi hoàn chỉnh 50 câu (khoảng 6-8 trang) chứa hình vẽ và công thức phức tạp phải hoàn thành bóc tách trong vòng **$\le 45$ giây** (bản in rõ) và **$\le 90$ giây** (bản scan/chụp).
- **NFR-PERF-03 (Thời gian Auto-crop hình ảnh):** Quá trình phát hiện Bounding Box, cắt và nén ảnh hình học/đồ thị định dạng WebP không được vượt quá **1.5 giây/ảnh**.
- **NFR-PERF-04 (Thời gian gợi ý AI Auto-tagging YCCĐ):** Tiến trình phân tích ngữ nghĩa thân câu hỏi và đưa ra gợi ý mã Yêu cầu cần đạt (YCCĐ) theo Thông tư 32 không quá **1.0 giây/câu**.

### 2.2. Tốc độ Sinh Đề & Trộn Mã đề (Exam Engine Performance)
- **NFR-PERF-05 (Thời gian sinh đề gốc từ ma trận YCCĐ):** Thuật toán tìm kiếm và lấy câu hỏi thỏa mãn ma trận (Constraint Solver) cho đề 50 câu phải hoàn thành trong vòng **$< 3$ giây** trên kho dữ liệu 100.000 câu hỏi.
- **NFR-PERF-06 (Thời gian trộn đề và sinh 4 mã đề hoán vị):** Quá trình chạy thuật toán hoán vị an toàn, kiểm tra cờ neo vị trí (Option Anchor) và xuất ra ma trận ánh xạ đáp án cho 4 mã đề phải hoàn thành trong **$< 2$ giây**.

### 2.3. Hiệu năng Giao diện, Render Công thức & Xuất bản (Frontend & Engine Performance)
- **NFR-PERF-07 (Tốc độ render công thức KaTeX):** Trên màn hình Studio Hậu kiểm chứa 50 câu hỏi đầy đủ công thức toán, thời gian render ban đầu (First Contentful Paint) không quá **1.2 giây**; tốc độ khung hình khi cuộn trang (Scrolling Frame Rate) phải duy trì ổn định $\ge 60$ FPS.
- **NFR-PERF-08 (Độ trễ Đồng bộ Cuộn trang - Synchronized Scrolling):** Khi người dùng chọn câu hỏi bên phải, khung xem tài liệu gốc bên trái cuộn đến vị trí tương ứng với độ trễ phản hồi **$< 100$ ms**.
- **NFR-PERF-09 (Độ trễ API thông thường):** Các API truy vấn tìm kiếm câu hỏi theo YCCĐ, lấy danh mục cây bài học/dạng bài có độ trễ $P95 < 200$ ms.
- **NFR-PERF-10 (Tốc độ Xử lý MathJax Persistent Worker):** Dịch vụ daemon Node.js MathJax chuyển đổi TeX sang MathML / SVG / Vector WMF phải hoàn thành trong **$< 20$ ms/công thức**, bảo đảm không tạo điểm nghẽn (bottleneck) trong tiến trình xuất bản.
- **NFR-PERF-11 (Thời gian Xuất bản Gói Đề thi ZIP Khảo thí):** Quá trình đóng gói toàn bộ 4 mã đề thi Word kèm bảng đáp án và hướng dẫn giải (khoảng 9 file DOCX) phải hoàn thành trong vòng **$< 10$ giây** (ngân sách NFR).
- **NFR-PERF-15 (Tốc độ Bóc Tách & Lưu Đề từ Composer Vào Ngân Hàng):** Tiến trình phân tích cú pháp LaTeX, trích xuất 22 câu hỏi (đầy đủ 3 thể thức QĐ 764, TikZ, bảng biến thiên, lời giải), chạy tự động gán nhãn AI `suggest_auto_tagging` và lưu vào CSDL hoàn thành trong vòng $\le 1.5$ giây.
- **NFR-PERF-16 (Độ Trễ Truy Vấn Lọc Cây Kiến Thức & Tìm Kiếm Ngân Hàng):** Thao tác lọc câu hỏi theo cây 6 tầng TT 32 kết hợp bộ lọc thứ cấp (thể thức, mức độ, dạng bài) và tìm kiếm từ khóa với chỉ mục Index tối ưu đạt độ trễ $P95 \le 150\text{ ms}$ trên tập dữ liệu $\ge 10.000$ câu hỏi.
- **NFR-QUAL-01 (Độ Sắc nét Tuyệt đối của Công thức MathType - 100% Vector WMF):** Công thức toán trong file Word phải đạt chuẩn Vector WMF (`image/x-wmf`) với APM header, đạt tỷ lệ 100% vector thuần (loại bỏ hoàn toàn fallback raster DIB), giữ nguyên độ nét vector tuyệt đối (zero blur) ở mọi mức thu phóng màn hình và in ấn.
- **NFR-COMP-01 (Tính Biên tập Hai chiều của MathType OLE - DSMT7 Stream):** Đối tượng OLE nhúng trong file `.docx` bắt buộc phải chứa luồng nhị phân DSMT7 chuẩn với bản ghi `TeX Input Language`, chuẩn hóa embellishment cho toán tử vectơ (`\vec`, `\overrightarrow`), kích hoạt và mở mượt mà trong trình soạn thảo MathType 7 thông qua thao tác double-click của người dùng mà không phát sinh bất kỳ lỗi COM/OLE hay popup cảnh báo thiếu ứng dụng server nào.
- **NFR-COMP-02 (Kiến trúc Biên dịch LaTeX Tectonic Độc lập Môi trường):** Phân hệ Soạn đề LaTeX hỗ trợ biên dịch đa tầng (Hybrid Multi-tier Compiler Architecture):
  1. *Microservice Tectonic Docker:* Độc lập trên container Docker (được triển khai trên host ARM/Armbian tại cổng 8090), sử dụng engine Tectonic XeTeX tự động nạp packages CTAN theo nhu cầu, cache gói dữ liệu liên hoàn, tốc độ biên dịch $\le 10$s cho đề thi tiếng Việt đầy đủ bảng biến thiên `tkz-tab` và đồ thị TikZ. Hỗ trợ tham số cấu hình timeout động `timeout_s` từ 60s đến 240s thích ứng theo quy mô đề thi.
  2. *Local Native Tectonic:* Tự động kích hoạt khi có binary `tectonic` trong PATH hệ thống với timeout động thích ứng $\text{calc\_timeout}$.
  3. *Headless Chromium Fallback:* Cơ chế dự phòng nội tại với Chromium + MathJax 4.0 + TikZ Vector SVG + CMU Serif typography bảo đảm hệ thống luôn xuất bản được PDF chất lượng cao ngay cả khi ngắt kết nối mạng ngoài.
- **NFR-PERF-14 (Ngân Sách Thời Gian & Cơ Chế Dynamic Adaptive Compilation Timeout Cho Đề Thi Quy Mô Lớn):**
  1. *Khả năng chịu tải tài liệu lớn:* Hệ thống đảm bảo biên dịch thành công 100% không phát sinh lỗi HTTP 504 Timeout đối với các đề thi chuẩn THPT Quốc gia quy mô đầy đủ ($\sim 24.000$ ký tự, $\ge 10$ hình TikZ/tkz-tab, 6 trang PDF vector A4).
  2. *Công thức timeout động:* $\text{calc\_timeout} = \max(60, \min(240, 45 + 10 \times \text{tikz\_count} + \lfloor \text{code\_len} / 250 
floor))$.
  3. *Ngân sách socket mạng:* Client thiết lập timeout cho `urlopen` là $\text{calc\_timeout} + 15$ giây để triệt tiêu hiện tượng ngắt kết nối trước server do trễ mạng (zero false network drop).
  4. *Tối ưu hóa thời gian biên dịch:* Khuyến nghị tham số `samples=50` (hoặc `samples=60`) cho các đường cong TikZ giúp rút ngắn thời gian biên dịch XeTeX xuống $\le 35$ giây trên hạ tầng máy chủ ARM mà vẫn đảm bảo độ mịn màng đạt chuẩn $1200\text{ DPI}$ vector A4.
- **NFR-PERF-12 (Tốc độ Phản hồi Gửi Prompt Trợ lý AI - Optimistic Dispatch & Instant Input Wipe):** Khi người dùng nhấn Enter hoặc bấm gửi, hệ thống đồng thời thực hiện xóa sạch lạc quan (Optimistic Input Wipe) cả 2 trường nhập liệu trong vòng $\le 0\text{ms}$ đồng bộ; giao diện phản hồi optimistic cập nhật bong bóng chat trong vòng $\le 16$ ms (1 frame); timeout Backend kết nối nhà cung cấp AI ngoài khống chế $\le 15$s kèm cơ chế fallback quy tắc thông minh tức thì, triệt tiêu hoàn toàn hiện tượng text chat cũ còn lưu kẹt trong ô nhập.
- **NFR-PERF-13 (Hiệu Năng Bóc Tách Đa Khối Diff & Áp Dụng Hàng Loạt - Multi-Diff Engine Budget):**
  1. *Thời gian bóc tách đa khối diff (`extract_all_diffs_from_text`):* Quét toàn bộ nội dung phản hồi, đối chiếu mã nguồn hiện tại và trả về danh sách `diffs` trong $\le 10$ ms.
  2. *Thời gian chuyển đổi bước duyệt tuần tự (1/N Stepper):* $\le 16$ ms (1 frame 60 FPS) cho thao tác cuộn màn hình, cập nhật huy hiệu và bôi đen vùng chọn dòng mới.
  3. *Thời gian thực thi [Áp dụng tất cả] (Bulk Apply All):* Áp dụng toàn bộ $N$ khối diff ($N \le 15$) vào mã nguồn trong $\le 50$ ms với cơ chế gom nhóm cập nhật DOM một lần duy nhất (Single-pass DOM update) và debounce biên dịch an toàn.
- **NFR-UX-01 (Độ Tương phản Màu sắc Giao diện Dark Mode - WCAG 2.1 AA):** Tỷ lệ tương phản giữa chữ và nền ô chat (`#composer-compact-input` và `#composer-chat-input`) bắt buộc đạt $\ge 7:1$ (sử dụng văn bản trắng sáng `#f8fafc` trên nền tối `#1c1c1f` / `#141824`, con trỏ caret màu xanh Apple `#38bdf8`), loại bỏ hoàn toàn lỗi chữ đen chìm trên nền tối.
- **NFR-UX-02 (Tốc độ & Độ Mượt mà Khi Kéo Thả Resizer & Splitter - 60 FPS Smooth Dragging):** Thao tác kéo thả thay đổi kích thước Splitter ngang (2 cột Editor/Preview qua `#composer-split-resizer`) và Vertical Resizer (Box Trợ lý Soạn thảo qua thanh pill hợp nhất `#composer-ai-resize-handle`) bắt buộc đạt tốc độ dựng hình 60 FPS ($\le 16.6$ ms/frame) trên trình duyệt, triệt tiêu hoàn toàn hiện tượng lag, giật khung hình (zero jank). Tự động ngắt transition CSS trong quá trình kéo và khôi phục mượt mà khi kết thúc thao tác; áp dụng Pointer Shield (`pointer-events: none`) trên canvas PDF để tránh gián đoạn con trỏ chuột.
- **NFR-UX-04 (Công Thái Học Thanh Phân Tách Ngang Chuẩn Apple HIG - Spacing & Visual Isolation):** Thanh phân tách `#composer-split-resizer` bắt buộc có độ rộng rãnh công thái học $\ge 14\text{px}$ (`w-3.5` / `w-4`), tích hợp khoảng cách đệm an toàn `mx-1` / `mx-1.5` so với viền bo góc của Cột Soạn thảo và Cột Live Preview. Trục viên thuốc và quầng highlight hover phải giữ khoảng cách thở tối thiểu $6\text{px} - 8\text{px}$ so với viền card, tuyệt đối không được đè sát hay chồng lấn lên viền card bên cạnh.
- **NFR-UX-03 (Trải Nghiệm Zoom & Bố Cục Xem Trước PDF - Zero Drift & No Right-Margin Clipping):**
  1. *Độ ổn định điểm neo zoom (Zero Drift Invariant):* Thuật toán zoom-to-point đảm bảo độ trôi dạt điểm neo dưới con trỏ chuột (Cursor Anchor) hoặc trọng tâm màn hình (Center Anchor) không vượt quá $\pm 2\text{px}$ sau mỗi bước zoom, triệt tiêu $100\%$ hiện tượng giật màn hình hoặc nhảy về góc trên cùng bên trái $(0, 0)$.
  2. *Toàn vẹn hiển thị không xén nét (No Right-Margin Clipping):* Vùng cuộn `#composer-pdf-scroll-container` (`overflow-x-auto`) đảm bảo $100\%$ nội dung tài liệu luôn tiếp cận được qua cuộn ngang ở mọi mức zoom $[40\%, 250\%]$; cơ chế Auto Fit-to-Width tự động thích ứng với chiều rộng cột preview trong thời gian thực khi kéo splitter, ngăn chặn hoàn toàn việc nội dung bị che khuất hoặc tràn lề ngoài ý muốn.
- **NFR-REL-03 (Độ Tin cậy của Động cơ Thay thế Diff - Zero Drift Fuzzy Matcher):** Tỷ lệ áp dụng diff sửa đổi thành công qua thuật toán so khớp mờ 6 tầng đạt $\ge 99.5\%$, triệt tiêu lỗi false-negative "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại" do khoảng trắng, ngắt dòng hoặc thụt lề; hỗ trợ áp dụng đồng thời chuỗi nhiều khối diff mà không làm lệch vị trí các khối kế tiếp.
- **NFR-REL-05 (Bảo Toàn Tùy Biến Giao Diện & Độc Lập Phiên Chat Trong Local Storage):** Cấu hình tỷ lệ chia cột (`quesy_composer_split_ratio`), độ cao tùy chỉnh box trợ lý (`quesy_composer_ai_height`), và danh sách phiên chat cũ (`quesy_composer_chat_sessions`) được lưu trữ độc lập và bảo toàn $100\%$ qua các lần tải lại trang (F5) mà không gây rò rỉ hay ghi đè lẫn nhau.

---

## 3. BẢO MẬT & TÍNH CƠ MẬT ĐỀ THI (SECURITY & CONFIDENTIALITY)

### 3.1. Cơ mật Đề thi Trước giờ G (Exam Secrecy & Data Privacy)
- **NFR-SEC-01 (Mã hóa dữ liệu lưu trữ - Encryption at Rest):**
  - Mọi nội dung câu hỏi, đề thi gốc và mã đề hoán vị ở trạng thái "Chưa công bố" (Confidential) phải được mã hóa ở cấp độ cơ sở dữ liệu bằng thuật toán **AES-256**.
  - Các khóa giải mã (KMS Keys) được lưu trữ riêng biệt trên dịch vụ quản lý khóa bảo mật và chỉ được cấp quyền giải mã khi có token ủy quyền hợp lệ.
- **NFR-SEC-02 (Mã hóa đường truyền - Encryption in Transit):** Bắt buộc sử dụng giao thức **TLS 1.3** trên toàn bộ các kết nối Web, API và WebSocket. Không hỗ trợ các phiên bản SSL/TLS cũ.
- **NFR-SEC-03 (Kiểm soát Tải file Đề thi Chính thức):** Khi cán bộ in sao tải file Word/PDF của kỳ thi chính thức, hệ thống bắt buộc yêu cầu xác thực hai yếu tố (2FA qua OTP/Authenticator App).

### 3.2. Quản trị Truy cập & Chống rò rỉ Dữ liệu
- **NFR-SEC-04 (Phân quyền RBAC & Data Scoping):**
  - Giáo viên chỉ được xem và sửa đổi các câu hỏi do chính mình tải lên hoặc các câu hỏi trong ngân hàng chung mà tổ bộ môn cho phép truy cập.
  - Ngăn chặn triệt để lỗ hổng truy cập trực tiếp đối tượng (IDOR): Kiểm tra quyền sở hữu trên từng câu hỏi trước khi trả về dữ liệu.
- **NFR-SEC-05 (Bảo mật Mật khẩu & Token JWT):** Mật khẩu người dùng được băm bằng thuật toán **PBKDF2-HMAC-SHA256** với 600.000 vòng lặp kết hợp Salt 32 bytes ngẫu nhiên độc lập cho từng tài khoản (không phụ thuộc C runtime ngoài). Phiên làm việc xác thực bằng Token JWT chuẩn mã hóa **HS256** thời hạn 7 ngày, kiểm soát vai trò RBAC chặt chẽ.
- **NFR-SEC-07 (Bảo mật OAuth 2.0 State):** Luồng đăng nhập mạng xã hội (Google, GitHub) sử dụng mã `state` ngẫu nhiên và chứng thực token ID trực tiếp với nhà cung cấp, loại bỏ nguy cơ tấn công Replay Attack và CSRF.
- **NFR-SEC-06 (Audit Logging Toàn diện):** Hệ thống phải ghi lại nhật ký bất biến (Immutable Audit Log) cho mọi hành động: Ai đã tạo đề, ai đã xem trước đề, ai đã tải file in ấn, địa chỉ IP và User-Agent.

---

## 4. TÍNH TIN CẬY & SẴN SÀNG (RELIABILITY & AVAILABILITY)

### 4.1. Cam kết Tính Sẵn sàng (Availability SLA)
- **NFR-REL-01 (Uptime SLA):** Hệ thống cam kết thời gian hoạt động tối thiểu **99.9%** (tổng thời gian gián đoạn không vượt quá 43.8 phút/tháng).
- **NFR-REL-02 (Cơ chế Dự phòng Đa mô hình AI - Multi-model Fallback):**
  - Khi nhà cung cấp AI chính (ví dụ: Google Gemini API) bị nghẽn mạng, gặp lỗi 5xx hoặc timeout quá 10 giây, hệ thống tự động chuyển tiếp yêu cầu (Circuit Breaker & Fallback) sang mô hình dự phòng (OpenAI GPT-4o hoặc mô hình mã nguồn mở nội bộ) mà không làm gián đoạn tiến trình của người dùng.

### 4.2. Sao lưu & Khôi phục Sau thảm họa (Backup & Disaster Recovery)
- **NFR-REL-03 (Tần suất sao lưu - RPO):** Tự động sao lưu cơ sở dữ liệu (Full Backup) mỗi 24 giờ và sao lưu nhật ký WAL (Write-Ahead Logging) liên tục. Cam kết Mục tiêu Điểm Phục hồi (RPO) **$< 15$ phút**.
- **NFR-REL-04 (Thời gian khôi phục - RTO):** Cam kết Mục tiêu Thời gian Phục hồi (RTO) **$< 2$ giờ** trong trường hợp hạ tầng máy chủ chính gặp sự cố vật lý nghiêm trọng.

### 4.3. Bảo toàn Dữ liệu Giao diện & Chat Bubble (UI Data Integrity)
- **NFR-REL-07 (Bảo toàn Khối mã Chat Bubble & Chống nuốt Code):**
  - Tỷ lệ nuốt mất mã nguồn trong bubble chat khi AI sinh mã LaTeX phải bằng **$0\%$**.
  - Hệ thống chỉ được phép ẩn khối mã và gắn badge *"Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn"* khi và chỉ khi diff thực sự tồn tại, hợp lệ và đã được nạp thành công vào editor (`diffs.length > 0`).
  - Trong mọi trường hợp khác (diff rỗng, không tìm thấy vị trí dòng cũ, hoặc mã độc lập), khối mã phải được bảo toàn nguyên vẹn 100% trong bubble chat kèm 3 nút thao tác: Chèn vào con trỏ, Sao chép, và Áp dụng thay thế.
- **NFR-REL-08 (Độ Tin Cậy của Động Cơ Nhúng Ngầm Canonical Preamble & Dual-Mode Normalizer):**
  - **Tỷ lệ nhận diện và chuẩn hóa chính xác:** Đạt **100%** trong việc phân biệt giữa mã nguồn thuần câu hỏi (Preamble-Free Question Body) và tài liệu hoàn chỉnh (Full Document).
  - **Khử xung đột đệm biên dịch (Zero Cache Collision):** Bộ tạo khóa mã băm kết hợp `(latex_code, title, mode)` đảm bảo việc chuyển đổi qua lại giữa chế độ Đề thi (`[dethi]`) và Lời giải (`[loigiai]`) không bao giờ phát sinh tình trạng trả về bản PDF cũ bị lưu đệm sai lệch.
  - **Tính tự chứa của tệp xuất bản (Self-Contained TeX Packaging):** 100% các file nguồn TeX khi tải về từ hệ thống đều tự động được bao bọc đầy đủ Canonical Preamble chuẩn khảo thí quốc gia và `\begin{document}...\end{document}`, đảm bảo biên dịch thành công ngay lần đầu tiên trên mọi môi trường TeX chuẩn bên ngoài mà không cần cấu hình thêm.

---

## 5. KHẢ NĂNG MỞ RỘNG & TẢI TRỌNG (SCALABILITY & CAPACITY)

### 5.1. Quy mô Dữ liệu (Data Capacity)
- **NFR-SCA-01 (Quy mô Ngân hàng Câu hỏi):** Cơ sở dữ liệu và chỉ mục tìm kiếm đáp ứng lưu trữ tối thiểu **1.000.000 câu hỏi** và **5.000.000 phương án/tiểu mục** mà hiệu năng truy vấn không giảm quá 10%.
- **NFR-SCA-02 (Lưu trữ Tài nguyên Đồ họa):** Hệ thống Object Storage (S3/MinIO) có khả năng lưu trữ tối thiểu **10 TB** hình ảnh đồ thị/biểu đồ với cơ chế CDN đệm (Cloudflare/CloudFront) tăng tốc độ tải.

### 5.2. Khả năng Chịu tải Đồng thời (Concurrent Load)
- **NFR-SCA-03 (Tải người dùng đồng thời):** Hệ thống chịu tải tối thiểu **5.000 người dùng hoạt động đồng thời (CCU)** trong các khung giờ cao điểm thi học kỳ.
- **NFR-SCA-04 (Hàng đợi Xử lý Bóc tách AI):** Kiến trúc hàng đợi Redis Queue + Worker Pods mở rộng ngang tự động (HPA) từ 2 lên 20 workers khi số lượng job bóc tách dồn ứ $> 50$ jobs.

---

## 6. KHẢ NĂNG SỬ DỤNG & TRẢI NGHIỆM NGƯỜI DÙNG (USABILITY)

### 6.1. Trải nghiệm Giao diện Hậu kiểm (HITL Experience)
- **NFR-USA-01 (Đồng bộ Cuộn trang - Synchronized Scrolling):** Khi người dùng cuộn xem câu hỏi ở cột bên phải, khung xem tài liệu gốc bên trái di chuyển mượt mà đến đúng vùng tài liệu tương ứng với độ trễ phản hồi **$< 100$ ms**.
- **NFR-USA-02 (Học nhanh - Learnability):** Giáo viên mới tiếp cận hệ thống có thể hoàn thành việc tải lên một đề thi và duyệt 10 câu hỏi đầu tiên vào ngân hàng trong vòng **$< 15$ phút** mà không cần tham gia lớp đào tạo trực tiếp.

### 6.2. Tiêu chuẩn Khả năng Tiếp cận (Accessibility & Compatibility)
- **NFR-USA-03 (Tương thích Trình duyệt):** Hoạt động đồng nhất 100% trên các trình duyệt phổ biến: Google Chrome (phiên bản $\ge 110$), Microsoft Edge (phiên bản $\ge 110$), Mozilla Firefox, và Safari trên MacOS/iPadOS.
- **NFR-USA-04 (Tương thích Thiết bị):** Hỗ trợ tốt trên màn hình máy tính bàn, laptop (tối thiểu 1366x768) và máy tính bảng (iPad/Android tablet).

---

## 7. TUÂN THỦ PHÁP LÝ & BẢO VỆ DỮ LIỆU (LEGAL & COMPLIANCE)

- **NFR-COM-01 (Tuân thủ Nghị định 13/2023/NĐ-CP):** Hệ thống bảo vệ dữ liệu cá nhân của giáo viên và học sinh (họ tên, email, kết quả điểm số), cung cấp tùy chọn xóa tài khoản và dữ liệu cá nhân (Right to be Forgotten).
- **NFR-COM-02 (Bản quyền Nội dung Khảo thí & Chuẩn hóa TT 32):** Hệ thống hỗ trợ đánh dấu bản quyền số (Watermarking) tên trường học/tổ bộ môn mờ trên file Word và PDF khi xuất bản nhằm bảo vệ quyền tác giả của đề thi. Toàn bộ mã hóa câu hỏi bám sát chuẩn Yêu cầu cần đạt của Thông tư 32/2018/TT-BGDĐT.

---

## 8. QUẢN TRỊ PHÁT TRIỂN, CỔNG PRE-COMMIT CI GATE & QUY TẮC GIT WORKFLOW (DEVELOPMENT GOVERNANCE)

- **NFR-DEV-01 (Quy chuẩn Git Commit & Push qua Cổng Pre-Commit CI):** Mọi thay đổi mã nguồn bắt buộc phải vượt qua toàn diện bài kiểm thử CI trên runner (100% test cases PASSED) trước khi thực hiện `git commit` tuân thủ chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`) và `git push` lên nhánh remote repository tương ứng.
- **NFR-DEV-02 (Tuyệt đối Không Tự Động Tạo Pull Request):**
  - Nghiêm cấm tuyệt đối các agent, tiến trình tự động hóa, hoặc script CI tự ý tạo Pull Request (`gh pr create`, REST API calls) hoặc tự động đẩy/cập nhật vào Pull Request.
  - Hành động mở hoặc cập nhật Pull Request chỉ được phép thực hiện khi và chỉ khi có yêu cầu bằng lời nói rõ ràng, tường minh từ người dùng (explicit user prompt).
- **NFR-DEV-03 (Dọn dẹp Tiến trình Nền):** Sau khi chạy thử nghiệm hoặc kiểm thử, toàn bộ các tiến trình nền (uvicorn cổng 8000, worker Node.js, subprocess) phải được dọn dẹp và tắt triệt để, không để tồn đọng tiến trình mồ côi.
- **NFR-DEV-04 (Cổng Kiểm Soát Pre-Commit CI Gate & Vòng Lặp Sửa Lỗi CI Loop):**
  - **Pre-commit Gate:** Trước khi commit, bắt buộc phải test qua được CI. Tuyệt đối cấm commit khi CI chưa pass.
  - **CI Loop:** Nếu CI test không pass, kích hoạt ngay vòng lặp: phân tích lỗi → sửa mã nguồn / cập nhật test & CI → chạy lại test CI cho đến khi 100% test cases đạt (`PASS CI`) mới được phép commit.
- **NFR-DEV-05 (Nguyên Tắc Cô Lập CI Tuyệt Đối & Phân Định Vai Trò - Strict CI Isolation):**
  - Sub-Agent đảm nhận làm CI (Sub-Agent 3) tách biệt hoàn toàn với tất cả các sub-agents còn lại.
  - **Mọi sub-agent khác (Sub-Agent 1, Sub-Agent 2, Sub-Agent 4...) tuyệt đối KHÔNG ĐƯỢC PHÉP truy cập và đọc CI** (`.github/workflows/`).
  - Chỉ duy nhất sub-Agent đảm nhận làm CI mới thực hiện viết, chỉnh sửa cấu hình CI/CD.
  - Sub-Agent viết CI có toàn quyền đọc và tiếp nhận các thông tin từ các sub-agents khác (specs, code diffs, dependencies, test cases, bug reports).
- **NFR-DEV-06 (Đồng Bộ CI Liên Tục Theo Code Mới):** Mỗi khi code có cập nhật gì mới (thư viện mới trong `requirements.txt`/`package.json`, fonts, môi trường headless browser, biến môi trường `.env`, cờ thực thi...), CI workflow bắt buộc phải được cập nhật đồng bộ ngay lập tức để loại bỏ mọi khả năng gây ra lỗi trên môi trường runner.
