"""Automated Test Suite for Experimental 2-Pass Decoupled AI Digitization Pipeline.

Verifies:
1. Uniform Document-to-Image conversion (PyMuPDF).
2. Computer Vision image enhancement (OpenCV CLAHE & illumination normalization).
3. Layout analysis & diagram/table region detection & WebP auto-cropping.
4. AI 2-Pass Stitching & Fallback mechanism (zero-loss guarantee).
5. New API Endpoints: /api/v1/digitize/upload-test and /api/v1/digitize/assets/:filename.
"""

import io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.image_enhancer import convert_document_to_images, enhance_page_image
from backend.services.layout_segmenter import detect_and_crop_regions
from backend.services.ai_provider_service import default_ai_provider_service


def test_enhance_page_image(tmp_path: Path):
    """Verifies image enhancement improves contrast and normalizes background brightness."""
    # Create synthetic test page image with dim gray background and text
    img = np.full((300, 400, 3), 215, dtype=np.uint8)
    # Add dark text-like patterns
    img[100:104, 50:250] = 30
    img[140:144, 50:320] = 40

    src_img_p = tmp_path / "raw_page.jpg"
    Image.fromarray(img).save(src_img_p, "JPEG")

    enh_img_p = tmp_path / "enhanced_page.jpg"
    result_path = enhance_page_image(src_img_p, enh_img_p)

    assert result_path.exists()
    assert result_path.stat().st_size > 500

    # Load enhanced image and verify paper background became lighter (closer to pure white 255)
    with Image.open(result_path) as im:
        arr = np.array(im.convert("L"))
        # Top-left background should be clean white
        bg_sample = arr[10:30, 10:30]
        assert np.mean(bg_sample) > 235.0


def test_convert_pdf_to_images(tmp_path: Path):
    """Verifies PyMuPDF page rasterization to high-resolution JPEG."""
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 100), "KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025 - TOÁN HỌC", fontsize=16)
    page.insert_text((50, 140), "Câu 1. Cho hàm số y = f(x)...", fontsize=12)

    pdf_path = tmp_path / "test_exam.pdf"
    doc.save(str(pdf_path))
    doc.close()

    out_dir = tmp_path / "extracted_pages"
    pages = convert_document_to_images(pdf_path, out_dir, target_dpi=150)

    assert len(pages) == 1
    assert pages[0].exists()
    with Image.open(pages[0]) as im:
        assert im.width > 1000
        assert im.height > 1500


def test_layout_segmenter_diagram_and_table_detection(tmp_path: Path):
    """Verifies detection and auto-cropping of diagram bounding boxes and tables."""
    # Create white canvas
    w, h = 1000, 1400
    canvas = np.full((h, w, 3), 255, dtype=np.uint8)

    # Draw a simulated coordinate plot diagram (box + curve)
    # Area = 260 x 220 = 57,200 px^2 (> 14,000 threshold)
    import cv2
    cv2.rectangle(canvas, (200, 300), (460, 520), (30, 30, 30), 2)
    cv2.line(canvas, (210, 410), (450, 410), (50, 50, 50), 2) # X axis
    cv2.line(canvas, (330, 310), (330, 510), (50, 50, 50), 2) # Y axis

    # Draw a simulated table with horizontal and vertical grid lines
    # Area = 400 x 120 = 48,000 px^2 (> 12,000 threshold)
    for y_line in range(700, 850, 35):
        cv2.line(canvas, (150, y_line), (550, y_line), (40, 40, 40), 2)
    for x_line in range(150, 600, 100):
        cv2.line(canvas, (x_line, 700), (x_line, 805), (40, 40, 40), 2)

    page_img_p = tmp_path / "page_with_diagram_and_table.jpg"
    Image.fromarray(canvas).save(page_img_p, "JPEG")

    out_assets = tmp_path / "segmented_assets"
    annotated_p, figures = detect_and_crop_regions(
        page_img_p,
        output_dir=out_assets,
        job_id="test_job_123",
        page_index=1
    )

    assert annotated_p.exists()
    assert len(figures) >= 1  # Should successfully detect the diagram and/or table

    # Verify cropped files exist and are valid images
    for fig in figures:
        crop_p = Path(fig["crop_path"])
        assert crop_p.exists()
        assert crop_p.stat().st_size > 100
        assert fig["tag"].startswith("{{") and fig["tag"].endswith("}}")


