import os
import io
import re
import sys
import shutil
import zipfile
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

from sqlalchemy.orm import Session
from backend.models import MasterExam, ExamVariant, Question, ExamVariantItem
from backend.services.composer_service import compile_latex_to_pdf
from backend.services.latex_converter import sanitize_latex_for_xetex

logger = logging.getLogger("quesy.docx_exporter")

STORAGE_EXPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "exports"
STORAGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

STORAGE_MATH_CACHE = Path(__file__).resolve().parent.parent.parent / "storage" / "math_cache"
STORAGE_MATH_CACHE.mkdir(parents=True, exist_ok=True)




def clean_math_expr(text: str) -> str:
    """Strips math delimiters ($...$, $$...$$, ${...}$, $${...}$$) and single outer enclosing braces."""
    if not text:
        return ""
    s = text.strip()
    # Strip any enclosing single or double quotes (e.g. "'${...}'")
    while (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    if s.startswith("${") and s.endswith("}$"):
        s = s[2:-2].strip()
    elif s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    while s.startswith("{") and s.endswith("}"):
        depth = 0
        is_enclosing = True
        for idx, ch in enumerate(s):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and idx < len(s) - 1:
                    is_enclosing = False
                    break
        if is_enclosing and depth == 0:
            s = s[1:-1].strip()
        else:
            break
    # Promote \frac to \dfrac for full-size professional math exam display
    s = re.sub(r"(?<![a-zA-Z\\])\\frac(?![a-zA-Z])", r"\\dfrac", s)
    return s


# ---------------------------------------------------------------------------
# PDF Conversion & Multi-format Export (3-Tier Resilient Engine)
# ---------------------------------------------------------------------------

logger = logging.getLogger("quesy.docx_exporter")

EDGE_BROWSER_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]


def find_browser_executable() -> Optional[Path]:
    """Finds available Edge or Chrome or Chromium executable cross-platform (Windows, Linux, macOS)."""
    # 1. System PATH lookup (Linux, macOS, standard Windows PATH)
    for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge", "edge"]:
        found = shutil.which(name)
        if found:
            return Path(found)

    # 2. Linux standard locations
    linux_paths = [
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/snap/bin/chromium"),
    ]
    for p in linux_paths:
        if p.exists():
            return p

    # 3. Windows standard locations
    windows_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in windows_paths:
        if p.exists():
            return p

    # 4. macOS standard locations
    mac_paths = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    for p in mac_paths:
        if p.exists():
            return p

    return None


def convert_html_to_pdf_browser(html_path: Path, pdf_path: Path) -> bool:
    """Renders HTML directly into high-fidelity vector PDF via headless Edge or Chrome."""
    browser_exe = find_browser_executable()
    if not browser_exe:
        return False
    try:
        cmd = [
            str(browser_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-pdf-header-footer",
            f"--print-to-pdf={str(pdf_path.resolve())}",
            html_path.resolve().as_uri()
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=12)
        return pdf_path.exists() and pdf_path.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"Browser HTML-to-PDF conversion failed: {e}")
        return False


