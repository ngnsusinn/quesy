# HƯỚNG DẪN SOẠN THẢO ĐỀ THI VỚI GÓI EX_TEST (PHIÊN BẢN 3.3)
**Hệ thống Quản lý Khảo thí & Soạn đề Quesy - Chuẩn TT 32/2018 & QĐ 764/2025**

---

## 1. TỔNG QUAN VỀ GÓI LỆNH EX_TEST

Gói lệnh `ex_test.sty` (phiên bản v3.3.6, tác giả: Thầy Trần Anh Tuấn, phát triển: Thầy Dương Phước Sang) là bộ công cụ chuyên dụng hàng đầu tại Việt Nam dùng để soạn thảo đề thi môn Toán và các môn khoa học tự nhiên. Gói hỗ trợ toàn diện các dạng thức trắc nghiệm mới nhất theo cấu trúc đề thi tốt nghiệp THPT từ năm 2025 của Bộ Giáo dục & Đào tạo.

### 1.1. Khai báo gói và các chế độ xuất bản (Package Options)
Đặt lệnh khai báo ở phần preamble của tài liệu LaTeX:
```latex
\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}          % Tối ưu cho engine XeTeX / Tectonic Unicode
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}      % Vẽ hình học vector & bảng biến thiên
\usepackage[dethi]{ex_test}    % Nạp gói ex_test với tùy chọn xuất bản
```

Các tùy chọn chính của `\usepackage[<tùy_chọn>]{ex_test}`:
- **`[dethi]`**: **Chế độ in đề thi** (mặc định). Ẩn toàn bộ lời giải và không đánh dấu đáp án đúng, dùng để in phát cho học sinh làm bài.
- **`[color]`**: **Chế độ đề có đáp án màu**. Ẩn lời giải, khoanh tròn/tô màu đỏ nổi bật các phương án đúng `\True`, phục vụ giáo viên coi thi và chấm nhanh.
- **`[loigiai]`**: **Chế độ lời giải chi tiết**. Hiển thị đầy đủ nội dung bên trong môi trường `\begin{loigiai}...\end{loigiai}`.
- **`[solcolor]`**: **Chế độ lời giải có màu**. Vừa hiển thị lời giải chi tiết, vừa tô màu đỏ đáp án đúng `\True`.
- **`[book]`**: **Chế độ viết sách/chuyên đề**. Tự động tách phần đề bài và phần lời giải chi tiết ra các file riêng biệt để in ở cuối sách.

### 1.2. Cơ chế Soạn Thảo Tinh Gọn Không Preamble trên Quesy (/composer)
- **Đặc quyền trên Quesy Composer:** Toàn bộ Preamble chuẩn (`\documentclass`, `fontspec`, `amsmath,amssymb`, `tikz,tkz-tab`, `tcolorbox`, `xparse`, `ex_test.sty` v3.3, khổ A4 lề 18mm) đã được động cơ Quesy tự động nhúng ngầm (Canonical Preamble Injection).
- **Chỉ cần viết nội dung câu hỏi:** Giáo viên chỉ cần viết các câu hỏi `\begin{ex}...\end{ex}` và tiêu đề, không cần gõ `\documentclass` hay `\begin{document}...\end{document}`.
- **Tự động chuyển chế độ Đề thi / Lời giải:** Sử dụng công tắc `LỜI GIẢI` trên giao diện, hệ thống tự động truyền cờ `[loigiai]` hoặc `[dethi]` vào engine biên dịch mà không cần chỉnh sửa mã nguồn.
- **Tương thích ngược:** Nếu dán cả văn bản hoàn chỉnh có sẵn `\documentclass`, hệ thống vẫn nhận diện và biên dịch bình thường.

### 1.3. Tiêu Đề Đề Thi 2 Cột Căn Giữa Chuẩn Quốc Gia 2025 (Header Minipage 0.38 / 0.58)
Theo mẫu khảo thí mới nhất của Bộ Giáo dục & Đào tạo:
- **Header 2 cột cân đối bằng `minipage`:**
  * Cột trái (`0.38\textwidth`): Căn giữa `\centering`, ghi Đơn vị quản lý / Tên trường THPT và trạng thái đề ("ĐỀ CHÍNH THỨC").
  * Cột phải (`0.58\textwidth`): Căn giữa `\centering`, ghi Tên kỳ thi, môn thi, khối lớp, năm học và thời gian làm bài.
  * Phân cách giữa 2 cột bằng khoảng trống co giãn `\hfill`.
