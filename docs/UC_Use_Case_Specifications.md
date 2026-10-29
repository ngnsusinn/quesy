# TÀI LIỆU ĐẶC TẢ USE CASE (USE CASE SPECIFICATIONS - UC)
**Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học (QUESY)**

- **Mã tài liệu:** QUESY-UC-01  
- **Phiên bản:** 3.6 (Con Trỏ Soạn Thảo Đen Nổi Bật High-Contrast Text Cursor & Caret Tại Ma Trận Đề & Ô Nhập Liệu, Hệ Thống Phân Trang Ngân Hàng Câu Hỏi Chuẩn Apple HIG)  
- **Mục tiêu tài liệu:** Đặc tả chi tiết các ca sử dụng (Use Cases) giải quyết bài toán số hóa đề thi, kiểm soát trùng lặp, hệ thống xác thực người dùng an toàn (PBKDF2/SHA256, JWT HS256, Google/GitHub OAuth, RBAC), phân hệ Ngân hàng câu hỏi toàn diện (CRUD, Modals Apple HIG, lọc 6 tầng TT 32, xuất PDF/CSV/LaTeX, nhập đề, kiểm tra trùng lặp AI >= 90%, đồng bộ badge, hệ thống phân trang Apple HIG tải theo trang on-demand KaTeX), phân hệ Soạn đề tinh gọn tích hợp nút chuyên biệt "LƯU VÀO NGÂN HÀNG" (trích xuất trọn vẹn trắc nghiệm, đúng sai QĐ 764, trả lời ngắn, TikZ, BBT, tự động gắn tag YCCĐ AI), phân hệ Soạn đề tinh gọn không cần preamble (Canonical Preamble Injection ex_test v3.3, tikz, tkz-tab, tcolorbox, A4), con trỏ soạn thảo đen nổi bật (High-Contrast Bold Black Text Cursor & Caret) tại ô ma trận và các input text, dựng đồ thị vector SVG, trộn đề an toàn, xuất bản in ấn, trợ lý soạn đề AI Copilot trực tiếp, cơ chế render KaTeX toàn diện triệt tiêu lỗi văn bản thô, và chuẩn hóa hệ thống dropdown select Apple HIG (.apple-select).
- **Ngày phát hành:** 2026-10-28
- **Tiêu chuẩn áp dụng:** RUP / Unified Modeling Language (UML)

---

## 1. SƠ ĐỒ TỔNG THỂ USE CASE (SYSTEM USE CASE DIAGRAM)

### 1.1. Quy tắc Quản trị Git, Pull Request First & Continuous PR Description Sync (Mandatory Git Rule)
- **Quy tắc tạo PR trước khi commit (PR First Rule):** Khi bắt đầu triển khai hoặc có nhánh làm việc (`feat`), BẮT BUỘC phải đảm bảo có Pull Request được mở trước trên GitHub (`gh pr create`). Tuyệt đối không commit khi chưa tồn tại Pull Request.
- **Quy tắc cập nhật mô tả PR liên tục (Continuous PR Description Sync):** Nếu đang tồn tại 1 Pull Request trước khi commit thì mỗi khi thực hiện `git commit` và `git push`, BẮT BUỘC phải cập nhật lại nội dung (description / body) của Pull Request đó (`gh pr edit <PR_NUM> --body "..."`) để phản ánh chính xác trạng thái kỹ thuật, các thay đổi mới nhất và kết quả kiểm thử.
- Mọi tác vụ phát triển tuân thủ nghiêm ngặt chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).

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

### UC-05: QUẢN LÝ NGÂN HÀNG CÂU HỎI LƯU TRỮ BỀN VỮNG SQLITE 100% (NO MOCK OVERWRITE)
- **Mã Use Case:** `UC-05`
- **Tên Use Case:** Quản lý Ngân hàng Câu hỏi Lưu trữ Bền vững SQLite & Triệt tiêu Ghi đè Mock Data
- **Tác nhân chính:** Giáo viên, Quản trị viên
- **Mô tả:** Đảm bảo toàn bộ câu hỏi thực tế trong CSDL SQLite (`storage/quesy.db`, 230+ câu hỏi) được tải đầy đủ lên giao diện khi khởi động hoặc F5, không bị ghi đè dữ liệu mẫu tĩnh, đồng bộ tuyệt đối qua mọi lần khởi động lại máy chủ.

