"""
Standalone Test Script for AI Ingestion, OCR & Parsing Pipeline Services.

Tests:
1. latex_converter.py: LaTeX sanitization, delimiter repairing, KaTeX validation, OMML & MTEF conversion.
2. crop_service.py: Diagram generation, auto-crop whitespace trimming, WebP conversion with UUID, saving to storage/assets/.
3. tagging_service.py: Embedding generation, deduplication (threshold >= 0.90), Circular 32 taxonomy auto-tagging.
4. ai_parser.py: Full pipeline parsing of sample DOCX & PDF exams according to Decision 764/QĐ-BGDĐT.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

from backend.services.latex_converter import (
    sanitize_latex,
    repair_math_delimiters,
    validate_katex,
    convert_omml_to_latex,
    decode_mtef
)
from backend.services.crop_service import CropService
from backend.services.tagging_service import (
    generate_embedding,
    cosine_similarity,
    compute_cosine_similarity,
    check_duplication,
    auto_tag_question,
    classify_cognitive_level
)
from backend.services.ai_parser import (
    AIExamParser,
    calculate_item_confidence,
    get_confidence_badge,
    parse_document_file
)


def create_sample_docx(dest_path: Path, crop_svc: CropService) -> Path:
    """Creates a sample Vietnamese exam DOCX file adhering to Decision 764/QĐ-BGDĐT."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()

    # Document Header
    p_hdr1 = doc.add_paragraph()
    p_hdr1.add_run("SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ HỒ CHÍ MINH\n").bold = True
    p_hdr1.add_run("TRƯỜNG THPT CHUYÊN LÊ HỒNG PHONG\n").bold = True
    p_hdr1.add_run("KỲ THI TỐT NGHIỆP THPT NĂM 2025\n").bold = True
    p_hdr1.add_run("Môn thi: TOÁN HỌC - LỚP 12\n")
    p_hdr1.add_run("Thời gian làm bài: 90 phút (không kể thời gian phát đề)\n")
    p_hdr1.add_run("Mã đề thi: 101\n")

    doc.add_paragraph("--------------------------------------------------")

    # Section 1: PHẦN I
    doc.add_heading("PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn. Thí sinh trả lời từ câu 1 đến câu 2. Mỗi câu hỏi thí sinh chỉ chọn một phương án.", level=2)

    # Question 1: Single choice with math & image
    p_q1 = doc.add_paragraph()
    p_q1.add_run("Câu 1. Cho hàm số $y = f(x)$ xác định và liên tục trên $\\mathbb{R}$ có đồ thị như hình vẽ bên. Điểm cực tiểu của đồ thị hàm số đã cho là:")

    # Add mock graph image
    mock_img = crop_svc.generate_mock_diagram(diagram_type="graph", title="Đồ thị hàm số y=f(x)")
    img_byte_arr = io.BytesIO()
    mock_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    doc.add_picture(img_byte_arr, width=Inches(3.2))

    p_q1_opts = doc.add_paragraph()
    p_q1_opts.add_run("A. $(1; -2)$.             B. $(-1; 2)$.\n")
    p_q1_opts.add_run("C. $x = 1$.               D. Không có đáp án nào đúng.")

    # Question 2: Single choice with math formula
    p_q2 = doc.add_paragraph()
    p_q2.add_run("Câu 2. Cho hàm số $y = x^3 - 3x^2 + 2$. Tìm tất cả các giá trị của tham số $m$ để phương trình $x^3 - 3x^2 + 2 = m$ có 3 nghiệm phân biệt.\n")
    p_q2.add_run("A. $-2 < m < 2$.\n")
    p_q2.add_run("B. $m > 2$.\n")
    p_q2.add_run("C. $m < -2$.\n")
    p_q2.add_run("D. Cả A và B đều sai.")

    # Section 2: PHẦN II
    doc.add_heading("PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 1. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.", level=2)

    # Question 1 (Part II): True/False 4 statements
    p_q3 = doc.add_paragraph()
    p_q3.add_run("Câu 1. Cho hàm số $y = f(x) = \\frac{2x - 1}{x + 1}$. Xét tính đúng sai của các khẳng định sau:\n")
    p_q3.add_run("a) Tập xác định của hàm số là $D = \\mathbb{R} \\setminus \\{-1\\}$.\n")
    p_q3.add_run("b) Đạo hàm của hàm số là $y' = \\frac{3}{(x + 1)^2}$ với mọi $x \\ne -1$.\n")
    p_q3.add_run("c) Đồ thị hàm số có đường tiệm cận đứng là đường thẳng $x = 2$.\n")
    p_q3.add_run("d) Hàm số đồng biến trên từng khoảng xác định $(-\\infty; -1)$ và $(-1; +\\infty)$.")

    # Section 3: PHẦN III
    doc.add_heading("PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu 1.", level=2)

    # Question 1 (Part III): Short answer
    p_q4 = doc.add_paragraph()
    p_q4.add_run("Câu 1. Một bể chứa nước có dạng hình hộp chữ nhật không nắp với thể tích bằng $V = 32\\text{ m}^3$. Đáy bể là hình chữ nhật có chiều dài gấp đôi chiều rộng. Tính chi phí thấp nhất để xây dựng bể nước biết chi phí xây dựng mỗi $\\text{m}^2$ thành bể và đáy bể bằng nhau (kết quả làm tròn đến hàng đơn vị).")

    # Answer Key Section
    doc.add_heading("BẢNG ĐÁP ÁN VÀ LỜI GIẢI CHI TIẾT", level=2)

    # Part I Answer Key
    doc.add_paragraph("PHẦN I:\n1. A\n2. A\n")

    # Part II Answer Key
    doc.add_paragraph("PHẦN II:\nCâu 1: a - Đúng, b - Đúng, c - Sai, d - Đúng\n")

    # Part III Answer Key
    doc.add_paragraph("PHẦN III:\nCâu 1: 48\n")

    # Explanations
    p_sol1 = doc.add_paragraph()
    p_sol1.add_run("Câu 1. Lời giải: Quan sát đồ thị ta thấy điểm đáy cực tiểu có tọa độ là $(1; -2)$. Chọn A.\n")

    p_sol2 = doc.add_paragraph()
    p_sol2.add_run("Câu 2. Lời giải: Ta có $y' = 3x^2 - 6x = 0 \\Leftrightarrow x = 0$ hoặc $x = 2$. Giá trị cực đại là $y(0) = 2$, giá trị cực tiểu là $y(2) = -2$. Đường thẳng $y = m$ cắt đồ thị tại 3 điểm phân biệt khi $-2 < m < 2$. Chọn A.\n")

    doc.save(str(dest_path))
    return dest_path


