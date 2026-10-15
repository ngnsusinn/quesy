# TÀI LIỆU YÊU CẦU NGHIỆP VỤ (BUSINESS REQUIREMENTS DOCUMENT - BRD)

**Dự án:** Hệ thống Quản lý Đề thi và Ngân hàng Câu hỏi Tích hợp AI Số hoá Đề thi  
**Tên mã dự án (Project Code):** QUESY  
**Căn cứ Pháp lý & Chuẩn mực Chuyên môn:**  
- **Thông tư số 32/2018/TT-BGDĐT** ngày 26/12/2018 của Bộ trưởng Bộ Giáo dục và Đào tạo ban hành Chương trình Giáo dục phổ thông (CT GDPT 2018).  
- **Thông tư số 22/2021/TT-BGDĐT** ngày 20/07/2021 của Bộ GD&ĐT quy định về đánh giá học sinh trung học cơ sở và trung học phổ thông.  
- **Quyết định số 764/QĐ-BGDĐT** ngày 08/03/2024 của Bộ GD&ĐT quy định về Cấu trúc định dạng đề thi Kỳ thi tốt nghiệp THPT từ năm 2025.  
**Phiên bản (Version):** 2.0 (Chuẩn hóa toàn diện theo Thông tư 32/2018/TT-BGDĐT)  
**Trạng thái (Status):** Đã phê duyệt cập nhật (Approved for Implementation)  
**Ngày phát hành:** 2026-10-14  

---

## BẢNG THEO DÕI THAY ĐỔI TÀI LIỆU (DOCUMENT HISTORY)

| Phiên bản | Ngày | Tác giả | Mô tả thay đổi | Người duyệt |
|:---|:---|:---|:---|:---|
| 1.0 | 2026-10-14 | BA Team | Khởi tạo tài liệu BRD ban đầu | PM |
| 1.1 | 2026-10-14 | BA Team | Bổ sung phân tầng Dạng câu hỏi, loại bỏ phân loại theo bộ sách | PM |
| **2.0** | 2026-10-14 | BA Team & Khảo thí | **Cập nhật toàn diện chuẩn hóa theo Thông tư 32/2018/TT-BGDĐT**: Tích hợp cây Mạch nội dung -> Yêu cầu cần đạt (YCCĐ); Đánh giá phẩm chất & năng lực; Chuẩn định dạng đề thi mới 2025 theo Quyết định 764/QĐ-BGDĐT. | Hội đồng Khảo thí & PM |

---

## 1. TỔNG QUAN DỰ ÁN & MỤC TIÊU KINH DOANH (EXECUTIVE SUMMARY)

### 1.1. Bối cảnh Giáo dục & Căn cứ Pháp lý Cốt lõi
Chương trình Giáo dục phổ thông 2018 (ban hành kèm theo **Thông tư số 32/2018/TT-BGDĐT**) đánh dấu bước chuyển biến căn bản của nền giáo dục Việt Nam: **Chuyển từ nền giáo dục định hướng nội dung (truyền thụ kiến thức một chiều) sang nền giáo dục định hướng năng lực (phát triển toàn diện phẩm chất và năng lực người học)**.