#### Luồng sự kiện chính:
1. Khi khởi động ứng dụng hoặc F5 tải lại trang, client thực thi `fetchQuestionsFromDB()` gọi API `GET /api/v1/questions?limit=1000`.
2. Hệ thống nạp toàn bộ danh sách câu hỏi thực tế từ SQLite vào `state.itemBank`.
3. Hệ thống render giao diện ngân hàng câu hỏi (`renderItemBank()`), áp dụng chuẩn hóa `formatStemForDisplay` cho mọi stem/options/sub-statements, phân trang theo cơ chế Apple HIG (`state.bankPagination = { currentPage: 1, pageSize: 12 }`), chỉ render danh sách câu hỏi của trang hiện tại và kích hoạt `renderKaTeX(container)` đảm bảo $100\%$ công thức toán học được biên dịch sắc nét (không sót text thô, tốc độ kết xuất $< 10$ms).
4. Thanh điều khiển phân trang `#bank-pagination-controls` hiển thị thông tin dải câu hỏi (`Hiển thị X - Y trong tổng số N câu hỏi`), các nút chuyển trang Trước/Sau, dải nút số trang thông minh với trang active xanh Apple `#0071e3`, và dropdown chọn số câu/trang (`12`, `24`, `48` câu/trang). Khi chuyển trang, giao diện tự động cuộn mượt về đầu danh sách `#bank-cards-grid`.
5. Toàn bộ các box chọn bộ lọc taxonomy áp dụng class `.apple-select` với icon chevron SVG slate-500, loại bỏ hoàn toàn class `font-mono` tại `#bank-filter-yccd` để giữ vững typography sans-serif Apple HIG; ô tìm kiếm `#bank-search-input` trang bị đệm an toàn 36px (`padding-left: 2.25rem !important;`) và icon kính lúp `pointer-events-none` chống đè placeholder và tối ưu nhận focus chuột. Khi người dùng thay đổi bất kỳ bộ lọc nào, hệ thống tự động reset `currentPage = 1`.
6. Hệ thống kiểm tra: Nếu CSDL đã có dữ liệu (`state.itemBank.length > 0`), tuyệt đối KHÔNG kích hoạt `seedInitialQuestions()`, bảo toàn 100% dữ liệu thực.
7. Khi người dùng thực hiện tạo câu hỏi mới, import LaTeX hàng loạt, chỉnh sửa câu hỏi, xóa câu hỏi hoặc bấm "LƯU VÀO NGÂN HÀNG" từ phân hệ Soạn đề, các thay đổi được ghi trực tiếp vào SQLite và client tự động kích hoạt `fetchQuestionsFromDB()` để đồng bộ lại dữ liệu.

#### Luồng ngoại lệ (Offline Fallback):
- Khi CSDL SQLite hoàn toàn rỗng hoặc máy chủ Backend chưa được kích hoạt, hệ thống mới kích hoạt `seedInitialQuestions()` làm dữ liệu mẫu dự phòng ngoại tuyến.

---

### UC-06: THIẾT LẬP BẢNG MA TRẬN PHÂN CẤP ĐA TẦNG (CHƯƠNG · BÀI · DẠNG x 3 PHẦN x 4 MỨC ĐỘ), ĐỐI SOÁT TỒN KHO & SINH ĐỀ THI GỐC
- **Mã Use Case:** `UC-06`
- **Tên Use Case:** Thiết lập Bảng Ma trận Phân cấp Đa tầng theo YCCĐ & 3 Phần x 4 Cấp độ Nhận thức NB-TH-VD-VDC, Đối soát Tồn kho Thời gian thực & Khởi tạo Đề thi Gốc
- **Tác nhân chính:** Tổ trưởng Chuyên môn, Giáo viên
- **Căn cứ pháp lý:** Thông tư 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT

#### Luồng sự kiện chính:
1. Người dùng truy cập phân hệ Ma trận đề thi (`/matrix`, tab `#tab-matrix`).
2. Giao diện Header Card hiển thị tinh gọn theo Apple HIG: Tên kỳ thi, Khối lớp & Môn học, Thời gian thi (sử dụng dropdown `#matrix-param-time` tích hợp class `.apple-select` đồng bộ hoàn hảo kích thước với các input text) và Thang điểm 10.0đ.
3. Hệ thống dựng Bảng Ma trận Phân cấp Đa tầng tương tác:
   - **Cột 1 (Chương · Bài · Dạng - Sticky Left):**
     * Cây phân tầng 3 cấp: Chương (Topic) -> Bài học (Lesson) -> Dạng bài tập (Problem Archetype / YCCĐ).
     * Tên dạng bài tập được biên dịch công thức toán học KaTeX trực quan.
     * Người dùng sử dụng các nút trên thanh công cụ Cột 1:
       + Nút **"Mở hết" (Expand All)** và **"Đóng hết" (Collapse All)** để gập/mở cây.
       + **Ô tìm kiếm dạng bài (`#matrix-search-archetype`):** Gõ từ khóa để lọc các dạng bài hoặc bài học cần cấu hình; trang bị đệm an toàn 36px (`padding-left: 2.25rem !important;`) và icon `pointer-events-none` triệt tiêu lỗi che đè placeholder và cho phép click thẳng vào input.
       + **Checkbox "Dạng có câu":** Lọc ẩn các dạng bài không có câu hỏi trong ngân hàng.
       + **Presets Khảo thí:** Chọn áp dụng nhanh ma trận mẫu Chuẩn THPT 2025 (22 câu 10.0đ), Định kỳ (20 câu), hoặc Cuối kỳ (28 câu).
   - **3 Nhóm Cột Lớn (Chuẩn Định Dạng 2025) x 4 Cột Con Nhận Thức:**
     * Nhóm Phần I (Trắc nghiệm 4 lựa chọn, 0.25đ/câu): Gồm 4 cột con NB, TH, VD, VDC.
     * Nhóm Phần II (Đúng / Sai 4 ý, 1.0đ/câu theo barem QĐ 764): Gồm 4 cột con NB, TH, VD, VDC.
     * Nhóm Phần III (Trả lời ngắn, 0.5đ/câu): Gồm 4 cột con NB, TH, VD, VDC.
     * Cột ngoài cùng: Tổng câu và Tổng điểm từng dòng.
