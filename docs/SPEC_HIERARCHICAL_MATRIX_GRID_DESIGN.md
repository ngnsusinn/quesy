# BẢN ĐẶC TẢ KIẾN TRÚC & THIẾT KẾ KỸ THUẬT CHI TIẾT
## CHUYỂN ĐỔI GIAO DIỆN MA TRẬN ĐỀ THI SANG BẢNG PHÂN CẤP ĐA TẦNG
### (CHƯƠNG · BÀI · DẠNG &times; 3 PHẦN &times; 4 CẤP ĐỘ NHẬN THỨC NB-TH-VD-VDC)

> **Mã tài liệu:** `SPEC-MATRIX-HIERARCHICAL-GRID-2026`  
> **Dự án:** Quesy - Hệ thống Quản trị Khảo thí, Soạn đề & Số hóa Đề thi Chuẩn Quốc gia  
> **Căn cứ pháp lý:** Thông tư 32/2018/TT-BGDĐT, Thông tư 22/2021/TT-BGDĐT, Quyết định 764/QĐ-BGDĐT (Định dạng Đề thi 2025)  
> **Phiên bản:** v4.0 (Kiến trúc Bảng Ma trận Đa tầng Tích hợp Kho Tồn câu hỏi & Footer Cố định)  
> **Tác giả:** Sub-Agent 1 (Architect & Requirements Engineer)  
> **Đối tượng bàn giao:** Sub-Agent 2 (Software Engineer & Coder)  

---

## 1. TỔNG QUAN & BỐI CẢNH CHUYỂN ĐỔI (CONTEXT & OBJECTIVES)

### 1.1. Hiện trạng và Hạn chế của Ma trận Cũ
Trong phiên bản tiền nhiệm (v3.5), phân hệ Ma trận đề thi (`#tab-matrix`) sử dụng lưới phẳng đơn giản:
- Mỗi dòng chỉ đại diện cho một cặp (YCCĐ, Dạng bài) và chỉ được chọn **duy nhất một dạng thức câu hỏi** qua dropdown `<select>` (Trắc nghiệm, Đúng/Sai, Trả lời ngắn, hoặc Tự luận).
- Các cột mức độ nhận thức chỉ giới hạn ở 3 mức: Biết (Nhận biết), Hiểu (Thông hiểu), Vận dụng; **thiếu hoàn toàn mức độ Vận dụng cao (VDC)** theo chuẩn khảo thí THPT Quốc gia 2025.
- Để cấu hình đề thi có cùng một bài học nhưng gồm nhiều dạng thức (ví dụ: Vừa có trắc nghiệm 4 lựa chọn, vừa có Đúng/Sai, vừa có Trả lời ngắn), giáo viên buộc phải thêm nhiều dòng thủ công rời rạc, gây trùng lặp nội dung, phân mảnh dữ liệu và khó quan sát tổng thể phân bổ kiến thức toàn chương.

### 1.2. Mục tiêu Chuyển đổi Sang Bảng Phân Cấp Đa Tầng (Hierarchical Multi-Tier Matrix Table)
1. **Phân cấp triệt để Cột 1 theo Cây Kiến thức Thông tư 32:**  
   `Chương (Topic) · Bài học (Lesson) · Dạng bài tập (Problem Archetype / YCCĐ)` với khả năng gập/mở đa tầng (Accordion/Tree Node), hỗ trợ công cụ:
   - Nút **Mở hết (Expand All)** và **Đóng hết (Collapse All)**.
   - **Ô tìm kiếm dạng bài (Live Search Input)**: Lọc tức thì dạng bài, bài học hoặc chương theo từ khóa.
   - **Checkbox "Dạng có câu"**: Chỉ hiển thị những dạng bài hiện có câu hỏi tồn kho trong ngân hàng hoặc đã được cấu hình số lượng $> 0$.
2. **Cấu trúc Lưới Ma trận Toàn diện 3 Phần &times; 4 Cấp độ Nhận thức:**  
   - 3 Nhóm cột lớn chuẩn Quyết định 764/QĐ-BGDĐT:
     - **Phần I: Trắc nghiệm 4 lựa chọn** (0.25đ / câu)
     - **Phần II: Đúng / Sai 4 ý** (Tối đa 1.0đ / câu theo barem bậc thang QĐ 764)
     - **Phần III: Trả lời ngắn** (0.5đ / câu)
     - *(Kiến trúc mở rộng: Phần IV - Tự luận)*
   - Mỗi nhóm cột lớn chia thành **4 cột con**: `NB` (Nhận biết), `TH` (Thông hiểu), `VD` (Vận dụng), `VDC` (Vận dụng cao).
   - Cột ngoài cùng: **Tổng câu** và **Tổng điểm** của từng dạng bài (và subtotal của từng bài/chương).
