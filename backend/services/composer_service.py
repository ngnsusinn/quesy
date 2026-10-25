"""Quesy Exam Composer Service - Open-Prism LaTeX Workspace Backend.
Compiles raw or structured LaTeX exam source code into publication-grade PDFs
with authentic Computer Modern Unicode (CMU Serif) typography, MathJax vector equations,
and TikZ / tkz-tab vector diagrams via Headless Chromium.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.services.latex_pdf_exporter import (
    find_browser_executable,
    get_cmu_font_css,
    render_math_html,
    convert_latex_table_to_html,
)
from backend.services.tikz_renderer import render_tikz_to_svg, normalize_tikz_exam_standard
from backend.services.latex_converter import sanitize_latex

logger = logging.getLogger("quesy.composer_service")

STORAGE_COMPOSER_CACHE = Path(__file__).resolve().parent.parent.parent / "storage" / "composer_cache"
STORAGE_COMPOSER_CACHE.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Canonical Starter Exam Templates
# ---------------------------------------------------------------------------

TEMPLATES: Dict[str, Dict[str, str]] = {
    "ex_test_standard_exam": {
        "title": "Đề thi Chuẩn Quốc Gia 2025 (Gói ex_test v3.3)",
        "description": "Đầy đủ 3 phần: Trắc nghiệm 4 lựa chọn (\\choice), Đúng/Sai (\\choiceTF), Trả lời ngắn (\\shortans), chèn hình \\immini.",
        "latex": r"""\begin{center}
  \textbf{\large KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}\\
  \textbf{\large MÔN THI: TOÁN HỌC}\\
  \textit{Thời gian làm bài: 90 phút, không kể thời gian phát đề}
\end{center}
\vspace{0.4cm}

\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\begin{ex}
\immini{
  Cho hàm số bậc ba $y = f(x)$ có đồ thị như hình bên.
  Hàm số đã cho đồng biến trên khoảng nào dưới đây?
}{
  \begin{tikzpicture}[scale=0.55, >=stealth]
    \draw[->] (-3, 0) -- (3.5, 0) node[right] {$x$};
    \draw[->] (0, -4) -- (0, 4.5) node[above] {$y$};
    \node[below left] at (0, 0) {$O$};
    \draw[dashed] (-1, 0) node[below] {$-1$} -- (-1, 3) -- (0, 3) node[left] {$3$};
    \draw[dashed] (2, 0) node[above] {$2$} -- (2, -2) -- (0, -2) node[left] {$-2$};
    \draw[thick, smooth, domain=-2.3:3.1] plot (\x, {(\x)^3 - 1.5*(\x)^2 - 6*(\x) + 0.5});
    \fill (-1, 3) circle (1.5pt);
    \fill (2, -2) circle (1.5pt);
  \end{tikzpicture}
}
\choice
{\True $(-\infty; -1)$}
{$(-1; 2)$}
{$(0; 2)$}
{$(-\infty; 2)$}
\begin{loigiai}
Dựa vào đồ thị, hàm số đồng biến trên các khoảng $(-\infty; -1)$ và $(2; +\infty)$.
\end{loigiai}
\end{ex}

\begin{ex}
Cho hàm số $y = f(x)$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Điểm cực đại của đồ thị hàm số là:
\choice
{$(1; -1)$}
{\True $(-2; 4)$}
{$(-2; -1)$}
{$(1; 4)$}
\begin{loigiai}
Tại $x = -2$, $f'(x)$ đổi dấu từ dương sang âm và $f(-2) = 4$. Do đó điểm cực đại là $(-2; 4)$.
\end{loigiai}
\end{ex}

\section*{PHẦN II. Câu trắc nghiệm Đúng/Sai}
\textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\begin{ex}
Cho hàm số $y = f(x) = x^3 - 3x^2 + 2$. Xét tính đúng sai của các khẳng định sau:
\choiceTF[1]
{\True Hàm số đạt cực đại tại điểm $x = 0$.}
{Giá trị cực tiểu của hàm số bằng $2$.}
{\True Điểm uốn của đồ thị hàm số là $I(1; 0)$.}
{Hàm số đồng biến trên toàn bộ tập xác định $\mathbb{R}$.}
\begin{loigiai}
Ta có $y' = 3x^2 - 6x = 3x(x - 2)$.
\begin{itemchoice}
\itemch Đúng. Qua $x = 0$, $y'$ đổi dấu từ $+$ sang $-$.
\itemch Sai. Giá trị cực tiểu $y(2) = -2$.
\itemch Đúng. $y'' = 6x - 6 = 0 \Leftrightarrow x = 1 \Rightarrow y(1) = 0$.
\itemch Sai. Hàm số nghịch biến trên $(0; 2)$.
\end{itemchoice}
\end{loigiai}
\end{ex}

\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}
\textit{Thí sinh trả lời từ câu 1 đến câu 6.}

\begin{ex}
Một vật thể chuyển động với vận tốc $v(t) = 3t^2 + 2t$ (m/s). Tính quãng đường vật đi được từ thời điểm $t = 0$ (s) đến $t = 2$ (s).
\shortans{12}
\begin{loigiai}
$s = \int_{0}^{2} (3t^2 + 2t)\,\mathrm{d}t = \left. (t^3 + t^2) \right|_0^2 = 12\text{ (m)}$.
\end{loigiai}
\end{ex}
"""
    },
    "circular_32_full_exam": {
        "title": "Đề thi Chuẩn Thông tư 32 (Định dạng 2025)",
        "description": "Đề thi đầy đủ 3 phần: Trắc nghiệm 4 lựa chọn, Đúng/Sai 4 ý (QĐ 764), và Trả lời ngắn.",
        "latex": r"""\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\begin{ex}
\immini{
  Cho hàm số bậc ba $y = f(x)$ liên tục trên $\mathbb{R}$ có đồ thị như hình vẽ.
  Hàm số đã cho nghịch biến trên khoảng nào dưới đây?
}{
  \begin{tikzpicture}[scale=0.55, >=stealth]
    \clip (-3.8, -5.5) rectangle (4.2, 5.5);
    \draw[->, thick] (-3.5, 0) -- (3.8, 0) node[right] {$x$};
    \draw[->, thick] (0, -5) -- (0, 5) node[above] {$y$};
    \node[below left] at (0, 0) {$O$};
    \draw[dashed] (-1, 0) node[below] {$-1$} -- (-1, 4) -- (0, 4) node[left] {$4$};
    \draw[dashed] (2, 0) node[above] {$2$} -- (2, -3) -- (0, -3) node[left] {$-3$};
    \draw[thick, black, smooth, samples=100, domain=-2.5:3.2] plot (\x, {(\x)^3 - 1.5*(\x)^2 - 6*(\x) + 0.5});
    \fill (-1, 4) circle (1.5pt);
    \fill (2, -3) circle (1.5pt);
  \end{tikzpicture}
}
\choice
{$(-\infty; -1)$}
{\True $(-1; 2)$}
{$(2; +\infty)$}
{$(-\infty; 2)$}
\begin{loigiai}
Dựa vào đồ thị, hàm số nghịch biến trên khoảng $(-1; 2)$.
\end{loigiai}
\end{ex}