4. Người dùng nhập số lượng câu hỏi cần rút vào các ô giao nhau giữa Dạng bài và (Phần thi, Cấp độ nhận thức):
   - Các ô nhập liệu (`.matrix-input-cell`, `<input type="number">`) được ẩn hoàn toàn spin buttons mặc định của trình duyệt (`-webkit-appearance: none`, `-moz-appearance: textfield`).
   - Khi rê chuột vào ô `.matrix-input-cell` hoặc thẻ `<input>`, con trỏ chuột chuyển ngay sang con trỏ soạn thảo đen đậm tương phản cao chuẩn SVG (`cursor: url("data:image/svg+xml,...") 12 12, text !important;`), đảm bảo độ nổi bật 100% trên nền sáng.
   - Caret nhấp nháy chuyển màu đen đậm sắc nét (`caret-color: #000000 !important;`).
   - Ô `.matrix-input-cell` phản hồi vi tương tác hover nổi bật: nền chuyển xanh nhạt `rgba(0, 113, 227, 0.08)`, viền thẻ input chuyển xanh Apple `#0071e3` cùng bóng đổ `0 0 0 2px rgba(0, 113, 227, 0.25)`.
   - Thao tác nhấp chuột vào bất kỳ vị trí nào trong ô `td.matrix-input-cell` tự động kích hoạt focus và bôi đen số trong input (Click-to-Focus).
   - Mỗi ô input đi kèm chip badge hiển thị tồn kho câu hỏi thực tế trong CSDL Question Bank (`Kho: {stock}`).
   - Chip badge tự động chuyển màu xanh lá (`stock-ok`) nếu đủ câu khả dụng hoặc màu đỏ cảnh báo (`stock-warn`) nếu số lượng chọn lớn hơn số câu trong kho.
5. Hệ thống tính toán thời gian thực:
   - Cập nhật số câu và điểm subtotal cho từng Bài học và từng Chương.
   - Cập nhật tổng số câu & điểm từng Phần (I, II, III) trên Thanh Footer Cố Định (`#matrix-sticky-footer`).
   - Cập nhật thang phân bổ nhận thức Bloom 4 màu: NB % - TH % - VD % - VDC %.
6. Người dùng có thể nhấn nút "Xuất Bản Đặc Tả Ma Trận" để tải về bản đặc tả dưới dạng PDF Vector, CSV UTF-8 BOM hoặc JSON qua endpoint `GET /api/v1/matrix/{id}/spec`.
7. Người dùng nhấn nút **`🚀 Tạo Đề Thi Gốc & Sang Trộn Đề`** (`#btn-matrix-generate-exam`) trên thanh Footer cố định.
8. Hệ thống lưu ma trận vào CSDL qua `POST /api/v1/matrix`, kích hoạt API `POST /api/v1/exams/generate` và chuyển tiếp mượt mà sang phân hệ Trộn đề an toàn (`#tab-shuffler`), sẵn sàng cho khâu hoán vị mã đề và xuất bản ấn phẩm khảo thí.

---

### UC-07: SINH ĐỀ THI GỐC, NHẬP TỪ MA TRẬN & HOÁN ĐỔI CÂU HỎI TƯƠNG ĐƯƠNG (IN-PLACE ITEM SWAP)
- **Mã Use Case:** `UC-07`
- **Tên Use Case:** Sinh Đề thi Gốc từ Ma trận và Hoán đổi Câu hỏi Tương đương
- **Tác nhân chính:** Giáo viên, Tổ trưởng Chuyên môn

#### Luồng sự kiện chính:
1. Người dùng chọn Ma trận đề thi cần sử dụng và thiết lập ràng buộc loại trừ (loại trừ câu hỏi đã xuất hiện trong 30 ngày qua).
2. Người dùng nhấn nút "Khởi Tạo Đề Thi Gốc & Sang Trộn Đề".
3. Hệ thống kích hoạt thuật toán Constraint Satisfaction Problem (CSP Solver):
   - Rút câu hỏi đạt `status = 'APPROVED'`, `is_defective == False` khớp từng ô ma trận.
   - Áp dụng trọng số trắc lượng học ưu tiên câu hỏi có độ phân biệt $D \ge 0.3$.
   - Bảo toàn các câu hỏi chùm có chung `passage_id`.
4. Hệ thống hiển thị Đề thi Gốc (Master Exam) tại tab `#tab-shuffler` (Bước 1):
   - Render đầy đủ thân câu hỏi, công thức KaTeX, đồ thị TikZ vector SVG, các phương án A-B-C-D, 4 khẳng định Đúng/Sai và ô trả lời ngắn.
   - Hiển thị badge Option Anchor nếu câu hỏi có phương án mỏ neo.
5. Giáo viên rà soát đề gốc:
   - Nếu muốn thay thế một câu hỏi bất kỳ, giáo viên bấm nút **"Đổi câu khác" (Swap Question)** tại card câu hỏi đó.
   - Hệ thống gọi API `GET /api/v1/exams/{master_id}/items/{item_id}/replacement-candidates` tìm kiếm các câu hỏi tương đương trong Question Bank (cùng YCCĐ, cùng mức độ Bloom, cùng thể thức, không trùng với đề gốc).
   - Giáo viên chọn câu hỏi thay thế hoặc cho phép hệ thống tự động bốc câu hỏi tối ưu nhất qua `POST /api/v1/exams/{master_id}/items/{item_id}/swap`.
   - Hệ thống cập nhật câu hỏi mới vào đề gốc thời gian thực, hủy bỏ các mã đề hoán vị cũ để đảm bảo tính đồng bộ dữ liệu.

