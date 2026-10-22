"""Quesy Exam Composer Service - Open-Prism LaTeX Workspace Backend.
Compiles raw or structured LaTeX exam source code into publication-grade PDFs
with authentic Computer Modern Unicode (CMU Serif) typography, MathJax vector equations,
and TikZ / tkz-tab vector diagrams via Headless Chromium.
"""

import hashlib
import logging
import re
import shutil
import subprocess
import time
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
    "circular_32_full_exam": {
        "title": "Đề thi Chuẩn Thông tư 32 (Định dạng 2025)",
        "description": "Đề thi đầy đủ 3 phần: Trắc nghiệm 4 lựa chọn, Đúng/Sai 4 ý (QĐ 764), và Trả lời ngắn.",
        "latex": r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}

\begin{document}

\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\textbf{Câu 1.} Cho hàm số bậc ba $y = f(x)$ liên tục trên $\mathbb{R}$ có đồ thị như hình vẽ:
\begin{tikzpicture}[scale=0.65, >=stealth]
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

Hàm số đã cho nghịch biến trên khoảng nào dưới đây?

\textbf{A.} $(-\infty; -1)$ \qquad \textbf{B.} $(-1; 2)$ \qquad \textbf{C.} $(2; +\infty)$ \qquad \textbf{D.} $(-\infty; 2)$

\textbf{Câu 2.} Cho hàm số $y = f(x)$ có bảng biến thiên như sau:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}

Điểm cực đại của đồ thị hàm số là:

\textbf{A.} $(1; -1)$ \qquad \textbf{B.} $(-2; 4)$ \qquad \textbf{C.} $(-2; -1)$ \qquad \textbf{D.} $(1; 4)$

\section*{PHẦN II. Câu trắc nghiệm Đúng/Sai}
\textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\textbf{Câu 1.} Cho hàm số bậc ba $y = f(x) = ax^3 + bx^2 + cx + d$ ($a \neq 0$). Xét tính Đúng/Sai của các khẳng định sau:

a) Đồ thị hàm số bậc ba luôn có tâm đối xứng là điểm uốn.

b) Nếu hàm số có hai điểm cực trị thì tích các giá trị cực trị luôn âm.

c) Hàm số luôn có đạo hàm cấp hai liên tục trên $\mathbb{R}$.

d) Điểm cực trị của hàm số là nghiệm của phương trình $f'(x) = 0$.

\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}
\textit{Thí sinh trả lời từ câu 1 đến câu 6.}

\textbf{Câu 1.} Cho hàm số $f(x) = \ln(x^2 - 2x + 5)$. Giá trị nhỏ nhất của hàm số trên $\mathbb{R}$ bằng bao nhiêu?

\end{document}
"""
    },
    "variation_table_calculus": {
        "title": "Chuyên đề Bảng Biến Thiên & Cực Trị (tkz-tab)",
        "description": "Các dạng bảng biến thiên hàm bậc 3, hàm bậc 4, và hàm phân thức có tiệm cận đứng.",
        "latex": r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}

\begin{document}

\section*{BÀI TẬP KHẢO SÁT HÀM SỐ QUA BẢNG BIẾN THIÊN}

\textbf{Câu 1.} Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.2,deltacl=0.6]
  {$x$/.6, $y'$/.6, $y$/2}
  {$-\infty$,$-1$,$0$,$1$,$+\infty$}
  \tkzTabLine{,-,$0$,+,$0$,-,$0$,+,}
  \tkzTabVar{+/ $+\infty$, -/$-5$, +/$2$, -/$-5$, +/$+\infty$}
\end{tikzpicture}

Tìm số điểm cực trị của hàm số đã cho.

\textbf{A.} $1$ \qquad \textbf{B.} $2$ \qquad \textbf{C.} $3$ \qquad \textbf{D.} $4$

\textbf{Câu 2.} Cho hàm số phân thức $y = \dfrac{ax+b}{cx+d}$ có bảng biến thiên:
\begin{tikzpicture}
  \tikzset{double style/.append style = {double distance=2.5pt}}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.4]
  {$x$/.6, $y'$/.6, $y$/2}
  {$-\infty$,$1$,$+\infty$}
  \tkzTabLine{,+,d,+,}
  \tkzTabVar{-/$2$, +D-/$+\infty$/$-\infty$, +/$2$}
\end{tikzpicture}

Phương trình đường tiệm cận đứng và tiệm cận ngang của đồ thị hàm số lần lượt là:

\textbf{A.} $x = 1, y = 2$ \qquad \textbf{B.} $x = 2, y = 1$ \qquad \textbf{C.} $x = -1, y = 2$ \qquad \textbf{D.} $x = 1, y = -2$

\end{document}
"""
    },
    "geometry_3d": {
        "title": "Chuyên đề Hình Học Không Gian (TikZ 3D)",
        "description": "Mẫu bài tập hình học không gian với khối đa diện, hình chóp, và hệ trục Oxyz.",
        "latex": r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\usepackage{amsmath,amssymb}
\usepackage{tikz}

\begin{document}

\section*{BÀI TẬP HÌNH HỌC KHÔNG GIAN CỔ ĐIỂN & OXYZ}

\textbf{Câu 1.} Cho hình chóp $S.ABCD$ có đáy $ABCD$ là hình vuông cạnh $a$, cạnh bên $SA$ vuông góc với mặt phẳng đáy $(ABCD)$ và $SA = a\sqrt{2}$.

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

Tính thể tích của khối chóp $S.ABCD$.

\textbf{A.} $V = \dfrac{a^3\sqrt{2}}{3}$ \qquad \textbf{B.} $V = a^3\sqrt{2}$ \qquad \textbf{C.} $V = \dfrac{a^3\sqrt{2}}{6}$ \qquad \textbf{D.} $V = \dfrac{a^3}{3}$

\end{document}
"""
    },
    "blank_document": {
        "title": "Tài Liệu Mới (Văn Bản Trống)",
        "description": "Mẫu tài liệu khởi tạo sạch sẽ với header cơ bản.",
        "latex": r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}

\begin{document}

\section*{TIÊU ĐỀ BÀI KIỂM TRA}
\textit{Họ và tên: .................................................... Lớp: ................}

\textbf{Câu 1.} Soạn thảo nội dung câu hỏi đầu tiên tại đây...

\end{document}
"""
    }
}


