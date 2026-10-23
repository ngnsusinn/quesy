import io
from pathlib import Path
from backend.services.docx_exporter import (
    clean_math_expr,
    generate_digitized_exam_pdf
)
from backend.services.latex_pdf_exporter import (
    render_math_html,
    clean_math_fallback_text
)

def test_clean_math_expr():
    assert clean_math_expr(r"${\overrightarrow{IJ} = \dfrac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}\right)}$") == r"\overrightarrow{IJ} = \dfrac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}\right)"
    assert clean_math_expr(r"${u_1 = 3}$") == "u_1 = 3"
    assert clean_math_expr(r"$u_6 = -96$") == "u_6 = -96"
    assert clean_math_expr(r"$$x^2 + 1$$") == "x^2 + 1"
    assert clean_math_expr(r"{\alpha + \beta}") == r"\alpha + \beta"

def test_add_math_text_omml_and_mathtype_and_latex():
    formula = r"${\overrightarrow{IJ} = \dfrac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}\right)}$"
    rendered = render_math_html(f"Cho tứ diện ABCD, {formula}.")
    assert "<span class=\"math-svg\"" in rendered or "<svg" in rendered

def test_generate_digitized_exam_formats(tmp_path: Path):
    questions = [
        {
            "id": 1,
            "item_format": "SINGLE_CHOICE",
            "stem": r"Cho tứ diện $ABCD$, gọi $I, J$ lần lượt là trung điểm của $AB$ và $CD$. Đẳng thức nào sau đây đúng?",
            "options": [
                {"label": "A", "content": r"${\overrightarrow{IJ} = \dfrac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}\right)}$"},
                {"label": "B", "content": r"${u_1 = 3}$"},
                {"label": "C", "content": r"${u_6 = -96}$"},
                {"label": "D", "content": r"${\overrightarrow{AB} + \overrightarrow{BC} = \overrightarrow{AC}}$"}
            ]
        }
    ]

    out_pdf = tmp_path / "exam_math_export.pdf"
    ok = generate_digitized_exam_pdf(questions, out_pdf)
    assert ok is True
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 500
    with open(out_pdf, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"
