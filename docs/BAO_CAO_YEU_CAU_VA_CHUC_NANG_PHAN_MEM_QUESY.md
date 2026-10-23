# BÁO CÁO CHI TIẾT YÊU CẦU VÀ CÁC CHỨC NĂNG CHÍNH CỦA PHẦN MỀM QUESY

---

| **Thuộc tính** | **Nội dung** |
|:---|:---|
| **Tên phần mềm** | **QUESY (Question Ecosystem System)** |
| **Tên đầy đủ** | Nền tảng Số hóa, Quản lý Đề thi, Ngân hàng Câu hỏi & Dựng Đồ thị Toán học Tự động bằng AI |
| **Mã hiệu tài liệu** | `QUESY-SRS-FRD-REPORT-2026` |
| **Phiên bản hệ thống** | `v2.6 (Production Ready)` |
| **Tiêu chuẩn thiết kế & kỹ thuật** | IEEE Std 830-1998 / ISO/IEC/IEEE 29148, Apple Human Interface Guidelines (HIG), Thông tư 32/2018/TT-BGDĐT, Quyết định 764/QĐ-BGDĐT (Định dạng đề thi 2025) |
| **Trạng thái kiểm thử** | 55/55 Automated Pytest Suites Passing (100%) |

---

## MỤC LỤC
1. [Giới thiệu & Định danh Phần mềm](#1-giới-thiệu--định-danh-phần-mềm)
2. [Sứ mệnh & Các Bài toán Thực tế Quesy Giải quyết](#2-sứ-mệnh--các-bài-toán-thực-tế-quesy-giải-quyết)
3. [Căn cứ Pháp lý & Tiêu chuẩn Khảo thí Quốc gia](#3-căn-cứ-pháp-lý--tiêu-chuẩn-khảo-thí-quốc-gia)
4. [Các Yêu cầu Chức năng Chính (Core Functional Requirements)](#4-các-yêu-cầu-chức-năng-chính-core-functional-requirements)
   - [4.1. Phân hệ Tiếp nhận & Số hóa Đề thi bằng AI (AI Ingestion & Parsing Pipeline)](#41-phân-hệ-tiếp-nhận--số-hóa-đề-thi-bằng-ai-ai-ingestion--parsing-pipeline)
   - [4.2. Phân hệ Studio Hậu kiểm Đối chiếu Song song (HITL Review Studio)](#42-phân-hệ-studio-hậu-kiểm-đối-chiếu-song-song-hitl-review-studio)
   - [4.3. Phân hệ Bộ Dựng Đồ Thị Vector SVG & Chuẩn Hóa Toán Học (TikZ Engine & LaTeX Sanitizer)](#43-phân-hệ-bộ-dựng-đồ-thị-vector-svg--chuẩn-hóa-toán-học-tikz-engine--latex-sanitizer)
   - [4.4. Phân hệ Cây Kiến thức Chuẩn hóa & Dạng Câu hỏi (Taxonomy & Problem Archetypes)](#44-phân-hệ-cây-kiến-thức-chuẩn-hóa--dạng-câu-hỏi-taxonomy--problem-archetypes)
   - [4.5. Phân hệ Quản lý Ngân hàng Câu hỏi & Chống Trùng lặp AI (Item Bank & Deduplication)](#45-phân-hệ-quản-lý-ngân-hàng-câu-hỏi--chống-trùng-lặp-ai-item-bank--deduplication)
   - [4.6. Phân hệ Ma trận Đề thi & Rút Đề theo Ràng buộc (Exam Matrix & Solver)](#46-phân-hệ-ma-trận-đề-thi--rút-đề-theo-ràng-buộc-exam-matrix--solver)
   - [4.7. Phân hệ Động cơ Trộn Đề An Toàn (Safe Shuffling Engine)](#47-phân-hệ-động-cơ-trộn-đề-an-toàn-safe-shuffling-engine)
   - [4.8. Phân hệ Xuất bản Đề thi Word OMML 2 Cột & In ấn (Publishing & Export Service)](#48-phân-hệ-xuất-bản-đề-thi-word-omml-2-cột--in-ấn-publishing--export-service)
   - [4.9. Phân hệ Chấm điểm Bậc thang & Quản lý Bảng điểm Lớp học (Grade & Roster Management)](#49-phân-hệ-chấm-điểm-bậc-thang--quản-lý-bảng-điểm-lớp-học-grade--roster-management)
   - [4.10. Phân hệ Soạn đề LaTeX Trực tiếp & Trợ lý AI Copilot (Composer & Smart Diff)](#410-phân-hệ-soạn-đề-latex-trực-tiếp--trợ-lý-ai-copilot-composer--smart-diff)
5. [Yêu cầu Phi chức năng & Trải nghiệm Người dùng (NFR & UX)](#5-yêu-cầu-phi-chức-năng--trải-nghiệm-người-dùng-nfr--ux)
6. [Ma trận Phân định Trách nhiệm & Nghiệm thu (Traceability & Acceptance Matrix)](#6-ma-trận-phân-định-trách-nhiệm--nghiệm-thu-traceability--acceptance-matrix)

---

## 1. GIỚI THIỆU & ĐỊNH DANH PHẦN MỀM

* **Tên thương hiệu phần mềm:** **QUESY** (viết tắt từ *Question Ecosystem System*).
* **Tên đầy đủ của hệ thống:** **Nền tảng Số hóa, Quản lý Đề thi, Ngân hàng Câu hỏi & Dựng Đồ thị Toán học Tự động bằng AI**.
* **Định vị sản phẩm:** Nền tảng phần mềm EdTech chuyên sâu dành cho Giáo viên bộ môn (Toán học, Vật lí, Hóa học, Sinh học...), Tổ trưởng chuyên môn, Ban Giám hiệu nhà trường và các Hội đồng Khảo thí. Quesy chuyển đổi toàn diện quy trình khảo thí từ thủ công, rời rạc sang quy trình số hóa khép kín, tự động hóa từ khâu tiếp nhận đề thô, bóc tách công thức toán, biên dịch đồ thị hàm số, chuẩn hóa ngân hàng câu hỏi, rút đề theo ma trận, xáo trộn mã đề an toàn, cho tới khâu xuất bản in ấn và chấm thi.

---

## 2. SỨ MỆNH & CÁC BÀI TOÁN THỰC TẾ QUESY GIẢI QUYẾT

Trong công tác biên soạn đề kiểm tra định kỳ và quản lý ngân hàng đề thi tại Việt Nam, giáo viên và các hội đồng khảo thí đối mặt với **6 rào cản kỹ thuật nghiêm trọng**:

| STT | Khó khăn / Nỗi đau thực tế | Giải pháp công nghệ đột phá của Quesy |
|:---:|:---|:---|
| **1** | **Gõ lại đề thi thủ công tốn hàng giờ:** Giáo viên mất 1.5 – 3 giờ để gõ lại một đề thi từ file PDF scan, ảnh chụp điện thoại hoặc file Word cũ; công thức MathType cũ bị lỗi thời, vỡ font khi sao chép. | **AI Ingestion & OCR Đa phương thức:** Tự động số hóa đề thi từ PDF scan, DOCX, ảnh chụp; giải mã trực tiếp dòng nhị phân MathType MTEF sang mã LaTeX chuẩn trong vài giây. |
| **2** | **Đồ thị và hình vẽ bị bỏ quên hoặc méo tỷ lệ:** OCR thông thường chỉ nhận diện văn bản thô, bỏ qua hình vẽ; hoặc khi vẽ đồ thị hàm phân thức có tiệm cận, tọa độ vọt lên vô cực làm khung hình bị co kéo méo mó. | **TikZ Engine & Auto-clipping Vector SVG:** Tự động biên dịch mã TikZ sang đồ họa vector SVG sắc nét qua Kroki; thuật toán Auto-clipping khống chế khung hình cân đối, hỗ trợ đồ thị trong đề bài và từng phương án A, B, C, D. |
| **3** | **Lỗi hiển thị công thức toán học (KaTeX Crashes):** Dấu ngoặc đơn/vuông bị lệch cỡ khi bọc phân số, số thập phân bị hở khoảng cách vô lý (`15 , 25`), vectơ dùng ký hiệu `\vec` bị ngắn cụt đầu. | **Bộ Chuẩn Hóa Toán Học Tự Động:** Chuẩn hóa toàn diện 4 yếu tố: dấu ngoặc kích thước động `\left`/`\right`, số thập phân chuẩn `{,}`, phân số `\dfrac`, ký hiệu vectơ `\overrightarrow`, vá lỗi môi trường `tabular` sang KaTeX `array`. |
| **4** | **Trộn đề làm vỡ logic câu hỏi:** Phần mềm trộn đề cổ điển đảo đáp án ngẫu nhiên khiến câu *"Cả A và B đều đúng"* nhảy lên vị trí A; bài đọc hiểu chung bị tách rời khỏi câu hỏi con; câu trắc nghiệm bị đảo lẫn vào phần tự luận. | **Động Cơ Trộn Đề An Toàn (Safe Shuffling Engine):** Khóa neo phương án phụ thuộc vị trí (**Option Anchor** - luôn neo ở D), bảo toàn ngữ cảnh bài đọc chung (**Passage Integrity**), bảo toàn phân vùng phần thi (**Section Integrity**) và tự động sinh bảng đối chiếu đáp án. |
| **5** | **Chấm điểm Đúng/Sai 4 ý phức tạp:** Dạng trắc nghiệm Đúng/Sai 4 khẳng định theo cấu trúc thi 2025 có cơ chế điểm bậc thang (0.1đ – 0.25đ – 0.5đ – 1.0đ), rất dễ tính nhầm khi chấm tay. | **Hệ Thống Chấm Điểm Bậc Thang & Quản Lý Lớp Học:** Tự động chấm điểm theo đúng công thức bậc thang, quản lý danh sách học sinh theo SBD/Mã học sinh, xuất/nhập bảng điểm Excel UTF-8 BOM chống lỗi font tiếng Việt. |
| **6** | **Dàn trang in ấn Word mất công:** Giáo viên phải tự kẻ bảng phách, chia 2 cột thủ công, công thức toán xuất ra không tương thích với trình soạn thảo Microsoft Word bản quyền. | **Xuất Bản 1-Click Chuẩn Khảo Thí:** Xuất file Word `.docx` 2 cột chuẩn phom Bộ GD&ĐT với công thức **Microsoft Word OMML native (`<m:oMath>`)**, xuất PDF in ấn, phiếu soi đáp án trắc nghiệm OMR đóng gói trong file ZIP. |

---

## 3. CĂN CỨ PHÁP LÝ & TIÊU CHUẨN KHẢO THÍ QUỐC GIA

Quesy được xây dựng tuân thủ tuyệt đối các văn bản quy phạm pháp luật và tiêu chuẩn kỹ thuật khảo thí của Bộ Giáo dục và Đào tạo:

1. **Thông tư số 32/2018/TT-BGDĐT (Chương trình Giáo dục phổ thông 2018):**
   - **Nguyên tắc cốt lõi:** Cấu trúc phân loại ngân hàng câu hỏi **tuyệt đối không phân chia theo các bộ sách giáo khoa thương mại** (như Kết nối tri thức, Cánh diều, Chân trời sáng tạo...). Chương trình quốc gia ban hành theo Thông tư 32 là căn cứ pháp lý duy nhất; sách giáo khoa chỉ là tài liệu tham khảo giảng dạy.
   - **Cấu trúc phân cấp chuẩn năng lực 6 tầng:**
     $$\text{Cấp học / Khối lớp} \longrightarrow \text{Môn học} \longrightarrow \text{Mạch nội dung (Strand)} \longrightarrow \text{Chủ đề / Chuyên đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{YCCĐ\ (Yêu\ cầu\ cần\ đạt)} \longrightarrow \mathbf{Dạng\ câu\ hỏi}$$
   - **Bảng động từ đánh giá 3 mức độ nhận thức:**
     - *Nhận biết (Recognition):* Nhận biết, nhớ lại (đọc, đếm, viết, làm quen, nhận dạng...).
     - *Thông hiểu (Comprehension):* Diễn đạt theo ý hiểu cá nhân (mô tả, giải thích, thể hiện, sắp xếp...).
     - *Vận dụng (Application):* Vận dụng giải quyết vấn đề thực tiễn (tính toán, vẽ, thực hiện, áp dụng công thức, so sánh, chứng minh - bao gồm cả Vận dụng cao).

2. **Quyết định số 764/QĐ-BGDĐT (Định dạng cấu trúc đề thi Tốt nghiệp THPT từ năm 2025):**
   - **Phần I:** Câu hỏi trắc nghiệm nhiều lựa chọn (4 phương án A, B, C, D - chọn 1 đáp án đúng).
   - **Phần II:** Câu hỏi trắc nghiệm Đúng/Sai (Mỗi câu gồm 1 thân bài và 4 khẳng định a, b, c, d độc lập). Điểm số tính theo bậc thang tiến bộ:
     - Đúng 1 ý: $0{,}1$ điểm.
     - Đúng 2 ý: $0{,}25$ điểm.
     - Đúng 3 ý: $0{,}5$ điểm.
     - Đúng cả 4 ý: $1{,}0$ điểm.
   - **Phần III:** Câu hỏi trắc nghiệm dạng trả lời ngắn (Học sinh điền kết quả dạng số thập phân, phân số hoặc chuỗi ký tự, hệ thống hỗ trợ dung sai $\pm \epsilon$).

---

## 4. CÁC YÊU CẦU CHỨC NĂNG CHÍNH (CORE FUNCTIONAL REQUIREMENTS)

Hệ thống Quesy bao gồm **9 phân hệ chức năng cốt lõi**, phối hợp nhịp nhàng tạo thành một dây chuyền công nghệ khép kín:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                DÂY CHUYỀN CHỨC NĂNG CỦA QUESY                          │
└────────────────────────────────────────────────────────────────────────────────────────┘

  [1. AI Ingestion] ──────► [2. HITL Review Studio] ──────► [3. TikZ & LaTeX Sanitizer]
   - DOCX (MathType MTEF)    - Dual-Pane Sync Scroll        - Vector SVG compilation
   - PDF Scan / Photo        - Confidence Barometer          - Auto-clip asymptotes
   - Vision LLM extract      - 1-Click In-place Editor       - \left \right, {,}, \dfrac
                                      │
                                      ▼
  [6. Matrix Blueprint] ◄───── [5. Item Bank] ◄──────────── [4. Competency Taxonomy]
   - 2D Blueprint grid        - AI Duplicate Check (pgvector)- Circular 32 6-tier tree
   - Bank stock alert         - 5 Item Formats (Dec. 764)    - Problem Archetypes
   - Constraint solver        - Full lifecycle audit         - Strict no-textbook rule
          │
          ▼
  [7. Safe Shuffling] ──────► [8. OMML Word Export] ──────► [9. Grade & Roster Mgmt]
   - Option Anchor (Rule D)  - 2-Column native OMML          - Decision 764 progressive
   - Passage Integrity       - Full ZIP package              - Excel UTF-8 BOM
   - Section Integrity       - Vector PDF print-ready        - Item psychometrics (p, D)
```

---

### 4.1. Phân hệ Tiếp nhận & Số hóa Đề thi bằng AI (AI Ingestion & Parsing Pipeline)

* **Mã phân hệ:** `MOD-01`
* **Mục tiêu:** Tự động chuyển đổi tài liệu đề thi thô ở mọi định dạng thành dữ liệu câu hỏi số hóa có cấu trúc cao.
* **Các chức năng chi tiết:**
  1. **Tiếp nhận đa định dạng tài liệu:** Cho phép người dùng tải lên các tệp `.docx`, `.doc`, `.pdf` nhiều trang, ảnh chụp `.png`, `.jpg`, `.webp` (dung lượng tối đa 50MB mỗi tệp).
  2. **Giải mã nhị phân MathType OLE (MTEF to LaTeX):** Khi tiếp nhận tệp Word, hệ thống quét trực tiếp các OLE Object, trích xuất chuỗi nhị phân MathType MTEF và chuyển dịch trực tiếp sang cú pháp LaTeX chuẩn (`$...$` inline, `$$...$$` display). Khắc phục triệt để lỗi vỡ font ký hiệu toán học cổ điển.
  3. **Tiền xử lý hình ảnh thị giác (Computer Vision Preprocessing):** Với tệp PDF scan hoặc chùm ảnh, hệ thống tự động render ảnh 300 DPI, áp dụng thuật toán cân bằng góc nghiêng xoay trang (OpenCV Deskew) và khử nhiễu nền bóng mờ (Adaptive Binarization).
  4. **Bóc tách cấu trúc bằng Vision LLM đa phương thức:** Tích hợp linh hoạt các mô hình thị giác tiên tiến (Google Gemini 1.5, OpenAI GPT-4o, Anthropic Claude, hoặc mô hình cục bộ Offline). Ép khuôn dữ liệu đầu ra nghiêm ngặt theo JSON Schema: tách biệt rõ Tiêu đề trường/sở, Phần thi (I, II, III), Thân câu hỏi, Phương án lựa chọn, Hình ảnh, và Bảng biểu.
  5. **Tự động nhận diện & Cắt ảnh đồ thị/hình học (Auto Image Crop):** Tự động phát hiện tọa độ Bounding Box của hình minh họa, biểu đồ, mạch điện; cắt ảnh, nén định dạng WebP sắc nét dung lượng nhẹ và gán mã định danh `[IMAGE:url]` vào đúng vị trí trong thân câu hỏi.
  6. **Tự động khớp nối Đáp án & Lời giải:** Quét bảng đáp án ở cuối đề thi hoặc tệp đáp án rời đi kèm, tự động gán thuộc tính `is_correct` cho từng phương án và gộp lời giải chi tiết vào từng câu hỏi.

---

### 4.2. Phân hệ Studio Hậu kiểm Đối chiếu Song song (HITL Review Studio)

* **Mã phân hệ:** `MOD-02`
* **Mục tiêu:** Cung cấp môi trường hậu kiểm Human-in-the-Loop giúp giáo viên kiểm soát chất lượng 100% dữ liệu trước khi lưu vào ngân hàng chính thức.
* **Các chức năng chi tiết:**
  1. **Không gian làm việc đối xứng toàn màn hình (Dual-pane Workspace):** Bố cục tràn màn hình 100% viewport width:
     - *Khung bên trái:* Trình xem tài liệu gốc (PDF/Ảnh/Word Viewer).
     - *Khung bên phải:* Luồng các thẻ câu hỏi điện tử đã được bóc tách và render KaTeX thời gian thực.
  2. **Giai đoạn Đệm & Sắp xếp lại Trang (Staging & Reordering):** Cho phép giáo viên xem trước ảnh các trang đã tải lên, đảo thứ tự trang (`←`, `→`), xóa trang lỗi, hoặc bổ sung trang mới trước khi bấm nút kích hoạt AI bóc tách.
  3. **Thanh đo mức độ tin cậy AI (Confidence Barometer):** Hiển thị trực quan chỉ số tin cậy cho từng câu hỏi:
     - *Xanh (Confidence $\ge 95\%$):* Đầy đủ dữ liệu, công thức toán chuẩn, có đáp án đúng.
     - *Vàng (Confidence $80\% - 94\%$):* Cần xem xét lại (thiếu lời giải hoặc ký hiệu nghi ngờ).
     - *Đỏ (Confidence $< 80\%$):* Thiếu đáp án đúng hoặc cú pháp công thức lỗi.
  4. **Cuộn trang đồng bộ siêu tốc (Synchronized Scrolling):** Nhấp vào bất kỳ câu hỏi nào bên cột phải, tài liệu gốc bên cột trái tự động cuộn đến đúng vị trí trang đó với độ trễ phản hồi $< 100$ms.
  5. **Trình biên tập nhanh tại chỗ (In-Place HITL Editor):**
     - Đổi đáp án đúng chỉ bằng 1 cú nhấp chuột lên nhãn A, B, C, D.
     - Nhấp đúp vào công thức để mở hộp thoại soạn thảo LaTeX với Live Preview tức thì.
     - Phân loại và gán nhanh mã Yêu cầu cần đạt (YCCĐ) theo cây danh mục Thông tư 32.
     - Nút khóa neo phương án cố định (`is_fixed = true`).

---

### 4.3. Phân hệ Bộ Dựng Đồ Thị Vector SVG & Chuẩn Hóa Toán Học (TikZ Engine & LaTeX Sanitizer)

* **Mã phân hệ:** `MOD-03`
* **Mục tiêu:** Tự động dựng lại đồ thị hàm số và hình học sắc nét vô hạn, loại bỏ triệt để mọi lỗi hiển thị toán học KaTeX.
* **Các chức năng chi tiết:**
  1. **Biên dịch TikZ/PGFPlots sang Vector SVG qua Kroki:** Tiếp nhận các đoạn mã nguồn TikZ trong câu hỏi và biên dịch trực tiếp sang vector SVG sắc nét thông qua dịch vụ Kroki.
  2. **Bộ nhớ đệm đồ họa cục bộ (Local Disk Cache):** Đồ thị SVG sau khi biên dịch được băm mã SHA-256 lưu trữ tại `storage/tikz_cache/`. Lần tải sau trả về kết quả tức thì (0ms latency), hoạt động hoàn hảo khi không có internet.
  3. **Thuật toán Tự động khống chế khung hình (Auto-clipping Plot Bounds):** Khi vẽ các đồ thị hàm phân thức bậc nhất trên bậc nhất ($y = \frac{ax+b}{cx+d}$) hoặc hàm có tiệm cận đứng/ngang, tọa độ hàm số có thể vọt lên vô cực làm đồ thị bị co rúm méo mó. Thuật toán của Quesy tự động phát hiện miền tọa độ $x, y$ và chèn khung `\clip` an toàn, bảo đảm tỷ lệ khung hình luôn vuông vắn, rõ nét.
  4. **Hỗ trợ Đồ thị độc lập trong từng Phương án A, B, C, D:** Cho phép các câu hỏi nhận dạng đồ thị hiển thị 4 đồ thị vector riêng biệt trong 4 thẻ phương án lựa chọn.
  5. **Bộ Chuẩn Hóa 4 Yếu Tố Toán Học:**
     - *Dấu ngoặc kích thước động:* Tự động bọc `\left(...\right)`, `\left[...\right]`, `\left\{...\right\}` giúp dấu ngoặc ôm trọn chiều cao biểu thức phân số/tích phân, đồng thời bảo vệ các căn bậc n `\sqrt[n]{x}`.
     - *Quy chuẩn số thập phân Việt Nam:* Tự động chuyển dấu phẩy thập phân trong đề bài thành `{,}` (ví dụ `15{,}25`) để KaTeX không tạo khoảng hở trắng, đồng thời giữ số sạch ở đáp án (`15,25`).
     - *Phân số hiển thị thoáng đẹp:* Tự động chuyển `\frac` sang `\dfrac` giúp tử số và mẫu số giữ nguyên cỡ chữ lớn dễ đọc.
     - *Ký hiệu vectơ chuẩn:* Tự động thay thế `\vec{AB}` ngắn cụt bằng `\overrightarrow{AB}` chuẩn mực.
     - *Sửa lỗi bảng số liệu:* Chuyển đổi môi trường `tabular` sang KaTeX `array` và tự động cân bằng dấu đóng thẻ `$$`.

---

### 4.4. Phân hệ Cây Kiến thức Chuẩn hóa & Dạng Câu hỏi (Taxonomy & Problem Archetypes)

* **Mã phân hệ:** `MOD-04`
* **Mục tiêu:** Chuẩn hóa toàn bộ kho học liệu và ngân hàng câu hỏi theo Chương trình GDPT 2018 (Thông tư 32).
* **Các chức năng chi tiết:**
  1. **Kiến trúc Cây Phân cấp 6 Tầng Thống nhất Toàn quốc:**
     - Tầng 1: Môn học (`Subject` - Toán, Lí, Hóa, Sinh, Tin, Văn, Anh...).
     - Tầng 2: Cấp học / Khối lớp (`Grade` - Lớp 10, Lớp 11, Lớp 12).
     - Tầng 3: Mạch nội dung (`Strand` - Ví dụ: *Số, Đại số và Một số yếu tố Giải tích*; *Hình học và Đo lường*; *Thống kê và Xác suất*).
     - Tầng 4: Chủ đề / Chuyên đề học tập (`Topic` - Ví dụ: *Ứng dụng đạo hàm để khảo sát hàm số*).
     - Tầng 5: Bài học / Đơn vị kiến thức (`Lesson`).
     - Tầng 6: Yêu cầu cần đạt (`LearningOutcome` - Mã chuẩn TT 32, ví dụ: `TOAN12.GT.01`).
  2. **Quản lý Dạng Câu hỏi Chuyên đề (Problem Archetypes):** Dưới mỗi YCCĐ, hệ thống cho phép tạo các danh mục dạng bài tập chuyên sâu (Ví dụ: *Dạng 1: Đọc đồ thị tìm cực trị*, *Dạng 2: Cực trị hàm chứa tham số $m$*, *Dạng 3: Bài toán tối ưu thực tiễn*). Nhờ đó, thuật toán rút đề sẽ lấy câu hỏi chính xác theo dạng bài, chống hiện tượng đề thi bị lệch dạng.
  3. **Tuyệt đối không phân chia theo Bộ sách giáo khoa:** Trong schema CSDL không tồn tại bất kỳ trường thông tin nào về "Bộ sách", bảo đảm tính trung lập và chuẩn hóa của kỳ thi quốc gia.
  4. **Phân loại 3 Mức độ Nhận thức theo Bảng Động từ TT 32:** Hỗ trợ chuẩn hóa câu hỏi theo 3 mức độ: Nhận biết, Thông hiểu, Vận dụng.

---

### 4.5. Phân hệ Quản lý Ngân hàng Câu hỏi & Chống Trùng lặp AI (Item Bank & Deduplication)

* **Mã phân hệ:** `MOD-05`
* **Mục tiêu:** Quản lý vòng đời câu hỏi, kiểm soát chất lượng học liệu và chống trùng lặp câu hỏi thông minh.
* **Các chức năng chi tiết:**
  1. **Hỗ trợ trọn vẹn 5 Hình thức Khảo thí (Item Formats):**
     - `SINGLE_CHOICE`: Trắc nghiệm 4 lựa chọn (A, B, C, D).
     - `TRUE_FALSE_GROUP`: Trắc nghiệm Đúng/Sai 4 khẳng định con a, b, c, d độc lập (Quyết định 764).
     - `SHORT_ANSWER`: Trắc nghiệm trả lời ngắn kèm dung sai sai số $\pm \epsilon$.
     - `PASSAGE_GROUP`: Câu hỏi chùm (Một đoạn văn bản/ngữ liệu bài đọc cha và các câu hỏi con đi kèm).
     - `ESSAY`: Câu hỏi tự luận có rubric tiêu chí chấm điểm chi tiết.
  2. **Kiểm soát Trùng lặp bằng AI Vector Embeddings:**
     - Mỗi câu hỏi được vector hóa thành vector không gian đa chiều (sử dụng text-embedding).
     - Khi lưu câu hỏi mới, hệ thống tự động đo khoảng cách Cosine Similarity với kho câu hỏi cùng khối môn:
       - *Similarity $< 80\%$:* Lưu trữ bình thường.
       - *$80\% \le \text{Similarity} < 90\%$:* Cảnh báo vàng gợi ý câu hỏi tương tự.
       - *$\text{Similarity} \ge 90\%$:* Chặn lưu tự động và bật hộp thoại cảnh báo trùng lặp màu đỏ, cho phép giáo viên đối chiếu trực quan 2 câu hỏi trước khi quyết định.
  3. **Quản lý Vòng đời Câu hỏi (Item Lifecycle):** Quản lý nghiêm ngặt các trạng thái câu hỏi: `DRAFT` (Nháp) $\rightarrow$ `PENDING_REVIEW` (Chờ duyệt) $\rightarrow$ `APPROVED` (Đã duyệt vào ngân hàng) $\rightarrow$ `ARCHIVED` (Lưu trữ).
  4. **Lưu vết Lịch sử Chỉnh sửa (Audit History):** Tự động ghi lại các phiên bản sửa đổi nội dung câu hỏi, người sửa và thời gian chỉnh sửa.

---

### 4.6. Phân hệ Ma trận Đề thi & Rút Đề theo Ràng buộc (Exam Matrix & Solver)

* **Mã phân hệ:** `MOD-06`
* **Mục tiêu:** Thiết lập bản đặc tả cấu trúc đề thi 2 chiều và tự động rút đề gốc thỏa mãn ma trận.
* **Các chức năng chi tiết:**
  1. **Lưới Thiết kế Ma trận 2 Chiều (2D Test Blueprint Grid):**
     - *Trục dọc:* Danh sách Mạch nội dung $\rightarrow$ Yêu cầu cần đạt (YCCĐ) $\rightarrow$ Dạng câu hỏi.
     - *Trục ngang:* 3 Cấp độ nhận thức (Nhận biết, Thông hiểu, Vận dụng) $\times$ Dạng thức câu hỏi.
     - *Cấu hình ô:* Số lượng câu hỏi cần rút, số điểm tương ứng cho từng câu.
  2. **Kiểm tra Tồn kho Ngân hàng Thời gian thực (Inventory Validation):**
     - Hệ thống kiểm tra số lượng câu hỏi khả dụng (`status = 'APPROVED'`) trong ngân hàng tương ứng với từng ô ma trận.
     - Nếu thiếu hụt câu hỏi, hệ thống đưa ra chẩn đoán chính xác: *"Thiếu 2 câu [Vận dụng - Dạng cực trị chứa tham số m]"* thay vì báo lỗi mơ hồ.
  3. **Động cơ Giải bài toán Ràng buộc (Constraint Satisfaction Solver):**
     - Rút ngẫu nhiên các câu hỏi đạt chuẩn từ ngân hàng.
     - Loại trừ các câu hỏi đã sử dụng trong các kỳ thi gần đây (Exclusion List).
     - Ưu tiên chọn các câu hỏi có chỉ số khảo thí tốt (độ khó $p$, độ phân biệt $D$).
  4. **Tạo Đề thi Gốc (Master Exam):** Tổng hợp danh sách câu hỏi thành Đề gốc (`MasterExam`) hoàn chỉnh, chuẩn bị cho khâu hoán vị mã đề.

---

### 4.7. Phân hệ Động cơ Trộn Đề An Toàn (Safe Shuffling Engine)

* **Mã phân hệ:** `MOD-07`
* **Mục tiêu:** Tạo ra $N$ mã đề hoán vị (101, 102, 103, 104...) từ 1 đề gốc nhưng bảo đảm tuyệt đối tính logic của đề thi.
* **4 Nguyên tắc An toàn Tuyệt đối:**
  1. **Nguyên tắc Khóa Neo Phương án (Option Anchor Rule):**
     - Tự động quét và phát hiện các phương án có nội dung phụ thuộc vị trí tương đối như: *"Cả A và B đều đúng"*, *"Tất cả các đáp án trên"*, *"Không có phương án nào thỏa mãn"*, hoặc phương án có cờ `is_fixed = true`.
     - Các phương án này **bắt buộc luôn bị khóa cố định ở vị trí cuối cùng (D)**. Hệ thống chỉ hoán vị nội bộ các phương án A, B, C độc lập, bảo đảm không bao giờ câu "Cả A và B" nhảy lên vị trí A hay B.
  2. **Nguyên tắc Bảo toàn Ngữ liệu Bài đọc Chung (Passage Integrity):**
     - Đoạn văn bản đọc hiểu cha và chùm câu hỏi con đi kèm luôn được giữ liền kề nhau trong mọi mã đề hoán vị.
     - Thứ tự các câu hỏi con có thể đảo trong nội bộ cụm, nhưng cụm không bao giờ bị xé lẻ hoặc nằm rải rác.
  3. **Nguyên tắc Bảo toàn Phân vùng Phần thi (Section Integrity):**
     - Câu hỏi chỉ hoán vị trong phạm vi từng phần: Phần I trắc nghiệm 4 lựa chọn chỉ đảo trong Phần I; Phần II Đúng/Sai chỉ đảo trong Phần II; Phần III Trả lời ngắn chỉ đảo trong Phần III.
  4. **Ma trận Ánh xạ Đáp án Tự động (Key Generator):**
     - Tự động sinh bảng đối chiếu chéo đáp án giữa Đề gốc và từng mã đề (ví dụ: Câu 5 đề 101 tương ứng Câu 12 đề gốc, đáp án đúng là C).
     - Giúp giáo viên đối chiếu và chấm bài nhanh chóng, chính xác.

---

### 4.8. Phân hệ Xuất bản Đề thi Word MathType OLE, OMML & In ấn (Publishing & Export Service)

* **Mã phân hệ:** `MOD-08`
* **Mục tiêu:** Xuất bản tài liệu đề thi và hướng dẫn giải chuẩn in ấn chỉ bằng 1 cú nhấp chuột, công thức toán nét căng tuyệt đối và hỗ trợ chỉnh sửa trực tiếp qua MathType 7.
* **Các chức năng chi tiết:**
  1. **Định dạng Microsoft Word (.docx) Chuẩn Khảo Thí Quốc Gia:**
     - Thiết lập chuẩn khổ giấy **A4 Portrait (210 x 297 mm)**, lề trang chuẩn $1.5\text{ cm} - 1.8\text{ cm}$, font **Times New Roman** kích cỡ $11\text{ pt}$, giãn dòng $1.15$.
     - Tự động bố cục bảng phách rọc, số báo danh, mã đề thi và tiêu đề chuẩn hóa Sở/Phòng GD&ĐT.
  2. **Công thức Toán MathType 7.0 OLE Object Vector WMF (`math_format="mathtype"`):**
     - Thay vì xuất ảnh bitmap/PNG gây mờ và vỡ hạt khi in ấn, hệ thống sinh trực tiếp **Vector Windows Metafile (WMF)** chuẩn APM (`magic: 0x9AC6CDD7`, base resolution 1440 DPI, scale 32 units/pt). Đạt tỷ lệ $100\%$ vector thuần không có bất kỳ file raster DIB nào.
     - Nhúng luồng OLE Compound File (CFB) với root CLSID `{0002CE03-0000-0000-C000-000000000046}`, stream `\x01CompObj` mang định danh `MathType 7.0 Equation`, và stream `Equation Native` chứa mã MTEF v5 định dạng chuẩn DSMT7 kèm bản ghi `TeX Input Language` bảo toàn chuỗi LaTeX gốc và chuẩn hóa embellishment cho toán tử vectơ (`\vec`, `\overrightarrow`).
     - **Tính năng độc quyền:** Cho phép giáo viên click đúp vào bất kỳ công thức nào trong Word để **mở thẳng phần mềm MathType 7 chỉnh sửa công thức 2 chiều mượt mà, không gặp lỗi OLE activation hay popup cảnh báo thiếu ứng dụng server**.
  3. **Công thức Toán Microsoft Word OMML Native (`<m:oMath>` - `math_format="omml"`):**
     - Chuyển đổi mã TeX sang MathML chuẩn thông qua MathJax, sau đó biên dịch sang định dạng phương trình bản địa Word qua stylesheet `MML2OMML.XSL`.
     - Có cơ chế Fallback tự động tổng hợp OMML thuần Python, bảo đảm chạy ổn định trên mọi môi trường máy chủ Linux/Docker/CI không có bộ Office cài sẵn.
  4. **Tự động Chuyển đổi Bảng Thống kê LaTeX (`\begin{array}`) thành Native Word Table:**
     - Tự động quét và nhận diện các mảng bảng phân phối tần số ghép nhóm hoặc bảng biến thiên trong đề thi.
     - Dựng thành bảng Microsoft Word thực tế (`<w:tbl>`) căn giữa, có viền nét mảnh (`border sz="4"`), loại bỏ triệt để hiện tượng hộp đen (black box) khi xuất sang PDF.
  5. **Dịch vụ MathJax Engine & Persistent Worker:**
     - Tích hợp daemon nền Node.js xử lý MathJax 3/4 với bộ gói TeX đầy đủ (`input/tex-full`).
     - Thời gian sinh công thức siêu tốc: trung bình **~14 ms/công thức**, kèm bộ nhớ đệm 2 tầng (in-memory LRU + disk SHA-256 cache).
     - Tự động bổ sung đệm an toàn (+160 units) chống xén nét mũi tên vectơ $\overrightarrow{AB}$ và tính toán độ hạ dòng `w:position` chính xác cho Word.
  6. **Đóng gói Gói Ấn phẩm Khảo thí Trọn bộ (ZIP Package):** Tự động đóng gói và tải về một tệp ZIP chứa đầy đủ:
     - Các tệp đề thi Word cho từng mã đề (`De_101.docx`, `De_102.docx`...).
     - Các tệp Hướng dẫn giải chi tiết cho từng mã đề (`LoiGiai_101.docx`...).
     - Tệp Bảng đáp án tổng hợp tất cả các mã đề (Excel/CSV UTF-8 BOM + PDF).
     - Phiếu trả lời trắc nghiệm chuẩn máy quét chấm thi OMR.
  7. **Xuất bản PDF Vector In ấn Tức thì:** Tích hợp bộ render PDF nội bộ (sử dụng ReportLab đăng ký font TrueType tiếng Việt Unicode), xuất file PDF in ấn chuẩn trong thời gian $< 100$ms mà không phụ thuộc vào tiến trình Word COM ngoài.

---

### 4.9. Phân hệ Chấm điểm Bậc thang & Quản lý Bảng điểm Lớp học (Grade & Roster Management)

* **Mã phân hệ:** `MOD-09`
* **Mục tiêu:** Hỗ trợ giáo viên chấm thi tự động, quản lý danh sách học sinh và phân tích chất lượng bài thi.
* **Các chức năng chi tiết:**
  1. **Thuật toán Chấm điểm Bậc thang Chuẩn Quyết định 764:**
     - Tự động chấm câu hỏi trắc nghiệm Đúng/Sai 4 khẳng định theo quy tắc lũy tiến chính xác:
       $$1\ \text{ý đúng} \rightarrow 0{,}1\ \text{điểm};\quad 2\ \text{ý đúng} \rightarrow 0{,}25\ \text{điểm};\quad 3\ \text{ý đúng} \rightarrow 0{,}5\ \text{điểm};\quad 4\ \text{ý đúng} \rightarrow 1{,}0\ \text{điểm}$$
  2. **Quản lý Lớp học & Danh sách Học sinh (Classroom & Roster):**
     - Quản lý danh sách học sinh theo từng Lớp học (`Classroom`) và Số báo danh / Mã học sinh (`student_code`), phù hợp thực tế giảng dạy của giáo viên bộ môn mà không đòi hỏi hạ tầng tài khoản phức tạp.
  3. **Nhập / Xuất Bảng điểm Excel / CSV Tương thích UTF-8 BOM:**
     - Mọi tệp xuất dữ liệu bảng điểm và danh sách lớp định dạng CSV/Excel đều được chèn ký tự UTF-8 BOM (`\ufeff`). Nhờ đó, phần mềm Microsoft Excel trên hệ điều hành Windows mở trực tiếp hiển thị 100% tiếng Việt có dấu sắc nét, tuyệt đối không bị lỗi font (mojibake).
  4. **Phân tích Khảo thí Hậu kiểm (Item Psychometrics):**
     - Sau khi có điểm thi, hệ thống tự động tính toán các chỉ số thống kê chất lượng câu hỏi:
       - *Độ khó thực nghiệm ($p$):* $p = \frac{\text{Số học sinh làm đúng}}{\text{Tổng số học sinh dự thi}}$.
       - *Độ phân biệt ($D$):* $D = P_H - P_L$ (Chênh lệch tỷ lệ đúng giữa nhóm $27\%$ điểm cao nhất và nhóm $27\%$ điểm thấp nhất).
     - Tự động gắn cờ cảnh báo câu hỏi lỗi nếu $D < 0.20$ để giáo viên và hội đồng bộ môn xem xét tinh chỉnh hoặc loại bỏ khỏi ngân hàng.

---

### 4.10. Phân hệ Soạn đề LaTeX Trực tiếp & Trợ lý AI Copilot (Composer & Smart Diff)

* **Mã phân hệ:** `MOD-10`
* **Mục tiêu:** Cung cấp không gian làm việc chuyên nghiệp chuẩn hóa theo gói lệnh quốc gia `ex_test.sty` v3.3, biên dịch PDF thời gian thực (Live Preview) và tích hợp Trợ lý AI Copilot hỗ trợ soạn thảo, đề xuất sửa lỗi cục bộ thông minh.
* **Các chức năng chi tiết:**
  1. **Không gian Làm việc Phân tách 2 Cột (6:4 Split View):**
     - Cột trái (60%): Editor mã nguồn Dark mode (`#141824`), toolbar `MỚI`, `THÊM ▾` (7 mẫu lệnh `ex_test`), đánh số dòng, hoàn tác/làm lại, dọn dẹp, sao chép.
     - Cột phải (40%): Xem trước trực tiếp tệp PDF biên dịch từ XeTeX Engine (Live Preview), tab Lịch sử biên dịch, công tắc LỜI GIẢI (`[dethi]` $\leftrightarrow$ `[loigiai]`), menu xuất PDF/TeX/Ngân hàng và thanh nút bấm nổi bật màu xanh **`BIÊN DỊCH`**.
  2. **Thanh Nhập Prompt AI Thu Gọn ở Chân Editor (Compact Floating AI Prompt Bar):**
     - Thanh dạng viên thuốc (floating pill bar) neo tại chân editor (`#composer-ai-compact-bar`), thiết kế bán trong suốt Apple Glassmorphism.
     - *Hành vi click:* Nhấp chuột vào thanh chỉ để focus con trỏ văn bản (`cursor-text`) và nhập liệu bình thường; **tuyệt đối không tự động mở full popup trợ lý** để tránh gián đoạn không gian soạn thảo.
     - *Kích hoạt mở rộng:* Chỉ khi người dùng nhấn phím **`Enter`** hoặc nhấp chuột vào **Nút Gửi Mũi Tên Tròn**, hệ thống mới mở bung giao diện Popup Trợ lý Soạn thảo (`#composer-ai-popup`), chuyển tiếp chuỗi prompt và kích hoạt luồng trả lời của AI Copilot.
     - *Menu mẫu lệnh nhanh:* Nút dấu cộng `+` cung cấp sẵn các mẫu prompt chuẩn (đổi cỡ chữ 12pt, tạo câu hỏi Phần I/II/III, vẽ bảng biến thiên `tkz-tab`, sửa lỗi cú pháp LaTeX).
  3. **Cơ Chế Trích Xuất & Duyệt Đề Xuất Sửa Đổi Trực Tiếp (Smart Inline Diff Suggestion):**
     - Thay vì xuất lại toàn bộ tài liệu dài dòng, AI Copilot tự động bóc tách đề xuất điều chỉnh thành đối tượng `DiffSuggestion` mang nội dung dòng cũ (`old_text`) và dòng mới (`new_text`).
     - Client tự động quét và xác định chính xác số thứ tự dòng (`lineNo`) trong editor, tự động cuộn màn hình đến dòng đó và bôi đen đoạn mã.
     - Banner Duyệt Diff (`#composer-pending-diff-banner`) hiển thị trực tiếp ngay trên editor với badge `GỢI Ý TẠI DÒNG [lineNo]`, hộp đối chiếu xóa đỏ (`- old_text`) và thêm xanh (`+ new_text`), kèm 2 nút bấm thao tác trực tiếp:
       - **`[Đồng ý]` (Accept):** Thay thế chuẩn xác dòng mã cũ bằng dòng mới trong bộ nhớ đệm, tự động gọi biên dịch tức thì `compile(true)` cập nhật Live PDF và hiển thị thông báo thành công.
       - **`[Từ chối]` (Reject):** Đóng banner gợi ý, giữ nguyên 100% mã nguồn ban đầu của giáo viên.
     - Thẻ Diff Card tương tác song song trong luồng chat lịch sử cho phép xem lại và tái áp dụng đề xuất bất cứ lúc nào.

---

## 5. YÊU CẦU PHI CHỨC NĂNG & TRẢI NGHIỆM NGƯỜI DÙNG (NFR & UX)

1. **Thiết kế Trải nghiệm Chuẩn Apple Human Interface Guidelines (HIG):**
   - Bố cục giao diện tối giản, phi trùng lặp, thoáng đãng, phân cấp thị giác rõ ràng.
   - Phản hồi vi mô xúc giác (tactile micro-interactions) khi nhấn nút: hiệu ứng co giãn mượt mà `active:scale-[0.97]`.
   - Font chữ Apple sans-serif đồng nhất toàn hệ thống (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto...`).
   - Điều hướng Single Page Application (SPA) với đường dẫn URL sạch sẽ (`/dashboard`, `/digitize`, `/bank`, `/matrix`, `/shuffler`), hỗ trợ lịch sử trình duyệt và tải lại trang (F5) không bị lỗi 404.
2. **Khả năng Hoạt động Ngoại tuyến (Offline PWA):**
   - Đăng ký Web App Manifest và Service Worker với chiến lược bộ nhớ đệm `Network-First`.
   - Ứng dụng có thể cài đặt trực tiếp lên máy tính hoặc điện thoại của giáo viên, sẵn sàng hoạt động trong điều kiện phòng học hoặc hội trường mất kết nối Internet.
3. **Hiệu năng & Khả năng Chịu tải:**
   - Thời gian bóc tách AI đề thi 50 câu: $< 180$ giây.
   - Thời gian render đồ thị TikZ đã lưu đệm: $\approx 0$ms.
   - Thời gian rút đề và hoán vị 4 mã đề: $< 1.5$ giây.
   - Thời gian tạo gói ấn phẩm Word OMML: $< 3.0$ giây.
4. **An toàn & Toàn vẹn Dữ liệu:**
   - Cơ chế bảo toàn khóa ngoại `CASCADE` trong CSDL quan hệ.
   - Chống xung đột cổng mạng trên máy chủ Windows (`start_server.py` tự động phát hiện và chuyển cổng linh hoạt, chống lỗi `[WinError 10048]`).

---

## 6. MA TRẬN PHÂN ĐỊNH TRÁCH NHIỆM & NGHIỆM THU (TRACEABILITY & ACCEPTANCE MATRIX)

| Mã Phân hệ | Mã Tính năng | Yêu cầu Kỹ thuật Cốt lõi | Phương thức Kiểm thử & Tiêu chuẩn Nghiệm thu |
|:---|:---|:---|:---|
| **MOD-01** | `FEAT-01` | Ingestion DOCX, PDF scan, Ảnh chụp, giải mã MathType MTEF sang LaTeX | Test tự động `test_ai_pipeline.py`: Bóc tách chính xác $\ge 90\%$ công thức toán. |
| **MOD-02** | `FEAT-02` | Studio HITL: Sync scroll, Confidence barometer, In-place editor | Kiểm thử giao diện: Độ trễ cuộn $< 100$ms, đổi đáp án 1-click thành công. |
| **MOD-03** | `FEAT-03` | Dựng TikZ sang SVG qua Kroki, Auto-clipping, chuẩn hóa `\left`/`\right`, `{,}`, `\dfrac` | Test tự động `test_services.py`: $100\%$ đồ thị có tiệm cận được bọc `\clip`, số thập phân chuẩn `{,}`. |
| **MOD-04** | `FEAT-04` | Cây phân loại 6 tầng theo TT 32, Dạng câu hỏi, không có trường Bộ sách | Test tự động `test_taxonomy.py`: CSDL chứa đầy đủ YCCĐ, tuyệt đối không có trường `textbook`. |
| **MOD-05** | `FEAT-05` | Ngân hàng 5 dạng câu hỏi, kiểm tra trùng lặp AI Cosine Similarity $\ge 0.90$ | Test tự động `test_deduplication.py`: Chặn lưu thành công và cảnh báo khi câu trùng $\ge 90\%$. |
| **MOD-06** | `FEAT-06` | Thiết lập ma trận 2D, kiểm tra tồn kho ngân hàng, rút câu hỏi thỏa mãn ràng buộc | Test tự động `test_api_endpoints.py`: Rút đề đúng tỷ lệ điểm và mức độ nhận thức. |
| **MOD-07** | `FEAT-07` | Trộn đề an toàn: Option Anchor (Khóa D), Passage Integrity, Section Integrity | Test tự động `test_rules_shuffling.py`: 1.000 lần sinh mã đề, $0\%$ câu neo bị đảo, $0\%$ bài đọc bị tách rời. |
| **MOD-08** | `FEAT-08` | Xuất file Word 2 cột OMML native, PDF vector in ấn, đóng gói trọn bộ ZIP | Test tự động `test_docx_export.py`: Mở file Word trên MS Word công thức chuẩn OMML `<m:oMath>`, không vỡ cột. |
| **MOD-09** | `FEAT-09` | Chấm điểm Đúng/Sai bậc thang (0.1 - 0.25 - 0.5 - 1.0), xuất Excel UTF-8 BOM | Test tự động `test_excel_roster_import_export.py`: Điểm số chính xác, file CSV không lỗi font tiếng Việt. |
| **MOD-10** | `FEAT-10` | Soạn đề LaTeX, Compact Prompt Bar (click để gõ, Enter mở popup), AI Inline Diff [Đồng ý]/[Từ chối] | Test tự động `test_composer.py`: Bóc tách diff `DiffSuggestion` chuẩn xác, thay thế đúng dòng và recompile thành công. |

---
*Báo cáo được biên soạn và chuẩn hóa phục vụ lưu trữ tài liệu kỹ thuật của dự án Quesy.*
