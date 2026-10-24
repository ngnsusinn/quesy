# AGENT INSTRUCTIONS & PROJECT RULES - QUESY

## 1. NGUYÊN TẮC CỐT LÕI (MANDATORY STANDING RULES)

1. **QUY TẮC ĐỒNG BỘ TÀI LIỆU, CÔ LẬP CI/CD (STRICT CI ISOLATION), VÒNG LẶP TEST CI & CỔNG COMMIT (DOCS, CI ISOLATION, CI LOOP & PRE-COMMIT GATE):**
   - **Bắt buộc:** Sau **bất kỳ** thay đổi, bổ sung, sửa lỗi (bug fix) hay refactor nào trong mã nguồn (`backend/`, `frontend/`, `tests/`):
     1. **Đồng bộ tài liệu dự án:** Phải rà soát và cập nhật đồng bộ toàn bộ tài liệu dự án trong `docs/` (bao gồm `SRS`, `FRD`, `BRD`, `NFR`, `TEST`, `UC`, `README.md`, `SOURCE_MAP.md`, v.v.) để phản ánh chính xác trạng thái kỹ thuật mới nhất.
     2. **Nguyên tắc Cô lập CI/CD & Phân định Vai trò Tuyệt đối (Strict CI Isolation & Role Separation):**
        - **Tách biệt hoàn toàn:** Sub-Agent đảm nhận làm CI (Sub-Agent 3) tách biệt hoàn toàn với tất cả các sub-agents còn lại.
        - **Cấm truy cập và đọc CI:** Mọi sub-agent khác (Sub-Agent 1, Sub-Agent 2, Sub-Agent 4, v.v.) **tuyệt đối KHÔNG ĐƯỢC PHÉP TRUY CẬP VÀ ĐỌC CI** (`.github/workflows/`, các tệp cấu hình CI).
        - **Độc quyền chỉnh sửa CI:** Chỉ duy nhất sub-Agent đảm nhận làm CI (Sub-Agent 3) mới được phép thực hiện việc truy cập, đọc, viết, chỉnh sửa cấu hình CI/CD.
        - **Tiếp nhận thông tin một chiều vào CI:** Sub-Agent viết CI có toàn quyền đọc và tiếp nhận các thông tin (đặc tả kiến trúc, mã nguồn mới, dependencies phát sinh, kết quả kiểm thử, báo cáo lỗi) từ các sub-agents khác để phục vụ việc tối ưu và cập nhật CI.
     3. **Bắt buộc cập nhật CI đồng bộ theo code mới (Continuous CI Synchronization):**
        - Mỗi khi code có bất kỳ cập nhật gì mới (thêm thư viện Python trong `requirements.txt`, gói npm trong `package.json`, cấu hình font, headless browser/Chromium, biến môi trường `.env`, cờ thực thi, logic test mới...), sub-Agent phụ trách CI bắt buộc phải cập nhật CI theo ngay lập tức để loại bỏ mọi khả năng gây ra lỗi trên môi trường runner (Ubuntu/Linux).
     4. **Cổng kiểm soát Pre-Commit & Vòng lặp Sửa lỗi CI (Pre-Commit CI Gate & CI Fix-and-Test Loop):**
        - **Bắt buộc test qua CI trước khi commit:** Trước khi thực hiện `git commit`, bắt buộc phải chạy và test qua được CI (chạy toàn bộ test suite, kiểm tra cú pháp và môi trường CI runner, 100% test cases đạt). Tuyệt đối cấm commit khi CI chưa pass.
        - **Vòng lặp sửa lỗi CI (CI Loop):** Nếu CI không pass (bất kỳ test case nào fail hoặc môi trường CI bị lỗi):
          `CI Test Thất bại` → `Phân tích nguyên nhân` → `Sub-Agent 2 sửa code / Sub-Agent 3 cập nhật CI & test` → `Sub-Agent 3 chạy lại CI test` → `Lặp lại quy trình` cho đến khi **PASS 100% CI MỚI ĐƯỢC PHÉP COMMIT**.
        - Sau khi CI pass 100%, thực hiện `git commit` ngay với thông điệp rõ ràng, tuân thủ chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).

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

