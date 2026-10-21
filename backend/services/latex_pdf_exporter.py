"""LaTeX-grade High-Fidelity PDF Exporter for Quesy Examination System.

Adheres strictly to Vietnamese Ministry of Education standards:
- Circular 32/2018/TT-BGDDT & Decision 764/QD-BGDDT format.
- Computer Modern Unicode (CMU Serif) typography - the authentic LaTeX aesthetic.
- Persistent MathJax vector SVG rendering (no raster artifacts, perfect baseline alignment).
- Eliminates awkward spacing before punctuation (. , ; : ! ?).
- Adaptive option columns (4-col / 2-col / 1-col), native HTML table conversion for data/variation arrays.
- High-resolution PDF generation via Headless Chrome / Edge print-to-pdf.
"""

import os
import re
import json
import base64
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config import BASE_DIR, EXPORTS_DIR
from backend.services.mathjax_service import render_mathjax_equation

logger = logging.getLogger("quesy.latex_pdf_exporter")

FONTS_DIR = BASE_DIR / "frontend" / "static" / "fonts" / "cmu-serif"

# Browser Executable Discovery
BROWSER_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

_CACHED_FONT_CSS: Optional[str] = None


def get_cmu_font_css() -> str:
    """Returns CSS @font-face rules with embedded Base64 CMU Serif fonts for 100% offline rendering."""
    global _CACHED_FONT_CSS
    if _CACHED_FONT_CSS is not None:
        return _CACHED_FONT_CSS

    roman_p = FONTS_DIR / "cmu-serif-500-roman.ttf"
    bold_p = FONTS_DIR / "cmu-serif-700-roman.ttf"
    italic_p = FONTS_DIR / "cmu-serif-500-italic.ttf"

    if roman_p.exists() and bold_p.exists() and italic_p.exists():
        try:
            b64_roman = base64.b64encode(roman_p.read_bytes()).decode("ascii")
            b64_bold = base64.b64encode(bold_p.read_bytes()).decode("ascii")
            b64_italic = base64.b64encode(italic_p.read_bytes()).decode("ascii")

            _CACHED_FONT_CSS = f"""
@font-face {{
  font-family: 'CMU Serif';
  src: url('data:font/ttf;base64,{b64_roman}') format('truetype');
  font-weight: normal;
  font-weight: 500;
  font-style: normal;
}}
@font-face {{
  font-family: 'CMU Serif';
  src: url('data:font/ttf;base64,{b64_bold}') format('truetype');
  font-weight: bold;
  font-weight: 700;
  font-style: normal;
}}
@font-face {{
  font-family: 'CMU Serif';
  src: url('data:font/ttf;base64,{b64_italic}') format('truetype');
  font-weight: normal;
  font-weight: 500;
  font-style: italic;
}}
"""
            return _CACHED_FONT_CSS
        except Exception as e:
            logger.warning(f"Could not load embedded CMU Serif base64 fonts: {e}")

    # Fallback to local file URLs or web fonts
    _CACHED_FONT_CSS = """
@import url('https://fonts.cdnfonts.com/css/latin-modern-roman');
"""
    return _CACHED_FONT_CSS


def find_browser_executable() -> Optional[Path]:
    """Finds available Edge or Chrome executable for headless PDF generation."""
    for p in BROWSER_CANDIDATES:
        if p.exists():
            return p
    return None


def latex_to_inline_svg(latex_str: str, has_trailing_punctuation: bool = False) -> str:
    """Converts a single LaTeX expression to inline MathJax SVG with baseline depth alignment."""
    cleaned = (latex_str or "").strip()
    if cleaned.startswith("${") and cleaned.endswith("}$"):
        cleaned = cleaned[2:-2].strip()
    elif cleaned.startswith("$$") and cleaned.endswith("$$"):
        cleaned = cleaned[2:-2].strip()
    elif cleaned.startswith("$") and cleaned.endswith("$"):
        cleaned = cleaned[1:-1].strip()

    # Promote fraction to dfrac for clear, legible exam fractions
    cleaned = re.sub(r'\\frac\b', r'\\dfrac', cleaned)

    res = render_mathjax_equation(cleaned)
    if not res or not res.get("svg"):
        return f"<code>{latex_str}</code>"

    svg = res.get("svg", "")

    # Let MathJax own native vertical-align (in ex) on the svg element align perfectly with text baseline.
    # Tight right margin if followed by punctuation to prevent floating periods/commas.
    right_margin = "0" if has_trailing_punctuation else "1.5px"
    margin_style = f"margin: 0 {right_margin} 0 1px;"

    return f'<span class="math-svg" style="display:inline; {margin_style}">{svg}</span>'


