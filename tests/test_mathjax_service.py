"""Unit tests for MathJax LaTeX Engine Service.
Tests LaTeX typesetting to MathML, SVG, high-DPI PNG and Word docx export.
"""

import io
from pathlib import Path
from backend.services.mathjax_service import (
    render_mathjax_equation,
    convert_latex_to_omml_mathjax,
    render_mathjax_batch
)
from backend.services.docx_exporter import generate_digitized_exam_pdf


def test_mathjax_basic():
    """Verifies that basic LaTeX formula converts to valid MathML and dimensions."""
    res = render_mathjax_equation("u_1 = 3", font_size_pt=11.0, dpi=300)
    assert res is not None
    assert res["mml"] is not None
    assert "<math" in res["mml"]
    assert "<mi>u</mi>" in res["mml"]
    assert res["w_pt"] > 0
    assert res["h_pt"] > 0
    assert res["png_bytes"] is not None
    assert res["png_bytes"][:8] == b"\x89PNG\r\n\x1a\n"


def test_mathjax_vector_equation():
    """Verifies complex vector formula with fraction and extensible arrows."""
    expr = r"\overrightarrow{IJ} = \frac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}\right)"
    res = render_mathjax_equation(expr, font_size_pt=11.0, dpi=300)
    assert res is not None
    assert res["w_pt"] > 50.0
    assert res["h_pt"] > 15.0
    assert res["shift_half_pt"] < 0
    assert res["png_bytes"] is not None


def test_mathjax_omml_conversion():
    """Verifies conversion of LaTeX formula to Word native OMML (<m:oMath>)."""
    omml = convert_latex_to_omml_mathjax(r"G(x) = 0{,}035x^2(15 - x)")
    assert omml is not None
    assert "oMath" in omml.tag


def test_mathjax_batch_rendering():
    """Verifies batch rendering of multiple formulas in a single invocation."""
    formulas = [
        r"u_1 = 3",
        r"u_6 = -96",
        r"\log_{0{,}5}(3x - 2) > 0",
        r"\frac{15}{56}"
    ]
    batch = render_mathjax_batch(formulas, font_size_pt=11.0, dpi=300)
    assert len(batch) >= 4
    for f in formulas:
        c = f.strip("$")
        assert c in batch
        assert batch[c]["mml"] is not None


def test_mathjax_pdf_export(tmp_path: Path):
    """Verifies that PDF export with MathJax vector formula typesetting succeeds."""
    questions = [
        {
            "id": 1,
            "item_format": "SINGLE_CHOICE",
            "stem": r"Cho một cấp số nhân có $u_1 = 3$; $u_6 = -96$. Số hạng thứ năm là",
            "options": [
                {"label": "A", "content": r"$u_5 = -24$"},
                {"label": "B", "content": r"$u_5 = 48$"},
                {"label": "C", "content": r"$u_5 = -48$"},
                {"label": "D", "content": r"$u_5 = 32$"}
            ]
        }
    ]
    out_pdf = tmp_path / "exam_mathjax.pdf"
    ok = generate_digitized_exam_pdf(questions, out_pdf)
    assert ok is True
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 500
