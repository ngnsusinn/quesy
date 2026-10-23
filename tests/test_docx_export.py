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