3. **Đối soát Tồn kho Thời gian thực trên Từng Ô Nhập Liệu:**  
   Mỗi ô giao nhau giữa `(Dạng bài)` và `(Phần thi, Cấp độ)` hiển thị input số lượng câu cần lấy kèm badge hiển thị số dư khả dụng trong ngân hàng câu hỏi (`Kho: {stock}`).
4. **Thanh Footer Cố định (Sticky Bottom Action Bar):**  
   Bám dính đáy màn hình, cập nhật tức thời tổng số câu từng phần (Phần I, Phần II, Phần III), tổng điểm toàn đề, thanh cân đối nhận thức Bloom (NB-TH-VD-VDC) và nút hành động nổi bật **"Tạo đề" (Khởi tạo Đề thi Gốc & Sang Trộn đề)**.

---

## 2. KIẾN TRÚC GIAO DIỆN NGƯỜI DÙNG (UI/UX SPECIFICATION)

### 2.1. Sơ đồ Bố cục Giao diện (Layout Wireframe)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TAB: MA TRẬN ĐỀ THI (/matrix)                                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. CARD THAM SỐ CHUNG]                                                                                                │
│ Tên kỳ thi: [ Đề Khảo sát Toán 12 - THPT 2025 ]  Khối lớp: [ Lớp 12 - Toán ]  Thời gian: [ 90 phút ▾]  Thang điểm: 10.0 │
│ Xuất bản đặc tả: [ 📄 Tải PDF (A4) ] [ 📊 Tải CSV (UTF-8 BOM) ] [ 💾 Tải JSON ]                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [2. THANH CÔNG CỤ CỘT 1 (TREE TOOLBAR)]                                                                                │
│ [ 🔍 Tìm kiếm dạng bài, bài học... ]  [x] Dạng có câu trong kho   [ ⊞ Mở hết ] [ ⊟ Đóng hết ]   [ Mẫu THPT 2025 ▾ ] [ Đặt lại ]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [3. BẢNG MA TRẬN PHÂN CẤP ĐA TẦNG (HIERARCHICAL MATRIX TABLE)]                                                         │
│ ┌────────────────────────┬─────────────────────────┬─────────────────────────┬─────────────────────────┬───────┬───────┤
│ │                        │ PHẦN I: TRẮC NGHIỆM (0.25đ)│ PHẦN II: ĐÚNG/SAI (1.0đ) │ PHẦN III: TL NGẮN (0.5đ) │ TỔNG  │ TỔNG  │
│ │ CHƯƠNG · BÀI · DẠNG    ├────┬────┬────┬──────────┼────┬────┬────┬──────────┼────┬────┬────┬──────────┤ CÂU   │ ĐIỂM  │
│ │                        │ NB │ TH │ VD │ VDC      │ NB │ TH │ VD │ VDC      │ NB │ TH │ VD │ VDC      │       │       │
│ ├────────────────────────┼────┴────┴────┴──────────┼────┴────┴────┴──────────┼────┴────┴────┴──────────┼───────┼───────┤
│ │ ▼ Chương I. Đạo hàm... │  [   3 câu - 0.75đ    ] │  [    1 câu - 1.0đ    ] │  [   2 câu - 1.0đ     ] │ 6 câu │ 2.75đ │
│ │  ▼ Bài 1. Tính đơn điệu│  [   2 câu - 0.50đ    ] │  [    1 câu - 1.0đ    ] │  [   1 câu - 0.5đ     ] │ 4 câu │ 2.00đ │
│ │   • Dạng 1: Đọc BBT... │[1] │[1] │ 0  │  0       │ 0  │[1] │ 0  │  0       │[1] │ 0  │ 0  │  0       │ 4 câu │ 1.75đ │
│ │     (Kho: 12)          │k:5 │k:4 │k:2 │ k:1      │k:3 │k:2 │k:1 │ k:0      │k:4 │k:2 │k:1 │ k:0      │       │       │
│ │   • Dạng 2: Cực trị $m$│ 0  │ 0  │[1] │  0       │ 0  │ 0  │ 0  │  0       │ 0  │ 0  │ 0  │  0       │ 1 câu │ 0.25đ │
│ │     (Kho: 8)           │k:0 │k:1 │k:4 │ k:3      │k:0 │k:1 │k:1 │ k:0      │k:0 │k:0 │k:2 │ k:0      │       │       │
│ │  ► Bài 2. GTLN - GTNN  │  ...                    │  ...                    │  ...                    │ ...   │ ...   │
│ │ ► Chương II. Tích phân │  ...                    │  ...                    │  ...                    │ ...   │ ...   │
│ └────────────────────────┴─────────────────────────┴─────────────────────────┴─────────────────────────┴───────┴───────┘
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [4. THANH FOOTER CỐ ĐỊNH (STICKY ACTION BAR)]                                                                          │
│ [Phần I: 12 câu (3.0đ)]  [Phần II: 4 câu (4.0đ)]  [Phần III: 6 câu (3.0đ)]  │ TỔNG: 22 CÂU / 10.0 ĐIỂM                 │
│ Tỷ lệ: [NB: 40% (8c)] [TH: 30% (7c)] [VD: 20% (5c)] [VDC: 10% (2c)]        │ [ Đặt lại ]   [ 🚀 TẠO ĐỀ THI GỐC & TRỘN ]│
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CHI TIẾT CẤU TRÚC THÀNH PHẦN (COMPONENT SPECIFICATIONS)

