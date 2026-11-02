# BẢN ĐẶC TẢ KỸ THUẬT CHI TIẾT (TECHNICAL SPECIFICATION)
## Tính năng: Split View Trợ lý AI, Cải tiến Tìm & Thay thế, và Mở rộng Chat Q&A
**Dành cho: Sub-Agent 2 (Software Engineering & Coding)**  
**Dự án:** Quesy - Nền tảng Khảo thí Toán học Quốc Gia 2025  
**Phiên bản:** 1.0  
**Ngày lập:** 02/11/2026  

---

### 1. TỔNG QUAN YÊU CẦU & BÀI TOÁN KỸ THUẬT

#### 1.1. Mục tiêu
Bản đặc tả này cung cấp thiết kế chi tiết để Sub-Agent 2 hiện thực hóa 3 nhóm tính năng trên phân hệ Soạn đề (`/composer`):
1. **Split View Trợ lý AI (Copilot Pane Split & Auto-Resize Editor):**
   - Loại bỏ cơ chế popup phủ đè lên editor dạng `absolute bottom-0 overlay`.
   - Chuyển sang mô hình chia đôi chiều dọc (Vertical Split View) trong cột trái.
   - Khi Trợ lý AI mở, editor tự động thu nhỏ lại để dùng song song cả hai.
   - Khi đóng Trợ lý AI, editor tự động phóng to chiếm trọn 100% chiều cao cột trái.
2. **Cải tiến Tìm & Thay thế Tự nhiên (Flexible Search & Replace):**
   - Hỗ trợ các cú pháp tiếng Việt linh hoạt: "thay X bằng Y", "tìm và thay thế X thành Y", "đổi X sang Y", "sửa X thành Y", không bắt buộc phải có dấu ngoặc kép.
   - Hỗ trợ thay thế linh hoạt: câu hỏi, biểu thức toán, biến số, thời gian làm bài, tên trường/sở, đổi đáp án trắc nghiệm.
3. **Mở rộng Hệ thống Chat Hỏi Đáp Khảo Thí & Sư Phạm (Educational Q&A Copilot):**
   - Giải đáp quy chế Quyết định 764/QĐ-BGDĐT (cách tính điểm bậc thang 0.1, 0.25, 0.5, 1.0), cấu trúc đề thi 2025 (3 phần, 22 câu), quy định Thông tư 32/2018/TT-BGDĐT. Không tự tiện chèn câu hỏi mẫu lạc đề.
   - Giải thích cú pháp gói lệnh `ex_test.sty`, hình vẽ `TikZ`, bảng biến thiên `tkz-tab` kèm ví dụ minh họa trực quan.
   - Kiểm tra và thống kê đề thi hiện tại: phân tích trực tiếp `current_latex`, thống kê số câu đã có ở Phần I (X/12), Phần II (Y/4), Phần III (Z/6), báo cáo phần nào thiếu/thừa.
   - Hướng dẫn giải và giải thích sư phạm câu hỏi trong đề thi hiện tại.

---

### 2. THIẾT KẾ KIẾN TRÚC & GIAO DIỆN (UI/UX) - TÍNH NĂNG 1: SPLIT VIEW

#### 2.1. Cấu trúc DOM hiện tại vs Cấu trúc mới
**Hiện tại:**
- `#composer-ai-popup` nằm bên trong `#composer-editor-pane` với class `hidden absolute bottom-0 left-0 right-0 z-30 h-[56%]`.
- Khi hiển thị, popup che lấp nửa dưới của khung soạn thảo `#composer-editor-input`.

**Cấu trúc mới:**
- Tách `#composer-ai-popup` thành một khung flex sibling độc lập nằm dưới `#composer-editor-pane` bên trong `#composer-left-col`.
- `#composer-left-col` có cấu trúc:
  ```html
  <div id="composer-left-col" class="w-full lg:w-[60%] flex flex-col h-full min-h-0 overflow-hidden relative shrink-0">
    <!-- 1. Hộp soạn thảo LaTeX: khi AI đóng chiếm 100%, khi AI mở co lại linh hoạt -->
    <div id="composer-editor-pane" class="w-full flex-1 min-h-[140px] bg-[#141824] rounded-xl border border-[#272f42] flex flex-col overflow-hidden shadow-xs relative transition-[height,flex] duration-200">
      ... (toolbar, diff banner, editor body, status bar, compact prompt bar) ...
    </div>

    <!-- 2. Khung Trợ lý AI Copilot (Split View): khi mở là relative flex item, khi đóng là hidden -->
    <div id="composer-ai-popup" class="hidden relative w-full bg-[#18181b] border border-white/10 shadow-2xl rounded-xl flex flex-col overflow-hidden shrink-0 mt-2 transition-[height] duration-200">
      ... (header, resize handle, chat messages, input container) ...
    </div>
  </div>
  ```

