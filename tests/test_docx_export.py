from pathlib import Path
from backend.services.docx_exporter import generate_digitized_exam_pdf

def test_docx_export_2_columns_header_and_equations(tmp_path):
    """Test generating an exam PDF paper with header, questions, and equations."""
    questions = [
        {
            "id": 1,
            "item_format": "SINGLE_CHOICE",
            "stem": "Cho hàm số y = f(x) xác định trên R. Giá trị cực tiểu của hàm số $y = x^3 - 3x + 2$ là:",
            "options": [
                {"label": "A", "content": "$y_{CT} = 0$"},
                {"label": "B", "content": "$y_{CT} = 4$"},
                {"label": "C", "content": "$y_{CT} = 2$"},
                {"label": "D", "content": "$y_{CT} = -2$"},
            ]
        },
        {
            "id": 2,
            "item_format": "SINGLE_CHOICE",
            "stem": r"Tìm nguyên hàm của hàm số $f(x) = \int e^{2x} dx$.",
            "options": [
                {"label": "A", "content": r"$\dfrac{1}{2} e^{2x} + C$"},
                {"label": "B", "content": r"$2 e^{2x} + C$"},
                {"label": "C", "content": r"$e^{2x} + C$"},
                {"label": "D", "content": "Cả A và B đều đúng"},
            ]
        }
    ]

    output_path = tmp_path / "De_Thi_101.pdf"
    ok = generate_digitized_exam_pdf(
        questions=questions,
        output_pdf=output_path,
        title="ĐỀ KHẢO SÁT CHẤT LƯỢNG HỌC KỲ I - NĂM HỌC 2025 - 2026",
        school_name="SỞ GD&ĐT HÀ NỘI - TRƯỜNG THPT CHUYÊN",
        subject_name="MÔN: TOÁN HỌC - LỚP 12",
        variant_code="101"
    )

    assert ok is True
    assert output_path.exists()
    assert output_path.stat().st_size > 500
    with open(output_path, "rb") as f:
        assert f.read(4) == b"%PDF"