### 3.1. Cột 1: Cấu trúc Cây Phân Cấp Chương · Bài · Dạng
- **Độ rộng:** `min-w-[320px] max-w-[400px]`, thiết lập `sticky left-0 z-10 bg-white` để khi cuộn ngang 12 cột nhận thức, tên chương/bài/dạng luôn cố định bên trái.
- **Tầng 1 - Hàng Chương (Topic Row):**
  - Giao diện: Nền `bg-slate-100 text-slate-900 font-bold py-2.5 px-3 border-t border-b border-slate-300`.
  - Icon điều khiển: Nút bấm chevron `▼` (mở) hoặc `▶` (gập), icon folder môn học.
  - Tên chương: Ví dụ `Chương I. Ứng dụng đạo hàm để khảo sát hàm số`.
  - Badge thống kê: Hiển thị tổng số câu đã cấu hình của cả chương (e.g., `Badge: 6 câu - 2.75đ`).
- **Tầng 2 - Hàng Bài học (Lesson Row):**
  - Giao diện: Thụt lề cấp 2 (`pl-6 pr-3 py-2 bg-slate-50 text-slate-800 font-semibold border-t border-slate-200`).
  - Icon điều khiển: Nút chevron `▼`/`▶`, icon file sách.
  - Tên bài: Ví dụ `Bài 1. Tính đơn điệu và cực trị của hàm số`.
  - Badge thống kê: Hiển thị tổng số câu đã cấu hình của bài học (e.g., `Badge: 4 câu - 2.00đ`).
- **Tầng 3 - Hàng Dạng bài tập (Problem Archetype Leaf Row):**
  - Giao diện: Thụt lề cấp 3 (`pl-10 pr-3 py-2 bg-white hover:bg-blue-50/20 text-slate-700 text-xs border-t border-slate-100`).
  - Nội dung: Tên dạng bài tập (hỗ trợ render KaTeX cho công thức toán inline như `$m$`, `$f(x)$`, `$Oxyz$`) kèm mã định danh chuẩn (`TOAN12.GT.01.D01`).
  - Badge tổng câu của riêng dạng bài này trong toàn bộ 3 phần thi.

### 3.2. Thanh Công cụ Điều khiển Cột 1 (Tree Toolbar Controls)
Bố trí ngay trên bảng ma trận với các công cụ:
1. **Ô tìm kiếm dạng bài (`#matrix-search-archetype`):**
   - Input dạng Apple search pill (`apple-input pl-8 pr-7 py-1.5 text-xs rounded-lg`).
   - Tự động lọc real-time khi gõ: Các node dạng bài hoặc bài học khớp từ khóa sẽ được giữ lại và mở ra tự động; các nhánh không khớp sẽ ẩn đi.
2. **Checkbox "Chỉ hiện dạng có câu hỏi" (`#matrix-filter-has-stock`):**
   - Toggle checkbox Apple HIG.
   - Khi được bật, chỉ hiển thị những dạng bài có ít nhất 1 câu hỏi khả dụng trong ngân hàng (`totalAvailableInBank > 0`) hoặc đã được giáo viên điền chỉ tiêu (`selectedQuestions > 0`). Giúp giáo viên loại bỏ các dạng bài trống, tập trung vào những dạng đang có dữ liệu trong ngân hàng.
3. **Nút "Mở hết" (`#btn-matrix-expand-all`):** Mở bung tất cả các cấp Chương và Bài học.
4. **Nút "Đóng hết" (`#btn-matrix-collapse-all`):** Gập gọn toàn bộ, chỉ hiển thị danh mục các Chương.
5. **Cụm Presets Khảo thí Chuẩn Quốc Gia:**
   - Dropdown chọn cấu hình mẫu:
     - *Preset 1: Chuẩn Tốt nghiệp THPT 2025 (22 câu - 10.0đ)*: 12 câu Phần I (3.0đ) + 4 câu Phần II (4.0đ) + 6 câu Phần III (3.0đ). Phân bổ 40% NB - 30% TH - 20% VD - 10% VDC.
     - *Preset 2: Kiểm tra Đánh giá Định kỳ (20 câu - 10.0đ)*.
     - *Preset 3: Khảo sát Cuối học kỳ (28 câu - 10.0đ)*.