\begin{ex}
Cho hàm số $y = f(x)$ có bảng biến thiên như sau:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Điểm cực đại của đồ thị hàm số là:
\choice
{$(1; -1)$}
{\True $(-2; 4)$}
{$(-2; -1)$}
{$(1; 4)$}
\begin{loigiai}
Điểm cực đại của đồ thị hàm số là $(-2; 4)$.
\end{loigiai}
\end{ex}

\section*{PHẦN II. Câu trắc nghiệm Đúng/Sai}
\textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\begin{ex}
Cho hàm số bậc ba $y = f(x) = ax^3 + bx^2 + cx + d$ ($a \neq 0$). Xét tính Đúng/Sai của các khẳng định sau:
\choiceTF[1]
{\True Đồ thị hàm số bậc ba luôn có tâm đối xứng là điểm uốn.}
{Nếu hàm số có hai điểm cực trị thì tích các giá trị cực trị luôn âm.}
{\True Hàm số luôn có đạo hàm cấp hai liên tục trên $\mathbb{R}$.}
{Điểm cực trị của hàm số là nghiệm của phương trình $f'(x) = 0$.}
\begin{loigiai}
\begin{itemchoice}
\itemch Đúng. Đồ thị hàm số bậc ba luôn nhận điểm uốn làm tâm đối xứng.
\itemch Sai. Hai giá trị cực trị có thể cùng dương hoặc cùng âm.
\itemch Đúng. Hàm đa thức bậc ba liên tục và có đạo hàm mọi cấp trên $\mathbb{R}$.
\itemch Sai. Điểm cực trị là hoành độ điểm cực trị hoặc điểm $(x_0; y_0)$.
\end{itemchoice}
\end{loigiai}
\end{ex}

\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}
\textit{Thí sinh trả lời từ câu 1 đến câu 6.}

\begin{ex}
Cho hàm số $f(x) = \ln(x^2 - 2x + 5)$. Giá trị nhỏ nhất của hàm số trên $\mathbb{R}$ bằng bao nhiêu?
\shortans{1.39}
\begin{loigiai}
Ta có $x^2 - 2x + 5 = (x - 1)^2 + 4 \ge 4 \Rightarrow \ln(x^2 - 2x + 5) \ge \ln 4 \approx 1{,}39$.
\end{loigiai}
\end{ex}
"""
    },
    "variation_table_calculus": {
        "title": "Chuyên đề Bảng Biến Thiên & Cực Trị (tkz-tab)",
        "description": "Các dạng bảng biến thiên hàm bậc 3, hàm bậc 4, và hàm phân thức có tiệm cận đứng.",
        "latex": r"""\section*{BÀI TẬP KHẢO SÁT HÀM SỐ QUA BẢNG BIẾN THIÊN}