def test_generate_variant_latex_structure_and_national_standards():
    """Kiểm thử generate_variant_latex: Tạo mã nguồn LaTeX thuần chuẩn Bộ GD&ĐT 2025:
    - Tiêu đề 2 cột: minipage {0.38\\textwidth} và minipage {0.58\\textwidth}, \\centering.
    - PHẦN I: \\choice{...}{...}{...}{...}, \\begin{ex} ... \\end{ex}.
    - PHẦN II: \\setcounter{ex}{0}, \\choiceTF[1], \\begin{itemchoice} (khi is_solution=True).
    - PHẦN III: \\setcounter{ex}{0}, \\shortans{...}.
    - Đồ thị TikZ căn giữa \\begin{center} \\begin{tikzpicture} ... \\end{tikzpicture} \\end{center}.
    - Khi is_solution=True: chứa môi trường \\begin{loigiai} ... \\end{loigiai}.
    """
    from types import SimpleNamespace
    from backend.services.docx_exporter import generate_variant_latex

    # Mock Question 1: Single choice có đồ thị TikZ căn giữa
    q1 = SimpleNamespace(
        id="q1",
        item_format="SINGLE_CHOICE",
        stem=("Cho hàm số $y=f(x)$ liên tục trên $\\mathbb{R}$. Đồ thị như hình vẽ:\n"
              "\\begin{center}\n"
              "\\begin{tikzpicture}[scale=0.8]\n"
              "\\draw[->] (-2,0) -- (2,0) node[right] {$x$};\n"
              "\\draw[->] (0,-1) -- (0,3) node[above] {$y$};\n"
              "\\draw[domain=-1.5:1.5,smooth,blue] plot (\\x,{(\\x)*(\\x)});\n"
              "\\end{tikzpicture}\n"
              "\\end{center}\n"
              "Điểm cực tiểu của hàm số đã cho là:"),
        options=[
            SimpleNamespace(label="A", content="$x = 0$", is_correct=True),
            SimpleNamespace(label="B", content="$x = 1$", is_correct=False),
            SimpleNamespace(label="C", content="$x = -1$", is_correct=False),
            SimpleNamespace(label="D", content="$x = 2$", is_correct=False),
        ],
        sub_statements=[],
        short_answer_key=None,
        explanation="Từ đồ thị, hàm số đạt cực tiểu tại điểm $x = 0$ với giá trị cực tiểu $y = 0$."
    )
    it1 = SimpleNamespace(
        variant_order_index=1,
        question=q1,
        option_mapping={"A": "A", "B": "B", "C": "C", "D": "D"},
        answer_key="A"
    )

    # Mock Question 2: Đúng / Sai 4 ý
    q2 = SimpleNamespace(
        id="q2",
        item_format="TRUE_FALSE_GROUP",
        stem="Cho hàm số $y = \\dfrac{2x - 1}{x + 1}$. Xét tính đúng sai của các khẳng định sau:",
        options=[],
        sub_statements=[
            SimpleNamespace(content="Tập xác định $D = \\mathbb{R} \\setminus \\{-1\\}$.", is_true=True, explanation="Mẫu $x + 1 \\neq 0 \\Leftrightarrow x \\neq -1$."),
            SimpleNamespace(content="Đồ thị hàm số có tiệm cận đứng $x = 1$.", is_true=False, explanation="Tiệm cận đứng là $x = -1$, không phải $x = 1$."),
            SimpleNamespace(content="Đồ thị hàm số có tiệm cận ngang $y = 2$.", is_true=True, explanation="Bậc tử bằng bậc mẫu, $\\lim_{x \\to \\pm\\infty} y = 2$."),
            SimpleNamespace(content="Hàm số nghịch biến trên từng khoảng xác định.", is_true=False, explanation="Đạo hàm $y' = 3/(x+1)^2 > 0$, hàm số đồng biến."),
        ],
        short_answer_key=None,
        explanation="Xét chi tiết từng khẳng định a, b, c, d."
    )
    it2 = SimpleNamespace(
        variant_order_index=2,
        question=q2,
        option_mapping=None,
        answer_key="Đ-S-Đ-S"
    )

    # Mock Question 3: Trả lời ngắn
    q3 = SimpleNamespace(
        id="q3",
        item_format="SHORT_ANSWER",
        stem="Cho hình chóp $S.ABC$ có đáy $ABC$ là tam giác vuông tại $B$, $AB=3$, $BC=4$. Cạnh bên $SA \\perp (ABC)$ và $SA=5$. Tính thể tích $V$ của khối chóp $S.ABC$.",
        options=[],
        sub_statements=[],
        short_answer_key="10",
        explanation="Diện tích đáy $S_{ABC} = \\dfrac{1}{2} \\times 3 \\times 4 = 6$. Thể tích $V = \\dfrac{1}{3} S_{ABC} \\times SA = 10$."
    )
    it3 = SimpleNamespace(
        variant_order_index=3,
        question=q3,
        option_mapping=None,
        answer_key="10"
    )

    variant = SimpleNamespace(
        variant_code="205",
        items=[it1, it2, it3],
        master_exam=SimpleNamespace(
            title="Đề Thi Thử Tốt Nghiệp THPT 2025",
            subject=SimpleNamespace(name="Toán học", code="TOAN")
        )
    )

    # 1. Kiểm thử tạo mã LaTeX cho Đề thi (is_solution=False)
    latex_exam = generate_variant_latex(variant, is_solution=False)  # type: ignore[arg-type]

    # Tiêu đề 2 cột canonical 0.38\textwidth / 0.58\textwidth [t] và căn giữa, không có \begin{center} bọc ngoài
    assert not latex_exam.startswith(r"\begin{center}")
    assert r"\begin{minipage}[t]{0.38\textwidth}" in latex_exam
    assert r"\begin{minipage}[t]{0.58\textwidth}" in latex_exam
    assert r"\textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO}" in latex_exam
    assert r"\textbf{TRƯỜNG THPT CHUYÊN}" in latex_exam
    assert r"\textbf{KỲ THI TỐT NGHIỆP THPT}" in latex_exam
    assert r"\textbf{MÔN TOÁN}" in latex_exam
    assert r"\framebox{\textbf{Mã đề: 205}}" in latex_exam
    assert r"\rule{\textwidth}{0.5pt}" in latex_exam

    # PHẦN I
    assert r"\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.}" in latex_exam
    assert r"\choice{" in latex_exam
    assert r"\begin{center}" in latex_exam
    assert r"\begin{tikzpicture}" in latex_exam
    assert "QQQBLOCKLATEXSAFE" not in latex_exam

    # PHẦN II có reset câu về 1 bằng \setcounter{ex}{0} và \choiceTF[1] với từng khẳng định bọc trong ngoặc nhọn {...}
    assert r"\setcounter{ex}{0}" in latex_exam
    assert r"\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.}" in latex_exam
    assert r"\choiceTF[1]" in latex_exam
    assert r"{\True Tập xác định" in latex_exam
    assert r"{Đồ thị hàm số có tiệm cận đứng" in latex_exam
    assert r"{\True Đồ thị hàm số có tiệm cận ngang" in latex_exam
    assert r"{Hàm số nghịch biến trên từng khoảng xác định.}" in latex_exam

    # PHẦN III có reset câu về 1 và \shortans
    assert r"\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.}" in latex_exam
    assert r"\shortans{10}" in latex_exam

    # Đề thi không chứa môi trường loigiai
    assert r"\begin{loigiai}" not in latex_exam
    assert r"\textbf{--- HẾT ---}" in latex_exam

    # 2. Kiểm thử tạo mã LaTeX cho Hướng dẫn giải (is_solution=True)
    latex_sol = generate_variant_latex(variant, is_solution=True)  # type: ignore[arg-type]
    assert r"\begin{loigiai}" in latex_sol
    assert r"\end{loigiai}" in latex_sol
    assert r"\begin{itemchoice}" in latex_sol
    assert r"\itemch" in latex_sol
    assert r"\True $x = 0$" in latex_sol