6. **Nút "Đặt lại" (`#btn-matrix-reset`):** Xóa toàn bộ chỉ tiêu về 0 kèm hộp thoại xác nhận.

### 3.3. Cấu trúc 3 Nhóm Cột Lớn &times; 4 Cột Con Nhận Thức
Bảng lưới ma trận có 2 hàng header:
- **Hàng Header 1:**
  - Cột 1 (`rowspan="2"`): `Chương · Bài · Dạng` (Sticky left)
  - Cụm Cột 1 (`colspan="4"`): `PHẦN I: TRẮC NGHIỆM (0.25đ/câu)` - Tông màu xanh dương (`bg-blue-100/70 text-blue-900 border-blue-200`)
  - Cụm Cột 2 (`colspan="4"`): `PHẦN II: ĐÚNG / SAI (1.0đ/câu)` - Tông màu tím chàm (`bg-indigo-100/70 text-indigo-900 border-indigo-200`)
  - Cụm Cột 3 (`colspan="4"`): `PHẦN III: TRẢ LỜI NGẮN (0.5đ/câu)` - Tông màu xanh ngọc (`bg-emerald-100/70 text-emerald-900 border-emerald-200`)
  - Cột Tổng câu (`rowspan="2"`): `Tổng câu` (W: 80px)
  - Cột Tổng điểm (`rowspan="2"`): `Tổng điểm` (W: 80px)
- **Hàng Header 2 (Các cột con nhận thức):**
  - Dưới Phần I: `NB`, `TH`, `VD`, `VDC`
  - Dưới Phần II: `NB`, `TH`, `VD`, `VDC`
  - Dưới Phần III: `NB`, `TH`, `VD`, `VDC`

### 3.4. Cấu tạo Ô Nhập Liệu (Matrix Input Cell) & Tồn Kho Câu Hỏi
Tại mỗi ô lá (giao giữa Dạng bài và Thể thức - Mức độ):
- **Phần tử Input (`<input type="number">`):**
  - Giá trị: Số nguyên $\ge 0$ (mặc định 0).
  - Class: `.matrix-cell-input` (rộng 44px, cao 28px, căn giữa, font đậm, border mờ, focus viền xanh Apple).
  - Thuộc tính data: `data-archetype-id`, `data-format`, `data-level`, `data-points`.
  - Tương tác: Gõ phím hoặc nhấn phím mũi tên lên/xuống cập nhật ngay lập tức footer và subtotal.
- **Badge Tồn kho Ngân hàng (`.matrix-stock-chip`):**
  - Nằm ngay dưới ô input: `Kho: {available}`.
  - Phân loại màu sắc thời gian thực:
    - *Đủ câu (`stock-ok`):* Màu xanh lá `bg-emerald-50 text-emerald-700 border-emerald-200` khi `available >= value`.
    - *Cảnh báo thiếu câu (`stock-warn`):* Màu đỏ `bg-rose-50 text-rose-700 border-rose-200 font-bold` khi `value > 0` và `value > available` (hiển thị `Kho: {available} / Cần: {value}`).
    - *Hết câu / Rỗng (`stock-zero`):* Màu xám nhạt `text-slate-400` khi `available == 0` và `value == 0`.
- **Tại các hàng Chương và Bài học (Subtotal Cells):**
  - Không hiển thị input mà hiển thị tổng số câu đã chọn của nhóm bài/chương đó trong cột tương ứng (dạng text in đậm `text-slate-700` hoặc badge pill mờ).

### 3.5. Thanh Footer Cố định (Sticky Action Footer Bar)
- **Vị trí & Kiểu dáng:**
  - `position: sticky; bottom: 0; z-index: 30;`
  - Nền kính mờ: `background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px);`
  - Đường viền trên: `border-t: 1px solid rgba(0, 0, 0, 0.1);`
  - Đổ bóng nhẹ: `box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.05);`
