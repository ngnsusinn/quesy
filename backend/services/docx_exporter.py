import os
import re
import zipfile
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls
import lxml.etree as etree

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False

from sqlalchemy.orm import Session
from backend.models import MasterExam, ExamVariant, Question, ExamVariantItem


STORAGE_EXPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "exports"
STORAGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
MML2OMML_PATH = ASSETS_DIR / "MML2OMML.XSL"


# ---------------------------------------------------------------------------
# 1. Native OMML Equation Converter
# ---------------------------------------------------------------------------

_xslt_transformer = None


def _get_xslt_transformer():
    """Lazily load and cache MML2OMML XSLT transformer."""
    global _xslt_transformer
    if _xslt_transformer is not None:
        return _xslt_transformer

    candidate_paths = [
        MML2OMML_PATH,
        Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"),
        Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"),
    ]

    for p in candidate_paths:
        if p.exists():
            try:
                xslt_tree = etree.parse(str(p))
                _xslt_transformer = etree.XSLT(xslt_tree)
                return _xslt_transformer
            except Exception:
                continue

    return None


def convert_latex_to_omml(latex_code: str) -> Optional[Any]:
    """Converts a LaTeX math expression to a native Word OMML (<m:oMath>) XML element."""
    if not HAS_LATEX2MATHML:
        return None

    clean_code = latex_code.strip().strip("$")
    if not clean_code:
        return None

    clean_code = clean_code.replace(r"\mathbb{R}", "R").replace(r"\mathbb{Z}", "Z")
    clean_code = clean_code.replace(r"\mathbb{N}", "N").replace(r"\mathbb{Q}", "Q")

    try:
        transformer = _get_xslt_transformer()
        mml_str = latex2mathml.converter.convert(clean_code)
        if transformer is not None:
            mml_dom = etree.fromstring(mml_str.encode("utf-8"))
            omml_dom = transformer(mml_dom)
            omml_str = etree.tostring(omml_dom).decode("utf-8")
            return parse_xml(omml_str)
    except Exception:
        pass

    return None


def add_math_text_to_paragraph(
    paragraph: docx.text.paragraph.Paragraph,
    text: str,
    bold_prefix: Optional[str] = None,
    italic_prefix: Optional[str] = None,
    default_font_size: int = 11,
):
    """Parses text containing inline LaTeX formulas ($...$ or $$...$$) and inserts
    runs with native Word OMML (<m:oMath>) equations seamlessly alongside plain text.
    """
    if bold_prefix and isinstance(bold_prefix, str):
        r_pre = paragraph.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(default_font_size)

    if italic_prefix and isinstance(italic_prefix, str):
        r_pre = paragraph.add_run(italic_prefix)
        r_pre.font.italic = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(default_font_size)

    if not text:
        return

    tokens = re.split(r"(\$\$.*?\$\$|\$.*?\$)", text, flags=re.DOTALL)

    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("$") and tok.endswith("$"):
            omml_elem = convert_latex_to_omml(tok)
            if omml_elem is not None:
                paragraph._p.append(omml_elem)
            else:
                clean_expr = tok.strip("$")
                r_math = paragraph.add_run(clean_expr)
                r_math.font.italic = True
                r_math.font.name = "Times New Roman"
                r_math.font.size = Pt(default_font_size)
        else:
            r_txt = paragraph.add_run(tok)
            r_txt.font.name = "Times New Roman"
            r_txt.font.size = Pt(default_font_size)


# ---------------------------------------------------------------------------
# 2. Official Ministry Examination Header & Layout
# ---------------------------------------------------------------------------