def test_export_single_variant_pdf(tmp_path):
    """Kiểm thử export_single_variant_pdf: tạo tệp PDF vector hợp lệ (b'%PDF')."""
    from types import SimpleNamespace
    from backend.services.docx_exporter import export_single_variant_pdf

    q = SimpleNamespace(
        id="q_single",
        item_format="SINGLE_CHOICE",
        stem="Giá trị lớn nhất của hàm số $f(x) = -x^2 + 4x + 1$ trên đoạn $[0; 3]$ bằng:",
        options=[
            SimpleNamespace(label="A", content="$5$", is_correct=True),
            SimpleNamespace(label="B", content="$4$", is_correct=False),
            SimpleNamespace(label="C", content="$1$", is_correct=False),
            SimpleNamespace(label="D", content="$-2$", is_correct=False),
        ],
        sub_statements=[],
        short_answer_key=None,
        explanation="Hàm số có đỉnh $x = 2 \\in [0; 3]$, $f(2) = 5$."
    )
    item = SimpleNamespace(
        variant_order_index=1,
        question=q,
        option_mapping={"A": "A", "B": "B", "C": "C", "D": "D"},
        answer_key="A"
    )
    variant = SimpleNamespace(
        variant_code="102",
        items=[item],
        master_exam=SimpleNamespace(
            title="Đề Khảo Sát Toán 12",
            subject=SimpleNamespace(name="Toán học", code="TOAN")
        )
    )

    out_file = tmp_path / "De_102.pdf"
    res_path = export_single_variant_pdf(variant, out_file)  # type: ignore[arg-type]

    assert res_path.exists()
    assert res_path.stat().st_size > 500
    with open(res_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF", f"Tệp PDF phải bắt đầu bằng %PDF, nhận được: {header}"


def test_export_exam_package_zip_comprehensive():
    """Kiểm thử export_exam_package_zip: Đóng gói đầy đủ trọn bộ ấn phẩm khảo thí:
    - De_{code}.pdf cho tất cả mã đề (Vector PDF hợp lệ %PDF).
    - LoiGiai_{code}.pdf cho tất cả mã đề (Vector PDF hợp lệ %PDF).
    - BangDapAn_TongHop.pdf (%PDF).
    - BangDapAn_TongHop.csv (Bắt đầu bằng UTF-8 BOM \\xef\\xbb\\xbf).
    - Phieu_Tra_Loi_Trac_Nghiem_2025.pdf (%PDF).
    """
    import zipfile
    import pytest
    from backend.database import SessionLocal
    from backend.models import MasterExam, ExamVariant
    from backend.services.docx_exporter import export_exam_package_zip

    db = SessionLocal()
    try:
        master = db.query(MasterExam).first()
        if not master:
            pytest.skip("Chưa có MasterExam trong database để kiểm thử export_exam_package_zip")

        variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master.id).all()
        if not variants:
            from backend.services.shuffling_engine import generate_shuffled_variants
            variants = generate_shuffled_variants(master.id, db, ["101"])
        elif len(variants) > 1:
            for extra_v in variants[1:]:
                db.delete(extra_v)
            db.commit()
            variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master.id).all()

        zip_str = export_exam_package_zip(master.id, db)
        zip_path = Path(zip_str)

        assert zip_path.exists()
        assert zip_path.stat().st_size > 1000

        with zipfile.ZipFile(zip_path, "r") as zf:
            namelist = zf.namelist()

            for v in variants:
                de_name = f"De_{v.variant_code}.pdf"
                lg_name = f"LoiGiai_{v.variant_code}.pdf"
                assert de_name in namelist, f"Thiếu {de_name} trong gói ZIP"
                assert lg_name in namelist, f"Thiếu {lg_name} trong gói ZIP"

                de_bytes = zf.read(de_name)
                assert de_bytes.startswith(b"%PDF"), f"{de_name} không phải file PDF hợp lệ"

                lg_bytes = zf.read(lg_name)
                assert lg_bytes.startswith(b"%PDF"), f"{lg_name} không phải file PDF hợp lệ"

            assert "BangDapAn_TongHop.pdf" in namelist
            mat_bytes = zf.read("BangDapAn_TongHop.pdf")
            assert mat_bytes.startswith(b"%PDF"), "BangDapAn_TongHop.pdf không phải PDF hợp lệ"

            assert "BangDapAn_TongHop.csv" in namelist
            csv_bytes = zf.read("BangDapAn_TongHop.csv")
            assert csv_bytes.startswith(b"\xef\xbb\xbf"), "BangDapAn_TongHop.csv phải có UTF-8 BOM"

            assert "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf" in namelist
            omr_bytes = zf.read("Phieu_Tra_Loi_Trac_Nghiem_2025.pdf")
            assert omr_bytes.startswith(b"%PDF"), "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf không phải PDF hợp lệ"

        if zip_path.exists():
            zip_path.unlink()
    finally:
        db.close()