#### Các luồng rẽ nhánh (Thanh Nguồn Đề Gốc trong Shuffler):
- **Luồng 1a (Chọn Đề Gốc Đã Lưu):** Tại tab `#tab-shuffler`, người dùng mở dropdown `#shuffler-select-master-exam` chọn một đề thi gốc đã lưu trong hệ thống. Hệ thống gọi `GET /api/v1/exams/{id}` và nạp ngay vào không gian làm việc.
- **Luồng 1b (Sinh Đề Gốc từ Ma Trận Khảo Thí Trực Tiếp):** Người dùng chọn một ma trận từ dropdown `#shuffler-select-matrix` và bấm nút **`⚡ Sinh Đề Gốc từ Ma Trận Này`**. Hệ thống gọi `POST /api/v1/exams/generate` với `matrix_id`, tự động rút đề theo ràng buộc và nạp trực tiếp vào Shuffler.
- **Luồng 1c (Đồng bộ Ma Trận Hiện Tại):** Người dùng bấm nút **`🔄 Đồng bộ từ Ma trận hiện tại`** để chuyển đổi ngay ma trận đang soạn thảo tại tab `/matrix` thành đề gốc trong Shuffler.

---

### UC-08: TRỘN ĐỀ HOÁN VỊ AN TOÀN 4 NGUYÊN TẮC (SAFE SHUFFLING)
- **Mã Use Case:** `UC-08`
- **Tên Use Case:** Trộn Đề Hoán Vị An Toàn 4 Nguyên Tắc & Lập Ma Trận Đáp Án
- **Tác nhân chính:** Giáo viên, Tổ trưởng chuyên môn

#### Luồng sự kiện chính:
1. Người dùng cấu hình trộn đề: Chọn 4 mã đề hoán vị chuẩn (101, 102, 103, 104).
2. Người dùng nhấn nút "Kích Hoạt Trộn Đề An Toàn (4 Mã Đề)".
3. Động cơ Safe Shuffling Engine thực thi nghiêm ngặt 4 nguyên tắc khảo thí an toàn:
   - **Section Integrity:** Chỉ hoán vị câu hỏi trong cùng một Phần (Phần I, Phần II, Phần III độc lập).
   - **Passage Integrity:** Gom ngữ liệu bài đọc chung và các câu con thành khối nguyên tử bất khả phân; các câu con luôn đi liền kề nhau.
   - **Option Anchor Rule (100%):** Tự động phát hiện phương án mỏ neo ("Cả A và B", "Tất cả các đáp án trên", "Không có đáp án nào"...) hoặc cờ `is_fixed = True`; **khóa cố định tại vị trí cuối cùng (D)** trong 100% các mã đề; chỉ hoán vị tự do các phương án A, B, C.
   - **Key Matrix:** Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu giữa đề gốc và 4 mã đề hoán vị.
4. Hệ thống hiển thị Kết quả Trộn Đề:
   - Huy hiệu xanh xác minh: `Option Anchor Rule: ĐẠT 100% (Khóa cố định tại vị trí D)`.
   - Các nút chuyển Tab xem trước từng mã đề (Mã 101, Mã 102, Mã 103, Mã 104) với KaTeX và TikZ đầy đủ.
   - Bảng Ma trận Ánh xạ Đáp án tổng hợp đối chiếu Đề gốc và 4 mã đề.

---

### UC-09: XUẤT BẢN ĐỀ THI ĐƠN LẺ & ĐÓNG GÓI ẤN PHẨM KHẢO THÍ (.ZIP) THUẦN VECTOR PDF LATEX
- **Mã Use Case:** `UC-09`
- **Tên Use Case:** Xuất bản Đề thi Đơn lẻ (PDF) & Đóng gói Ấn phẩm Khảo thí (.ZIP) Thuần Vector PDF LaTeX (Tectonic XeTeX Engine)
- **Tác nhân chính:** Giáo viên, Cán bộ in sao đề

#### Luồng sự kiện chính:
1. Người dùng có thể nhấn nút **"Tải PDF Mã {code}"** để tải trực tiếp file đề thi đơn lẻ dạng PDF Vector 2 cột chuẩn Bộ GD&ĐT qua `GET /api/v1/exams/{master_id}/export-pdf?variant_code={code}`. Hệ thống chuyển đổi mã đề sang LaTeX chuẩn Quốc gia (`ex_test.sty` v3.3) và biên dịch qua Tectonic XeTeX Engine.
2. Người dùng nhấn nút **"TẢI TRỌN GÓI ĐỀ THI PDF (.ZIP)"** qua `GET /api/v1/exams/{master_id}/export-zip?format=pdf`.
3. Hệ thống tạo và đóng gói tự động các file sau vào tệp ZIP:
   - `De_101.pdf`, `De_102.pdf`, `De_103.pdf`, `De_104.pdf`: Đề thi 4 mã đề hoán vị A4 Portrait 2 cột biên dịch từ LaTeX XeTeX chuẩn mực.
   - `LoiGiai_101.pdf`, `LoiGiai_102.pdf`, `LoiGiai_103.pdf`, `LoiGiai_104.pdf`: Hướng dẫn giải chi tiết kèm barem điểm bậc thang QĐ 764 biên dịch từ LaTeX XeTeX chuẩn mực.
   - `BangDapAn_TongHop.pdf`: Bảng ma trận đối chiếu đáp án tổng hợp in ấn dạng PDF.
   - `BangDapAn_TongHop.csv`: Bảng ma trận đối chiếu đáp án định dạng CSV có ký tự UTF-8 BOM (`\ufeff`) tương thích 100% Microsoft Excel tiếng Việt.
   - `Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`: Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR 2025.
