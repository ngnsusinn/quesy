# AGENT INSTRUCTIONS & PROJECT RULES - QUESY

## 1. NGUYÊN TẮC CỐT LÕI (MANDATORY STANDING RULES)

1. **QUY TẮC ĐỒNG BỘ TÀI LIỆU, ĐỐI CHIẾU CI/CD & COMMIT (DOCS, CI/CD & COMMIT ON EVERY CODE CHANGE):**
   - **Bắt buộc:** Sau **bất kỳ** thay đổi, bổ sung, sửa lỗi (bug fix) hay refactor nào trong mã nguồn (`backend/`, `frontend/`, `tests/`):
     1. Phải rà soát và cập nhật đồng bộ toàn bộ tài liệu dự án trong `docs/` (bao gồm `SRS`, `FRD`, `BRD`, `NFR`, `TEST`, `UC`, `README.md`, v.v.) để phản ánh chính xác trạng thái kỹ thuật mới nhất.
     2. **Bắt buộc đối chiếu và cập nhật cấu hình CI/CD (`.github/workflows/`):** Mỗi khi có thay đổi trong mã nguồn, phải chủ động rà soát xem có phát sinh dependencies mới (Python packages trong `requirements.txt`, npm packages trong `package.json`, font, headless browser/Chromium, biến môi trường `.env`, cờ thực thi...) hay không để cập nhật đồng bộ workflow CI/CD ngay lập tức, bảo đảm 100% test cases vượt qua trên mọi môi trường (Ubuntu/Linux runner).
     3. Chạy toàn bộ test suite (`pytest`) đảm bảo 100% test cases đạt (`71/71 PASSED`).
     4. Thực hiện `git commit` ngay với thông điệp rõ ràng, tuân thủ chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).

2. **CHUẨN MỰC KHẢO THÍ QUỐC GIA:**
   - **Thông tư 32/2018/TT-BGDĐT:** Phân cấp cây kiến thức 6 tầng theo Yêu cầu cần đạt (YCCĐ) và Dạng câu hỏi. **Tuyệt đối không phân chia theo các bộ sách giáo khoa thương mại** (như Cánh diều, Kết nối tri thức, Chân trời sáng tạo).
   - **Quyết định 764/QĐ-BGDĐT:** Câu hỏi trắc nghiệm Đúng/Sai 4 khẳng định phải áp dụng logic tính điểm bậc thang: Đúng 1 ý = 0.1đ; Đúng 2 ý = 0.25đ; Đúng 3 ý = 0.5đ; Đúng cả 4 ý = 1.0đ.

3. **CHUẨN MỰC XUẤT BẢN ĐỀ THI & TÀI LIỆU KHẢO THÍ THUẦN VECTOR PDF:**
   - **Định hướng Kiến trúc Thuần LaTeX & Vector PDF:**
     - Loại bỏ hoàn toàn sự phụ thuộc vào Microsoft Word (.docx) và MathType OLE binary formats để đảm bảo tính nhất quán tuyệt đối, chuẩn mực in ấn độ phân giải cao và tính di động trên mọi nền tảng máy chủ (Linux/Docker/ARM).
     - Định dạng xuất bản chính là **Vector PDF** biên dịch qua Tectonic XeTeX Engine (`armbian:8090` / local binary) kết hợp gói `ex_test.sty` chuẩn đề thi Quốc gia hoặc HTML5/ReportLab rendering.
   - **Đóng gói trọn bộ ấn phẩm khảo thí (.ZIP):**
     - Đề thi từng mã đề hoán vị dạng PDF (`De_{code}.pdf`) với layout 2 cột rõ ràng, tiêu đề chuẩn quy cách Bộ GD&ĐT.
     - Hướng dẫn giải chi tiết từng mã đề (`LoiGiai_{code}.pdf`) kèm barem tính điểm bậc thang theo Quyết định 764/QĐ-BGDĐT.
     - Bảng ma trận đáp án tổng hợp (`BangDapAn_TongHop.pdf` & `BangDapAn_TongHop.csv`).
     - Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR (`Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`).
   - **Quy cách in ấn:** Toàn bộ văn bản xuất bản phải tuân thủ chuẩn khổ giấy **A4 Portrait (210 x 297 mm)**, lề trang 1.5 cm - 1.8 cm, font Times New Roman / CMU Serif, giãn dòng 1.15.

