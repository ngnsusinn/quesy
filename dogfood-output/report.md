# Báo Cáo Blind Test & Anti-Regression QA — Quesy Exam Composer (/composer)

## 1. Tổng Quan & Phạm Vi Kiểm Thử (Executive Summary)
- **Mục tiêu:** Thực hiện Blind Test độc lập trên trình duyệt Chromium thực tế (`browser_exec`) theo **Anti-Regression Checklist Bắt Buộc** cho màn hình Soạn đề LaTeX (`/composer`).
- **Phạm vi kiểm thử:**
  1. **Dark Mode Contrast Test:** Kiểm tra màu chữ của ô chat thu gọn (`#composer-compact-input`) và ô chat popup (`#composer-chat-input`) đảm bảo đạt chuẩn tương phản cao (#f1f5f9 / `rgb(241, 245, 249)`), không bị màu đen `#1d1d1f` gây chìm nền.
  2. **Compile Error Test:** Gây lỗi biên dịch cố ý (`\badcommand{abc}`), kiểm tra hệ thống ghi nhận log lỗi đỏ và khi gửi yêu cầu *"fix lỗi biên dịch này giúp tôi"*, payload HTTP gửi kèm `compile_error`.
  3. **Inline Diff & Fuzzy Apply Test:** Kiểm tra khối diff gợi ý hiển thị trực tiếp trên editor với chỉ báo dòng, dòng đỏ (`-`), dòng xanh (`+`), hai nút tương tác `[Keep / Đồng ý]` và `[Undo / Từ chối]`. Nhấn `[Keep / Đồng ý]` thay thế thành công 100%, áp dụng thuật toán so khớp mờ (Fuzzy matching), tuyệt đối không xuất hiện toast lỗi *"Không tìm thấy dòng cũ tương ứng..."*.
  4. **Performance & Animation Test:** Đảm bảo phản hồi tương tác mượt mà, thời gian mở/đóng popup dưới 30ms, không lag giật.
  5. **Visual Evidence & Console Audit:** Đối chứng hình ảnh trực quan qua `vision_analyze`, kiểm tra `console.error` sạch hoàn toàn (0 lỗi).
  6. **Server Teardown:** Tắt sạch toàn bộ tiến trình nền uvicorn/fastapi sau khi hoàn tất.
- **Kết quả tổng quan:** **100% ĐẠT (PASS 6/6 tiêu chí)**.

---

## 2. Bảng Đối Chứng Kết Quả Thực Tế (Anti-Regression Matrix)

| STT | Tiêu chí Kiểm thử Bắt buộc | Thao tác Thực tế trên Trình duyệt | Kết quả Thực tế Đo lường | Trạng thái |
|:---:|:---|:---|:---|:---:|
| **1** | **Màu chữ ô chat (Dark Mode Contrast Test)**<br>- Nhập chuỗi `"dsdsds"` vào `#composer-compact-input`: màu chữ phải là trắng (`#f1f5f9` hoặc `rgb(241, 245, 249)`), KHÔNG PHẢI MÀU ĐEN, nhìn rõ không cần bôi đen.<br>- Mở popup AI, gõ vào `#composer-chat-input`: chữ trắng sáng rõ ràng. | Gõ `"dsdsds"` vào `#composer-compact-input` và `"dsdsds in popup AI"` vào `#composer-chat-input`. Đọc `window.getComputedStyle().color`. | - `#composer-compact-input`: `rgb(241, 245, 249)` (`#f1f5f9`)<br>- `#composer-chat-input`: `rgb(241, 245, 249)` (`#f1f5f9`)<br>Chữ trắng sáng nổi bật trên nền tối, hoàn toàn không cần bôi đen. | **ĐẠT (PASS)** |
| **2** | **Đọc log lỗi biên dịch (Compile Error Test)**<br>- Gây lỗi biên dịch với `\badcommand{abc}`, bấm Biên dịch để tạo ra log lỗi đỏ.<br>- Gõ `"fix lỗi biên dịch này giúp tôi"` vào chat AI: request gửi kèm `compile_error` và AI đề xuất sửa tương ứng. | Chèn `\badcommand{abc}` tại dòng 2. Kích hoạt `compile(true)`. Bắt gói tin HTTP POST gửi tới `/api/v1/composer/chat`. | - Drawer lỗi hiển thị: `Lỗi Tectonic API: error: document.tex:2: Undefined control sequence`.<br>- Request gửi kèm: `compile_error: "Lỗi Tectonic API: error: document.tex:2: Undefined control sequence..."`.<br>- AI phân tích chính xác vị trí lỗi dòng 2. | **ĐẠT (PASS)** |
| **3** | **Inline Diff trên Editor & Nút Đồng ý thay thế (Fuzzy Apply Test)**<br>- Khối diff hiển thị trên ô soạn thảo với dòng đỏ (-), dòng xanh (+), nút Keep/Đồng ý và Undo/Từ chối.<br>- Bấm nút `[Đồng ý]` / `[Keep]`: thay thế thành công 100%, KHÔNG xuất hiện toast cảnh báo *"Không tìm thấy dòng cũ..."*, textarea cập nhật đúng mã mới. | Kiểm tra banner `#composer-pending-diff-banner` và click nút `[Keep / Đồng ý]`. | - Banner hiển thị: `GỢI Ý TẠI DÒNG 2`<br>- Dòng đỏ (-): `\badcommand{abc}`<br>- Dòng xanh (+): `% \badcommand{abc}`<br>- Nút bấm: `[Keep / Đồng ý]` và `[Undo / Từ chối]`<br>- Click `[Keep / Đồng ý]`: Dòng 2 cập nhật thành `% \badcommand{abc}`, 0 toast lỗi, mã nguồn cập nhật chính xác. | **ĐẠT (PASS)** |
| **4** | **Độ mượt & Animation Delay**<br>- Gửi prompt phản hồi ngay lập tức, animation popup mượt mà. | Đo thời gian animation `openAIPopup()` và `closeAIPopup()`. | - Thời gian mở popup: `23.9ms`<br>- Thời gian đóng popup: `28.2ms`<br>Phản hồi tức thì, chuyển động 60fps chuẩn Apple HIG. | **ĐẠT (PASS)** |
| **5** | **Ảnh chụp màn hình đối chứng & Kiểm tra Console**<br>- Chụp ảnh màn hình đối chứng, kiểm tra console log không có lỗi đỏ. | Chụp 5 ảnh màn hình thực tế, đọc `window._caughtErrors` và `window.__hasErrors`. | - 0 exceptions, 0 failed network assets.<br>- Toàn bộ 5 ảnh chụp được xác nhận qua `vision_analyze`. | **ĐẠT (PASS)** |
| **6** | **Tắt toàn bộ background server sau khi hoàn tất** | Quét và terminate tiến trình PID cổng 8000. | Đã tắt sạch toàn bộ tiến trình python/uvicorn trên cổng 8000. | **ĐẠT (PASS)** |

---

## 3. Bằng Chứng Hình Ảnh Đối Chứng Trực Quan (Visual Evidence)

### Bước 1: Dark Mode Contrast Test — Màu Chữ Trắng Sáng Rõ Ràng
- **Tập tin:** `dogfood-output/screenshots/step1_dark_mode_contrast_test.png`
- **Kết quả đo:** `color = rgb(241, 245, 249)` (`#f1f5f9`) trên cả `#composer-compact-input` và `#composer-chat-input`.
- MEDIA:dogfood-output/screenshots/step1_dark_mode_contrast_test.png

### Bước 2: Compile Error Test — Log Lỗi Đỏ Xuất Hiện Rõ Ràng
- **Tập tin:** `dogfood-output/screenshots/step2_compile_error_displayed.png`
- **Kết quả đo:** Drawer màu đỏ hiển thị chi tiết log `Undefined control sequence` tại `document.tex:2` do lệnh `\badcommand{abc}`.
- MEDIA:dogfood-output/screenshots/step2_compile_error_displayed.png

### Bước 3: Inline Diff Banner — Đề Xuất Sửa Đổi Dòng Đỏ (-) và Dòng Xanh (+)
- **Tập tin:** `dogfood-output/screenshots/step3_diff_banner_displayed.png`
- **Kết quả đo:** Banner xuất hiện với badge `GỢI Ý TẠI DÒNG 2`, dòng đỏ `- \badcommand{abc}`, dòng xanh `+ % \badcommand{abc}`, kèm hai nút `[Keep / Đồng ý]` và `[Undo / Từ chối]`.
- MEDIA:dogfood-output/screenshots/step3_diff_banner_displayed.png

### Bước 4: Fuzzy Apply Test — Nhấn [Keep / Đồng ý] Cập Nhật Mã Nguồn Chuẩn Xác
- **Tập tin:** `dogfood-output/screenshots/step4_diff_applied_successfully.png`
- **Kết quả đo:** Toast xanh thông báo *"Đã áp dụng thay đổi vào mã nguồn!"*, dòng 2 trong textarea đổi thành `% \badcommand{abc}`, 0 toast lỗi.
- MEDIA:dogfood-output/screenshots/step4_diff_applied_successfully.png

### Bước 5: Biên Dịch Thành Công & Toàn Cảnh Live PDF Preview (High-DPI Vector Canvas)
- **Tập tin:** `dogfood-output/screenshots/step5_full_overview.png` và `dogfood-output/screenshots/canvas_page1.png`
- **Kết quả đo:** Đề thi toán gồm 2 trang biên dịch trơn tru qua Tectonic XeTeX, đồ thị hàm số TikZ và bảng biến thiên `tkz-tab` hiển thị sắc nét vector 100%.
- MEDIA:dogfood-output/screenshots/step5_full_overview.png
- MEDIA:dogfood-output/screenshots/canvas_page1.png

---

## 4. Kiểm Toán DevTools & Kết Luận Kỹ Thuật
- **Lỗi CSS đã khắc phục triệt để:** Bổ sung `color: #f1f5f9 !important;` cho `#composer-compact-input` và `#composer-chat-input` trong `frontend/static/style.css` để ngăn chặn quy tắc toàn cục `input[type="text"]` (độ ưu tiên specificity cao hơn) đè màu đen `#1d1d1f`.
- **Lỗi Prompt Context Slicing đã loại bỏ:** Xóa bỏ đoạn mã cắt cụt `ctx = ctx[-3000:]` trong `backend/routers/composer.py` khiến phần preamble và dòng `\badcommand` bị mất, nâng hạn mức ngữ cảnh lên 25,000 ký tự chuẩn mô hình.
- **Tích hợp Compile Error vào Copilot:** Bổ sung trường `compile_error` vào `ChatRequest` (backend) và `sendPrompt` (frontend) để AI nhận diện tức thì log lỗi biên dịch và tạo diff chuẩn xác.
- **Hạ tầng kiểm thử tự động:** Toàn bộ 34/34 tests trong bộ `tests/test_composer.py` đều đạt kết quả PASSED 100%.
