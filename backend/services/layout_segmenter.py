"""Layout Analysis & Diagram/Table Segmentation Service for Quesy.

Key Features:
- Detects non-text regions (graphs, geometry drawings, coordinate plots, tables) on exam pages.
- Merges proximate contours to extract unified, cohesive figures with labels.
- Auto-crops each figure with safe padding margins and saves as optimized WebP.
- Renders visible visual landmark markers (e.g. `[FIGURE_1]`, `[TABLE_1]`) on the page image
  sent to AI Pass 1, eliminating hallucination and misalignment.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("quesy.layout_segmenter")

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def detect_and_crop_regions(
    image_path: Union[str, Path],
    output_dir: Union[str, Path],
    job_id: str,
    page_index: int = 1,
    start_figure_idx: int = 1
) -> Tuple[Path, List[Dict[str, Any]]]:
    """Detects diagrams, function plots, geometry figures and tables from a page image.
    
    Returns:
    - annotated_page_path: Path to the page image with visual landmark labels.
    - detected_figures: List of metadata dicts for each cropped figure.
    """
    img_p = Path(image_path).resolve()
    out_d = Path(output_dir).resolve()
    out_d.mkdir(parents=True, exist_ok=True)

    if not img_p.exists():
        raise FileNotFoundError(f"Page image not found: {img_p}")

    detected_figures: List[Dict[str, Any]] = []
    annotated_page_p = out_d / f"annotated_p{page_index:02d}_{img_p.name}"

    if not HAS_CV2:
        # Fallback if OpenCV is absent: copy original image without segmentation
        import shutil
        shutil.copy2(img_p, annotated_page_p)
        return annotated_page_p, detected_figures

    try:
        # Load image via OpenCV
        img = cv2.imread(str(img_p))
        if img is None:
            import shutil
            shutil.copy2(img_p, annotated_page_p)
            return annotated_page_p, detected_figures

        h_page, w_page = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Detect Tables (including variation tables / bảng biến thiên and data matrices)
        table_boxes = _detect_table_grids(gray, w_page, h_page)

        # 2. Detect Mathematical Diagrams (coordinate plots, geometry figures, function curves)
        diagram_boxes = _detect_diagram_contours(gray, table_boxes, w_page, h_page)

        # 3. Combine and sort all regions top-to-bottom, left-to-right (Reading Order)
        raw_regions: List[Dict[str, Any]] = []
        for b in table_boxes:
            raw_regions.append({"bbox": b, "type": "table"})
        for b in diagram_boxes:
            raw_regions.append({"bbox": b, "type": "diagram"})

        # Sort primarily by y (top to bottom), then by x
        raw_regions.sort(key=lambda r: (r["bbox"][1] // 50, r["bbox"][0]))

        # 4. Crop each region and render visual marker boxes on annotated page
        annotated_img = img.copy()
        current_fig_num = start_figure_idx

        for reg in raw_regions:
            x, y, w, h = reg["bbox"]
            reg_type = reg["type"]

            # Generous safe padding (18px for tables to preserve x, f'(x), +inf labels; 16px for diagrams)
            pad = 18 if reg_type == "table" else 16
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(w_page, x + w + pad)
            y2 = min(h_page, y + h + pad)

            crop_np = img[y1:y2, x1:x2]
            if crop_np.size == 0:
                continue

            # Tag identifier (e.g. FIGURE_1 or TABLE_1)
            prefix = "TABLE" if reg_type == "table" else "FIGURE"
            fig_tag_id = f"{prefix}_{current_fig_num}"
            fig_placeholder = f"{{{{{fig_tag_id}}}}}"

            crop_filename = f"crop_{job_id}_p{page_index:02d}_{fig_tag_id.lower()}.webp"
            crop_path = out_d / crop_filename

            # Save cropped region via PIL to WebP
            crop_rgb = cv2.cvtColor(crop_np, cv2.COLOR_BGR2RGB)
            crop_pil = Image.fromarray(crop_rgb)
            crop_pil.save(crop_path, "WEBP", quality=90)

            detected_figures.append({
                "id": fig_tag_id,
                "tag": fig_placeholder,
                "type": reg_type,
                "page_index": page_index,
                "figure_number": current_fig_num,
                "crop_path": str(crop_path),
                "crop_filename": crop_filename,
                "crop_url": f"/api/v1/digitize/assets/{crop_filename}",
                "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                "status": "EXTRACTED"
            })

            # Render visual indicator badge on annotated page
            # Purple border for diagrams, Emerald border for tables
            border_color = (180, 50, 140) if reg_type == "diagram" else (40, 160, 80)
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), border_color, 2)

            # Badge background and label
            label_text = f" [{fig_tag_id}] "
            font_scale = 0.7
            font_thick = 2
            (lbl_w, lbl_h), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thick)
            badge_y1 = max(0, y1 - lbl_h - 8)
            badge_y2 = y1
            cv2.rectangle(annotated_img, (x1, badge_y1), (x1 + lbl_w + 10, badge_y2), border_color, -1)
            cv2.putText(
                annotated_img,
                label_text,
                (x1 + 4, badge_y2 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                font_thick
            )

            current_fig_num += 1

        # Save annotated image
        cv2.imwrite(str(annotated_page_p), annotated_img, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        logger.info(f"Page {page_index}: Detected and cropped {len(detected_figures)} regions ({len(diagram_boxes)} diagrams, {len(table_boxes)} tables).")
        return annotated_page_p, detected_figures
    except Exception as e:
        logger.warning(f"Region segmentation exception on {img_p.name}: {e}")
        import shutil
        shutil.copy2(img_p, annotated_page_p)
        return annotated_page_p, detected_figures


def _detect_table_grids(
    gray: np.ndarray,
    w_page: int,
    h_page: int
) -> List[Tuple[int, int, int, int]]:
    """Detects genuine table structures (including variation tables / bảng biến thiên and data matrices).
    Combines horizontal grid lines and vertical dividers. Rejects isolated fraction lines, underlines, and footers.
    """
    boxes: List[Tuple[int, int, int, int]] = []
    try:
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)

        # Margin suppression
        thresh[:15, :] = 0
        thresh[-15:, :] = 0
        thresh[:, :15] = 0
        thresh[:, -15:] = 0

        # Detect horizontal grid lines (min length 45px)
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (45, 1))
        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

        # Detect vertical grid lines (min length 30px)
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

        # Combine table grid lines
        table_lines = cv2.add(h_lines, v_lines)
        # Bridge cells and rows together (kernel: 45w x 20h)
        t_bridge = cv2.dilate(table_lines, cv2.getStructuringElement(cv2.MORPH_RECT, (45, 20)), iterations=2)

        contours, _ = cv2.findContours(t_bridge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            aspect = w / max(1, h)

            # 1. Skip bottom footer banner (Trang 2/5 - Mã đề...)
            if (y + h) > (h_page * 0.94) and w < (w_page * 0.45) and h < 120:
                continue

            # 2. Skip vertical edge artifact
            if (x <= 15 or (x + w) >= w_page - 15) and aspect < 0.2:
                continue

            # 3. Minimum size constraints: width >= 180px, height >= 50px, area >= 20,000 px^2
            if w < 180 or h < 50 or area < 20000:
                continue

            # 4. Maximum size: cannot occupy entire page
            if w > (w_page * 0.95) and h > (h_page * 0.85):
                continue

            # 5. Tables have wide aspect ratio (aspect >= 1.8) or multiple grid rows
            if aspect >= 1.8:
                # Refine box to exact grid lines
                cell_crop = table_lines[y:y+h, x:x+w]
                pts = cv2.findNonZero(cell_crop)
                if pts is not None:
                    rx, ry, rw, rh = cv2.boundingRect(pts)
                    boxes.append((x + rx, y + ry, rw, rh))
                else:
                    boxes.append((x, y, w, h))
    except Exception as e:
        logger.debug(f"Table detection skipped: {e}")
    return _merge_close_boxes(boxes, max_distance=15)


def _detect_diagram_contours(
    gray: np.ndarray,
    excluded_boxes: List[Tuple[int, int, int, int]],
    w_page: int,
    h_page: int
) -> List[Tuple[int, int, int, int]]:
    """Detects geometric figures, function plots, and coordinate axes.
    Rejects text paragraphs, single formula lines, and headers/footers.
    """
    boxes: List[Tuple[int, int, int, int]] = []
    try:
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)

        # Margin suppression
        thresh[:15, :] = 0
        thresh[-15:, :] = 0
        thresh[:, :15] = 0
        thresh[:, -15:] = 0

        # Mask out already detected tables with generous margin
        for ex, ey, ew, eh in excluded_boxes:
            pad = 22
            cv2.rectangle(
                thresh,
                (max(0, ex - pad), max(0, ey - pad)),
                (min(w_page, ex + ew + pad), min(h_page, ey + eh + pad)),
                0,
                -1
            )

        # Detect coordinate axes (perpendicular horizontal and vertical segments >= 36px)
        diag_h = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (36, 1)))
        diag_v = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 36)))
        diag_axes = cv2.add(diag_h, diag_v)

        # Bridge curves and axes together
        d_bridge = cv2.dilate(diag_axes, cv2.getStructuringElement(cv2.MORPH_RECT, (35, 35)), iterations=2)
        contours, _ = cv2.findContours(d_bridge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidate_boxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            aspect = float(w) / max(1, h)

            # Skip footer banner
            if (y + h) > (h_page * 0.94) and w < (w_page * 0.45) and h < 120:
                continue

            # Educational math diagrams: Area >= 22,000 px^2, Width >= 130px, Height >= 110px
            if area < 22000 or w < 130 or h < 110:
                continue

            # Must not be an elongated single-line paragraph or full-bleed banner
            if not (0.40 <= aspect <= 2.4):
                continue
            if w > (w_page * 0.9) or h > (h_page * 0.7):
                continue

            crop_thresh = thresh[y:y+h, x:x+w]

            # Vertical extent check: real 2D math diagrams have vertical axes or curves
            # Text paragraphs or single underlines have near-zero vertical line pixels
            v_check = cv2.morphologyEx(crop_thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 28)))
            if np.sum(v_check > 0) < 50:
                continue

            # Advanced Stroke Analysis: Differentiate 2D diagram graphics from text paragraphs
            num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(crop_thresh)
            if num_labels <= 1:
                continue

            max_component_diagonal = 0.0
            for comp_idx in range(1, num_labels):
                comp_w = stats[comp_idx, cv2.CC_STAT_WIDTH]
                comp_h = stats[comp_idx, cv2.CC_STAT_HEIGHT]
                diag = (comp_w ** 2 + comp_h ** 2) ** 0.5
                if diag > max_component_diagonal:
                    max_component_diagonal = diag

            # Diagrams have coordinate axes or graphic curve strokes (diagonal >= 50px)
            if max_component_diagonal >= 50.0:
                candidate_boxes.append((x, y, w, h))

        boxes = _merge_close_boxes(candidate_boxes, max_distance=25)
    except Exception as e:
        logger.debug(f"Diagram detection skipped: {e}")
    return boxes


def _merge_close_boxes(
    boxes: List[Tuple[int, int, int, int]],
    max_distance: int = 25
) -> List[Tuple[int, int, int, int]]:
    """Merges overlapping or nearby bounding boxes (e.g. axis labels near coordinate plots)."""
    if not boxes:
        return []

    merged = []
    used = [False] * len(boxes)

    for i in range(len(boxes)):
        if used[i]:
            continue
        x1, y1, w1, h1 = boxes[i]
        x2 = x1 + w1
        y2 = y1 + h1
        used[i] = True

        changed = True
        while changed:
            changed = False
            for j in range(len(boxes)):
                if used[j]:
                    continue
                bx1, by1, bw, bh = boxes[j]
                bx2 = bx1 + bw
                by2 = by1 + bh

                # Check if boxes i and j are within max_distance of each other
                if not (bx1 > x2 + max_distance or bx2 < x1 - max_distance or
                        by1 > y2 + max_distance or by2 < y1 - max_distance):
                    x1 = min(x1, bx1)
                    y1 = min(y1, by1)
                    x2 = max(x2, bx2)
                    y2 = max(y2, by2)
                    used[j] = True
                    changed = True

        merged.append((x1, y1, x2 - x1, y2 - y1))

    return merged