- **Dòng thông tin thí sinh & khung mã đề:**
  * Định dạng: `Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: ...}}`
- **Đường nét liền phân cách duy nhất:**
  * Chỉ sử dụng **DUY NHẤT một đường nét liền đơn** `\noindent\rule{\textwidth}{0.5pt}` nằm ngay phía dưới dòng thông tin thí sinh (tuyệt đối KHÔNG có đường kẻ liền bên trên).
- **Định dạng phân đoạn đề thi (Sections) & Reset Số Thứ Tự Câu Hỏi:**
  * Sử dụng chuẩn in đậm và in nghiêng:
    ```latex
    \noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}
    ```
  * **QUY TẮC RESET THỨ TỰ CÂU HỎI VỀ 1 (\setcounter{ex}{0}):**
    Theo chuẩn đề thi Quốc gia (QĐ 764), Phần II (Đúng/Sai) và Phần III (Trả lời ngắn) bắt buộc phải đếm lại từ **Câu 1** (không được đếm nối tiếp thành Câu 13 hay Câu 17). Trong gói `ex_test.sty`, môi trường `ex` sử dụng bộ đếm LaTeX `ex`. Do đó, ngay sau tiêu đề của PHẦN II, PHẦN III (và PHẦN IV nếu có), BẮT BUỘC chèn lệnh:
    ```latex
    \setcounter{ex}{0}
    ```
    (Lệnh này reset bộ đếm về 0, để câu `\begin{ex}` kế tiếp sẽ bắt đầu chính xác là "Câu 1.").
  * **NGHIÊM CẤM THẺ \large & \section\*:**
    Tuyệt đối **KHÔNG sử dụng thẻ `\large`, `\Large`, `\LARGE`** trong tiêu đề phần (thẻ `\large` đẩy cỡ chữ lên 14pt, làm vỡ giãn cách dọc và sai chuẩn khảo thí). Tiêu đề phần chỉ sử dụng cỡ chữ 12pt thông thường: `\noindent\textbf{PHẦN ...}` `\textit{...}`. Đồng thời tuyệt đối không dùng `\section*{...}` (gây thụt lề lớn và khoảng trắng thừa).

---

## 2. CẤU TRÚC SOẠN THẢO CÁC DẠNG CÂU HỎI THEO ĐỊNH DẠNG 2025

### 2.1. Phần I: Câu trắc nghiệm nhiều phương án lựa chọn (Chọn 1 trong 4)
Sử dụng môi trường `\begin{ex} ... \end{ex}` và lệnh `\choice`:

```latex
\begin{ex}[Đề Khảo sát 2026]
Cho hàm số bậc ba $y = f(x)$ có bảng biến thiên như sau:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\choice
{\True $(-\infty; -2)$}
{$(-2; 1)$}
{$(-1; 2)$}
{$(0; 1)$}
\begin{loigiai}
Dựa vào bảng biến thiên, ta thấy $f'(x) > 0$ trên các khoảng $(-\infty; -2)$ và $(1; +\infty)$.
Do đó, hàm số đồng biến trên khoảng $(-\infty; -2)$.
\end{loigiai}
\end{ex}
```

**Các tùy chọn chia cột của `\choice`:**
- `\choice{A}{B}{C}{D}`: Tự động tính toán độ dài 4 phương án để chia 4 cột, 2 cột hoặc 1 cột tối ưu diện tích trang giấy.
- `\choice[1]{A}{B}{C}{D}`: Ép 4 phương án xếp theo **1 cột** (dọc).
- `\choice[2]{A}{B}{C}{D}`: Ép 4 phương án xếp theo **2 cột** (mỗi dòng 2 phương án).
- `\choice[4]{A}{B}{C}{D}`: Ép 4 phương án dàn đều trên **1 hàng ngang** (4 cột).
- `\True`: Đặt trước nội dung của phương án đúng (hệ thống sẽ tự động ghi nhận đáp án vào cơ sở dữ liệu).

---

### 2.2. Phần II: Câu trắc nghiệm Đúng / Sai (4 khẳng định bậc thang QĐ 764)
Sử dụng lệnh `\choiceTF[1]` cho câu hỏi có 4 ý lựa chọn (tham số `[1]` ép buộc hiển thị **1 cột dọc duy nhất**, mỗi khẳng định a, b, c, d nằm trên một dòng riêng biệt, tuyệt đối không chia 4 cột hay 2 cột).

