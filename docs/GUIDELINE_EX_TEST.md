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
Sử dụng lệnh `\choiceTF` cho câu hỏi có 4 ý lựa chọn:

```latex
\begin{ex}[Chuyên đề Đạo hàm]
Cho hàm số $y = f(x) = x^3 - 3x^2 + 2$. Xét tính đúng/sai của các khẳng định sau:
\choiceTF
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

**Quy tắc:**
- Ý nào đúng: Đặt `\True` ở đầu nội dung khẳng định.
- Ý nào sai: Để nội dung khẳng định bình thường (không có `\True`).
- Môi trường `\begin{itemchoice} \itemch ... \end{itemchoice}` trong `\begin{loigiai}` giúp trình bày lời giải phân tách rành mạch cho từng ý a), b), c), d).

---

### 2.3. Phần III: Câu trắc nghiệm Trả lời ngắn
Sử dụng lệnh `\shortans{<kết_quả>}`:

```latex
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

## 3. LỆNH CHÈN HÌNH MINH HỌA SONG SONG VĂN BẢN (`\immini` & `\imminiL`)

Để chèn đồ thị toạ độ TikZ hoặc hình vẽ không gian nằm gọn gàng bên cạnh câu hỏi:
- **`\immini{Văn bản câu hỏi}{Mã hình vẽ TikZ hoặc \includegraphics}`**: Hình vẽ nằm bên **PHẢI**, chữ nằm bên trái.
- **`\imminiL{Văn bản câu hỏi}{Mã hình vẽ TikZ hoặc \includegraphics}`**: Hình vẽ nằm bên **TRÁI**, chữ nằm bên phải.

**Ví dụ thực tế:**
```latex
\begin{ex}
\immini{
  Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$, có đồ thị như hình vẽ bên.
  Số nghiệm thực của phương trình $2f(x) - 3 = 0$ là:
  \choice
  {$1$}
  {$2$}
  {\True $3$}
  {$4$}
}{
  \begin{tikzpicture}[scale=0.6, >=stealth]
    \draw[->] (-2.5,0) -- (3,0) node[below] {$x$};
    \draw[->] (0,-2.5) -- (0,3) node[left] {$y$};
    \node[below left] at (0,0) {$O$};
    \draw[thick, smooth, domain=-2:2.2] plot (\x, {(\x)^3 - 3*(\x) + 1});
  \end{tikzpicture}
}
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
