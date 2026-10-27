# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (BUSINESS REQUIREMENTS DOCUMENT - BRD)

**Dự án:** Hệ thống Quản lý Đề thi, Ngân hàng Câu hỏi & Số hoá AI Toán học  
**Tên mã dự án (Project Code):** QUESY  
**Mục tiêu cốt lõi:** Giải quyết triệt để các rào cản và nút thắt cổ chai trong quy trình số hóa đề thi, tự động tái tạo đồ thị vector, chuẩn hóa công thức toán học, trộn đề an toàn chống vỡ logic và xuất bản ấn phẩm khảo thí in ấn chuyên nghiệp.  
**Phiên bản (Version):** 3.4 (Hoàn thiện Toàn diện Phân hệ Ma trận Đề thi 2D theo TT 22 & QĐ 764, Thư viện Presets, Đối soát Tồn kho, Xuất bản Bản Đặc tả & Động cơ Sinh & Trộn Đề An Toàn 4 Nguyên Tắc)  
**Trạng thái (Status):** Đã phê duyệt triển khai (Approved for Implementation)  
**Ngày phát hành:** 2026-10-27

---

## BẢNG THEO DÕI THAY ĐỔI TÀI LIỆU (DOCUMENT HISTORY)

| Phiên bản | Ngày | Tác giả | Mô tả thay đổi | Người duyệt |
|:---|:---|:---|:---|:---|
| 1.0 | 2026-10-14 | BA Team | Khởi tạo tài liệu BRD ban đầu | PM |
| 2.0 | 2026-10-15 | BA Team | Tích hợp cấu trúc đa dạng câu hỏi và cây phân loại năng lực | PM |
| 2.5 | 2026-10-18 | BA Team & Tech Lead | Tái cơ cấu toàn diện tài liệu theo định hướng Giải pháp & Giá trị thực tế: Tích hợp bộ dựng đồ thị vector SVG TikZ/PGFPlots tự động có Auto-clipping, 4 quy tắc toán học KaTeX, động cơ Safe Shuffling (Option Anchor), chấm điểm bậc thang và xuất bản Word OMML native. | Ban Giám đốc & PM |
| 2.6 | 2026-10-21 | BA Team & Tech Lead | Tích hợp chuẩn xuất bản MathType 7.0 OLE Vector WMF (double-click editable), dịch vụ MathJax Persistent Worker Engine (~14ms/công thức), và chuyển đổi bảng thống kê `\begin{array}` thành Word Table `<w:tbl>` chống lỗi đen PDF. | Ban Giám đốc & PM |
| 2.7 | 2026-10-21 | BA Team & Tech Lead | Chuẩn hóa nhị phân DSMT7 Native Preamble, bản ghi TeX Input Language, bổ sung embellishment vectơ (`\vec`, `\overrightarrow`), đạt $100\%$ Vector WMF tuyệt đối, giải quyết triệt để lỗi OLE activation trong Microsoft Word. | Ban Giám đốc & PM |
| 3.0 | 2026-10-24 | BA Team & Tech Lead | Tích hợp Động cơ Thay thế Câu hỏi Thông minh (Question Replacement Engine), Cơ chế bảo toàn khối mã Chat Bubble (Safe Chat Sync), và Quy chuẩn Quản trị Git Workflow (Chỉ commit và push, tuyệt đối không tự động tạo PR). | Ban Giám đốc & PM |
| 3.3 | 2026-10-25 | BA Team & Tech Lead | Hoàn thiện Toàn diện Ngân hàng Câu hỏi CRUD & Import/Export, Hệ thống Xác thực Auth JWT/OAuth & Lưu Đề từ Soạn thảo vào Ngân hàng. | Ban Giám đốc & PM |
| **3.4** | 2026-10-27 | BA Team & Lead Architect | **Hoàn thiện Toàn diện Phân hệ Ma trận Đề thi 2D (TT 22 & QĐ 764), 3 Ma trận mẫu Presets, Đối soát Tồn kho Thời gian thực, Xuất bản Bản đặc tả (PDF/CSV/JSON), Động cơ Sinh Đề Gốc kèm Đổi câu hỏi tương đương, Động cơ Trộn Đề An Toàn 4 Nguyên Tắc (Option Anchor 100%), và Đóng gói Ấn phẩm Khảo thí (.ZIP/.PDF).** | Ban Giám đốc & PM |

---

## 1. TỔNG QUAN DỰ ÁN & VẤN ĐỀ THỰC TẾ (EXECUTIVE SUMMARY)