7. **QUY TRÌNH PHỐI HỢP & HOẠT ĐỘNG CỦA 4 SUB-AGENT (SUB-AGENT ORCHESTRATION & EXECUTION PROTOCOL):**
   - **QUY ĐỊNH VỀ MÔ HÌNH AI (SUB-AGENT MODEL MAPPING):**
     1. **Sub-Agent 1 (Analysis, Specs & Docs):** Sử dụng model `gemini 3.8 flash high`, `thinking: ultra`, `temp: 0.2`.
     2. **Sub-Agent 2 (Software Engineering & Coding):** Sử dụng model `gemini 3 flash`, `thinking: medium`.
     3. **Sub-Agent 3 (Automated Test & CI/CD Verification):** Sử dụng model `gemini 3.5 flash lite`.
     4. **Sub-Agent 4 (E2E Browser Blind Test & UI/UX Audit):** Sử dụng model `gemini 3.8 flash high`, `thinking: ultra`, `temp: 0.2`.

   - **QUY ĐỊNH VỀ TRÌNH TỰ HOẠT ĐỘNG & TƯƠNG TÁC GIỮA CÁC SUB-AGENT (EXECUTION PROTOCOL & HANDOFF):**
     1. **Pha 1 - Đọc hiểu, Phân tích & Đặc tả Kiến trúc (Sub-Agent 1):**
        - Sub-Agent 1 chuyên trách đọc hiểu yêu cầu nghiệp vụ, mổ xẻ mã nguồn, phân tích kiến trúc, rà soát và cập nhật đồng bộ toàn bộ tài liệu dự án trong `docs/` (`SRS`, `FRD`, `BRD`, `NFR`, `SOURCE_MAP.md`, `README.md`).
        - Định vị chính xác các file, hàm, API bị ảnh hưởng và xây dựng bản đặc tả kỹ thuật chi tiết.
        - **Quy tắc cô lập CI:** Tuyệt đối không được phép truy cập và đọc CI (`.github/workflows/`).
     2. **Pha 2 - Triển khai Mã nguồn & Trao đổi Làm rõ (Sub-Agent 2):**
        - Sub-Agent 2 chuyên trách lập trình mã nguồn, hiện thực hóa tính năng, sửa lỗi (bug fixes) và tối ưu hóa hiệu năng theo đúng thiết kế của Sub-Agent 1.
        - Giữ gìn chuẩn mực code, chuẩn Apple HIG, tương tác vi mô Emil Kowalski, không tự ý refactor ngoài phạm vi yêu cầu.
        - **Quy tắc hỏi lại Sub-Agent 1:** Trong quá trình thực hiện, **nếu Sub-Agent 2 cần làm rõ bất kỳ điều gì (về nghiệp vụ, logic dữ liệu, API contract, hoặc kiến trúc), bắt buộc phải hỏi lại Sub-Agent 1** để được làm rõ và thống nhất giải pháp trước khi tiếp tục code.
        - **Quy tắc cô lập CI:** Tuyệt đối không được phép truy cập và đọc CI (`.github/workflows/`). Chủ động cung cấp thông tin thay đổi code cho Sub-Agent 3.
     3. **Pha 3 - Cổng Kiểm thử Song song (Parallel Verification Gate - Sub-Agent 3 & Sub-Agent 4):**
        - **QUY TẮC BẮT BUỘC:** **Sub-Agent 3 và Sub-Agent 4 CHỈ ĐƯỢC PHÉP CHẠY SAU KHI Sub-Agent 2 ĐÃ CHẠY XONG HOÀN TOÀN.** Tuyệt đối không kích hoạt Sub-Agent 3 và 4 khi Sub-Agent 2 chưa hoàn thành mã nguồn.
        - Sau khi Sub-Agent 2 hoàn thành mã nguồn, Sub-Agent 3 và Sub-Agent 4 được kích hoạt song song:
          + **Sub-Agent 3 (Automated Test & Độc quyền CI/CD):**
            - *Độc quyền cấu hình CI/CD:* Là Sub-Agent DUY NHẤT được phép truy cập, đọc, viết, chỉnh sửa cấu hình CI/CD (`.github/workflows/ci.yml`). Tách biệt hoàn toàn với các Sub-Agent khác.
            - *Tiếp nhận thông tin một chiều:* Đọc và nhận thông tin từ các Sub-Agent khác (mã nguồn, dependencies, đặc tả, lỗi) để đồng bộ CI.
            - Chuyên trách viết mới, cập nhật test cases tự động (`pytest`), bảo đảm bao phủ kịch bản biên và âm tính.
            - Chạy kiểm thử tự động trên môi trường giả lập CI, đảm bảo 100% test cases vượt qua trước khi commit.
          + **Sub-Agent 4 (E2E Browser Blind Test & UI/UX Audit):**
            - Kiểm thử độc lập, khách quan trên trình duyệt thật (`browser_exec`), thao tác thủ công toàn diện (`fill_input`, `click_at_xy`), chụp ảnh màn hình, đọc DevTools console log/error.
            - *Quy tắc cô lập CI:* Tuyệt đối không được phép truy cập và đọc CI (`.github/workflows/`).
     4. **Pha 4 - Quy trình Xử lý Lỗi & Vòng lặp Hiệu chỉnh (Defect Clarification & Refactoring Loop):**
        - **QUY TẮC BẮT BUỘC:** **Nếu Sub-Agent 3 hoặc Sub-Agent 4 run fail, xảy ra lỗi hoặc tìm ra bất kỳ lỗi nào** (trong 5 nhóm khuyết tật phần mềm hoặc fail test CI):
          1. Sub-Agent 3 và/hoặc Sub-Agent 4 **bắt buộc phải đưa toàn bộ thông tin lỗi (log, traceback, console error, screenshot) và trao đổi lại với Sub-Agent 1 để làm rõ lỗi ở đâu** (nghiệp vụ, kiến trúc, API contract, CSS hay logic).
          2. Sau khi Sub-Agent 1 phân tích và làm rõ nguyên nhân gốc rễ, **Sub-Agent 1 chỉ thị và bắt Sub-Agent 2 code lại (refactor / bug fix)** theo đúng định hướng giải pháp.
          3. Sau khi Sub-Agent 2 code lại xong, hệ thống **tiến hành tiếp tục trình tự tiếp theo:** kích hoạt lại Sub-Agent 3 và Sub-Agent 4 để kiểm thử lại mã nguồn mới.
          4. Lặp lại vòng lặp này liên tục cho đến khi 100% test cases đạt, CI pass và không còn bất kỳ lỗi nào mới được phép nghiệm thu và commit.

   - **ĐỊNH NGHĨA TOÀN DIỆN VỀ "LỖI" TRONG KIỂM THỬ (COMPREHENSIVE DEFECT DEFINITION):**
     - **Bắt buộc:** Khái niệm "Lỗi" trong kiểm thử của Sub-Agent 3 và Sub-Agent 4 tuyệt đối **không chỉ giới hạn ở lỗi logic nghiệp vụ hay lỗi backend**, mà bao trùm toàn diện 5 nhóm khuyết tật phần mềm:
       1. *Lỗi Logic & Backend:* Ngoại lệ mã nguồn (500, 422, 404), sai lệch điểm số lũy tiến QĐ 764, sai thuật toán xáo trộn câu hỏi, treo tiến trình nền.
       2. *Lỗi Giao diện & Layout (Visual & Layout):* Vỡ khung, kẹt thanh cuộn (không cuộn được textarea), tràn viền, lệch căn lề, che khuất nội dung giữa 2 cột Split View.
       3. *Lỗi Màu sắc & Đồng nhất Phong cách (Color & Theme Consistency):* Màu sắc không đồng nhất, sai mã màu quy định (ví dụ nút BIÊN DỊCH phải là xanh dương `#0071e3`), lỗi biến đổi màu nền ngoài ý muốn khi con trỏ focus/active (như nền dark mode bị biến thành màu trắng).
       4. *Lỗi Tương tác & Hành vi Người dùng (Interaction & UX):* Nút bấm không phản hồi xúc giác (scale 0.97), dropdown không đóng, thao tác thay thế text làm mất sạch code cũ thay vì chỉ sửa đúng dòng chỉ định, thiếu trạng thái loading/thông báo toast.
       5. *Lỗi Console & Tài nguyên Trình duyệt (Console & Network Assets):* Mọi lỗi màu đỏ trong DevTools `console.error`, unhandled promise rejections, cảnh báo deprecated, lỗi tải font/ảnh 404 hoặc xén nét công thức toán LaTeX/TikZ.

