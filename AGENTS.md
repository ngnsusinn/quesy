# AGENT INSTRUCTIONS & PROJECT RULES - QUESY

## 1. NGUYÊN TẮC CỐT LÕI (MANDATORY STANDING RULES)

1. **QUY TẮC ĐỒNG BỘ TÀI LIỆU, ĐỐI CHIẾU CI/CD & COMMIT (DOCS, CI/CD & COMMIT ON EVERY CODE CHANGE):**
   - **Bắt buộc:** Sau **bất kỳ** thay đổi, bổ sung, sửa lỗi (bug fix) hay refactor nào trong mã nguồn (`backend/`, `frontend/`, `tests/`):
     1. Phải rà soát và cập nhật đồng bộ toàn bộ tài liệu dự án trong `docs/` (bao gồm `SRS`, `FRD`, `BRD`, `NFR`, `TEST`, `UC`, `README.md`, v.v.) để phản ánh chính xác trạng thái kỹ thuật mới nhất.
     2. **Bắt buộc đối chiếu và cập nhật cấu hình CI/CD (`.github/workflows/`):** Mỗi khi có thay đổi trong mã nguồn, phải chủ động rà soát xem có phát sinh dependencies mới (Python packages trong `requirements.txt`, npm packages trong `package.json`, font, headless browser/Chromium, biến môi trường `.env`, cờ thực thi...) hay không để cập nhật đồng bộ workflow CI/CD ngay lập tức, bảo đảm 100% test cases vượt qua trên mọi môi trường (Ubuntu/Linux runner).
     3. Chạy toàn bộ test suite (`pytest`) đảm bảo 100% test cases đạt (`56/56 PASSED`).
     4. Thực hiện `git commit` ngay với thông điệp rõ ràng, tuân thủ chuẩn Conventional Commits (`feat:`, `fix:`, `docs:`, `perf:`, `refactor:`).

2. **CHUẨN MỰC KHẢO THÍ QUỐC GIA:**
   - **Thông tư 32/2018/TT-BGDĐT:** Phân cấp cây kiến thức 6 tầng theo Yêu cầu cần đạt (YCCĐ) và Dạng câu hỏi. **Tuyệt đối không phân chia theo các bộ sách giáo khoa thương mại** (như Cánh diều, Kết nối tri thức, Chân trời sáng tạo).
   - **Quyết định 764/QĐ-BGDĐT:** Câu hỏi trắc nghiệm Đúng/Sai 4 khẳng định phải áp dụng logic tính điểm bậc thang: Đúng 1 ý = 0.1đ; Đúng 2 ý = 0.25đ; Đúng 3 ý = 0.5đ; Đúng cả 4 ý = 1.0đ.

3. **CHUẨN MỰC XUẤT BẢN CÔNG THỨC TOÁN & TÀI LIỆU WORD:**
   - **MathType 7.0 OLE Vector WMF (`math_format="mathtype"`):**
     - Luôn sử dụng ảnh Vector WMF (`image/x-wmf`) chuẩn APM header (`magic: 0x9AC6CDD7`, SCALE=20 twips/pt, 1440 DPI) làm hình đại diện nhúng OLE. Tuyệt đối không dùng ảnh raster PNG gây mờ vỡ nét và mất khả năng kích hoạt OLE.
     - Luồng OLE CFB nhị phân phải chứa `\x01CompObj` (`MathType 7.0 Equation`, root CLSID `{0002CE03-0000-0000-C000-000000000046}`), `\x01Ole`, `\x03ObjInfo` (`0x0004`), và `Equation Native` stream chứa MTEF v5 sinh từ MathJax MathML.
     - Phải bảo đảm tính năng chỉnh sửa 2 chiều: Giáo viên click đúp trong Microsoft Word sẽ mở thẳng MathType 7 để sửa công thức bình thường.
   - **Tự động chuyển đổi bảng thống kê:** Mọi mảng bảng số liệu LaTeX `\begin{array}` hoặc `tabular` trong đề thi phải được tự động chuyển thành bảng Word native `<w:tbl>` căn giữa có viền mảnh, chống lỗi hộp đen (black box) khi xuất PDF.
   - **Quy cách in ấn:** Toàn bộ văn bản xuất bản phải tuân thủ chuẩn khổ giấy **A4 Portrait (210 x 297 mm)**, lề trang 1.5 cm - 1.8 cm, font Times New Roman 11pt, giãn dòng 1.15.

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