Nguyên tắc pháp lý tối cao được quy định rõ tại Thông tư 32/2018/TT-BGDĐT:
1. **Chương trình là văn bản mang tính pháp lệnh duy nhất và thống nhất toàn quốc.** Căn cứ đánh giá kết quả học tập của học sinh là các **Yêu cầu cần đạt (YCCĐ)** về phẩm chất và năng lực quy định trong Chương trình tổng thể và các chương trình môn học.
2. **Chủ trương "Một chương trình, nhiều bộ sách giáo khoa":** Sách giáo khoa (như Kết nối tri thức với cuộc sống, Cánh diều, Chân trời sáng tạo...) chỉ đóng vai trò là tài liệu dạy học và học liệu tham khảo cụ thể hóa chương trình. **Đề thi, ma trận kiểm tra và ngân hàng câu hỏi chuẩn quốc gia tuyệt đối không căn cứ vào ngữ liệu riêng biệt của bất kỳ bộ SGK nào**, mà phải bám sát trực tiếp vào chuẩn **Yêu cầu cần đạt (YCCĐ)** của Chương trình GDPT 2018.
3. **Đổi mới công tác Khảo thí & Đánh giá định kỳ:** Theo Thông tư 22/2021/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (áp dụng từ kỳ thi tốt nghiệp THPT 2025), cấu trúc đề thi được chuẩn hóa với 3 phần thi trắc nghiệm phi truyền thống (Trắc nghiệm nhiều lựa chọn, Trắc nghiệm Đúng/Sai 4 ý có tính điểm lũy tiến, Trắc nghiệm Trả lời ngắn) cùng các câu hỏi giải quyết vấn đề thực tiễn gắn với đời sống.

### 1.2. Nỗi đau Thực tế của Ngành Khảo thí
- **Gánh nặng nhập liệu và số hóa:** Hàng chục nghìn đề thi của các trường, sở GD&ĐT đang tồn tại dưới dạng file Word (`.docx`), PDF hoặc scan. Giáo viên mất 1.5 - 2 giờ để gõ lại một đề có công thức MathType/LaTeX và hình vẽ.
- **Lệch chuẩn chương trình mới:** Nhiều ngân hàng câu hỏi cũ bị phân mảnh theo bộ SGK hoặc tiếp cận đơn thuần theo bài học SGK cũ, không liên kết được với mã chuẩn Yêu cầu cần đạt (YCCĐ) và năng lực đặc thù theo Thông tư 32.
- **Rủi ro khi trộn đề thi:** Đề thi theo định dạng mới (Đúng/Sai 4 ý, câu chùm ngữ liệu) nếu trộn bằng các phần mềm trộn đề cổ điển sẽ làm xé lẻ câu con, làm mất nghĩa của các đáp án phụ thuộc vị trí ("Cả A và B", "Tất cả các ý trên").

### 1.3. Tầm nhìn Sản phẩm (Product Vision)
Xây dựng nền tảng **Quesy** - Hệ sinh thái Quản lý Đề thi và Ngân hàng Câu hỏi chuẩn hóa năng lực, tích hợp Trí tuệ Nhân tạo Đa phương thức (Multimodal Vision LLM) để:
- Tự động bóc tách và số hóa đề thi từ file thô (Word/PDF/ảnh) sang ngân hàng câu hỏi có cấu trúc JSON/LaTeX.
- Quản trị ngân hàng câu hỏi chuẩn hóa 100% theo **Yêu cầu cần đạt (YCCĐ) của Thông tư 32/2018/TT-BGDĐT**, gắn với **Dạng câu hỏi** và **Năng lực đặc thù**, không phụ thuộc bộ sách giáo khoa.
- Tự động sinh đề và hoán vị mã đề an toàn ngữ nghĩa theo ma trận kiểm tra định kỳ (giữa kỳ, cuối kỳ) và cấu trúc đề thi tốt nghiệp THPT 2025.
- Xuất bản tài liệu Word (`.docx`) 2 cột công thức OMML chuẩn in ấn của Bộ GD&ĐT.

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

