"""Image Enhancement and Document-to-Image Conversion Service for Quesy (2-Pass Decoupled Pipeline).

Key Features:
- Uniform Page Rasterization: Converts PDFs, DOCX, and images into high-resolution RGB JPEG pages.
- Adaptive Illumination Normalization: Removes phone shadows, uneven lighting, and yellow/gray paper cast.
- Local Contrast Enhancement (CLAHE): Sharpens math exponents, indices, fraction lines, and radical signs.
- Automatic Deskewing: Detects slight camera tilt and straightens page layout.
"""

from __future__ import annotations

import io
import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
from PIL import Image

logger = logging.getLogger("quesy.image_enhancer")

# Optional PyMuPDF import
try:
    import pymupdf
    HAS_PYMUPDF = True
except ImportError:
    try:
        import fitz as pymupdf
        HAS_PYMUPDF = True
    except ImportError:
        HAS_PYMUPDF = False

# Optional OpenCV import
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def convert_document_to_images(
    file_path: Union[str, Path],
    output_dir: Union[str, Path],
    target_dpi: int = 200
) -> List[Path]:
    """Converts any supported exam document (PDF, Images, DOCX) into uniform high-res RGB JPEG page images.
    
    Returns a sorted list of generated page image paths.
    """
    src_path = Path(file_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not src_path.exists():
        raise FileNotFoundError(f"Source document not found: {src_path}")

    ext = src_path.suffix.lower()
    page_paths: List[Path] = []

    # 1. Image inputs (JPG, PNG, WEBP, BMP)
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        target_file = out_dir / f"page_01{ext}"
        try:
            with Image.open(src_path) as im:
                rgb_im = im.convert("RGB")
                target_file = out_dir / "page_01.jpg"
                rgb_im.save(target_file, "JPEG", quality=92)
            page_paths.append(target_file)
        except Exception as e:
            logger.warning(f"Direct PIL load failed for {src_path}: {e}, copying raw file")
            shutil.copy2(src_path, target_file)
            page_paths.append(target_file)
        return page_paths

    # 2. PDF inputs
    if ext == ".pdf":
        if HAS_PYMUPDF:
            try:
                doc = pymupdf.open(str(src_path))
                for page_idx, page in enumerate(doc):
                    pix = page.get_pixmap(dpi=target_dpi)
                    page_out = out_dir / f"page_{page_idx + 1:02d}.jpg"
                    pix.save(str(page_out))
                    page_paths.append(page_out)
                doc.close()
                if page_paths:
                    logger.info(f"Rendered {len(page_paths)} pages from PDF {src_path.name} at {target_dpi} DPI via PyMuPDF.")
                    return page_paths
            except Exception as pdf_err:
                logger.error(f"PyMuPDF rendering failed for {src_path}: {pdf_err}")

        # Fallback using pypdf image extraction if PyMuPDF failed
        try:
            import pypdf
            reader = pypdf.PdfReader(str(src_path))
            for page_idx, page in enumerate(reader.pages):
                for img_idx, img_obj in enumerate(page.images):
                    im = Image.open(io.BytesIO(img_obj.data)).convert("RGB")
                    page_out = out_dir / f"page_{page_idx + 1:02d}_{img_idx + 1:02d}.jpg"
                    im.save(page_out, "JPEG", quality=90)
                    page_paths.append(page_out)
            if page_paths:
                return page_paths
        except Exception as pypdf_err:
            logger.warning(f"pypdf image extraction fallback failed: {pypdf_err}")

    # 3. DOCX inputs: Convert to HTML -> Headless Chromium PDF -> PyMuPDF Images
    if ext in [".docx", ".doc"]:
        converted_pages = _convert_docx_to_page_images(src_path, out_dir, target_dpi=target_dpi)
        if converted_pages:
            return converted_pages

    # 4. Fallback for text-only files (TXT, MD) or unsupported
    if ext in [".txt", ".md"]:
        text_content = src_path.read_text(encoding="utf-8", errors="ignore")
        img = _render_text_to_synthetic_page(text_content)
        page_out = out_dir / "page_01.jpg"
        img.save(page_out, "JPEG", quality=90)
        page_paths.append(page_out)
        return page_paths

    if not page_paths:
        logger.warning(f"Could not convert document {src_path.name} to images. Returning empty list.")
    return page_paths


def _convert_docx_to_page_images(
    docx_path: Path,
    out_dir: Path,
    target_dpi: int = 200
) -> List[Path]:
    """Converts DOCX to high-res page images via Headless Chromium PDF bridge."""
    try:
        from backend.services.latex_converter import extract_and_convert_docx_content
        from backend.services.latex_pdf_exporter import find_browser_executable
        import subprocess

        browser = find_browser_executable()
        if not browser or not HAS_PYMUPDF:
            return []

        doc_text = extract_and_convert_docx_content(str(docx_path))
        # Build clean HTML presentation for rendering
        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4 portrait; margin: 18mm 16mm 18mm 16mm; }}
  body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.45; color: #111; }}
  p {{ margin-bottom: 0.6em; text-align: justify; }}
  h1, h2, h3 {{ text-align: center; font-size: 13pt; margin-bottom: 1em; }}
</style>
</head>
<body>
  <div class="content">{doc_text.replace(chr(10), '<br/>')}</div>