4. **HIỆU NĂNG & DỊCH VỤ MATHJAX ENGINE:**
   - Dịch vụ MathJax được vận hành qua daemon persistent worker nền (`backend/services/mathjax_worker.js`) với bộ gói `input/tex-full`, tốc độ xử lý ~14 ms/công thức, bảo đảm ngân sách hiệu năng xuất file ZIP trọn bộ $< 10$ giây.
   - Tự động bổ sung đệm an toàn (+160 units) chống xén nét ký hiệu vươn cao (vectơ $\overrightarrow{AB}$, ngoặc co giãn).

5. **GIAO DIỆN & TRẢI NGHIỆM NGƯỜI DÙNG:**
   - Tuân thủ nghiêm ngặt Apple Human Interface Guidelines (HIG) và tương tác vi mô Emil Kowalski.
   - Phản hồi xúc giác tức thì (scale 0.97 khi nhấn), giao diện tối giản, cuộn đồng bộ mượt mà, font chữ sans-serif đồng nhất.
   - Điều hướng SPA với URL sạch (`/path`) và đăng ký đầy đủ route trên FastAPI tránh lỗi 404 khi tải lại trang (F5).

6. **DỌN DẸP & DIỆT TIẾN TRÌNH NỀN (PROCESS CLEANUP & TERMINATION ON TURN COMPLETION):**
   - **Bắt buộc:** Sau khi hoàn tất quá trình phản hồi, chạy thử nghiệm, kiểm thử hoặc chỉnh sửa mã nguồn:
     1. Phải chủ động kiểm tra và **tắt/diệt toàn bộ các tiến trình nền (kill background processes)**: máy chủ uvicorn/fastapi trên cổng 8000, worker Node.js mồ côi (`mathjax_worker.js`), và các tiến trình con subprocess.
     2. **Tuyệt đối không để sót tiến trình chạy ngầm dồn ứ (no leftover background processes)** gây chiếm dụng RAM, rò rỉ tài nguyên hệ thống, hoặc chiếm giữ cổng mạng gây xung đột phiên bản mã nguồn cũ giữa các lượt tương tác của người dùng.
     3. Mọi tiến trình nền phục vụ kiểm nghiệm chỉ được chạy tạm thời, phải dọn dẹp sạch sẽ trước khi kết thúc lượt phản hồi.