4. Trình duyệt tự động kích hoạt tải xuống file `Goi_DeThi_PDF_{id}.zip` an toàn.

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
   - Nếu lần biên dịch trước đó gặp lỗi từ XeTeX/Tectonic, hệ thống tự động đính kèm `compile_error` vào payload gửi đến `POST /api/v1/composer/chat`. Phía máy chủ tự động ánh xạ số dòng lỗi trừ đi 11 dòng preamble chuẩn để khoanh vùng chính xác dòng lỗi trên ô soạn thảo.
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
- **Luồng 6j - Soạn thảo Đề thi Tinh gọn Không Preamble & Tự Động Nhúng Ngầm Canonical Preamble (Preamble-Free Authoring & Mode Switch):**
  1. Người dùng mở phân hệ Soạn đề (`/composer`):
     - Textarea editor `#composer-editor-input` nạp sẵn nội dung đề thi tinh gọn chỉ gồm tiêu đề và các câu hỏi chuẩn `ex_test.sty` (`\begin{ex}...\end{ex}`), hoàn toàn không chứa khai báo `\documentclass`, `\usepackage`, hay `\begin{document}`.
     - Giao diện hiển thị chỉ báo trạng thái: *"Preamble tiêu chuẩn đã được nạp tự động (ex_test v3.3, tikz, tkz-tab, tcolorbox, A4)"*.
  2. Người dùng nhập mới, chỉnh sửa các câu hỏi trắc nghiệm (`\choice`), Đúng/Sai (`\choiceTF`), Trả lời ngắn (`\shortans`), chèn đồ thị TikZ (`\begin{tikzpicture}`) hoặc hình ảnh cạnh chữ (`\immini`).
  3. Khi gửi biên dịch (nhấn `BIÊN DỊCH` hoặc auto-compile sau 800ms):
     - Trình duyệt gửi request `POST /api/v1/composer/compile` với payload `{ latex_code, title, mode }`.
     - Máy chủ phát hiện mã không có `\documentclass`, tự động tiêm Canonical Preamble tích hợp đầy đủ các gói `fontspec`, `amsmath,amssymb`, `tikz,tkz-tab`, `tcolorbox`, `xparse` và `\usepackage[{mode}]{ex_test}` khổ giấy A4 chuẩn lề 18mm.
     - PDF được biên dịch ra sắc nét và hiển thị trực tiếp trên Live Preview.
  4. Người dùng gạt công tắc `LỜI GIẢI` (`#composer-solution-toggle`):
     - Giao diện chuyển đổi trạng thái `this.showSolution` giữa `true` (Hiện lời giải) và `false` (Ẩn lời giải).
     - Hệ thống gửi yêu cầu biên dịch với cờ `mode = 'loigiai'` hoặc `mode = 'dethi'`.
     - Backend biên dịch tức thì với tùy chọn tương ứng của `ex_test`, không sửa đổi bất kỳ ký tự nào trong textarea editor của người dùng.
  5. Khi người dùng dán toàn bộ tài liệu TeX cũ có sẵn `\documentclass`:
     - Backend tự động nhận diện chế độ toàn vẹn, bảo toàn cấu trúc tài liệu của người dùng, nâng cấp các gói lệnh tương thích XeTeX và đồng bộ tùy chọn `[dethi]` / `[loigiai]`.
  6. Khi người dùng chọn menu `XUẤT FILE ▾` -> `Tải mã nguồn TeX (.tex)`:
     - Hệ thống tự động kiểm tra: nếu mã trong editor là dạng tinh gọn không preamble, hệ thống tự động bọc Canonical Preamble và `\begin{document}...\end{document}` trước khi lưu tệp tải về, đảm bảo giáo viên có thể biên dịch độc lập ngay trên TeXLive / Overleaf.
