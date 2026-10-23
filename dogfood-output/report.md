# Báo Cáo Blind Test & Anti-Regression QA — Quesy Exam Composer (/composer)

## 1. Tổng Quan & Phạm Vi Kiểm Thử (Executive Summary)
- **Mục tiêu:** Thực hiện Blind Test độc lập trên trình duyệt Chromium thực tế (`browser_exec`) theo **Anti-Regression Checklist** bắt buộc cho màn hình Soạn đề LaTeX (`/composer`).
- **Phạm vi kiểm thử:**
  - Ô input thu gọn `#composer-compact-input` và thanh công cụ AI Copilot dạng viên thuốc (`#composer-ai-compact-bar`).
  - Hộp thoại trợ lý AI mở rộng (`#composer-ai-popup`).
  - Giao tiếp gửi tin nhắn AI Copilot (`/api/v1/composer/chat`).
  - Banner đề xuất diff nội dòng `#composer-pending-diff-banner` (chỉ báo dòng, xóa `-`, thêm `+`).
  - Nút `[Đồng ý]` áp dụng thay đổi thông minh trực tiếp vào editor mã nguồn LaTeX (`#composer-editor-input`).
  - Kiểm tra Console DevTools, không có lỗi JavaScript màu đỏ.
- **Kết quả tổng thể:** **100% ĐẠT (PASS 6/6 tiêu chí)**. Không ghi nhận bất kỳ lỗi JavaScript đỏ nào trong console.

---

## 2. Kết Quả Thực Hiện Chi Tiết Theo Anti-Regression Checklist

| STT | Tiêu chí Kiểm thử Bắt buộc | Thao tác Thực tế trên Trình duyệt | Kết quả Thực tế | Trạng thái |
|:---:|:---|:---|:---|:---:|
| **1** | Click vào ô input `#composer-compact-input`: popup `#composer-ai-popup` **KHÔNG** mở, ô input nhận focus và có thể gõ text | Click và focus vào `#composer-compact-input`. Kiểm tra class của `#composer-ai-popup` và `document.activeElement`. | `popupHidden: true`, `compactBarHidden: false`, `activeElement: 'composer-compact-input'`. Gõ text thành công mà không bị bật popup. | **ĐẠT (PASS)** |
| **2** | Gõ câu lệnh `"Đổi cỡ chữ toàn tài liệu sang 12pt"` vào `#composer-compact-input` và nhấn Enter: popup `#composer-ai-popup` **MỚI MỞ RA**, tin nhắn gửi đi và AI trả lời | Gõ chuỗi câu lệnh vào input và phát sự kiện phím `Enter`. | Popup `#composer-ai-popup` ngay lập tức mở ra (`popupOpened: true`). Tin nhắn được đẩy vào hội thoại, AI gửi phản hồi kèm gợi ý diff. | **ĐẠT (PASS)** |
| **3** | Trên Editor xuất hiện banner gợi ý sửa `#composer-pending-diff-banner` hiển thị đúng dòng, nội dung cũ (-) và nội dung mới (+) | Kiểm tra DOM banner khi AI hoàn tất phản hồi. | Banner xuất hiện trên đỉnh editor: dòng số `1`, nội dung cũ `\documentclass[11pt,a4paper]{article}` (-), nội dung mới `\documentclass[12pt,a4paper]{article}` (+). | **ĐẠT (PASS)** |
| **4** | Nhấn nút `[Đồng ý]` trên banner: đúng dòng khai báo documentclass trên textarea đổi thành `12pt`, không bị mất code xung quanh | Click nút `[Đồng ý]` (`app.composer.applyPendingDiff()`). | Dòng 1 đổi thành `\documentclass[12pt,a4paper]{article}`. Toàn bộ 99 dòng mã nguồn xung quanh được bảo toàn 100%. Banner tự động ẩn. | **ĐẠT (PASS)** |
| **5** | Chụp ảnh màn hình đối chứng trực quan, đọc console log/error đảm bảo không có lỗi JavaScript màu đỏ | Chụp ảnh các bước qua `capture_screenshot()`, kiểm tra `window._caughtErrors` và phân tích hình ảnh qua `vision_analyze`. | Giao diện sắc nét, bố cục 6:4 chuẩn HIG, không có lỗi JS đỏ, không có phần tử đè lệch. | **ĐẠT (PASS)** |
| **6** | Tắt toàn bộ background server sau khi hoàn tất | Quét port 8000 và terminate tiến trình nền. | Đã tắt sạch toàn bộ tiến trình FastAPI/Uvicorn trên cổng 8000. | **ĐẠT (PASS)** |

---

## 3. Bằng Chứng Hình Ảnh Đối Chứng (Visual Evidence)

### Bước 1: Click vào `#composer-compact-input` nhận focus bình thường, popup KHÔNG mở
- **Ảnh chụp:** `dogfood-output/screenshots/step1_click_compact_input.png`
- MEDIA:dogfood-output/screenshots/step1_click_compact_input.png

### Bước 2 & 3: Nhấn Enter, Popup Trợ lý mở và Banner Smart Diff `#composer-pending-diff-banner` xuất hiện
- **Ảnh chụp:** `dogfood-output/screenshots/step3_diff_banner_displayed.png`
- MEDIA:dogfood-output/screenshots/step3_diff_banner_displayed.png

### Bước 4: Nhấn `[Đồng ý]`, Dòng khai báo documentclass đổi thành `12pt` chuẩn xác
- **Ảnh chụp:** `dogfood-output/screenshots/step4_diff_applied_successfully.png`
- MEDIA:dogfood-output/screenshots/step4_diff_applied_successfully.png

### Bước 5: Toàn cảnh Workspace Soạn đề LaTeX & Live PDF Preview (High-DPI)
- **Ảnh chụp:** `dogfood-output/screenshots/step5_full_overview.png`
- MEDIA:dogfood-output/screenshots/step5_full_overview.png

---

## 4. Kiểm Toán Console & Tài Nguyên Mạng (Audit Log)
- `errors.hasErrors`: `[]` (Không có unhandled exceptions).
- `scriptsFailed`: `0` (Tất cả script Tailwind, Lucide, MathJax, PDF.js tải thành công).
- `DOM error indicators`: `0` toast/alert lỗi.
- `Automated Test Suite`: 34/34 tests trong `tests/test_composer.py` PASSED 100%.