- **Các thông số hiển thị thời gian thực:**
  1. *Cụm thống kê 3 Phần thi:*
     - `Phần I (Trắc nghiệm): {count_p1} câu ({points_p1}đ)`
     - `Phần II (Đúng / Sai): {count_p2} câu ({points_p2}đ)`
     - `Phần III (Trả lời ngắn): {count_p3} câu ({points_p3}đ)`
  2. *Tổng số toàn bài thi:*
     - `TỔNG CỘNG: {total_questions} câu | {total_points} / 10.0 điểm`
  3. *Tỷ lệ Cân đối Mức độ Nhận thức (Bloom Metric Bar):*
     - Thanh phân bổ màu 4 mức độ:
       - NB (Nhận biết): Xanh dương (`#3b82f6`)
       - TH (Thông hiểu): Tím chàm (`#6366f1`)
       - VD (Vận dụng): Xanh lá (`#10b981`)
       - VDC (Vận dụng cao): Tím hồng (`#a855f7`)
     - Nhãn văn bản: `NB: {pct_nb}% | TH: {pct_th}% | VD: {pct_vd}% | VDC: {pct_vdc}%`
     - Cảnh báo chuẩn hóa: Hiện badge màu xanh nếu đạt tỷ lệ chuẩn khảo thí (hoặc cảnh báo vàng nếu chênh lệch $> \pm 5\%$).
  4. *Nút Hành động Chính ("Tạo Đề Thi"):*
     - Nút **`🚀 Tạo Đề Thi Gốc & Sang Trộn Đề` (`#btn-matrix-generate-exam`)**:
       - Chuẩn Apple HIG Primary Button (`btn-apple-primary font-bold py-2.5 px-6 shadow-md`).
       - Phản hồi xúc giác scale 0.97 (`active:scale-[0.97] transition-transform`).
       - Xử lý click:
         1. Kiểm tra tồn kho toàn ma trận: Nếu thiếu câu, hiển thị modal hoặc toast xác nhận (cho phép rút một phần qua `allow_partial: true`).
         2. Gọi API `POST /api/v1/matrix` để lưu ma trận chi tiết vào CSDL.
         3. Gọi API `POST /api/v1/exams/generate` với `matrix_id` vừa lưu để sinh đề thi gốc.
         4. Điều hướng mượt mà sang phân hệ Trộn Đề (`#tab-shuffler`, `/shuffler`), tự động nạp đề gốc và danh sách câu hỏi.

---

## 4. THIẾT KẾ DỮ LIỆU & HỢP ĐỒNG API (DATA ARCHITECTURE & APIS)

### 4.1. Mô hình Dữ liệu Cơ sở Dữ liệu (ORM Models)
Hệ thống sử dụng trực tiếp các bảng CSDL đã chuẩn hóa trong `backend/models.py`:
- `exam_matrices`: Lưu trữ thông tin ma trận đề thi tổng thể (`id`, `title`, `subject_id`, `grade_id`, `duration_minutes`, `total_points`).
- `exam_matrix_items`: Chi tiết từng ô ma trận phân bổ:
  ```python
  class ExamMatrixItem(Base):
      __tablename__ = "exam_matrix_items"
      id = Column(String(36), primary_key=True, default=generate_uuid)
      matrix_id = Column(String(36), ForeignKey("exam_matrices.id", ondelete="CASCADE"), nullable=False, index=True)
      learning_outcome_id = Column(String(36), ForeignKey("learning_outcomes.id"), nullable=True, index=True)
      problem_archetype_id = Column(String(36), ForeignKey("problem_archetypes.id"), nullable=True, index=True)
      cognitive_level = Column(String(50), nullable=False, default="RECOGNITION")  # RECOGNITION, COMPREHENSION, APPLICATION, HIGH_APPLICATION
      question_type = Column(String(50), nullable=False, default="SINGLE_CHOICE")  # SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, ESSAY
      item_format = synonym("question_type")
      quantity = Column(Integer, default=1, nullable=False)
      points_per_item = Column(Float, default=0.25, nullable=False)
      section_number = Column(Integer, default=1)  # 1: Phần I, 2: Phần II, 3: Phần III, 4: Phần IV
      order_index = Column(Integer, default=0)
  ```

### 4.2. API Lấy Tồn Kho Câu Hỏi Ngân Hàng Thời Gian Thực (Inventory Endpoint)
- **Endpoint:** `GET /api/v1/matrices/bank-inventory?subject_id={subject_id}&grade_id={grade_id}`
- **Chức năng:** Trả về số lượng câu hỏi khả dụng (`status = 'APPROVED'`, `is_defective == False`) gom nhóm theo:
  `problem_archetype_id` &times; `item_format` &times; `cognitive_level`.
- **Cấu trúc Response:**
  ```json
  {
    "subject_id": "TOAN",
    "grade_id": "GRADE_12",
    "total_approved_questions": 120,
    "inventory": {
      "pa_gt01_d1": {
        "SINGLE_CHOICE": {
          "RECOGNITION": 12,
          "COMPREHENSION": 8,
          "APPLICATION": 4,
          "HIGH_APPLICATION": 1
        },
        "TRUE_FALSE_GROUP": {
          "RECOGNITION": 3,
          "COMPREHENSION": 4,
          "APPLICATION": 2,
          "HIGH_APPLICATION": 0
        },
        "SHORT_ANSWER": {
          "RECOGNITION": 2,
          "COMPREHENSION": 3,
          "APPLICATION": 3,
          "HIGH_APPLICATION": 1
        }
      }
    }
  }
  ```