**Lưu ý bắt buộc:** Ngay sau dòng tiêu đề Phần II, phải có lệnh `\setcounter{ex}{0}` để câu hỏi bắt đầu lại từ Câu 1:

```latex
\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}
\setcounter{ex}{0}

\begin{ex}[Chuyên đề Đạo hàm]
Cho hàm số $y = f(x) = x^3 - 3x^2 + 2$. Xét tính đúng/sai của các khẳng định sau:
\choiceTF[1]
{\True Hàm số đạt cực đại tại điểm $x = 0$.}
{Giá trị cực tiểu của hàm số bằng $2$.}
{\True Điểm uốn của đồ thị hàm số là $I(1; 0)$.}
{Hàm số đồng biến trên toàn bộ tập xác định $\mathbb{R}$.}
\begin{loigiai}
Ta có $y' = 3x^2 - 6x = 3x(x - 2)$. Cho $y' = 0 \Leftrightarrow x = 0$ hoặc $x = 2$.
\begin{itemchoice}
\itemch Đúng. Vì qua $x = 0$, $y'$ đổi dấu từ dương sang âm nên hàm số đạt cực đại tại $x = 0$.
\itemch Sai. Giá trị cực tiểu là $y(2) = 2^3 - 3(2)^2 + 2 = -2 \neq 2$.
\itemch Đúng. $y'' = 6x - 6 = 0 \Leftrightarrow x = 1 \Rightarrow y(1) = 0$.
\itemch Sai. Hàm số nghịch biến trên khoảng $(0; 2)$.
\end{itemchoice}
\end{loigiai}
\end{ex}
```

- **Quy tắc Chuẩn mực Khảo thí 2025:**
- **Tham số `[1]` là BẮT BUỘC:** Lệnh `\choiceTF[1]` bảo đảm 4 ý a), b), c), d) luôn dàn trải theo 1 cột thẳng đứng (single-column, 100% độ rộng dòng), không tự động co cụm thành 2 cột hay 4 cột ngang gây xô lệch bố cục in ấn.
- **BẮT BUỘC BỌC MỖI KHẲNG ĐỊNH TRONG CẶP NGOẶC NHỌN `{...}`:** Mỗi khẳng định con trong `\choiceTF[1]` BẮT BUỘC phải nằm trong cặp ngoặc nhọn `{...}`, ví dụ: `{\True Khẳng định 1}` hoặc `{Khẳng định 2}`. Nếu thiếu `{...}` (ví dụ viết trần `\True Khẳng định 1`), macro `\choiceTF` của TeX sẽ nuốt token đầu tiên làm tham số đối số; khi khẳng định bắt đầu bằng công thức toán `$x = ...$`, token `$` đầu tiên bị nuốt lẻ loi, làm đảo lộn ngữ pháp TeX và trực tiếp gây lỗi nghiêm trọng: `! Missing $ inserted. error: the XeTeX engine had an unrecoverable error`.
- **BẮT BUỘC KHÔNG gõ tiền tố nhãn `a)`, `b)`, `c)`, `d)`:** Trong từng ý khẳng định `{...}`, tuyệt đối không gõ nhầm các tiền tố `a) ...`, `b) ...`, `c) ...`, `d) ...` vì lệnh `\choiceTF` đã tự động sinh các nhãn in đậm tương ứng. Nếu gõ vào sẽ dẫn đến lỗi lặp nhãn kép `a) a)`, `b) b)` trong văn bản PDF xuất bản.
- **Tuyệt đối KHÔNG thêm `\\\\`:** Sau mỗi khối ngoặc nhọn `{...}`, không được đặt thêm dấu xuống dòng `\\\\` (sẽ gây lỗi nghiêm trọng `! LaTeX Error: There's no line here to end`).
- **QUY TẮC AN TOÀN KÝ TỰ GẠCH DƯỚI `_` VÀ KÝ TỰ ĐẶC BIỆT NGOÀI MATH MODE:** Trong XeTeX/Tectonic, ký tự `_` mang mã phân loại (catcode 8) chỉ được phép sử dụng trong chế độ toán học (math mode `$x_1$`). Mọi ký tự `_` xuất hiện trong văn bản thuần túy (như mã định danh `PERSIST_13951386`, `Ma_de_101`, `cau_hoi_1`) BẮT BUỘC phải được escape thành `\_`. Nếu để trần ngoài toán học, TeX sẽ coi đây là lệnh chỉ số dưới và tự chèn `$` dẫn tới văng lỗi `Missing $ inserted`. Hệ thống Quesy tích hợp bộ lọc tự động `sanitize_latex_for_xetex` để tự động hóa quy tắc này.
- Ý nào đúng: Đặt `\True` ở đầu nội dung khẳng định (`{\True Nội dung ý đúng}`).
- Ý nào sai: Để nội dung khẳng định bình thường không có `\True` (`{Nội dung ý sai}`).
- Môi trường `\begin{itemchoice} \itemch ... \end{itemchoice}` trong `\begin{loigiai}` giúp trình bày lời giải phân tách rành mạch cho từng ý a), b), c), d).