# ---------------------------------------------------------------------------
# 2. LaTeX to HTML Compilation Parser
# ---------------------------------------------------------------------------

def compile_latex_source_to_html(latex_source: str, default_title: str = "Đề Thi Soạn Thảo LaTeX") -> str:
    """Converts general LaTeX or exam code into publication-grade HTML with CMU Serif,
    MathJax vector equations, and TikZ/tkz-tab vector SVGs for Chromium PDF compilation.
    """
    raw = latex_source.strip()
    if not raw:
        raw = TEMPLATES["blank_document"]["latex"]

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
    body = re.sub(r'\\begin\{document\}', '', body)
    body = re.sub(r'\\end\{document\}', '', body)

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

    # 6. Parse sections and structure
    body = re.sub(r'\\section\*?\{([^}]+)\}', r'<h2 class="latex-section">\1</h2>', body)
    body = re.sub(r'\\subsection\*?\{([^}]+)\}', r'<h3 class="latex-subsection">\1</h3>', body)

    # 7. Convert paragraphs
    paragraphs = re.split(r'\n\s*\n', body)
    rendered_paragraphs = []

    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if any(p.startswith(prefix) for prefix in ("__LATEX_TIKZ_COMPILED_", "__LATEX_TABLE_COMPILED_", "<h2", "<h3")):
            rendered_paragraphs.append(p)
            continue

        # Render math in this paragraph
        p_html = render_math_html(p)
        rendered_paragraphs.append(f'<div class="latex-p">{p_html}</div>')

    final_body = "\n".join(rendered_paragraphs)

    # Restore TikZ and Tables
    for idx, svg_html in enumerate(tikz_blocks):
        final_body = final_body.replace(f"__LATEX_TIKZ_COMPILED_{idx}__", svg_html)
    for idx, tbl_html in enumerate(table_blocks):
        final_body = final_body.replace(f"__LATEX_TABLE_COMPILED_{idx}__", tbl_html)

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
      text-transform: uppercase;
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
# 3. PDF Compilation Execution
# ---------------------------------------------------------------------------

def compile_latex_to_pdf(
    latex_source: str,
    output_pdf: Path,
    title: str = "Tài Liệu Soạn Thảo"
) -> Tuple[bool, str, int]:
    """Compiles LaTeX source code to vector-crisp PDF via Headless Chromium.
    Returns (success, error_message, elapsed_ms).
    """
    start_time = time.perf_counter()
    output_pdf = Path(output_pdf).resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temp_html = output_pdf.with_suffix(".temp.html")

    try:
        html = compile_latex_source_to_html(latex_source, default_title=title)
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


# ---------------------------------------------------------------------------
# 4. Extract Questions from LaTeX to Quesy Bank Schema
# ---------------------------------------------------------------------------

def extract_questions_from_latex(latex_source: str) -> List[Dict[str, Any]]:
    """Parses questions from LaTeX text into Quesy Question Bank format."""
    questions: List[Dict[str, Any]] = []
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