- **Fallback Client-side:** Nếu không gọi endpoint trên, hàm frontend `computeBankInventoryFromState()` tự động duyệt mảng `state.itemBank` và tổng hợp bản đồ tồn kho với cấu trúc y hệt, bảo đảm ứng dụng hoạt động 100% trơn tru trong môi trường offline / PWA.

### 4.3. API Lưu Ma Trận & Bản Đặc Tả
- **Endpoint:** `POST /api/v1/matrix` (hoặc alias `/api/v1/matrices`)
- **Request Body:**
  ```json
  {
    "title": "Đề Khảo sát Toán 12 - Chuẩn TN THPT 2025",
    "subject_id": "TOAN",
    "grade_id": "GRADE_12",
    "duration_minutes": 90,
    "total_points": 10.0,
    "items": [
      {
        "problem_archetype_id": "pa_gt01_d1",
        "learning_outcome_id": "yccd_gt_01",
        "cognitive_level": "RECOGNITION",
        "item_format": "SINGLE_CHOICE",
        "quantity": 2,
        "points_per_item": 0.25,
        "section_number": 1
      },
      {
        "problem_archetype_id": "pa_gt01_d1",
        "learning_outcome_id": "yccd_gt_01",
        "cognitive_level": "COMPREHENSION",
        "item_format": "TRUE_FALSE_GROUP",
        "quantity": 1,
        "points_per_item": 1.0,
        "section_number": 2
      }
    ]
  }
  ```

### 4.4. Động cơ Sinh Đề Gốc theo Ma Trận (Solver Integration)
- Khi người dùng nhấn nút "Tạo Đề Thi", frontend gọi:
  ```json
  POST /api/v1/exams/generate
  {
    "matrix_id": "<ID_MA_TRẬN_VỪA_LƯU>",
    "title": "Đề thi Gốc Kỳ thi Tốt nghiệp THPT 2025 - Môn Toán",
    "allow_partial": true
  }
  ```
- Bộ giải `backend/services/matrix_solver.py` tự động rút đúng số lượng câu hỏi khớp chính xác từng ô ma trận:
  - Phân loại câu hỏi vào đúng Section:
    - `SINGLE_CHOICE` $\rightarrow$ Section 1 (Phần I: Câu 1 đến câu $N_1$)
    - `TRUE_FALSE_GROUP` $\rightarrow$ Section 2 (Phần II: Câu $N_1 + 1$ đến câu $N_1 + N_2$)
    - `SHORT_ANSWER` $\rightarrow$ Section 3 (Phần III: Câu $N_1 + N_2 + 1$ đến hết)
  - Áp dụng các nguyên tắc khảo thí: Psychometric Weighting (độ phân biệt $D \ge 0.3$), Option Anchor Invariant (vị trí D cố định cho phương án neo), và chuyển giao sang tab `#tab-shuffler`.

---

## 5. MÔ HÌNH QUẢN LÝ TRẠNG THÁI CLIENT-SIDE (FRONTEND STATE MACHINE)

### 5.1. Cấu trúc State trong `frontend/static/app.js`
Trong `state.matrixConfig`, bổ sung cấu trúc lưới đa tầng:
```javascript
state.hierarchicalMatrix = {
  treeData: null,         // Dữ liệu cây 6 tầng nạp từ GET /api/v1/taxonomy/tree
  inventoryMap: {},       // Bản đồ tồn kho: { [archetype_id]: { [format]: { [level]: count } } }
  expandedNodes: new Set(), // Set chứa ID các Chương và Bài đang mở (cho phép gập/mở)
  searchQuery: '',        // Từ khóa tìm kiếm dạng bài
  filterOnlyHasStock: false, // Checkbox chỉ hiện dạng có câu
  cellSelections: {},     // Bản đồ số câu đã chọn: { `${archetype_id}_${format}_${level}`: quantity }
};
```

### 5.2. Công thức Tính Toán Điểm & Tỷ Lệ Nhận Thức Real-time
1. **Điểm từng câu theo định dạng:**
   - `SINGLE_CHOICE`: 0.25 điểm / câu
   - `TRUE_FALSE_GROUP`: 1.0 điểm / câu (chấm bậc thang theo QĐ 764: 1 ý = 0.1đ; 2 ý = 0.25đ; 3 ý = 0.5đ; 4 ý = 1.0đ)
   - `SHORT_ANSWER`: 0.5 điểm / câu
   - `ESSAY`: 1.0 điểm / câu