---

### 2.3. Phần III: Câu trắc nghiệm Trả lời ngắn
Sử dụng lệnh `\shortans{<kết_quả>}`.

**Lưu ý bắt buộc:** Ngay sau dòng tiêu đề Phần III, phải có lệnh `\setcounter{ex}{0}` để câu hỏi bắt đầu lại từ Câu 1:

```latex
\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}
\setcounter{ex}{0}

\begin{ex}[Tích phân ứng dụng]
Một vật thể chuyển động với vận tốc $v(t) = 3t^2 + 2t$ (m/s). Tính quãng đường vật đi được từ thời điểm $t = 0$ (s) đến thời điểm $t = 2$ (s).
\shortans{12}
\begin{loigiai}
Quãng đường vật đi được là:
$s = \displaystyle\int_{0}^{2} (3t^2 + 2t)\,\mathrm{d}t = \left. (t^3 + t^2) \right|_0^2 = 8 + 4 = 12\text{ (m)}$.
\end{loigiai}
\end{ex}
```

**Các tùy chọn của `\shortans`:**
- `\shortans{12}`: Hiển thị ô vuông điền kết quả dài 4 cm ở góc phải.
- `\shortans[0]{12}`: **Định dạng chuẩn Đề thi 2025** (không hiển thị khung điền, câu hỏi kết thúc tự nhiên).
- `\shortans[oly]{12}`: Hiển thị 4 ô ly để học sinh tập tô số phiếu trắc nghiệm.
- `\shortans[3]{12}`: Hiển thị khung điền có chiều rộng tùy chỉnh (3 cm).

---

### 2.4. Câu hỏi Ghép đôi (Matching) & Kéo thả (Drag & Drop)

#### Ghép đôi (`\match` và `\with`):
```latex
\begin{ex}
Ghép mỗi hàm số ở Cột I với tập xác định tương ứng ở Cột II:
\match
{$y = \dfrac{1}{x}$}
{$y = \sqrt{x}$}
{$y = \ln x$}
\with
[1]{$\mathbb{R} \setminus \{0\}$}
[2]{$[0; +\infty)$}
[3]{$(0; +\infty)$}
{$\mathbb{R}$}
\end{ex}
```

---

## 3. QUY TẮC CĂN GIỮA TOÀN BỘ ĐỒ THỊ, HÌNH HỌC VÀ BẢNG BIẾN THIÊN (CENTERED DIAGRAMS INVARIANT)

Theo quy chuẩn khảo thí Quốc gia và thiết kế xuất bản đề thi hiện đại:
- **MẶC ĐỊNH 100% CĂN GIỮA (CENTERED):** Toàn bộ đồ thị hàm số TikZ, hình học không gian TikZ, bảng biến thiên `tkz-tab` và bảng biểu thống kê BẮT BUỘC PHẢI ĐƯỢC ĐẶT NẰM Ở CHÍNH GIỮA trang giấy, TUYỆT ĐỐI KHÔNG NẰM LỆCH 1 BÊN.
- **Môi trường căn giữa bắt buộc:** Đặt mã hình vẽ hoặc bảng biến thiên trong môi trường `\begin{center} ... \end{center}`:
  ```latex
  \begin{center}
  \begin{tikzpicture}[...]
    ...
  \end{tikzpicture}
  \end{center}
  ```