7. **QUY TRÌNH PHÂN HÓA 4 AGENT CHUYÊN TRÁCH & VÒNG LẶP KIỂM THỬ THỰC TẾ (4-AGENT ROLES & E2E BROWSER BLIND TEST LOOP):**
   - **Bắt buộc áp dụng cấu trúc 4 Agent chuyên trách trong quy trình phát triển và kiểm thử dự án:**
     1. **Agent 1 - Analysis & Comprehension (Đọc hiểu & Mổ xẻ Dự án):**
        - Chuyên trách đọc hiểu yêu cầu nghiệp vụ, mổ xẻ mã nguồn, phân tích kiến trúc, rà soát tài liệu kỹ thuật (`SRS`, `FRD`, `BRD`, `NFR`, `SOURCE_MAP.md`).
        - Xác định đúng vị trí và phạm vi tác động trước khi thực hiện bất kỳ thay đổi nào.
     2. **Agent 2 - Software Engineering & Coding (Triển khai Mã nguồn):**
        - Chuyên trách lập trình mã nguồn, hiện thực hóa tính năng, sửa lỗi (bug fixes) và tối ưu hóa hiệu năng theo đúng thiết kế của Agent 1.
        - Giữ gìn chuẩn mực code, không tự ý refactor lan man ngoài phạm vi yêu cầu.
     3. **Agent 3 - Test & Verification (Kiểm thử Chức năng Tự động):**
        - Chuyên trách chạy kiểm thử tự động toàn diện (`pytest`), kiểm tra tính toàn vẹn của dữ liệu và đảm bảo 100% test cases vượt qua (`71/71 PASSED`).
     4. **Agent 4 - Blind Test (Kiểm thử Mù & Đối chứng Thực tế trên Trình duyệt):**
        - Kiểm thử độc lập, khách quan, không dựa vào các giả định chủ quan của coder để tìm ra các lỗi ẩn và lỗi trải nghiệm người dùng thực tế.
        - **Yêu cầu bắt buộc đối với Agent Test & Blind Test:**
          - **Trực tiếp truy cập vào trình duyệt (Browser):** Khởi chạy trình duyệt thật để kiểm tra toàn bộ giao diện và luồng nghiệp vụ end-to-end.
          - **Thao tác thủ công toàn diện:** Tự động hóa việc **nhập text** (`fill_input`), **click chuột thủ công** (`click_at_xy`), cuộn trang, đổi tab, chuyển đổi chế độ xem.
          - **Chụp ảnh màn hình (Capture Screen):** Chụp và lưu ảnh màn hình thực tế để làm bằng chứng trực quan đối chiếu kết quả hiển thị.
          - **Đọc Log & Console Trình duyệt:** Đọc chi tiết log máy chủ và bảng điều khiển `console.log` / `console.error` của trình duyệt để phát hiện các lỗi ngầm, lỗi CSS/JS hoặc lỗi mạng 404/500.
   - **ĐỊNH NGHĨA TOÀN DIỆN VỀ "LỖI" TRONG KIỂM THỬ (COMPREHENSIVE DEFECT DEFINITION):**
     - **Bắt buộc:** Khái niệm "Lỗi" trong kiểm thử của Agent 3 và Agent 4 tuyệt đối **không chỉ giới hạn ở lỗi logic nghiệp vụ hay lỗi backend**, mà bao trùm toàn diện 5 nhóm khuyết tật phần mềm:
       1. *Lỗi Logic & Backend:* Ngoại lệ mã nguồn (500, 422, 404), sai lệch điểm số lũy tiến QĐ 764, sai thuật toán xáo trộn câu hỏi, treo tiến trình nền.
       2. *Lỗi Giao diện & Layout (Visual & Layout):* Vỡ khung, kẹt thanh cuộn (không cuộn được textarea), tràn viền, lệch căn lề, che khuất nội dung giữa 2 cột Split View.
       3. *Lỗi Màu sắc & Đồng nhất Phong cách (Color & Theme Consistency):* Màu sắc không đồng nhất, sai mã màu quy định (ví dụ nút BIÊN DỊCH phải là xanh dương `#0071e3`), lỗi biến đổi màu nền ngoài ý muốn khi con trỏ focus/active (như nền dark mode bị biến thành màu trắng).
       4. *Lỗi Tương tác & Hành vi Người dùng (Interaction & UX):* Nút bấm không phản hồi xúc giác (scale 0.97), dropdown không đóng, thao tác thay thế text làm mất sạch code cũ thay vì chỉ sửa đúng dòng chỉ định, thiếu trạng thái loading/thông báo toast.
       5. *Lỗi Console & Tài nguyên Trình duyệt (Console & Network Assets):* Mọi lỗi màu đỏ trong DevTools `console.error`, unhandled promise rejections, cảnh báo deprecated, lỗi tải font/ảnh 404 hoặc xén nét công thức toán LaTeX/TikZ.

   - **Vòng lặp Phản hồi Khép kín (Coding -> Test -> Blind Test / Review Loop):**
     - Khi Agent Test hoặc Blind Test phát hiện bất kỳ lỗi nào thuộc 5 nhóm trên:
       `Phát hiện lỗi` $\rightarrow$ `Agent 2 (Coding) sửa đổi` $\rightarrow$ `Agent 3 (Test) chạy kiểm thử` $\rightarrow$ `Agent 4 (Blind Test) thẩm định trên trình duyệt thực tế` $\rightarrow$ `Lặp lại quy trình` cho đến khi **hoàn thành 100% mọi yêu cầu được đưa ra mà không còn bất kỳ lỗi nào**.