### 1.1. Các Vấn đề Thực tế & Nỗi đau Lớn trong Công tác Khảo thí
Trong hoạt động giảng dạy, kiểm tra và khảo thí tại các trường học, giáo viên và hội đồng chuyên môn đang phải đối mặt với 6 thách thức kỹ thuật lớn:

1. **Gánh nặng gõ lại đề thi thủ công:** Hàng chục nghìn đề thi của các trường đang lưu trữ dưới dạng bản in, ảnh chụp hoặc file Word định dạng cũ. Giáo viên mất từ 1.5 đến 2 giờ đồng hồ chỉ để gõ lại một đề thi có công thức toán MathType, thường xuyên bị lỗi font, mất ký tự khi sao chép.
2. **Hình vẽ và đồ thị bị bỏ quên hoặc vẽ méo mó:** Hầu hết công cụ OCR hiện nay chỉ trích xuất được văn bản thuần, hoàn toàn bất lực trước đồ thị hàm số và hình học không gian. Khi cố gắng vẽ lại, các đồ thị có tiệm cận thường bị vọt toạ độ vô cực, kéo giãn khung vẽ và làm méo xẹp tỷ lệ hiển thị.
3. **Lỗi hiển thị công thức toán học (KaTeX Parse Errors):** Các hệ thống học tập trực tuyến thường xuyên gặp lỗi vỡ giao diện do công thức toán thiếu dấu ngoặc kích thước động, dấu phẩy số thập phân bị hở khoảng cách, hoặc dấu gạch chéo tập hợp bị lỗi escape hiển thị chuỗi chữ đỏ thô.
4. **Trộn đề thi làm đảo lộn logic câu hỏi:** Các phần mềm trộn đề cổ điển thực hiện hoán vị ngẫu nhiên làm các phương án chứa từ ngữ phụ thuộc vị trí (*"Cả A và B đều đúng"*, *"Tất cả các ý trên"*) bị đảo lên đầu (A, B); các câu hỏi chung ngữ liệu đọc hiểu bị xé lẻ sang các trang khác nhau.
5. **Chấm điểm câu hỏi đa khẳng định phức tạp:** Dạng câu hỏi Đúng/Sai 4 khẳng định có cơ chế tính điểm bậc thang phi tuyến tính (0.1đ - 0.25đ - 0.5đ - 1.0đ) khiến công tác chấm thi thủ công rất dễ xảy ra nhầm lẫn và sai sót điểm số.
6. **Mất nhiều thời gian dàn trang in ấn:** Sau khi biên soạn, giáo viên phải mất nhiều công sức căn chỉnh lề 2 cột trên Word, chuyển đổi lại công thức sang Microsoft Word Equation bản địa để in ấn cho học sinh.

### 1.2. Tầm nhìn & Mục tiêu Sản phẩm (Product Vision)
Xây dựng nền tảng **Quesy** - Hệ sinh thái khảo thí thông minh toàn diện, tích hợp Trí tuệ Nhân tạo Đa phương thức (Multimodal Vision AI) và Đồ họa Vector Tự động nhằm:
- **Tự động hóa 100% quá trình số hóa đề thi:** Biến tài liệu giấy, PDF scan và Word cũ thành ngân hàng câu hỏi điện tử chuẩn KaTeX và đồ họa vector SVG chỉ trong vài giây.
- **Tái tạo đồ thị chuẩn xác tuyệt đối:** Dựng lại hoàn hảo đồ thị hàm bậc ba, hàm phân thức, hàm trùng phương và hình học không gian có cơ chế Auto-clipping khống chế tỷ lệ khung hình, hiển thị cả ở đề bài lẫn 4 phương án trắc nghiệm A, B, C, D.
- **Bảo toàn logic đề thi khi hoán vị:** Động cơ Safe Shuffling Engine giữ nguyên bài đọc chung, khóa cố định phương án phụ thuộc vị trí ở đáp án D và sinh ma trận đối chiếu đáp án tự động.
- **Xuất bản ấn phẩm chuyên nghiệp 1-click:** Xuất file Word A4 Portrait với công thức **MathType 7.0 OLE Vector WMF** (nét căng, click đúp mở MathType sửa được ngay) hoặc **Word OMML native**, xuất PDF in ấn và phiếu soi đáp án trắc nghiệm OMR.

---

## 2. ĐỐI TƯỢNG SỬ DỤNG & MA TRẬN PHÂN QUYỀN (RACI MATRIX)

