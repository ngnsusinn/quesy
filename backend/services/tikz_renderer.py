"""TikZ Picture to SVG Renderer Service for Quesy.
Compiles LaTeX TikZ / PGFPlots code to vector SVG diagrams with local disk caching.
Conforms to MoET Circular 32/2018/TT-BGDĐT exam geometry and function graphing standards.
"""

import hashlib
import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger("quesy.tikz_renderer")

STORAGE_TIKZ_CACHE = Path(__file__).resolve().parent.parent.parent / "storage" / "tikz_cache"
STORAGE_TIKZ_CACHE.mkdir(parents=True, exist_ok=True)

KROKI_TIKZ_URL = "https://kroki.io/tikz/svg"


def transliterate_vietnamese_for_latex(text: str) -> str:
    """Safely converts Vietnamese diacritics to unaccented ASCII so pdflatex won't crash on Kroki."""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def auto_clip_tikz_plot(tikz_code: str) -> str:
    """Automatically adds a \\clip boundary around coordinate axes if plot exists without clip,
    preventing rational functions or asymptotes from stretching the diagram into extreme aspect ratios.
    """
    if r"\clip" in tikz_code or "plot" not in tikz_code:
        return tikz_code

    pattern = re.compile(
        r'\\draw\[[^\]]*->[^\]]*\]\s*\(\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*\)\s*--\s*\(\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*\)'
    )
    m = pattern.findall(tikz_code)
    if len(m) >= 2:
        xs = [float(c[0]) for c in m if abs(float(c[1])) < 1e-3] + [float(c[2]) for c in m if abs(float(c[3])) < 1e-3]
        ys = [float(c[1]) for c in m if abs(float(c[0])) < 1e-3] + [float(c[3]) for c in m if abs(float(c[2])) < 1e-3]
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            clip_cmd = f"  \\clip ({min_x - 0.8:.1f}, {min_y - 0.8:.1f}) rectangle ({max_x + 0.8:.1f}, {max_y + 0.8:.1f});"
            # Insert clip immediately after \begin{tikzpicture}[...]
            tikz_code = re.sub(
                r'(\\begin\{tikzpicture\}(?:\[[^\]]*\])?)',
                lambda m: f"{m.group(1)}\n{clip_cmd}",
                tikz_code,
                count=1
            )
    return tikz_code


def wrap_tikz_in_standalone_document(tikz_code: str) -> str:
    """Wraps raw TikZ environment inside a complete standalone LaTeX document for compilation."""
    clean_tikz = tikz_code.strip()

    # Remove outer $$ or $ if mistakenly wrapped around tikzpicture
    clean_tikz = re.sub(r'^\$\$?', '', clean_tikz).strip()
    clean_tikz = re.sub(r'\$\$?$', '', clean_tikz).strip()

    # Transliterate any Vietnamese diacritics that cause LaTeX OT1 encoding crash
    clean_tikz = transliterate_vietnamese_for_latex(clean_tikz)

    # Auto-bound extreme aspect ratio plots
    clean_tikz = auto_clip_tikz_plot(clean_tikz)

    # If user provided only draw commands, wrap inside \begin{tikzpicture}...\end{tikzpicture}
    if "\\begin{tikzpicture}" not in clean_tikz:
        clean_tikz = f"\\begin{{tikzpicture}}\n{clean_tikz}\n\\end{{tikzpicture}}"

    doc = (
        "\\documentclass[tikz,border=2mm]{standalone}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\usepackage{pgfplots}\n"
        "\\pgfplotsset{compat=1.18}\n"
        "\\usetikzlibrary{patterns,patterns.meta,arrows.meta,calc,intersections,decorations.pathmorphing,decorations.shapes,angles,quotes,shapes.geometric}\n"
        "\\begin{document}\n"
        f"{clean_tikz}\n"
        "\\end{document}\n"
    )
    return doc


def render_tikz_to_svg(tikz_code: str, timeout: float = 12.0) -> Dict[str, Any]:
    """Compiles TikZ code into SVG using Kroki with local caching."""
    if not tikz_code or not tikz_code.strip():
        return {"success": False, "svg": "", "error": "Empty TikZ code"}

    clean_code = tikz_code.strip()
    code_hash = hashlib.md5(clean_code.encode("utf-8")).hexdigest()
    cache_file = STORAGE_TIKZ_CACHE / f"{code_hash}.svg"

    # 1. Return from disk cache if already compiled
    if cache_file.exists():
        try:
            svg_content = cache_file.read_text(encoding="utf-8")
            if svg_content and "<svg" in svg_content:
                return {"success": True, "svg": svg_content, "cached": True}
        except Exception as e:
            logger.warning(f"Error reading TikZ cache: {e}")

    # 2. Compile via Kroki API
    full_latex_doc = wrap_tikz_in_standalone_document(clean_code)

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                KROKI_TIKZ_URL,
                content=full_latex_doc,
                headers={"Content-Type": "text/plain; charset=utf-8"}
            )

        if resp.status_code == 200:
            svg_text = resp.text
            # Clean xml declaration for inline HTML insertion
            if "<?xml" in svg_text:
                svg_text = re.sub(r'<\?xml.*?\?>', '', svg_text).strip()
            if "<!DOCTYPE" in svg_text:
                svg_text = re.sub(r'<!DOCTYPE.*?>', '', svg_text).strip()

            # Cache to disk
            if "<svg" in svg_text:
                cache_file.write_text(svg_text, encoding="utf-8")
                return {"success": True, "svg": svg_text, "cached": False}
            return {"success": False, "svg": "", "error": "Invalid SVG output"}
        else:
            err_msg = f"Kroki error (HTTP {resp.status_code}): {resp.text[:200]}"
            logger.warning(err_msg)
            return {"success": False, "svg": "", "error": err_msg}

    except Exception as e:
        logger.warning(f"TikZ rendering network/timeout error: {e}")
        return {"success": False, "svg": "", "error": str(e)}


def generate_tikz_fallback_svg(title: str = "Đồ thị TikZ") -> str:
    """Generates an aesthetic SVG placeholder when offline or before compilation."""
    return f"""
    <svg width="240" height="80" viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg" class="mx-auto rounded-lg">
      <rect width="240" height="80" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" rx="8"/>
      <path d="M 30 50 L 70 30 L 110 55 L 150 20 L 190 40 L 210 25" fill="none" stroke="#0071e3" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="150" cy="20" r="4" fill="#0071e3"/>
      <text x="120" y="70" text-anchor="middle" font-family="-apple-system, sans-serif" font-size="11" fill="#64748b">{title}</text>
    </svg>
    """.strip()