def test_sanitize_latex_for_xetex_comprehensive():
    """Kiểm thử sanitize_latex_for_xetex:
    - Bare underscores như PERSIST_13951386, var_name ngoài math mode được escape thành \\_.
    - Ký tự % và & ngoài math mode được escape thành \\% và \\&.
    - Subscripts toán học như $x_1$, $$y_{max}$$, \\(a_i\\) giữ nguyên vẹn.
    - TikZ environments và các khối lồng nhau giữ nguyên vẹn, không để sót placeholder QQQBLOCKLATEXSAFE.
    """
    from backend.services.latex_converter import sanitize_latex_for_xetex

    # 1. Bare underscores ngoài math mode
    inp1 = "Câu hỏi kiểm thử PERSIST_13951386 với biến var_name và param_val_2."
    exp1 = r"Câu hỏi kiểm thử PERSIST\_13951386 với biến var\_name và param\_val\_2."
    assert sanitize_latex_for_xetex(inp1) == exp1

    # 2. Toàn vẹn subscripts trong math mode ($...$, $$...$$, \[...\])
    inp2 = "Cho hàm số $y = f(x_1)$ với $x_1 < x_2$ và $$y_{max} = \\max_{x \\in D} f(x)$$."
    res2 = sanitize_latex_for_xetex(inp2)
    assert "$y = f(x_1)$" in res2
    assert "$x_1 < x_2$" in res2
    assert "$$y_{max} = \\max_{x \\in D} f(x)$$" in res2
    assert "x\\_1" not in res2
    assert "y\\_{max}" not in res2

    # 3. Ký tự % và & ngoài math mode được escape
    inp3 = "Tỉ lệ đạt 95% & xếp loại Giỏi."
    exp3 = r"Tỉ lệ đạt 95\% \& xếp loại Giỏi."
    assert sanitize_latex_for_xetex(inp3) == exp3

    # 4. TikZ đơn lẻ và lồng trong \\begin{center}
    inp4 = (
        "Đồ thị hàm số như hình vẽ:\n"
        "\\begin{center}\n"
        "\\begin{tikzpicture}[scale=0.8]\n"
        "\\draw[->] (-2,0) -- (2,0) node[right] {$x_1$};\n"
        "\\draw[->] (0,-1) -- (0,3) node[above] {$y_{max}$};\n"
        "\\draw[domain=-1.5:1.5,smooth,blue] plot (\\x,{(\\x)*(\\x)});\n"
        "\\end{tikzpicture}\n"
        "\\end{center}\n"
        "với biến test_flag_01."
    )
    res4 = sanitize_latex_for_xetex(inp4)
    assert "test\\_flag\\_01" in res4
    assert "\\begin{tikzpicture}[scale=0.8]" in res4
    assert "\\end{tikzpicture}" in res4
    assert "node[right] {$x_1$}" in res4
    assert "node[above] {$y_{max}$}" in res4
    assert "QQQBLOCKLATEXSAFE" not in res4


