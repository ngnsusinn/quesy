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

        # 1. Detect Tables via Horizontal and Vertical Grid Segments
        table_boxes = _detect_table_grids(gray)

        # 2. Detect Diagrams and Coordinate Plots
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

            # Add 12px safe padding
            pad = 12
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


def _detect_table_grids(gray: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """Detects table structures through horizontal and vertical grid line intersection."""
    boxes: List[Tuple[int, int, int, int]] = []
    try:
        # Binary inverse threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5)

        # Detect horizontal lines
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 1))
        h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

        # Detect vertical lines
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
        v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

        # Table structure is the combination of horizontal and vertical grids
        table_mask = cv2.add(h_lines, v_lines)
        table_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        table_mask = cv2.dilate(table_mask, table_kernel, iterations=2)

        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            # Filter table by minimum size (must be at least 160px wide and 55px tall)
            if w > 160 and h > 55 and (w * h) > 12000:
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
    """Detects geometric figures, function plots, and coordinate axes."""
    boxes: List[Tuple[int, int, int, int]] = []
    try:
        # Gaussian blur + Otsu threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Mask out already detected tables
        for ex, ey, ew, eh in excluded_boxes:
            cv2.rectangle(thresh, (max(0, ex - 5), max(0, ey - 5)), (min(w_page, ex + ew + 5), min(h_page, ey + eh + 5)), 0, -1)

        # Close small gaps in line drawings
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidate_boxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            aspect_ratio = float(w) / max(1, h)

            # Criteria for diagrams/plots (unlike normal text lines which are wide and short):
            # 1. Minimum width > 110px and height > 90px
            # 2. Area > 14,000 px^2
            # 3. Aspect ratio between 0.35 and 2.8 (square-ish / boxy)
            # 4. Less than 85% of total page width/height (avoid capturing whole page border)
            if w > 110 and h > 90 and area > 14000:
                if 0.35 <= aspect_ratio <= 2.8 and w < (w_page * 0.88) and h < (h_page * 0.65):
                    candidate_boxes.append((x, y, w, h))

        boxes = _merge_close_boxes(candidate_boxes, max_distance=28)
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