#### 2.2. Trạng thái hiển thị & Logic điều khiển (Frontend - `app.js`)
1. **Khi mở Trợ lý AI (`openAIPopup`):**
   - `#composer-ai-popup`: Xóa class `hidden`, hiển thị dạng `flex flex-col`.
   - Chiều cao popup (`popup.style.height`): Thiết lập theo giá trị lưu trữ trong `localStorage` (`quesy_composer_ai_height`), mặc định là `48%` (hoặc `340px` trên màn hình tiêu chuẩn).
   - `#composer-editor-pane`: Tự động co lại nhờ `flex-1 min-h-[140px]`. Cả hai khung chia sẻ chiều cao của `#composer-left-col`.
   - `#composer-ai-compact-bar`: Thêm class `hidden` để tránh trùng lặp ô nhập.
   - Cuộn khung chat `composer-chat-messages` xuống đáy.
2. **Khi đóng Trợ lý AI (`closeAIPopup`):**
   - `#composer-ai-popup`: Thêm class `hidden`.
   - `#composer-editor-pane`: Tự động nở rộng chiếm trọn 100% chiều cao của `#composer-left-col`.
   - `#composer-ai-compact-bar`: Xóa class `hidden`, hiển thị thanh pill bar nổi ở đáy editor.
3. **Kéo thả điều chỉnh tỷ lệ chiều cao (`initAIPopupResizer`):**
   - Thanh pill handle `#composer-ai-resize-handle` đặt ở thanh header của popup.
   - Khi kéo chuột (`mousedown` -> `mousemove`):
     - Lấy kích thước của `#composer-left-col`: `const colRect = leftCol.getBoundingClientRect();`.
     - Tính chiều cao mới: `const newH = colRect.bottom - e.clientY;`.
     - Quy đổi tỷ lệ phần trăm: `let pct = (newH / colRect.height) * 100;`.
     - Giới hạn an toàn: `pct = Math.min(80, Math.max(20, pct));`.
     - Gán: `popup.style.height = `${pct.toFixed(1)}%`;`.
     - Lưu vào `localStorage.setItem('quesy_composer_ai_height', popup.style.height);`.
4. **Phím tắt và Nút Phóng to / Thu nhỏ (`toggleAIPopupFullscreen`):**
   - Khi bấm nút phóng to trên header:
     - Nếu đang ở chế độ lớn (`>= 80%`), chuyển về mặc định `48%`.
     - Nếu đang ở chế độ thường, chuyển thành `82%` (editor co lại thành `18%`).

---

### 3. THIẾT KẾ CHI TIẾT - TÍNH NĂNG 2: TÌM & THAY THẾ TỰ NHIÊN (SEARCH & REPLACE)

#### 3.1. Các mẫu câu tiếng Việt tự nhiên cần nhận diện
Sub-Agent 2 cần bổ sung bộ regex và logic phân tích ngôn ngữ tự nhiên trong `extract_all_diffs_from_text` và `composer_chat_endpoint` của `backend/routers/composer.py`:

| Trường hợp | Mẫu câu người dùng | Cặp trích xuất (old_text -> new_text) |
|---|---|---|
| **Chuỗi chung không ngoặc kép** | "thay 90 phút bằng 50 phút" | `"90 phút"` -> `"50 phút"` |
| **Tìm và thay thế** | "tìm và thay thế 2024 thành 2025" | `"2024"` -> `"2025"` |
| **Đổi sang** | "đổi TRƯỜNG THPT X sang TRƯỜNG THPT Y" | `"TRƯỜNG THPT X"` -> `"TRƯỜNG THPT Y"` |
| **Sửa thành** | "sửa điểm A thành điểm B" | `"điểm A"` -> `"điểm B"` |
| **Thay thế câu hỏi** | "thay câu 1 bằng câu ..." hoặc "đổi câu hỏi 3 thành ..." | Khối câu hỏi $N$ cũ -> Khối câu hỏi mới `\begin{ex}...\end{ex}` |
| **Đổi đáp án đúng** | "đổi đáp án câu 2 sang D" hoặc "thay đáp án đúng thành C" | Khối `\choice` cũ với `\True` tại phương án cũ -> Khối `\choice` mới với `\True` tại phương án mới |
| **Biểu thức toán học** | "thay biểu thức x^2 + 1 bằng x^2 - 1" | `"$x^2 + 1$"` (hoặc `"x^2 + 1"`) -> `"$x^2 - 1$"` |
| **Biến số** | "thay biến x bằng biến t" hoặc "đổi biến x thành y" | Khớp biến trong ngữ cảnh hoặc dòng chứa biến |
| **Thời gian làm bài** | "đổi thời gian làm bài thành 50 phút" | Dòng chứa `Thời gian làm bài` cập nhật số phút |
| **Tên trường / Sở GD** | "thay tên trường thành THPT Chuyên Lê Hồng Phong" | Dòng chứa `TRƯỜNG THPT` cập nhật tên mới |