### 2.1. Nhóm Người dùng
1. **Ban Giám hiệu / Phòng Khảo thí:** Ban hành khung kế hoạch kiểm tra đánh giá định kỳ, quản trị ngân hàng câu hỏi cấp trường/sở, bảo mật đề thi chính thức.
2. **Tổ trưởng Chuyên môn / Cán bộ Thẩm định:** Phê duyệt câu hỏi vào ngân hàng chính thức, phê duyệt Ma trận và Bản đặc tả đề thi theo chuẩn YCCĐ của môn học.
3. **Giáo viên Bộ môn:** Tải đề gốc lên để AI bóc tách, hậu kiểm trên Studio HITL, gán mã YCCĐ & Dạng câu hỏi, sinh đề kiểm tra thường xuyên và định kỳ.
4. **Học sinh:** Tham gia làm bài kiểm tra trực tuyến hoặc tải phiếu ôn tập theo từng YCCĐ.
5. **Quản trị viên Hệ thống:** Quản lý cấu hình AI, hạn mức sử dụng và hạ tầng.

### 2.2. Ma trận Trách nhiệm (RACI)

| Quy trình Nghiệp vụ | Super Admin | Tổ trưởng CM | Giáo viên | GV Phản biện | Thí sinh |
|:---|:---:|:---:|:---:|:---:|:---:|
| Cập nhật Danh mục YCCĐ theo TT 32 | **A** | **R** | C | I | I |
| Số hóa Đề thi bằng AI & Hậu kiểm HITL | I | C | **A/R** | I | I |
| Gán mã YCCĐ, Dạng câu hỏi & Mức độ tư duy | I | C | **A/R** | C | I |
| Thẩm định & Phê duyệt câu hỏi vào Bank | I | **A/R** | C | **R** | I |
| Thiết lập Ma trận & Bản đặc tả Đề thi | I | **A/R** | C | C | I |
| Sinh Đề thi Gốc & Hoán vị Mã đề An toàn | I | A | **R** | C | I |
| Xuất bản gói in ấn Word 2 cột & Phiếu OMR | I | I | **A/R** | I | I |
| Phân tích Chỉ số Khảo thí (p, D) sau kỳ thi | I | **A/R** | R | C | I |

---

## 3. PHÂN RÃ CÁC PHÂN HỆ YÊU CẦU NGHIỆP VỤ (EPICS BREAKDOWN)

### BR-01: PHÂN HỆ SỐ HOÁ ĐỀ THI ĐA NGUỒN & HẬU KIỂM SONG SONG (HITL STUDIO)
- **BR-01.1 Tiếp nhận tài liệu đề thi đa dạng:** Hỗ trợ `.docx`, `.doc` (chứa MathType OLE binary), `.pdf` (văn bản hoặc bản scan nhiều trang), ảnh chụp `.png`, `.jpg`, `.jpeg`, `.webp`. Dung lượng tối đa 50MB.
- **BR-01.2 Bóc tách cấu trúc & giải mã MathType sang LaTeX chuẩn:** Tự động nhận diện câu hỏi, phần dẫn, các phương án. Giải mã trực tiếp nhị phân MathType MTEF sang chuỗi LaTeX chuẩn (`$...$` inline, `$$...$$` block).
- **BR-01.3 Tự động cắt ảnh hình học & đồ thị (Auto Image Crop):** Bounding Box đồ thị hàm số, hình học không gian, sơ đồ mạch điện, biểu đồ. Cắt ảnh độ phân giải cao, nén WebP, lưu trữ và nhúng vào câu hỏi.
- **BR-01.4 Gợi ý gán nhãn thông minh bằng AI:** Tự động phân tích ngữ nghĩa thân câu hỏi và đề xuất chủ đề, bài học, dạng câu hỏi và mức độ tư duy.
- **BR-01.5 Studio hậu kiểm song song (HITL Studio):** Thiết kế tối giản Apple HIG: Cột trái xem tài liệu gốc có tính năng thu phóng; Cột phải hiển thị danh sách câu hỏi bóc tách render KaTeX thời gian thực. Cảnh báo độ tin cậy theo màu sắc, chỉnh sửa nhanh công thức và đổi đáp án trắc nghiệm chỉ bằng 1 cú nhấp chuột.

---