8. **QUY TẮC TỰ ĐỘNG CHUYỂN HÓA BÁO LỖI THÀNH BÀI TEST CHỐNG TÁI DIỄN CHO SUB-AGENT 4 (AUTOMATIC DEFECT-TO-TEST CONVERSION & ANTI-REGRESSION SHIELD):**
   - **Bắt buộc:** Bất cứ khi nào Người dùng (User) phản ánh, đề xuất, nhắc nhở hoặc báo cáo bất kỳ lỗi nào liên quan đến **Backend** hoặc **Frontend** (ví dụ: lỗi viền kép textarea, lỗi zoom làm co khung preview, sai lệch màu sắc nút bấm, kẹt thanh cuộn, lỗi API 500/422, xén nét ký hiệu LaTeX/TikZ, v.v.):
     1. **Tự động trích xuất tiêu chí kiểm thử (Auto-Extract Test Criteria):**
        - Parent Agent phải phân tích và trích xuất ngay lập tức hiện tượng lỗi thành một hoặc nhiều kịch bản kiểm thử đối chứng cụ thể (Anti-Regression Assertions) với trạng thái kỳ vọng rõ ràng.
     2. **Bổ sung trực tiếp vào nhiệm vụ của Sub-Agent 4 (Inject into Sub-Agent 4 Goal & Context):**
        - Mọi lỗi người dùng từng phản ánh phải được tự động chuyển hóa thành **yêu cầu kiểm thử bắt buộc (Mandatory Checklist)** trong prompt giao việc cho Sub-Agent 4 ở lệnh `delegate_task`.
        - Sub-Agent 4 bắt buộc phải trực tiếp truy cập vào đúng thành phần/giao diện đó trên trình duyệt thật (`browser_exec`), thực hiện thao tác tương tác thực tế (click, gõ phím, cuộn, zoom, đổi tab), chụp ảnh màn hình đối chứng và đọc log console.
        - Sub-Agent 4 phải đưa ra khẳng định rõ ràng trong báo cáo nghiệm thu: lỗi đã được kiểm tra trên trình duyệt và xác nhận biến mất 100% (không tái diễn).
     3. **Bổ sung vào Automated Test Suite (Sub-Agent 3):**
        - Đối với các lỗi thuộc tầng logic, dữ liệu hoặc hợp đồng API, Sub-Agent 3 có trách nhiệm tự động viết bổ sung test case tương ứng vào `tests/` để ngăn chặn lỗi ở mức CI/CD tự động.
     4. **Tiêu chí nghiệm thu nghiêm ngặt (Zero Regression Gate):**
        - Tuyệt đối không đóng yêu cầu nếu Sub-Agent 4 chưa thực hiện bài test đối chứng thực tế trên trình duyệt cho lỗi mà người dùng đã nêu.