def test_latex_converter():
    print("\n--- 1. Testing latex_converter.py ---")

    # Test 1: Sanitization
    raw_tex = "Cho hàm số y = x³ - 3mx² + 2. Với x ∈ ℝ và f(x) ≥ 0, sin(x) = 1."
    clean_tex = sanitize_latex(raw_tex)
    print(f"Sanitized LaTeX: {clean_tex}")
    assert "x^{3}" in clean_tex, "Superscript not normalized"
    assert "\\in" in clean_tex, "Belongs to symbol not normalized"
    assert "\\mathbb{R}" in clean_tex, "Real number set not normalized"
    assert "\\ge" in clean_tex, "Greater than or equal not normalized"
    print("✓ LaTeX sanitization passed")

    # Test 2: Delimiter repair
    unclosed_math = "Tính tích phân: $I = \\int_{0}^{1} x dx"
    repaired = repair_math_delimiters(unclosed_math)
    print(f"Repaired Delimiters: {repaired}")
    assert repaired.endswith("$"), "Unclosed $ delimiter not repaired"
    print("✓ Delimiter balancing passed")

    # Test 3: KaTeX validation
    valid_formula = r"\frac{x^2 + 1}{2x - 3} + \sqrt{x^2 + 1}"
    is_valid, err = validate_katex(valid_formula)
    assert is_valid, f"Expected valid KaTeX, got error: {err}"

    invalid_formula = r"\frac{a}{b"
    is_invalid, err = validate_katex(invalid_formula)
    assert not is_invalid, "Expected invalid KaTeX for unclosed brace"
    print("✓ KaTeX validation passed")

    # Test 4: MTEF binary decoding
    hdr = b"\x05\x01\x01\x00\x00"
    mtef_raw = hdr + b"\x01\x02\x00\x79\x00\x02\x00\x3d\x00\x03\x06\x00\x00\x01\x02\x00\x31\x00\x00\x01\x02\x00\x78\x00\x00\x00\x00"
    decoded_mtef = decode_mtef(mtef_raw)
    print(f"Decoded MTEF Formula: {decoded_mtef}")

    # Test 5: Variation table array normalization (strip rogue internal and outer '|')
    raw_array = r"$$\begin{array}{|c|ccccccc|} \hline x & -\infty & & -2 & & 1 & & +\infty \\ \hline f'(x) & & + & 0 & - & 0 & + & \\ \hline f(x) & & \nearrow & & \searrow & & \nearrow & \\ \hline \end{array}$$"
    cleaned_array = sanitize_latex(raw_array)
    assert r"\begin{array}{c|ccccccc}" in cleaned_array
    assert r"|c|" not in cleaned_array
    print("✓ Variation table array column normalization passed")
    assert "\\dfrac" in decoded_mtef or "\\frac" in decoded_mtef, "MTEF fraction not decoded"
    print("✓ MTEF binary decoding passed")

    # Test 5: Verify 4 New Assessment Digitization Rules
    # Rule 1: Brackets \left and \right
    # Rule 2: Decimal commas {,}
    # Rule 3: \dfrac instead of \frac
    # Rule 4: \overrightarrow instead of \vec
    raw_math = r"Cho \vec{u} = (15,25; -3,5), \vec{AB} = \vec a, f(x) = \frac{1}{2}x và khoảng [0; 3)"
    sanitized_math = sanitize_latex(f"${raw_math}$")
    print(f"Sanitized Math Rules Output: {sanitized_math}")
    assert r"\overrightarrow{u}" in sanitized_math, "Rule 4: \\vec must be converted to \\overrightarrow"
    assert r"\overrightarrow{AB}" in sanitized_math, "Rule 4: \\vec{AB} must be \\overrightarrow{AB}"
    assert r"15{,}25" in sanitized_math, "Rule 2: Decimal comma must be formatted as {,}"
    assert r"-3{,}5" in sanitized_math, "Rule 2: Decimal comma must be formatted as {,}"
    assert r"\dfrac{1}{2}" in sanitized_math, "Rule 3: Fraction must use \\dfrac instead of \\frac"
    assert r"\left(15{,}25; -3{,}5\right)" in sanitized_math, "Rule 1: Parentheses must use \\left( and \\right)"
    assert r"\left[0; 3\right)" in sanitized_math, "Rule 1: Brackets must use \\left[ and \\right)"

    # Test 6: Verify Table auto-closing and text mode protection
    raw_table = (
        r"Bảng sau: "
        r"$$\begin{array}{|c|c|}"
        r"\hline "
        r"\text{Thời gian \left(phút\right)} & [9{,}5; 12{,}5) \\ "
        r"\hline "
        r"\text{Số học sinh} & 3 \\ "
        r"\hline "
        r"\end{array} "
        r"Tứ phân vị thứ nhất $ Q_1 $ là:"
    )
    clean_table = sanitize_latex(raw_table)
    assert r"\end{array}$$" in clean_table, "Unclosed \\begin{array} must be auto-closed with $$"
    assert r"\text{Thời gian (phút)}" in clean_table, "\\left in \\text{} must be cleaned for KaTeX compatibility"
    assert r"\left[9{,}5; 12{,}5\right)" in clean_table

    # Test 7: Verify TikZ standalone wrapping and renderer
    from backend.services.tikz_renderer import wrap_tikz_in_standalone_document
    tikz_sample = r"\begin{tikzpicture} \draw (0,0) circle (1); \end{tikzpicture}"
    wrapped_doc = wrap_tikz_in_standalone_document(tikz_sample)
    assert r"\documentclass[tikz,border=2mm]{standalone}" in wrapped_doc
    assert r"\begin{document}" in wrapped_doc
    assert r"\end{document}" in wrapped_doc

    # Test 8: Verify set curly braces normalization (\mathbb{R} \setminus \left\\{1\right\\})
    raw_set_stem = r"Cho hàm số $y = f(x)$ xác định trên tập $\mathbb{R} \setminus \left\\{1\right\\}$."
    clean_set_stem = sanitize_latex(raw_set_stem)
    assert r"\left\{1\right\}" in clean_set_stem, "Double-escaped curly braces must be normalized to single \\left\\{1\\right\\}"
    assert r"\\{" not in clean_set_stem, "No raw \\\\{ should remain to break KaTeX"
    assert r"\left\left\{" not in clean_set_stem, "No duplicate \\left\\left\\{ should occur"

    # Test 9: Verify TikZ libraries, Vietnamese transliteration, and auto-clipping
    from backend.services.tikz_renderer import transliterate_vietnamese_for_latex, auto_clip_tikz_plot
    raw_tikz_vn = r"\node at (0, 0) {$--- \text{ đường gấp}$};"
    clean_tikz_vn = transliterate_vietnamese_for_latex(raw_tikz_vn)
    assert "duong gap" in clean_tikz_vn

    raw_tikz_unclipped = (
        r"\begin{tikzpicture}[scale=0.7]"
        r"\draw[->, thick] (-6, 0) -- (4, 0);"
        r"\draw[->, thick] (0, -2) -- (0, 8);"
        r"\draw plot (\x, {1/(\x+2)});"
        r"\end{tikzpicture}"
    )
    clipped = auto_clip_tikz_plot(raw_tikz_unclipped)
    assert r"\clip" in clipped, "Auto-clipping must insert \\clip boundary for coordinate axes"

    # Test 10: Answer values must not use {,} notation
    from backend.services.ai_provider_service import default_ai_provider_service
    test_q_json = '''```json
    {
      "questions": [
        {
          "id": 1,
          "item_format": "SHORT_ANSWER",
          "stem": "Tính kết quả",
          "short_answer_value": "3{,}9",
          "tolerance": 0.01
        },
        {
          "id": 2,
          "item_format": "SINGLE_CHOICE",
          "stem": "Chọn kết quả",
          "options": [
            {"label": "A", "content": "$15{,}25$", "is_correct": true}
          ]
        }
      ]
    }
    ```'''
    parsed_qs, _ = default_ai_provider_service._parse_json_result(test_q_json)
    assert parsed_qs[0]["short_answer_value"] == "3,9", "short_answer_value must not use {,}"
    assert "15,25" in parsed_qs[1]["options"][0]["content"], "options content must contain 15,25"
    assert "{,}" not in parsed_qs[1]["options"][0]["content"], "options content must not use {,}"