### BR-01: PHÂN HỆ AI SỐ HOÁ ĐỀ THI & STUDIO HẬU KIỂM SONG SONG
- **BR-01.1 Tiếp nhận tài liệu đề thi:** Hỗ trợ `.docx`, `.doc` (chứa MathType OLE binary), `.pdf` (text-based hoặc scanned), ảnh chụp `.png`, `.jpg`. Tải kèm file bảng đáp án / barem chấm rời. Dung lượng tối đa 50MB.
- **BR-01.2 Bóc tách cấu trúc & chuyển đổi LaTeX chuẩn:** Tự động tách câu, các phần (Phần I, II, III). Giải mã binary MathType MTEF sang chuỗi LaTeX chuẩn (`$...$` inline, `$$...$$` block). Khử nhiễu, cân bằng góc nghiêng trang scan (Deskew & Binarization).
- **BR-01.3 Tự động Cắt ảnh Hình học & Đồ thị (Auto Image Crop):** Bounding Box đồ thị hàm số, hình học không gian, sơ đồ mạch điện, biểu đồ hóa học. Cắt ảnh độ phân giải cao, nén WebP, lưu vào S3/MinIO và nhúng liên kết vào thân câu hỏi.
- **BR-01.4 Gợi ý Gán nhãn AI Thông minh (AI Auto-tagging):** AI phân tích ngữ nghĩa thân câu hỏi và đề xuất: Mạch nội dung, Chủ đề, Dạng câu hỏi, Mức độ tư duy và **Mã Yêu cầu cần đạt (YCCĐ)** tương ứng theo danh mục Thông tư 32.
- **BR-01.5 Studio Hậu kiểm Song song (Human-in-the-Loop Studio):** Cột trái xem tài liệu gốc (PDF/Word) có **Synchronized Scrolling** (cuộn đồng bộ); Cột phải hiển thị danh sách câu hỏi bóc tách render KaTeX realtime. Cảnh báo độ tin cậy theo màu: Xanh (>= 95%), Vàng (80 - 94%), Đỏ (< 80%). Sửa nhanh công thức và đổi đáp án chỉ bằng 1 click.

---

### BR-02: NGÂN HÀNG CÂU HỎI CHUẨN HÓA THEO YÊU CẦU CẦN ĐẠT (YCCĐ - TT 32)

- **BR-02.1 Chuẩn hóa Cây Phân cấp Kiến thức & Năng lực (Taxonomy):**
  - Tuyệt đối **không phân chia theo bộ sách giáo khoa**, bám sát 100% khung CT GDPT 2018 theo Thông tư 32/2018/TT-BGDĐT.
  - Cấu trúc phân cấp 6 tầng:
    $$\text{Cấp học / Khối lớp} \longrightarrow \text{Môn học} \longrightarrow \text{Mạch nội dung (Strand)} \longrightarrow \text{Chủ đề / Chuyên đề} \longrightarrow \text{Bài học} \longrightarrow \mathbf{Yêu\ cầu\ cần\ đạt\ (YCCĐ)}$$
  - **Tầng Dạng câu hỏi (Dạng bài tập chuyên đề):** Mỗi bài học/YCCĐ được chia chi tiết thành các Dạng bài tập cụ thể để chống lệch dạng khi sinh đề thi.
  - **Ví dụ phân tầng Môn Toán 12 theo TT 32:**
    - *Cấp học:* THPT -> *Khối:* Lớp 12 -> *Môn:* Toán học.
    - *Mạch nội dung:* Số, Đại số và Một số yếu tố giải tích.
    - *Chủ đề:* Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số.
    - *Bài học:* Tính đơn điệu và cực trị của hàm số.
    - *Yêu cầu cần đạt (YCCĐ):* `TOAN12.GT.01` - *"Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị hàm số."*
    - *Dạng câu hỏi (Dạng bài tập):* `Dạng 1:` Tìm cực trị hàm đa thức bậc 3 chứa tham số $m$; `Dạng 2:` Cực trị hàm hợp $f(u(x))$; `Dạng 3:` Bài toán thực tế ứng dụng cực trị.

- **BR-02.2 Phân loại theo 3 Mức độ Tư duy / Nhận thức (Theo Bảng động từ TT 32):**
  Bám sát bảng tổng hợp động từ mô tả mức độ YCCĐ tại Chương trình môn học (Thông tư 32):
  1. **Biết (Nhận biết):** Nhận biết và nhớ lại thông tin đã tiếp nhận trước đó (Động từ: *Đọc, đếm, viết, làm quen, nhận dạng, nhận biết...*).
  2. **Hiểu (Thông hiểu):** Hiểu được ý nghĩa thông tin, diễn đạt theo ý hiểu cá nhân (Động từ: *Mô tả, giải thích, thể hiện, sắp xếp...*).
  3. **Vận dụng:** Vận dụng thông tin đã biết vào tình huống mới hoặc giải quyết vấn đề (Động từ: *Tính, vẽ, thực hiện, sử dụng, vận dụng, so sánh, phân biệt, lí giải, chứng minh, giải quyết vấn đề thực tiễn...* - bao gồm Vận dụng và Vận dụng cao).