### BR-02: BỘ DỰNG ĐỒ THỊ VECTOR SVG TỰ ĐỘNG & CHUẨN HÓA TOÁN HỌC
- **BR-02.1 Biên dịch đồ thị TikZ/PGFPlots sang Vector SVG:** Tự động nhận diện mã nguồn hình học và chuyển đổi sang định dạng vector SVG sắc nét, hiển thị trực quan trên trình duyệt mà không cần cài đặt phần mềm LaTeX cục bộ.
- **BR-02.2 Auto-clipping khống chế tỷ lệ khung hình:** Tự động phát hiện phạm vi hệ trục toạ độ để giới hạn vùng vẽ hàm phân thức có tiệm cận, loại bỏ hoàn toàn hiện tượng vọt toạ độ vô cực gây méo xẹp tỷ lệ đồ thị.
- **BR-02.3 Hỗ trợ đồ thị trong các phương án trắc nghiệm:** Tự động nhận diện và hiển thị đồ thị độc lập trong từng phương án lựa chọn A, B, C, D dưới dạng thẻ trực quan.
- **BR-02.4 Bộ 4 quy tắc chuẩn hóa toán học:**
  1. *Dấu ngoặc kích thước động:* Tự động bọc `\left(...\right)`, `\left[...\right]`, `\left\{...\right\}` (bảo vệ căn `\sqrt[...]` và text mode).
  2. *Số thập phân chuẩn:* Định dạng dấu phẩy `{,}` trong công thức đề bài để KaTeX không tạo khoảng trống (ví dụ `15{,}25`), đồng thời giữ số sạch ở đáp án (`3,9`, `15,25`).
  3. *Phân số chuẩn:* Luôn chuyển sang `\dfrac` giúp công thức hiển thị thoáng đẹp.
  4. *Ký hiệu vectơ:* Chuẩn hóa thành `\overrightarrow{AB}` thay vì `\vec`.
- **BR-02.5 Tự động sửa lỗi bảng số liệu:** Chuyển đổi môi trường `tabular` sang KaTeX `array` và tự động đóng thẻ `$$`.

---