import pytest


@pytest.fixture
def sample_docx_path(tmp_path: Path) -> Path:
    crop_svc = CropService(storage_dir=tmp_path / "storage" / "assets")
    docx_file = tmp_path / "sample_exam.docx"
    return create_sample_docx(docx_file, crop_svc)


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    pdf_file = tmp_path / "sample_exam.pdf"
    return create_sample_pdf(pdf_file)


def test_crop_service(tmp_path: Path):
    print("\n--- 2. Testing crop_service.py ---")
    svc = CropService(storage_dir=tmp_path / "storage" / "assets")

    # Test 1: Generate diagram & auto-crop whitespace borders
    raw_diagram = svc.generate_mock_diagram(diagram_type="graph")
    cropped_info = svc.crop_and_save(raw_diagram, job_id="job_test_crop", crop_type="graph")

    print(f"Cropped WebP Asset: {cropped_info['url']}, format: {cropped_info['format']}, size: {cropped_info['width']}x{cropped_info['height']}")
    assert os.path.exists(cropped_info["file_path"]), "WebP asset not written to disk"
    assert cropped_info["filename"].endswith(".webp"), "Asset filename must have .webp extension"
    assert cropped_info["filename"].startswith("img_"), "Asset filename must follow img_{uuid}.webp pattern"
    assert cropped_info["crop_type"] == "graph", "Crop type classification failed"
    print("✓ Auto-crop and WebP storage passed")