- **Vị trí bố trí chuẩn mực:** Nằm ngay bên dưới phần dẫn đề bài (stem) và ở phía trên các phương án lựa chọn (`\choice`, `\choiceTF[1]` hoặc `\shortans`).
- **LOẠI BỎ HOÀN TOÀN KHUYẾN NGHỊ `\immini` KHỎI MẶC ĐỊNH:** Tuyệt đối không tự động bọc đồ thị vào lệnh `\immini` hay `\imminiL`. Việc dùng `\immini` ép chữ và phương án vào một cột hẹp bên trái làm co kéo vỡ dòng, cắt xén nhãn tọa độ, và đặc biệt gây lỗi TeX nghiêm trọng khi lồng `\choice` vào trong tham số của `\immini`. Lệnh `\immini` chỉ được xem là tùy chọn legacy tương thích ngược.
- **Mật độ điểm lấy mẫu (Sampling Density):** Khi vẽ đồ thị hàm số TikZ (`plot(\x, ...)`), luôn đặt `samples=50` hoặc `samples=60` thay vì `samples=100+`. Ở độ phân giải vector 1200 DPI, 50 điểm lấy mẫu cho đường cong Bézier trơn mượt hoàn hảo và giảm tải 50% thời gian mở rộng macro của TeX.

**Ví dụ câu hỏi có đồ thị chuẩn căn giữa:**
```latex
\begin{ex}
Cho hàm số bậc ba $y = f(x)$ có đồ thị như hình vẽ bên dưới. Hàm số đã cho nghịch biến trên khoảng nào dưới đây?
\begin{center}
\begin{tikzpicture}[scale=0.6, >=stealth, font=\footnotesize]
  \draw[->] (-3,0) -- (4,0) node[above] {$x$};
  \draw[->] (0,-4) -- (0,5) node[right] {$y$};
  \fill (0,0) circle (1.2pt) node[below left] {$O$};
  \draw[dashed] (-1,0) node[below] {$-1$} -- (-1,4) -- (0,4) node[left] {$4$};
  \draw[dashed] (2,0) node[above] {$2$} -- (2,-2) -- (0,-2) node[left] {$-2$};
  \draw[thick, smooth, samples=50, domain=-2.3:3.1] plot(\x, {(\x+3)*(\x-1)*(\x-3)/3});
\end{tikzpicture}
\end{center}
\choice
{$(-\infty; -1)$}
{\True $(-1; 2)$}
{$(2; +\infty)$}
{$(-\infty; 2)$}
\begin{loigiai}
Dựa vào đồ thị, hàm số đạt cực đại tại $x = -1$ và đạt cực tiểu tại $x = 2$. Do đó hàm số nghịch biến trên khoảng $(-1; 2)$.
\end{loigiai}
\end{ex}
```

---

## 4. BẢNG ĐÁP ÁN TỰ ĐỘNG (ANSWER KEYS)

Để tự động xuất bảng đáp án ở cuối đề thi:
```latex
\Opensolutionfile{ans}[ans.tex]
% ... Toàn bộ các câu hỏi \begin{ex} đặt tại đây ...
\Closesolutionfile{ans}

\newpage
\section*{BẢNG ĐÁP ÁN}
\inputansbox{ans.tex}       % Xuất bảng đáp án dạng ô đóng khung
```

---

## 5. TÍCH HỢP TỰ ĐỘNG VỚI QUESY & TECTONIC DOCKER

1. **XeTeX Unicode 100%:** Gói `ex_test.sty` được Quesy cấu hình chạy trên nền Tectonic XeTeX với font `CMU Serif` / `Latin Modern Roman`, tự động nhận diện tiếng Việt có dấu mà không cần gói legacy `\usepackage[utf8]{vietnam}`.
2. **Trích xuất 1-Click vào Ngân hàng:** Trình soạn thảo Quesy tự động nhận diện cấu trúc `\begin{ex} ... \choice`, `\choiceTF`, `\shortans` để bóc tách trực tiếp vào cơ sở dữ liệu ngân hàng câu hỏi.
3. **Chống sập ảnh thiếu:** Nếu đề bài có `\includegraphics` nhưng chưa nạp file ảnh, Tectonic Microservice tự động bù đắp placeholder trong suốt, bảo đảm đề thi luôn biên dịch thành công.

---

## 6. HỆ THỐNG TRỢ LÝ AI COPILOT CHẨN ĐOÁN & SỬA LỖI BIÊN DỊCH TỰ ĐỘNG