- **Luồng 6k - Đính kèm, Dán Clipboard (Ctrl+V) & Kéo Thả Phân Tích Hình Ảnh (Multi-Modal Image Input, Clipboard Paste & Visual Reasoning):**
  1. *Đính kèm từ Compact Bar:*
     - Người dùng nhấp vào nút icon ảnh trên thanh `#composer-ai-compact-bar` để chọn một hoặc nhiều file ảnh từ máy tính, HOẶC dán ảnh trực tiếp từ clipboard (`Ctrl+V` / `Cmd+V`) khi đang gõ tại `#composer-compact-input`.
     - Hệ thống kích hoạt Fast Dispatch: Tự động mở bung popup trợ lý lớn `#composer-ai-popup`, ẩn thanh compact bar, chuyển con trỏ vào ô nhập `#composer-chat-input`, đưa ảnh vào mảng `attachedImages` và hiển thị khay thumbnail đính kèm ngay trên ô chat.
  2. *Thao tác trên Khung Chat Lớn (#composer-chat-input-container):*
     - Người dùng có thể: (a) Nhấp vào nút icon ảnh trên toolbar của chat card; (b) Nhấn tổ hợp phím `Ctrl+V` / `Cmd+V` để dán ảnh chụp màn hình; (c) Kéo và thả file ảnh trực tiếp vào khung chat (vùng dropzone phát sáng viền tím `border-purple-500/80 bg-purple-500/10`).
     - Khay thumbnail `#composer-attached-images-container` hiển thị danh sách các ảnh đã chọn (kích thước 54px x 54px, bo góc mượt mà).
     - Người dùng có thể nhấp vào nút (✕) ở góc trên mỗi thumbnail để gỡ ảnh ra khỏi danh sách đính kèm, hoặc nhấp vào ảnh để mở Lightbox xem trước cỡ lớn.
  3. *Gửi yêu cầu và Hiển thị:*
     - Người dùng gõ thêm câu lệnh yêu cầu (ví dụ: *"Trích xuất đề bài từ ảnh và vẽ lại đồ thị hàm số bằng TikZ"*) và nhấn `Enter` hoặc nhấp nút tròn mũi tên gửi.
     - Hệ thống đóng gói mảng Base64 Data URL vào trường `images` trong payload `POST /api/v1/composer/chat`.
     - Bong bóng chat của người dùng lập tức hiển thị nội dung câu hỏi cùng các thumbnail ảnh đính kèm; sau đó khay thumbnail đính kèm được dọn sạch (`attachedImages = []`).
  4. *Phản hồi từ AI Copilot:*
     - AI Copilot đa phương tiện (hoặc Offline Fallback) đọc ảnh, nhận diện đề bài, phân tích đồ thị/bảng biến thiên, sinh ra khối mã LaTeX `ex_test.sty` và khối TikZ tương ứng.
     - Phản hồi trả về kèm khối diff hoặc suggested_latex để giáo viên 1-click chèn hoặc thay thế trực tiếp vào trình soạn thảo đề thi.
- **Luồng 6l - Dán Ảnh Clipboard Chuẩn Xác Không Nhân Đôi (Event Isolation & Debounce Paste):**
  1. Người dùng sao chép một ảnh chụp màn hình vào Clipboard và nhấn `Ctrl+V` (hoặc `Cmd+V`) vào ô chat `#composer-chat-input`.
  2. Cơ chế Event Isolation kích hoạt: Gọi đồng thời `e.preventDefault()` và `e.stopPropagation()`, ngăn chặn hiện tượng sự kiện dán bị nổi bọt lên container cha `#composer-chat-input-container`.
  3. Cơ chế Debounce 500ms và Deduplication kiểm tra chữ ký ảnh: Nếu ảnh vừa được thêm vào trong vòng 500ms hoặc đã có trong danh sách `attachedImages`, hệ thống từ chối thêm trùng.
  4. Khay thumbnail hiển thị chính xác **duy nhất 1 ảnh**, thông báo toast xuất hiện duy nhất 1 lần, triệt tiêu hoàn toàn lỗi 1 ảnh dán thành 2 ảnh.
- **Luồng 6m - Chuẩn Hóa Khảo Thí 2025: Reset Thứ Tự Câu Hỏi Về 1 Ở Mỗi Phần (\setcounter{ex}{0}) & Loại Bỏ \large:**
  1. Người dùng biên dịch hoặc nạp mẫu đề thi chuẩn Quốc gia gồm PHẦN I, PHẦN II, PHẦN III.
  2. Tại đầu mỗi phần mới (PHẦN II, PHẦN III), hệ thống tự động kiểm tra và chèn lệnh `\setcounter{ex}{0}` ngay sau tiêu đề/hướng dẫn.
  3. Khi biên dịch PDF qua Tectonic/XeTeX hoặc xem trước HTML, PHẦN II tự động bắt đầu lại từ **Câu 1 đến Câu 4**; PHẦN III tự động bắt đầu lại từ **Câu 1 đến Câu 6** (không bị đếm nối tiếp thành Câu 13, 17...).
  4. Nếu trong mã nguồn có các thẻ `\large`, `\Large` ở tiêu đề phần (do người dùng vô tình dán vào), bộ tiền xử lý tự động bóc tách sạch sẽ, đưa tiêu đề về dạng chuẩn 12pt in đậm `\noindent\textbf{PHẦN ...}` `\textit{...}`.
- **Luồng 6n - Quy Trình Biên Dịch Nhanh Đa Tầng (Instant Preview 0.2s, Focus Quick Compile 1.5s & Draft Mode 15s):**
  1. *Xem trước Tức thì (Instant Live Preview):* Khi đang soạn thảo gõ chữ, hệ thống tự động kích hoạt chế độ xem trước HTML/SVG với độ trễ 0.2s, nạp lại các hình TikZ cũ từ MD5 Disk Cache trong 10ms.
  2. *Biên dịch Nhanh Câu Đang Sửa (Focus Quick Compile):* Khi giáo viên vừa sửa 1 câu hỏi cụ thể, bấm nút `⚡ BIÊN DỊCH CÂU NÀY` hoặc nhấn `Ctrl+Shift+S`. Hệ thống chỉ biên dịch duy nhất câu hỏi tại con trỏ sang PDF vector trong 1.0 - 1.8 giây để kiểm tra ngay bố cục.
  3. *Chế độ Nháp (Draft Mode):* Khi cần biên dịch toàn bộ đề nhưng muốn tiết kiệm thời gian, giáo viên bật cờ "Chế độ Nháp". Hệ thống tự động giảm `samples=35` cho toàn bộ đồ thị TikZ, hoàn thành biên dịch toàn bộ 22 câu trong 12 - 18 giây thay vì 65 giây.
  4. *Xuất bản Chính thức:* Khi đề thi hoàn thiện, tắt Chế độ Nháp và nhấn `BIÊN DỊCH` (`Ctrl+S`) để xuất bản bản in chất lượng cao 1200 DPI.

  ---

  ### UC-09: ĐĂNG KÝ, ĐĂNG NHẬP & QUẢN LÝ PHIÊN LÀM VIỆC (AUTHENTICATION & RBAC)

  - **Tác nhân:** Giáo viên, Học sinh, Quản trị viên (Admin).
  - **Mục tiêu:** Tạo tài khoản, xác thực danh tính an toàn, bảo vệ dữ liệu khảo thí và phân quyền truy cập.
  - **Tiền điều kiện:** Người dùng truy cập vào ứng dụng Quesy trên trình duyệt.
  - **Luồng sự kiện chính (MSS):**
    1. Người dùng bấm nút `[Đăng nhập]` hoặc `[Đăng ký]` trên góc phải thanh điều hướng header.
    2. Hệ thống hiển thị Modal Xác thực Apple HIG với 2 tab: Đăng nhập và Đăng ký.
    3. Khi Đăng ký:
       - Người dùng nhập Họ tên, Email, Mật khẩu (>= 6 ký tự) và chọn vai trò Giáo viên / Học sinh.
       - Nhấn `Tạo tài khoản`. Hệ thống băm mật khẩu PBKDF2-HMAC-SHA256, lưu vào bảng `users`, sinh JWT HS256 và trả về.
    4. Khi Đăng nhập Email/Mật khẩu:
       - Người dùng nhập Email, Mật khẩu và nhấn `Đăng nhập`.
       - Hệ thống kiểm tra mật khẩu đã băm, cấp JWT HS256, lưu `quesy_auth_token` vào `localStorage`.
    5. Khi Đăng nhập Mạng xã hội OAuth (Google / GitHub):
       - Người dùng bấm nút `Google` hoặc `GitHub`.
       - Hệ thống xác thực danh tính mạng xã hội, tạo hoặc liên kết tài khoản và trả về JWT.
    6. Giao diện Header tự động cập nhật: Ẩn nút Đăng nhập/Đăng ký, hiển thị Avatar người dùng, Tên, Role badge và Menu Tài khoản.
    7. Khi Đăng xuất: Người dùng chọn `Đăng xuất` từ menu tài khoản; hệ thống xóa token khỏi `localStorage` và khôi phục trạng thái ban đầu.

  ---

  ### UC-10: QUẢN TRỊ TOÀN DIỆN NGÂN HÀNG CÂU HỎI (ITEM BANK FULL CRUD & MODALS)

  - **Tác nhân:** Giáo viên, Tổ trưởng chuyên môn.
  - **Mục tiêu:** Quản trị toàn diện vòng đời câu hỏi trong CSDL khảo thí chuẩn Thông tư 32/2018 và QĐ 764/QĐ-BGDĐT.
  - **Tiền điều kiện:** Người dùng điều hướng tới tab `/bank`.
  - **Luồng sự kiện chính (MSS):**
    1. *Lọc cây kiến thức 6 tầng & Bộ lọc thứ cấp:*
       - Người dùng chọn Khối lớp -> Môn học -> Mạch nội dung TT 32 -> Chủ đề -> Bài học -> YCCĐ.
       - Chọn Dạng câu hỏi, Mức độ nhận thức (Biết, Hiểu, Vận dụng, Vận dụng cao), Thể thức (Trắc nghiệm, Đúng/Sai, Trả lời ngắn).
       - Nhập từ khóa tìm kiếm: Hệ thống tự động lọc danh sách với độ trễ < 150ms và tự động reset trang hiện tại về trang 1 (`state.bankPagination.currentPage = 1`).
    2. *Phân trang danh sách câu hỏi chuẩn Apple HIG:*
       - Hệ thống hiển thị câu hỏi theo trang (mặc định 12 câu/trang, tùy chọn 24 hoặc 48 câu/trang qua dropdown `#bank-page-size-select`).
       - Dải hiển thị ghi rõ `Hiển thị X - Y trong tổng số N câu hỏi`.
       - Người dùng bấm nút `< Trước` hoặc `Sau >` hoặc nhấp vào số trang cụ thể trên thanh `#bank-pagination-controls`.
       - Giao diện nạp ngay câu hỏi của trang đó, chỉ biên dịch KaTeX cho trang hiện tại (<10ms) và cuộn mượt về đầu danh sách.
    3. *Thêm câu hỏi mới (+ Thêm thủ công):*
       - Người dùng bấm nút `+ Thêm câu hỏi thủ công`.
       - Hệ thống mở Modal Thêm mới (`#question-create-modal`).
       - Chọn thể thức: SINGLE_CHOICE (4 options A-D, radio chọn đáp án đúng, checkbox khóa D), TRUE_FALSE_GROUP (4 ý a-d, switch Đúng/Sai), hoặc SHORT_ANSWER (ô nhập kết quả và dung sai).
       - Nhập nội dung stem kèm công cụ chèn nhanh công thức toán học và xem trước KaTeX Live.
       - Nhấn `Gợi ý YCCĐ AI` để tự động đề xuất mã YCCĐ; nhấn `Kiểm tra Trùng lặp AI` để kiểm tra Cosine Similarity.
       - Nhấn `Lưu vào Ngân hàng`: Hệ thống gọi `POST /api/v1/questions`, cập nhật danh sách và tăng số lượng trên badge `#bank-count-badge`.
    3. *Xem chi tiết câu hỏi:*
       - Người dùng bấm vào thẻ câu hỏi hoặc nút `Xem chi tiết`.
       - Hệ thống mở Modal Chi tiết (`#question-detail-modal`), render công thức toán học KaTeX, đồ thị TikZ SVG, barem điểm bậc thang QĐ 764 và chỉ số $p, D$.
    4. *Sửa câu hỏi:*
       - Người dùng bấm nút `Sửa` trên thẻ câu hỏi hoặc trong modal chi tiết.
       - Hệ thống mở Modal Sửa (`#question-edit-modal`) nạp sẵn dữ liệu câu hỏi.
       - Chỉnh sửa nội dung, đáp án, lời giải và bấm `Lưu thay đổi`: Hệ thống gọi `PUT /api/v1/questions/{id}` cập nhật CSDL.
    5. *Xóa câu hỏi:*
       - Người dùng bấm nút `Xóa` -> Hộp thoại xác nhận an toàn xuất hiện.
       - Xác nhận xóa -> Hệ thống gọi `DELETE /api/v1/questions/{id}`, xóa cascade options/sub-statements, cập nhật ngay số lượng badge `#bank-count-badge`.
    6. *Xuất & Nhập Ngân hàng:*
       - Xuất: Chọn `Xuất ngân hàng` -> Chọn PDF Vector (A4 in ấn), CSV UTF-8 BOM (chuẩn Excel không lỗi font), hoặc LaTeX (`ex_test.sty`).
       - Nhập: Bấm `Nhập câu hỏi` -> Tải file hoặc dán mã LaTeX -> Hệ thống bóc tách, tự động gắn tag và đẩy vào CSDL.

  ---

  ### UC-11: LƯU TOÀN BỘ ĐỀ THI TỪ SOẠN THẢO VÀO NGÂN HÀNG CÂU HỎI (1-CLICK SAVE FROM COMPOSER)

  - **Tác nhân:** Giáo viên biên soạn đề thi.
  - **Mục tiêu:** Lưu toàn bộ các câu hỏi từ văn bản LaTeX đang soạn thảo vào Ngân hàng câu hỏi CSDL mà không phải sao chép thủ công.
  - **Tiền điều kiện:** Giáo viên đang mở phân hệ Soạn đề (`/composer`) và có mã nguồn LaTeX đề thi hợp lệ.
  - **Luồng sự kiện chính (MSS):**
    1. Giáo viên hoàn tất soạn thảo đề thi trên LaTeX Editor.
    2. Giáo viên nhấp nút chuyên biệt **`📥 LƯU VÀO NGÂN HÀNG`** (`#btn-composer-save-to-bank`) trực tiếp trên thanh công cụ Composer.
    3. Hệ thống hiển thị hiệu ứng loading phản hồi xúc giác.
    4. Trình duyệt gửi request `POST /api/v1/composer/save-to-bank` với payload `latex_code`.
    5. Backend thực hiện phân tích:
       - Bóc tách toàn diện các câu hỏi chuẩn `\begin{ex}` hoặc `\textbf{Câu X.}`.
       - Trích xuất Trắc nghiệm đơn `\choice` (nhận diện `\True`), Đúng/Sai 4 ý `\choiceTF[1]` (nhận diện `\True` từng ý a, b, c, d), và Trả lời ngắn `\shortans`.
       - Giữ nguyên vẹn đồ thị TikZ, bảng biến thiên `tkz-tab` và khối lời giải `\begin{loigiai}`.
       - Tự động nhận diện môn học, khối lớp, chạy `suggest_auto_tagging` gán mã YCCĐ chuẩn Thông tư 32.
       - Lưu tất cả câu hỏi vào cơ sở dữ liệu `questions`, `question_options`, `sub_statements`.
    6. Backend phản hồi kết quả chi tiết: Tổng số câu đã lưu kèm số lượng câu của từng thể thức.
    7. Frontend hiển thị thông báo Toast thành công Apple HIG với thông tin chi tiết: *"Đã lưu thành công 22 câu hỏi vào Ngân hàng câu hỏi (12 Trắc nghiệm đơn, 4 Đúng/Sai 4 ý, 6 Trả lời ngắn)"*.
    8. Badge số lượng `#bank-count-badge` trên thanh điều hướng lập tức cập nhật số lượng mới.
    9. Khi giáo viên chuyển sang tab Ngân hàng câu hỏi (`/bank`), danh sách câu hỏi mới đã sẵn sàng hiển thị và phục vụ rút đề ma trận.