def test_tagging_service():
    print("\n--- 3. Testing tagging_service.py ---")

    # Test 1: Auto-tagging with Circular 32 standards
    q_stem = "Cho hàm số $y = f(x)$ có bảng biến thiên như hình bên. Điểm cực đại của đồ thị hàm số là:"
    tags = auto_tag_question(q_stem)
    print(f"Auto-tagging output:")
    print(f"  - Strand: {tags['strand']}")
    print(f"  - Topic: {tags['topic']}")
    print(f"  - Lesson: {tags['lesson']}")
    print(f"  - YCCĐ: {tags['learning_outcome_code']} - {tags['learning_outcome_desc'][:50]}...")
    print(f"  - Archetype: {tags['problem_archetype']}")
    print(f"  - Cognitive Level: {tags['cognitive_level']} ({tags['cognitive_level_vn']})")

    assert tags["learning_outcome_code"] == "TOAN12.GT.01", "Expected TOAN12.GT.01 YCCĐ code"
    assert tags["strand"] == "Số, Đại số và Một số yếu tố giải tích"
    assert tags["cognitive_level"] in ("RECOGNITION", "KNOWLEDGE")

    # Test 2: Application level (parameter m)
    q_app = "Tìm tất cả các giá trị thực của tham số $m$ để hàm số có đúng 3 điểm cực trị."
    tags_app = auto_tag_question(q_app)
    assert tags_app["cognitive_level"] == "APPLICATION", "Expected APPLICATION for parameter m problem"
    print("✓ Circular 32 taxonomy classification passed")

    # Test 3: Deduplication with cosine similarity threshold >= 0.90
    stem_original = "Cho hàm số $y = x^3 - 3x^2 + 4$. Tìm giá trị lớn nhất của hàm số trên đoạn [0; 3]."
    stem_duplicate = "Cho hàm số $y = x^3 - 3x^2 + 4$. Tìm giá trị lớn nhất của hàm số trên đoạn [0; 3]."
    stem_different = "Trong không gian $Oxyz$, viết phương trình mặt phẳng đi qua điểm $M(1; 2; 3)$."

    bank = [
        {"id": "TOAN12-GT-0142", "stem": stem_original}
    ]

    # Test exact duplicate
    res_dup = check_duplication(stem_duplicate, bank, threshold=0.90)
    print(f"Duplicate check (threshold >= 0.90): {res_dup['status']} - {res_dup['message']}")
    assert res_dup["status"] == "DUPLICATE_BLOCKED", f"Expected DUPLICATE_BLOCKED, got {res_dup['status']}"
    assert res_dup["is_duplicate"] is True

    # Test different question
    res_diff = check_duplication(stem_different, bank, threshold=0.90)
    print(f"Unique check: {res_diff['status']} - {res_diff['message']}")
    assert res_diff["status"] == "UNIQUE"
    assert res_diff["is_duplicate"] is False
    print("✓ Vector embeddings & Cosine similarity deduplication passed")