def test_stitching_figures_valid_tikz():
    """Verifies {{FIGURE_1}} placeholder is substituted with LaTeX/TikZ code."""
    questions = [
        {
            "id": 1,
            "stem": "Cho hàm số có đồ thị như hình vẽ {{FIGURE_1}}. Tìm tiệm cận ngang.",
            "options": [{"label": "A", "content": "y = 1"}, {"label": "B", "content": "y = 2"}]
        }
    ]
    detected_figures = [
        {"id": "FIGURE_1", "crop_url": "/api/v1/digitize/assets/crop_fig.webp", "type": "diagram"}
    ]
    figure_latex_map = {
        "FIGURE_1": r"\begin{tikzpicture}\draw (0,0) -- (2,2);\end{tikzpicture}"
    }

    stitched = default_ai_provider_service.stitch_figures(questions, detected_figures, figure_latex_map)
    assert "\\begin{tikzpicture}" in stitched[0]["stem"]
    assert "{{FIGURE_1}}" not in stitched[0]["stem"]


def test_stitching_figures_fallback_on_invalid_tikz():
    """Verifies {{FIGURE_1}} falls back to clean image crop tag if TikZ is invalid."""
    questions = [
        {
            "id": 1,
            "stem": "Cho đồ thị hàm số như hình {{FIGURE_1}}. Mệnh đề nào đúng?",
            "options": []
        }
    ]
    detected_figures = [
        {"id": "FIGURE_1", "crop_url": "/api/v1/digitize/assets/crop_fig_01.webp", "type": "diagram"}
    ]
    # Spurious / invalid TikZ that will fail rendering
    figure_latex_map = {
        "FIGURE_1": r"\begin{tikzpicture} this is completely broken invalid syntax }}} \end{tikzpicture}"
    }

    stitched = default_ai_provider_service.stitch_figures(questions, detected_figures, figure_latex_map)
    # Must fallback to image tag, preventing lost diagrams or raw broken code
    assert "crop-figure-fallback" in stitched[0]["stem"]
    assert "/api/v1/digitize/assets/crop_fig_01.webp" in stitched[0]["stem"]
    assert "{{FIGURE_1}}" not in stitched[0]["stem"]