def test_generate_variant_latex_choice_tf_braces_and_canonical_header():
    """Kiểm thử cấu trúc generate_variant_latex:
    - \\choiceTF[1] BẮT BUỘC có cặp ngoặc nhọn {...} quanh từng khẳng định con.
    - Tuyệt đối không có khẳng định trần không ngoặc nhọn.
    - Header 2 cột canonical chuẩn (minipage [t] 0.38\\textwidth và 0.58\\textwidth, \\centering, \\hfill, \\rule{\\textwidth}{0.5pt}).
    - Không có \\begin{center} bọc ngoài 2 minipage.
    - Cuối tài liệu có vĩ thanh \\begin{center}\\textbf{--- HẾT ---}\\end{center}.
    """
    from types import SimpleNamespace
    from backend.services.docx_exporter import generate_variant_latex

    q_tf = SimpleNamespace(
        id="q_tf_check",
        item_format="TRUE_FALSE_GROUP",
        stem="Xét tính đúng sai của hàm số $y = f(x)$ với biến config_id:",
        options=[],
        sub_statements=[
            SimpleNamespace(content="Khẳng định thứ nhất với $x_1 = 0$", is_true=True, explanation="Giải thích 1"),
            SimpleNamespace(content="Khẳng định thứ hai với $x_2 = 1$", is_true=False, explanation="Giải thích 2"),
            SimpleNamespace(content="Khẳng định thứ ba với $x_3 = 2$", is_true=True, explanation="Giải thích 3"),
            SimpleNamespace(content="Khẳng định thứ tư với $x_4 = 3$", is_true=False, explanation="Giải thích 4"),
        ],
        short_answer_key=None,
        explanation="Hướng dẫn giải toàn diện."
    )
    item_tf = SimpleNamespace(
        variant_order_index=1,
        question=q_tf,
        option_mapping=None,
        answer_key="Đ-S-Đ-S"
    )
    variant = SimpleNamespace(
        variant_code="301",
        items=[item_tf],
        master_exam=SimpleNamespace(
            title="Đề Khảo Sát Toán Chuẩn",
            subject=SimpleNamespace(name="Toán học", code="TOAN")
        )
    )

    latex_code = generate_variant_latex(variant, is_solution=False)  # type: ignore[arg-type]

    # 1. Header canonical checks
    assert not latex_code.startswith(r"\begin{center}")
    assert r"\begin{minipage}[t]{0.38\textwidth}" in latex_code
    assert r"\begin{minipage}[t]{0.58\textwidth}" in latex_code
    assert r"\framebox{\textbf{Mã đề: 301}}" in latex_code
    assert r"\rule{\textwidth}{0.5pt}" in latex_code

    # 2. \choiceTF[1] checks: tất cả khẳng định BẮT BUỘC bọc trong {...}
    assert r"\choiceTF[1]" in latex_code
    tf_idx = latex_code.find(r"\choiceTF[1]")
    tf_block = latex_code[tf_idx:].split(r"\end{ex}")[0]
    tf_lines = [line.strip() for line in tf_block.splitlines() if line.strip() and line.strip() != r"\choiceTF[1]"]

    assert len(tf_lines) == 4, f"Cần đúng 4 khẳng định con, hiện có {len(tf_lines)}"
    for idx, line in enumerate(tf_lines):
        assert line.startswith("{") and line.endswith("}"), f"Khẳng định #{idx+1} '{line}' không được bọc trong cặp ngoặc nhọn {{...}}"

    # 3. Vĩ thanh cuối tài liệu
    assert r"\begin{center}\textbf{--- HẾT ---}\end{center}" in latex_code