- **BR-02.3 Phân loại theo Năng lực Đặc thù Môn học:**
  - Hỗ trợ gán nhãn thành phần năng lực chuyên biệt theo TT 32:
    - *Môn Toán:* Năng lực tư duy và lập luận toán học; Năng lực mô hình hoá toán học; Năng lực giải quyết vấn đề toán học; Năng lực giao tiếp toán học; Năng lực sử dụng công cụ, phương tiện học toán.
    - *Môn KHTN / Vật lí / Hóa học / Sinh học:* Nhận thức khoa học; Tìm hiểu thế giới tự nhiên; Vận dụng kiến thức, kĩ năng đã học.
    - *Môn Tiếng Anh / Ngoại ngữ:* Năng lực giao tiếp (Nghe, Nói, Đọc, Viết) theo Khung năng lực ngoại ngữ 6 bậc dùng cho Việt Nam.

- **BR-02.4 Đa dạng Thể thức Câu hỏi (Bám sát Quyết định 764/QĐ-BGDĐT):**
  1. `SINGLE_CHOICE`: Trắc nghiệm 4 lựa chọn (A, B, C, D) truyền thống.
  2. `TRUE_FALSE_GROUP`: Trắc nghiệm Đúng/Sai 4 khẳng định độc lập (mỗi câu gồm ý a, b, c, d).
  3. `SHORT_ANSWER`: Trắc nghiệm trả lời ngắn (điền số hoặc từ ngữ, hỗ trợ sai số tính toán $\pm \epsilon$).
  4. `PASSAGE_GROUP`: Câu hỏi chùm (Một đoạn văn bản/ngữ liệu bài đọc chung và các câu hỏi con đi kèm).
  5. `ESSAY`: Câu hỏi tự luận kèm rubric barem chấm điểm theo tiêu chí.

- **BR-02.5 Vòng đời & Kiểm soát Trùng lặp bằng AI Vector:**
  - Vòng đời: `DRAFT` -> `PENDING_REVIEW` -> `APPROVED` -> `ARCHIVED`. Lưu trữ lịch sử phiên bản (Audit Diff View).
  - Sử dụng AI Vector Search (Cosine Similarity): Cảnh báo vàng khi trùng >= 80%, **chặn lưu và cảnh báo đỏ khi trùng >= 90%** so với các câu hỏi cùng môn/lớp.

---

### BR-03: MA TRẬN ĐỀ THI & BẢN ĐẶC TẢ KHẢO THÍ CHUẨN HOÁ
- **BR-03.1 Ma trận Đề thi Đánh giá Định kỳ (Theo Thông tư 22/2021/TT-BGDĐT):**
  - Ma trận 2 chiều cho đề kiểm tra giữa kỳ, cuối kỳ:
    - Trục dọc: Danh sách Chủ đề / Mạch nội dung / Bài học / Dạng bài.
    - Trục ngang: 3 Cấp độ nhận thức (Biết - Hiểu - Vận dụng) $\times$ Dạng thức câu hỏi (Trắc nghiệm nhiều lựa chọn, Đúng/Sai, Trả lời ngắn, Tự luận).
  - Tự động kiểm tra tỷ lệ phân bố điểm số (chuẩn: 70% Trắc nghiệm khách quan - 30% Tự luận; hoặc 40% Biết - 30% Hiểu - 30% Vận dụng).