#### 3.2. Thuật toán phân tích cú pháp không ngoặc kép
Triển khai hàm helper:
```python
def parse_flexible_replace_command(text: str) -> Optional[Tuple[str, str]]:
    """Trích xuất cặp (old_term, new_term) từ câu lệnh tiếng Việt tự nhiên."""
    patterns = [
        # 1. Có ngoặc kép/nháy đơn
        r'(?:tìm\s+và\s+thay\s+thế|thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]\s+(?:bằng|thành|sang|với|bởi|by|with)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]',
        # 2. "tìm và thay thế X thành/bằng Y" (không ngoặc kép)
        r'tìm\s+và\s+thay\s+thế\s+(.+?)\s+(?:thành|bằng|sang|bởi)\s+(.+)',
        # 3. "thay thế X bằng/thành/sang Y" (không ngoặc kép)
        r'thay\s+thế\s+(.+?)\s+(?:bằng|thành|sang|bởi)\s+(.+)',
        # 4. "thay X bằng/thành/sang Y" (không ngoặc kép)
        r'thay\s+(.+?)\s+(?:bằng|thành|sang|bởi)\s+(.+)',
        # 5. "đổi X sang/thành/bằng Y" (không ngoặc kép)
        r'đổi\s+(.+?)\s+(?:sang|thành|bằng)\s+(.+)',
        # 6. "sửa X thành/sang/bằng Y" (không ngoặc kép)
        r'sửa\s+(.+?)\s+(?:thành|sang|bằng)\s+(.+)',
        # 7. "chuyển X sang/thành Y" (không ngoặc kép)
        r'chuyển\s+(.+?)\s+(?:sang|thành)\s+(.+)',
    ]
    ...
```
Sau khi trích xuất được `old_term` và `new_term`:
- Dùng `find_in_latex(old_term, current_latex)` để tìm vị trí xuất hiện trong tài liệu hiện tại.
- Nếu `old_term` xuất hiện dưới dạng chuỗi con trong 1 dòng (ví dụ "90 phút" trong dòng thời gian), `find_in_latex` phải ưu tiên trả về đúng chuỗi con `"90 phút"` (nếu nó xuất hiện nguyên bản), hoặc thay thế chuỗi con bên trong dòng đó để tạo ra diff cấp độ dòng chính xác.
- Tạo `DiffSuggestion(action="replace", old_text=matched_old, new_text=new_term, description=f"Thay thế '{old_term}' thành '{new_term}'")`.
- Trả về `ChatResponse` kèm thông điệp giải thích rõ ràng và khối ````diff`.

---

### 4. THIẾT KẾ CHI TIẾT - TÍNH NĂNG 3: MỞ RỘNG CHAT HỎI ĐÁP (Q&A COPILOT)

#### 4.1. Phân loại Ý định (Intent Classification)
Trước khi xử lý trong `composer_chat_endpoint`, hệ thống phân loại ý định người dùng thành 2 nhóm:
1. **Action / Generate Intent:** Người dùng yêu cầu tạo mới đề thi, chèn template, tạo câu hỏi mới.
2. **Q&A / Pedagogical / Explanatory Intent:** Người dùng đặt câu hỏi giải thích, hỏi quy chế, hỏi cú pháp, kiểm tra thống kê hoặc hỏi cách giải.

Dấu hiệu nhận diện Q&A Intent:
- Chứa các từ khóa nghi vấn: "như thế nào", "là gì", "tại sao", "hướng dẫn", "giải thích", "cách tính", "quy chế", "quy định", "thống kê", "kiểm tra", "bao nhiêu câu", "đủ chưa", "thiếu gì", "cú pháp", "cách dùng", "nghĩa là gì".

#### 4.2. Bốn Kịch Bản Q&A Chi Tiết

##### Kịch bản 1: Hỏi về quy chế & cấu trúc đề thi 2025
- **Trigger keywords:** "quy chế", "quy định", "quyết định 764", "qđ 764", "764", "cách tính điểm", "điểm bậc thang", "tính điểm đúng sai", "thông tư 32", "tt 32", "cấu trúc đề thi 2025", "cấu trúc đề thi", "bao nhiêu câu", "thời gian làm bài".
- **Hành vi xử lý:**
  - Giải thích chuẩn xác, chi tiết từng nội dung người dùng hỏi:
    + **QĐ 764/QĐ-BGDĐT:** Thang điểm bậc thang Phần II Đúng/Sai 4 khẳng định: Đúng 1 ý = 0.1 điểm; Đúng 2 ý = 0.25 điểm; Đúng 3 ý = 0.5 điểm; Đúng 4 ý = 1.0 điểm. Tối đa 4 câu = 4.0 điểm.
    + **Cấu trúc Đề thi Tốt nghiệp THPT 2025 Môn Toán:** Tổng thời gian 90 phút, 22 câu hỏi, thang điểm 10.0:
      * Phần I: 12 câu trắc nghiệm nhiều phương án (mỗi câu 0.25đ -> tổng 3.0đ).
      * Phần II: 4 câu trắc nghiệm Đúng/Sai 4 khẳng định (điểm bậc thang -> tổng 4.0đ).
      * Phần III: 6 câu trắc nghiệm Trả lời ngắn (mỗi câu 0.5đ -> tổng 3.0đ).
    + **Thông tư 32/2018/TT-BGDĐT:** Ma trận định hướng năng lực 4 mức độ (40% Nhận biết, 30% Thông hiểu, 20% Vận dụng, 10% Vận dụng cao), phân chia theo Yêu cầu cần đạt (YCCĐ), hoàn toàn độc lập với các bộ sách giáo khoa thương mại.
  - **Ràng buộc:** Tuyệt đối không xuất mã đề thi mẫu lạc đề hay chèn template câu hỏi vào khung soạn thảo khi người dùng chỉ hỏi quy chế.

##### Kịch bản 2: Hỏi về cú pháp ex_test, TikZ, tkz-tab
- **Trigger keywords:** "cú pháp ex_test", "hướng dẫn ex_test", "lệnh choice", "lệnh choicetf", "shortans", "cú pháp tikz", "hướng dẫn vẽ tikz", "cú pháp tkz-tab", "hướng dẫn tkz-tab", "bảng biến thiên tkz-tab".
- **Hành vi xử lý:**
  - Trình bày sư phạm, nêu rõ cấu trúc lệnh, các tham số bắt buộc và kèm ví dụ minh họa ngắn gọn:
    + `ex_test.sty`: Trình bày môi trường `\begin{ex}...\end{ex}`, lệnh `\choice{A}{\True B}{C}{D}`, lệnh `\choiceTF[1]` (nhấn mạnh tham số `[1]` để mỗi ý 1 dòng), lệnh `\shortans{kết_quả}`, và môi trường `\begin{loigiai}...\end{loigiai}`.
    + `TikZ`: Trình bày môi trường `\begin{tikzpicture}...\end{tikzpicture}`, hệ trục `\draw[->]`, điểm `\coordinate`, lệnh vẽ hàm số `plot` với khuyến nghị `samples=50` để tối ưu XeTeX, và quy tắc bất biến căn giữa `\begin{center}`.
    + `tkz-tab`: Trình bày `\tkzTabInit`, `\tkzTabLine`, `\tkzTabVar` với ví dụ bảng biến thiên hàm bậc 3 hoặc phân thức.
  - Cung cấp nút tiện ích `suggested_latex` để người dùng có thể chèn ví dụ nếu muốn.

##### Kịch bản 3: Thống kê & Kiểm tra đề thi hiện tại
- **Trigger keywords:** "kiểm tra đề", "thống kê đề", "đủ câu chưa", "đã có bao nhiêu câu", "đề còn thiếu gì", "kiểm tra cấu trúc", "soát đề", "tiến độ đề thi".
- **Hành vi xử lý:**
  - Phân tích trực tiếp chuỗi `current_latex`:
    + Đếm số câu Phần I (chứa `\choice`): chuẩn 12 câu.
    + Đếm số câu Phần II (chứa `\choiceTF`): chuẩn 4 câu.
    + Đếm số câu Phần III (chứa `\shortans` hoặc `\SA`): chuẩn 6 câu.
    + Kiểm tra Header đề thi (2 cột, trường/sở, kỳ thi, mã đề).
  - Trả về bảng tổng hợp trực quan:
    * **Tổng số câu hiện có:** $N / 22$ câu.
    * **Phần I (Trắc nghiệm 4 lựa chọn):** $A / 12$ câu (đạt / thiếu $12 - A$ câu / thừa).
    * **Phần II (Đúng/Sai QĐ 764):** $B / 4$ câu (đạt / thiếu $4 - B$ câu / thừa).
    * **Phần III (Trả lời ngắn):** $C / 6$ câu (đạt / thiếu $6 - C$ câu / thừa).
    * **Tiêu đề đề thi:** Đã có / Chưa có tiêu đề 2 cột chuẩn.
  - Gợi ý cụ thể bước hành động tiếp theo cho giáo viên (ví dụ: "Bạn cần soạn thêm 3 câu cho Phần I và 2 câu cho Phần III để hoàn thiện đề thi chuẩn Quốc Gia 2025").

##### Kịch bản 4: Hướng dẫn giải / Giải thích câu hỏi trong đề
- **Trigger keywords:** "hướng dẫn giải câu", "giải thích câu", "giải câu", "tại sao câu", "cách giải câu", "hướng dẫn câu".
- **Hành vi xử lý:**
  - Nhận diện số thứ tự câu hỏi cần giải: "câu 1", "câu 2", "câu 3 phần 3"...
  - Dùng `find_nth_question_in_latex(current_latex, q_num, section=sec)` để trích xuất nội dung câu hỏi từ mã LaTeX hiện tại.
  - Phân tích đề bài toán:
    + Đưa ra phương pháp giải sư phạm (bước 1, bước 2, bước 3).
    + Nếu có lời giải trong `\begin{loigiai}`, phân tích và giải thích chi tiết các biến đổi toán học.
    + Đối với câu hỏi trắc nghiệm: chỉ rõ vì sao chọn phương án đúng, vì sao các phương án khác sai.
    + Đối với câu hỏi Đúng/Sai: giải thích chi tiết tính đúng/sai của từng ý a), b), c), d).

---

### 5. DANH MỤC TỆP TIN ẢNH HƯỞNG & NHIỆM VỤ CỤ THỂ CHO SUB-AGENT 2

1. **`frontend/index.html`:**
   - Điều chỉnh vị trí `#composer-ai-popup`: Di chuyển ra ngoài `#composer-editor-pane`, trở thành flex sibling trực tiếp bên trong `#composer-left-col`.
   - Cập nhật class CSS: `#composer-ai-popup` dùng `relative flex-col` thay cho `absolute bottom-0`.
   - Giữ nguyên các ID phần tử con bên trong popup để tương thích hoàn toàn.
