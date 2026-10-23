import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_element(name):
    return OxmlElement(name)

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets internal padding for a cell in twips (1 pt = 20 twips)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4"):
    """Sets neat borders for the whole table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:left w:val="none"/>'
                        f'<w:right w:val="none"/>'
                        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:insideV w:val="none"/>'
                        f'</w:tblBorders>')
    tblPr.append(borders)

def set_table_grid_borders(table, color="B0C4DE", sz="6"):
    """Sets clean grid borders for tables."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
                        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
                        f'</w:tblBorders>')
    tblPr.append(borders)

def build_report_document(output_path: Path):
    doc = Document()

    # 1. Page Setup: A4 Portrait, Margins 20mm
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(20)
    section.right_margin = Mm(20)

    # 2. Header and Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("BÁO CÁO ĐĂNG KÝ ĐỀ TÀI DỰ ÁN PHẦN MỀM — HỆ THỐNG QUESY")
    hrun.font.name = "Times New Roman"
    hrun.font.size = Pt(8.5)
    hrun.font.italic = True
    hrun.font.color.rgb = RGBColor(120, 120, 120)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun = fp.add_run("Quesy Assessment & Item Bank System • Chuẩn Thông tư 32/2018 & Quyết định 764/BGDĐT")
    frun.font.name = "Times New Roman"
    frun.font.size = Pt(8.5)
    frun.font.italic = True
    frun.font.color.rgb = RGBColor(130, 130, 130)

    # Base Style Config
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(11)
    style_normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # HEADER BANNER (Cơ quan chủ quản / Trường học)
    # -------------------------------------------------------------
    tbl_inst = doc.add_table(rows=1, cols=2)
    tbl_inst.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_inst.autofit = False
    tbl_inst.columns[0].width = Mm(85)
    tbl_inst.columns[1].width = Mm(85)

    c0 = tbl_inst.cell(0, 0)
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0_1 = p0.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\n")
    r0_1.font.bold = True
    r0_1.font.size = Pt(10)
    r0_2 = p0.add_run("TRƯỜNG ĐẠI HỌC / KHOA CÔNG NGHỆ THÔNG TIN\n")
    r0_2.font.bold = True
    r0_2.font.size = Pt(10)
    r0_3 = p0.add_run("BỘ MÔN: KỸ THUẬT PHẦN MỀM")
    r0_3.font.size = Pt(9.5)

    c1 = tbl_inst.cell(0, 1)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1_1 = p1.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n")
    r1_1.font.bold = True
    r1_1.font.size = Pt(10)
    r1_2 = p1.add_run("Độc lập – Tự do – Hạnh phúc\n")
    r1_2.font.bold = True
    r1_2.font.size = Pt(10)
    r1_3 = p1.add_run("-------------------o0o-------------------")
    r1_3.font.size = Pt(9)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # DOCUMENT MAIN TITLE
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(4)
    r_t1 = p_title.add_run("BẢN ĐĂNG KÝ ĐỀ TÀI DỰ ÁN PHẦN MỀM\n")
    r_t1.font.size = Pt(16)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(0, 51, 102) # Deep Navy

    r_t2 = p_title.add_run("BÁO CÁO MÔ TẢ ĐẶC TẢ YÊU CẦU & CÁC CHỨC NĂNG CHÍNH CỦA HỆ THỐNG")
    r_t2.font.size = Pt(12)
    r_t2.font.bold = True
    r_t2.font.color.rgb = RGBColor(0, 113, 227) # Apple Blue

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("(Áp dụng cho Học phần: Đồ án môn học / Công nghệ phần mềm / Khóa luận tốt nghiệp)")
    r_sub.font.italic = True
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(100, 100, 100)

    # -------------------------------------------------------------
    # SECTION 1: DANH SÁCH THÀNH VIÊN ĐĂNG KÝ & THÔNG TIN HỌC PHẦN
    # -------------------------------------------------------------
    p_s1 = doc.add_paragraph()
    r_s1 = p_s1.add_run("I. THÔNG TIN CHUNG & DANH SÁCH THÀNH VIÊN THỰC HIỆN")
    r_s1.font.size = Pt(13)
    r_s1.font.bold = True
    r_s1.font.color.rgb = RGBColor(0, 51, 102)
    p_s1.paragraph_format.space_before = Pt(6)
    p_s1.paragraph_format.space_after = Pt(4)

    # Member Table (Clean, Professional formatting with placeholders for students)
    tbl_members = doc.add_table(rows=5, cols=6)
    tbl_members.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_grid_borders(tbl_members, color="A0B4CC", sz="6")

    headers = ["STT", "Mã số sinh viên (MSSV)", "Họ và tên sinh viên", "Lớp sinh hoạt", "Vai trò / Phân công", "Chữ ký"]
    col_widths = [Mm(12), Mm(34), Mm(45), Mm(26), Mm(38), Mm(15)]

    hdr_cells = tbl_members.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F497D") # Dark Blue
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    member_data = [
        ("1", "[Điền MSSV thành viên 1]", "[Điền Họ và tên thành viên 1]", "[Điền Lớp]", "Trưởng nhóm (Project Lead & Fullstack)", ""),
        ("2", "[Điền MSSV thành viên 2]", "[Điền Họ và tên thành viên 2]", "[Điền Lớp]", "Thành viên (Backend & AI Microservices)", ""),
        ("3", "[Điền MSSV thành viên 3]", "[Điền Họ và tên thành viên 3]", "[Điền Lớp]", "Thành viên (Frontend SPA & UI/UX Designer)", ""),
        ("4", "[Điền MSSV thành viên 4]", "[Điền Họ và tên thành viên 4]", "[Điền Lớp]", "Thành viên (QA / Test Suite & Data Standard)", ""),
    ]

    for row_idx, data in enumerate(member_data, start=1):
        row_cells = tbl_members.rows[row_idx].cells
        bg_col = "F5F8FC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            row_cells[col_idx].text = val
            set_cell_background(row_cells[col_idx], bg_col)
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=80, right=80)
            p = row_cells[col_idx].paragraphs[0]
            if col_idx in [0, 1, 3, 5]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.size = Pt(9.5)
                if "[" in val:
                    r.font.italic = True
                    r.font.color.rgb = RGBColor(90, 90, 90)

    for row in tbl_members.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Advisor & Course Information Table
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    tbl_info = doc.add_table(rows=4, cols=2)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_info, color="CBD5E1", sz="4")
    tbl_info.columns[0].width = Mm(50)
    tbl_info.columns[1].width = Mm(120)

    info_data = [
        ("Giảng viên hướng dẫn (GVHD):", "[Điền Học hàm, Học vị, Họ và tên Giảng viên hướng dẫn]"),
        ("Học phần / Môn học:", "Công nghệ Phần mềm / Đồ án Chuyên ngành Kỹ thuật Phần mềm"),
        ("Thời gian thực hiện đề tài:", "Học kỳ 1 - Năm học 2026 - 2027"),
        ("Môi trường triển khai & Thử nghiệm:", "Local Development Server, Docker Container, Web Browser"),
    ]

    for r_idx, (k, v) in enumerate(info_data):
        c_k = tbl_info.cell(r_idx, 0)
        c_v = tbl_info.cell(r_idx, 1)
        c_k.text = k
        c_v.text = v
        set_cell_margins(c_k, top=60, bottom=60, left=60, right=60)
        set_cell_margins(c_v, top=60, bottom=60, left=60, right=60)
        pk = c_k.paragraphs[0]
        pk.runs[0].font.bold = True
        pk.runs[0].font.size = Pt(10)
        pv = c_v.paragraphs[0]
        pv.runs[0].font.size = Pt(10)
        if "[" in v:
            pv.runs[0].font.italic = True
            pv.runs[0].font.color.rgb = RGBColor(80, 80, 80)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECTION 2: THÔNG TIN ĐỊNH DANH PHẦN MỀM
    # -------------------------------------------------------------
    p_s2 = doc.add_paragraph()
    r_s2 = p_s2.add_run("II. THÔNG TIN ĐỊNH DANH VÀ TỔNG QUAN PHẦN MỀM")
    r_s2.font.size = Pt(13)
    r_s2.font.bold = True
    r_s2.font.color.rgb = RGBColor(0, 51, 102)
    p_s2.paragraph_format.space_before = Pt(8)
    p_s2.paragraph_format.space_after = Pt(4)

    p_ident = doc.add_paragraph()
    p_ident.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p_ident.add_run("1. Tên thương hiệu phần mềm: ")
    r.font.bold = True
    r_val = p_ident.add_run("QUESY (Question Ecosystem System)\n")
    r_val.font.bold = True
    r_val.font.color.rgb = RGBColor(0, 113, 227)

    r = p_ident.add_run("2. Tên đầy đủ của đề tài: ")
    r.font.bold = True
    p_ident.add_run("Nền tảng Số hóa Đề thi bằng AI, Quản lý Ngân hàng Câu hỏi Chuẩn Quốc gia và Soạn thảo LaTeX Tích hợp Trợ lý Trí tuệ Nhân tạo (AI Copilot Studio).\n")

    r = p_ident.add_run("3. Lĩnh vực ứng dụng: ")
    r.font.bold = True
    p_ident.add_run("Công nghệ Giáo dục (EdTech), Đo lường & Khảo thí Đánh giá năng lực học sinh phổ thông.\n")

    r = p_ident.add_run("4. Căn cứ Pháp lý & Tiêu chuẩn Khảo thí Quốc gia bắt buộc tuân thủ:\n")
    r.font.bold = True
    
    p_tt32 = doc.add_paragraph(style='List Bullet')
    p_tt32.paragraph_format.space_after = Pt(2)
    r = p_tt32.add_run("Thông tư số 32/2018/TT-BGDĐT: ")
    r.font.bold = True
    p_tt32.add_run("Chương trình Giáo dục phổ thông 2018. Phân cấp cây kiến thức 6 tầng chuẩn hóa theo Yêu cầu cần đạt (YCCĐ) và Dạng câu hỏi chuyên đề. ")
    r_imp = p_tt32.add_run("Tuyệt đối không phân chia câu hỏi theo các bộ sách giáo khoa thương mại")
    r_imp.font.bold = True
    r_imp.font.underline = True
    p_tt32.add_run(" (Cánh diều, Kết nối tri thức, Chân trời sáng tạo...), bảo đảm tính khách quan, chuẩn mực của đề thi cấp quốc gia.")

    p_qd764 = doc.add_paragraph(style='List Bullet')
    p_qd764.paragraph_format.space_after = Pt(2)
    r = p_qd764.add_run("Quyết định số 764/QĐ-BGDĐT: ")
    r.font.bold = True
    p_qd764.add_run("Quy định định dạng cấu trúc đề thi tốt nghiệp THPT từ năm 2025. Chuẩn hóa 3 phần thi: Phần I (Trắc nghiệm nhiều lựa chọn), Phần II (Trắc nghiệm Đúng/Sai 4 khẳng định theo quy tắc điểm bậc thang tiến bộ: 0.1đ – 0.25đ – 0.5đ – 1.0đ), và Phần III (Trắc nghiệm trả lời ngắn).")

    p_math = doc.add_paragraph(style='List Bullet')
    p_math.paragraph_format.space_after = Pt(4)
    r = p_math.add_run("Chuẩn mực Công thức Toán học & Xuất bản Word/PDF: ")
    r.font.bold = True
    p_math.add_run("Công thức toán được nhúng dạng MathType 7.0 OLE Object Vector WMF (cho phép giáo viên click đúp chỉnh sửa 2 chiều trên Microsoft Word) kết hợp bộ phương trình bản địa Word OMML (<m:oMath>); tự động dựng hình TikZ vector và chuẩn hóa bảng LaTeX thành Word native table chống lỗi hộp đen (black box).")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # SECTION 3: CÁC YÊU CẦU CHỨC NĂNG CHÍNH CỦA PHẦN MỀM (10 PHÂN HỆ)
    # -------------------------------------------------------------
    p_s3 = doc.add_paragraph()
    r_s3 = p_s3.add_run("III. CÁC YÊU CẦU CHỨC NĂNG CHÍNH CỦA PHẦN MỀM (CORE FUNCTIONAL REQUIREMENTS)")
    r_s3.font.size = Pt(13)
    r_s3.font.bold = True
    r_s3.font.color.rgb = RGBColor(0, 51, 102)
    p_s3.paragraph_format.space_before = Pt(8)
    p_s3.paragraph_format.space_after = Pt(4)

    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_desc.add_run("Hệ thống Quesy được thiết kế kiến trúc theo chu trình khảo thí khép kín gồm ")
    r_bold = p_desc.add_run("10 phân hệ chức năng cốt lõi")
    r_bold.font.bold = True
    p_desc.add_run(", giải quyết trọn vẹn mọi rào cản kỹ thuật từ khâu thu nhận đề thô, bóc tách công thức toán, biên tập câu hỏi, trộn đề an toàn cho đến xuất bản và chấm điểm:")

    # Summary Matrix Table of 10 Modules
    tbl_mod_summary = doc.add_table(rows=11, cols=4)
    tbl_mod_summary.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_grid_borders(tbl_mod_summary, color="B0C4DE", sz="6")

    mod_headers = ["Mã Phân hệ", "Tên Phân hệ Chức năng", "Mục tiêu & Nghiệp vụ Trọng tâm", "Mức độ Ưu tiên"]
    mod_col_widths = [Mm(25), Mm(50), Mm(75), Mm(20)]

    for idx, text in enumerate(mod_headers):
        cell = tbl_mod_summary.rows[0].cells[idx]
        cell.text = text
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=120, bottom=120, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)

    modules_brief = [
        ("MOD-01", "Tiếp nhận & Số hóa Đề thi bằng AI (AI Ingestion)", "Bóc tách đa phương thức (DOCX, PDF, Ảnh), giải mã MathType OLE MTEF sang LaTeX chuẩn trong vài giây.", "Bắt buộc (P0)"),
        ("MOD-02", "Studio Hậu kiểm Đối chiếu (HITL Review Studio)", "Giao diện Dual-pane cuộn đồng bộ (<100ms), thanh đo độ tin cậy AI, chỉnh sửa đáp án/công thức 1-click.", "Bắt buộc (P0)"),
        ("MOD-03", "Dựng Đồ thị TikZ & Chuẩn hóa Toán học", "Biên dịch TikZ sang SVG, auto-clipping chống méo tiệm cận, chuẩn hóa \\left\\right, phân số \\dfrac, số thập phân {,}.", "Bắt buộc (P0)"),
        ("MOD-04", "Cây Kiến thức 6 Tầng & Dạng Câu hỏi", "Cây danh mục chuẩn TT 32/2018, liên kết mã YCCĐ, phân loại dạng bài chuyên sâu, tuyệt đối không có trường Bộ sách.", "Bắt buộc (P0)"),
        ("MOD-05", "Ngân hàng Câu hỏi & Chống trùng lặp AI", "Quản lý 5 hình thức thi QĐ 764, vector embeddings quét trùng lặp Cosine Similarity >= 90%, quản lý vòng đời.", "Bắt buộc (P0)"),
        ("MOD-06", "Ma trận Đề thi 2 Chiều & Solver Rút đề", "Thiết lập ma trận theo chuẩn kiến thức - nhận thức, kiểm tra tồn kho ngân hàng thời gian thực, rút đề gốc tối ưu.", "Bắt buộc (P0)"),
        ("MOD-07", "Động cơ Trộn Đề Hoán vị An toàn", "Bảo đảm 4 nguyên tắc: Option Anchor (khóa D), Passage Integrity (giữ bài đọc), Section Integrity, sinh ma trận đáp án.", "Bắt buộc (P0)"),
        ("MOD-08", "Xuất bản Đề thi Word MathType OLE & In ấn", "Xuất Word 2 cột A4 chuẩn font Times New Roman 11pt, MathType OLE WMF click đúp sửa trực tiếp, đóng gói ZIP trọn bộ.", "Bắt buộc (P0)"),
        ("MOD-09", "Chấm điểm Bậc thang & Quản lý Điểm", "Tự động chấm Đúng/Sai bậc thang (0.1 - 0.25 - 0.5 - 1.0), quản lý SBD lớp học, xuất Excel UTF-8 BOM chống lỗi font tiếng Việt.", "Quan trọng (P1)"),
        ("MOD-10", "Soạn đề LaTeX Trực tiếp & Trợ lý AI Copilot", "Workspace 6:4, editor dark mode hỗ trợ ex_test v3.3, Trợ lý AI popup bottom sheet, Live PDF preview đồng bộ zoom 100%.", "Bắt buộc (P0)"),
    ]

    for row_idx, data in enumerate(modules_brief, start=1):
        row = tbl_mod_summary.rows[row_idx]
        bg = "F9FBFE" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = row.cells[col_idx]
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=90, bottom=90, left=70, right=70)
            p = cell.paragraphs[0]
            if col_idx in [0, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.size = Pt(9)
                if col_idx == 0:
                    r.font.bold = True
                elif col_idx == 3:
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 102, 204)

    for row in tbl_mod_summary.rows:
        for idx, width in enumerate(mod_col_widths):
            row.cells[idx].width = width

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # DETAILED SPECIFICATION OF 10 MODULES
    # -------------------------------------------------------------
    detailed_modules = [
        {
            "num": "1",
            "code": "MOD-01",
            "name": "Phân hệ Tiếp nhận & Số hóa Đề thi bằng Trí tuệ Nhân tạo (AI Ingestion & Parsing Pipeline)",
            "goal": "Tự động chuyển đổi tài liệu đề thi thô ở mọi định dạng (PDF scan, ảnh chụp, DOCX) thành cơ sở dữ liệu câu hỏi số hóa có cấu trúc cao, giữ nguyên 100% công thức toán học và hình minh họa.",
            "features": [
                ("Tiếp nhận đa định dạng:", "Hỗ trợ tải lên tài liệu Microsoft Word (.docx, .doc), tài liệu PDF đa trang, chùm ảnh chụp (.png, .jpg, .jpeg, .webp) với cơ chế kéo thả trực quan và thanh tiến trình xử lý thời gian thực."),
                ("Giải mã nhị phân MathType OLE (MTEF to LaTeX):", "Phân tích cấu trúc OpenXML của file Word, quét tìm các đối tượng OLE Object và giải mã trực tiếp dòng nhị phân MTEF v5 sang mã nguồn LaTeX ($...$ inline, $$...$$ display), khắc phục triệt để lỗi mất công thức hoặc vỡ font khi sao chép."),
                ("Tiền xử lý hình ảnh thị giác (Computer Vision Preprocessing):", "Áp dụng thuật toán cân bằng góc nghiêng xoay trang (Deskew) và thuật toán khử bóng mờ thích nghi (Adaptive Binarization) đối với tài liệu scan/chụp ảnh để đạt độ nét 300 DPI trước khi nhận diện."),
                ("Bóc tách cấu trúc bằng Vision LLM Đa phương thức:", "Tích hợp mô hình AI thị giác chuyên sâu (Google Gemini 1.5, GPT-4o, Claude 3.5), ép khuôn đầu ra JSON Schema nghiêm ngặt: tách biệt Tiêu đề đề thi, Phần thi (I, II, III), Thân câu hỏi, Phương án lựa chọn (A, B, C, D), Lời giải và Đáp án."),
                ("Tự động nhận diện và cắt ảnh đồ thị / hình vẽ (Auto Image Crop):", "Thuật toán phát hiện tọa độ Bounding Box của hình học không gian, đồ thị hàm số, mạch điện; tự động cắt và lưu trữ WebP tối ưu dung lượng, gắn định danh [IMAGE:url] vào đúng vị trí văn bản."),
                ("Tự động phân tích bảng đáp án & Lời giải:", "Tự động phát hiện bảng đáp án ở cuối đề thi hoặc file đáp án đính kèm để gán cờ is_correct cho từng phương án và gộp lời giải chi tiết tương ứng.")
            ]
        },
        {
            "num": "2",
            "code": "MOD-02",
            "name": "Phân hệ Studio Hậu kiểm Đối chiếu Song song (HITL Review Studio)",
            "goal": "Cung cấp môi trường kiểm thử tương tác người - máy (Human-in-the-Loop) giúp giáo viên đối soát 100% chất lượng dữ liệu số hóa với tài liệu gốc trước khi phê duyệt vào ngân hàng.",
            "features": [
                ("Không gian đối chiếu song song (Dual-pane Split View):", "Bố cục 2 cột tràn toàn màn hình: cột trái hiển thị tài liệu gốc (PDF/Ảnh/Word Viewer), cột phải hiển thị luồng thẻ câu hỏi điện tử đã được render công thức KaTeX sắc nét."),
                ("Cuộn trang đồng bộ siêu tốc (Synchronized Scrolling):", "Khi giáo viên nhấp vào bất kỳ câu hỏi nào bên cột số hóa, tài liệu gốc bên cột trái tự động cuộn đến đúng vị trí trang chứa câu hỏi đó với độ trễ phản hồi cực thấp (< 100ms)."),
                ("Thanh đo mức độ tin cậy AI (Confidence Barometer):", "Tự động đánh giá chất lượng bóc tách theo 3 mức màu: Xanh (>=95% - Đạt chuẩn), Vàng (80-94% - Cần kiểm tra lại), Đỏ (<80% - Cảnh báo thiếu đáp án hoặc cú pháp toán nghi ngờ)."),
                ("Trình biên tập nhanh tại chỗ (In-place HITL Editor):", "Cho phép đổi đáp án đúng chỉ bằng 1 cú nhấp chuột lên nhãn A, B, C, D; nhấp đúp vào công thức để mở hộp soạn thảo LaTeX có xem trước trực tiếp; gán mã YCCĐ và cờ cố định vị trí (is_fixed)."),
                ("Giai đoạn đệm & Sắp xếp trang (Staging & Page Reorder):", "Xem trước thumbnail các trang đã tải lên, hỗ trợ đảo thứ tự trang, xóa trang thừa hoặc thêm trang bổ sung trước khi kích hoạt quy trình bóc tách AI.")
            ]
        },
        {
            "num": "3",
            "code": "MOD-03",
            "name": "Phân hệ Dựng Đồ Thị Vector SVG & Chuẩn Hóa Toán Học (TikZ Engine & LaTeX Sanitizer)",
            "goal": "Tự động tái tạo đồ thị hàm số và hình học toán học dưới dạng vector SVG sắc nét vô hạn, loại bỏ triệt để mọi lỗi hiển thị toán học KaTeX.",
            "features": [
                ("Biên dịch TikZ/PGFPlots sang Vector SVG qua Kroki:", "Tiếp nhận các đoạn mã nguồn TikZ trong câu hỏi và biên dịch sang đồ họa vector SVG sắc nét, độ phân giải vô hạn."),
                ("Bộ nhớ đệm đồ họa cục bộ (Local Disk Cache):", "Đồ thị SVG sau khi sinh được băm mã SHA-256 lưu trữ đệm tại ổ đĩa cục bộ, cho phép truy xuất tức thì (0ms latency) và hoạt động ngoại tuyến không cần kết nối mạng."),
                ("Thuật toán Khống chế khung hình tự động (Auto-clipping Plot Bounds):", "Tự động phát hiện miền tọa độ x, y của các hàm số có tiệm cận vọt lên vô cực (hàm phân thức bậc nhất/bậc nhất) và tự động chèn lệnh \\clip an toàn, loại bỏ hiện tượng co kéo méo mó khung đồ thị."),
                ("Hỗ trợ đồ thị độc lập trong từng phương án A, B, C, D:", "Hỗ trợ các câu hỏi nhận dạng đồ thị hàm số bằng cách hiển thị 4 đồ thị vector riêng biệt trong 4 thẻ phương án lựa chọn."),
                ("Bộ chuẩn hóa 4 yếu tố toán học:", "Tự động bọc ngoặc kích thước động \\left/\\right ôm trọn phân số; chuyển số thập phân Việt Nam sang {,} chống hở khoảng cách; nâng cấp phân số \\frac thành \\dfrac thoáng đẹp; chuẩn hóa vectơ \\vec thành \\overrightarrow.")
            ]
        },
        {
            "num": "4",
            "code": "MOD-04",
            "name": "Phân hệ Cây Kiến thức Chuẩn hóa 6 Tầng & Dạng Câu hỏi (Taxonomy & Problem Archetypes)",
            "goal": "Chuẩn hóa toàn bộ kho học liệu theo đúng Chương trình Giáo dục phổ thông 2018 (Thông tư 32/2018/TT-BGDĐT) và phân loại theo dạng bài tập khảo thí.",
            "features": [
                ("Kiến trúc Cây phân cấp chuẩn 6 tầng thống nhất toàn quốc:", "Môn học (Subject) -> Cấp học/Khối lớp (Grade) -> Mạch nội dung (Strand) -> Chủ đề/Chuyên đề (Topic) -> Bài học (Lesson) -> Yêu cầu cần đạt (YCCĐ)."),
                ("Quản lý Dạng câu hỏi chuyên đề (Problem Archetypes):", "Dưới mỗi YCCĐ cho phép thiết lập các dạng bài tập chi tiết (ví dụ: Dạng 1: Đọc đồ thị tìm cực trị; Dạng 2: Cực trị chứa tham số m; Dạng 3: Bài toán tối ưu thực tế), bảo đảm ma trận rút đề chính xác theo dạng bài."),
                ("Nguyên tắc Không phân chia theo Bộ sách giáo khoa:", "Trong cơ sở dữ liệu hoàn toàn không có trường 'Bộ sách', bảo đảm câu hỏi bám sát chuẩn năng lực quốc gia và có thể dùng chung cho mọi trường học trên toàn quốc."),
                ("Phân loại 3 mức độ nhận thức chuẩn TT 32:", "Áp dụng bảng động từ đo lường chuẩn: Nhận biết (nhận dạng, nhớ lại), Thông hiểu (mô tả, giải thích), Vận dụng (tính toán, chứng minh, giải quyết vấn đề thực tiễn).")
            ]
        },
        {
            "num": "5",
            "code": "MOD-05",
            "name": "Phân hệ Quản lý Ngân hàng Câu hỏi & Chống Trùng lặp AI (Item Bank & Vector Deduplication)",
            "goal": "Quản lý toàn diện vòng đời câu hỏi, phân quyền duyệt học liệu và kiểm soát chống trùng lặp câu hỏi bằng trí tuệ nhân tạo vector embeddings.",
            "features": [
                ("Hỗ trợ trọn vẹn 5 hình thức khảo thí (QĐ 764):", "Trắc nghiệm 4 lựa chọn (SINGLE_CHOICE), Trắc nghiệm Đúng/Sai 4 khẳng định con (TRUE_FALSE_GROUP), Trả lời ngắn (SHORT_ANSWER), Câu hỏi chùm bài đọc hiểu (PASSAGE_GROUP), và Tự luận (ESSAY)."),
                ("Kiểm soát trùng lặp thông minh bằng AI Vector Embeddings:", "Chuyển đổi nội dung câu hỏi thành vector đa chiều và đo khoảng cách Cosine Similarity trong CSDL: dưới 80% (an toàn), từ 80% đến dưới 90% (cảnh báo vàng câu tương tự), từ 90% trở lên (chặn lưu tự động và mở modal đối chiếu trực quan 2 câu hỏi)."),
                ("Quản lý vòng đời câu hỏi nghiêm ngặt (Item Lifecycle):", "Theo dõi trạng thái: Bản nháp (DRAFT) -> Chờ duyệt (PENDING_REVIEW) -> Đã duyệt vào ngân hàng (APPROVED) -> Lưu trữ (ARCHIVED)."),
                ("Lưu vết lịch sử thay đổi (Audit History):", "Ghi lại nhật ký phiên bản sửa đổi câu hỏi, định danh người thực hiện và mốc thời gian chi tiết phục vụ công tác thanh tra khảo thí.")
            ]
        },
        {
            "num": "6",
            "code": "MOD-06",
            "name": "Phân hệ Ma trận Đề thi 2 Chiều & Rút Đề theo Ràng buộc (Exam Matrix & Solver)",
            "goal": "Cho phép tổ bộ môn thiết kế bản đặc tả đề thi chuẩn và tự động rút đề thi gốc tối ưu thỏa mãn mọi ràng buộc khảo thí.",
            "features": [
                ("Lưới thiết kế ma trận 2 chiều (2D Test Blueprint Grid):", "Trục dọc thể hiện Cây kiến thức (Mạch nội dung -> YCCĐ -> Dạng câu hỏi); Trục ngang thể hiện 3 Mức độ nhận thức x Dạng thức câu hỏi; mỗi ô cấu hình số câu và số điểm."),
                ("Kiểm tra tồn kho ngân hàng thời gian thực (Inventory Validation):", "Hệ thống tự động đếm số lượng câu hỏi khả dụng đã duyệt trong kho, hiển thị chẩn đoán chính xác: 'Thiếu 2 câu [Vận dụng - Cực trị chứa tham số m]' nếu không đủ câu hỏi."),
                ("Động cơ Giải bài toán Ràng buộc (Constraint Satisfaction Solver):", "Thuật toán rút ngẫu nhiên có trọng số, loại trừ các câu hỏi đã xuất hiện trong danh sách kỳ thi gần đây (Exclusion List), ưu tiên câu hỏi có chỉ số độ phân biệt cao."),
                ("Tạo đề thi gốc (Master Exam):", "Tổng hợp và khóa cấu trúc đề thi gốc, phân bổ mã định danh và lưu trữ snapshot đề thi phục vụ bước trộn đề.")
            ]
        },
        {
            "num": "7",
            "code": "MOD-07",
            "name": "Phân hệ Động cơ Trộn Đề Hoán vị An toàn (Safe Shuffling Engine)",
            "goal": "Tạo ra N mã đề hoán vị (101, 102, 103, 104...) từ 1 đề gốc nhưng bảo đảm tuyệt đối tính logic học thuật và không làm sai lệch ý nghĩa câu hỏi.",
            "features": [
                ("Nguyên tắc Khóa Neo Phương án (Option Anchor Rule):", "Tự động phát hiện các phương án phụ thuộc vị trí tương đối như: 'Cả A và B đều đúng', 'Tất cả các đáp án trên', hoặc phương án có cờ is_fixed. Hệ thống bắt buộc luôn neo phương án này ở vị trí D cuối cùng, chỉ đảo nội bộ các phương án A, B, C độc lập."),
                ("Nguyên tắc Bảo toàn Ngữ cảnh Bài đọc chung (Passage Integrity):", "Bảo đảm đoạn văn bản đọc hiểu cha và chùm câu hỏi con đi kèm luôn được xếp liền kề nhau trong mọi mã đề hoán vị, không bao giờ bị xé lẻ hoặc nằm rải rác."),
                ("Nguyên tắc Bảo toàn Phân vùng Phần thi (Section Integrity):", "Câu hỏi chỉ đảo trong nội bộ từng phần thi: Phần I chỉ đảo trong Phần I, Phần II chỉ đảo trong Phần II, Phần III chỉ đảo trong Phần III."),
                ("Tự động sinh Ma trận Ánh xạ Đáp án chéo (Key Generator):", "Tự động xuất bảng đối chiếu đáp án chi tiết giữa đề gốc và từng mã đề hoán vị, phục vụ giáo viên chấm thi và rà soát kết quả.")
            ]
        },
        {
            "num": "8",
            "code": "MOD-08",
            "name": "Phân hệ Xuất bản Đề thi Word MathType OLE, OMML & In ấn 1-Click (Publishing Service)",
            "goal": "Xuất bản tài liệu đề thi và hướng dẫn giải chuẩn in ấn chỉ bằng 1 cú nhấp chuột, công thức toán sắc nét tuyệt đối và cho phép chỉnh sửa 2 chiều bằng MathType 7.",
            "features": [
                ("Xuất file Word (.docx) Chuẩn Khảo thí Quốc gia:", "Khổ giấy A4 Portrait (210 x 297 mm), lề trang chuẩn 1.5cm - 1.8cm, font Times New Roman 11pt, giãn dòng 1.15; tự động tạo bảng phách rọc, tiêu đề Sở/Trường và khung mã đề."),
                ("Công thức Toán MathType 7.0 OLE Object Vector WMF (Độc quyền):", "Sinh luồng OLE nhị phân CFB chứa MTEF v5 kèm ảnh đại diện Vector WMF chuẩn APM (1440 DPI, scale 32 units/pt). Đạt 100% vector thuần, cho phép giáo viên click đúp trong Microsoft Word để mở thẳng MathType 7 chỉnh sửa công thức bình thường."),
                ("Công thức Toán Microsoft Word OMML Native (<m:oMath>):", "Tích hợp chuyển đổi MathML sang phương trình bản địa Word, hỗ trợ chạy trơn tru trên mọi môi trường Linux/Docker không cần bộ Office cài sẵn."),
                ("Tự động chuyển đổi bảng LaTeX thành Word Native Table:", "Tự động phát hiện các mảng bảng phân phối tần số hoặc bảng biến thiên trong LaTeX và chuyển thành bảng Word thực tế (<w:tbl>) căn giữa có viền mảnh, chống lỗi hộp đen (black box) khi in PDF."),
                ("Đóng gói Trọn bộ Ấn phẩm Khảo thí trong file ZIP:", "Chỉ 1 click tải về trọn bộ: Đề thi Word từng mã đề, Hướng dẫn giải chi tiết từng mã đề, Bảng đáp án Excel UTF-8 BOM, Phiếu trả lời trắc nghiệm chuẩn máy chấm OMR và tệp PDF in ấn.")
            ]
        },
        {
            "num": "9",
            "code": "MOD-09",
            "name": "Phân hệ Chấm điểm Bậc thang Tiến bộ & Quản lý Điểm lớp học (Grade & Roster Management)",
            "goal": "Tự động hóa công tác chấm bài theo thang điểm lũy tiến 2025, quản lý danh sách học sinh và phân tích chỉ số khảo thí hậu kiểm.",
            "features": [
                ("Thuật toán Chấm điểm Đúng/Sai bậc thang chuẩn Quyết định 764:", "Tự động chấm dạng câu hỏi Đúng/Sai 4 khẳng định theo quy tắc lũy tiến chính xác: Đúng 1 ý = 0.1đ; Đúng 2 ý = 0.25đ; Đúng 3 ý = 0.5đ; Đúng cả 4 ý = 1.0đ."),
                ("Quản lý Danh sách Học sinh theo Lớp học (Classroom & Roster):", "Quản lý danh sách học sinh theo từng Lớp học và Số báo danh (SBD) / Mã học sinh, đáp ứng trực tiếp nhu cầu giảng dạy thực tế của giáo viên."),
                ("Nhập / Xuất Bảng điểm Excel tương thích UTF-8 BOM:", "Tự động chèn ký tự UTF-8 BOM vào file CSV/Excel, bảo đảm Microsoft Excel trên Windows mở trực tiếp hiển thị 100% tiếng Việt có dấu chuẩn xác, không bị lỗi font."),
                ("Phân tích Chỉ số Khảo thí Hậu kiểm (Item Psychometrics):", "Tự động tính toán Độ khó thực nghiệm (p) và Độ phân biệt (D). Tự động gắn cờ cảnh báo câu hỏi lỗi nếu D < 0.20 để tổ chuyên môn kịp thời tinh chỉnh ngân hàng.")
            ]
        },
        {
            "num": "10",
            "code": "MOD-10",
            "name": "Phân hệ Soạn đề LaTeX Trực tiếp & Trợ lý Trí tuệ Nhân tạo (LaTeX Workspace & AI Copilot)",
            "goal": "Cung cấp môi trường biên soạn đề thi chuyên nghiệp theo mô hình Split View 6:4, tích hợp Trợ lý AI thế hệ mới hỗ trợ đề xuất chỉnh sửa đúng dòng và xem trước PDF vector tức thì.",
            "features": [
                ("Giao diện Split View tỷ lệ ngang 6:4 chuẩn Noctorium / Open-Prism:", "Cột trái chiếm 60% chiều rộng dành cho Trình soạn thảo LaTeX toàn phần; Cột phải chiếm 40% hiển thị trực tiếp bản in PDF và nút BIÊN DỊCH độc lập; bố cục nằm gọn trong 1 trang màn hình không sinh cuộn ngoài (Zero-scroll)."),
                ("Trình soạn thảo LaTeX Dark Mode chuẩn gói lệnh ex_test.sty v3.3:", "Tích hợp sẵn bộ template chuẩn quốc gia: Trắc nghiệm 4 lựa chọn (\\choice), Đúng/Sai (\\choiceTF), Trả lời ngắn (\\shortans), Chèn hình bên chữ (\\immini), Bảng biến thiên (tkz-tab) và Lời giải chi tiết (\\begin{loigiai})."),
                ("Trợ lý Soạn thảo AI (Quesy Copilot) Đa trạng thái:", "Ở trạng thái thu nhỏ là thanh nổi hình viên thuốc (Compact Floating Pill) ở đáy editor; khi bấm mở sẽ bung lên Bottom Sheet Popup bo tròn chứa đầy đủ Lịch sử câu lệnh, nút làm mới, hộp nhập lệnh thông minh."),
                ("Đề xuất Thay đổi Trực tiếp (Smart AI Inline Diff Replacer):", "Khi người dùng yêu cầu AI chỉnh sửa (ví dụ: đổi cỡ chữ 11pt sang 12pt), AI không xóa toàn bộ code cũ mà chỉ đề xuất thay đổi đúng dòng chỉ định; giao diện hiển thị banner so sánh Diff (+ thêm, - bớt) kèm nút Đồng ý / Từ chối để người dùng duyệt."),
                ("Bộ biên dịch Hybrid 3 tầng & Engine XeTeX Tectonic:", "Tự động kết nối Remote Tectonic Docker API trên máy chủ chuyên dụng (armbian:8090), tự động nạp thư viện tcolorbox xparse và tự động bóc tách \\choice lồng trong \\immini chống crash biên dịch."),
                ("Trình xem trước PDF Vector Canvas (PDF.js) Đồng bộ Thu phóng 100%:", "Kết xuất tài liệu vector sắc nét, đồng bộ 100% giữa các nút bấm thu phóng (+, -, 1:1) và phím tắt Ctrl + cuộn chuột, tự động căn giữa trang giấy và theo dõi phân trang < Trang X / Y > thời gian thực.")
            ]
        }
    ]

    for mod in detailed_modules:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.space_before = Pt(8)
        p_m.paragraph_format.space_after = Pt(2)
        r_m = p_m.add_run(f"3.{mod['num']}. {mod['name']} ({mod['code']})")
        r_m.font.size = Pt(11.5)
        r_m.font.bold = True
        r_m.font.color.rgb = RGBColor(0, 51, 102)

        # Module Goal Box
        tbl_goal = doc.add_table(rows=1, cols=1)
        tbl_goal.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl_goal.columns[0].width = Mm(170)
        c_g = tbl_goal.cell(0, 0)
        c_g.text = f"Mục tiêu phân hệ: {mod['goal']}"
        set_cell_background(c_g, "F0F4F8")
        set_cell_margins(c_g, top=70, bottom=70, left=100, right=100)
        set_table_borders(tbl_goal, color="0071E3", sz="8")
        pg = c_g.paragraphs[0]
        pg.runs[0].font.italic = True
        pg.runs[0].font.size = Pt(10)
        pg.runs[0].font.color.rgb = RGBColor(40, 40, 40)

        # Features list
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        for f_title, f_desc in mod["features"]:
            p_feat = doc.add_paragraph(style='List Bullet')
            p_feat.paragraph_format.space_after = Pt(2)
            p_feat.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            rf_t = p_feat.add_run(f"{f_title} ")
            rf_t.font.bold = True
            rf_t.font.size = Pt(10.5)
            rf_d = p_feat.add_run(f_desc)
            rf_d.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECTION 4: YÊU CẦU PHI CHỨC NĂNG (NFR) & KIẾN TRÚC KỸ THUẬT
    # -------------------------------------------------------------
    p_s4 = doc.add_paragraph()
    r_s4 = p_s4.add_run("IV. YÊU CẦU PHI CHỨC NĂNG (NFR) VÀ KIẾN TRÚC CÔNG NGHỆ")
    r_s4.font.size = Pt(13)
    r_s4.font.bold = True
    r_s4.font.color.rgb = RGBColor(0, 51, 102)
    p_s4.paragraph_format.space_before = Pt(8)
    p_s4.paragraph_format.space_after = Pt(4)

    tbl_nfr = doc.add_table(rows=6, cols=3)
    tbl_nfr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_grid_borders(tbl_nfr, color="B0C4DE", sz="6")

    nfr_headers = ["Nhóm Yêu cầu", "Chỉ số Kỹ thuật & Tiêu chuẩn Đo lường", "Giải pháp Hiện thực trong Quesy"]
    nfr_widths = [Mm(35), Mm(65), Mm(70)]

    for idx, text in enumerate(nfr_headers):
        cell = tbl_nfr.rows[0].cells[idx]
        cell.text = text
        set_cell_background(cell, "1F497D")
        set_cell_margins(cell, top=100, bottom=100, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)

    nfr_data = [
        ("1. Hiệu năng & Tốc độ xử lý", "• Bóc tách đề thi 50 câu: < 180s.\n• Render đồ thị đệm: ~0ms.\n• Rút đề & trộn 4 mã đề: < 1.5s.\n• Sinh trọn bộ gói ZIP Word: < 3.0s.", "Ứng dụng kiến trúc bất đồng bộ FastAPI AsyncIO, Persistent Node.js MathJax worker daemon, bộ đệm 2 tầng (RAM LRU + Disk Cache SHA-256)."),
        ("2. Giao diện & Trải nghiệm (UI/UX)", "• Tuân thủ nghiêm ngặt Apple HIG.\n• Phản hồi xúc giác (scale 0.97).\n• Điều hướng SPA URL sạch (/path).\n• Bố cục Zero-scroll 100% viewport.", "Thiết kế Single Page Application với Vanilla JS thuần (Zero framework overhead), Tailwind CSS, Lucide icons, cơ chế deep-linking không bị lỗi 404 khi F5."),
        ("3. Độ chính xác & Toàn vẹn dữ liệu", "• Tỷ lệ parse công thức đúng: >= 90%.\n• Lỗi trật khớp logic hoán vị: 0%.\n• Lỗi vỡ font tiếng Việt Excel: 0%.", "Sử dụng Vision LLM có JSON Schema validation, thuật toán Safe Shuffling khóa neo cứng phương án phụ thuộc, xuất file CSV/Excel UTF-8 BOM chuẩn."),
        ("4. Tính tương thích & Xuất bản", "• File Word mở trực tiếp trên mọi phiên bản MS Word 2013-2024.\n• Chỉnh sửa 2 chiều qua MathType 7.\n• Khổ giấy in ấn A4 chuẩn Bộ GD&ĐT.", "Tích hợp động cơ tổng hợp MathType 7.0 OLE Vector WMF thuần Python với APM header, tự động chuyển mảng LaTeX sang native Word table, loại bỏ hoàn toàn ảnh raster mờ nét."),
        ("5. Khả năng Chịu lỗi & Vận hành", "• 100% pass Automated Test Suite (71/71 passed).\n• Tự động giải phóng cổng bận.\n• Diệt sạch tiến trình nền.", "Bộ kiểm thử tự động pytest bao phủ toàn diện 5 nhóm lỗi phần mềm, cơ chế auto-kill port và failover tự động trong start_server.py chống lỗi WinError 10048.")
    ]

    for row_idx, data in enumerate(nfr_data, start=1):
        row = tbl_nfr.rows[row_idx]
        bg = "F9FBFE" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate(data):
            cell = row.cells[col_idx]
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=70, right=70)
            p = cell.paragraphs[0]
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.bold = True
                    r.font.size = Pt(9)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                for r in p.runs:
                    r.font.size = Pt(9)

    for row in tbl_nfr.rows:
        for idx, width in enumerate(nfr_widths):
            row.cells[idx].width = width

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # SECTION 5: KẾ HOẠCH TRIỂN KHAI & TIÊU CHÍ NGHIỆM THU
    # -------------------------------------------------------------
    p_s5 = doc.add_paragraph()
    r_s5 = p_s5.add_run("V. KẾ HOẠCH THỰC HIỆN VÀ TIÊU CHÍ NGHIỆM THU ĐỀ TÀI")
    r_s5.font.size = Pt(13)
    r_s5.font.bold = True
    r_s5.font.color.rgb = RGBColor(0, 51, 102)
    p_s5.paragraph_format.space_before = Pt(8)
    p_s5.paragraph_format.space_after = Pt(4)

    p_plan = doc.add_paragraph()
    p_plan.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_plan.add_run("Đề tài áp dụng quy trình phát triển phần mềm chuẩn hóa với mô hình ")
    r_ag = p_plan.add_run("4 Agent chuyên trách khép kín")
    r_ag.font.bold = True
    p_plan.add_run(" (Agent 1: Phân tích kiến trúc & Đọc hiểu; Agent 2: Lập trình mã nguồn; Agent 3: Kiểm thử tự động Pytest; Agent 4: Blind Test trực tiếp trên trình duyệt thật). Sản phẩm bàn giao và tiêu chí nghiệm thu bao gồm:")

    deliverables = [
        ("Mã nguồn hoàn chỉnh (Source Code):", "Mã nguồn đầy đủ backend (FastAPI/Python 3.13) và frontend (SPA HTML/CSS/JS) đã được cấu hình tự động hóa, đóng gói sạch sẽ, kèm script start_server.py chạy 1-click."),
        ("Bộ kiểm thử tự động toàn diện (Test Suite):", "71/71 kịch bản kiểm thử tự động Pytest đạt 100% PASSED, bao phủ đầy đủ các ca kiểm thử tích hợp, API contract, logic chấm điểm bậc thang QĐ 764 và thuật toán trộn đề."),
        ("Bộ tài liệu kỹ thuật hoàn chỉnh (Full Technical Specs):", "Đầy đủ các hồ sơ tài liệu kỹ thuật chuẩn quốc tế lưu trữ tại thư mục docs/: BRD (Yêu cầu nghiệp vụ), SRS (Đặc tả hệ thống), FRD (Đặc tả chức năng), NFR (Yêu cầu phi chức năng), TEST (Kịch bản kiểm thử), và SOURCE_MAP (Bản đồ kiến trúc dự án)."),
        ("Sản phẩm phần mềm thực nghiệm (Running Artifact):", "Hệ thống vận hành trơn tru trên môi trường thực tế, kết nối thành công với Remote Tectonic XeTeX Engine Docker biên dịch đề thi sang PDF vector và xuất bản tệp Word MathType OLE hoàn hảo.")
    ]

    for d_title, d_desc in deliverables:
        p_d = doc.add_paragraph(style='List Bullet')
        p_d.paragraph_format.space_after = Pt(2)
        p_d.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        rd_t = p_d.add_run(f"{d_title} ")
        rd_t.font.bold = True
        rd_t.font.size = Pt(10.5)
        rd_d = p_d.add_run(d_desc)
        rd_d.font.size = Pt(10.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # -------------------------------------------------------------
    # SIGNATURE BLOCK
    # -------------------------------------------------------------
    tbl_sign = doc.add_table(rows=1, cols=2)
    tbl_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_sign.columns[0].width = Mm(85)
    tbl_sign.columns[1].width = Mm(85)

    cs0 = tbl_sign.cell(0, 0)
    ps0 = cs0.paragraphs[0]
    ps0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs0_1 = ps0.add_run("GIẢNG VIÊN HƯỚNG DẪN\n")
    rs0_1.font.bold = True
    rs0_1.font.size = Pt(11)
    rs0_2 = ps0.add_run("(Ký, ghi rõ họ tên và ý kiến phê duyệt)\n\n\n\n\n")
    rs0_2.font.italic = True
    rs0_2.font.size = Pt(9.5)
    rs0_3 = ps0.add_run("[Họ và tên Giảng viên hướng dẫn]")
    rs0_3.font.bold = True
    rs0_3.font.italic = True
    rs0_3.font.size = Pt(10.5)

    cs1 = tbl_sign.cell(0, 1)
    ps1 = cs1.paragraphs[0]
    ps1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rs1_1 = ps1.add_run("Hà Nội, ngày ...... tháng ...... năm 2026\n")
    rs1_1.font.italic = True
    rs1_1.font.size = Pt(10)
    rs1_2 = ps1.add_run("ĐẠI DIỆN NHÓM SINH VIÊN (TRƯỞNG NHÓM)\n")
    rs1_2.font.bold = True
    rs1_2.font.size = Pt(11)
    rs1_3 = ps1.add_run("(Ký và ghi rõ họ tên)\n\n\n\n\n")
    rs1_3.font.italic = True
    rs1_3.font.size = Pt(9.5)
    rs1_4 = ps1.add_run("[Họ và tên Sinh viên Trưởng nhóm]")
    rs1_4.font.bold = True
    rs1_4.font.italic = True
    rs1_4.font.size = Pt(10.5)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Successfully generated DOCX report at: {output_path}")

if __name__ == "__main__":
    out_file = Path("Bao_Cao_Dang_Ky_De_Tai_Phan_Mem_Quesy.docx").resolve()
    if len(sys.argv) > 1:
        out_file = Path(sys.argv[1]).resolve()
    build_report_document(out_file)