def render_math_html(text: str) -> str:
    """Parses text containing math delimiters and replaces with inline vector SVGs,
    strictly eliminating extra whitespace before punctuation (. , ; : ! ?).
    """
    if not text:
        return ""

    raw = text.strip()
    while (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        raw = raw[1:-1].strip()

    # Normalize merged math expressions: ${\left(A\right)}, {\left(B\right)}$
    raw = re.sub(r"(?<!\\)\}\s*,\s*\{", r"}$, ${", raw)

    # Strip space before punctuation after math token: "${...} ." -> "${...}."
    raw = re.sub(r'(\$\{[^}]*\}\$|\$[^$]*\$)\s+([.,;:!?])', r'\1\2', raw)

    tokens = re.split(r"(\$\$\{.*?\}\$\$|\$\$.*?\$\$|\$\\{.*?\\\}\$|\$\{.*?\}\$|\$.*?\$)", raw, flags=re.DOTALL)
    out = []

    for i, tok in enumerate(tokens):
        if not tok:
            continue
        stripped = tok.strip()
        is_math = (
            (stripped.startswith("${") and stripped.endswith("}$"))
            or (stripped.startswith("$$") and stripped.endswith("$$"))
            or (stripped.startswith("$") and stripped.endswith("$"))
        )
        if is_math and len(stripped) > 2:
            # Check if next token starts with punctuation
            has_next_punct = False
            if i + 1 < len(tokens):
                next_tok = tokens[i + 1].lstrip()
                if next_tok and next_tok[0] in ".,;:!?":
                    has_next_punct = True
            out.append(latex_to_inline_svg(stripped, has_trailing_punctuation=has_next_punct))
        else:
            cleaned_text = tok.replace("<", "&lt;").replace(">", "&gt;")
            out.append(cleaned_text)

    res = "".join(out)
    # Final cleanup of any lingering whitespace between math span and punctuation
    res = re.sub(r'</span>\s+([.,;:!\?)])', r'</span>\1', res)
    return res


def convert_latex_table_to_html(table_latex: str) -> str:
    """Converts a LaTeX array or tabular environment into a clean, bordered HTML table."""
    body_match = re.search(r'\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|tabular)\}', table_latex, re.DOTALL)
    if not body_match:
        return ""

    body = body_match.group(1).strip()
    lines = body.split(r"\\")
    rows_html = []

    for line in lines:
        cleaned_line = line.replace(r"\hline", "").strip()
        if not cleaned_line:
            continue
        cells = [c.strip() for c in cleaned_line.split("&")]
        cells_html = []
        for cell in cells:
            if cell.startswith(r"\text{") and cell.endswith("}"):
                c_content = cell[6:-1].strip()
            elif not cell.startswith("$"):
                c_content = f"${cell}$"
            else:
                c_content = cell
            rendered_cell = render_math_html(c_content)
            cells_html.append(f"<td>{rendered_cell}</td>")
        rows_html.append(f"<tr>{''.join(cells_html)}</tr>")

    if not rows_html:
        return ""

    return f"""
    <table class="exam-table">
      {''.join(rows_html)}
    </table>
    """


def generate_digitized_exam_latex_pdf(
    questions: List[Dict[str, Any]],
    output_pdf: Path,
    title: str = "ĐỀ THI KHẢO THÍ",
    school_name: str = "SỞ GIÁO DỤC VÀ ĐÀO TẠO",
    subject_name: str = "Toán học",
    grade: str = "12",
    variant_code: str = "101",
    duration: int = 90
) -> bool:
    """Generates an official high-fidelity print-ready PDF for digitized questions
    strictly adopting authentic LaTeX font typography (CMU Serif) and MathJax vector equations.
    """
    output_pdf = Path(output_pdf).resolve()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temp_html = output_pdf.with_suffix(".temp.html")

    font_css = get_cmu_font_css()

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>{title} - Mã đề {variant_code}</title>
  <style>
    {font_css}

    @page {{
      size: A4 portrait;
      margin: 16mm 16mm 16mm 16mm;
      @bottom-right {{
        content: "Trang " counter(page) " - Mã đề thi " "{variant_code}";
        font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif;
        font-size: 9pt;
      }}
    }}

    body {{
      font-family: 'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif;
      font-size: 11pt;
      line-height: 1.45;
      color: #000;
      margin: 0;
      padding: 0;
      background: #fff;
      -webkit-font-smoothing: subpixel-antialiased;
    }}

    .header-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 8px;
    }}
    .header-table td {{
      vertical-align: top;
      text-align: center;
    }}
    .school-col {{
      width: 45%;
    }}
    .school-title {{
      font-size: 10.5pt;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .school-name {{
      font-size: 11pt;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .exam-col {{
      width: 55%;
    }}
    .exam-main-title {{
      font-size: 11.5pt;
      font-weight: bold;
      text-transform: uppercase;
    }}
    .exam-sub {{
      font-size: 10.5pt;
      font-style: italic;
    }}
    .variant-badge {{
      display: inline-block;
      border: 1.5px solid #000;
      padding: 1px 8px;
      font-weight: bold;
      font-size: 10.5pt;
      margin-top: 4px;
    }}
    .divider-line {{
      width: 50%;
      height: 1px;
      background: #000;
      margin: 4px auto 0 auto;
    }}

    /* Compact 3-column student info table strictly preventing line wraps */
    .student-table {{
      width: 100%;
      border: 1px solid #333;
      border-collapse: collapse;
      margin-top: 6px;
      margin-bottom: 12px;
      font-size: 9.5pt;
      background: #fafafa;
    }}
    .student-table td {{
      padding: 4px 8px;
      vertical-align: middle;
      white-space: nowrap;
    }}

    .section-banner {{
      font-size: 11pt;
      font-weight: bold;
      margin-top: 12px;
      margin-bottom: 6px;
      text-align: left;
      break-after: avoid;
    }}

    .question-block {{
      margin-bottom: 8px;
      page-break-inside: avoid;
    }}
    .question-stem {{
      text-align: left;
      margin-bottom: 3px;
      word-spacing: normal;
    }}
    .question-number {{
      font-weight: bold;
    }}

    .tf-sub-item {{
      margin-left: 20px;
      margin-bottom: 3px;
      text-align: left;
      word-spacing: normal;
    }}
    .tf-label {{
      font-weight: bold;
    }}

    .options-grid-4 {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 3px 8px;
      margin-left: 15px;
      margin-top: 4px;
    }}
    .options-grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 3px 12px;
      margin-left: 15px;
      margin-top: 4px;
    }}
    .options-grid-1 {{
      margin-left: 15px;
      margin-top: 4px;
    }}
    .option-item {{
      text-align: justify;
    }}
    .option-label {{
      font-weight: bold;
    }}

    .exam-table {{
      margin: 8px auto;
      border-collapse: collapse;
      border: 1px solid #000;
      page-break-inside: avoid;
    }}
    .exam-table td, .exam-table th {{
      border: 0.8px solid #000;
      padding: 4px 10px;
      text-align: center;
      font-size: 10.5pt;
    }}

    .tikz-container {{
      text-align: center;
      margin: 6px 0;
      page-break-inside: avoid;
    }}
    .tikz-container img {{
      max-width: 55%;
      height: auto;
    }}

    .footer-end {{
      text-align: center;
      font-weight: bold;
      margin-top: 20px;
      font-size: 11pt;
      letter-spacing: 2px;
      break-inside: avoid;
    }}
    .footer-note {{
      text-align: center;
      font-style: italic;
      font-size: 10pt;
      margin-top: 4px;
      break-inside: avoid;
    }}

    .math-svg svg {{
      height: 100% !important;
      display: inline !important;
      overflow: visible !important;
    }}
  </style>
</head>
<body>
  <table class="header-table">
    <tr>
      <td class="school-col">
        <div class="school-title">{school_name}</div>
        <div class="school-name">TRƯỜNG THPT CHUYÊN</div>
        <div style="font-size: 9.5pt; font-style: italic; margin-top: 2px;">(Đề thi có 02 trang)</div>
        <div class="divider-line"></div>
      </td>
      <td class="exam-col">
        <div class="exam-main-title">{title}</div>
        <div style="font-weight: bold; font-size: 11pt;">Bài thi: {subject_name.upper()} - KHỐI {grade}</div>
        <div class="exam-sub">Thời gian làm bài: {duration} phút (không kể thời gian phát đề)</div>
        <div class="variant-badge">MÃ ĐỀ THI: {variant_code}</div>
      </td>
    </tr>
  </table>

  <table class="student-table">
    <tr>
      <td style="width: 52%; text-align: left;">
        Họ và tên thí sinh: ....................................................
      </td>
      <td style="width: 26%; text-align: center;">
        Số báo danh: ....................
      </td>
      <td style="width: 22%; text-align: right;">
        Phòng thi: ............
      </td>
    </tr>
  </table>
"""

    section_titles = {
        1: "PHẦN I. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.",
        2: "PHẦN II. Thí sinh trả lời từ câu 1 đến 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.",
        3: "PHẦN III. Thí sinh trả lời từ câu 1 đến câu 6. Câu trắc nghiệm trả lời ngắn.",
        4: "PHẦN IV. Tự luận."
    }

    current_sec = None

    for idx, q in enumerate(questions):
        fmt = q.get("item_format", "SINGLE_CHOICE")
        if fmt == "SINGLE_CHOICE":
            sec = 1
        elif fmt == "TRUE_FALSE_GROUP":
            sec = 2
        elif fmt == "SHORT_ANSWER":
            sec = 3
        else:
            sec = 4

        if sec != current_sec:
            current_sec = sec
            html_content += f'<div class="section-banner">{section_titles.get(sec, f"PHẦN {sec}.")}</div>\n'

        stem = q.get("stem", "")

        # Check for TikZ diagram
        tikz_match = re.search(r'\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}', stem)
        # Check for LaTeX table array
        table_match = re.search(r'(\\$\$)?\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|tabular)\}(\\$\$)?', stem, re.DOTALL)

        html_content += f'<div class="question-block">\n'

        if tikz_match:
            tikz_code = tikz_match.group(0)
            pre_text = stem[:tikz_match.start()].strip()
            post_text = stem[tikz_match.end():].strip()

            html_content += f'<div class="question-stem"><span class="question-number">Câu {idx + 1}.</span> {render_math_html(pre_text)}</div>\n'

            try:
                from backend.services.tikz_renderer import render_tikz_to_png
                png_res = render_tikz_to_png(tikz_code)
                if png_res.get("success") and png_res.get("png_path"):
                    png_p = Path(png_res["png_path"]).resolve()
                    img_url = f"file:///{str(png_p).replace(os.sep, '/')}"
                    html_content += f'<div class="tikz-container"><img src="{img_url}" alt="Diagram"/></div>\n'
            except Exception as tikz_err:
                logger.warning(f"Could not render TikZ diagram: {tikz_err}")

            if post_text:
                html_content += f'<div class="question-stem">{render_math_html(post_text)}</div>\n'

        elif table_match:
            pre_text = stem[:table_match.start()].strip()
            post_text = stem[table_match.end():].strip()
            table_latex = table_match.group(0)

            html_content += f'<div class="question-stem"><span class="question-number">Câu {idx + 1}.</span> {render_math_html(pre_text)}</div>\n'
            html_content += convert_latex_table_to_html(table_latex)

            if post_text:
                html_content += f'<div class="question-stem">{render_math_html(post_text)}</div>\n'

        else:
            html_content += f'<div class="question-stem"><span class="question-number">Câu {idx + 1}.</span> {render_math_html(stem)}</div>\n'

        # Options / Sub-statements
        if fmt == "SINGLE_CHOICE":
            options = q.get("options", [])
            max_len = max([len(o.get("content", "")) for o in options], default=0) if options else 0

            grid_class = "options-grid-4" if max_len <= 32 else ("options-grid-2" if max_len <= 68 else "options-grid-1")
            html_content += f'<div class="{grid_class}">\n'
            for opt in options:
                opt_html = render_math_html(opt.get("content", ""))
                html_content += f'  <div class="option-item"><span class="option-label">{opt.get("label")}.</span> {opt_html}</div>\n'
            html_content += '</div>\n'

        elif fmt == "TRUE_FALSE_GROUP":
            for sub in q.get("sub_statements", []):
                sub_html = render_math_html(sub.get("content", ""))
                html_content += f'  <div class="tf-sub-item"><span class="tf-label">{sub.get("label")})</span> {sub_html}</div>\n'

        elif fmt == "SHORT_ANSWER":
            html_content += '  <div style="margin-left: 20px; font-style: italic; margin-top: 3px;">Đáp số: ................................................................</div>\n'

        html_content += '</div>\n'

    html_content += """
  <div class="footer-end">---------- HẾT ----------</div>
  <div class="footer-note">Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.</div>
</body>
</html>
"""

    temp_html.write_text(html_content, encoding="utf-8")

    browser = find_browser_executable()
    if not browser:
        logger.error("No compatible browser (Chrome or Edge) found for PDF export.")
        return False

    try:
        cmd = [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            f"--print-to-pdf={str(output_pdf)}",
            f"file:///{str(temp_html).replace(os.sep, '/')}"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        success = output_pdf.exists() and output_pdf.stat().st_size > 1000
        return success
    except Exception as e:
        logger.error(f"Failed to generate LaTeX-grade PDF via browser: {e}")
        return False
    finally:
        if temp_html.exists():
            try:
                temp_html.unlink()
            except Exception:
                pass
