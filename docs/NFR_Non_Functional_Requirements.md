# TÀI LIỆU YÊU CẦU PHI CHỨC NĂNG (NON-FUNCTIONAL REQUIREMENTS - NFR)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-NFR-01  
- **Phiên bản:** 2.9 (Cải tiến Giao diện Soạn đề LaTeX: Splitter Kéo Thả Ngang 2 Cột, Kéo Thả Độ Cao Trợ Lý Soạn Thảo, Hiển Thị Diff Độc Quyền Trên Code Editor & Quản Lý Phiên Chat Sạch Sẽ Với History Drawer)  
- **Tiêu chuẩn áp dụng:** ISO/IEC 25010 (Software Product Quality Model)  
- **Mục tiêu kỹ thuật:** Thiết lập các tiêu chuẩn hiệu năng bóc tách AI, tốc độ biên dịch đồ thị vector SVG, độ sắc nét vector WMF của công thức toán, khả năng mở sửa MathType 2 chiều không lỗi OLE activation, độ tương phản chuẩn WCAG 2.1 AA cho Dark Mode, độ trễ tương tác optimistic prompt dispatch, kéo thả resizer/splitter 60 FPS mượt mà, độ tin cậy của thuật toán thay thế dòng mờ, độ bảo mật dữ liệu đề thi và tính sẵn sàng cao.  
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
- **NFR-QUAL-01 (Độ Sắc nét Tuyệt đối của Công thức MathType - 100% Vector WMF):** Công thức toán trong file Word phải đạt chuẩn Vector WMF (`image/x-wmf`) với APM header, đạt tỷ lệ 100% vector thuần (loại bỏ hoàn toàn fallback raster DIB), giữ nguyên độ nét vector tuyệt đối (zero blur) ở mọi mức thu phóng màn hình và in ấn.
- **NFR-COMP-01 (Tính Biên tập Hai chiều của MathType OLE - DSMT7 Stream):** Đối tượng OLE nhúng trong file `.docx` bắt buộc phải chứa luồng nhị phân DSMT7 chuẩn với bản ghi `TeX Input Language`, chuẩn hóa embellishment cho toán tử vectơ (`\vec`, `\overrightarrow`), kích hoạt và mở mượt mà trong trình soạn thảo MathType 7 thông qua thao tác double-click của người dùng mà không phát sinh bất kỳ lỗi COM/OLE hay popup cảnh báo thiếu ứng dụng server nào.
- **NFR-COMP-02 (Kiến trúc Biên dịch LaTeX Tectonic Độc lập Môi trường):** Phân hệ Soạn đề LaTeX hỗ trợ biên dịch đa tầng (Hybrid Multi-tier Compiler Architecture):
  1. *Microservice Tectonic Docker:* Độc lập trên container Docker (được triển khai trên host ARM/Armbian tại cổng 8090), sử dụng engine Tectonic XeTeX tự động nạp packages CTAN theo nhu cầu, cache gói dữ liệu liên hoàn, tốc độ biên dịch $\le 10$s cho đề thi tiếng Việt đầy đủ bảng biến thiên `tkz-tab` và đồ thị TikZ.
  2. *Local Native Tectonic:* Tự động kích hoạt khi có binary `tectonic` trong PATH hệ thống.
  3. *Headless Chromium Fallback:* Cơ chế dự phòng nội tại với Chromium + MathJax 4.0 + TikZ Vector SVG + CMU Serif typography bảo đảm hệ thống luôn xuất bản được PDF chất lượng cao ngay cả khi ngắt kết nối mạng ngoài.
- **NFR-PERF-12 (Tốc độ Phản hồi Gửi Prompt Trợ lý AI - Optimistic Dispatch):** Khi người dùng nhấn Enter hoặc bấm gửi, giao diện phản hồi optimistic cập nhật bong bóng chat trong vòng $\le 16$ ms (1 frame); timeout Backend kết nối nhà cung cấp AI ngoài khống chế $\le 15$s kèm cơ chế fallback quy tắc thông minh tức thì, triệt tiêu độ trễ gây đóng băng UI.
- **NFR-UX-01 (Độ Tương phản Màu sắc Giao diện Dark Mode - WCAG 2.1 AA):** Tỷ lệ tương phản giữa chữ và nền ô chat (`#composer-compact-input` và `#composer-chat-input`) bắt buộc đạt $\ge 7:1$ (sử dụng văn bản trắng sáng `#f8fafc` trên nền tối `#1c1c1f` / `#141824`, con trỏ caret màu xanh Apple `#38bdf8`), loại bỏ hoàn toàn lỗi chữ đen chìm trên nền tối.
- **NFR-UX-02 (Tốc độ & Độ Mượt mà Khi Kéo Thả Resizer & Splitter - 60 FPS Smooth Dragging):** Thao tác kéo thả thay đổi kích thước Splitter ngang (2 cột Editor/Preview) và Vertical Resizer (Box Trợ lý Soạn thảo qua thanh pill hợp nhất `#composer-ai-resize-handle`) bắt buộc đạt tốc độ dựng hình 60 FPS ($\le 16.6$ ms/frame) trên trình duyệt, triệt tiêu hoàn toàn hiện tượng lag, giật khung hình (zero jank). Tự động ngắt transition CSS trong quá trình kéo và khôi phục mượt mà khi kết thúc thao tác; áp dụng Pointer Shield (`pointer-events: none`) trên canvas PDF để tránh gián đoạn con trỏ chuột.
- **NFR-UX-03 (Trải Nghiệm Zoom & Bố Cục Xem Trước PDF - Zero Drift & No Right-Margin Clipping):**
  1. *Độ ổn định điểm neo zoom (Zero Drift Invariant):* Thuật toán zoom-to-point đảm bảo độ trôi dạt điểm neo dưới con trỏ chuột (Cursor Anchor) hoặc trọng tâm màn hình (Center Anchor) không vượt quá $\pm 2\text{px}$ sau mỗi bước zoom, triệt tiêu $100\%$ hiện tượng giật màn hình hoặc nhảy về góc trên cùng bên trái $(0, 0)$.
  2. *Toàn vẹn hiển thị không xén nét (No Right-Margin Clipping):* Vùng cuộn `#composer-pdf-scroll-container` (`overflow-x-auto`) đảm bảo $100\%$ nội dung tài liệu luôn tiếp cận được qua cuộn ngang ở mọi mức zoom $[40\%, 250\%]$; cơ chế Auto Fit-to-Width tự động thích ứng với chiều rộng cột preview trong thời gian thực khi kéo splitter, ngăn chặn hoàn toàn việc nội dung bị che khuất hoặc tràn lề ngoài ý muốn.
- **NFR-REL-03 (Độ Tin cậy của Động cơ Thay thế Diff - Zero Drift Fuzzy Matcher):** Tỷ lệ áp dụng diff sửa đổi thành công qua thuật toán so khớp mờ 5 tầng đạt $\ge 99.5\%$, triệt tiêu lỗi false-negative "Không tìm thấy dòng cũ tương ứng trong văn bản hiện tại" do khoảng trắng, ngắt dòng hoặc thụt lề.
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
- **NFR-SEC-05 (Bảo mật Mật khẩu):** Mật khẩu người dùng được băm bằng thuật toán **Argon2id** (hoặc Bcrypt với work factor tối thiểu 12), kết hợp Salt ngẫu nhiên cho từng tài khoản.
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