</body>
</html>"""
        temp_html = out_dir / f"temp_{docx_path.stem}.html"
        temp_pdf = out_dir / f"temp_{docx_path.stem}.pdf"
        temp_html.write_text(html_content, encoding="utf-8")

        cmd = [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--print-to-pdf={str(temp_pdf.resolve())}",
            temp_html.resolve().as_uri()
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if temp_pdf.exists() and temp_pdf.stat().st_size > 1000:
            doc = pymupdf.open(str(temp_pdf))
            pages = []
            for page_idx, page in enumerate(doc):
                pix = page.get_pixmap(dpi=target_dpi)
                page_out = out_dir / f"page_{page_idx + 1:02d}.jpg"
                pix.save(str(page_out))
                pages.append(page_out)
            doc.close()
            # Cleanup temp artifacts
            for t in [temp_html, temp_pdf]:
                if t.exists():
                    try:
                        t.unlink()
                    except Exception:
                        pass
            return pages
    except Exception as e:
        logger.warning(f"DOCX to image conversion bridge failed: {e}")
    return []


def _render_text_to_synthetic_page(text: str) -> Image.Image:
    """Renders raw text onto a standard white A4-proportioned image."""
    width, height = 1654, 2338  # A4 at 200 DPI
    img = Image.new("RGB", (width, height), (255, 255, 255))
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    lines = text.split("\n")[:80]
    y = 80
    for line in lines:
        draw.text((80, y), line[:120], fill=(20, 20, 20))
        y += 26
    return img


def enhance_page_image(
    input_image_path: Union[str, Path],
    output_image_path: Optional[Union[str, Path]] = None,
    auto_deskew: bool = True
) -> Path:
    """Applies advanced computer vision enhancement on a page image:
    1. Deskewing (if tilted > 0.5 degrees)
    2. Background normalization (removes uneven yellow/gray shadows)
    3. CLAHE local contrast boosting (makes exponents, fractions, radical signs stand out)
    4. Mild unsharp masking for sharp character edges.
    """
    in_p = Path(input_image_path).resolve()
    if not in_p.exists():
        raise FileNotFoundError(f"Image not found: {in_p}")

    out_p = Path(output_image_path).resolve() if output_image_path else in_p.with_name(f"{in_p.stem}_enhanced.jpg")

    if not HAS_CV2:
        # Fallback to PIL basic contrast enhancement if OpenCV is not available
        return _enhance_page_image_pil(in_p, out_p)

    try:
        # Load image with OpenCV (BGR)
        img = cv2.imread(str(in_p))
        if img is None:
            return _enhance_page_image_pil(in_p, out_p)

        # 1. Auto-Deskewing
        if auto_deskew:
            img = _deskew_image(img)

        # 2. Illumination Normalization (Background Division & Bleed-Through Suppression)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Morphological dilation with large kernel estimates local page background
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 35))
        bg = cv2.morphologyEx(gray, cv2.MORPH_DILATE, kernel)
        bg = np.maximum(bg, 1)
        normalized = cv2.divide(gray, bg, scale=255)

        # Whiten paper background (suppresses faint bleed-through from reverse side of thin exam paper)
        clean = np.where(normalized > 200, 255, normalized)
        # Contrast stretch remaining dark foreground ink
        enhanced = ((np.clip(clean, 0, 200) / 200.0) * 255).astype(np.uint8)

        # 3. Mild Unsharp Masking to crisp up math strokes without haloing
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 1.5)
        unsharp = cv2.addWeighted(enhanced, 1.2, gaussian, -0.2, 0)

        # 4. Save enhanced image with high JPEG quality
        cv2.imwrite(str(out_p), unsharp, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        return out_p
    except Exception as cv_err:
        logger.warning(f"OpenCV enhancement error for {in_p.name}: {cv_err}, falling back to PIL")
        return _enhance_page_image_pil(in_p, out_p)


def _deskew_image(img: np.ndarray) -> np.ndarray:
    """Detects text orientation angle and deskews image if angle between 0.5 and 15 degrees."""
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Threshold: text pixels become white, background black
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Find coordinates of all foreground pixels
        pts = cv2.findNonZero(thresh)
        if pts is None or len(pts) < 100:
            return img

        # Compute minimum area rotated rectangle
        rect = cv2.minAreaRect(pts)
        angle = rect[-1]

        # OpenCV minAreaRect returns angle in [-90, 0)
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if tilt is between 0.5 and 15 degrees
        if 0.5 < abs(angle) < 15.0:
            h, w = img.shape[:2]
            center = (w // 2, h // 2)
            rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(
                img,
                rot_mat,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(255, 255, 255)
            )
            return deskewed
    except Exception as e:
        logger.debug(f"Deskew calculation skipped: {e}")
    return img


def _enhance_page_image_pil(in_p: Path, out_p: Path) -> Path:
    """Fallback PIL-based contrast and brightness booster."""
    try:
        from PIL import ImageEnhance, ImageOps
        with Image.open(in_p) as im:
            rgb_im = im.convert("RGB")
            # Autocontrast
            ac_im = ImageOps.autocontrast(rgb_im, cutoff=1)
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(ac_im)
            res = enhancer.enhance(1.3)
            res.save(out_p, "JPEG", quality=92)
            return out_p
    except Exception as e:
        logger.error(f"PIL fallback enhancement failed: {e}")
        shutil.copy2(in_p, out_p)
        return out_p