2. **Tổng số câu & điểm từng phần:**
   - $\text{Total}_{P1} = \sum \text{quantity}(\text{format} = \text{SINGLE\_CHOICE})$
   - $\text{Points}_{P1} = \text{Total}_{P1} \times 0.25$
   - $\text{Total}_{P2} = \sum \text{quantity}(\text{format} = \text{TRUE\_FALSE\_GROUP})$
   - $\text{Points}_{P2} = \text{Total}_{P2} \times 1.0$
   - $\text{Total}_{P3} = \sum \text{quantity}(\text{format} = \text{SHORT\_ANSWER})$
   - $\text{Points}_{P3} = \text{Total}_{P3} \times 0.5$
   - $\text{GrandTotal} = \text{Total}_{P1} + \text{Total}_{P2} + \text{Total}_{P3}$
   - $\text{GrandPoints} = \text{Points}_{P1} + \text{Points}_{P2} + \text{Points}_{P3}$
3. **Tỷ lệ % Cấp độ Nhận thức Bloom (4 Mức độ):**
   - $\% \text{NB} = \text{round}\left(\frac{\text{Count}(\text{RECOGNITION})}{\text{GrandTotal}} \times 100\right)$
   - $\% \text{TH} = \text{round}\left(\frac{\text{Count}(\text{COMPREHENSION})}{\text{GrandTotal}} \times 100\right)$
   - $\% \text{VD} = \text{round}\left(\frac{\text{Count}(\text{APPLICATION})}{\text{GrandTotal}} \times 100\right)$
   - $\% \text{VDC} = \max\left(0, 100 - \% \text{NB} - \% \text{TH} - \% \text{VD}\right)$

---

## 6. QUY TRÌNH & KẾ HOẠCH TRIỂN KHAI CHO SUB-AGENT 2 (IMPLEMENTATION ROADMAP)

Sub-Agent 2 triển khai theo các bước tuần tự rõ ràng sau:

### Bước 1: Cập nhật Backend API (`backend/routers/matrix.py`)
1. Bổ sung trường `section_number: Optional[int] = 1` vào `MatrixItemCreate` và `MatrixItemOut`.
2. Tạo endpoint `GET /api/v1/matrices/bank-inventory` (hoặc alias `/api/v1/matrix/bank-inventory`):
   - Truy vấn gom nhóm `func.count(Question.id)` theo `(problem_archetype_id, item_format, cognitive_level)` trên các câu hỏi `APPROVED` không defective.
   - Trả về cấu trúc JSON inventory chuẩn.

### Bước 2: Tái cấu trúc Giao diện HTML (`frontend/index.html`)
1. Tại `#tab-matrix`:
   - Giữ lại Card tham số chung trên cùng (`#matrix-param-name`, `#matrix-param-time`, các nút tải PDF/CSV).
   - Thay thế toàn bộ thẻ table phẳng cũ bằng container bảng phân cấp đa tầng:
     - Thanh công cụ Cột 1: Ô tìm kiếm `#matrix-search-archetype`, checkbox `#matrix-filter-has-stock`, nút Mở hết `#btn-matrix-expand-all`, Đóng hết `#btn-matrix-collapse-all`, cụm Presets.
     - Thẻ `<table id="matrix-hierarchical-table">`:
       - Header 2 tầng: Cột 1 (Chương · Bài · Dạng sticky), 3 Nhóm cột lớn (Phần I, II, III), 12 cột con (NB, TH, VD, VDC), Cột Tổng câu, Cột Tổng điểm.
       - Tbody `#matrix-hierarchical-tbody`: Nơi render các dòng Chương, Bài và Dạng.
   - Thêm thanh Footer Cố định `#matrix-sticky-footer` ở đáy card:
     - Thống kê Phần I, II, III.
     - Tổng cộng câu & điểm.
     - Thanh tỷ lệ nhận thức 4 màu NB-TH-VD-VDC.
     - Nút "Tạo Đề Thi Gốc & Sang Trộn Đề" (`#btn-matrix-generate-exam`).

### Bước 3: Cập nhật CSS Chuẩn Apple HIG (`frontend/static/style.css`)
1. Bổ sung các class cho bảng đa tầng:
   - `.matrix-tree-col`: Sticky left, background trắng/xám nhẹ, shadow ngăn cách bên phải.
   - `.matrix-row-chapter`, `.matrix-row-lesson`, `.matrix-row-archetype`: Định dạng khoảng thụt đầu dòng (indentation), màu nền, font weight.
   - `.matrix-cell-input`: Input nhỏ gọn 44px, viền mờ, focus sáng xanh Apple Blue.
   - `.matrix-stock-chip`: Badge hiển thị tồn kho `Kho: X` (màu xanh khi đủ, màu đỏ cảnh báo khi thiếu).
   - `.matrix-sticky-footer`: Bám dính đáy màn hình, background kính mờ backdrop-blur, đổ bóng mượt mà.

