"""MathJax LaTeX Engine Service for Quesy.
Provides high-fidelity mathematical typesetting for Microsoft Word (.docx) and PDF export
using MathJax (inspired by SimpleMathJax) and resvg.

Capabilities:
1. LaTeX to MathML (tex2mml) and native Word OMML (<m:oMath>).
2. LaTeX to vector SVG with exact baseline alignment (vertical-align) metrics.
3. LaTeX to high-resolution PNG (300/600 DPI) with zero-clipping bounding box padding.
4. Local disk and memory caching for maximum export throughput.
"""

import os
import io
import json
import base64
import hashlib
import logging
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

import lxml.etree as etree
from docx.oxml import parse_xml

from backend.config import settings, STORAGE_DIR, BASE_DIR

logger = logging.getLogger("quesy.mathjax_service")

MATHJAX_CACHE_DIR = STORAGE_DIR / "cache" / "mathjax"
MATHJAX_CACHE_DIR.mkdir(parents=True, exist_ok=True)

WORKER_JS_PATH = BASE_DIR / "backend" / "services" / "mathjax_worker.js"

# In-memory LRU-like dictionary cache
_MEM_CACHE: Dict[str, Dict[str, Any]] = {}
_OMML_CACHE: Dict[str, Any] = {}

# Reusable XSLT transformer reference
_xslt_transformer = None

# Persistent Worker Process & Mutex
_worker_proc: Optional[subprocess.Popen] = None
_worker_lock = threading.Lock()


def _get_transformer():
    global _xslt_transformer
    if _xslt_transformer is None:
        from backend.services.docx_exporter import _get_xslt_transformer
        _xslt_transformer = _get_xslt_transformer()
    return _xslt_transformer


def _get_or_create_worker() -> subprocess.Popen:
    """Returns the persistent background Node.js MathJax worker process."""
    global _worker_proc
    if _worker_proc is None or _worker_proc.poll() is not None:
        _worker_proc = subprocess.Popen(
            ["node", str(WORKER_JS_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
    return _worker_proc


def _query_worker(req_payload: dict, timeout_s: float = 12.0) -> Optional[dict]:
    """Sends a single request to the persistent worker and reads the JSON line response,
    with automatic single-attempt retry upon worker desync/crash.
    """
    global _worker_proc
    with _worker_lock:
        for attempt in range(2):
            try:
                worker = _get_or_create_worker()
                req_str = json.dumps(req_payload) + "\n"
                worker.stdin.write(req_str)
                worker.stdin.flush()
                line = worker.stdout.readline()
                if not line:
                    raise RuntimeError("MathJax worker returned empty response line")
                return json.loads(line)
            except Exception as err:
                logger.warning(f"MathJax persistent worker communication error (attempt {attempt+1}/2): {err}")
                if _worker_proc:
                    try:
                        _worker_proc.terminate()
                    except Exception:
                        pass
                    _worker_proc = None
                if attempt == 1:
                    return None
    return None


def clean_latex(latex_code: str) -> str:
    """Strips delimiters and normalizes LaTeX string."""
    clean = (latex_code or "").strip()
    if clean.startswith("${") and clean.endswith("}$"):
        clean = clean[2:-2].strip()
    elif clean.startswith("$$") and clean.endswith("$$"):
        clean = clean[2:-2].strip()
    elif clean.startswith("$") and clean.endswith("$"):
        clean = clean[1:-1].strip()
    return clean


def render_mathjax_equation(
    latex_code: str,
    font_size_pt: float = 11.0,
    dpi: int = 300,
    generate_png: bool = True
) -> Optional[Dict[str, Any]]:
    """Renders a single LaTeX formula using MathJax.

    Returns:
        dict with keys:
            'latex': str
            'mml': str (MathML)
            'svg': str (SVG with padding)
            'w_pt': float (width in pt)
            'h_pt': float (height in pt)
            'depth_pt': float (descent below baseline in pt)
            'shift_half_pt': int (Word w:position value)
            'png_bytes': Optional[bytes]
        or None if conversion fails.
    """
    clean = clean_latex(latex_code)
    if not clean:
        return None

    cache_key = f"{clean}|{font_size_pt}|{dpi}|{generate_png}"
    if cache_key in _MEM_CACHE:
        return _MEM_CACHE[cache_key]

    disk_hash = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
    meta_path = MATHJAX_CACHE_DIR / f"{disk_hash}.json"
    png_path = MATHJAX_CACHE_DIR / f"{disk_hash}.png"

    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                res = json.load(f)
            if png_path.exists():
                res["png_bytes"] = png_path.read_bytes()
            else:
                res["png_bytes"] = None
            _MEM_CACHE[cache_key] = res
            return res
        except Exception as e:
            logger.debug(f"Failed to read MathJax disk cache: {e}")

    req_payload = {
        "latex": clean,
        "fontSizePt": font_size_pt,
        "dpi": dpi,
        "generatePng": generate_png
    }

    data = _query_worker(req_payload)
    if not data or data.get("error"):
        return None

    try:
        png_bytes = None
        if data.get("png_base64"):
            png_bytes = base64.b64decode(data["png_base64"])

        res = {
            "latex": clean,
            "mml": data.get("mml"),
            "svg": data.get("svg"),
            "w_pt": data.get("w_pt", 0.0),
            "h_pt": data.get("h_pt", 0.0),
            "depth_pt": data.get("depth_pt", 0.0),
            "shift_half_pt": data.get("shift_half_pt", 0),
            "png_bytes": png_bytes
        }

        # Save to disk cache
        try:
            meta_to_save = {k: v for k, v in res.items() if k != "png_bytes"}
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta_to_save, f, ensure_ascii=False)
            if png_bytes:
                png_path.write_bytes(png_bytes)
        except Exception as e:
            logger.debug(f"Could not write MathJax disk cache: {e}")

        _MEM_CACHE[cache_key] = res
        return res

    except Exception as err:
        logger.warning(f"MathJax rendering failed for '{clean[:30]}': {err}")
        return None


def convert_latex_to_omml_mathjax(latex_code: str) -> Optional[Any]:
    """Converts a LaTeX expression to native Word OMML (<m:oMath>) using MathJax + XSLT."""
    clean = clean_latex(latex_code)
    if not clean:
        return None

    if clean in _OMML_CACHE:
        # Clone XML node
        return parse_xml(etree.tostring(_OMML_CACHE[clean]).decode("utf-8"))

    mj_res = render_mathjax_equation(clean, generate_png=False)
    if not mj_res or not mj_res.get("mml"):
        return None

    mml_str = mj_res["mml"]
    transformer = _get_transformer()
    if transformer is None:
        return None

    try:
        mml_dom = etree.fromstring(mml_str.encode("utf-8"))
        omml_dom = transformer(mml_dom)
        omml_str = etree.tostring(omml_dom).decode("utf-8")
        omml_elem = parse_xml(omml_str)
        _OMML_CACHE[clean] = omml_elem
        return parse_xml(omml_str)
    except Exception as e:
        logger.debug(f"OMML transform error for '{clean[:30]}': {e}")
        return None


def render_mathjax_batch(
    formulas: List[str],
    font_size_pt: float = 11.0,
    dpi: int = 300,
    generate_png: bool = True
) -> Dict[str, Dict[str, Any]]:
    """Batch-renders a list of formulas using the persistent worker."""
    results = {}
    for f in formulas:
        c = clean_latex(f)
        if not c:
            continue
        res = render_mathjax_equation(c, font_size_pt=font_size_pt, dpi=dpi, generate_png=generate_png)
        if res:
            results[c] = res
    return results