def test_ai_parser_pipeline(sample_docx_path: Path):
    print("\n--- 4. Testing ai_parser.py Full Pipeline ---")
    parser = AIExamParser()
    result = parser.parse_document(sample_docx_path, job_id="job_full_test")

    # Print JSON output summary
    print("\nParsed Result JSON Structure:")
    metadata = result["metadata"]
    print(f"Exam Title: {metadata['title']}")
    print(f"School: {metadata['school']}")
    print(f"Subject: {metadata['subject']}")
    print(f"Grade: {metadata['grade']}")
    print(f"Exam Code: {metadata['exam_code']}")
    print(f"Total Questions: {metadata['total_questions']}")
    print(f"Overall Confidence: {metadata['overall_confidence']}%")
    print(f"Confidence Breakdown: {metadata['confidence_breakdown']}")

    # Assertions on Metadata
    assert metadata["exam_code"] == "101", "Exam code not parsed"
    assert metadata["duration_minutes"] == 90, "Duration not parsed"
    assert metadata["total_questions"] >= 4, f"Expected at least 4 questions, got {metadata['total_questions']}"

    # Verify Question 1 (Part I: Single Choice)
    q1 = result["questions"][0]
    print(f"\nQuestion 1 ({q1['section']} - {q1['item_format']}):")
    print(f"  Stem: {q1['stem'][:80]}...")
    print(f"  Options count: {len(q1['options'])}")
    print(f"  Options: {[opt['label'] for opt in q1['options']]}")
    print(f"  Correct option: {[opt['label'] for opt in q1['options'] if opt['is_correct']]}")
    print(f"  Explanation: {q1['explanation'][:60]}...")
    print(f"  YCCĐ: {q1.get('learning_outcome_code')}")
    print(f"  Confidence: {q1['confidence_score']}% ({q1['confidence_badge']})")

    assert q1["item_format"] == "SINGLE_CHOICE"
    assert len(q1["options"]) == 4, "Expected 4 options A, B, C, D"
    assert any(opt["is_correct"] for opt in q1["options"]), "Correct answer not mapped"
    assert q1["confidence_badge"] == "GREEN", f"Expected GREEN confidence, got {q1['confidence_badge']}"

    # Verify Option Anchor Rule on Option D ("Không có đáp án nào đúng" -> is_fixed=True)
    opt_d = next(opt for opt in q1["options"] if opt["label"] == "D")
    assert opt_d["is_fixed"] is True, "Option Anchor Rule not enforced for 'Không có đáp án nào đúng'"
    print("  ✓ Option Anchor Rule verified (is_fixed=True for anchor option)")

    # Verify Question 3 (Part II: True / False 4 statements)
    q3 = next(q for q in result["questions"] if q["item_format"] == "TRUE_FALSE_GROUP")
    print(f"\nQuestion 3 ({q3['section']} - {q3['item_format']}):")
    print(f"  Stem: {q3['stem'][:80]}...")
    print(f"  Sub-statements count: {len(q3['sub_statements'])}")
    for stmt in q3["sub_statements"]:
        print(f"    - {stmt['label']}) {stmt['content'][:40]}... -> is_true: {stmt['is_true']}")
    print(f"  Confidence: {q3['confidence_score']}% ({q3['confidence_badge']})")

    assert len(q3["sub_statements"]) == 4, "Expected 4 sub-statements a, b, c, d"
    # From answer key: a-Đ, b-Đ, c-S, d-Đ
    assert q3["sub_statements"][0]["is_true"] is True
    assert q3["sub_statements"][1]["is_true"] is True
    assert q3["sub_statements"][2]["is_true"] is False
    assert q3["sub_statements"][3]["is_true"] is True
    print("  ✓ Answer key accurately mapped to sub-statements a, b, c, d")

    # Verify Question 4 (Part III: Short Answer)
    q4 = next(q for q in result["questions"] if q["item_format"] == "SHORT_ANSWER")
    print(f"\nQuestion 4 ({q4['section']} - {q4['item_format']}):")
    print(f"  Stem: {q4['stem'][:80]}...")
    print(f"  Expected answer: {q4.get('expected_answer')}")
    print(f"  Confidence: {q4['confidence_score']}% ({q4['confidence_badge']})")
    assert q4["expected_answer"] == "48", f"Expected answer 48, got {q4.get('expected_answer')}"
    print("  ✓ Short answer expected value accurately mapped from answer key")

    # Output Sample JSON payload
    output_json_path = sample_docx_path.parent / "parsed_exam_output.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved clean JSON output to {output_json_path}")