### Bước 4: Hiện thực hóa Logic trong JavaScript (`frontend/static/app.js`)
1. Hàm `loadTaxonomyAndInventoryForMatrix()`: Tải cây taxonomy từ `GET /api/v1/taxonomy/tree` và nạp bản đồ tồn kho.
2. Hàm `renderHierarchicalMatrixGrid()`:
   - Duyệt cây Chương $\rightarrow$ Bài $\rightarrow$ Dạng.
   - Áp dụng bộ lọc tìm kiếm `searchQuery` và checkbox `filterOnlyHasStock`.
   - Render các dòng Chương (có subtotal), Bài (có subtotal), và Dạng bài (có 12 ô input + chip tồn kho).
   - Gọi `renderKaTeX()` cho các tên dạng bài có ký hiệu toán học.
3. Hàm `updateMatrixCellSelection(archetypeId, yccdId, format, level, qty)`:
   - Cập nhật số lượng câu chọn vào `state.hierarchicalMatrix.cellSelections`.
   - Cập nhật tức thì subtotal của dòng, của bài, của chương và toàn bộ thanh Footer.
4. Hàm `toggleMatrixNode(nodeId)`: Gập/mở Chương hoặc Bài.
5. Hàm `applyHierarchicalMatrixPreset(presetName)`: Tự động điền các chỉ tiêu mẫu chuẩn Bộ GD&ĐT 2025.
6. Hàm `generateMasterExamFromHierarchicalMatrix()`:
   - Thu thập tất cả các ô có `quantity > 0`.
   - Lưu ma trận qua `POST /api/v1/matrix`.
   - Gọi `POST /api/v1/exams/generate`.
   - Chuyển tiếp sang `#tab-shuffler`.

---

## 7. TIÊU CHÍ NGHIỆM THU CHO SUB-AGENT 3 VÀ SUB-AGENT 4 (VERIFICATION GATES)

### 7.1. Tiêu chí Kiểm thử Tự động Backend (Sub-Agent 3 Gate)
1. `GET /api/v1/matrices/bank-inventory` trả về mã 200, đúng cấu trúc bản đồ `archetype -> format -> level`.
2. `POST /api/v1/matrix` lưu thành công ma trận có danh sách items đa dạng gồm cả 3 thể thức (`SINGLE_CHOICE`, `TRUE_FALSE_GROUP`, `SHORT_ANSWER`) và 4 mức độ (`RECOGNITION`, `COMPREHENSION`, `APPLICATION`, `HIGH_APPLICATION`).
3. `POST /api/v1/exams/generate` với ma trận đa tầng sinh ra Đề thi gốc `MasterExam` có đầy đủ 3 phần thi phân chia chính xác.
4. Tỷ lệ vượt qua 100% test cases tự động (`pytest`).

### 7.2. Tiêu chí Nghiệm thu Trình duyệt Thật E2E (Sub-Agent 4 Gate)
1. Truy cập tab `/matrix` hiển thị đúng Bảng Ma trận Phân cấp Đa tầng: Cột 1 Chương · Bài · Dạng có icon gập/mở, 3 Nhóm cột lớn (Phần I, II, III), mỗi nhóm 4 cột con (NB, TH, VD, VDC), và cột Tổng câu/Tổng điểm ngoài cùng.
2. Thao tác nút "Mở hết" bung toàn bộ các bài và dạng; nút "Đóng hết" gập gọn chỉ còn danh sách Chương.
3. Nhập từ khóa vào ô tìm kiếm dạng bài (ví dụ `đơn điệu` hoặc `cực trị`) lọc mượt mà, chỉ hiển thị đúng các nhánh liên quan.
4. Tick chọn checkbox "Dạng có câu" ẩn các dạng bài có số tồn kho bằng 0.
5. Nhập số câu vào các ô input: Chip tồn kho hiển thị đúng (`Kho: X`), badge tự động đổi màu xanh nếu đủ hoặc đỏ nếu thiếu câu.
6. Thanh Footer cố định ở đáy màn hình hiển thị chính xác tổng số câu từng phần (Phần I, II, III), tổng điểm toàn đề đạt 10.0đ và thanh phân bổ nhận thức Bloom 4 màu.
7. Nhấn nút "Tạo Đề Thi Gốc & Sang Trộn Đề": Chuyển hướng thành công sang tab `/shuffler`, nạp đề gốc với đầy đủ danh sách câu hỏi.
8. DevTools Console không có bất kỳ lỗi màu đỏ nào (`console.error`).