2. **`frontend/static/app.js`:**
   - Cập nhật `openAIPopup`: Mở popup dưới dạng split view, khôi phục chiều cao từ `localStorage`, ẩn compact bar.
   - Cập nhật `closeAIPopup`: Ẩn popup, editor pane tự động mở rộng toàn chiều cao, hiện compact bar.
   - Cập nhật `initAIPopupResizer`: Tính toán chiều cao dựa trên `composer-left-col` thay vì `composer-editor-pane`.
   - Cập nhật `toggleAIPopupFullscreen`: Chuyển đổi giữa 48% và 82% chiều cao của cột trái.
3. **`frontend/static/style.css`:**
   - Cập nhật CSS cho `#composer-ai-popup`: Xóa các thuộc tính absolute cũ nếu có, bảo đảm hiển thị đẹp mắt, viền bo tròn, shadow đồng bộ Apple HIG.
4. **`backend/routers/composer.py`:**
   - Cập nhật `extract_all_diffs_from_text`: Bổ sung nhận diện thay thế tự nhiên không ngoặc kép (`parse_flexible_replace_command`), hỗ trợ đổi đáp án, thời gian, tên trường, biểu thức.
   - Tối ưu hóa `composer_chat_endpoint`:
     - Nhận diện các kịch bản Q&A (Quy chế QĐ 764, TT 32, Cấu trúc 2025; Cú pháp ex_test/TikZ/tkz-tab; Thống kê đề thi; Hướng dẫn giải).
     - Triệt tiêu việc chèn câu hỏi mẫu lạc đề khi người dùng đang hỏi đáp thông tin.
     - Triển khai logic thống kê số lượng câu hỏi thực tế trong `current_latex`.

---

### 6. QUY TẮC CÔ LẬP CI DÀNH CHO SUB-AGENT 2
- **Tuyệt đối KHÔNG ĐƯỢC PHÉP TRUY CẬP VÀ ĐỌC CI** (`.github/workflows/`).
- Sau khi hoàn thành code, bàn giao kết quả và danh mục tệp tin thay đổi cho Sub-Agent 3 (Automated Test & CI) và Sub-Agent 4 (E2E Browser Blind Test).