- **BR-03.2 Bản Đặc tả Đề thi Chi tiết (Test Blueprint):**
  - Gắn từng câu hỏi trong ma trận với chính xác **Mã Yêu cầu cần đạt (YCCĐ)** của Thông tư 32.
  - Đảm bảo tính pháp lý: Mọi câu hỏi xuất hiện trong đề thi đều có thể truy xuất nguồn gốc về chuẩn YCCĐ tương ứng của chương trình giáo dục phổ thông.

---

### BR-04: ĐỘNG CƠ SINH ĐỀ & HOÁN VỊ MÃ ĐỀ AN TOÀN
- **BR-04.1 Rút Đề Gốc theo Ràng buộc (Constraint Satisfaction Solver):**
  - Rút ngẫu nhiên các câu hỏi đạt trạng thái `APPROVED` thỏa mãn chính xác ma trận và bản đặc tả.
  - Áp dụng danh sách loại trừ (Exclusion list): Không chọn câu hỏi đã xuất hiện trong bài kiểm tra của khối/lớp trong vòng 30 - 60 ngày qua.
- **BR-04.2 Trộn Mã Đề An toàn Tuyệt đối (Safe Shuffling Engine):**
  - Sinh $N$ mã đề hoán vị (101, 102, 103, 104...) từ đề gốc.
  - **Bảo toàn phân vùng:** Chỉ đảo câu hỏi trong cùng một Phần/Dạng thức (Phần I trắc nghiệm đơn, Phần II đúng sai, Phần III trả lời ngắn).
  - **Bảo toàn câu hỏi chùm:** Ngữ liệu bài đọc chung và các câu hỏi con luôn đi liền kề nhau, không bị xé lẻ.
  - **Neo cố định phương án (Option Anchor Rule):** Phương án chứa "Cả A và B", "Tất cả các ý trên", "Không có đáp án nào" hoặc cờ `is_fixed = true` bắt buộc **khóa cố định ở vị trí cuối cùng (D)**.
  - Tự động sinh Ma trận Ánh xạ Đáp án đối chiếu giữa đề gốc và các mã đề hoán vị.

---

### BR-05: XUẤT BẢN ẤN PHẨM KHẢO THÍ & ĐÁNH GIÁ NĂNG LỰC
- **BR-05.1 Xuất bản Microsoft Word (.docx) Chuẩn Mẫu in:**
  - Header chuẩn Bộ GD&ĐT: Tên trường/sở, kỳ thi, môn thi, mã đề, khung số báo danh và bảng phách.
  - Bố cục 2 cột (Two-column layout) tiết kiệm giấy in.
  - Công thức toán học/hóa học chuyển sang định dạng **Microsoft Word OMML (Office Math Markup Language) native**, chữ vector sắc nét, chỉnh sửa được trực tiếp trên Word.
  - Gói xuất bản ZIP: $N$ file đề thi Word, file Lời giải chi tiết, file Bảng đáp án tổng hợp, file Phiếu trả lời trắc nghiệm (chuẩn máy chấm OMR).
- **BR-05.2 Thống kê Khảo thí & Đánh giá Năng lực Hậu kiểm:**
  - Tự động tính toán Độ khó thực nghiệm ($p$-value) và Độ phân biệt ($D$-index) khi nhập điểm học sinh. Cảnh báo câu hỏi lỗi ($D < 0.2$).

---

### BR-06: BẢO MẬT CƠ MẬT ĐỀ THI & AUDIT TRAIL
- Mã hóa toàn bộ câu hỏi và đề thi ở trạng thái "Chưa công bố" bằng **AES-256**.
- Xác thực 2 bước (2FA) khi cán bộ in sao tải file đề thi chính thức.
- Phân quyền RBAC nghiêm ngặt và ghi nhật ký bất biến (Audit Log) mọi thao tác.

---

## 4. BẢNG TỔNG HỢP QUY TẮC NGHIỆP VỤ CỐT LÕI (CORE BUSINESS RULES)