Khi biên dịch đề thi phát sinh lỗi, hệ thống kích hoạt chu trình khép kín:
1. **Lưu trữ Log Lỗi:** Backend trả về thông báo lỗi compiler chi tiết (`compile_error`). Client lưu trữ tại `this.lastCompileError`.
2. **Truyền Log vào AI Copilot:** Khi người dùng gửi prompt yêu cầu "sửa lỗi", "fix lỗi", "tại sao lỗi" hoặc click nút SỬA LỖI trên Gemini Dropdown, log lỗi được tự động đính kèm vào payload `POST /api/v1/composer/chat`.
3. **Ánh xạ Dòng Lỗi (Preamble Line Offset):** Vì trình soạn thảo hoạt động ở chế độ Preamble-free (không chứa 11 dòng preamble chuẩn), động cơ chẩn đoán tự động tính `Dòng_Editor = Dòng_Compiler - 11` để định vị chính xác vị trí dòng lỗi trên màn hình người dùng.
4. **Các lỗi thường gặp và cách xử lý:**
   - **`There's no line here to end`:** Do thừa dấu `\\` sau các khối ngoặc nhọn `{...}` của `\choice` hoặc `\choiceTF`. Cách sửa: xóa bỏ dấu `\\`.
   - **`Undefined control sequence`:** Lệnh không tồn tại (như gõ nhầm `\ule` thay vì `\rule`, `\choiceTFt` thay vì `\choiceTF[1]`, `ight|` thay vì `\right|`, hoặc chuỗi `\n` bị chèn nhầm). Cách sửa: thay thế bằng lệnh chuẩn.
   - **`Missing $ inserted`:** Thiếu dấu `$` bọc quanh ký hiệu toán học (`_`, `^`, `\alpha`, `\int`). Cách sửa: bọc công thức trong cặp `$ ... $`.
   - **`Missing \right. inserted`:** Mất cân bằng giữa `\left.` và `\right.`. Cách sửa: hoàn thiện cặp ngoặc co giãn.
5. **Sinh Diff Thông Minh:** AI trả về khối ```diff``` chỉ chứa dòng cũ và dòng mới, cho phép giáo viên bấm **[Đồng ý]** để sửa trực tiếp trên trình soạn thảo.

---

## 7. QUY TRÌNH BIÊN DỊCH NHANH & TỐI ƯU HÓA THỜI GIAN SOẠN THẢO (FAST COMPILATION WORKFLOW)

Khi soạn thảo đề thi quy mô lớn (22 câu, nhiều hình TikZ), việc biên dịch lại toàn bộ tài liệu qua XeTeX có thể mất 40s - 65s. Quesy hỗ trợ quy trình biên dịch thông minh 3 tầng:

1. **Xem trước Tức thì (Instant Live Preview - 0.2s):**
   - Nhấp chọn chế độ *"Xem trước Tức thì (HTML)"* trên thanh điều khiển xem trước.
   - MathJax hiển thị công thức toán tức thì; các hình TikZ không thay đổi được nạp trực tiếp từ Disk Cache MD5 trong 10ms.
   - Trải nghiệm gõ phím và xem trước không độ trễ.

2. **Biên dịch Nhanh Câu Đang Sửa (Focus / Partial Question Quick Compile - 1.5s):**
   - Đặt con trỏ chuột bên trong câu hỏi cần xem trước, hoặc bôi đen khối `\begin{ex}...\end{ex}`.
   - Nhấn nút **`⚡ BIÊN DỊCH CÂU NÀY`** hoặc tổ hợp phím **`Ctrl+Shift+S`** (`Cmd+Shift+S`).
   - Hệ thống tự động bọc riêng câu hỏi đó vào preamble chuẩn và biên dịch PDF trong vòng 1-2 giây.

3. **Chế độ Nháp (Draft Mode - Giảm 70% thời gian biên dịch toàn đề):**
   - Bật cờ *"Chế độ Nháp (Draft Mode)"* khi kiểm tra bố cục tổng thể.
   - Hệ thống tự động hạ `samples=35` cho toàn bộ các đường cong TikZ, giúp biên dịch trọn bộ 22 câu trong 12 - 18 giây thay vì 65s.
   - Khi chuẩn bị in ấn chính thức: Tắt Chế độ Nháp và nhấn **`BIÊN DỊCH`** (`Ctrl+S`) để xuất bản bản in vector 1200 DPI chất lượng cao nhất.