def create_sample_pdf(dest_path: Path) -> Path:
    """Creates a sample PDF exam file."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 320 >>
stream
BT
/F1 12 Tf
50 720 Td
(KANG THI TOT NGHIEP THPT 2025) Tj
0 -20 Td
(Mon thi: TOAN HOC - LOP 12) Tj
0 -20 Td
(Ma de thi: 102) Tj
0 -30 Td
(PHAN I. Cau trac nghiem nhieu phuong an lua chon) Tj
0 -25 Td
(Cau 1. Cho ham so y = f(x) co do thi nhu hinh ben. Diem cuc dai la:) Tj
0 -20 Td
(A. (1; 2)     B. (-1; -2)     C. x = 0     D. y = 1) Tj
0 -30 Td
(BANG DAP AN) Tj
0 -20 Td
(1. A) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000060 00000 n 
0000000117 00000 n 
0000000227 00000 n 
0000000598 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
673
%%EOF"""
    with open(dest_path, "wb") as f:
        f.write(pdf_content)
    return dest_path


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    pdf_file = tmp_path / "sample_exam.pdf"
    return create_sample_pdf(pdf_file)


def test_pdf_parsing(sample_pdf_path: Path):
    print("\n--- 5. Testing PDF Exam Parsing ---")
    parser = AIExamParser()
    result = parser.parse_document(sample_pdf_path, job_id="job_pdf_test")
    print(f"PDF Exam Title: {result['metadata']['title']}")
    print(f"PDF Exam Code: {result['metadata']['exam_code']}")
    print(f"PDF Total Questions: {result['metadata']['total_questions']}")
    print(f"PDF Overall Confidence: {result['metadata']['overall_confidence']}%")

    assert result["metadata"]["exam_code"] == "102"
    assert result["metadata"]["total_questions"] >= 1
    q = result["questions"][0]
    assert q["options"][0]["is_correct"] is True
    print(f"  ✓ PDF parsed successfully with question {q['question_number']} (is_correct={q['options'][0]['is_correct']})")