def generate_variant_html(v: ExamVariant, output_html: Path) -> Path:
    """Generates an official Vietnamese Examination 2-column HTML layout."""
    master = v.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"
    exam_title = master.title if master else "KỲ THI TỐT NGHIỆP THPT NĂM 2025"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Mã đề {v.variant_code}</title>
  <style>
    @page {{ size: A4; margin: 15mm 15mm 15mm 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.45; color: #111; margin: 0; padding: 0; }}
    .header-table {{ width: 100%; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px; border-collapse: collapse; }}
    .header-table td {{ vertical-align: top; }}
    .school {{ text-align: center; font-weight: bold; font-size: 11pt; width: 45%; }}
    .exam-info {{ text-align: center; font-size: 11pt; width: 55%; }}
    .exam-title {{ font-weight: bold; font-size: 12pt; text-transform: uppercase; }}
    .variant-box {{ display: inline-block; border: 2px solid #000; padding: 3px 12px; font-weight: bold; font-size: 13pt; margin-top: 5px; }}
    .student-box {{ width: 100%; border: 1px solid #444; margin-bottom: 15px; padding: 6px 12px; font-size: 10pt; background: #fafafa; }}
    .columns {{ column-count: 2; column-gap: 24px; column-rule: 0.5px solid #bbb; text-align: justify; }}
    .section-title {{ font-weight: bold; font-size: 11pt; margin-top: 10px; margin-bottom: 6px; text-transform: uppercase; color: #002244; break-after: avoid; }}
    .question {{ margin-bottom: 14px; break-inside: avoid; }}
    .q-stem {{ font-weight: 500; margin-bottom: 4px; }}
    .options-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; margin-left: 10px; margin-top: 4px; }}
    .tf-sub {{ margin-left: 10px; margin-top: 3px; }}
    .footer-note {{ text-align: center; font-style: italic; margin-top: 25px; border-top: 1px dashed #888; padding-top: 8px; font-size: 10pt; }}
  </style>
</head>
<body>
  <table class="header-table">
    <tr>
      <td class="school">
        SỞ GIÁO DỤC VÀ ĐÀO TẠO<br>
        <b>TRƯỜNG THPT CHUYÊN</b><br>
        <i>(Đề thi gồm có 02 trang)</i>
      </td>
      <td class="exam-info">
        <div class="exam-title">{exam_title}</div>
        <div><b>BÀI THI: {subject_name.upper()}</b></div>
        <div><i>Thời gian làm bài: 90 phút (không kể thời gian phát đề)</i></div>
        <div class="variant-box">MÃ ĐỀ: {v.variant_code}</div>
      </td>
    </tr>
  </table>

  <div class="student-box">
    Họ và tên thí sinh: ............................................................................ Số báo danh: ..................... Phách: .....................
  </div>

  <div class="columns">
"""

    items = sorted(v.items, key=lambda x: x.variant_order_index)
    curr_sec = None
    for it in items:
        q = it.question
        if not q:
            continue
        if q.item_format == "SINGLE_CHOICE" and curr_sec != 1:
            html += '<div class="section-title">PHẦN I. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.</div>'
            curr_sec = 1
        elif q.item_format == "TRUE_FALSE_GROUP" and curr_sec != 2:
            html += '<div class="section-title">PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 4.</div>'
            curr_sec = 2
        elif q.item_format == "SHORT_ANSWER" and curr_sec != 3:
            html += '<div class="section-title">PHẦN III. Câu trắc nghiệm trả lời ngắn.</div>'
            curr_sec = 3

        clean_stem = q.stem.replace("<", "&lt;").replace(">", "&gt;")
        html += f'<div class="question"><div class="q-stem"><b>Câu {it.variant_order_index}:</b> {clean_stem}</div>'

        if q.item_format == "SINGLE_CHOICE":
            html += '<div class="options-grid">'
            mapping = json.loads(it.option_mapping) if (it.option_mapping and isinstance(it.option_mapping, str)) else (it.option_mapping or {})
            if mapping:
                for lbl in ["A", "B", "C", "D"]:
                    if lbl in mapping:
                        orig = mapping[lbl]
                        orig_opt = next((o for o in q.options if o.label == orig), None)
                        txt = orig_opt.content if orig_opt else mapping[lbl]
                        clean_opt = txt.replace("<", "&lt;").replace(">", "&gt;")
                        html += f'<div><b>{lbl}.</b> {clean_opt}</div>'
            elif q.options:
                for o in q.options:
                    clean_opt = o.content.replace("<", "&lt;").replace(">", "&gt;")
                    html += f'<div><b>{o.label}.</b> {clean_opt}</div>'
            html += '</div>'
        elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
            for sub in q.sub_statements:
                clean_sub = sub.content.replace("<", "&lt;").replace(">", "&gt;")
                html += f'<div class="tf-sub"><b>{sub.label})</b> {clean_sub}</div>'
        elif q.item_format == "SHORT_ANSWER":
            html += '<div style="margin-left: 10px; font-style: italic; color: #555;">Đáp số: ....................................................</div>'

        html += '</div>'

    html += """
  </div>
  <div class="footer-note">--- HẾT ---<br>Cán bộ coi thi không giải thích gì thêm.</div>
</body>
</html>"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def generate_solution_html(v: ExamVariant, output_html: Path) -> Path:
    """Generates clean HTML for detailed solutions."""
    master = v.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Lời giải Mã đề {v.variant_code}</title>
  <style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; color: #111; }}
    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px; }}
    .title {{ font-size: 14pt; font-weight: bold; }}
    .subtitle {{ font-size: 11pt; font-style: italic; color: #444; }}
    .solution-item {{ margin-bottom: 15px; border-bottom: 1px dotted #ccc; padding-bottom: 10px; }}
    .q-title {{ font-weight: bold; color: #003366; }}
    .ans-key {{ font-weight: bold; color: #0066cc; margin: 4px 0; }}
    .explanation {{ margin-left: 12px; background: #f8fafc; padding: 6px 12px; border-left: 3px solid #3b82f6; }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title">HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ {v.variant_code}</div>
    <div class="subtitle">BÀI THI: {subject_name.upper()} • CHUẨN THÔNG TƯ 32/2018/TT-BGDĐT</div>
  </div>
"""

    items = sorted(v.items, key=lambda x: x.variant_order_index)
    for it in items:
        q = it.question
        if not q:
            continue
        clean_stem = q.stem.replace("<", "&lt;").replace(">", "&gt;")
        clean_exp = (q.explanation or "Đang cập nhật hướng dẫn giải.").replace("<", "&lt;").replace(">", "&gt;")
        html += f"""
  <div class="solution-item">
    <div class="q-title">Câu {it.variant_order_index}: {clean_stem}</div>
    <div class="ans-key">Đáp án chuẩn: {it.answer_key or 'A'}</div>
    <div class="explanation"><b>Lời giải chi tiết:</b><br>{clean_exp}</div>
  </div>
"""

    html += "</body></html>"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def generate_answer_sheet_html(master: MasterExam, variants: List[ExamVariant], output_html: Path) -> Path:
    """Generates clean HTML for answer key matrix."""
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Bảng Đáp Án Tổng Hợp</title>
  <style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; color: #111; }}
    .header {{ text-align: center; font-weight: bold; font-size: 13pt; margin-bottom: 12px; }}
    table {{ width: 100%; border-collapse: collapse; text-align: center; }}
    th, td {{ border: 1px solid #444; padding: 6px; }}
    th {{ background: #f1f5f9; }}
  </style>
</head>
<body>
  <div class="header">BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ THI</div>
  <table>
    <tr>
      <th>Câu</th>
      <th>Thể thức</th>
      {"".join([f"<th>Mã {v.variant_code}</th>" for v in variants])}
    </tr>
"""
    num_questions = master.total_questions
    for q_idx in range(1, num_questions + 1):
        m_item = next((it for it in master.items if it.order_index == q_idx), None)
        fmt = m_item.question.item_format if (m_item and m_item.question) else "SINGLE_CHOICE"
        html += f"<tr><td>{q_idx}</td><td>{fmt}</td>"
        for v in variants:
            v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
            ans = v_item.answer_key if v_item and v_item.answer_key else "-"
            html += f"<td><b>{ans}</b></td>"
        html += "</tr>"

    html += "</table></body></html>"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def register_vietnamese_fonts():
    """Registers true Times New Roman fonts for ReportLab Unicode rendering."""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        fonts_to_register = [
            ('TimesNewRoman', r'C:\Windows\Fonts\times.ttf'),
            ('TimesNewRoman-Bold', r'C:\Windows\Fonts\timesbd.ttf'),
            ('TimesNewRoman-Italic', r'C:\Windows\Fonts\timesi.ttf'),
        ]
        for name, p in fonts_to_register:
            if Path(p).exists() and name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, p))
    except Exception as e:
        logger.warning(f"Could not register system TTF fonts: {e}")


def generate_pdf_reportlab(variant: ExamVariant, output_pdf: Path) -> bool:
    """Ultra-fast pure Python PDF generator using ReportLab with Times New Roman Unicode."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        
        style_norm = ParagraphStyle('Norm', fontName=font_main, fontSize=11, leading=14)
        style_bold = ParagraphStyle('Bold', fontName=font_bold, fontSize=11, leading=14)
        style_center = ParagraphStyle('Center', fontName=font_bold, fontSize=12, leading=15, alignment=1)
        style_sec = ParagraphStyle('Sec', fontName=font_bold, fontSize=11, leading=15, textColor=colors.HexColor('#002244'))

        story = []
        master = variant.master_exam
        title = master.title if master else "KỲ THI TỐT NGHIỆP THPT"
        sub_name = master.subject.name if (master and master.subject) else "Toán học"

        header_data = [
            [
                Paragraph("<b>SỞ GIÁO DỤC VÀ ĐÀO TẠO</b><br/>TRƯỜNG THPT CHUYÊN", style_norm),
                Paragraph(f"<b>{title.upper()}</b><br/><b>MÔN: {sub_name.upper()} - MÃ ĐỀ: {variant.variant_code}</b>", style_center)
            ]
        ]
        t = Table(header_data, colWidths=[240, 280])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        curr_sec = None
        items = sorted(variant.items, key=lambda x: x.variant_order_index)
        for it in items:
            q = it.question
            if not q: continue
            
            if q.item_format == "SINGLE_CHOICE" and curr_sec != 1:
                story.append(Paragraph("<b>PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 1
            elif q.item_format == "TRUE_FALSE_GROUP" and curr_sec != 2:
                story.append(Paragraph("<b>PHẦN II. Câu trắc nghiệm đúng sai.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 2
            elif q.item_format == "SHORT_ANSWER" and curr_sec != 3:
                story.append(Paragraph("<b>PHẦN III. Câu trắc nghiệm trả lời ngắn.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 3

            clean_stem = q.stem.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Câu {it.variant_order_index}:</b> {clean_stem}", style_norm))
            story.append(Spacer(1, 4))
            
            if q.item_format == "SINGLE_CHOICE":
                mapping = json.loads(it.option_mapping) if (it.option_mapping and isinstance(it.option_mapping, str)) else (it.option_mapping or {})
                opts_rendered = []
                if mapping:
                    for lbl in ["A", "B", "C", "D"]:
                        if lbl in mapping:
                            orig = mapping[lbl]
                            orig_opt = next((o for o in q.options if o.label == orig), None)
                            txt = orig_opt.content if orig_opt else mapping[lbl]
                            clean_opt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            opts_rendered.append(Paragraph(f"<b>{lbl}.</b> {clean_opt}", style_norm))
                elif q.options:
                    for o in q.options:
                        clean_opt = o.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        opts_rendered.append(Paragraph(f"<b>{o.label}.</b> {clean_opt}", style_norm))
                if opts_rendered:
                    col_w = 520 / len(opts_rendered)
                    t_opts = Table([opts_rendered], colWidths=[col_w]*len(opts_rendered))
                    story.append(t_opts)
                    story.append(Spacer(1, 6))
            elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
                for sub in q.sub_statements:
                    clean_sub = sub.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{sub.label})</b> {clean_sub}", style_norm))
                story.append(Spacer(1, 6))
            elif q.item_format == "SHORT_ANSWER":
                story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<i>Đáp số: ....................................................</i>", style_norm))
                story.append(Spacer(1, 6))

        doc.build(story)
        return output_pdf.exists() and output_pdf.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"ReportLab generation failed: {e}")
        return False


def generate_variant_latex(variant: ExamVariant, is_solution: bool = False) -> str:
    items = sorted(variant.items, key=lambda x: x.variant_order_index)
    
    sec1 = [it for it in items if (it.question and it.question.item_format == "SINGLE_CHOICE")]
    sec2 = [it for it in items if (it.question and it.question.item_format == "TRUE_FALSE_GROUP")]
    sec3 = [it for it in items if (it.question and it.question.item_format == "SHORT_ANSWER")]
    
    if not sec1 and not sec2 and not sec3:
        sec1 = items

    n1 = len(sec1)
    n2 = len(sec2)
    n3 = len(sec3)

    exam_or_sol_title = r"\textbf{ĐỀ CHÍNH THỨC}" if not is_solution else r"\textbf{HƯỚNG DẪN GIẢI CHI TIẾT}"
    latex_lines = [
        r"\begin{minipage}[t]{0.38\textwidth}",
        r"  \centering",
        r"  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO}\\",
        r"  \textbf{TRƯỜNG THPT CHUYÊN}\\",
        rf"  {exam_or_sol_title}",
        r"\end{minipage}",
        r"\hfill",
        r"\begin{minipage}[t]{0.58\textwidth}",
        r"  \centering",
        r"  \textbf{KỲ THI TỐT NGHIỆP THPT}\\",
        r"  \textbf{MÔN TOÁN}\\",
        r"  \textit{Thời gian làm bài: 90 phút}",
        r"\end{minipage}",
        r"\vspace{0.25cm}",
        r"\noindent Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: " + str(variant.variant_code) + r"}}",
        r"\vspace{0.1cm}\noindent" + chr(92) + "rule{" + chr(92) + "textwidth}{0.5pt}" + chr(92) + "vspace{0.3cm}"
    ]

    if n1 > 0:
        latex_lines.append(rf"\noindent\textbf{{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n1}. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec1:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            stem = re.sub(r'^(?:Câu\s*\d+[\.:]?\s*)', '', stem)
            stem = sanitize_latex_for_xetex(stem)
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            
            mapping = it.option_mapping or {"A": "A", "B": "B", "C": "C", "D": "D"}
            opts = q.options or []
            choice_parts = []
            for lbl in ["A", "B", "C", "D"]:
                orig_lbl = mapping.get(lbl, lbl)
                opt_obj = next((o for o in opts if o.label == orig_lbl or o.label == lbl), None)
                content = opt_obj.content if opt_obj else f"Phương án {lbl}"
                content = re.sub(r'^[A-D]\)[\.\s]*', '', content)
                content = sanitize_latex_for_xetex(content)
                is_corr = opt_obj.is_correct if opt_obj else False
                prefix = r"\True " if is_corr else ""
                choice_parts.append(f"{prefix}{content}")
            
            if len(choice_parts) >= 4:
                latex_lines.append(rf"\choice{{{choice_parts[0]}}}{{{choice_parts[1]}}}{{{choice_parts[2]}}}{{{choice_parts[3]}}}")
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                exp = sanitize_latex_for_xetex(q.explanation or "Hướng dẫn giải chi tiết đang cập nhật.")
                latex_lines.append(exp)
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    if n2 > 0:
        latex_lines.append(r"\setcounter{ex}{0}")
        latex_lines.append(rf"\noindent\textbf{{PHẦN II. Câu trắc nghiệm đúng sai.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n2}. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec2:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            stem = re.sub(r'^(?:Câu\s*\d+[\.:]?\s*)', '', stem)
            stem = sanitize_latex_for_xetex(stem)
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            subs = q.sub_statements or []
            choice_tf_lines = [r"\choiceTF[1]"]
            for sub in subs:
                is_t = sub.is_true if hasattr(sub, 'is_true') else (sub.is_correct if hasattr(sub, 'is_correct') else True)
                prefix = r"\True " if is_t else ""
                content = sub.content or ""
                content = re.sub(r'^[a-d]\)\s*', '', content)
                content = sanitize_latex_for_xetex(content)
                choice_tf_lines.append(rf"{{{prefix}{content}}}")
            while len(choice_tf_lines) < 5:
                choice_tf_lines.append(r"{}")
            latex_lines.append("\n".join(choice_tf_lines))
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                latex_lines.append(r"\begin{itemchoice}")
                for sub in subs:
                    exp = sanitize_latex_for_xetex(sub.explanation or "Giải thích chi tiết.")
                    latex_lines.append(rf"\itemch {exp}")
                latex_lines.append(r"\end{itemchoice}")
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    if n3 > 0:
        latex_lines.append(r"\setcounter{ex}{0}")
        latex_lines.append(rf"\noindent\textbf{{PHẦN III. Câu trắc nghiệm trả lời ngắn.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n3}.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec3:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            stem = re.sub(r'^(?:Câu\s*\d+[\.:]?\s*)', '', stem)
            stem = sanitize_latex_for_xetex(stem)
            ans_key = sanitize_latex_for_xetex(it.answer_key or q.short_answer_key or "0")
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            latex_lines.append(rf"\shortans{{{ans_key}}}")
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                exp = sanitize_latex_for_xetex(q.explanation or f"Đáp số: {ans_key}")
                latex_lines.append(exp)
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    latex_lines.append(r"\vspace{1em}")
    latex_lines.append(r"\begin{center}\textbf{--- HẾT ---}\end{center}")
    return "\n".join(latex_lines)


def generate_variant_pdf(variant: ExamVariant, output_pdf: Path) -> bool:
    """Generates pure vector LaTeX PDF using Tectonic / Composer service."""
    try:
        latex_code = generate_variant_latex(variant, is_solution=False)
        success, err_msg, elapsed = compile_latex_to_pdf(
            latex_code, output_pdf, title=f"Đề Thi Mã {variant.variant_code}", mode="dethi"
        )
        if success and output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"LaTeX/Tectonic PDF generation failed: {e}")

    return generate_pdf_reportlab(variant, output_pdf)


def generate_solution_pdf(variant: ExamVariant, output_pdf: Path) -> bool:
    """Generates solution PDF using Tectonic XeTeX Engine via generate_variant_latex(is_solution=True)."""
    try:
        latex_code = generate_variant_latex(variant, is_solution=True)
        success, err_msg, elapsed = compile_latex_to_pdf(
            latex_code, output_pdf, title=f"Lời Giải Chi Tiết Mã {variant.variant_code}", mode="loigiai"
        )
        if success and output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"LaTeX/Tectonic solution PDF generation failed: {e}")

    try:
        return _legacy_generate_solution_pdf_reportlab(variant, output_pdf)
    except Exception:
        return False


def _legacy_generate_solution_pdf_reportlab(variant: ExamVariant, output_pdf: Path) -> bool:
    """Generates solution PDF using ultra-fast ReportLab with browser fallback."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        font_italic = 'TimesNewRoman-Italic' if 'TimesNewRoman-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

        style_norm = ParagraphStyle('Norm', fontName=font_main, fontSize=10.5, leading=14)
        style_bold = ParagraphStyle('Bold', fontName=font_bold, fontSize=10.5, leading=14)
        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=13, leading=16, alignment=1)
        style_sub = ParagraphStyle('Sub', fontName=font_italic, fontSize=10, leading=13, alignment=1)
        style_exp = ParagraphStyle('Exp', fontName=font_main, fontSize=10, leading=13, backColor=colors.HexColor('#f8fafc'), borderPadding=6)

        story = [
            Paragraph(f"<b>HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ THI {variant.variant_code}</b>", style_title),
            Paragraph("<i>BÀI THI: TOÁN HỌC • CHUẨN ĐỊNH DẠNG BỘ GIÁO DỤC 2025</i>", style_sub),
            Spacer(1, 12)
        ]

        for it in sorted(variant.items, key=lambda x: x.variant_order_index):
            q = it.question
            if not q: continue
            clean_stem = q.stem.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Câu {it.variant_order_index}:</b> {clean_stem}", style_bold))
            story.append(Paragraph(f"<b>Đáp án đúng:</b> <font color='#0066cc'><b>{it.answer_key or 'A'}</b></font>", style_norm))
            clean_exp = (q.explanation or "Đang cập nhật hướng dẫn giải chi tiết.").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Lời giải chi tiết:</b><br/>{clean_exp}", style_exp))
            story.append(Spacer(1, 8))

        doc.build(story)
        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"ReportLab solution PDF failed: {e}")

    # Fallback to browser
    temp_html = output_pdf.with_suffix(".temp.html")
    try:
        generate_solution_html(variant, temp_html)
        if convert_html_to_pdf_browser(temp_html, output_pdf):
            return True
    except Exception as e:
        logger.warning(f"Browser solution PDF failed: {e}")
    finally:
        if temp_html.exists():
            try:
                temp_html.unlink()
            except Exception:
                pass
    return False


def generate_answer_sheet_pdf(master: MasterExam, variants: List[ExamVariant], output_pdf: Path) -> bool:
    """Generates answer key matrix PDF using ultra-fast ReportLab with browser fallback."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=13, leading=16, alignment=1)

        story = [
            Paragraph("<b>BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ THI</b>", style_title),
            Spacer(1, 10)
        ]
        data = [["Câu", "Thể thức"] + [f"Mã {v.variant_code}" for v in variants]]
        for q_idx in range(1, master.total_questions + 1):
            m_item = next((it for it in master.items if it.order_index == q_idx), None)
            fmt = m_item.question.item_format if (m_item and m_item.question) else "SINGLE_CHOICE"
            fmt_lbl = "TN 4 Lựa chọn" if fmt == "SINGLE_CHOICE" else "Đúng/Sai" if fmt == "TRUE_FALSE_GROUP" else "Trả lời ngắn"
            row = [str(q_idx), fmt_lbl]
            for v in variants:
                v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
                row.append(v_item.answer_key if v_item and v_item.answer_key else "-")
            data.append(row)

        col_w = [40, 95] + [(515 - 135) / len(variants)] * len(variants)
        t_mat = Table(data, colWidths=col_w)
        t_mat.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#888888')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_mat)
        doc.build(story)
        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"ReportLab answer sheet PDF failed: {e}")

    # Fallback to browser
    temp_html = output_pdf.with_suffix(".temp.html")
    try:
        generate_answer_sheet_html(master, variants, temp_html)
        if convert_html_to_pdf_browser(temp_html, output_pdf):
            return True
    except Exception as e:
        logger.warning(f"Answer sheet PDF generation failed: {e}")
    finally:
        if temp_html.exists():
            try:
                temp_html.unlink()
            except Exception:
                pass
    return False


def generate_omr_bubble_sheet_pdf(output_pdf: Path) -> bool:
    """Generates official 2025 OMR Answer Bubble Sheet PDF for students to fill in."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=25, bottomMargin=25)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        font_italic = 'TimesNewRoman-Italic' if 'TimesNewRoman-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=12.5, alignment=1)
        style_sub = ParagraphStyle('Sub', fontName=font_main, fontSize=9.5, alignment=1)
        style_sec = ParagraphStyle('Sec', fontName=font_bold, fontSize=10, textColor=colors.HexColor('#002b49'))
        style_cell = ParagraphStyle('Cell', fontName=font_main, fontSize=8.5, alignment=1)

        story = [
            Paragraph("<b>BỘ GIÁO DỤC VÀ ĐÀO TẠO</b>", style_sub),
            Paragraph("<b>PHIẾU TRẢ LỜI TRẮC NGHIỆM (ĐỊNH DẠNG TỪ NĂM 2025)</b>", style_title),
            Paragraph("<i>Dùng bút chì 2B để tô kín các ô tròn tương ứng với phương án lựa chọn</i>", style_sub),
            Spacer(1, 6)
        ]

        info_data = [
            [
                Paragraph("Họ và tên: .................................................... Lớp: .........................<br/>Ngày sinh: ......./......./...........   SBD: .........................<br/>Hội đồng thi: .........................................................", style_cell),
                Paragraph("<b>SỐ BÁO DANH</b><br/>[ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ]<br/><b>MÃ ĐỀ THI</b><br/>[ &nbsp; ][ &nbsp; ][ &nbsp; ]", style_cell)
            ]
        ]
        t_info = Table(info_data, colWidths=[365, 155])
        t_info.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#999999')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN I: THÍ SINH CHỌN MỘT PHƯƠNG ÁN TRẢ LỜI (Từ câu 1 đến câu 12)</b>", style_sec))
        p1_data = [["Câu", "Phương án", "Câu", "Phương án"]]
        for i in range(1, 7):
            p1_data.append([str(i), "[A]   [B]   [C]   [D]", str(i+6), "[A]   [B]   [C]   [D]"])
        t_p1 = Table(p1_data, colWidths=[40, 220, 40, 220])
        t_p1.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_p1)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN II: THÍ SINH CHỌN ĐÚNG HOẶC SAI TRONG MỖI Ý a), b), c), d) (Từ câu 1 đến câu 4)</b>", style_sec))
        p2_data = [["Câu", "Ý a", "Ý b", "Ý c", "Ý d"]]
        for i in range(1, 5):
            p2_data.append([f"Câu {i}", "[Đ]  [S]", "[Đ]  [S]", "[Đ]  [S]", "[Đ]  [S]"])
        t_p2 = Table(p2_data, colWidths=[65, 113, 114, 114, 114])
        t_p2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_p2)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN III: THÍ SINH VIẾT VÀ TÔ KẾT QUẢ VÀO Ô ĐÁP SỐ (Từ câu 1 đến câu 6)</b>", style_sec))
        p3_data = [
            ["Câu", "Đáp số", "Câu", "Đáp số"],
            ["1", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "4", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
            ["2", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "5", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
            ["3", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "6", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
        ]
        t_p3 = Table(p3_data, colWidths=[35, 225, 35, 225])
        t_p3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_p3)

        doc.build(story)
        return output_pdf.exists() and output_pdf.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"ReportLab OMR Bubble Sheet PDF failed: {e}")
        return False


def export_single_variant_pdf(variant: ExamVariant, output_path: Path) -> Path:
    """Generates an official PDF directly for a single exam variant."""
    success = generate_variant_pdf(variant, output_path)
    if not success or not output_path.exists():
        generate_pdf_reportlab(variant, output_path)
    return output_path


def export_exam_package_zip(
    master_exam_id: str,
    db: Session,
    include_pdf: bool = True,
    export_format: str = "pdf"
) -> str:
    """Creates a comprehensive PDF export package containing:
    - De_{code}.pdf for all variants
    - LoiGiai_{code}.pdf for all variants
    - BangDapAn_TongHop.pdf and BangDapAn_TongHop.csv
    - Phieu_Tra_Loi_Trac_Nghiem_2025.pdf
    Returns the absolute path to the generated zip file.
    """
    master = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_exam_id).all()
    if not variants:
        raise ValueError("No exam variants found. Please shuffle the exam first.")

    temp_dir = STORAGE_EXPORTS_DIR / f"temp_{master_exam_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"Goi_DeThi_{master.subject.code if master.subject else 'MON'}_{master.id[:8]}.zip"
    zip_path = STORAGE_EXPORTS_DIR / zip_filename

    generated_pdf_files = []
    generated_csv_files = []

    try:
        # 1. Generate PDF for each variant and its solution
        for v in variants:
            exam_pdf = temp_dir / f"De_{v.variant_code}.pdf"
            sol_pdf = temp_dir / f"LoiGiai_{v.variant_code}.pdf"
            generate_variant_pdf(v, exam_pdf)
            generate_solution_pdf(v, sol_pdf)
            generated_pdf_files.extend([exam_pdf, sol_pdf])

        # 2. Generate CSV answer key
        csv_file = temp_dir / "BangDapAn_TongHop.csv"
        try:
            from backend.services.shuffling_engine import get_answer_key_matrix
            km = get_answer_key_matrix(master.id, db)
            rows = km.get("key_matrix", [])
            csv_lines = ["Câu,Thể thức,Đề gốc," + ",".join([f"Mã {v.variant_code}" for v in variants])]
            for r in rows:
                c_line = [str(r.get("master_question_index", "")), str(r.get("item_format", "")), str(r.get("master_answer_key", ""))]
                for v in variants:
                    c_line.append(str(r.get(f"variant_{v.variant_code}", "")))
                csv_lines.append(",".join(c_line))
            csv_file.write_text("\n".join(csv_lines), encoding="utf-8-sig")
            generated_csv_files.append(csv_file)
        except Exception:
            pass

        # 3. Generate answer matrix PDF
        matrix_pdf = temp_dir / "BangDapAn_TongHop.pdf"
        generate_answer_sheet_pdf(master, variants, matrix_pdf)
        generated_pdf_files.append(matrix_pdf)

        # 4. Generate Blank 2025 OMR Bubble Sheet for student testing
        omr_pdf = temp_dir / "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf"
        generate_omr_bubble_sheet_pdf(omr_pdf)
        generated_pdf_files.append(omr_pdf)

        # 5. Create ZIP archive
        files_to_zip = [f for f in generated_pdf_files if f.exists()] + generated_csv_files

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in files_to_zip:
                if f.exists():
                    zipf.write(f, arcname=f.name)

        return str(zip_path)
    finally:
        all_temp = generated_pdf_files + generated_csv_files
        for f in all_temp:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass
        try:
            if temp_dir.exists():
                temp_dir.rmdir()
        except Exception:
            pass


def compute_item_analytics(
    master_exam_id: str,
    student_scores: List[Dict[str, Any]],
    db: Session
) -> Dict[str, Any]:
    """Calculates psychometric metrics:
    - Item difficulty p = R / N (Proportion of students answering correctly)
    - Item discrimination D = P_H - P_L (Upper 27% correct rate minus lower 27% correct rate)
    - Flags defective questions if D < 0.20
    Updates Question records in the database.
    """
    master = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    N = len(student_scores)
    if N < 4:
        raise ValueError("At least 4 student score records are required for psychometric calculations.")

    # Sort students by total_score descending
    sorted_students = sorted(student_scores, key=lambda s: s.get("total_score", 0.0), reverse=True)
    cutoff = max(1, int(round(0.27 * N)))

    high_group = sorted_students[:cutoff]
    low_group = sorted_students[-cutoff:]
    n_group = cutoff

    items_report = []
    defective_count = 0

    # Collect all questions in master exam
    for master_item in master.items:
        q = master_item.question
        q_id = q.id
        q_key = f"q_{master_item.order_index}"

        # Total correct
        total_correct = sum(1 for s in sorted_students if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_val = round(total_correct / N, 3)

        # High group correct
        high_correct = sum(1 for s in high_group if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_high = high_correct / n_group

        # Low group correct
        low_correct = sum(1 for s in low_group if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_low = low_correct / n_group

        d_val = round(p_high - p_low, 3)

        # Defective rule: D < 0.2
        is_defective = d_val < 0.20
        if is_defective:
            defective_count += 1

        # Update question record in database
        q.difficulty_p = p_val
        q.discrimination_d = d_val
        q.is_defective = is_defective
        db.add(q)

        items_report.append({
            "order_index": master_item.order_index,
            "question_id": q.id,
            "stem": q.stem[:80] + "..." if len(q.stem) > 80 else q.stem,
            "difficulty_p": p_val,
            "discrimination_d": d_val,
            "is_defective": is_defective,
            "status": "DEFECTIVE_FLAGGED" if is_defective else "ACCEPTABLE"
        })

    db.commit()

    return {
        "master_exam_id": master.id,
        "total_candidates": N,
        "high_group_size": cutoff,
        "low_group_size": cutoff,
        "defective_questions_count": defective_count,
        "items": items_report
    }


def generate_digitized_exam_pdf(
    questions: List[Dict[str, Any]],
    output_pdf: Path,
    title: str = "ĐỀ THI KHẢO THÍ",
    school_name: str = "SỞ GIÁO DỤC VÀ ĐÀO TẠO",
    subject_name: str = "Toán học",
    grade: str = "12",
    variant_code: str = "101",
    duration: int = 90,
    math_format: str = "latex"
) -> bool:
    """Generates an official high-fidelity print-quality PDF for digitized questions via LaTeX engine."""
    output_pdf = Path(output_pdf).resolve()
    from backend.services.latex_pdf_exporter import generate_digitized_exam_latex_pdf
    ok = generate_digitized_exam_latex_pdf(
        questions=questions,
        output_pdf=output_pdf,
        title=title,
        school_name=school_name,
        subject_name=subject_name,
        grade=grade,
        variant_code=variant_code,
        duration=duration
    )
    return bool(ok and output_pdf.exists() and output_pdf.stat().st_size > 1000)


# ===========================================================================
# Retired Word / docx stubs for backwards compatibility
# ===========================================================================

def generate_variant_docx(*args, **kwargs):
    """Retired: Word (.docx) export has been replaced by pure Vector PDF (LaTeX ex_test.sty)."""
    raise NotImplementedError("Word (.docx) export has been retired in favor of pure Vector PDF.")


def generate_solution_docx(*args, **kwargs):
    """Retired: Word (.docx) export has been replaced by pure Vector PDF (LaTeX ex_test.sty)."""
    raise NotImplementedError("Word (.docx) export has been retired in favor of pure Vector PDF.")


def generate_answer_sheet_docx(*args, **kwargs):
    """Retired: Word (.docx) export has been replaced by pure Vector PDF (LaTeX ex_test.sty)."""
    raise NotImplementedError("Word (.docx) export has been retired in favor of pure Vector PDF.")


def generate_digitized_exam_docx(*args, **kwargs):
    """Retired: Word (.docx) export has been replaced by pure Vector PDF (LaTeX ex_test.sty)."""
    raise NotImplementedError("Word (.docx) export has been retired in favor of pure Vector PDF.")


def convert_docx_to_pdf(*args, **kwargs) -> bool:
    """Retired: Word COM conversion has been replaced by native LaTeX and ReportLab engines."""
    return False