\begin{ex}
Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.2,deltacl=0.6]
  {$x$/.6, $y'$/.6, $y$/2}
  {$-\infty$,$-1$,$0$,$1$,$+\infty$}
  \tkzTabLine{,-,$0$,+,$0$,-,$0$,+,}
  \tkzTabVar{+/ $+\infty$, -/$-5$, +/$2$, -/$-5$, +/$+\infty$}
\end{tikzpicture}
Tìm số điểm cực trị của hàm số đã cho.
\choice
{$1$}
{$2$}
{\True $3$}
{$4$}
\begin{loigiai}
Đạo hàm $y'$ đổi dấu 3 lần tại $x = -1, 0, 1$, do đó hàm số có 3 điểm cực trị.
\end{loigiai}
\end{ex}

\begin{ex}
Cho hàm số phân thức $y = \dfrac{ax+b}{cx+d}$ có bảng biến thiên:
\begin{tikzpicture}
  \tikzset{double style/.append style = {double distance=2.5pt}}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.4]
  {$x$/.6, $y'$/.6, $y$/2}
  {$-\infty$,$1$,$+\infty$}
  \tkzTabLine{,+,d,+,}
  \tkzTabVar{-/$2$, +D-/$+\infty$/$-\infty$, +/$2$}
\end{tikzpicture}
Phương trình đường tiệm cận đứng và tiệm cận ngang của đồ thị hàm số lần lượt là:
\choice
{\True $x = 1, y = 2$}
{$x = 2, y = 1$}
{$x = -1, y = 2$}
{$x = 1, y = -2$}
\begin{loigiai}
Dựa vào bảng biến thiên, tiệm cận đứng là $x = 1$ và tiệm cận ngang là $y = 2$.
\end{loigiai}
\end{ex}
"""
    },
    "geometry_3d": {
        "title": "Chuyên đề Hình Học Không Gian (TikZ 3D)",
        "description": "Mẫu bài tập hình học không gian với khối đa diện, hình chóp, và hệ trục Oxyz.",
        "latex": r"""\section*{BÀI TẬP HÌNH HỌC KHÔNG GIAN CỔ ĐIỂN & OXYZ}

\begin{ex}
Cho hình chóp $S.ABCD$ có đáy $ABCD$ là hình vuông cạnh $a$, cạnh bên $SA$ vuông góc với mặt phẳng đáy $(ABCD)$ và $SA = a\sqrt{2}$.
\begin{center}
\begin{tikzpicture}[scale=0.85]
  \coordinate (A) at (0, 0);
  \coordinate (B) at (-1.6, -1.2);
  \coordinate (C) at (2.4, -1.2);
  \coordinate (D) at (4, 0);
  \coordinate (S) at (0, 3.2);

  \draw[thick] (S) -- (B) -- (C) -- (D) -- (S) -- (C);
  \draw[dashed, thick] (B) -- (A) -- (D) (S) -- (A);

  \node[above] at (S) {$S$};
  \node[left] at (B) {$B$};
  \node[below] at (C) {$C$};
  \node[right] at (D) {$D$};
  \node[above left] at (A) {$A$};
\end{tikzpicture}
\end{center}
Tính thể tích của khối chóp $S.ABCD$.
\choice
{\True $V = \dfrac{a^3\sqrt{2}}{3}$}
{$V = a^3\sqrt{2}$}
{$V = \dfrac{a^3\sqrt{2}}{6}$}
{$V = \dfrac{a^3}{3}$}
\begin{loigiai}
Diện tích đáy $S_{ABCD} = a^2$. Chiều cao $h = SA = a\sqrt{2}$.\\
Thể tích $V = \dfrac{1}{3} S_{ABCD} \cdot SA = \dfrac{a^3\sqrt{2}}{3}$.
\end{loigiai}
\end{ex}
"""
    },
    "blank_document": {
        "title": "Tài Liệu Mới (Văn Bản Trống)",
        "description": "Mẫu tài liệu khởi tạo sạch sẽ với header cơ bản.",
        "latex": r"""\section*{TIÊU ĐỀ BÀI KIỂM TRA}

\begin{ex}
Soạn thảo nội dung câu hỏi đầu tiên tại đây...
\choice
{\True Phương án A}
{Phương án B}
{Phương án C}
{Phương án D}
\begin{loigiai}
Lời giải chi tiết cho câu hỏi.
\end{loigiai}
\end{ex}
"""
    }
}
TEMPLATES["calculus_12_exam"] = TEMPLATES["variation_table_calculus"]
TEMPLATES["geometry_12_exam"] = TEMPLATES["geometry_3d"]
TEMPLATES["blank_exam"] = TEMPLATES["blank_document"]


def fix_immini_choice_nesting(latex_text: str) -> str:
    """If \\choice{...}{...}{...}{...} is accidentally placed inside \\immini{...}{...},
    extract it and place \\choice outside after \\immini to prevent TeX box errors."""
    if r"\immini" not in latex_text or r"\choice" not in latex_text:
        return latex_text

    pattern = re.compile(r"\\immini(?:L)?\s*\{")
    pos = 0
    while True:
        m = pattern.search(latex_text, pos)
        if not m:
            break

        start_arg1 = m.end()
        depth = 1
        i = start_arg1
        while i < len(latex_text) and depth > 0:
            if latex_text[i] == '{': depth += 1
            elif latex_text[i] == '}': depth -= 1
            i += 1

        if depth != 0:
            pos = start_arg1
            continue

        arg1 = latex_text[start_arg1:i-1]

        if r"\choice" not in arg1:
            pos = i
            continue

        while i < len(latex_text) and latex_text[i].isspace():
            i += 1
        if i >= len(latex_text) or latex_text[i] != '{':
            pos = i
            continue

        start_arg2 = i + 1
        depth = 1
        j = start_arg2
        while j < len(latex_text) and depth > 0:
            if latex_text[j] == '{': depth += 1
            elif latex_text[j] == '}': depth -= 1
            j += 1

        if depth != 0:
            pos = start_arg2
            continue

        arg2 = latex_text[start_arg2:j-1]

        choice_idx = arg1.find(r"\choice")
        choice_block = arg1[choice_idx:].strip()
        clean_arg1 = arg1[:choice_idx].strip()

        replacement = f"\\immini{{\n  {clean_arg1}\n}}{{\n  {arg2}\n}}\n{choice_block}"
        latex_text = latex_text[:m.start()] + replacement + latex_text[j:]
        pos = m.start() + len(replacement)

    return latex_text


def ensure_full_latex_document(
    latex_source: str = "",
    mode: str = "dethi",
    title: str = "Tài Liệu Soạn Thảo",
    latex_code: Optional[str] = None
) -> str:
    r"""Wraps preamble-free LaTeX question code with standard exam preamble
    including fontspec, amsmath, amssymb, amsfonts, geometry a4 1.5cm margin,
    multicol, tikz, tkz-tab, tcolorbox, and ex_test with [dethi] or [loigiai] mode.
    Preserves existing full documents with documentclass (backward compatibility),
    while normalizing packages (vietnam -> fontspec, ensures tcolorbox for ex_test)
    and synchronizing ex_test mode option ([dethi] vs [loigiai]) if requested.
    """
    raw = (latex_source or latex_code or "").strip()
    if not raw:
        return raw

    # Normalize mode
    norm_mode = "loigiai" if str(mode).strip().lower() in ("loigiai", "solcolor", "color", "solution", "true", "1") else "dethi"

    # Backward compatibility: If already has \documentclass, do not double-wrap
    if r"\documentclass" in raw:
        # In XeTeX/Tectonic, replace legacy 8-bit vietnam package with modern fontspec
        raw = re.sub(r'\\usepackage(\[[^\]]*\])?\{vietnam\}', r'\\usepackage{fontspec}', raw)

        # Ensure tcolorbox with skins,breakable,xparse if ex_test or immini is present
        if "ex_test" in raw or "immini" in raw:
            if "tcolorbox" not in raw:
                if "ex_test" in raw:
                    raw = re.sub(
                        r'(\\usepackage(\[[^\]]*\])?\{ex_test\})',
                        r'\\usepackage{tcolorbox}\n\\tcbuselibrary{skins,breakable,xparse}\n\1',
                        raw,
                        count=1
                    )
                else:
                    raw = re.sub(
                        r'(\\begin\{document\})',
                        r'\\usepackage{tcolorbox}\n\\tcbuselibrary{skins,breakable,xparse}\n\1',
                        raw,
                        count=1
                    )
            elif "xparse" not in raw:
                if r"\tcbuselibrary" in raw:
                    raw = re.sub(
                        r'(\\tcbuselibrary\{[^}]*\})',
                        r'\1\n\\tcbuselibrary{xparse}',
                        raw,
                        count=1
                    )
                else:
                    raw = re.sub(
                        r'(\\usepackage\{tcolorbox\})',
                        r'\1\n\\tcbuselibrary{skins,breakable,xparse}',
                        raw,
                        count=1
                    )

        # If ex_test is included, ensure the mode option matches requested mode
        if "ex_test" in raw:
            raw = re.sub(r'\\usepackage\[[^\]]*\]\{ex_test\}', lambda m: f"\\usepackage[{norm_mode}]{{ex_test}}", raw)
            raw = re.sub(r'\\usepackage\{ex_test\}', lambda m: f"\\usepackage[{norm_mode}]{{ex_test}}", raw)

        raw = fix_immini_choice_nesting(raw)
        return raw

    # Strip any accidental outer \begin{document} / \end{document} if no \documentclass
    body = raw
    doc_match = re.search(r'\\begin\{document\}([\s\S]*?)\\end\{document\}', body)
    if doc_match:
        body = doc_match.group(1).strip()
    body = re.sub(r'\\documentclass(\[[^\]]*\])?\{[^}]*\}', '', body)
    body = re.sub(r'\\usepackage(\[[^\]]*\])?\{[^}]*\}', '', body)
    body = re.sub(r'\\tcbuselibrary\{[^}]*\}', '', body)
    body = re.sub(r'\\begin\{document\}', '', body).strip()
    body = re.sub(r'\\end\{document\}', '', body).strip()

    body = fix_immini_choice_nesting(body)

    preamble = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage{{fontspec}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage[left=1.5cm,right=1.5cm,top=1.5cm,bottom=1.5cm]{{geometry}}
\\usepackage{{multicol}}
\\usepackage{{tikz,tkz-tab}}
\\usepackage{{tcolorbox}}
\\tcbuselibrary{{skins,breakable,xparse}}
\\usepackage[{norm_mode}]{{ex_test}}

\\begin{{document}}
{body}
\\end{{document}}"""

    return preamble


# ---------------------------------------------------------------------------
# 2. Section Question Counter & Sync
# ---------------------------------------------------------------------------

def sync_section_question_counts(latex_code: str) -> str:
    """Dynamically counts questions in each section (PHẦN I, II, III) and updates
    the instruction text 'từ câu 1 đến câu X' to match actual question count."""
    if not latex_code:
        return latex_code

    section_headers = re.findall(
        r'(?:\\noindent\s*)?\\textbf\{PHẦN\s+[IVX0-9]+[^}]*\}|\\section\*?\{PHẦN\s+[IVX0-9]+[^}]*\}|PHẦN\s+[IVX0-9]+\.[^\n]*',
        latex_code,
        re.IGNORECASE
    )
    if not section_headers:
        return latex_code

    sections = re.split(
        r'(?=(?:\\noindent\s*)?\\textbf\{PHẦN|\\section\*?\{PHẦN|PHẦN\s+[IVX0-9]+\.)',
        latex_code,
        flags=re.IGNORECASE
    )
    if len(sections) <= 1:
        return latex_code

    updated = []
    for sec in sections:
        ex_matches = re.findall(r'\\begin\{(?:ex|bt|vd)\}', sec)
        count = len(ex_matches) if ex_matches else 0
        if count == 0:
            clean_body = re.sub(r'từ\s+câu\s+1\s*(?:đến|tới|-)\s*câu\s*\d+[^\n]*', '', sec, flags=re.IGNORECASE)
            q_nums = set()
            for m in re.finditer(r'(?:\\textbf\{\s*Câu\s*(\d+)[\.:]?\s*\}|(?<![\w\\{])Câu\s*(\d+)[\.:])', clean_body, re.IGNORECASE):
                num = m.group(1) or m.group(2)
                if num:
                    q_nums.add(int(num))
            count = len(q_nums)
        if count > 0:
            sec = re.sub(r'(từ\s+câu\s+1\s+đến\s+câu\s+)\d+', rf'\g<1>{count}', sec, flags=re.IGNORECASE)
            sec = re.sub(r'(từ\s+câu\s+1\s*(?:đến|tới|-)\s*câu\s*)\d+', rf'\g<1>{count}', sec, flags=re.IGNORECASE)
        updated.append(sec)

    return "".join(updated)


# ---------------------------------------------------------------------------
# 3. LaTeX to HTML Compilation Parser
# ---------------------------------------------------------------------------

def compile_latex_source_to_html(
    latex_source: str,
    default_title: str = "Đề Thi Soạn Thảo LaTeX",
    mode: str = "dethi"
) -> str:
    """Converts general LaTeX or exam code into publication-grade HTML with CMU Serif,
    MathJax vector equations, and TikZ/tkz-tab vector SVGs for Chromium PDF compilation.
    """
    raw = (latex_source or "").strip()
    if not raw:
        raw = TEMPLATES["blank_exam"]["latex"]

    raw = ensure_full_latex_document(raw, mode=mode, title=default_title)

    # 1. Extract title if present: \title{...}
    title_match = re.search(r'\\title\{([^}]+)\}', raw)
    doc_title = title_match.group(1).strip() if title_match else default_title

    # 2. Extract body between \begin{document} and \end{document} if present
    doc_match = re.search(r'\\begin\{document\}([\s\S]*?)\\end\{document\}', raw)
    body = doc_match.group(1).strip() if doc_match else raw

    # 3. Strip out preamble commands if they leaked into body
    body = re.sub(r'\\documentclass\[?[^\]]*\]?\{[^}]*\}', '', body)
    body = re.sub(r'\\usepackage\[?[^\]]*\]?\{[^}]*\}', '', body)
    body = re.sub(r'\\pagestyle\{[^}]*\}', '', body)
    body = re.sub(r'\\thispagestyle\{[^}]*\}', '', body)
    body = re.sub(r'\\tcbuselibrary\{[^}]*\}', '', body)
    body = re.sub(r'\\begin\{document\}', '', body)
    body = re.sub(r'\\end\{document\}', '', body)

    # 3b. Mode-specific solution handling
    norm_mode = "loigiai" if str(mode).strip().lower() in ("loigiai", "solcolor", "color", "solution", "true", "1") else "dethi"
    if norm_mode == "dethi":
        body = re.sub(r'\\begin\{loigiai\}[\s\S]*?\\end\{loigiai\}', '', body)
        body = re.sub(r'\\loigiai\{[\s\S]*?\}', '', body)
    # When norm_mode == "loigiai", we keep \begin{loigiai}...\end{loigiai} in body so math inside loigiai gets rendered in step 7.

    # 4. Extract and render all TikZ blocks to vector SVGs
    tikz_blocks = []
    def _save_tikz(m):
        code = m.group(0).strip()
        # Clean accidental outer $$
        code = re.sub(r'^\$\$?', '', code).strip()
        code = re.sub(r'\$\$?$', '', code).strip()
        try:
            res = render_tikz_to_svg(code)
            if res.get("success") and res.get("svg"):
                svg = res["svg"]
                svg = re.sub(r'<\?xml.*?\?>', '', svg).strip()
                html = f'<div class="tikz-vector-container">{svg}</div>'
            else:
                err_text = res.get("error", "Lỗi biên dịch TikZ")
                html = f'<div class="tikz-vector-container" style="color:#b91c1c; background:#fef2f2; border:1px dashed #f87171; border-radius:8px; padding:10px; font-size:10pt;">[TikZ Error: {err_text}]</div>'
        except Exception as e:
            html = f'<div class="tikz-vector-container" style="color:#b91c1c;">[Lỗi TikZ: {e}]</div>'

        tikz_blocks.append(html)
        return f"__LATEX_TIKZ_COMPILED_{len(tikz_blocks) - 1}__"

    body = re.sub(r'\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}', _save_tikz, body)

    # 5. Extract and render all standalone LaTeX tables / arrays
    table_blocks = []
    def _save_table(m):
        tbl_code = m.group(0).strip()
        tbl_html = convert_latex_table_to_html(tbl_code)
        table_blocks.append(tbl_html)
        return f"__LATEX_TABLE_COMPILED_{len(table_blocks) - 1}__"

    body = re.sub(
        r'(?:\$\$\s*)?\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|tabular)\}(?:\s*\$\$)?',
        _save_table,
        body,
        flags=re.DOTALL
    )

    # 6. Parse choice and choiceTF into HTML
    def _render_choice(m):
        opts = [m.group(i).strip() for i in range(1, 5)]
        html_opts = []
        for idx, opt in enumerate(opts):
            lbl = chr(65 + idx)
            is_correct = r"\True" in opt
            clean_opt = re.sub(r'\\True\s*', '', opt).strip()
            style = "font-weight: bold; color: #0071e3;" if is_correct else ""
            html_opts.append(f'<div style="display: inline-block; width: 48%; margin-bottom: 4px; {style}"><strong>{lbl}.</strong> {clean_opt}</div>')
        return f'<div style="display: flex; flex-wrap: wrap; gap: 4px; margin: 6px 0;">{"".join(html_opts)}</div>'

    body = re.sub(r'\\choice(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', _render_choice, body)

    def _render_choicetf(m):
        opts = [m.group(i).strip() for i in range(1, 5)]
        html_opts = []
        for idx, opt in enumerate(opts):
            lbl = chr(97 + idx)
            is_true = r"\True" in opt
            clean_opt = re.sub(r'\\True\s*', '', opt).strip()
            clean_opt = re.sub(r'^[a-d]\)\s*', '', clean_opt).strip()
            badge = '<span style="color: #16a34a; font-weight: bold; margin-right: 4px;">[Đ]</span>' if is_true else '<span style="color: #dc2626; font-weight: bold; margin-right: 4px;">[S]</span>'
            html_opts.append(f'<div style="display: block; width: 100%; margin-bottom: 4px;">{badge}<strong>{lbl})</strong> {clean_opt}</div>')
        return f'<div style="display: block; margin: 6px 0;">{"".join(html_opts)}</div>'

    body = re.sub(r'\\choiceTF(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', _render_choicetf, body)

    # 6. Parse sections and structure
    body = re.sub(r'\\section\*?\{([^}]+)\}', r'<h2 class="latex-section">\1</h2>', body)
    body = re.sub(r'\\subsection\*?\{([^}]+)\}', r'<h3 class="latex-subsection">\1</h3>', body)

    # 6b. Parse minipages on body before paragraph splitting
    minipage_blocks = []
    def _save_minipage(m):
        width_arg = m.group(1).strip()
        content = m.group(2)
        align_style = "text-align: center;" if r"\centering" in content else "text-align: left;"
        content_cleaned = content.replace(r"\centering", "").strip()
        m_w = re.match(r'^([\d.]+)\s*\\(?:textwidth|linewidth)$', width_arg)
        if m_w:
            css_width = f"{float(m_w.group(1))*100:.1f}%"
        else:
            css_width = width_arg.replace(r"	extwidth", "100%").replace(r"\linewidth", "100%")
        content_cleaned = re.sub(r'\\\\(?:\s*\[[^\]]*\])?', '<br>', content_cleaned)
        div_html = f'<div style="display: inline-block; vertical-align: top; width: {css_width}; width: {width_arg}; {align_style}">{content_cleaned}</div>'
        minipage_blocks.append(div_html)
        return f"__LATEX_MINIPAGE_COMPILED_{len(minipage_blocks) - 1}__"

    body = re.sub(r'\\begin\{minipage\}(?:\[[^\]]*\])?\{([^}]+)\}([\s\S]*?)\\end\{minipage\}', _save_minipage, body, flags=re.DOTALL)

    # 7. Convert paragraphs
    paragraphs = re.split(r'\n\s*\n', body)
    rendered_paragraphs = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if any(p.startswith(prefix) for prefix in ("__LATEX_TIKZ_COMPILED_", "__LATEX_TABLE_COMPILED_", "__LATEX_MINIPAGE_COMPILED_", "<h2", "<h3")):
            rendered_paragraphs.append(p)
            continue

        # Render math in this paragraph
        p_html = render_math_html(p)
        rendered_paragraphs.append(f'<div class="latex-p">{p_html}</div>')

    final_body = "\n".join(rendered_paragraphs)

    # 7b. Parse minipages, hfill, rule, dotfill, framebox, fbox on final_body
    # (Applied after render_math_html to protect HTML tags from being escaped into &lt; and &gt;)
    def _fix_rule(m):
        w = m.group(1).strip()
        h = m.group(2).strip()
        m_w = re.match(r'^([\d.]+)\s*\\(?:textwidth|linewidth)$', w)
        if m_w:
            css_w = f"{float(m_w.group(1))*100:.1f}%"
        else:
            css_w = w.replace(r"	extwidth", "100%").replace(r"\linewidth", "100%")
        return f'<hr style="width: {css_w}; height: {h}; background: #000; border: none; margin: 4px 0;">'

    final_body = re.sub(r'(?:\\\\|\\)rule\{([^}]+)\}\{([^}]+)\}', _fix_rule, final_body)
    final_body = re.sub(r'\\hfill', '<span style="float: right;"></span>', final_body)
    final_body = re.sub(r'\\dotfill', '<span style="border-bottom: 1px dotted #000; display: inline-block; width: 80px;"></span>', final_body)
    final_body = re.sub(r'\\(?:framebox|fbox)\{((?:[^{}]|\\{[^{}]*\\})+)\}', r'<span style="border: 1px solid #000; padding: 2px 4px; display: inline-block;">\1</span>', final_body)
    final_body = re.sub(r'\\noindent\s*', '', final_body)
    final_body = re.sub(r'\\vspace\{[^}]*\}', '', final_body)
    final_body = re.sub(r'\	extbf\{((?:[^{}]|\\{[^{}]*\\})+)\}', r'<strong>\1</strong>', final_body)
    final_body = re.sub(r'\	extit\{((?:[^{}]|\\{[^{}]*\\})+)\}', r'<em>\1</em>', final_body)

    # 7c. Render loigiai block on final_body if in loigiai mode
    if norm_mode == "loigiai":
        def _render_lg(m):
            lg_inner = m.group(1).strip()
            lg_inner = re.sub(r'\\begin\{itemchoice\}', '<div style="margin-top:4px;">', lg_inner)
            lg_inner = re.sub(r'\\end\{itemchoice\}', '</div>', lg_inner)
            lg_inner = re.sub(r'\\itemch\s*', '<div style="margin-bottom:2px;">• ', lg_inner)
            return f'<div class="loigiai-block" style="background:#f8fafc; border-left:3px solid #0071e3; padding:8px 12px; margin:8px 0; border-radius:4px; font-size:10pt;"><strong>Lời giải:</strong><div style="margin-top:4px;">{lg_inner}</div></div>'
        final_body = re.sub(r'\\begin\{loigiai\}([\s\S]*?)\\end\{loigiai\}', _render_lg, final_body)

    # 7d. Restore TikZ, Tables, and Minipages
    for idx, svg_html in enumerate(tikz_blocks):
        final_body = final_body.replace(f"__LATEX_TIKZ_COMPILED_{idx}__", svg_html)
    for idx, tbl_html in enumerate(table_blocks):
        final_body = final_body.replace(f"__LATEX_TABLE_COMPILED_{idx}__", tbl_html)
    for idx, mini_html in enumerate(minipage_blocks):
        final_body = final_body.replace(f"__LATEX_MINIPAGE_COMPILED_{idx}__", mini_html)

    font_css = get_cmu_font_css()

    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>{doc_title}</title>
  <style>
    {font_css}

    @page {{
      size: A4 portrait;
      margin: 16mm 16mm 16mm 16mm;
      @bottom-right {{
        content: "Trang " counter(page);
        font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif;
        font-size: 9pt;
      }}
    }}

    body {{
      font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #000;
      margin: 0;
      padding: 0;
      background: #fff;
      -webkit-font-smoothing: subpixel-antialiased;
    }}

    .latex-section {{
      font-size: 11.5pt;
      font-weight: bold;
      margin-top: 14px;
      margin-bottom: 6px;
      break-after: avoid;
    }}

    .latex-subsection {{
      font-size: 11pt;
      font-weight: bold;
      margin-top: 10px;
      margin-bottom: 4px;
      break-after: avoid;
    }}

    .latex-p {{
      margin-bottom: 6px;
      text-align: left;
      word-spacing: normal;
    }}

    .tikz-vector-container {{
      text-align: center;
      margin: 10px auto;
      page-break-inside: avoid;
    }}
    .tikz-vector-container svg {{
      max-width: 62%;
      height: auto;
      display: block;
      margin: 0 auto;
    }}
    .tikz-vector-container svg text,
    .tikz-vector-container svg tspan {{
      font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif !important;
    }}

    /* Tables */
    .exam-table, .variation-table {{
      margin: 10px auto;
      border-collapse: collapse;
      page-break-inside: avoid;
      font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif;
    }}
    .exam-table td, .exam-table th {{
      border: 0.8px solid #000;
      padding: 4px 10px;
      text-align: center;
      font-size: 10.5pt;
    }}
    .variation-table {{
      border: none;
    }}
    .variation-table td {{
      border: none;
      padding: 3px 10px;
      text-align: center;
      font-size: 10.5pt;
      min-width: 26px;
    }}
    .variation-table tr.row-x td, .variation-table tr.row-fprime td {{
      border-bottom: 0.9px solid #000;
    }}
    .variation-table td:first-child {{
      border-right: 0.9px solid #000;
      padding-right: 14px;
      font-weight: bold;
    }}
  </style>
</head>
<body>
  {final_body}
</body>
</html>"""
    return full_html


# ---------------------------------------------------------------------------
# 3. PDF Compilation Execution (Hybrid: Tectonic XeTeX with Chromium Fallback)
# ---------------------------------------------------------------------------

def find_tectonic_executable() -> Optional[Path]:
    """Finds tectonic executable in PATH or standard local locations."""
    found = shutil.which("tectonic")
    if found:
        return Path(found)

    candidate_paths = [
        Path("/usr/local/bin/tectonic"),
        Path("/usr/bin/tectonic"),
        Path.home() / ".cargo" / "bin" / "tectonic",
        Path(__file__).resolve().parent.parent.parent / "bin" / "tectonic",
        Path(__file__).resolve().parent.parent.parent / "bin" / "tectonic.exe",
    ]
    for p in candidate_paths:
        if p.exists() and p.is_file():
            return p
    return None


def compile_with_tectonic(
    latex_source: str,
    output_pdf: Path,
    title: str = "Tài Liệu Soạn Thảo",
    mode: str = "dethi"
) -> Tuple[bool, str, int]:
    """Compiles LaTeX source code directly to PDF using Tectonic XeTeX engine."""
    start_time = time.perf_counter()
    tectonic_bin = find_tectonic_executable()
    if not tectonic_bin:
        return False, "Không tìm thấy công cụ Tectonic trên hệ thống.", 0

    import tempfile
    output_pdf = Path(output_pdf).resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    raw = ensure_full_latex_document(latex_source, mode=mode, title=title)

    with tempfile.TemporaryDirectory(prefix="tectonic_build_") as tmp_dir:
        tmp_dir_path = Path(tmp_dir)

        # Copy local bundled packages (e.g. ex_test.sty) into build directory
        for p in [
            Path(__file__).resolve().parent.parent / "templates" / "ex_test.sty",
            Path(__file__).resolve().parent.parent.parent / "storage" / "latex_packages" / "ex_test.sty"
        ]:
            if p.exists():
                shutil.copy2(p, tmp_dir_path / "ex_test.sty")
                break

        # Mock missing images referenced in \\includegraphics so xdvipdfmx never halts on missing image
        blank_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\x0bIDATx\x9cc`\x00\x00\x00\x06\x00\x010\x948/\x00\x00\x00\x00IEND\xaeB`\x82"
        for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', raw):
            img_rel = m.group(1).strip()
            candidates = [img_rel] if "." in img_rel else [img_rel + ext for ext in [".png", ".jpg", ".pdf"]]
            for cand in candidates:
                cand_path = tmp_dir_path / cand
                cand_path.parent.mkdir(parents=True, exist_ok=True)
                if not cand_path.exists():
                    cand_path.write_bytes(blank_png)

        tex_file = tmp_dir_path / "document.tex"
        tex_file.write_text(raw, encoding="utf-8")

        cmd = [
            str(tectonic_bin),
            "--outdir", str(tmp_dir_path),
            "--print",
            str(tex_file)
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=45,
                encoding="utf-8",
                errors="replace",
                cwd=str(tmp_dir_path)
            )
            built_pdf = tmp_dir_path / "document.pdf"
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            if built_pdf.exists() and built_pdf.stat().st_size > 1000:
                shutil.copy2(built_pdf, output_pdf)
                return True, "", elapsed_ms
            else:
                err_output = res.stderr or res.stdout or "Biên dịch Tectonic thất bại."
                lines = [l for l in err_output.split("\n") if "error:" in l.lower() or "fatal:" in l.lower() or "!" in l]
                err_summary = "\n".join(lines[:10]) if lines else err_output[-800:]
                return False, err_summary, elapsed_ms
        except subprocess.TimeoutExpired:
            return False, "Biên dịch Tectonic quá thời gian cho phép (>45 giây).", 0
        except Exception as e:
            return False, f"Lỗi thực thi Tectonic: {e}", 0


def compile_latex_to_pdf_chromium(
    latex_source: str,
    output_pdf: Path,
    title: str = "Tài Liệu Soạn Thảo",
    mode: str = "dethi"
) -> Tuple[bool, str, int]:
    """Compiles LaTeX source code to vector-crisp PDF via Headless Chromium.
    Returns (success, error_message, elapsed_ms).
    """
    start_time = time.perf_counter()
    output_pdf = Path(output_pdf).resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temp_html = output_pdf.with_suffix(".temp.html")

    try:
        html = compile_latex_source_to_html(latex_source, default_title=title, mode=mode)
        temp_html.write_text(html, encoding="utf-8")

        browser_bin = find_browser_executable()
        if not browser_bin:
            return False, "Không tìm thấy trình duyệt Chromium/Chrome trên hệ thống để biên dịch PDF.", 0

        cmd = [
            str(browser_bin),
            "--headless",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--print-to-pdf={str(output_pdf)}",
            temp_html.resolve().as_uri()
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace"
        )
        if temp_html.exists():
            temp_html.unlink()

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True, "", elapsed_ms
        else:
            return False, f"Lỗi xuất bản PDF: {res.stderr or 'Tệp PDF rỗng'}", elapsed_ms

    except subprocess.TimeoutExpired:
        if temp_html.exists():
            temp_html.unlink()
        return False, "Biên dịch PDF quá thời gian cho phép (>30 giây).", 0
    except Exception as e:
        if temp_html.exists():
            temp_html.unlink()
        logger.exception(f"Unexpected compilation failure: {e}")
        return False, str(e), 0



def compile_with_remote_tectonic_api(
    latex_source: str,
    output_pdf: Path,
    title: str = "Tài Liệu Soạn Thảo",
    mode: str = "dethi"
) -> Tuple[bool, str, int]:
    """Compiles LaTeX using remote Tectonic Docker microservice (e.g. on armbian)."""
    start_time = time.perf_counter()
    api_url = os.environ.get("LATEX_API_URL") or os.environ.get("TECTONIC_API_URL")

    # If not explicitly configured in env, check armbian default
    if not api_url:
        try:
            req_check = urllib.request.Request("http://armbian:8090/health")
            with urllib.request.urlopen(req_check, timeout=0.8) as resp:
                if resp.status == 200:
                    api_url = "http://armbian:8090/compile"
        except Exception:
            api_url = None

    if not api_url:
        return False, "Không có dịch vụ Tectonic API từ xa.", 0

    try:
        sanitized_latex = ensure_full_latex_document(latex_source, mode=mode, title=title)
        payload = json.dumps({
            "latex_code": sanitized_latex,
            "timeout_s": 60
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=65) as resp:
            pdf_bytes = resp.read()
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            if len(pdf_bytes) > 500 and pdf_bytes.startswith(b"%PDF"):
                output_pdf = Path(output_pdf).resolve()
                output_pdf.parent.mkdir(parents=True, exist_ok=True)
                output_pdf.write_bytes(pdf_bytes)
                return True, "", elapsed_ms
            return False, "Dữ liệu trả về từ Tectonic API không hợp lệ.", elapsed_ms
    except urllib.error.HTTPError as he:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        try:
            detail = json.loads(he.read().decode())
            err_msg = detail.get("detail", str(he))
        except Exception:
            err_msg = str(he)
        return False, f"Lỗi Tectonic API: {err_msg}", elapsed_ms
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        return False, f"Không thể kết nối Tectonic API: {e}", elapsed_ms


def compile_latex_to_pdf(
    latex_source: str,
    output_pdf: Path,
    title: str = "Tài Liệu Soạn Thảo",
    mode: str = "dethi"
) -> Tuple[bool, str, int]:
    """Unified LaTeX Compiler:
    1. Checks if Remote Tectonic Docker API is available -> Compiles with remote Tectonic.
    2. Checks if local Tectonic XeTeX engine is available -> Compiles with native Tectonic.
    3. Falls back to Headless Chromium + MathJax + TikZ + CMU Serif vector pipeline.
    """
    full_latex = ensure_full_latex_document(latex_source, mode=mode, title=title)

    # 1. Try Remote Tectonic API
    ok, err, ms = compile_with_remote_tectonic_api(full_latex, output_pdf, title=title, mode=mode)
    if ok:
        return ok, err, ms
    if "Lỗi Tectonic API:" in err:
        logger.warning(f"Remote Tectonic returned syntax error: {err}")
        return False, err, ms

    # 2. Try Local Tectonic
    if find_tectonic_executable():
        ok, err, ms = compile_with_tectonic(full_latex, output_pdf, title=title, mode=mode)
        if ok:
            return ok, err, ms
        logger.warning(f"Local Tectonic compilation failed ({err}). Falling back to Headless Chromium engine.")

    # 3. Fallback to Chromium engine
    return compile_latex_to_pdf_chromium(full_latex, output_pdf, title=title, mode=mode)


# ---------------------------------------------------------------------------
# 4. Extract Questions from LaTeX to Quesy Bank Schema
# ---------------------------------------------------------------------------

def extract_questions_from_latex(latex_source: str) -> List[Dict[str, Any]]:
    """Parses questions from LaTeX text into Quesy Question Bank format.
    Supports both ex_test syntax (\\begin{ex} ... \\end{ex}) and classic (\\textbf{Câu X.}).
    """
    questions: List[Dict[str, Any]] = []

    # 1. Check for ex_test syntax (\begin{ex} ... \end{ex})
    ex_blocks = re.findall(r'\\begin\{ex\}(?:\[[^\]]*\])?([\s\S]*?)\\end\{ex\}', latex_source)
    if ex_blocks:
        for block in ex_blocks:
            block = block.strip()
            # Separate loigiai if present
            lg_match = re.search(r'\\begin\{loigiai\}([\s\S]*?)\\end\{loigiai\}', block)
            explanation = lg_match.group(1).strip() if lg_match else ""
            main_block = re.sub(r'\\begin\{loigiai\}[\s\S]*?\\end\{loigiai\}', '', block).strip()

            # A. Check for \choice
            choice_match = re.search(r'\\choice(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', main_block)
            if choice_match:
                stem = main_block[:choice_match.start()].strip()
                # Unwrap \immini{stem}{fig} if present
                im_match = re.match(r'\\immini(?:L)?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', stem)
                if im_match:
                    stem = im_match.group(1).strip() + "\n" + im_match.group(2).strip()

                options = []
                for idx, lbl in enumerate(["A", "B", "C", "D"]):
                    raw_opt = choice_match.group(idx + 1).strip()
                    is_correct = r"\True" in raw_opt
                    clean_opt = re.sub(r'\\True\s*', '', raw_opt).strip()
                    options.append({
                        "label": lbl,
                        "content": clean_opt,
                        "is_correct": is_correct,
                        "is_fixed": False
                    })
                if not any(o["is_correct"] for o in options):
                    options[0]["is_correct"] = True

                questions.append({
                    "item_format": "SINGLE_CHOICE",
                    "stem": stem,
                    "options": options,
                    "explanation": explanation,
                    "cognitive_level": "RECOGNITION",
                    "learning_outcome_code": "TOAN12.GT.01"
                })
                continue

            # B. Check for \choiceTF
            tf_match = re.search(r'\\choiceTF(?:\[[^\]]*\])?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', main_block)
            if tf_match:
                stem = main_block[:tf_match.start()].strip()
                im_match = re.match(r'\\immini(?:L)?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', stem)
                if im_match:
                    stem = im_match.group(1).strip() + "\n" + im_match.group(2).strip()

                sub_statements = []
                for idx, lbl in enumerate(["a", "b", "c", "d"]):
                    raw_sub = tf_match.group(idx + 1).strip()
                    is_true = r"\True" in raw_sub
                    clean_sub = re.sub(r'\\True\s*', '', raw_sub).strip()
                    clean_sub = re.sub(r'^[a-d]\)\s*', '', clean_sub).strip()
                    sub_statements.append({
                        "label": lbl,
                        "content": clean_sub,
                        "is_true": is_true,
                        "explanation": ""
                    })
                questions.append({
                    "item_format": "TRUE_FALSE_GROUP",
                    "stem": stem,
                    "sub_statements": sub_statements,
                    "explanation": explanation,
                    "cognitive_level": "COMPREHENSION",
                    "learning_outcome_code": "TOAN12.GT.01"
                })
                continue

            # C. Check for \shortans or \SA
            sa_match = re.search(r'\\(?:shortans|SA)(?:\[[^\]]*\])?\{([^}]+)\}', main_block)
            if sa_match:
                sa_val = sa_match.group(1).strip()
                stem = re.sub(r'\\(?:shortans|SA)(?:\[[^\]]*\])?\{[^}]+\}', '', main_block).strip()
                im_match = re.match(r'\\immini(?:L)?\s*\{([\s\S]*?)\}\s*\{([\s\S]*?)\}', stem)
                if im_match:
                    stem = im_match.group(1).strip() + "\n" + im_match.group(2).strip()

                questions.append({
                    "item_format": "SHORT_ANSWER",
                    "stem": stem,
                    "short_answer_value": sa_val,
                    "tolerance": 0.0,
                    "explanation": explanation,
                    "cognitive_level": "APPLICATION",
                    "learning_outcome_code": "TOAN12.GT.01"
                })
                continue

            # D. Generic fallback
            questions.append({
                "item_format": "SHORT_ANSWER",
                "stem": main_block,
                "short_answer_value": "1",
                "tolerance": 0.0,
                "explanation": explanation,
                "cognitive_level": "APPLICATION",
                "learning_outcome_code": "TOAN12.GT.01"
            })
        return questions

    # 2. Classic \textbf{Câu X.} parsing
    blocks = re.split(r'(?=\\textbf\{Câu\s+\d+\.\})', latex_source)

    for block in blocks:
        block = block.strip()
        m_num = re.match(r'\\textbf\{Câu\s+(\d+)\.\}\s*([\s\S]*)', block)
        if not m_num:
            continue

        num_str = m_num.group(1)
        content = m_num.group(2).strip()

        # Check for multiple choice options: \textbf{A.} ... \textbf{B.} ...
        opt_matches = list(re.finditer(r'\\textbf\{([A-D])\.\}\s*([^\\]+)', content))
        if len(opt_matches) >= 4:
            stem = content[:opt_matches[0].start()].strip()
            options = []
            for om in opt_matches:
                lbl = om.group(1)
                opt_content = om.group(2).strip()
                options.append({
                    "label": lbl,
                    "content": opt_content,
                    "is_correct": lbl == "A",
                    "is_fixed": False
                })
            questions.append({
                "item_format": "SINGLE_CHOICE",
                "stem": stem,
                "options": options,
                "cognitive_level": "RECOGNITION",
                "learning_outcome_code": "TOAN12.GT.01"
            })
            continue

        # Check for True/False group: a) ... b) ... c) ... d)
        tf_matches = list(re.finditer(r'(?:^|\n)\s*([a-d])\)\s*([^\n]+)', content))
        if len(tf_matches) == 4:
            stem = content[:tf_matches[0].start()].strip()
            sub_statements = []
            for tm in tf_matches:
                lbl = tm.group(1)
                st_content = tm.group(2).strip()
                sub_statements.append({
                    "label": lbl,
                    "content": st_content,
                    "is_true": lbl in ("a", "c"),
                    "explanation": ""
                })
            questions.append({
                "item_format": "TRUE_FALSE_GROUP",
                "stem": stem,
                "sub_statements": sub_statements,
                "cognitive_level": "COMPREHENSION",
                "learning_outcome_code": "TOAN12.GT.01"
            })
            continue

        # Default to short answer
        questions.append({
            "item_format": "SHORT_ANSWER",
            "stem": content,
            "short_answer_value": "1",
            "tolerance": 0.0,
            "cognitive_level": "APPLICATION",
            "learning_outcome_code": "TOAN12.GT.01"
        })

    return questions