### BR-03: NGÂN HÀNG CÂU HỎI CHUẨN HÓA THEO DẠNG BÀI & NĂNG LỰC
- **BR-03.1 Cây phân cấp kiến thức độc lập (Taxonomy):** Cấu trúc phân cấp 6 tầng khoa học:
  $$\text{Cấp học / Khối lớp} \longrightarrow \text{Môn học} \longrightarrow \text{Mạch nội dung} \longrightarrow \text{Chủ đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{Dạng\ câu\ hỏi\ chuyên\ sâu}$$
  *Hoàn toàn độc lập, không bị phân mảnh hay ràng buộc vào các bộ sách giáo khoa riêng lẻ.*
- **BR-03.2 Phân loại theo 4 Mức độ Nhận thức:** Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao.
- **BR-03.3 Đa dạng thể thức câu hỏi hiện đại:**
  1. `SINGLE_CHOICE`: Trắc nghiệm 4 lựa chọn (A, B, C, D).
  2. `TRUE_FALSE_GROUP`: Trắc nghiệm Đúng/Sai 4 khẳng định độc lập (mỗi câu gồm ý a, b, c, d).
  3. `SHORT_ANSWER`: Trắc nghiệm trả lời ngắn (điền số hoặc từ ngữ, hỗ trợ dung sai tính toán $\pm \epsilon$).
  4. `PASSAGE_GROUP`: Câu hỏi chùm (Một đoạn văn bản/ngữ liệu bài đọc chung và các câu hỏi con đi kèm).
  5. `ESSAY`: Câu hỏi tự luận kèm rubric barem chấm điểm theo tiêu chí.
- **BR-03.4 Kiểm soát trùng lặp bằng AI Vector:** Sử dụng thuật toán Cosine Similarity để so khớp nội dung: Cảnh báo vàng khi trùng $\ge 80\%$, **chặn lưu và cảnh báo đỏ khi trùng $\ge 90\%$** so với các câu hỏi trong ngân hàng.

---

### BR-04: MA TRẬN ĐỀ THI 2D THEO YCCĐ, PRESETS & ĐỐI SOÁT TỒN KHO THỜI GIAN THỰC
- **BR-04.1 Ma trận đề thi 2 chiều tương tác (Interactive 2D Matrix Grid):**
  - Căn cứ pháp lý: Thông tư 22/2021/TT-BGDĐT (đánh giá học sinh THCS và THPT) và Định dạng đề thi tốt nghiệp THPT từ năm 2025 (Quyết định 764/QĐ-BGDĐT).
  - Trục dọc: Phân cấp theo Mạch nội dung (Strand) $
ightarrow$ Yêu cầu cần đạt (YCCĐ) $
ightarrow$ Dạng câu hỏi (Problem Archetype) và Thể thức câu hỏi (ItemFormat: `SINGLE_CHOICE`, `TRUE_FALSE_GROUP`, `SHORT_ANSWER`).
  - Trục ngang: 3 Cột cấp độ nhận thức bám sát Bảng động từ TT 32:
    1. *Biết (Nhận biết):* TN đơn (0.25đ/câu).
    2. *Hiểu (Thông hiểu):* Đúng/Sai (1.0đ/câu theo barem lũy tiến QĐ 764) hoặc TN đơn.
    3. *Vận dụng:* Trả lời ngắn (0.5đ/câu) hoặc Vận dụng / Vận dụng cao.
  - Tính toán thời gian thực: Tự động cộng dồn tổng số câu, tổng điểm từng dòng, tổng điểm từng cột và thang điểm tổng 10.0đ. Cảnh báo trực quan khi tổng điểm lệch khỏi 10.0đ.
  - Thanh tiến trình phân bổ Bloom (Biết %, Hiểu %, Vận dụng %) với nhãn cảnh báo trực quan: Đạt chuẩn khảo thí khi tỷ lệ tiệm cận 40% Biết - 30% Hiểu - 30% Vận dụng (dung sai $\pm 5\%$).
- **BR-04.2 Thư viện Ma trận mẫu (Exam Matrix Presets):**
  1. *Preset 1: Chuẩn Tốt nghiệp THPT 2025 (34 câu, 10.0 điểm, thời gian 90 phút):*
     - Phần I: 12 câu trắc nghiệm đơn $\times$ 0.25đ = 3.0 điểm.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0 điểm.
     - Phần III: 6 câu Trả lời ngắn $\times$ 0.5đ = 3.0 điểm.
     - Tỷ lệ chuẩn: 40% Biết (3.0đ) - 30% Hiểu (3.5đ) - 30% Vận dụng (3.5đ).
  2. *Preset 2: Kiểm tra Định kỳ / Giữa kỳ (20 câu, 10.0 điểm, thời gian 50-60 phút):*
     - Phần I: 12 câu trắc nghiệm đơn $\times$ 0.25đ = 3.0 điểm.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0 điểm.
     - Phần III: 4 câu Trả lời ngắn $\times$ 0.75đ = 3.0 điểm.
     - Tỷ lệ: ~50% Biết, 30% Hiểu, 20% Vận dụng.
  3. *Preset 3: Kiểm tra Cuối kỳ (28 câu, 10.0 điểm, thời gian 90 phút):*
     - Phần I: 16 câu trắc nghiệm đơn $\times$ 0.25đ = 4.0 điểm.
     - Phần II: 4 câu Đúng/Sai 4 khẳng định $\times$ 1.0đ = 4.0 điểm.
     - Phần III: 8 câu Trả lời ngắn $\times$ 0.25đ = 2.0 điểm.
     - Tỷ lệ: 40% Biết, 35% Hiểu, 25% Vận dụng.
- **BR-04.3 Đối soát tồn kho câu hỏi thời gian thực (Live Inventory Checker):**
  - Hệ thống tự động kiểm tra đối soát số lượng câu hỏi thực tế trong CSDL Question Bank cho từng ô ma trận (`learning_outcome_id x cognitive_level x item_format x problem_archetype_id`).
  - Trạng thái hiển thị trực quan:
    * *Đủ câu (Xanh):* Hiển thị số lượng khả dụng trong kho kèm badge xanh (ví dụ: `Kho: 15/4 câu (Đủ)`).
    * *Cảnh báo thiếu câu (Đỏ):* Hiển thị số lượng khả dụng và số lượng cần bổ sung kèm badge đỏ nổi bật (ví dụ: `Kho: 1/4 câu (Thiếu 3 câu)`).
  - Cảnh báo toàn ma trận: Hiển thị danh sách các ô thiếu câu và tổng số câu cần nạp thêm trước khi tiến hành rút đề.
- **BR-04.4 Xuất bản Bản đặc tả Ma trận Đề thi (Test Blueprint Specification Publishing):**
  - Hỗ trợ xuất bản bản đặc tả ma trận đề thi ra 3 định dạng:
    1. *JSON:* API RESTful phục vụ tích hợp và lưu trữ dữ liệu.
    2. *CSV UTF-8 BOM:* Tương thích 100% Microsoft Excel tiếng Việt trên Windows.
    3. *PDF Vector:* Khổ A4 Portrait chuẩn quy cách Bộ GD&ĐT gồm Khung Ma trận 2D và Bảng Đặc tả chi tiết từng YCCĐ.
- **BR-04.5 Rút đề gốc theo thuật toán thỏa mãn ràng buộc (CSP Solver):**
  - Rút câu hỏi đạt chuẩn `status = 'APPROVED'` và `is_defective == False` thỏa mãn chính xác từng ô ma trận.
  - Áp dụng danh sách loại trừ (Exclusion list): Cho phép tick chọn loại trừ các câu hỏi đã xuất hiện trong bài kiểm tra 30 ngày qua.
  - Trọng số trắc lượng học (Psychometric Weighting): Ưu tiên câu hỏi có độ phân biệt tốt ($D \ge 0.3$) và độ khó cân đối ($p \approx 0.55$).

---

### BR-05: ĐỘNG CƠ SINH & TRỘN ĐỀ THI AN TOÀN (SAFE SHUFFLING ENGINE)
- **BR-05.1 Đề thi Gốc (Master Exam) & Động cơ Đổi câu hỏi Tương đương (In-Place Question Swap Engine):**
  - Sinh đề thi gốc từ Ma trận hoặc chọn từ ngân hàng đề thi.
  - Hiển thị danh sách câu hỏi đề gốc với đầy đủ công thức toán KaTeX và đồ thị vector TikZ SVG.
  - Tính năng "Đổi câu khác" (Swap Question): Cho phép giáo viên thay thế một câu hỏi bất kỳ trong đề gốc bằng một câu hỏi tương đương từ ngân hàng câu hỏi (cùng YCCĐ, cùng mức độ nhận thức Bloom, cùng thể thức thi, trạng thái APPROVED, không bị defective).
  - Tự động hủy các mã đề hoán vị cũ khi đề gốc bị thay đổi để đảm bảo tính đồng bộ dữ liệu.
- **BR-05.2 4 Nguyên tắc Trộn Đề An Toàn Bắt Buộc (4 Safe Shuffling Rules - QĐ 764):**
  1. *Nguyên tắc 1 - Section Integrity (Bảo toàn phân đoạn):* Câu hỏi chỉ được hoán vị trong cùng một Phân đoạn / Thể thức (Phần I chỉ đảo trong Phần I, Phần II trong Phần II, Phần III trong Phần III).
  2. *Nguyên tắc 2 - Passage Integrity (Bảo toàn câu hỏi chùm / ngữ liệu):* Giữ liền mạch khối câu hỏi có chung ngữ liệu bài đọc hoặc hình vẽ; các câu hỏi con luôn nằm liền kề ngay sau đoạn văn bản ngữ liệu chung.
  3. *Nguyên tắc 3 - Option Anchor Rule (Khóa mỏ neo phương án):* Tự động nhận diện các phương án chứa từ ngữ phụ thuộc vị trí ("Cả A và B", "Cả hai đáp án", "Tất cả các đáp án trên", "Tất cả các ý trên", "Không có đáp án nào"...) hoặc cờ `is_fixed = True`. **BẮT BUỘC KHÓA CỐ ĐỊNH phương án này tại vị trí cuối cùng: Vị trí D** trong mọi mã đề hoán vị; chỉ xáo trộn các phương án A, B, C tự do. Đảm bảo tỷ lệ đạt Option Anchor Rule 100%.
  4. *Nguyên tắc 4 - Key Matrix Generator (Ma trận đáp án đối chiếu):* Tự động sinh bảng ma trận đối chiếu đáp án chéo giữa đề gốc và các mã đề hoán vị (101, 102, 103, 104...).
- **BR-05.3 Xuất bản Đề thi Đơn lẻ & Đóng gói Ấn phẩm Khảo thí (.ZIP):**
  - Hoán vị sinh 4 mã đề chuẩn: 101, 102, 103, 104.
  - Tab xem trước từng mã đề (Mã 101, 102, 103, 104) với huy hiệu xác minh Option Anchor Rule đạt 100%.
  - Bảng ma trận đáp án tổng hợp (Answer Key Matrix table).
  - Nút tải PDF riêng cho từng mã đề (`export-pdf`).
  - Nút tải trọn gói ấn phẩm đề thi (.ZIP): Đóng gói đầy đủ `De_{code}.pdf`, `LoiGiai_{code}.pdf`, `BangDapAn_TongHop.pdf`, `BangDapAn_TongHop.csv` (UTF-8 BOM), và `Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`.

---

### BR-06: XUẤT BẢN ẤN PHẨM KHẢO THÍ & CHẤM ĐIỂM HỌC SINH
- **BR-06.1 Xuất bản Microsoft Word (.docx) chuẩn in ấn & MathType OLE:**
  - Khổ chuẩn A4 Portrait (210 x 297 mm), lề trang chuẩn 1.5 cm - 1.8 cm, font Times New Roman 11pt, giãn dòng 1.15.
  - Hỗ trợ công thức **MathType 7.0 OLE Object Vector WMF** (`image/x-wmf` với APM header, root CLSID `{0002CE03-0000-0000-C000-000000000046}`, stream `Equation Native` chứa MTEF v5 DSMT7 và bản ghi `TeX Input Language`), **cho phép click đúp mở MathType 7 để chỉnh sửa trực tiếp 2 chiều đồng bộ với Web**. Chuẩn hóa typeface `0x82` bảo toàn toàn bộ dấu ngoặc `[`, `]`, `(`, `)`, `{`, `}`, đạt 100% Vector WMF thuần không dùng ảnh raster DIB mờ hạt và triệt tiêu lỗi dấu `?`.
  - Hỗ trợ định dạng **Microsoft Word OMML native**, chữ vector sắc nét, chỉnh sửa trực tiếp trên Word.
  - Tự động chuyển đổi bảng thống kê `\begin{array}` thành bảng Word `<w:tbl>`, loại bỏ lỗi hộp đen khi xuất PDF.
  - Gói xuất bản ZIP: $N$ file đề thi Word, file Lời giải chi tiết, file Bảng đáp án tổng hợp (Excel/CSV UTF-8 BOM + PDF), file Phiếu trả lời trắc nghiệm (chuẩn máy chấm OMR).
- **BR-06.2 Chấm điểm bậc thang & Quản lý bảng điểm:**
  - Tự động tính điểm dạng câu hỏi Đúng/Sai 4 khẳng định theo thang điểm bậc thang: Đúng 1 ý: 0.1đ; Đúng 2 ý: 0.25đ; Đúng 3 ý: 0.5đ; Đúng cả 4 ý: 1.0đ.
  - Quản lý danh sách lớp học và học sinh, xuất/nhập bảng điểm định dạng CSV/Excel UTF-8 BOM chuẩn tiếng Việt.
- **BR-06.3 Hoạt động Offline (PWA):**
  - Ứng dụng hỗ trợ Progressive Web App với cơ chế Network-First, đảm bảo truy cập và làm việc ổn định ngay cả khi gián đoạn mạng.

---

## 4. BẢNG TỔNG HỢP QUY TẮC NGHIỆP VỤ CỐT LÕI (CORE BUSINESS RULES)

| Mã Quy tắc | Tên Quy tắc | Nội dung Chi tiết |
|:---|:---|:---|
| **RULE-01** | Tính điểm Đúng/Sai 4 ý (Thang bậc thang) | Mỗi câu hỏi có 4 khẳng định a, b, c, d. Điểm tính theo bậc thang: Đúng 1 ý: $0.1$ điểm (10%); Đúng 2 ý: $0.25$ điểm (25%); Đúng 3 ý: $0.5$ điểm (50%); Đúng cả 4 ý: $1.0$ điểm (100%). |
| **RULE-02** | Neo Cố định Phương án (Option Anchor) | Phương án có chứa từ ngữ phụ thuộc vị trí ("Cả A và B", "Tất cả các đáp án trên") hoặc cờ `is_fixed = true` phải được khóa cố định ở vị trí cuối cùng (D) khi hoán vị mã đề. |
| **RULE-03** | Bảo toàn Toàn vẹn Câu hỏi Chùm | Toàn bộ câu hỏi con trong cùng một nhóm ngữ liệu chung phải luôn nằm liền kề nhau và ngay sau văn bản ngữ liệu bài đọc. |
| **RULE-04** | Chuẩn hóa theo Dạng bài & Năng lực | Câu hỏi được phân loại theo Dạng bài toán cụ thể và cấp độ tư duy, hoàn toàn độc lập với các bộ sách giáo khoa thương mại. |
| **RULE-05** | Ngưỡng Cảnh báo Trùng lặp AI Vector | Nếu độ tương đồng cosine >= 0.90 giữa câu hỏi mới và câu hỏi hiện có trong DB, hệ thống bắt buộc kích hoạt modal cảnh báo màu đỏ và chặn lưu tự động. |
| **RULE-06** | Cơ cấu Ma trận Đề thi Đánh giá Định kỳ | Tỷ lệ điểm các câu hỏi trong đề kiểm tra phải nằm trong biên độ cấu hình ma trận quy định (dung sai $\pm 5\%$). |
| **RULE-07** | Bảo toàn Khối mã Chat Bubble & Động cơ Thay thế Câu hỏi | Khi người dùng ra lệnh thay thế câu thứ N, hệ thống tự động bóc tách câu cũ làm `old_text` và gán câu mới làm `new_text`. Khối code trong chat bubble tuyệt đối không bị nuốt mất nếu không có diff hợp lệ gửi sang editor. |
| **RULE-08** | Quy chuẩn Git Workflow - Không Tự Động Tạo PR | Chỉ thực hiện `git commit` và `git push` lên repository; tuyệt đối không tự động tạo hoặc cập nhật Pull Request trừ khi có yêu cầu bằng lời nói rõ ràng từ người dùng. |
| **RULE-09** | Bảo mật Định danh & Mật khẩu Băm | Mật khẩu người dùng bắt buộc băm qua PBKDF2-HMAC-SHA256 (600.000 vòng lặp, salt 32 bytes); phiên làm việc quản lý qua JWT HS256 (thời hạn 7 ngày); bảo vệ an toàn ngân hàng đề thi. |
| **RULE-10** | Tích lũy Ngân hàng Chuẩn hóa từ Soạn thảo | Khi lưu đề thi từ Composer vào Ngân hàng, hệ thống bắt buộc bóc tách trọn vẹn cả 3 thể thức QĐ 764, bảo toàn đồ thị TikZ, BBT `tkz-tab`, lời giải chi tiết và tự động gán nhãn YCCĐ. |
| **RULE-11** | Bảo toàn 4 Nguyên Tắc Trộn Đề An Toàn (Safe Shuffling) | Hoán vị mã đề bắt buộc tuân thủ 100%: Section Integrity (đảo trong cùng phần), Passage Integrity (bảo toàn ngữ liệu câu chùm), Option Anchor Rule (khóa mỏ neo tại vị trí D), và Key Matrix (bảng đối chiếu đáp án). |
| **RULE-12** | Đối soát Tồn kho Ma trận & Ràng buộc Khả dụng | Trước khi rút đề, hệ thống đối soát số lượng câu hỏi khả dụng theo từng ô ma trận; nếu thiếu câu phải đưa ra cảnh báo chính xác (số lượng thiếu, YCCĐ, mức độ) và chặn rút đề nếu không bật cờ allow_partial. |
| **RULE-13** | Hoán đổi Câu hỏi Đề Gốc Độc lập (In-Place Item Swap) | Khi đổi câu hỏi trong Master Exam, câu mới bắt buộc cùng YCCĐ, cùng mức độ nhận thức Bloom và cùng thể thức thi; hệ thống tự động làm mới đề gốc và hủy bỏ các mã đề hoán vị cũ để đảm bảo tính nhất quán. |

---

## 5. MA TRẬN TRUY XUẤT NGUỒN GỐC (TRACEABILITY MATRIX)

| Mã BRD | Tên Nghiệp vụ | Phân hệ Đáp ứng | Ưu tiên | Giá trị Giải quyết |
|:---|:---|:---|:---:|:---|
| **BR-01** | AI Số hoá Đề thi & Studio HITL | AI Parsing Engine & HITL | P0 | Giảm 90% thời gian gõ lại đề thủ công |
| **BR-02** | Dựng Đồ thị TikZ SVG & Chuẩn hóa Toán | TikZ Renderer & LaTeX Sanitizer | P0 | Hiển thị đồ thị vector sắc nét, chống lỗi KaTeX |
| **BR-03** | Ngân hàng Câu hỏi Chuẩn hóa & CRUD | Taxonomy & Item Bank | P0 | Quản lý vòng đời đầy đủ, lọc 6 tầng TT 32, xuất/nhập đa định dạng, chống trùng lặp |
| **BR-04** | Ma trận Đề thi 2D theo YCCĐ & Đối soát Tồn kho | Matrix Blueprint Builder | P0 | Tự động hóa tạo đề thi cân đối cấu trúc TT 22 & QĐ 764, 3 Presets, xuất bản bản đặc tả |
| **BR-05** | Động cơ Sinh & Trộn Đề An Toàn 4 Nguyên Tắc | Safe Shuffling Engine & Master Exam | P0 | Chống lỗi logic đáp án neo, bảo toàn bài đọc, đổi câu hỏi linh hoạt, sinh ma trận đáp án |
| **BR-06** | Xuất bản Vector PDF, Word OMML & Gói ZIP | Export Service & Publishing Pipeline | P0 | Xuất bản in ấn 1-click, đóng gói trọn gói ZIP đề thi, lời giải, barem bậc thang và phiếu OMR |
| **BR-07** | Trợ lý Soạn thảo AI & Thay thế Câu hỏi Thông minh | Composer Copilot & Question Replacement Engine | P0 | Hỗ trợ giáo viên chỉnh sửa/thay thế câu hỏi 1-click, bảo toàn code và trải nghiệm mượt mà |
| **BR-08** | Xác thực Người dùng & Phân quyền Khảo thí | Auth Service & User Management | P0 | Bảo mật kho đề thi, hỗ trợ OAuth Google/GitHub, JWT và phân quyền RBAC Giáo viên / Học sinh |
| **BR-09** | Lưu Đề từ Soạn Thảo vào Ngân Hàng | Composer & Item Bank Ingestion | P0 | Khép kín chu trình biên soạn, tích lũy tự động kho câu hỏi chuẩn quốc gia chỉ với 1 click |