| Mã Quy tắc | Tên Quy tắc | Nội dung Chi tiết theo Thông tư 32 & Quyết định 764 |
|:---|:---|:---|
| **RULE-01** | Tính điểm Đúng/Sai 4 ý (Bậc thang 2025) | Mỗi câu hỏi có 4 khẳng định a, b, c, d. Điểm tính theo bậc thang: Đúng 1 ý: $0.1$ điểm (10%); Đúng 2 ý: $0.25$ điểm (25%); Đúng 3 ý: $0.5$ điểm (50%); Đúng cả 4 ý: $1.0$ điểm (100%). |
| **RULE-02** | Neo Cố định Phương án (Option Anchor) | Phương án có chứa từ ngữ phụ thuộc vị trí ("Cả A và B", "Tất cả các đáp án trên") hoặc cờ `is_fixed = true` phải được khóa cố định ở vị trí cuối cùng (D) khi hoán vị mã đề. |
| **RULE-03** | Bảo toàn Toàn vẹn Câu hỏi Chùm | Toàn bộ câu hỏi con trong cùng một nhóm ngữ liệu chung phải luôn nằm liền kề nhau và ngay sau văn bản ngữ liệu bài đọc. Không được phân tán câu con sang các trang khác. |
| **RULE-04** | Chuẩn hóa theo YCCĐ (Không theo SGK) | Mọi câu hỏi khi duyệt vào ngân hàng chính thức bắt buộc phải gắn với tối thiểu 01 mã Yêu cầu cần đạt (YCCĐ) theo Thông tư 32/2018/TT-BGDĐT. Tuyệt đối không lưu trường dữ liệu bộ SGK. |
| **RULE-05** | Ngưỡng Cảnh báo Trùng lặp AI Vector | Nếu độ tương đồng cosine >= 0.90 giữa câu hỏi mới và câu hỏi hiện có trong DB, hệ thống bắt buộc kích hoạt modal cảnh báo màu đỏ và chặn lưu tự động cho đến khi người dùng xác nhận. |
| **RULE-06** | Cơ cấu Ma trận Đề thi Đánh giá Định kỳ | Tỷ lệ điểm các câu hỏi trong đề kiểm tra định kỳ phải nằm trong biên độ cấu hình ma trận quy định (ví dụ: Tỷ lệ Biết - Hiểu - Vận dụng là $40\% - 30\% - 30\%$, dung sai $\pm 5\%$). |

---

## 5. MA TRẬN TRUY XUẤT NGUỒN GỐC (TRACEABILITY MATRIX)

| Mã BRD | Tên Nghiệp vụ | Phân hệ Đáp ứng | Ưu tiên | Căn cứ Quy chuẩn |
|:---|:---|:---|:---:|:---|
| **BR-01** | AI Số hoá Đề thi & Studio HITL | AI Parsing Engine & HITL | P0 | Tự động hóa khảo thí |
| **BR-02.1** | Cây Phân loại theo YCCĐ & Dạng bài | Taxonomy Management | P0 | **Thông tư 32/2018/TT-BGDĐT** |
| **BR-02.2** | 3 Cấp độ tư duy (Biết, Hiểu, Vận dụng) | Item Cognitive Classification | P0 | **Bảng động từ mức độ TT 32** |
| **BR-02.4** | Thể thức câu hỏi Trắc nghiệm 2025 | Item Bank Format Engine | P0 | **Quyết định 764/QĐ-BGDĐT** |
| **BR-03** | Ma trận Đề thi & Bản đặc tả YCCĐ | Matrix Blueprint Builder | P0 | **Thông tư 22/2021/TT-BGDĐT** |
| **BR-04** | Trộn Đề & Hoán vị An toàn | Safe Shuffling Engine | P0 | Tiêu chuẩn khảo thí an toàn |
| **BR-05** | Xuất bản Word OMML 2 Cột & In ấn | Export Service | P0 | Quy chuẩn in ấn Bộ GD&ĐT |
| **BR-06** | Cơ mật Đề thi & Audit Trail | Security & Governance | P1 | Bảo mật đề thi quốc gia |