def main():
    print("======================================================================")
    print(" QUESY AI INGESTION, OCR & PARSING PIPELINE TEST SUITE")
    print("======================================================================")

    test_dir = PROJECT_ROOT / "tests" / "tmp_test_pipeline"
    test_dir.mkdir(parents=True, exist_ok=True)

    # 1. Test LaTeX converter
    test_latex_converter()

    # 2. Test Crop service
    test_crop_service(test_dir)

    # 3. Test Tagging service & Deduplication
    test_tagging_service()

    # 4. Create Sample DOCX and test AI Parser
    crop_svc = CropService(storage_dir=PROJECT_ROOT / "storage" / "assets")
    sample_docx = test_dir / "De_Thi_Mau_TT32_2025.docx"
    create_sample_docx(sample_docx, crop_svc)
    test_ai_parser_pipeline(sample_docx)

    # 5. Create Sample PDF and test AI Parser
    sample_pdf = test_dir / "De_Thi_Mau_TT32_2025.pdf"
    create_sample_pdf(sample_pdf)
    test_pdf_parsing(sample_pdf)

    print("\n======================================================================")
    print(" ALL PIPELINE SERVICE TESTS PASSED SUCCESSFULLY! ")
    print("======================================================================")


if __name__ == "__main__":
    main()
