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

    # Tiêu đề 2 cột chuẩn 0.38\textwidth / 0.58\textwidth và căn giữa
    assert r"\begin{minipage}{0.38\textwidth}" in latex_exam
    assert r"\begin{minipage}{0.58\textwidth}" in latex_exam
    assert r"\centering \textbf{TRƯỜNG THPT CHUYÊN}\\" in latex_exam
    assert r"\centering \textbf{KỲ THI TỐT NGHIỆP TRUNG HỌC PHỔ THÔNG}\\" in latex_exam
    assert r"\framebox{\textbf{Mã đề: 205}}" in latex_exam

    # PHẦN I
    assert r"\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.}" in latex_exam
    assert r"\choice{" in latex_exam
    assert r"\begin{center}" in latex_exam
    assert r"\begin{tikzpicture}" in latex_exam

    # PHẦN II có reset câu về 1 bằng \setcounter{ex}{0} và \choiceTF[1]
    assert r"\setcounter{ex}{0}" in latex_exam
    assert r"\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.}" in latex_exam
    assert r"\choiceTF[1]" in latex_exam

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
            variants = generate_shuffled_variants(master.id, db, ["101", "102"])

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