def _set_cell_border(cell, **kwargs):
    """Sets thin borders on a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="{kwargs.get("top", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="{kwargs.get("left", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="{kwargs.get("bottom", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="{kwargs.get("right", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)


def _remove_table_borders(table):
    """Removes all borders from a table."""
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/><w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)


def _setup_exam_header(
    doc: docx.Document,
    school_name: str,
    exam_title: str,
    subject_name: str,
    grade: str,
    variant_code: str,
    duration: int = 90,
):
    """Generates the official Ministry of Education standard examination header:
    - Left column: School/Department name, Official Exam designation, Page count notice.
    - Right column: Exam Title, Subject, Grade, Duration.
    - Prominent Variant Code Box.
    - Student info box (Họ tên, SBD, Lớp/Phòng thi).
    - Phách box (Số phách, Điểm số).
    """
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    _remove_table_borders(header_table)
    header_table.columns[0].width = Cm(8.0)
    header_table.columns[1].width = Cm(10.0)

    # Left cell: Authority & School
    left_cell = header_table.cell(0, 0)
    p_left = left_cell.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_auth = p_left.add_run(f"{school_name.upper()}\n")
    r_auth.font.bold = True
    r_auth.font.size = Pt(10.5)
    r_auth.font.name = "Times New Roman"

    r_official = p_left.add_run("ĐỀ THI CHÍNH THỨC\n")
    r_official.font.bold = True
    r_official.font.size = Pt(11)
    r_official.font.name = "Times New Roman"

    r_pages = p_left.add_run("(Đề thi có 04 trang)")
    r_pages.font.italic = True
    r_pages.font.size = Pt(9.5)
    r_pages.font.name = "Times New Roman"

    # Right cell: Exam Title & Subject Info
    right_cell = header_table.cell(0, 1)
    p_right = right_cell.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r_exam = p_right.add_run(f"{exam_title.upper()}\n")
    r_exam.font.bold = True
    r_exam.font.size = Pt(10.5)
    r_exam.font.name = "Times New Roman"

    grade_str = f" - KHỐI {grade}" if grade else ""
    r_subj = p_right.add_run(f"Bài thi: {subject_name.upper()}{grade_str}\n")
    r_subj.font.bold = True
    r_subj.font.size = Pt(11)
    r_subj.font.name = "Times New Roman"

    r_dur = p_right.add_run(f"Thời gian làm bài: {duration} phút, không kể thời gian phát đề")
    r_dur.font.italic = True
    r_dur.font.size = Pt(9.5)
    r_dur.font.name = "Times New Roman"

    # Variant Code Box
    p_var_wrap = doc.add_paragraph()
    p_var_wrap.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_var_wrap.paragraph_format.space_before = Pt(4)
    p_var_wrap.paragraph_format.space_after = Pt(4)
    r_var_box = p_var_wrap.add_run(f"  MÃ ĐỀ THI: {variant_code}  ")
    r_var_box.font.bold = True
    r_var_box.font.size = Pt(11)
    r_var_box.font.name = "Times New Roman"

    # Student Information & Phách Box Table
    info_table = doc.add_table(rows=2, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False
    info_table.columns[0].width = Cm(12.5)
    info_table.columns[1].width = Cm(5.5)

    c1_1 = info_table.cell(0, 0)
    p_name = c1_1.paragraphs[0]
    p_name.paragraph_format.space_after = Pt(2)
    r_n = p_name.add_run("Họ và tên thí sinh: ................................................................................")
    r_n.font.size = Pt(10)
    r_n.font.name = "Times New Roman"

    c1_2 = info_table.cell(0, 1)
    p_sbd = c1_2.paragraphs[0]
    p_sbd.paragraph_format.space_after = Pt(2)
    r_sbd = p_sbd.add_run("Số báo danh: ...........................")
    r_sbd.font.size = Pt(10)
    r_sbd.font.name = "Times New Roman"

    c2_1 = info_table.cell(1, 0)
    p_room = c2_1.paragraphs[0]
    p_room.paragraph_format.space_after = Pt(2)
    r_rm = p_room.add_run("Phòng thi: .................... Lớp: ....................")
    r_rm.font.size = Pt(10)
    r_rm.font.name = "Times New Roman"

    c2_2 = info_table.cell(1, 1)
    p_phach = c2_2.paragraphs[0]
    p_phach.paragraph_format.space_after = Pt(2)
    r_ph = p_phach.add_run("Số phách: .................. Điểm: ......")
    r_ph.font.size = Pt(10)
    r_ph.font.name = "Times New Roman"

    _set_cell_border(c1_1, top="single", left="single", bottom="none", right="single")
    _set_cell_border(c1_2, top="single", left="single", bottom="none", right="single")
    _set_cell_border(c2_1, top="none", left="single", bottom="single", right="single")
    _set_cell_border(c2_2, top="none", left="single", bottom="single", right="single")

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(8)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_div.add_run("─────────────────────────────────────────────────────────────")
    r_line.font.size = Pt(8)
    r_line.font.color.rgb = RGBColor(128, 128, 128)


def _set_section_2_columns(section):
    """Enforces 2-column layout on a Word section via OpenXML."""
    sectPr = section._sectPr
    cols = sectPr.xpath("./w:cols")
    if cols:
        cols[0].set(qn("w:num"), "2")
        cols[0].set(qn("w:space"), "720")
    else:
        cols_elem = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="720"/>')
        sectPr.append(cols_elem)


def _set_section_1_column(section):
    """Resets section layout to 1 column."""
    sectPr = section._sectPr
    cols = sectPr.xpath("./w:cols")
    if cols:
        cols[0].set(qn("w:num"), "1")
    else:
        cols_elem = parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>')
        sectPr.append(cols_elem)


def generate_variant_docx(variant: ExamVariant, output_path: Path):
    """Generates an official Ministry format .docx exam paper for a specific variant:
    - Official header (School name, Exam title, Subject, Grade, Variant code box, Student info, Phách).
    - 2-column layout for question content.
    - Native OMML (<m:oMath>) equations.
    """
    doc = docx.Document()

    # 1. Page Margins (1.5 cm all around to maximize 2-column space)
    s1 = doc.sections[0]
    s1.top_margin = Cm(1.5)
    s1.bottom_margin = Cm(1.5)
    s1.left_margin = Cm(1.5)
    s1.right_margin = Cm(1.5)

    master = variant.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"
    grade = str(master.grade_id) if master else "12"
    exam_title = master.title if master else "Kỳ thi Tốt nghiệp THPT Năm 2025"
    school_name = "SỞ GIÁO DỤC VÀ ĐÀO TẠO"

    # Header in Section 1 (1 column)
    _setup_exam_header(
        doc=doc,
        school_name=school_name,
        exam_title=exam_title,
        subject_name=subject_name,
        grade=grade,
        variant_code=variant.variant_code,
        duration=90,
    )

    # 2. Section 2: Questions in 2-Column Layout (Continuous section break)
    s2 = doc.add_section(WD_SECTION.CONTINUOUS)
    _set_section_2_columns(s2)

    # Sort variant items by variant_order_index
    items = sorted(variant.items, key=lambda x: x.variant_order_index)

    current_section = None
    section_titles = {
        1: "PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.",
        2: "PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.",
        3: "PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu 6.",
        4: "PHẦN IV. Tự luận.",
    }

    last_passage_id = None

    for item in items:
        q: Question = item.question
        if not q:
            continue

        # Determine section
        sec = 1
        if q.item_format == "SINGLE_CHOICE":
            sec = 1
        elif q.item_format == "TRUE_FALSE_GROUP":
            sec = 2
        elif q.item_format == "SHORT_ANSWER":
            sec = 3
        else:
            sec = 4

        # Section Header Banner
        if sec != current_section:
            current_section = sec
            sec_heading = doc.add_paragraph()
            sec_heading.paragraph_format.space_before = Pt(10)
            sec_heading.paragraph_format.space_after = Pt(4)
            r_sec = sec_heading.add_run(section_titles.get(sec, f"PHẦN {sec}"))
            r_sec.font.bold = True
            r_sec.font.size = Pt(10.5)
            r_sec.font.name = "Times New Roman"

        # Passage Rendering (RULE-03: Passage context immediately precedes child questions)
        pid = getattr(q, "passage_id", None)
        p_content = getattr(q, "passage_content", None)
        if pid and pid != last_passage_id and p_content:
            last_passage_id = pid
            p_pass_intro = doc.add_paragraph()
            p_pass_intro.paragraph_format.space_before = Pt(6)
            p_pass_intro.paragraph_format.space_after = Pt(2)
            r_intro = p_pass_intro.add_run("Đọc đoạn thông tin sau và trả lời các câu hỏi:")
            r_intro.font.bold = True
            r_intro.font.italic = True
            r_intro.font.size = Pt(10)
            r_intro.font.name = "Times New Roman"

            p_pass = doc.add_paragraph()
            p_pass.paragraph_format.left_indent = Inches(0.15)
            p_pass.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_pass, p_content, default_font_size=10)

        # Question Stem with Native OMML Equations
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(4)
        p_q.paragraph_format.space_after = Pt(2)
        add_math_text_to_paragraph(p_q, q.stem, bold_prefix=f"Câu {item.variant_order_index}: ", default_font_size=10.5)

        # Render options or sub-statements
        if q.item_format == "SINGLE_CHOICE" and q.options:
            mapping = {}
            if item.option_mapping:
                try:
                    mapping = json.loads(item.option_mapping)
                except Exception:
                    pass

            inv_map = {v: k for k, v in mapping.items()} if mapping else {}
            labels = ["A", "B", "C", "D"]

            for lbl in labels:
                orig_label = inv_map.get(lbl, lbl)
                orig_opt = next((o for o in q.options if o.label == orig_label), None)
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.2)
                p_opt.paragraph_format.space_after = Pt(1.5)
                content = orig_opt.content if orig_opt else ""
                add_math_text_to_paragraph(p_opt, content, bold_prefix=f"{lbl}. ", default_font_size=10.5)

        elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
            for sub in q.sub_statements:
                p_sub = doc.add_paragraph()
                p_sub.paragraph_format.left_indent = Inches(0.2)
                p_sub.paragraph_format.space_after = Pt(1.5)
                add_math_text_to_paragraph(p_sub, sub.content, bold_prefix=f"{sub.label}) ", default_font_size=10)

        elif q.item_format == "SHORT_ANSWER":
            p_ans = doc.add_paragraph()
            p_ans.paragraph_format.left_indent = Inches(0.2)
            p_ans.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_ans, "................................................................", italic_prefix="Đáp số: ", default_font_size=10)

    # 3. Section 3: Return to 1 Column for Footer / End Note
    s3 = doc.add_section(WD_SECTION.CONTINUOUS)
    _set_section_1_column(s3)

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(14)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("─────────────────── HẾT ───────────────────")
    r_end.font.bold = True
    r_end.font.size = Pt(11)
    r_end.font.name = "Times New Roman"

    p_super = doc.add_paragraph()
    p_super.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_super.paragraph_format.space_after = Pt(6)
    r_sup = p_super.add_run("Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.")
    r_sup.font.italic = True
    r_sup.font.size = Pt(10)
    r_sup.font.name = "Times New Roman"

    doc.save(output_path)


def generate_solution_docx(variant: ExamVariant, output_path: Path):
    """Generates a detailed solution document for a variant with OMML equations."""
    doc = docx.Document()
    s = doc.sections[0]
    s.top_margin = Cm(1.5)
    s.bottom_margin = Cm(1.5)
    s.left_margin = Cm(1.5)
    s.right_margin = Cm(1.5)

    master = variant.master_exam
    subject_name = master.subject.name if master and master.subject else "Toán học"

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(f"HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ {variant.variant_code}\nBÀI THI: {subject_name.upper()}\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.name = "Times New Roman"

    p_banner = doc.add_paragraph()
    p_banner.paragraph_format.space_after = Pt(10)
    r_b = p_banner.add_run("Áp dụng thang điểm Quyết định 764/QĐ-BGDĐT: Đúng 1 ý: 0.1đ | Đúng 2 ý: 0.25đ | Đúng 3 ý: 0.5đ | Đúng 4 ý: 1.0đ")
    r_b.font.italic = True
    r_b.font.size = Pt(10)
    r_b.font.color.rgb = RGBColor(100, 100, 100)

    items = sorted(variant.items, key=lambda x: x.variant_order_index)
    for item in items:
        q: Question = item.question
        if not q:
            continue

        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        add_math_text_to_paragraph(p_q, q.stem, bold_prefix=f"Câu {item.variant_order_index}: ")

        # Show Answer Key
        p_k = doc.add_paragraph()
        p_k.paragraph_format.space_after = Pt(2)
        r_k = p_k.add_run(f"Đáp án: {item.answer_key or 'Đang cập nhật'}")
        r_k.font.bold = True
        r_k.font.color.rgb = RGBColor(0, 102, 204)

        # Show Explanation
        if q.explanation:
            p_exp = doc.add_paragraph()
            p_exp.paragraph_format.left_indent = Inches(0.2)
            p_exp.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_exp, q.explanation, italic_prefix="Lời giải chi tiết: ")

    doc.save(output_path)


def generate_answer_sheet_docx(master: MasterExam, variants: List[ExamVariant], output_path: Path):
    """Generates an Answer Key Matrix overview Word document."""
    doc = docx.Document()
    s = doc.sections[0]
    s.top_margin = Cm(1.5)
    s.bottom_margin = Cm(1.5)
    s.left_margin = Cm(1.5)
    s.right_margin = Cm(1.5)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(f"BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ\n{master.title.upper()}\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.name = "Times New Roman"

    num_q = master.total_questions
    col_count = 1 + len(variants)

    table = doc.add_table(rows=num_q + 1, cols=col_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].paragraphs[0].add_run("Câu").font.bold = True
    for idx, v in enumerate(variants):
        hdr_cells[idx + 1].paragraphs[0].add_run(f"Mã {v.variant_code}").font.bold = True

    # Fill rows
    for q_idx in range(1, num_q + 1):
        row_cells = table.rows[q_idx].cells
        row_cells[0].paragraphs[0].add_run(str(q_idx))
        for v_idx, v in enumerate(variants):
            v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
            val = v_item.answer_key if v_item and v_item.answer_key else "-"
            row_cells[v_idx + 1].paragraphs[0].add_run(val)

    # Add RULE-01 Grading matrix explanation table
    p_rule = doc.add_paragraph()
    p_rule.paragraph_format.space_before = Pt(14)
    r_r = p_rule.add_run("QUY TẮC CHẤM ĐIỂM TRẮC NGHIỆM ĐÚNG/SAI (RULE-01 - Quyết định 764/QĐ-BGDĐT)")
    r_r.font.bold = True

    scale_table = doc.add_table(rows=5, cols=3)
    scale_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scale_hdr = scale_table.rows[0].cells
    scale_hdr[0].paragraphs[0].add_run("Số ý đúng trong 1 câu").font.bold = True
    scale_hdr[1].paragraphs[0].add_run("Tỷ lệ điểm").font.bold = True
    scale_hdr[2].paragraphs[0].add_run("Điểm nhận được (Thang 1.0)").font.bold = True

    scale_rows = [
        ("Đúng 1 ý", "10%", "0.10 điểm"),
        ("Đúng 2 ý", "25%", "0.25 điểm"),
        ("Đúng 3 ý", "50%", "0.50 điểm"),
        ("Đúng cả 4 ý", "100%", "1.00 điểm"),
    ]
    for r_i, (k, p, d) in enumerate(scale_rows, start=1):
        c = scale_table.rows[r_i].cells
        c[0].paragraphs[0].add_run(k)
        c[1].paragraphs[0].add_run(p)
        c[2].paragraphs[0].add_run(d)

    doc.save(output_path)


# ---------------------------------------------------------------------------
# PDF Conversion & Multi-format Export
# ---------------------------------------------------------------------------

logger = logging.getLogger("quesy.docx_exporter")


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Converts a DOCX file to PDF using Word COM automation on Windows or headless Edge."""
    docx_p = Path(docx_path).resolve()
    pdf_p = Path(pdf_path).resolve()

    # Strategy 1: Word COM Automation on Windows
    if os.name == "nt":
        try:
            ps_cmd = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{str(docx_p)}')
    $doc.SaveAs([ref]'{str(pdf_p)}', [ref]17)
    $doc.Close([ref]$false)
}} finally {{
    $word.Quit()
}}
"""
            res = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True, timeout=30)
            if pdf_p.exists() and pdf_p.stat().st_size > 1000:
                return True
        except Exception as e:
            logger.warning(f"Word COM PDF conversion failed: {e}")

    return False


def batch_convert_docx_to_pdf(pairs: List[Tuple[Path, Path]]) -> None:
    """Converts multiple DOCX files to PDF in a single Word COM session for speed."""
    if not pairs or os.name != "nt":
        return
    try:
        lines = [
            "$word = New-Object -ComObject Word.Application",
            "$word.Visible = $false",
            "try {"
        ]
        for docx_p, pdf_p in pairs:
            lines.append(f"    $doc = $word.Documents.Open('{str(Path(docx_p).resolve())}')")
            lines.append(f"    $doc.SaveAs([ref]'{str(Path(pdf_p).resolve())}', [ref]17)")
            lines.append(f"    $doc.Close([ref]$false)")
        lines.append("} finally {")
        lines.append("    $word.Quit()")
        lines.append("}")
        ps_cmd = "\n".join(lines)
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True, timeout=90)
    except Exception as e:
        logger.warning(f"Batch PDF conversion error: {e}")


def export_single_variant_pdf(variant: ExamVariant, output_path: Path) -> Path:
    """Generates an official PDF directly for a single exam variant."""
    temp_docx = output_path.with_suffix(".temp.docx")
    generate_variant_docx(variant, temp_docx)
    try:
        success = convert_docx_to_pdf(temp_docx, output_path)
        if not success:
            raise RuntimeError("Không thể tạo file PDF từ tài liệu Word.")
        return output_path
    finally:
        if temp_docx.exists():
            temp_docx.unlink()


def export_exam_package_zip(
    master_exam_id: str,
    db: Session,
    include_pdf: bool = True,
    export_format: str = "all"
) -> str:
    """Creates a comprehensive ZIP export package containing:
    - De_{code}.docx for all variants (valid OpenXML documents)
    - De_{code}.pdf for all variants (if include_pdf=True or export_format in ['pdf', 'all'])
    - LoiGiai_{code}.docx and .pdf
    - BangDapAn_TongHop.docx and .csv
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

    generated_docx_files = []
    generated_pdf_files = []
    generated_csv_files = []
    pdf_conversion_pairs = []

    try:
        # 1. Generate DOCX for each variant and its solution
        for v in variants:
            exam_file = temp_dir / f"De_{v.variant_code}.docx"
            generate_variant_docx(v, exam_file)
            generated_docx_files.append(exam_file)

            sol_file = temp_dir / f"LoiGiai_{v.variant_code}.docx"
            generate_solution_docx(v, sol_file)
            generated_docx_files.append(sol_file)

            if include_pdf or export_format in ["all", "pdf"]:
                exam_pdf = temp_dir / f"De_{v.variant_code}.pdf"
                sol_pdf = temp_dir / f"LoiGiai_{v.variant_code}.pdf"
                pdf_conversion_pairs.append((exam_file, exam_pdf))
                pdf_conversion_pairs.append((sol_file, sol_pdf))
                generated_pdf_files.extend([exam_pdf, sol_pdf])

        # 2. Generate answer matrix docx & CSV
        matrix_file = temp_dir / "BangDapAn_TongHop.docx"
        generate_answer_sheet_docx(master, variants, matrix_file)
        generated_docx_files.append(matrix_file)

        # Generate CSV answer key
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

        if include_pdf or export_format in ["all", "pdf"]:
            matrix_pdf = temp_dir / "BangDapAn_TongHop.pdf"
            pdf_conversion_pairs.append((matrix_file, matrix_pdf))
            generated_pdf_files.append(matrix_pdf)

            # Perform batch PDF conversion
            batch_convert_docx_to_pdf(pdf_conversion_pairs)

        # 3. Create ZIP archive based on requested format
        files_to_zip = []
        if export_format == "docx":
            files_to_zip = generated_docx_files + generated_csv_files
        elif export_format == "pdf":
            files_to_zip = [f for f in generated_pdf_files if f.exists()] + generated_csv_files
            if not files_to_zip:
                files_to_zip = generated_docx_files + generated_csv_files
        else:  # "all"
            files_to_zip = generated_docx_files + [f for f in generated_pdf_files if f.exists()] + generated_csv_files

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in files_to_zip:
                if f.exists():
                    zipf.write(f, arcname=f.name)

        return str(zip_path)
    finally:
        all_temp = generated_docx_files + generated_pdf_files + generated_csv_files
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