def test_api_upload_test_endpoint_and_assets():
    """Verifies POST /api/v1/digitize/upload-test and GET /api/v1/digitize/assets/:filename."""
    client = TestClient(app)

    # 1. Test upload-test endpoint
    dummy_img = Image.new("RGB", (200, 200), (255, 255, 255))
    buf = io.BytesIO()
    dummy_img.save(buf, format="JPEG")
    buf.seek(0)

    res = client.post(
        "/api/v1/digitize/upload-test",
        files={"file": ("test_de_2pass.jpg", buf, "image/jpeg")},
        data={"sync": "true"}
    )
    assert res.status_code == 202
    data = res.json()
    assert data["pipeline_mode"] == "test_2pass"
    job_id = data["job_id"]

    # 2. Check job status returns pipeline_mode, detected_figures, and live progress
    status_res = client.get(f"/api/v1/digitize/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["pipeline_mode"] == "test_2pass"
    assert isinstance(status_data["detected_figures"], list)
    assert "progress_percent" in status_data
    assert "progress_stage" in status_data

    # 3. Test asset serving endpoint
    # Create dummy asset in storage/assets/
    project_root = Path(__file__).resolve().parent.parent
    assets_dir = project_root / "storage" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    test_asset = assets_dir / "crop_test_dummy_asset.webp"
    dummy_img.save(test_asset, format="WEBP")

    asset_res = client.get(f"/api/v1/digitize/assets/{test_asset.name}")
    assert asset_res.status_code == 200
    assert asset_res.headers["content-type"] in ["image/webp", "image/jpeg"]

    # Clean up test asset
    if test_asset.exists():
        test_asset.unlink()


def test_normalize_option_text():
    """Verifies multiple choice option text normalization:
    1. Removes redundant leading label prefixes ('A. ', 'A) ').
    2. Converts accidental all-caps text to sentence case while preserving math.
    """
    from backend.services.ai_provider_service import normalize_option_text

    assert normalize_option_text("A. 1") == "1"
    assert normalize_option_text("B) $y = x^2 - 1$") == "$y = x^2 - 1$"
    assert normalize_option_text("C. HÀM SỐ ĐỒNG BIẾN TRÊN KHOẢNG (0; 1)") == "Hàm số đồng biến trên khoảng (0; 1)"
    assert normalize_option_text("D. TẤT CẢ CÁC ĐÁP ÁN ĐỀU ĐÚNG") == "Tất cả các đáp án đều đúng"
    assert normalize_option_text("x = 2") == "x = 2"


def test_tkz_tab_variation_table_compilation():
    """Verifies TikZ tkz-tab variation table document wrapping, label math-mode normalization, and rendering support."""
    from backend.services.tikz_renderer import wrap_tikz_in_standalone_document, render_tikz_to_svg, normalize_tikz_exam_standard

    # 1. Test auto-fixing raw un-delimited labels: x/.6, f'(x)/.6 -> $x$/.6, $f'(x)$/.6
    raw_snippet = r"""\begin{tikzpicture}
\tkzTabInit[nocadre]{x/.6, f'(x)/.6, f(x)/2}
{$-\infty$,$1$,$3$,$+\infty$}
\tkzTabLine{,-,0,+,0,-,}
\tkzTabVar{+/ $+\infty$, -/$-2$, +/$4$, -/$-\infty$}
\end{tikzpicture}"""
    normalized = normalize_tikz_exam_standard(raw_snippet)
    assert r"{$x$/.6,$f'(x)$/.6,$f(x)$/2}" in normalized

    # 2. Test document wrapper includes tkz-tab package
    wrapped_doc = wrap_tikz_in_standalone_document(normalized)
    assert r"\usepackage{tkz-tab}" in wrapped_doc
    assert r"\tkzTabInit" in wrapped_doc

    # 3. Render to SVG (reads from cache or Kroki)
    res = render_tikz_to_svg(normalized)
    assert res.get("success") is True
    assert "<svg" in res.get("svg", "")


def test_convert_variation_array_to_tkz_tab():
    """Verifies that legacy or AI-generated \\begin{array} variation tables are automatically converted to native TikZ tkz-tab."""
    from backend.services.latex_converter import convert_variation_array_to_tkz_tab, sanitize_latex

    array_stem = r"""Cho hàm số ${y = f\left(x\right)}$ liên tục trên ${\mathbb{R}}$ và có bảng biến thiên sau:
$$\begin{array}{|c|ccccccc|} \hline x & -\infty & & -2 & & 1 & & +\infty \\ \hline f'\left(x\right) & & + & 0 & - & 0 & + & \\ \hline & & & 4 & & & & +\infty \\ f\left(x\right) & & \nearrow & & \searrow & & \nearrow & \\ & -\infty & & & & -1 & & \\ \hline \end{array}$$
Điểm cực đại của đồ thị hàm số là:"""

    converted = convert_variation_array_to_tkz_tab(array_stem)
    assert r"\begin{tikzpicture}" in converted
    assert r"\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]" in converted
    assert r"{$x$/.6, $f'(x)$/.6, $f(x)$/2}" in converted
    assert r"{$-\infty$,$-2$,$1$,$+\infty$}" in converted
    assert r"\tkzTabLine{,+,0,-,0,+,}" in converted
    assert r"\tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}" in converted
    assert r"\end{tikzpicture}" in converted

    # Test through end-to-end sanitize_latex pipeline
    sanitized = sanitize_latex(array_stem)
    assert r"\begin{tikzpicture}" in sanitized
    assert r"\tkzTabInit" in sanitized
    assert r"\begin{array}" not in sanitized