def test_pure_vector_pdf_tectonic_compilation_no_fallback_on_persist_and_tf(tmp_path):
    """Kiểm thử biên dịch thực tế của đề thi từng bị lỗi 'Missing $ inserted':
    - Đề thi chứa tag 'PERSIST_13951386' và câu hỏi Đúng/Sai 4 ý với subscripts.
    - Xác nhận biên dịch Tectonic XeTeX thành công 100% ra file Vector PDF sắc nét (>10KB, bắt đầu bằng b'%PDF').
    - Không bị fallback sang ReportLab (cả đề thi lẫn hướng dẫn giải).
    """
    from types import SimpleNamespace
    from backend.services.docx_exporter import generate_variant_pdf, generate_solution_pdf

    q1 = SimpleNamespace(
        id="q_persist",
        item_format="SINGLE_CHOICE",
        stem="Câu hỏi kiểm thử PERSIST_13951386: Cho hàm số $f'(x) = 3x^2 - 6x$. Giá trị cực tiểu $y_{min}$ là:",
        options=[
            SimpleNamespace(label="A", content="$y_{min} = -4$", is_correct=True),
            SimpleNamespace(label="B", content="$y_{min} = 0$", is_correct=False),
            SimpleNamespace(label="C", content="$y_{min} = 4$", is_correct=False),
            SimpleNamespace(label="D", content="$y_{min} = -2$", is_correct=False),
        ],
        sub_statements=[],
        short_answer_key=None,
        explanation="Đạo hàm $f'(x) = 0 \\Leftrightarrow x = 0$ hoặc $x = 2$. Cực tiểu tại $x = 2$."
    )
    it1 = SimpleNamespace(
        variant_order_index=1,
        question=q1,
        option_mapping={"A": "A", "B": "B", "C": "C", "D": "D"},
        answer_key="A"
    )

    q2 = SimpleNamespace(
        id="q_tf_persist",
        item_format="TRUE_FALSE_GROUP",
        stem="Cho hàm số $y = \\dfrac{2x - 1}{x + 1}$ với hệ số a_coef và b_coef. Xét các khẳng định:",
        options=[],
        sub_statements=[
            SimpleNamespace(content="Tập xác định $D = \\mathbb{R} \\setminus \\{-1\\}$.", is_true=True, explanation="Mẫu $x + 1 \\neq 0$."),
            SimpleNamespace(content="Tiệm cận đứng là đường thẳng $x = -1$.", is_true=True, explanation="Nghiệm mẫu số."),
            SimpleNamespace(content="Tiệm cận ngang là đường thẳng $y = 2$.", is_true=True, explanation="Bậc tử bằng bậc mẫu."),
            SimpleNamespace(content="Hàm số nghịch biến trên từng khoảng xác định.", is_true=False, explanation="Đạo hàm dương, đồng biến."),
        ],
        short_answer_key=None,
        explanation="Giải thích chi tiết 4 khẳng định a, b, c, d."
    )
    it2 = SimpleNamespace(
        variant_order_index=2,
        question=q2,
        option_mapping=None,
        answer_key="Đ-Đ-Đ-S"
    )

    q3 = SimpleNamespace(
        id="q_sa_persist",
        item_format="SHORT_ANSWER",
        stem="Cho khối lăng trụ tam giác có diện tích đáy $S = 6$ và chiều cao $h = 5$. Thể tích $V$ là:",
        options=[],
        sub_statements=[],
        short_answer_key="30",
        explanation="Thể tích $V = S \\times h = 30$."
    )
    it3 = SimpleNamespace(
        variant_order_index=3,
        question=q3,
        option_mapping=None,
        answer_key="30"
    )

    variant = SimpleNamespace(
        variant_code="901",
        items=[it1, it2, it3],
        master_exam=SimpleNamespace(
            title="Kỳ Thi Tốt Nghiệp THPT - Bài Thi Toán",
            subject=SimpleNamespace(name="Toán học", code="TOAN")
        )
    )

    exam_pdf = tmp_path / "De_901.pdf"
    sol_pdf = tmp_path / "LoiGiai_901.pdf"

    # 1. Biên dịch Đề thi thành Vector PDF qua Tectonic XeTeX
    ok_exam = generate_variant_pdf(variant, exam_pdf)  # type: ignore[arg-type]
    assert ok_exam is True, "Biên dịch Đề thi thành PDF qua Tectonic thất bại"
    assert exam_pdf.exists(), "Tệp De_901.pdf không tồn tại"
    size_exam = exam_pdf.stat().st_size
    assert size_exam > 10000, f"Kích thước PDF ({size_exam} bytes) quá nhỏ, nghi vấn fallback"
    exam_bytes = exam_pdf.read_bytes()
    assert exam_bytes.startswith(b"%PDF"), "De_901.pdf không bắt đầu bằng %PDF header"

    # 2. Biên dịch Hướng dẫn giải thành Vector PDF qua Tectonic XeTeX
    ok_sol = generate_solution_pdf(variant, sol_pdf)  # type: ignore[arg-type]
    assert ok_sol is True, "Biên dịch Hướng dẫn giải thành PDF qua Tectonic thất bại"
    assert sol_pdf.exists(), "Tệp LoiGiai_901.pdf không tồn tại"
    size_sol = sol_pdf.stat().st_size
    assert size_sol > 10000, f"Kích thước LoiGiai_901.pdf ({size_sol} bytes) quá nhỏ, nghi vấn fallback"
    sol_bytes = sol_pdf.read_bytes()
    assert sol_bytes.startswith(b"%PDF"), "LoiGiai_901.pdf không bắt đầu bằng %PDF header"

