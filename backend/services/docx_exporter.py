import os
import io
import re
import sys
import shutil
import threading
import ctypes
import struct
import zipfile
import json
import hashlib
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

import docx
from docx.shared import Inches, Pt, Cm, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls, nsmap
from docx.opc.part import Part
from docx.opc.packuri import PackURI
import lxml.etree as etree

from backend.config import settings
from backend.services.composer_service import compile_latex_to_pdf

try:
    import matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'Times New Roman'
    matplotlib.rcParams['mathtext.it'] = 'Times New Roman:italic'
    matplotlib.rcParams['mathtext.bf'] = 'Times New Roman:bold'
    matplotlib.rcParams['mathtext.sf'] = 'Times New Roman'
    matplotlib.rcParams['mathtext.tt'] = 'Courier New'
except Exception:
    pass

# Register VML / Office namespaces for MathType OLE embedding
nsmap['v'] = 'urn:schemas-microsoft-com:vml'
nsmap['o'] = 'urn:schemas-microsoft-com:office:office'

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False

from sqlalchemy.orm import Session
from backend.models import MasterExam, ExamVariant, Question, ExamVariantItem


STORAGE_EXPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "exports"
STORAGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

STORAGE_MATH_CACHE = Path(__file__).resolve().parent.parent.parent / "storage" / "math_cache"
STORAGE_MATH_CACHE.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
MML2OMML_PATH = ASSETS_DIR / "MML2OMML.XSL"
MATHTYPE_TEMPLATE_PATH = ASSETS_DIR / "mathtype_template.bin"

_MATHTYPE_TEMPLATE_BYTES = None

def _get_mathtype_template_bytes() -> bytes:
    global _MATHTYPE_TEMPLATE_BYTES
    if _MATHTYPE_TEMPLATE_BYTES is None:
        if MATHTYPE_TEMPLATE_PATH.exists():
            _MATHTYPE_TEMPLATE_BYTES = MATHTYPE_TEMPLATE_PATH.read_bytes()
        else:
            _MATHTYPE_TEMPLATE_BYTES = b""
    return _MATHTYPE_TEMPLATE_BYTES

_MATH_PARSER = None


def _get_math_parser():
    global _MATH_PARSER
    if _MATH_PARSER is None:
        try:
            from matplotlib.mathtext import MathTextParser
            _MATH_PARSER = MathTextParser('agg')
        except Exception as e:
            logger.warning(f"Could not initialize MathTextParser: {e}")
    return _MATH_PARSER


def render_latex_to_mathtype_image(latex_expr: str) -> Optional[Tuple[str, float]]:
    """Renders LaTeX formula to a high-resolution PNG image (MathType-like appearance)
    and returns (image_path, height_in_points) for inline embedding into python-docx.
    Uses disk caching under storage/math_cache.
    """
    if not latex_expr or not latex_expr.strip():
        return None

    clean = latex_expr.strip()
    while clean.startswith("$"):
        clean = clean[1:].strip()
    while clean.endswith("$"):
        clean = clean[:-1].strip()

    if not clean:
        return None

    cache_key = hashlib.md5(clean.encode("utf-8")).hexdigest()
    img_path = STORAGE_MATH_CACHE / f"{cache_key}.png"

    if img_path.exists() and img_path.stat().st_size > 0:
        try:
            from PIL import Image
            with Image.open(img_path) as im:
                h_pt = max(8.0, min(65.0, (im.height / 200.0) * 72.0))
                return str(img_path), h_pt
        except Exception:
            pass

    # 1. Try Matplotlib MathTextParser (Fast & Offline)
    parser = _get_math_parser()
    if parser:
        try:
            from PIL import Image
            import numpy as np

            m_code = clean
            m_code = m_code.replace(r"\dfrac", r"\frac")
            m_code = m_code.replace(r"\overrightarrow", r"\vec")
            m_code = m_code.replace(r"\setminus", r"\backslash")
            m_code = m_code.replace("{,}", ",")
            m_code = m_code.replace(r"\left", "").replace(r"\right", "")

            res = parser.parse(f"${m_code}$", dpi=600)
            arr = res[5].astype(np.float32) / 255.0
            arr_boosted = np.clip(np.power(arr, 0.45) * 255.0, 0, 255).astype(np.uint8)
            h, w = arr_boosted.shape
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            rgba[:, :, 3] = arr_boosted
            im = Image.fromarray(rgba)
            im.save(str(img_path), format='PNG', dpi=(600, 600))
            h_pt = max(8.0, min(65.0, (h / 600.0) * 72.0))
            return str(img_path), h_pt
        except Exception as e:
            logger.debug(f"MathTextParser fallback for '{clean[:30]}': {e}")

    # 2. Fallback to Kroki /tikz/png with node
    try:
        import httpx
        from backend.services.tikz_renderer import KROKI_TIKZ_PNG_URL
        tex_doc = (
            r"\documentclass[tikz,border=1pt]{standalone}" "\n"
            r"\usepackage{amsmath,amssymb}" "\n"
            r"\begin{document}" "\n"
            r"\begin{tikzpicture}" "\n"
            rf"\node[inner sep=0pt] at (0,0) {{${clean}$}};" "\n"
            r"\end{tikzpicture}" "\n"
            r"\end{document}"
        )
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(KROKI_TIKZ_PNG_URL, content=tex_doc.encode("utf-8"), headers={"Content-Type": "text/plain; charset=utf-8"})
            if resp.status_code == 200 and resp.content[:8] == b'\x89PNG\r\n\x1a\n':
                img_path.write_bytes(resp.content)
                from PIL import Image
                with Image.open(img_path) as im:
                    h_pt = max(8.0, min(65.0, (im.height / 200.0) * 72.0))
                    return str(img_path), h_pt
    except Exception as e:
        logger.debug(f"Kroki fallback error: {e}")

    return None


# ---------------------------------------------------------------------------
# 1. Native OMML Equation Converter
# ---------------------------------------------------------------------------

_xslt_transformer = None


def _get_xslt_transformer():
    """Lazily load and cache MML2OMML XSLT transformer."""
    global _xslt_transformer
    if _xslt_transformer is not None:
        return _xslt_transformer

    candidate_paths = [
        MML2OMML_PATH,
        Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"),
        Path(r"C:\Program Files (x86)\Microsoft Office\root\Office16\MML2OMML.XSL"),
    ]

    for p in candidate_paths:
        if p.exists():
            try:
                xslt_tree = etree.parse(str(p))
                _xslt_transformer = etree.XSLT(xslt_tree)
                return _xslt_transformer
            except Exception:
                continue

    return None


def clean_math_expr(text: str) -> str:
    """Strips math delimiters ($...$, $$...$$, ${...}$, $${...}$$) and single outer enclosing braces."""
    if not text:
        return ""
    s = text.strip()
    # Strip any enclosing single or double quotes (e.g. "'${...}'")
    while (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    if s.startswith("${") and s.endswith("}$"):
        s = s[2:-2].strip()
    elif s.startswith("$$") and s.endswith("$$"):
        s = s[2:-2].strip()
    elif s.startswith("$") and s.endswith("$"):
        s = s[1:-1].strip()
    while s.startswith("{") and s.endswith("}"):
        depth = 0
        is_enclosing = True
        for idx, ch in enumerate(s):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and idx < len(s) - 1:
                    is_enclosing = False
                    break
        if is_enclosing and depth == 0:
            s = s[1:-1].strip()
        else:
            break
    # Promote \frac to \dfrac for full-size professional math exam display
    s = re.sub(r"(?<![a-zA-Z\\])\\frac(?![a-zA-Z])", r"\\dfrac", s)
    return s


def convert_latex_to_omml(latex_code: str) -> Optional[Any]:
    """Converts a LaTeX math expression to a native Word OMML (<m:oMath>) XML element
    using MathJax (high fidelity, complete TeX package support) with latex2mathml fallback.
    """
    clean_code = clean_math_expr(latex_code)
    if not clean_code:
        return None

    # 1. Try MathJax engine first (handles \overrightarrow, \dfrac, cases, matrices, etc.)
    try:
        from backend.services.mathjax_service import convert_latex_to_omml_mathjax
        omml_elem = convert_latex_to_omml_mathjax(clean_code)
        if omml_elem is not None:
            return omml_elem
    except Exception as e:
        logger.debug(f"MathJax OMML conversion error: {e}")

    if not HAS_LATEX2MATHML:
        return None

    clean_code = clean_code.replace(r"\mathbb{R}", "R").replace(r"\mathbb{Z}", "Z")
    clean_code = clean_code.replace(r"\mathbb{N}", "N").replace(r"\mathbb{Q}", "Q")

    try:
        transformer = _get_xslt_transformer()
        mml_str = latex2mathml.converter.convert(clean_code)
        if transformer is not None:
            mml_dom = etree.fromstring(mml_str.encode("utf-8"))
            omml_dom = transformer(mml_dom)
            omml_str = etree.tostring(omml_dom).decode("utf-8")
            return parse_xml(omml_str)
    except Exception:
        pass

    return None


def _custom_mathtype_preamble(mathtype_version: str = "DSMT7", base_pt: float = 11.0, raw_latex: Optional[str] = None) -> bytes:
    import docx_equation.mathtype.mtef as mtef
    pref = mtef._equation_preferences()
    if base_pt == 11.0:
        pref = pref.replace(bytes.fromhex("21 2f"), bytes.fromhex("21 1f"))
    parts = [
        b"\x05\x01\x00\x07\x04DSMT7\x00\x01",
    ]
    if raw_latex:
        parts.append(b"f'TeX Input Language\x00" + raw_latex.encode("utf-8") + b"\x00")
    parts.extend([
        b"\x13WinAllBasicCodePages\x00",
        mtef._font_def(5, "Times New Roman"),
        mtef._font_def(3, "Symbol"),
        mtef._font_def(5, "Courier New"),
        mtef._font_def(4, "MT Extra"),
        pref,
    ])
    return b"".join(parts)


def _custom_encode_mtef(expr, base_pt: float = 11.0, raw_latex: Optional[str] = None) -> bytes:
    import docx_equation.mathtype.mtef as mtef
    import unicodedata

    # Ensure docx_equation does not emit corrupt MTEF bytes or spurious size/style overrides
    mtef._empty_line = lambda: b"\x01\x01"

    # Clean script encoders matching native MathType 7 byte-for-byte:
    # 0x0B (SIZE: SUB) is placed immediately after TMPL (before slot line) so kerning and spacing match native MathType
    null_slot = bytes([0x01, 0x01])  # 2-byte null slot (no END tag per MTEF spec for mtefOPT_LINE_NULL)

    def _clean_superscript_encode(self):
        tmpl = bytes([0x03, 0x00, 0x1C, 0x00, 0x00, 0x0B])
        return self.base.encode() + tmpl + null_slot + mtef._line(self.superscript) + bytes([0x00, 0x0A])

    def _clean_subscript_encode(self):
        tmpl = bytes([0x03, 0x00, 0x1B, 0x00, 0x00, 0x0B])
        return self.base.encode() + tmpl + mtef._line(self.subscript) + null_slot + bytes([0x00, 0x0A])

    def _clean_subsup_encode(self):
        tmpl = bytes([0x03, 0x00, 0x1D, 0x00, 0x00, 0x0B])
        return self.base.encode() + tmpl + mtef._line(self.subscript) + mtef._line(self.superscript) + bytes([0x00, 0x0A])

    def _custom_hat_encode(self):
        body = self.body
        is_single = False
        single_char = None
        if isinstance(body, mtef.Text) and len(body.value) == 1:
            is_single = True
            single_char = body.value
        elif isinstance(body, mtef.Symbol):
            is_single = True
            single_char = body.char
        elif isinstance(body, mtef.Sequence) and len(body.items) == 1:
            it = body.items[0]
            if isinstance(it, mtef.Text) and len(it.value) == 1:
                is_single = True
                single_char = it.value
            elif isinstance(it, mtef.Symbol):
                is_single = True
                single_char = it.char

        if is_single and self.kind == "vector":
            base_b = mtef._encode_char(single_char)
            base_emb = bytes([base_b[0], base_b[1] | 0x01]) + base_b[2:]
            return base_emb + bytes([0x06, 0x00, 11])

        if self.kind == "vector":
            return (
                bytes([0x03, 0x00, 0x1F, 0x02, 0x00, 0x0F, 0x00, 0x01, 0x00, 0x0F, 0x01])
                + body.encode()
                + bytes([0x00, 0x02, 0x00, 0x96, 0xD7, 0x20, 0x00])
            )

        sel = 0x20 if self.kind == "tilde" else 0x21
        return mtef._template(sel, 0, 0) + mtef._line(body) + b"\x00"

    mtef.Hat.encode = _custom_hat_encode

    # Clean character and text encoders: uniform font styles
    KNOWN_FUNCTIONS = {"sin", "cos", "tan", "cot", "log", "ln", "lim", "exp", "min", "max", "arcsin", "arccos", "arctan"}

    # Additional operators for MathType MTEF
    if "\\" not in mtef._OPERATOR_CODE:
        mtef._OPERATOR_CODE["\\"] = (0x005C, 0x5C)
    if "\u2216" not in mtef._OPERATOR_CODE:
        mtef._OPERATOR_CODE["\u2216"] = (0x2216, 0x5C)
    if "|" not in mtef._OPERATOR_CODE:
        mtef._OPERATOR_CODE["|"] = (0x007C, 0x7C)
    if "\u2223" not in mtef._OPERATOR_CODE:
        mtef._OPERATOR_CODE["\u2223"] = (0x2223, 0x7C)

    # Invisible MathML / Unicode characters that cause black diamond replacement symbols () in MathType
    INVISIBLE_MATH_CHARS = {
        "\u2061",  # ApplyFunction
        "\u2062",  # InvisibleTimes
        "\u2063",  # InvisibleComma
        "\u2064",  # InvisiblePlus
        "\u200b",  # ZERO WIDTH SPACE
        "\u200c",  # ZERO WIDTH NON-JOINER
        "\u200d",  # ZERO WIDTH JOINER
        "\u200e",  # LTR Mark
        "\u200f",  # RTL Mark
        "\ufeff",  # ZERO WIDTH NO-BREAK SPACE / BOM
    }

    def _improved_encode_char(char: str) -> bytes:
        if len(char) != 1:
            return b"".join(_improved_encode_char(item) for item in char)
        if char in INVISIBLE_MATH_CHARS or char == "\u00a0":
            return b"" if char in INVISIBLE_MATH_CHARS else b" "
        if char in mtef._OPERATOR_CODE:
            unicode_code, mt_code = mtef._OPERATOR_CODE[char]
            return bytes([0x02, 0x04, 0x86]) + unicode_code.to_bytes(2, "little") + bytes([mt_code])
        if char.isdigit() or char in ",.":
            typeface = 0x88  # fnNUMBER (Numbers and decimal separators in uniform upright style)
        elif char.isalpha():
            typeface = 0x83  # fnVARIABLE (Italic math variables)
        elif char in "()[]{}":
            typeface = 0x82  # fnFUNCTION / Fences and grouping brackets (ensures MathType displays [, ], (, ), {, })
        elif char in ";:":
            typeface = 0x81  # fnTEXT (Punctuation)
        elif char in "\\|":
            typeface = 0x86  # fnSYMBOL (Set difference backslash, vertical bars)
        elif char.isspace():
            typeface = 0x86  # fnSYMBOL
        elif unicodedata.category(char).startswith(("S", "M")):
            typeface = 0x86  # fnSYMBOL
        else:
            typeface = 0x83
        code_point = ord(char)
        if code_point > 0xFFFF:
            raise ValueError(f"Character outside BMP: {char!r}")
        return bytes([0x02, 0x00, typeface]) + code_point.to_bytes(2, "little")

    def _text_encode(self) -> bytes:
        val = self.value
        if val.lower() in KNOWN_FUNCTIONS:
            return b"".join(
                bytes([0x02, 0x00, 0x82]) + ord(c).to_bytes(2, "little")
                for c in val
            )
        return b"".join(_improved_encode_char(c) for c in val)

    mtef._encode_char = _improved_encode_char
    mtef.Text.encode = _text_encode
    mtef.Superscript.encode = _clean_superscript_encode
    mtef.Subscript.encode = _clean_subscript_encode
    mtef.Subsup.encode = _clean_subsup_encode

    return _custom_mathtype_preamble("DSMT7", base_pt=float(base_pt), raw_latex=raw_latex) + b"\x0a" + mtef._line(expr)


def _build_mathtype_cfb_binary(mtef_bytes: bytes) -> bytes:
    """Builds a compliant OLE Compound File (CFB) with root CLSID {0002CE03-0000-0000-C000-000000000046}
    and red-black directory tree for MathType 7.0 equation activation in Microsoft Word.
    """
    import docx_equation.mathtype.cfb as cfb
    import docx_equation.mathtype.ole as ole

    compobj = bytes.fromhex(
        "0100feff030a0000ffffffff03ce020000000000c000000000000046"
        "160000004d6174685479706520372e30204571756174696f6e00"
        "0c0000004d6174685479706520454600"
        "0f0000004571756174696f6e2e44534d543400"
        "f439b271000000000000000000000000"
    )
    objinfo = bytes.fromhex("000003000400")
    ole_s = bytes.fromhex("0100000208000000000000000000000000000000")
    eq_native = ole._equation_native_stream(mtef_bytes)

    streams = {
        "\x01CompObj": compobj,
        "\x01Ole": ole_s,
        "\x03ObjInfo": objinfo,
        "Equation Native": eq_native,
    }

    ordered_names = ["\x01Ole", "\x01CompObj", "\x03ObjInfo", "Equation Native"]
    ordered_streams = [cfb.Stream(name, streams[name], 0) for name in ordered_names]

    mini_stream = bytearray()
    updated = []
    mini_fat_entries = []

    for stream in ordered_streams:
        start = len(mini_stream) // cfb.MINI_SECTOR_SIZE
        sectors = max(1, cfb.ceil(len(stream.data) / cfb.MINI_SECTOR_SIZE))
        padded = stream.data + b"\x00" * (sectors * cfb.MINI_SECTOR_SIZE - len(stream.data))
        mini_stream.extend(padded)
        for offset in range(sectors):
            if offset == sectors - 1:
                mini_fat_entries.append(cfb.ENDOFCHAIN)
            else:
                mini_fat_entries.append(start + offset + 1)
        updated.append(cfb.Stream(stream.name, stream.data, start))

    mini_stream_bytes = cfb._pad(bytes(mini_stream), cfb.SECTOR_SIZE)
    mini_stream_sector_count = len(mini_stream_bytes) // cfb.SECTOR_SIZE
    mini_fat_bytes = cfb._pack_sector_entries(mini_fat_entries)
    mini_fat_sector_count = len(mini_fat_bytes) // cfb.SECTOR_SIZE

    directory_start = 1
    directory_sector_count = 2

    mini_stream_start = directory_start + directory_sector_count
    mini_fat_start = mini_stream_start + mini_stream_sector_count
    fat_sector_index = 0
    sector_count = 1 + directory_sector_count + mini_stream_sector_count + mini_fat_sector_count

    entries = []
    # Root Entry (sid 0, points to child 2 = \x01CompObj)
    root = bytearray(cfb._directory_entry(
        "Root Entry", object_type=5, color=0, left=cfb.NOSTREAM, right=cfb.NOSTREAM, child=2,
        start_sector=mini_stream_start, stream_size=len(mini_stream),
    ))
    root[80:96] = bytes.fromhex("03 ce 02 00 00 00 00 00 c0 00 00 00 00 00 00 46")
    entries.append(bytes(root))

    # sid 1: \x01Ole
    s1 = updated[0]
    entries.append(cfb._directory_entry(
        s1.name, object_type=2, color=1, left=cfb.NOSTREAM, right=cfb.NOSTREAM, child=cfb.NOSTREAM,
        start_sector=s1.start_mini_sector, stream_size=len(s1.data)
    ))

    # sid 2: \x01CompObj (left=1, right=3)
    s2 = updated[1]
    entries.append(cfb._directory_entry(
        s2.name, object_type=2, color=1, left=1, right=3, child=cfb.NOSTREAM,
        start_sector=s2.start_mini_sector, stream_size=len(s2.data)
    ))

    # sid 3: \x03ObjInfo (left=NOSTREAM, right=4)
    s3 = updated[2]
    entries.append(cfb._directory_entry(
        s3.name, object_type=2, color=1, left=cfb.NOSTREAM, right=4, child=cfb.NOSTREAM,
        start_sector=s3.start_mini_sector, stream_size=len(s3.data)
    ))

    # sid 4: Equation Native (left=NOSTREAM, right=NOSTREAM)
    s4 = updated[3]
    entries.append(cfb._directory_entry(
        s4.name, object_type=2, color=0, left=cfb.NOSTREAM, right=cfb.NOSTREAM, child=cfb.NOSTREAM,
        start_sector=s4.start_mini_sector, stream_size=len(s4.data)
    ))

    while len(entries) % 4 != 0:
        entries.append(bytes(128))
    directory_bytes = b"".join(entries)

    fat_entries = [cfb.FREESECT] * (cfb.ceil(sector_count / 128) * 128)
    fat_entries[fat_sector_index] = cfb.FATSECT
    for index in range(directory_sector_count):
        sector = directory_start + index
        fat_entries[sector] = directory_start + index + 1 if index < directory_sector_count - 1 else cfb.ENDOFCHAIN

    for index in range(mini_stream_sector_count):
        sector = mini_stream_start + index
        fat_entries[sector] = mini_stream_start + index + 1 if index < mini_stream_sector_count - 1 else cfb.ENDOFCHAIN
    for index in range(mini_fat_sector_count):
        sector = mini_fat_start + index
        fat_entries[sector] = mini_fat_start + index + 1 if index < mini_fat_sector_count - 1 else cfb.ENDOFCHAIN

    fat_bytes = cfb._pack_sector_entries(fat_entries[:128])
    header = cfb._header(
        fat_sector_index=fat_sector_index,
        directory_start=directory_start,
        mini_fat_start=mini_fat_start,
        mini_fat_sector_count=mini_fat_sector_count,
    )
    return b"".join([header, fat_bytes, directory_bytes, mini_stream_bytes, mini_fat_bytes])


def generate_mathtype_ole(latex_math: str, default_font_size: Union[int, float] = 11) -> bytes:
    """Encodes LaTeX formula into compliant MathType 7.0 OLE CFB binary."""
    clean = latex_math.strip().strip("$").strip()
    clean = clean.replace(r"\setminus", r"\backslash").replace("{,}", ",")

    try:
        import docx_equation
        mml = None
        try:
            from backend.services.mathjax_service import render_mathjax_equation
            mj_res = render_mathjax_equation(clean, generate_png=False)
            if mj_res and mj_res.get("mml"):
                mml = mj_res["mml"]
                for inv in ["\u2061", "\u2062", "\u2063", "\u2064", "\u200b", "\ufeff", "&#x2061;", "&#x2062;", "&#x2063;", "&#x2064;"]:
                    mml = mml.replace(inv, "")
        except Exception:
            pass
        if not mml:
            import latex2mathml.converter
            mml = latex2mathml.converter.convert(clean)
        expr = docx_equation.parse_mathml(mml)
        mtef_bytes = _custom_encode_mtef(expr, base_pt=float(default_font_size), raw_latex=clean)
    except Exception:
        # Fallback to simple DSMT7 MTEF
        mtef_bytes = _custom_mathtype_preamble("DSMT7", base_pt=float(default_font_size), raw_latex=clean) + b"\x0a\x01\x00\x02\x00\x83x\x00\x00\x00"

    return _build_mathtype_cfb_binary(mtef_bytes)


BLACKBOARD_BOLD_TO_LATIN = {
    0x211a: ord("Q"),  # \mathbb{Q}
    0x211d: ord("R"),  # \mathbb{R}
    0x2124: ord("Z"),  # \mathbb{Z}
    0x2115: ord("N"),  # \mathbb{N}
    0x2102: ord("C"),  # \mathbb{C}
}

UNICODE_TO_SYMBOL = {
    0x03c0: 0x70,  # \pi
    0x03b1: 0x61,  # \alpha
    0x03b2: 0x62,  # \beta
    0x03b3: 0x67,  # \gamma
    0x03b4: 0x64,  # \delta
    0x03b5: 0x65,  # \epsilon
    0x03b8: 0x71,  # \theta
    0x03bb: 0x6c,  # \lambda
    0x03bc: 0x6d,  # \mu
    0x03c3: 0x73,  # \sigma
    0x03c6: 0x6a,  # \phi
    0x03c9: 0x77,  # \omega
    0x0394: 0x44,  # \Delta
    0x03a9: 0x57,  # \Omega
    0x221a: 0xd6,  # \sqrt
    0x2264: 0xa3,  # \le
    0x2265: 0xb3,  # \ge
    0x2260: 0xb9,  # \ne
    0x00b1: 0xb1,  # \pm
    0x00d7: 0xb4,  # \times
    0x00f7: 0xb8,  # \div
    0x2212: 0x2d,  # minus −
    0x2248: 0xbb,  # \approx
    0x2208: 0xce,  # \in
    0x2209: 0xcf,  # \notin
    0x221e: 0xa5,  # \infty
    0x2192: 0xae,  # \rightarrow
    0x20d7: 0xae,  # combining vector arrow
    0x21d2: 0xde,  # \Rightarrow
    0x21d4: 0xdb,  # \Leftrightarrow
    0x22c5: 0xd7,  # \cdot
    0x2202: 0xb6,  # \partial
    0x222b: 0xf2,  # \int
    0x2205: 0xc6,  # \emptyset
    0x2229: 0xc7,  # \cap
    0x222a: 0xc8,  # \cup
    0x2282: 0xcc,  # \subset
    0x2286: 0xcd,  # \subseteq
    0x2200: 0x22,  # \forall
    0x2203: 0x24,  # \exists
    0x2220: 0xd0,  # \angle
    0x22a5: 0x5e,  # \perp
    0x2216: 0x5c,  # \setminus (set difference \)
    0x2223: 0x7c,  # \mid (|)
    0x2236: 0x3a,  # \colon (:)
    0x2026: 0x85,  # \dots (…)
    0x2032: 0xa2,  # prime ′ (MathType standard)
    0x2033: 0xb2,  # double prime ″
    0x2034: 0xb3,  # triple prime ‴
}


def _build_wmf_rec(func: int, data: bytes = b"") -> bytes:
    if len(data) % 2 != 0:
        data += b"\x00"
    size_words = (len(data) + 6) // 2
    return struct.pack("<IH", size_words, func) + data


def _create_logfont_record(name: str, height: int, italic: bool = False, charset: int = 0, weight: int = 400) -> bytes:
    face = name.encode("ascii")[:31].ljust(32, b"\x00")
    return struct.pack("<hhhhhBBBBBBBB", height, 0, 0, 0, weight, 1 if italic else 0, 0, 0, charset, 0, 0, 0, 0) + face


def _render_compliant_mathtype_wmf(clean_latex: str, default_font_size: Union[int, float] = 11) -> Optional[Tuple[bytes, float, float, float]]:
    """Builds a compliant vector Windows Metafile (WMF) in 100% pure Python with MOVETO & TA_UPDATECP.
    When Microsoft Word exports to PDF, Word parses these records into real selectable vector text.
    Zero DLL dependencies — runs natively on Linux, Docker, Windows.
    """
    try:
        clean = clean_latex
        m_code = clean.replace("{,}", ",")
        m_code = re.sub(r"\\setminus(?![a-zA-Z])", r"\\backslash", m_code)
        m_code = re.sub(r"\\middle(?![a-zA-Z])", "", m_code)
        m_code = re.sub(r"\\mid(?![a-zA-Z])", "|", m_code)
        m_code = re.sub(r"\\overrightarrow(?![a-zA-Z])", r"\\vec", m_code)
        m_code = re.sub(r"\\widehat(?![a-zA-Z])", r"\\hat", m_code)
        m_code = re.sub(r"\\ne(?![a-zA-Z])", r"\\neq", m_code)
        m_code = re.sub(r"\\le(?![a-zA-Z])", r"\\leq", m_code)
        m_code = re.sub(r"\\ge(?![a-zA-Z])", r"\\geq", m_code)
        m_code = re.sub(r"\\mathbb\{([A-Za-z])\}", r"\\mathbf{\1}", m_code)
        m_code = m_code.replace(r"\mathbb{Q}", r"\mathbf{Q}").replace(r"\mathbb{R}", r"\mathbf{R}").replace(r"\mathbb{Z}", r"\mathbf{Z}").replace(r"\mathbb{N}", r"\mathbf{N}").replace(r"\mathbb{C}", r"\mathbf{C}")
        m_code = m_code.replace('"', "").replace('"', "").replace(r"\_", "_")
        m_code = m_code.replace(r"\varnothing", r"\emptyset")
        # 1. Normalize spaces around relational operators (=, <, >, \le, \ge)
        m_code = re.sub(r"(?<![<>=!\\:])=(?!=)", " = ", m_code)
        m_code = re.sub(r"(?<![<>=!\\:])<(?![=<])", " < ", m_code)
        m_code = re.sub(r"(?<![<>=!\\:])>(?![=>])", " > ", m_code)

        # 2. Normalize spaces around binary + and - between operands
        m_code = re.sub(r"(?<=[a-zA-Z0-9\}\)])\s*\+\s*(?=[a-zA-Z0-9\{\\])", " + ", m_code)
        m_code = re.sub(r"(?<=[a-zA-Z0-9\}\)])\s*-\s*(?=[a-zA-Z0-9\{\\])", " - ", m_code)

        # 3. Add italic spacing between single letter variable/function or prime and opening paren:
        m_code = re.sub(r"(?<![a-zA-Z\\])([a-zA-Z]|(?:[a-zA-Z]'+))\s*(\\(?:left\s*)?\()", r"\1\,\2", m_code)

        # 4. Add spacing between adjacent factors: (x+2)(x-1) -> (x+2)\,(x-1) or \right)\left( -> \right)\,\left(
        m_code = re.sub(r"(\)|\\right\))\s*(\^\{?\d+\}?)?\s*(\(|\\left\()", r"\1\2\,\3", m_code)
        m_code = re.sub(r"[ \t]+", " ", m_code).strip()
        m_code = m_code.strip("$").strip()

        from matplotlib.mathtext import MathTextParser
        from matplotlib.font_manager import FontProperties

        parser = MathTextParser("path")
        prop = FontProperties(size=default_font_size)
        try:
            w_pt, h_pt, d_pt, glyphs, rects = parser.parse(f"${m_code}$", dpi=72, prop=prop)
        except Exception:
            fallback = m_code.replace(r"\left", "").replace(r"\right", "")
            try:
                w_pt, h_pt, d_pt, glyphs, rects = parser.parse(f"${fallback}$", dpi=72, prop=prop)
            except Exception:
                w_pt, h_pt, d_pt, glyphs, rects = parser.parse(fallback, dpi=72, prop=prop)

        # Calculate exact bounding envelope across all glyphs and rects
        all_top_pts = [g[5] + g[1] * 0.75 for g in glyphs] + [r[1] + r[3] for r in rects]
        all_bot_pts = [g[5] - g[1] * 0.25 for g in glyphs] + [r[1] for r in rects]

        max_ascent = max(all_top_pts, default=default_font_size * 0.80)
        max_descent = -min(all_bot_pts, default=-default_font_size * 0.22)

        has_subscript = bool(re.search(r'_[^{\s]|_\{', m_code))
        has_superscript = bool(re.search(r'\^[^{\s]|\^\{', m_code))
        has_fraction = r"\frac" in m_code or r"\dfrac" in m_code

        min_ascent = default_font_size * 0.80
        min_descent = default_font_size * 0.22

        if has_fraction:
            min_ascent = max(min_ascent, default_font_size * 1.10)
            min_descent = max(min_descent, default_font_size * 0.50)
        elif has_subscript:
            # Standard MathType metrics for subscripted formulas (like u_1 = 3, u_6 = -96)
            min_ascent = max(min_ascent, default_font_size * 1.0)  # 11.0pt
            min_descent = max(min_descent, default_font_size * 0.455) # 5.0pt

        pad_left = 1.0
        pad_right = 1.0

        # Ensure at least 0.8pt clearance above the highest glyph and below the lowest glyph
        effective_ascent = max(max_ascent + 0.8, min_ascent)
        effective_descent = max(max_descent + 0.8, min_descent)

        new_w_pt = w_pt + pad_left + pad_right
        new_h_pt = effective_ascent + effective_descent
        new_d_pt = effective_descent
        base_y_pt = effective_ascent

        SCALE = 32  # 32 units/pt = 2304 units/inch (matches MathType standard)
        w_u = max(1, int(round(new_w_pt * SCALE)))
        h_u = max(1, int(round(new_h_pt * SCALE)))

        records = [
            _build_wmf_rec(0x0102, struct.pack("<H", 1)),          # SETMAPMODE: MM_TEXT (1)
            _build_wmf_rec(0x0201, struct.pack("<I", 0x00FFFFFF)), # SETBKCOLOR: White
            _build_wmf_rec(0x012e, struct.pack("<H", 25)),         # SETTEXTALIGN: TA_UPDATECP (1) | TA_BASELINE (24) = 25
            _build_wmf_rec(0x020b, struct.pack("<hh", 0, 0)),      # SETWINDOWORG: (0, 0)
            _build_wmf_rec(0x020c, struct.pack("<hh", h_u, w_u)),  # SETWINDOWEXT: (height, width)
            _build_wmf_rec(0x0209, struct.pack("<I", 0x00000000)), # SETTEXTCOLOR: Black
        ]

        # Pen for fraction bars & lines (Handle 0)
        pen_w = max(1, int(round(0.8 * SCALE)))
        pen = struct.pack("<HHHI", 0, pen_w, 0, 0x00000000)
        records.append(_build_wmf_rec(0x02fa, pen))  # Handle 0 = Pen

        # Solid black brush for tall delimiter fills (Handle 3)
        brush = struct.pack("<HIH", 0, 0x00000000, 0)
        records.append(_build_wmf_rec(0x02fc, brush))  # Handle 3 = Brush

        active_font_handle = -1
        cur_font_key = None

        for g in glyphs:
            font_obj, fontsize, c, _idx, ox, oy = g[:6]

            # Render tall delimiter fences (\left, \right brackets, braces, parentheses) and diagonal arrows as vector polygons
            fam = getattr(font_obj, "family_name", "")
            if fam.startswith("STIXSize") or c in (0x2197, 0x2198, 0x2196, 0x2199, 0x2191, 0x2193) or (fam == "cmsy10" and c in (37, 38, 39, 40)):
                try:
                    from matplotlib.path import Path as MplPath
                    font_obj.set_size(fontsize, 72)
                    font_obj.load_char(c)
                    v_path, codes_path = font_obj.get_path()
                    mpl_p = MplPath(v_path, codes_path)
                    polys = mpl_p.to_polygons()
                    records.append(_build_wmf_rec(0x012d, struct.pack("<H", 0)))  # Select Pen 0
                    records.append(_build_wmf_rec(0x012d, struct.pack("<H", 3)))  # Select Brush 3
                    for poly in polys:
                        if len(poly) < 3:
                            continue
                        pts = []
                        for px, py in poly:
                            x_u = int(round((ox + px + pad_left) * SCALE))
                            y_u = int(round((base_y_pt - (oy + py)) * SCALE))
                            pts.append((x_u, y_u))
                        poly_data = struct.pack(f"<{len(pts)*2}h", *[coord for pt in pts for coord in pt])
                        records.append(_build_wmf_rec(0x0324, struct.pack("<H", len(pts)) + poly_data))
                    continue
                except Exception:
                    pass

            # Remap any fence/brace codes to standard { and }
            if c in (0xa9, 0x7b):
                c = 123  # '{'
            elif c in (0xaa, 0x7d):
                c = 125  # '}'

            # Remap TeX Computer Modern cmsy10 char 48 to Unicode prime 0x2032
            if getattr(font_obj, "family_name", "") == "cmsy10" and c == 48:
                c = 0x2032

            is_bb = c in BLACKBOARD_BOLD_TO_LATIN
            is_sym = c in UNICODE_TO_SYMBOL
            is_alpha = chr(c).isalpha() if 32 <= c <= 126 else False
            style_name = getattr(font_obj, "style_name", "").lower()
            is_it = "oblique" in style_name or "italic" in style_name
            is_bold = "bold" in style_name
            f_weight = 700 if is_bold else 400

            if is_bb:
                char_b = bytes([BLACKBOARD_BOLD_TO_LATIN[c]])
                f_name = "Times New Roman"
                f_charset = 0
                f_it = False
                f_weight = 700
            elif is_sym:
                char_b = bytes([UNICODE_TO_SYMBOL[c]])
                f_name = "Symbol"
                f_charset = 2
                f_it = is_it if c == 0x03c0 else False  # \pi follows italic style, operators remain upright
            elif is_alpha:
                char_b = chr(c).encode("ascii")
                f_name = "Times New Roman"
                f_charset = 0
                f_it = is_it  # Natural italic from TeX engine: Upright for functions (cos, sin, tan, cot), Italic for variables
            else:
                try:
                    char_b = chr(c).encode("cp1252")
                except Exception:
                    char_b = chr(c).encode("latin-1", errors="replace")
                f_name = "Times New Roman"
                f_charset = 0
                f_it = is_it

            font_key = (f_name, round(fontsize, 2), f_it, f_charset, f_weight)
            if font_key != cur_font_key:
                f_h = -int(round(fontsize * SCALE))
                lf_data = _create_logfont_record(f_name, f_h, f_it, f_charset, f_weight)
                next_h = 2 if active_font_handle == 1 else 1
                records.append(_build_wmf_rec(0x02fb, lf_data))
                records.append(_build_wmf_rec(0x012d, struct.pack("<H", next_h)))
                if active_font_handle != -1:
                    records.append(_build_wmf_rec(0x01f0, struct.pack("<H", active_font_handle)))
                active_font_handle = next_h
                cur_font_key = font_key

            x_u = int(round((ox + pad_left) * SCALE))
            y_u = int(round((base_y_pt - oy) * SCALE))

            records.append(_build_wmf_rec(0x0214, struct.pack("<hh", y_u, x_u)))
            ext_data = struct.pack("<hhhh", 0, 0, len(char_b), 0) + char_b
            records.append(_build_wmf_rec(0x0a32, ext_data))

        if rects:
            records.append(_build_wmf_rec(0x012d, struct.pack("<H", 0)))
            for rx, ry, rw, rh in rects:
                x1 = int(round((rx + pad_left) * SCALE))
                x2 = int(round((rx + rw + pad_left) * SCALE))
                y_bar = int(round((base_y_pt - ry - rh * 0.5) * SCALE))
                poly_data = struct.pack("<Hhhhh", 2, x1, y_bar, x2, y_bar)
                records.append(_build_wmf_rec(0x0325, poly_data))

        if active_font_handle != -1:
            records.append(_build_wmf_rec(0x01f0, struct.pack("<H", active_font_handle)))
        records.append(_build_wmf_rec(0x01f0, struct.pack("<H", 0)))  # Delete Pen 0
        records.append(_build_wmf_rec(0x01f0, struct.pack("<H", 3)))  # Delete Brush 3

        records.append(_build_wmf_rec(0x0000))  # EOF

        wmf_recs = b"".join(records)
        total_words = 9 + len(wmf_recs) // 2
        max_rec = max(len(r) // 2 for r in records)
        wmf_header = struct.pack("<HHHIHIH", 1, 9, 0x0300, total_words, 8, max_rec, 0)
        wmf_body = wmf_header + wmf_recs

        inch = 2304
        apm_no_cs = struct.pack("<IHhhhhHI", 0x9ac6cdd7, 0, 0, 0, w_u, h_u, inch, 0)
        words = struct.unpack("<10H", apm_no_cs)
        cs = 0
        for w_val in words:
            cs ^= w_val
        apm_header = apm_no_cs + struct.pack("<H", cs)
        return apm_header + wmf_body, new_w_pt, new_h_pt, new_d_pt
    except Exception as e:
        logger.debug(f"Pure vector WMF fallback for '{clean_latex[:30]}': {e}")
        return None


def _bitmap_to_wmf(png_bytes: bytes, w_pt: float, h_pt: float) -> bytes:
    """Wraps a high-DPI raster image into a compliant Windows Metafile (WMF) with APM header.
    Ensures Microsoft Word treats the OLE presentation as image/x-wmf, binding ProgID=Equation.DSMT4.
    """
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes))
    bg = Image.new('RGB', im.size, (255, 255, 255))
    if im.mode in ('RGBA', 'LA'):
        bg.paste(im, mask=im.split()[-1])
    else:
        bg.paste(im)

    bmp_buf = io.BytesIO()
    bg.save(bmp_buf, format='BMP')
    bmp_bytes = bmp_buf.getvalue()
    dib_bytes = bmp_bytes[14:]

    w_px, h_px = bg.size
    SCALE = 20  # 20 twips/pt
    w_u = min(32767, max(1, int(round(w_pt * SCALE))))
    h_u = min(32767, max(1, int(round(h_pt * SCALE))))

    rec_mapmode = struct.pack('<IH', 4, 0x0102) + struct.pack('<H', 1)
    rec_winorg = struct.pack('<IH', 5, 0x020b) + struct.pack('<hh', 0, 0)
    rec_winext = struct.pack('<IH', 5, 0x020c) + struct.pack('<hh', h_u, w_u)

    params = struct.pack(
        '<I8h',
        0x00CC0020,  # SRCCOPY
        h_px, w_px, 0, 0,
        h_u, w_u, 0, 0
    )
    dib_rec_data = params + dib_bytes
    if len(dib_rec_data) % 2 != 0:
        dib_rec_data += b'\x00'
    rec_dib_words = (len(dib_rec_data) + 6) // 2
    rec_dib = struct.pack('<IH', rec_dib_words, 0x0b41) + dib_rec_data
    rec_eof = struct.pack('<IH', 3, 0x0000)

    records = rec_mapmode + rec_winorg + rec_winext + rec_dib + rec_eof
    total_words = 9 + len(records) // 2
    max_rec_words = rec_dib_words

    wmf_header = struct.pack('<HHHIHIH', 1, 9, 0x0300, total_words, 0, max_rec_words, 0)
    wmf_body = wmf_header + records

    inch = 1440
    apm_no_cs = struct.pack('<IH4hHI', 0x9AC6CDD7, 0, 0, 0, w_u, h_u, inch, 0)
    words = struct.unpack('<10H', apm_no_cs)
    cs = 0
    for w in words:
        cs ^= w
    apm_header = apm_no_cs + struct.pack('<H', cs)

    return apm_header + wmf_body


def add_mathtype_equation_to_paragraph(
    paragraph: docx.text.paragraph.Paragraph,
    latex_expr: str,
    default_font_size: Union[int, float] = 11,
    use_mathjax: bool = True,
) -> bool:
    """Inserts a genuine MathType OLE Object (<w:object> with ProgID="Equation.DSMT4",
    v:shape, v:imagedata, and w:position baseline alignment) into the paragraph run.
    Uses pure-Python vector WMF for crisp display and selectable text in PDF, with MathJax MathML
    MTEF encoding so formulas open and edit natively in MathType 7.
    """
    clean = clean_math_expr(latex_expr)
    if not clean:
        return False

    part = paragraph.part
    ole_bytes = None
    img_format = "wmf"
    img_bytes = None
    w_pt, h_pt, depth_pt = 0.0, 0.0, 0.0
    shift_half_pt = 0

    # 1. Generate MTEF and MathType 7.0 OLE Binary using MathJax MathML
    should_use_mathjax = use_mathjax and getattr(settings, "USE_MATHJAX", True)
    if should_use_mathjax:
        try:
            from backend.services.mathjax_service import render_mathjax_equation
            mtef_clean = clean.replace(r"\overrightarrow", r"\vec")
            mj_res = render_mathjax_equation(mtef_clean, font_size_pt=default_font_size, dpi=600, generate_png=True)
            if mj_res and mj_res.get("mml"):
                mml = mj_res["mml"]
                for inv in ["\u2061", "\u2062", "\u2063", "\u2064", "\u200b", "\ufeff", "&#x2061;", "&#x2062;", "&#x2063;", "&#x2064;"]:
                    mml = mml.replace(inv, "")
                try:
                    import docx_equation
                    expr = docx_equation.parse_mathml(mml)
                    mtef = _custom_encode_mtef(expr, default_font_size, raw_latex=clean)
                    ole_bytes = _build_mathtype_cfb_binary(mtef)
                except Exception as e:
                    logger.debug(f"MathJax MathML to MTEF error: {e}")
            if mj_res and mj_res.get("shift_half_pt"):
                shift_half_pt = mj_res["shift_half_pt"]
        except Exception as e:
            logger.debug(f"MathJax renderer fallback: {e}")

    # Fallback OLE binary if not created yet
    if not ole_bytes:
        ole_bytes = generate_mathtype_ole(clean, default_font_size=default_font_size)

    # 2. Generate vector WMF (crisp vector rendering in Word & PDF)
    wmf_res = _render_compliant_mathtype_wmf(clean, default_font_size=default_font_size)
    if wmf_res is not None:
        img_bytes, w_pt, h_pt, depth_pt = wmf_res
        img_format = "wmf"
        shift_half_pt = -max(0, int(round(depth_pt * 2)))
    else:
        # Fallback to high-DPI MathJax image wrapped in WMF (ensures image/x-wmf MIME)
        try:
            from backend.services.mathjax_service import render_mathjax_equation
            mj_res = render_mathjax_equation(clean, font_size_pt=default_font_size, dpi=600, generate_png=True)
            if mj_res and mj_res.get("png_bytes"):
                w_pt = mj_res["w_pt"]
                h_pt = mj_res["h_pt"]
                depth_pt = mj_res["depth_pt"]
                if not shift_half_pt:
                    shift_half_pt = mj_res.get("shift_half_pt", -max(0, int(round(depth_pt * 2))))
                img_bytes = _bitmap_to_wmf(mj_res["png_bytes"], w_pt, h_pt)
                img_format = "wmf"
        except Exception as e:
            logger.debug(f"Fallback bitmap WMF error: {e}")

    if not img_bytes:
        return False

    if not ole_bytes:
        ole_bytes = generate_mathtype_ole(clean, default_font_size=default_font_size)

    try:
        pkg = part.package
        # 3. Add image part to document
        if img_format == "wmf":
            img_idx = sum(1 for p in pkg.parts if '/word/media/image' in p.partname) + 1
            img_uri = PackURI(f'/word/media/image{img_idx}.wmf')
            img_part = Part(img_uri, 'image/x-wmf', img_bytes)
            pkg.parts.append(img_part)
            rId_img = part.relate_to(img_part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
        else:
            rId_img, img_part = part.get_or_add_image(io.BytesIO(img_bytes))

        # 4. Add OLE part to package
        ole_idx = sum(1 for p in pkg.parts if 'oleObject' in p.partname) + 1
        ole_uri = PackURI(f'/word/embeddings/oleObject{ole_idx}.bin')
        ole_part = Part(ole_uri, 'application/vnd.openxmlformats-officedocument.oleObject', ole_bytes)
        pkg.parts.append(ole_part)
        rId_ole = part.relate_to(ole_part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject')

        # Dimensions & baseline shift
        dxa = int(round(w_pt * 20))
        dya = int(round(h_pt * 20))
        if not shift_half_pt:
            shift_half_pt = -max(0, int(round(depth_pt * 2)))

        shape_id = f"_x0000_i{1025 + ole_idx}"
        obj_id = f"_{hashlib.md5(clean.encode()).hexdigest()[:10]}"

        # XML Run with genuine MathType OLE Object & VML shapetype (defined once per document part)
        has_shapetype = getattr(part, "_has_vml_shapetype_t75", False)
        shapetype_xml = ""
        if not has_shapetype:
            part._has_vml_shapetype_t75 = True
            shapetype_xml = (
                f'    <v:shapetype {nsdecls("v")} {nsdecls("o")} id="_x0000_t75" coordsize="21600,21600" o:spt="75" o:preferrelative="t" path="m@4@5l@4@11@9@11@9@5xe" filled="f" stroked="f">\n'
                f'      <v:stroke joinstyle="miter"/>\n'
                f'      <v:formulas>\n'
                f'        <v:f eqn="if lineDrawn pixelLineWidth 0"/>\n'
                f'        <v:f eqn="sum @0 1 0"/>\n'
                f'        <v:f eqn="sum 0 0 @1"/>\n'
                f'        <v:f eqn="prod @2 1 2"/>\n'
                f'        <v:f eqn="prod @3 21600 pixelWidth"/>\n'
                f'        <v:f eqn="prod @3 21600 pixelHeight"/>\n'
                f'        <v:f eqn="sum @0 0 1"/>\n'
                f'        <v:f eqn="prod @6 1 2"/>\n'
                f'        <v:f eqn="prod @7 21600 pixelWidth"/>\n'
                f'        <v:f eqn="sum @8 21600 0"/>\n'
                f'        <v:f eqn="prod @7 21600 pixelHeight"/>\n'
                f'        <v:f eqn="sum @10 21600 0"/>\n'
                f'      </v:formulas>\n'
                f'      <v:path o:extrusionok="f" gradientshapeok="t" o:connecttype="rect"/>\n'
                f'      <o:lock v:ext="edit" aspectratio="t"/>\n'
                f'    </v:shapetype>\n'
            )

        run_xml = (
            f'<w:r {nsdecls("w")}>\n'
            f'  <w:rPr><w:position w:val="{shift_half_pt}"/></w:rPr>\n'
            f'  <w:object w:dxaOrig="{dxa}" w:dyaOrig="{dya}">\n'
            f'{shapetype_xml}'
            f'    <v:shape {nsdecls("v")} {nsdecls("o")} {nsdecls("r")} id="{shape_id}" type="#_x0000_t75" style="width:{w_pt:.2f}pt;height:{h_pt:.2f}pt" o:ole="">\n'
            f'      <v:imagedata r:id="{rId_img}" o:title=""/>\n'
            f'    </v:shape>\n'
            f'    <o:OLEObject {nsdecls("o")} {nsdecls("r")} Type="Embed" ProgID="Equation.DSMT4" ShapeID="{shape_id}" DrawAspect="Content" ObjectID="{obj_id}" r:id="{rId_ole}"/>\n'
            f'  </w:object>\n'
            f'</w:r>\n'
        )
        r_elem = parse_xml(run_xml)
        paragraph._p.append(r_elem)
        return True
    except Exception as e:
        logger.warning(f"Error creating MathType OLE object in docx: {e}")
        return False


def add_math_text_to_paragraph(
    paragraph: docx.text.paragraph.Paragraph,
    text: str,
    bold_prefix: Optional[str] = None,
    italic_prefix: Optional[str] = None,
    default_font_size: Union[int, float] = 11,
    math_format: str = "mathtype",
):
    """Parses text containing inline LaTeX formulas (${...}$, $$...$$, or $...$) and inserts
    runs with genuine MathType OLE equations (math_format="mathtype", default), native Word OMML
    (<m:oMath>) equations (math_format="omml"), or raw LaTeX code enclosed in ${...}$ (math_format="latex").
    """
    if bold_prefix and isinstance(bold_prefix, str):
        r_pre = paragraph.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(default_font_size)

    if italic_prefix and isinstance(italic_prefix, str):
        r_pre = paragraph.add_run(italic_prefix)
        r_pre.font.italic = True
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(default_font_size)

    if not text:
        return

    text = text.strip()
    while (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
        text = text[1:-1].strip()

    # Normalize merged math expressions like ${\left(SAD\right)}, {\left(SBC\right)}$ -> ${\left(SAD\right)}$, ${\left(SBC\right)}$
    text = re.sub(r"(?<!\\)\}\s*,\s*\{", r"}$, ${", text)

    tokens = re.split(r"(\$\$\{.*?\}\$\$|\$\$.*?\$\$|\$\\{.*?\\}\$|\$\{.*?\}\$|\$.*?\$)", text, flags=re.DOTALL)

    for tok in tokens:
        if not tok:
            continue
        stripped = tok.strip()
        is_math = (
            (stripped.startswith("${") and stripped.endswith("}$"))
            or (stripped.startswith("$$") and stripped.endswith("$$"))
            or (stripped.startswith("$") and stripped.endswith("$"))
        )
        if is_math and len(stripped) > 2:
            clean_expr = clean_math_expr(stripped)
            if math_format == "latex":
                r_math = paragraph.add_run(f"${{{clean_expr}}}$")
                r_math.font.name = "Times New Roman"
                r_math.font.size = Pt(default_font_size)
            elif math_format in ("image", "mathtype"):
                ok = add_mathtype_equation_to_paragraph(
                    paragraph, clean_expr, default_font_size=default_font_size, use_mathjax=True
                )
                if not ok:
                    omml_elem = convert_latex_to_omml(clean_expr)
                    if omml_elem is not None:
                        paragraph._p.append(omml_elem)
                    else:
                        r_math = paragraph.add_run(clean_expr)
                        r_math.font.italic = True
                        r_math.font.name = "Times New Roman"
                        r_math.font.size = Pt(default_font_size)
            else:  # "omml" (MathML chuẩn Word / MathType)
                omml_elem = convert_latex_to_omml(clean_expr)
                if omml_elem is not None:
                    paragraph._p.append(omml_elem)
                else:
                    ok = add_mathtype_equation_to_paragraph(
                        paragraph, clean_expr, default_font_size=default_font_size, use_mathjax=True
                    )
                    if not ok:
                        try:
                            omml_fallback = parse_xml(
                                f'<m:oMath {nsdecls("m")}>'
                                f'<m:r><m:rPr><w:rFonts {nsdecls("w")} w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></m:rPr><m:t>{clean_expr}</m:t></m:r>'
                                f'</m:oMath>'
                            )
                            paragraph._p.append(omml_fallback)
                        except Exception:
                            r_math = paragraph.add_run(clean_expr)
                            r_math.font.italic = True
                            r_math.font.name = "Times New Roman"
                            r_math.font.size = Pt(default_font_size)
        else:
            stripped = tok.strip()
            if stripped.startswith("\\") and any(
                cmd in stripped for cmd in ("\\frac", "\\sqrt", "\\vec", "\\overrightarrow", "\\dfrac", "\\alpha", "\\beta")
            ):
                clean_expr = clean_math_expr(stripped)
                if math_format == "latex":
                    r_math = paragraph.add_run(f"${{{clean_expr}}}$")
                    r_math.font.name = "Times New Roman"
                    r_math.font.size = Pt(default_font_size)
                elif math_format in ("image", "mathtype"):
                    ok = add_mathtype_equation_to_paragraph(
                        paragraph, clean_expr, default_font_size=default_font_size, use_mathjax=True
                    )
                    if not ok:
                        omml_elem = convert_latex_to_omml(clean_expr)
                        if omml_elem is not None:
                            paragraph._p.append(omml_elem)
                        else:
                            r_math = paragraph.add_run(clean_expr)
                            r_math.font.italic = True
                            r_math.font.name = "Times New Roman"
                            r_math.font.size = Pt(default_font_size)
                else:
                    omml_elem = convert_latex_to_omml(clean_expr)
                    if omml_elem is not None:
                        paragraph._p.append(omml_elem)
                    else:
                        r_math = paragraph.add_run(clean_expr)
                        r_math.font.italic = True
                        r_math.font.name = "Times New Roman"
                        r_math.font.size = Pt(default_font_size)
            else:
                r_txt = paragraph.add_run(tok)
                r_txt.font.name = "Times New Roman"
                r_txt.font.size = Pt(default_font_size)


# ---------------------------------------------------------------------------
# 2. Official Ministry Examination Header & Layout
# ---------------------------------------------------------------------------

def _configure_document_styles(doc: docx.Document):
    """Configures Times New Roman 11pt, line spacing 1.15, suppression of spelling squiggles, and vi-VN language."""
    try:
        settings_elem = doc.settings.element
        settings_elem.append(parse_xml(f'<w:hideSpellingErrors {nsdecls("w")}/>'))
        settings_elem.append(parse_xml(f'<w:hideGrammaticalErrors {nsdecls("w")}/>'))
    except Exception:
        pass

    try:
        norm_style = doc.styles['Normal']
        norm_style.font.name = 'Times New Roman'
        norm_style.font.size = Pt(11)
        norm_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        norm_style.paragraph_format.line_spacing = 1.15
        rPr = norm_style.element.get_or_add_rPr()
        rPr.append(parse_xml(f'<w:noProof {nsdecls("w")}/>'))
        rPr.append(parse_xml(f'<w:lang {nsdecls("w")} w:val="vi-VN"/>'))
    except Exception:
        pass


def _set_cell_border(cell, **kwargs):
    """Sets thin borders on a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="{kwargs.get("top", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="{kwargs.get("left", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="{kwargs.get("bottom", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="{kwargs.get("right", "single")}" w:sz="{kwargs.get("sz", "4")}" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)


def _remove_table_borders(table):
    """Removes all borders from a table."""
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/><w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)


def _setup_exam_header(
    doc: docx.Document,
    school_name: str,
    exam_title: str,
    subject_name: str,
    grade: str,
    variant_code: str,
    duration: int = 90,
    compact_student_info: bool = False,
):
    """Generates the official Ministry of Education standard examination header:
    - Left column: School/Department name, Official Exam designation, Page count notice.
    - Right column: Exam Title, Subject, Grade, Duration.
    - Prominent Variant Code Box.
    - Student info box (Họ tên, SBD, Lớp/Phòng thi).
    - Phách box (Số phách, Điểm số).
    """
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    _remove_table_borders(header_table)
    header_table.columns[0].width = Cm(8.0)
    header_table.columns[1].width = Cm(10.0)

    # Left cell: Authority & School
    left_cell = header_table.cell(0, 0)
    p_left = left_cell.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_auth = p_left.add_run(f"{school_name.upper()}\n")
    r_auth.font.bold = True
    r_auth.font.size = Pt(10.5)
    r_auth.font.name = "Times New Roman"

    r_official = p_left.add_run("ĐỀ THI CHÍNH THỨC\n")
    r_official.font.bold = True
    r_official.font.size = Pt(11)
    r_official.font.name = "Times New Roman"

    r_pages = p_left.add_run("(Đề thi có 04 trang)")
    r_pages.font.italic = True
    r_pages.font.size = Pt(9.5)
    r_pages.font.name = "Times New Roman"

    # Right cell: Exam Title & Subject Info
    right_cell = header_table.cell(0, 1)
    p_right = right_cell.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER

    r_exam = p_right.add_run(f"{exam_title.upper()}\n")
    r_exam.font.bold = True
    r_exam.font.size = Pt(10.5)
    r_exam.font.name = "Times New Roman"

    grade_str = f" - KHỐI {grade}" if grade else ""
    r_subj = p_right.add_run(f"Bài thi: {subject_name.upper()}{grade_str}\n")
    r_subj.font.bold = True
    r_subj.font.size = Pt(11)
    r_subj.font.name = "Times New Roman"

    r_dur = p_right.add_run(f"Thời gian làm bài: {duration} phút, không kể thời gian phát đề")
    r_dur.font.italic = True
    r_dur.font.size = Pt(9.5)
    r_dur.font.name = "Times New Roman"

    if compact_student_info:
        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_before = Pt(6)
        p_info.paragraph_format.space_after = Pt(4)
        r_info = p_info.add_run(f"Họ và tên thí sinh: .................................................................... Số báo danh: ................ Mã đề thi: {variant_code}")
        r_info.font.name = "Times New Roman"
        r_info.font.size = Pt(10)

        p_div = doc.add_paragraph()
        p_div.paragraph_format.space_before = Pt(2)
        p_div.paragraph_format.space_after = Pt(8)
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_line = p_div.add_run("────────────────────────────────────────────────────────────────────────")
        r_line.font.size = Pt(8)
        r_line.font.color.rgb = RGBColor(160, 160, 160)
        return

    # Variant Code Box
    p_var_wrap = doc.add_paragraph()
    p_var_wrap.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_var_wrap.paragraph_format.space_before = Pt(4)
    p_var_wrap.paragraph_format.space_after = Pt(4)
    r_var_box = p_var_wrap.add_run(f"  MÃ ĐỀ THI: {variant_code}  ")
    r_var_box.font.bold = True
    r_var_box.font.size = Pt(11)
    r_var_box.font.name = "Times New Roman"

    # Student Information & Phách Box Table
    info_table = doc.add_table(rows=2, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False
    info_table.columns[0].width = Cm(12.5)
    info_table.columns[1].width = Cm(5.5)

    c1_1 = info_table.cell(0, 0)
    p_name = c1_1.paragraphs[0]
    p_name.paragraph_format.space_after = Pt(2)
    r_n = p_name.add_run("Họ và tên thí sinh: ................................................................................")
    r_n.font.size = Pt(10)
    r_n.font.name = "Times New Roman"

    c1_2 = info_table.cell(0, 1)
    p_sbd = c1_2.paragraphs[0]
    p_sbd.paragraph_format.space_after = Pt(2)
    r_sbd = p_sbd.add_run("Số báo danh: ...........................")
    r_sbd.font.size = Pt(10)
    r_sbd.font.name = "Times New Roman"

    c2_1 = info_table.cell(1, 0)
    p_room = c2_1.paragraphs[0]
    p_room.paragraph_format.space_after = Pt(2)
    r_rm = p_room.add_run("Phòng thi: .................... Lớp: ....................")
    r_rm.font.size = Pt(10)
    r_rm.font.name = "Times New Roman"

    c2_2 = info_table.cell(1, 1)
    p_phach = c2_2.paragraphs[0]
    p_phach.paragraph_format.space_after = Pt(2)
    r_ph = p_phach.add_run("Số phách: .................. Điểm: ......")
    r_ph.font.size = Pt(10)
    r_ph.font.name = "Times New Roman"

    _set_cell_border(c1_1, top="single", left="single", bottom="none", right="single")
    _set_cell_border(c1_2, top="single", left="single", bottom="none", right="single")
    _set_cell_border(c2_1, top="none", left="single", bottom="single", right="single")
    _set_cell_border(c2_2, top="none", left="single", bottom="single", right="single")

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(8)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_div.add_run("─────────────────────────────────────────────────────────────")
    r_line.font.size = Pt(8)
    r_line.font.color.rgb = RGBColor(128, 128, 128)


def _set_section_2_columns(section):
    """Enforces 2-column layout on a Word section via OpenXML."""
    sectPr = section._sectPr
    cols = sectPr.xpath("./w:cols")
    if cols:
        cols[0].set(qn("w:num"), "2")
        cols[0].set(qn("w:space"), "720")
    else:
        cols_elem = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="720"/>')
        sectPr.append(cols_elem)


def _set_section_1_column(section):
    """Resets section layout to 1 column."""
    sectPr = section._sectPr
    cols = sectPr.xpath("./w:cols")
    if cols:
        cols[0].set(qn("w:num"), "1")
    else:
        cols_elem = parse_xml(f'<w:cols {nsdecls("w")} w:num="1"/>')
        sectPr.append(cols_elem)


def generate_variant_docx(*args, **kwargs):
    raise NotImplementedError("Tính năng xuất Word (.docx) và MathType đã bị loại bỏ. Vui lòng sử dụng xuất bản PDF vector.")

def _legacy_generate_variant_docx(variant: ExamVariant, output_path: Path, math_format: str = "omml"):
    """Generates an official Ministry format .docx exam paper for a specific variant:
    - Official header (School name, Exam title, Subject, Grade, Variant code box, Student info, Phách).
    - 2-column layout for question content.
    - Native OMML (<m:oMath>) or MathType OLE equations.
    """
    doc = docx.Document()
    _configure_document_styles(doc)

    # 1. Page Format: Standard A4 Portrait (210 x 297 mm, 1.5 cm margins)
    s1 = doc.sections[0]
    s1.orientation = WD_ORIENT.PORTRAIT
    s1.page_width = Mm(210)
    s1.page_height = Mm(297)
    s1.top_margin = Cm(1.5)
    s1.bottom_margin = Cm(1.5)
    s1.left_margin = Cm(1.5)
    s1.right_margin = Cm(1.5)

    master = variant.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"
    grade = str(master.grade_id) if master else "12"
    exam_title = master.title if master else "Kỳ thi Tốt nghiệp THPT Năm 2025"
    school_name = "SỞ GIÁO DỤC VÀ ĐÀO TẠO"

    # Header in Section 1 (1 column)
    _setup_exam_header(
        doc=doc,
        school_name=school_name,
        exam_title=exam_title,
        subject_name=subject_name,
        grade=grade,
        variant_code=variant.variant_code,
        duration=90,
    )

    # 2. Section 2: Questions in 2-Column Layout (Continuous section break)
    s2 = doc.add_section(WD_SECTION.CONTINUOUS)
    _set_section_2_columns(s2)

    # Sort variant items by variant_order_index
    items = sorted(variant.items, key=lambda x: x.variant_order_index)

    current_section = None
    section_titles = {
        1: "PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.",
        2: "PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.",
        3: "PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu 6.",
        4: "PHẦN IV. Tự luận.",
    }

    last_passage_id = None

    for item in items:
        q: Question = item.question
        if not q:
            continue

        # Determine section
        sec = 1
        if q.item_format == "SINGLE_CHOICE":
            sec = 1
        elif q.item_format == "TRUE_FALSE_GROUP":
            sec = 2
        elif q.item_format == "SHORT_ANSWER":
            sec = 3
        else:
            sec = 4

        # Section Header Banner
        if sec != current_section:
            current_section = sec
            sec_heading = doc.add_paragraph()
            sec_heading.paragraph_format.space_before = Pt(10)
            sec_heading.paragraph_format.space_after = Pt(4)
            r_sec = sec_heading.add_run(section_titles.get(sec, f"PHẦN {sec}"))
            r_sec.font.bold = True
            r_sec.font.size = Pt(10.5)
            r_sec.font.name = "Times New Roman"

        # Passage Rendering (RULE-03: Passage context immediately precedes child questions)
        pid = getattr(q, "passage_id", None)
        p_content = getattr(q, "passage_content", None)
        if pid and pid != last_passage_id and p_content:
            last_passage_id = pid
            p_pass_intro = doc.add_paragraph()
            p_pass_intro.paragraph_format.space_before = Pt(6)
            p_pass_intro.paragraph_format.space_after = Pt(2)
            r_intro = p_pass_intro.add_run("Đọc đoạn thông tin sau và trả lời các câu hỏi:")
            r_intro.font.bold = True
            r_intro.font.italic = True
            r_intro.font.size = Pt(10)
            r_intro.font.name = "Times New Roman"

            p_pass = doc.add_paragraph()
            p_pass.paragraph_format.left_indent = Inches(0.15)
            p_pass.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_pass, p_content, default_font_size=10, math_format=math_format)

        # Question Stem with Native OMML Equations
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(4)
        p_q.paragraph_format.space_after = Pt(2)
        add_math_text_to_paragraph(p_q, q.stem, bold_prefix=f"Câu {item.variant_order_index}: ", default_font_size=10.5, math_format=math_format)

        # Render options or sub-statements
        if q.item_format == "SINGLE_CHOICE" and q.options:
            mapping = {}
            if item.option_mapping:
                try:
                    mapping = json.loads(item.option_mapping)
                except Exception:
                    pass

            inv_map = {v: k for k, v in mapping.items()} if mapping else {}
            labels = ["A", "B", "C", "D"]

            for lbl in labels:
                orig_label = inv_map.get(lbl, lbl)
                orig_opt = next((o for o in q.options if o.label == orig_label), None)
                p_opt = doc.add_paragraph()
                p_opt.paragraph_format.left_indent = Inches(0.2)
                p_opt.paragraph_format.space_after = Pt(1.5)
                content = orig_opt.content if orig_opt else ""
                add_math_text_to_paragraph(p_opt, content, bold_prefix=f"{lbl}. ", default_font_size=10.5, math_format=math_format)

        elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
            for sub in q.sub_statements:
                p_sub = doc.add_paragraph()
                p_sub.paragraph_format.left_indent = Inches(0.2)
                p_sub.paragraph_format.space_after = Pt(1.5)
                add_math_text_to_paragraph(p_sub, sub.content, bold_prefix=f"{sub.label}) ", default_font_size=10, math_format=math_format)

        elif q.item_format == "SHORT_ANSWER":
            p_ans = doc.add_paragraph()
            p_ans.paragraph_format.left_indent = Inches(0.2)
            p_ans.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_ans, "................................................................", italic_prefix="Đáp số: ", default_font_size=10, math_format=math_format)

    # 3. Section 3: Return to 1 Column for Footer / End Note
    s3 = doc.add_section(WD_SECTION.CONTINUOUS)
    _set_section_1_column(s3)

    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(14)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("─────────────────── HẾT ───────────────────")
    r_end.font.bold = True
    r_end.font.size = Pt(11)
    r_end.font.name = "Times New Roman"

    p_super = doc.add_paragraph()
    p_super.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_super.paragraph_format.space_after = Pt(6)
    r_sup = p_super.add_run("Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.")
    r_sup.font.italic = True
    r_sup.font.size = Pt(10)
    r_sup.font.name = "Times New Roman"

    doc.save(output_path)


def generate_solution_docx(*args, **kwargs):
    raise NotImplementedError("Tính năng xuất Word (.docx) và MathType đã bị loại bỏ. Vui lòng sử dụng xuất bản PDF vector.")

def _legacy_generate_solution_docx(variant: ExamVariant, output_path: Path, math_format: str = "omml"):
    """Generates a detailed solution document for a variant with OMML equations."""
    doc = docx.Document()
    _configure_document_styles(doc)
    s = doc.sections[0]
    s.orientation = WD_ORIENT.PORTRAIT
    s.page_width = Mm(210)
    s.page_height = Mm(297)
    s.top_margin = Cm(1.5)
    s.bottom_margin = Cm(1.5)
    s.left_margin = Cm(1.5)
    s.right_margin = Cm(1.5)

    master = variant.master_exam
    subject_name = master.subject.name if master and master.subject else "Toán học"

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(f"HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ {variant.variant_code}\nBÀI THI: {subject_name.upper()}\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.name = "Times New Roman"

    p_banner = doc.add_paragraph()
    p_banner.paragraph_format.space_after = Pt(10)
    r_b = p_banner.add_run("Áp dụng thang điểm Quyết định 764/QĐ-BGDĐT: Đúng 1 ý: 0.1đ | Đúng 2 ý: 0.25đ | Đúng 3 ý: 0.5đ | Đúng 4 ý: 1.0đ")
    r_b.font.italic = True
    r_b.font.size = Pt(10)
    r_b.font.color.rgb = RGBColor(100, 100, 100)

    items = sorted(variant.items, key=lambda x: x.variant_order_index)
    for item in items:
        q: Question = item.question
        if not q:
            continue

        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        add_math_text_to_paragraph(p_q, q.stem, bold_prefix=f"Câu {item.variant_order_index}: ", math_format=math_format)

        # Show Answer Key
        p_k = doc.add_paragraph()
        p_k.paragraph_format.space_after = Pt(2)
        r_k = p_k.add_run(f"Đáp án: {item.answer_key or 'Đang cập nhật'}")
        r_k.font.bold = True
        r_k.font.color.rgb = RGBColor(0, 102, 204)

        # Show Explanation
        if q.explanation:
            p_exp = doc.add_paragraph()
            p_exp.paragraph_format.left_indent = Inches(0.2)
            p_exp.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_exp, q.explanation, italic_prefix="Lời giải chi tiết: ", math_format=math_format)

    doc.save(output_path)


def generate_answer_sheet_docx(*args, **kwargs):
    raise NotImplementedError("Tính năng xuất Word (.docx) và MathType đã bị loại bỏ. Vui lòng sử dụng xuất bản PDF vector.")

def _legacy_generate_answer_sheet_docx(master: MasterExam, variants: List[ExamVariant], output_path: Path):
    """Generates an Answer Key Matrix overview Word document."""
    doc = docx.Document()
    s = doc.sections[0]
    s.orientation = WD_ORIENT.PORTRAIT
    s.page_width = Mm(210)
    s.page_height = Mm(297)
    s.top_margin = Cm(1.5)
    s.bottom_margin = Cm(1.5)
    s.left_margin = Cm(1.5)
    s.right_margin = Cm(1.5)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run(f"BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ\n{master.title.upper()}\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r.font.name = "Times New Roman"

    num_q = master.total_questions
    col_count = 1 + len(variants)

    table = doc.add_table(rows=num_q + 1, cols=col_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    # Headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].paragraphs[0].add_run("Câu").font.bold = True
    for idx, v in enumerate(variants):
        hdr_cells[idx + 1].paragraphs[0].add_run(f"Mã {v.variant_code}").font.bold = True

    # Fill rows
    for q_idx in range(1, num_q + 1):
        row_cells = table.rows[q_idx].cells
        row_cells[0].paragraphs[0].add_run(str(q_idx))
        for v_idx, v in enumerate(variants):
            v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
            val = v_item.answer_key if v_item and v_item.answer_key else "-"
            row_cells[v_idx + 1].paragraphs[0].add_run(val)

    # Add RULE-01 Grading matrix explanation table
    p_rule = doc.add_paragraph()
    p_rule.paragraph_format.space_before = Pt(14)
    r_r = p_rule.add_run("QUY TẮC CHẤM ĐIỂM TRẮC NGHIỆM ĐÚNG/SAI (RULE-01 - Quyết định 764/QĐ-BGDĐT)")
    r_r.font.bold = True

    scale_table = doc.add_table(rows=5, cols=3)
    scale_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scale_hdr = scale_table.rows[0].cells
    scale_hdr[0].paragraphs[0].add_run("Số ý đúng trong 1 câu").font.bold = True
    scale_hdr[1].paragraphs[0].add_run("Tỷ lệ điểm").font.bold = True
    scale_hdr[2].paragraphs[0].add_run("Điểm nhận được (Thang 1.0)").font.bold = True

    scale_rows = [
        ("Đúng 1 ý", "10%", "0.10 điểm"),
        ("Đúng 2 ý", "25%", "0.25 điểm"),
        ("Đúng 3 ý", "50%", "0.50 điểm"),
        ("Đúng cả 4 ý", "100%", "1.00 điểm"),
    ]
    for r_i, (k, p, d) in enumerate(scale_rows, start=1):
        c = scale_table.rows[r_i].cells
        c[0].paragraphs[0].add_run(k)
        c[1].paragraphs[0].add_run(p)
        c[2].paragraphs[0].add_run(d)

    doc.save(output_path)


# ---------------------------------------------------------------------------
# PDF Conversion & Multi-format Export (3-Tier Resilient Engine)
# ---------------------------------------------------------------------------

logger = logging.getLogger("quesy.docx_exporter")

EDGE_BROWSER_PATHS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]


def find_browser_executable() -> Optional[Path]:
    """Finds available Edge or Chrome or Chromium executable cross-platform (Windows, Linux, macOS)."""
    # 1. System PATH lookup (Linux, macOS, standard Windows PATH)
    for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge", "edge"]:
        found = shutil.which(name)
        if found:
            return Path(found)

    # 2. Linux standard locations
    linux_paths = [
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/snap/bin/chromium"),
    ]
    for p in linux_paths:
        if p.exists():
            return p

    # 3. Windows standard locations
    windows_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in windows_paths:
        if p.exists():
            return p

    # 4. macOS standard locations
    mac_paths = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]
    for p in mac_paths:
        if p.exists():
            return p

    return None


def convert_html_to_pdf_browser(html_path: Path, pdf_path: Path) -> bool:
    """Renders HTML directly into high-fidelity vector PDF via headless Edge or Chrome."""
    browser_exe = find_browser_executable()
    if not browser_exe:
        return False
    try:
        cmd = [
            str(browser_exe),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-pdf-header-footer",
            f"--print-to-pdf={str(pdf_path.resolve())}",
            html_path.resolve().as_uri()
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=12)
        return pdf_path.exists() and pdf_path.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"Browser HTML-to-PDF conversion failed: {e}")
        return False


def generate_variant_html(v: ExamVariant, output_html: Path) -> Path:
    """Generates an official Vietnamese Examination 2-column HTML layout."""
    master = v.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"
    exam_title = master.title if master else "KỲ THI TỐT NGHIỆP THPT NĂM 2025"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Mã đề {v.variant_code}</title>
  <style>
    @page {{ size: A4; margin: 15mm 15mm 15mm 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.45; color: #111; margin: 0; padding: 0; }}
    .header-table {{ width: 100%; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px; border-collapse: collapse; }}
    .header-table td {{ vertical-align: top; }}
    .school {{ text-align: center; font-weight: bold; font-size: 11pt; width: 45%; }}
    .exam-info {{ text-align: center; font-size: 11pt; width: 55%; }}
    .exam-title {{ font-weight: bold; font-size: 12pt; text-transform: uppercase; }}
    .variant-box {{ display: inline-block; border: 2px solid #000; padding: 3px 12px; font-weight: bold; font-size: 13pt; margin-top: 5px; }}
    .student-box {{ width: 100%; border: 1px solid #444; margin-bottom: 15px; padding: 6px 12px; font-size: 10pt; background: #fafafa; }}
    .columns {{ column-count: 2; column-gap: 24px; column-rule: 0.5px solid #bbb; text-align: justify; }}
    .section-title {{ font-weight: bold; font-size: 11pt; margin-top: 10px; margin-bottom: 6px; text-transform: uppercase; color: #002244; break-after: avoid; }}
    .question {{ margin-bottom: 14px; break-inside: avoid; }}
    .q-stem {{ font-weight: 500; margin-bottom: 4px; }}
    .options-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; margin-left: 10px; margin-top: 4px; }}
    .tf-sub {{ margin-left: 10px; margin-top: 3px; }}
    .footer-note {{ text-align: center; font-style: italic; margin-top: 25px; border-top: 1px dashed #888; padding-top: 8px; font-size: 10pt; }}
  </style>
</head>
<body>
  <table class="header-table">
    <tr>
      <td class="school">
        SỞ GIÁO DỤC VÀ ĐÀO TẠO<br>
        <b>TRƯỜNG THPT CHUYÊN</b><br>
        <i>(Đề thi gồm có 02 trang)</i>
      </td>
      <td class="exam-info">
        <div class="exam-title">{exam_title}</div>
        <div><b>BÀI THI: {subject_name.upper()}</b></div>
        <div><i>Thời gian làm bài: 90 phút (không kể thời gian phát đề)</i></div>
        <div class="variant-box">MÃ ĐỀ: {v.variant_code}</div>
      </td>
    </tr>
  </table>

  <div class="student-box">
    Họ và tên thí sinh: ............................................................................ Số báo danh: ..................... Phách: .....................
  </div>

  <div class="columns">
"""

    items = sorted(v.items, key=lambda x: x.variant_order_index)
    curr_sec = None
    for it in items:
        q = it.question
        if not q:
            continue
        if q.item_format == "SINGLE_CHOICE" and curr_sec != 1:
            html += '<div class="section-title">PHẦN I. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.</div>'
            curr_sec = 1
        elif q.item_format == "TRUE_FALSE_GROUP" and curr_sec != 2:
            html += '<div class="section-title">PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 4.</div>'
            curr_sec = 2
        elif q.item_format == "SHORT_ANSWER" and curr_sec != 3:
            html += '<div class="section-title">PHẦN III. Câu trắc nghiệm trả lời ngắn.</div>'
            curr_sec = 3

        clean_stem = q.stem.replace("<", "&lt;").replace(">", "&gt;")
        html += f'<div class="question"><div class="q-stem"><b>Câu {it.variant_order_index}:</b> {clean_stem}</div>'

        if q.item_format == "SINGLE_CHOICE":
            html += '<div class="options-grid">'
            mapping = json.loads(it.option_mapping) if (it.option_mapping and isinstance(it.option_mapping, str)) else (it.option_mapping or {})
            if mapping:
                for lbl in ["A", "B", "C", "D"]:
                    if lbl in mapping:
                        orig = mapping[lbl]
                        orig_opt = next((o for o in q.options if o.label == orig), None)
                        txt = orig_opt.content if orig_opt else mapping[lbl]
                        clean_opt = txt.replace("<", "&lt;").replace(">", "&gt;")
                        html += f'<div><b>{lbl}.</b> {clean_opt}</div>'
            elif q.options:
                for o in q.options:
                    clean_opt = o.content.replace("<", "&lt;").replace(">", "&gt;")
                    html += f'<div><b>{o.label}.</b> {clean_opt}</div>'
            html += '</div>'
        elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
            for sub in q.sub_statements:
                clean_sub = sub.content.replace("<", "&lt;").replace(">", "&gt;")
                html += f'<div class="tf-sub"><b>{sub.label})</b> {clean_sub}</div>'
        elif q.item_format == "SHORT_ANSWER":
            html += '<div style="margin-left: 10px; font-style: italic; color: #555;">Đáp số: ....................................................</div>'

        html += '</div>'

    html += """
  </div>
  <div class="footer-note">--- HẾT ---<br>Cán bộ coi thi không giải thích gì thêm.</div>
</body>
</html>"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def generate_solution_html(v: ExamVariant, output_html: Path) -> Path:
    """Generates clean HTML for detailed solutions."""
    master = v.master_exam
    subject_name = master.subject.name if (master and master.subject) else "Toán học"

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Lời giải Mã đề {v.variant_code}</title>
  <style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; color: #111; }}
    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px; }}
    .title {{ font-size: 14pt; font-weight: bold; }}
    .subtitle {{ font-size: 11pt; font-style: italic; color: #444; }}
    .solution-item {{ margin-bottom: 15px; border-bottom: 1px dotted #ccc; padding-bottom: 10px; }}
    .q-title {{ font-weight: bold; color: #003366; }}
    .ans-key {{ font-weight: bold; color: #0066cc; margin: 4px 0; }}
    .explanation {{ margin-left: 12px; background: #f8fafc; padding: 6px 12px; border-left: 3px solid #3b82f6; }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title">HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ {v.variant_code}</div>
    <div class="subtitle">BÀI THI: {subject_name.upper()} • CHUẨN THÔNG TƯ 32/2018/TT-BGDĐT</div>
  </div>
"""

    items = sorted(v.items, key=lambda x: x.variant_order_index)
    for it in items:
        q = it.question
        if not q:
            continue
        clean_stem = q.stem.replace("<", "&lt;").replace(">", "&gt;")
        clean_exp = (q.explanation or "Đang cập nhật hướng dẫn giải.").replace("<", "&lt;").replace(">", "&gt;")
        html += f"""
  <div class="solution-item">
    <div class="q-title">Câu {it.variant_order_index}: {clean_stem}</div>
    <div class="ans-key">Đáp án chuẩn: {it.answer_key or 'A'}</div>
    <div class="explanation"><b>Lời giải chi tiết:</b><br>{clean_exp}</div>
  </div>
"""

    html += "</body></html>"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def generate_answer_sheet_html(master: MasterExam, variants: List[ExamVariant], output_html: Path) -> Path:
    """Generates clean HTML for answer key matrix."""
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <title>Bảng Đáp Án Tổng Hợp</title>
  <style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; color: #111; }}
    .header {{ text-align: center; font-weight: bold; font-size: 13pt; margin-bottom: 12px; }}
    table {{ width: 100%; border-collapse: collapse; text-align: center; }}
    th, td {{ border: 1px solid #444; padding: 6px; }}
    th {{ background: #f1f5f9; }}
  </style>
</head>
<body>
  <div class="header">BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ THI</div>
  <table>
    <tr>
      <th>Câu</th>
      <th>Thể thức</th>
      {"".join([f"<th>Mã {v.variant_code}</th>" for v in variants])}
    </tr>
"""
    num_questions = master.total_questions
    for q_idx in range(1, num_questions + 1):
        m_item = next((it for it in master.items if it.order_index == q_idx), None)
        fmt = m_item.question.item_format if (m_item and m_item.question) else "SINGLE_CHOICE"
        html += f"<tr><td>{q_idx}</td><td>{fmt}</td>"
        for v in variants:
            v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
            ans = v_item.answer_key if v_item and v_item.answer_key else "-"
            html += f"<td><b>{ans}</b></td>"
        html += "</tr>"

    html += "</table></body></html>"
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html


def register_vietnamese_fonts():
    """Registers true Times New Roman fonts for ReportLab Unicode rendering."""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        fonts_to_register = [
            ('TimesNewRoman', r'C:\Windows\Fonts\times.ttf'),
            ('TimesNewRoman-Bold', r'C:\Windows\Fonts\timesbd.ttf'),
            ('TimesNewRoman-Italic', r'C:\Windows\Fonts\timesi.ttf'),
        ]
        for name, p in fonts_to_register:
            if Path(p).exists() and name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(name, p))
    except Exception as e:
        logger.warning(f"Could not register system TTF fonts: {e}")


def generate_pdf_reportlab(variant: ExamVariant, output_pdf: Path) -> bool:
    """Ultra-fast pure Python PDF generator using ReportLab with Times New Roman Unicode."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        
        style_norm = ParagraphStyle('Norm', fontName=font_main, fontSize=11, leading=14)
        style_bold = ParagraphStyle('Bold', fontName=font_bold, fontSize=11, leading=14)
        style_center = ParagraphStyle('Center', fontName=font_bold, fontSize=12, leading=15, alignment=1)
        style_sec = ParagraphStyle('Sec', fontName=font_bold, fontSize=11, leading=15, textColor=colors.HexColor('#002244'))

        story = []
        master = variant.master_exam
        title = master.title if master else "KỲ THI TỐT NGHIỆP THPT"
        sub_name = master.subject.name if (master and master.subject) else "Toán học"

        header_data = [
            [
                Paragraph("<b>SỞ GIÁO DỤC VÀ ĐÀO TẠO</b><br/>TRƯỜNG THPT CHUYÊN", style_norm),
                Paragraph(f"<b>{title.upper()}</b><br/><b>MÔN: {sub_name.upper()} - MÃ ĐỀ: {variant.variant_code}</b>", style_center)
            ]
        ]
        t = Table(header_data, colWidths=[240, 280])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

        curr_sec = None
        items = sorted(variant.items, key=lambda x: x.variant_order_index)
        for it in items:
            q = it.question
            if not q: continue
            
            if q.item_format == "SINGLE_CHOICE" and curr_sec != 1:
                story.append(Paragraph("<b>PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 1
            elif q.item_format == "TRUE_FALSE_GROUP" and curr_sec != 2:
                story.append(Paragraph("<b>PHẦN II. Câu trắc nghiệm đúng sai.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 2
            elif q.item_format == "SHORT_ANSWER" and curr_sec != 3:
                story.append(Paragraph("<b>PHẦN III. Câu trắc nghiệm trả lời ngắn.</b>", style_sec))
                story.append(Spacer(1, 4))
                curr_sec = 3

            clean_stem = q.stem.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Câu {it.variant_order_index}:</b> {clean_stem}", style_norm))
            story.append(Spacer(1, 4))
            
            if q.item_format == "SINGLE_CHOICE":
                mapping = json.loads(it.option_mapping) if (it.option_mapping and isinstance(it.option_mapping, str)) else (it.option_mapping or {})
                opts_rendered = []
                if mapping:
                    for lbl in ["A", "B", "C", "D"]:
                        if lbl in mapping:
                            orig = mapping[lbl]
                            orig_opt = next((o for o in q.options if o.label == orig), None)
                            txt = orig_opt.content if orig_opt else mapping[lbl]
                            clean_opt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            opts_rendered.append(Paragraph(f"<b>{lbl}.</b> {clean_opt}", style_norm))
                elif q.options:
                    for o in q.options:
                        clean_opt = o.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        opts_rendered.append(Paragraph(f"<b>{o.label}.</b> {clean_opt}", style_norm))
                if opts_rendered:
                    col_w = 520 / len(opts_rendered)
                    t_opts = Table([opts_rendered], colWidths=[col_w]*len(opts_rendered))
                    story.append(t_opts)
                    story.append(Spacer(1, 6))
            elif q.item_format == "TRUE_FALSE_GROUP" and q.sub_statements:
                for sub in q.sub_statements:
                    clean_sub = sub.content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>{sub.label})</b> {clean_sub}", style_norm))
                story.append(Spacer(1, 6))
            elif q.item_format == "SHORT_ANSWER":
                story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<i>Đáp số: ....................................................</i>", style_norm))
                story.append(Spacer(1, 6))

        doc.build(story)
        return output_pdf.exists() and output_pdf.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"ReportLab generation failed: {e}")
        return False


def generate_variant_latex(variant: ExamVariant, is_solution: bool = False) -> str:
    items = sorted(variant.items, key=lambda x: x.variant_order_index)
    
    sec1 = [it for it in items if (it.question and it.question.item_format == "SINGLE_CHOICE")]
    sec2 = [it for it in items if (it.question and it.question.item_format == "TRUE_FALSE_GROUP")]
    sec3 = [it for it in items if (it.question and it.question.item_format == "SHORT_ANSWER")]
    
    if not sec1 and not sec2 and not sec3:
        sec1 = items

    n1 = len(sec1)
    n2 = len(sec2)
    n3 = len(sec3)

    latex_lines = [
        r"\begin{center}",
        r"\begin{minipage}{0.38\textwidth}",
        r"\centering \textbf{TRƯỜNG THPT CHUYÊN}\\ \textbf{ĐỀ THI KHẢO SÁT CHẤT LƯỢNG}",
        r"\end{minipage}",
        r"\hfill",
        r"\begin{minipage}{0.58\textwidth}",
        r"\centering \textbf{KỲ THI TỐT NGHIỆP TRUNG HỌC PHỔ THÔNG}\\ \textbf{NĂM HỌC 2025 - MÔN: TOÁN HỌC}",
        r"\end{minipage}",
        r"\end{center}",
        r"\vspace{0.3em}",
        r"\begin{center}",
        r"\textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}",
        r"\end{center}",
        r"\vspace{0.3em}",
        r"\noindent Họ và tên thí sinh: \dotfill Số báo danh: \dotfill \framebox{\textbf{Mã đề: " + variant.variant_code + r"}}",
        r"\vspace{0.4em}",
        r"\rule{\textwidth}{0.5pt}",
        r"\vspace{0.5em}"
    ]

    if n1 > 0:
        latex_lines.append(rf"\noindent\textbf{{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n1}. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec1:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            
            mapping = it.option_mapping or {"A": "A", "B": "B", "C": "C", "D": "D"}
            opts = q.options or []
            choice_parts = []
            for lbl in ["A", "B", "C", "D"]:
                orig_lbl = mapping.get(lbl, lbl)
                opt_obj = next((o for o in opts if o.label == orig_lbl or o.label == lbl), None)
                content = opt_obj.content if opt_obj else f"Phương án {lbl}"
                is_corr = opt_obj.is_correct if opt_obj else False
                prefix = r"\True " if is_corr else ""
                choice_parts.append(f"{prefix}{content}")
            
            if len(choice_parts) >= 4:
                latex_lines.append(rf"\choice{{{choice_parts[0]}}}{{{choice_parts[1]}}}{{{choice_parts[2]}}}{{{choice_parts[3]}}}")
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                latex_lines.append(q.explanation or "Hướng dẫn giải chi tiết đang cập nhật.")
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    if n2 > 0:
        latex_lines.append(r"\setcounter{ex}{0}")
        latex_lines.append(rf"\noindent\textbf{{PHẦN II. Câu trắc nghiệm đúng sai.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n2}. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec2:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            subs = q.sub_statements or []
            choice_tf_lines = [r"\choiceTF[1]"]
            for sub in subs:
                is_t = sub.is_true if hasattr(sub, 'is_true') else True
                prefix = r"\True " if is_t else ""
                content = sub.content or ""
                content = re.sub(r'^[a-d]\)\s*', '', content)
                choice_tf_lines.append(rf"{prefix}{content}")
            latex_lines.append("\n".join(choice_tf_lines))
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                latex_lines.append(r"\begin{itemchoice}")
                for sub in subs:
                    exp = sub.explanation or "Giải thích chi tiết."
                    latex_lines.append(rf"\itemch {exp}")
                latex_lines.append(r"\end{itemchoice}")
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    if n3 > 0:
        latex_lines.append(r"\setcounter{ex}{0}")
        latex_lines.append(rf"\noindent\textbf{{PHẦN III. Câu trắc nghiệm trả lời ngắn.}} \textit{{Thí sinh trả lời từ câu 1 đến câu {n3}.}}")
        latex_lines.append(r"\vspace{0.3em}")
        for it in sec3:
            q = it.question
            if not q: continue
            stem = q.stem or ""
            ans_key = it.answer_key or q.short_answer_key or "0"
            latex_lines.append(r"\begin{ex}")
            latex_lines.append(stem)
            latex_lines.append(rf"\shortans{{{ans_key}}}")
            
            if is_solution:
                latex_lines.append(r"\begin{loigiai}")
                latex_lines.append(q.explanation or f"Đáp số: {ans_key}")
                latex_lines.append(r"\end{loigiai}")
            latex_lines.append(r"\end{ex}")
            latex_lines.append(r"\vspace{0.2em}")

    latex_lines.append(r"\vspace{1em}")
    latex_lines.append(r"\begin{center}\textbf{--- HẾT ---}\end{center}")
    return "\n".join(latex_lines)


def generate_variant_pdf(variant: ExamVariant, output_pdf: Path) -> bool:
    """Generates pure vector LaTeX PDF using Tectonic / Composer service."""
    try:
        latex_code = generate_variant_latex(variant, is_solution=False)
        success, err_msg, elapsed = compile_latex_to_pdf(
            latex_code, output_pdf, title=f"Đề Thi Mã {variant.variant_code}", mode="dethi"
        )
        if success and output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"LaTeX/Tectonic PDF generation failed: {e}")

    return generate_pdf_reportlab(variant, output_pdf)


def generate_solution_pdf(variant: ExamVariant, output_pdf: Path) -> bool:
    """Generates solution PDF using ultra-fast ReportLab with browser fallback."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        font_italic = 'TimesNewRoman-Italic' if 'TimesNewRoman-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

        style_norm = ParagraphStyle('Norm', fontName=font_main, fontSize=10.5, leading=14)
        style_bold = ParagraphStyle('Bold', fontName=font_bold, fontSize=10.5, leading=14)
        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=13, leading=16, alignment=1)
        style_sub = ParagraphStyle('Sub', fontName=font_italic, fontSize=10, leading=13, alignment=1)
        style_exp = ParagraphStyle('Exp', fontName=font_main, fontSize=10, leading=13, backColor=colors.HexColor('#f8fafc'), borderPadding=6)

        story = [
            Paragraph(f"<b>HƯỚNG DẪN GIẢI CHI TIẾT - MÃ ĐỀ THI {variant.variant_code}</b>", style_title),
            Paragraph("<i>BÀI THI: TOÁN HỌC • CHUẨN ĐỊNH DẠNG BỘ GIÁO DỤC 2025</i>", style_sub),
            Spacer(1, 12)
        ]

        for it in sorted(variant.items, key=lambda x: x.variant_order_index):
            q = it.question
            if not q: continue
            clean_stem = q.stem.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Câu {it.variant_order_index}:</b> {clean_stem}", style_bold))
            story.append(Paragraph(f"<b>Đáp án đúng:</b> <font color='#0066cc'><b>{it.answer_key or 'A'}</b></font>", style_norm))
            clean_exp = (q.explanation or "Đang cập nhật hướng dẫn giải chi tiết.").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"<b>Lời giải chi tiết:</b><br/>{clean_exp}", style_exp))
            story.append(Spacer(1, 8))

        doc.build(story)
        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"ReportLab solution PDF failed: {e}")

    # Fallback to browser
    temp_html = output_pdf.with_suffix(".temp.html")
    try:
        generate_solution_html(variant, temp_html)
        if convert_html_to_pdf_browser(temp_html, output_pdf):
            return True
    except Exception as e:
        logger.warning(f"Browser solution PDF failed: {e}")
    finally:
        if temp_html.exists():
            try:
                temp_html.unlink()
            except Exception:
                pass
    return False


def generate_answer_sheet_pdf(master: MasterExam, variants: List[ExamVariant], output_pdf: Path) -> bool:
    """Generates answer key matrix PDF using ultra-fast ReportLab with browser fallback."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=36, bottomMargin=36)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=13, leading=16, alignment=1)

        story = [
            Paragraph("<b>BẢNG ĐÁP ÁN TỔNG HỢP CÁC MÃ ĐỀ THI</b>", style_title),
            Spacer(1, 10)
        ]
        data = [["Câu", "Thể thức"] + [f"Mã {v.variant_code}" for v in variants]]
        for q_idx in range(1, master.total_questions + 1):
            m_item = next((it for it in master.items if it.order_index == q_idx), None)
            fmt = m_item.question.item_format if (m_item and m_item.question) else "SINGLE_CHOICE"
            fmt_lbl = "TN 4 Lựa chọn" if fmt == "SINGLE_CHOICE" else "Đúng/Sai" if fmt == "TRUE_FALSE_GROUP" else "Trả lời ngắn"
            row = [str(q_idx), fmt_lbl]
            for v in variants:
                v_item = next((vi for vi in v.items if vi.variant_order_index == q_idx), None)
                row.append(v_item.answer_key if v_item and v_item.answer_key else "-")
            data.append(row)

        col_w = [40, 95] + [(515 - 135) / len(variants)] * len(variants)
        t_mat = Table(data, colWidths=col_w)
        t_mat.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#888888')),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9.5),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(t_mat)
        doc.build(story)
        if output_pdf.exists() and output_pdf.stat().st_size > 1000:
            return True
    except Exception as e:
        logger.warning(f"ReportLab answer sheet PDF failed: {e}")

    # Fallback to browser
    temp_html = output_pdf.with_suffix(".temp.html")
    try:
        generate_answer_sheet_html(master, variants, temp_html)
        if convert_html_to_pdf_browser(temp_html, output_pdf):
            return True
    except Exception as e:
        logger.warning(f"Answer sheet PDF generation failed: {e}")
    finally:
        if temp_html.exists():
            try:
                temp_html.unlink()
            except Exception:
                pass
    return False


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> bool:
    """Converts a DOCX file to PDF using Word COM automation on Windows with strict 10s timeout."""
    docx_p = Path(docx_path).resolve()
    pdf_p = Path(pdf_path).resolve()

    if os.name == "nt":
        try:
            ps_cmd = f"""
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open('{str(docx_p)}')
    $doc.SaveAs([ref]'{str(pdf_p)}', [ref]17)
    $doc.Close([ref]$false)
}} finally {{
    $word.Quit()
}}
"""
            res = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=12)
            if pdf_p.exists() and pdf_p.stat().st_size > 1000:
                return True
        except Exception as e:
            logger.warning(f"Word COM PDF conversion failed: {e}")

    return False


def generate_omr_bubble_sheet_pdf(output_pdf: Path) -> bool:
    """Generates official 2025 OMR Answer Bubble Sheet PDF for students to fill in."""
    try:
        register_vietnamese_fonts()
        from reportlab.pdfbase import pdfmetrics
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, leftMargin=36, rightMargin=36, topMargin=25, bottomMargin=25)
        font_main = 'TimesNewRoman' if 'TimesNewRoman' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        font_bold = 'TimesNewRoman-Bold' if 'TimesNewRoman-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        font_italic = 'TimesNewRoman-Italic' if 'TimesNewRoman-Italic' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Oblique'

        style_title = ParagraphStyle('Title', fontName=font_bold, fontSize=12.5, alignment=1)
        style_sub = ParagraphStyle('Sub', fontName=font_main, fontSize=9.5, alignment=1)
        style_sec = ParagraphStyle('Sec', fontName=font_bold, fontSize=10, textColor=colors.HexColor('#002b49'))
        style_cell = ParagraphStyle('Cell', fontName=font_main, fontSize=8.5, alignment=1)

        story = [
            Paragraph("<b>BỘ GIÁO DỤC VÀ ĐÀO TẠO</b>", style_sub),
            Paragraph("<b>PHIẾU TRẢ LỜI TRẮC NGHIỆM (ĐỊNH DẠNG TỪ NĂM 2025)</b>", style_title),
            Paragraph("<i>Dùng bút chì 2B để tô kín các ô tròn tương ứng với phương án lựa chọn</i>", style_sub),
            Spacer(1, 6)
        ]

        info_data = [
            [
                Paragraph("Họ và tên: .................................................... Lớp: .........................<br/>Ngày sinh: ......./......./...........   SBD: .........................<br/>Hội đồng thi: .........................................................", style_cell),
                Paragraph("<b>SỐ BÁO DANH</b><br/>[ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ][ &nbsp; ]<br/><b>MÃ ĐỀ THI</b><br/>[ &nbsp; ][ &nbsp; ][ &nbsp; ]", style_cell)
            ]
        ]
        t_info = Table(info_data, colWidths=[365, 155])
        t_info.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#999999')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN I: THÍ SINH CHỌN MỘT PHƯƠNG ÁN TRẢ LỜI (Từ câu 1 đến câu 12)</b>", style_sec))
        p1_data = [["Câu", "Phương án", "Câu", "Phương án"]]
        for i in range(1, 7):
            p1_data.append([str(i), "[A]   [B]   [C]   [D]", str(i+6), "[A]   [B]   [C]   [D]"])
        t_p1 = Table(p1_data, colWidths=[40, 220, 40, 220])
        t_p1.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_p1)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN II: THÍ SINH CHỌN ĐÚNG HOẶC SAI TRONG MỖI Ý a), b), c), d) (Từ câu 1 đến câu 4)</b>", style_sec))
        p2_data = [["Câu", "Ý a", "Ý b", "Ý c", "Ý d"]]
        for i in range(1, 5):
            p2_data.append([f"Câu {i}", "[Đ]  [S]", "[Đ]  [S]", "[Đ]  [S]", "[Đ]  [S]"])
        t_p2 = Table(p2_data, colWidths=[65, 113, 114, 114, 114])
        t_p2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_p2)
        story.append(Spacer(1, 8))

        story.append(Paragraph("<b>PHẦN III: THÍ SINH VIẾT VÀ TÔ KẾT QUẢ VÀO Ô ĐÁP SỐ (Từ câu 1 đến câu 6)</b>", style_sec))
        p3_data = [
            ["Câu", "Đáp số", "Câu", "Đáp số"],
            ["1", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "4", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
            ["2", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "5", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
            ["3", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]", "6", "[ - ] [ , ] [ 0 ] [ 1 ] [ 2 ] [ 3 ] [ 4 ] [ 5 ] [ 6 ] [ 7 ] [ 8 ] [ 9 ]"],
        ]
        t_p3 = Table(p3_data, colWidths=[35, 225, 35, 225])
        t_p3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), font_main),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(t_p3)

        doc.build(story)
        return output_pdf.exists() and output_pdf.stat().st_size > 1000
    except Exception as e:
        logger.warning(f"ReportLab OMR Bubble Sheet PDF failed: {e}")
        return False


def export_single_variant_pdf(variant: ExamVariant, output_path: Path) -> Path:
    """Generates an official PDF directly for a single exam variant."""
    success = generate_variant_pdf(variant, output_path)
    if not success or not output_path.exists():
        generate_pdf_reportlab(variant, output_path)
    return output_path


def export_exam_package_zip(
    master_exam_id: str,
    db: Session,
    include_pdf: bool = True,
    export_format: str = "pdf"
) -> str:
    """Creates a comprehensive PDF export package containing:
    - De_{code}.pdf for all variants
    - LoiGiai_{code}.pdf for all variants
    - BangDapAn_TongHop.pdf and BangDapAn_TongHop.csv
    - Phieu_Tra_Loi_Trac_Nghiem_2025.pdf
    Returns the absolute path to the generated zip file.
    """
    master = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    variants = db.query(ExamVariant).filter(ExamVariant.master_exam_id == master_exam_id).all()
    if not variants:
        raise ValueError("No exam variants found. Please shuffle the exam first.")

    temp_dir = STORAGE_EXPORTS_DIR / f"temp_{master_exam_id}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"Goi_DeThi_{master.subject.code if master.subject else 'MON'}_{master.id[:8]}.zip"
    zip_path = STORAGE_EXPORTS_DIR / zip_filename

    generated_pdf_files = []
    generated_csv_files = []

    try:
        # 1. Generate PDF for each variant and its solution
        for v in variants:
            exam_pdf = temp_dir / f"De_{v.variant_code}.pdf"
            sol_pdf = temp_dir / f"LoiGiai_{v.variant_code}.pdf"
            generate_variant_pdf(v, exam_pdf)
            generate_solution_pdf(v, sol_pdf)
            generated_pdf_files.extend([exam_pdf, sol_pdf])

        # 2. Generate CSV answer key
        csv_file = temp_dir / "BangDapAn_TongHop.csv"
        try:
            from backend.services.shuffling_engine import get_answer_key_matrix
            km = get_answer_key_matrix(master.id, db)
            rows = km.get("key_matrix", [])
            csv_lines = ["Câu,Thể thức,Đề gốc," + ",".join([f"Mã {v.variant_code}" for v in variants])]
            for r in rows:
                c_line = [str(r.get("master_question_index", "")), str(r.get("item_format", "")), str(r.get("master_answer_key", ""))]
                for v in variants:
                    c_line.append(str(r.get(f"variant_{v.variant_code}", "")))
                csv_lines.append(",".join(c_line))
            csv_file.write_text("\n".join(csv_lines), encoding="utf-8-sig")
            generated_csv_files.append(csv_file)
        except Exception:
            pass

        # 3. Generate answer matrix PDF
        matrix_pdf = temp_dir / "BangDapAn_TongHop.pdf"
        generate_answer_sheet_pdf(master, variants, matrix_pdf)
        generated_pdf_files.append(matrix_pdf)

        # 4. Generate Blank 2025 OMR Bubble Sheet for student testing
        omr_pdf = temp_dir / "Phieu_Tra_Loi_Trac_Nghiem_2025.pdf"
        generate_omr_bubble_sheet_pdf(omr_pdf)
        generated_pdf_files.append(omr_pdf)

        # 5. Create ZIP archive
        files_to_zip = [f for f in generated_pdf_files if f.exists()] + generated_csv_files

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for f in files_to_zip:
                if f.exists():
                    zipf.write(f, arcname=f.name)

        return str(zip_path)
    finally:
        all_temp = generated_pdf_files + generated_csv_files
        for f in all_temp:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass
        try:
            if temp_dir.exists():
                temp_dir.rmdir()
        except Exception:
            pass


def compute_item_analytics(
    master_exam_id: str,
    student_scores: List[Dict[str, Any]],
    db: Session
) -> Dict[str, Any]:
    """Calculates psychometric metrics:
    - Item difficulty p = R / N (Proportion of students answering correctly)
    - Item discrimination D = P_H - P_L (Upper 27% correct rate minus lower 27% correct rate)
    - Flags defective questions if D < 0.20
    Updates Question records in the database.
    """
    master = db.query(MasterExam).filter(MasterExam.id == master_exam_id).first()
    if not master:
        raise ValueError(f"MasterExam with id '{master_exam_id}' not found.")

    N = len(student_scores)
    if N < 4:
        raise ValueError("At least 4 student score records are required for psychometric calculations.")

    # Sort students by total_score descending
    sorted_students = sorted(student_scores, key=lambda s: s.get("total_score", 0.0), reverse=True)
    cutoff = max(1, int(round(0.27 * N)))

    high_group = sorted_students[:cutoff]
    low_group = sorted_students[-cutoff:]
    n_group = cutoff

    items_report = []
    defective_count = 0

    # Collect all questions in master exam
    for master_item in master.items:
        q = master_item.question
        q_id = q.id
        q_key = f"q_{master_item.order_index}"

        # Total correct
        total_correct = sum(1 for s in sorted_students if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_val = round(total_correct / N, 3)

        # High group correct
        high_correct = sum(1 for s in high_group if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_high = high_correct / n_group

        # Low group correct
        low_correct = sum(1 for s in low_group if s.get("answers", {}).get(q_key, False) or s.get("answers", {}).get(q_id, False))
        p_low = low_correct / n_group

        d_val = round(p_high - p_low, 3)

        # Defective rule: D < 0.2
        is_defective = d_val < 0.20
        if is_defective:
            defective_count += 1

        # Update question record in database
        q.difficulty_p = p_val
        q.discrimination_d = d_val
        q.is_defective = is_defective
        db.add(q)

        items_report.append({
            "order_index": master_item.order_index,
            "question_id": q.id,
            "stem": q.stem[:80] + "..." if len(q.stem) > 80 else q.stem,
            "difficulty_p": p_val,
            "discrimination_d": d_val,
            "is_defective": is_defective,
            "status": "DEFECTIVE_FLAGGED" if is_defective else "ACCEPTABLE"
        })

    db.commit()

    return {
        "master_exam_id": master.id,
        "total_candidates": N,
        "high_group_size": cutoff,
        "low_group_size": cutoff,
        "defective_questions_count": defective_count,
        "items": items_report
    }


def _add_options_adaptive(
    doc: docx.Document,
    options: List[Dict[str, Any]],
    default_font_size: Union[int, float] = 11,
    math_format: str = "mathtype"
):
    """Lays out 4 choices (A, B, C, D) adaptively like standard Vietnamese exam papers:
    - 4 columns across 1 line if all options are short (<= 18 chars, no TikZ)
    - 2 columns x 2 rows if options are medium (<= 38 chars, no TikZ)
    - 1 column (4 paragraphs) if options are long or contain TikZ diagrams
    """
    if not options:
        return

    # Check if any option has tikz or is long
    has_tikz = any(re.search(r'\\begin\{tikzpicture\}', opt.get("content", "")) for opt in options)
    clean_contents = [re.sub(r'[\$\s\\]', '', opt.get("content", "")) for opt in options]
    max_len = max((len(c) for c in clean_contents), default=0)

    if not has_tikz and max_len <= 18 and len(options) == 4:
        # Layout 4 options across 1 line in a borderless table
        tbl = doc.add_table(rows=1, cols=4)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        _remove_table_borders(tbl)
        col_w = Inches(1.70)  # 4 * 1.70 = 6.80 inches ~ 17.3 cm (strictly within page margins)
        for col in tbl.columns:
            col.width = col_w
        for opt_idx, opt in enumerate(options):
            lbl = opt.get("label", chr(65 + opt_idx))
            cell = tbl.cell(0, opt_idx)
            cell.width = col_w
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_math_text_to_paragraph(p, opt.get("content", ""), bold_prefix=f"{lbl}. ", default_font_size=default_font_size, math_format=math_format)

    elif not has_tikz and max_len <= 38 and len(options) == 4:
        # Layout 2 options per row (2 rows x 2 cols) in a borderless table
        tbl = doc.add_table(rows=2, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        _remove_table_borders(tbl)
        col_w = Inches(3.40)  # 2 * 3.40 = 6.80 inches
        for col in tbl.columns:
            col.width = col_w
        for opt_idx, opt in enumerate(options):
            r_idx = opt_idx // 2
            c_idx = opt_idx % 2
            lbl = opt.get("label", chr(65 + opt_idx))
            cell = tbl.cell(r_idx, c_idx)
            cell.width = col_w
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            add_math_text_to_paragraph(p, opt.get("content", ""), bold_prefix=f"{lbl}. ", default_font_size=default_font_size, math_format=math_format)

    else:
        # Layout 1 option per line (paragraphs)
        for opt_idx, opt in enumerate(options):
            lbl = opt.get("label", chr(65 + opt_idx))
            content = opt.get("content", "")
            p_opt = doc.add_paragraph()
            p_opt.paragraph_format.left_indent = Inches(0.2)
            p_opt.paragraph_format.space_before = Pt(1)
            p_opt.paragraph_format.space_after = Pt(2)
            p_opt.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p_opt.paragraph_format.line_spacing = 1.15

            opt_tikz = re.search(r'\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}', content)
            if opt_tikz:
                r_lbl = p_opt.add_run(f"{lbl}. ")
                r_lbl.font.bold = True
                r_lbl.font.name = "Times New Roman"
                r_lbl.font.size = Pt(default_font_size)
                try:
                    from backend.services.tikz_renderer import render_tikz_to_png
                    png_res = render_tikz_to_png(opt_tikz.group(0))
                    if png_res.get("success") and png_res.get("png_path"):
                        doc.add_picture(png_res["png_path"], width=Inches(2.2))
                except Exception:
                    pass
            else:
                add_math_text_to_paragraph(p_opt, content, bold_prefix=f"{lbl}. ", default_font_size=default_font_size, math_format=math_format)


def generate_digitized_exam_docx(
    questions: List[Dict[str, Any]],
    output_path: Path,
    title: str = "ĐỀ THI KHẢO THÍ",
    school_name: str = "SỞ GIÁO DỤC VÀ ĐÀO TẠO",
    subject_name: str = "Toán học",
    grade: str = "12",
    variant_code: str = "101",
    duration: int = 90,
    math_format: str = "mathtype"
) -> Path:
    """Generates an official single-column Word .docx document for a list of digitized questions,
    matching standard Vietnamese examination format (top-to-bottom layout like PDF exam papers),
    with genuine MathType OLE equations (Equation.DSMT4), adaptive option columns, and embedded TikZ diagrams.
    """
    doc = docx.Document()
    _configure_document_styles(doc)

    # 1. Page Format: Standard A4 Portrait (210 x 297 mm, 1.8 cm margins)
    s1 = doc.sections[0]
    s1.orientation = WD_ORIENT.PORTRAIT
    s1.page_width = Mm(210)
    s1.page_height = Mm(297)
    s1.top_margin = Cm(1.5)
    s1.bottom_margin = Cm(1.5)
    s1.left_margin = Cm(1.8)
    s1.right_margin = Cm(1.8)

    # 2. Header in Section 1 (Single column, with compact student info matching PDF)
    _setup_exam_header(
        doc=doc,
        school_name=school_name,
        exam_title=title,
        subject_name=subject_name,
        grade=grade,
        variant_code=variant_code,
        duration=duration,
        compact_student_info=True
    )

    section_titles = {
        1: "PHẦN I. Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.",
        2: "PHẦN II. Thí sinh trả lời từ câu 1 đến 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.",
        3: "PHẦN III. Thí sinh trả lời từ câu 1 đến câu 6. Câu trắc nghiệm trả lời ngắn.",
        4: "PHẦN IV. Tự luận.",
    }

    current_section = None

    for idx, q in enumerate(questions):
        fmt = q.get("item_format", "SINGLE_CHOICE")
        sec = 1
        if fmt == "SINGLE_CHOICE":
            sec = 1
        elif fmt == "TRUE_FALSE_GROUP":
            sec = 2
        elif fmt == "SHORT_ANSWER":
            sec = 3
        else:
            sec = 4

        # Section Header Banner
        if sec != current_section:
            current_section = sec
            sec_heading = doc.add_paragraph()
            sec_heading.paragraph_format.space_before = Pt(12)
            sec_heading.paragraph_format.space_after = Pt(4)
            r_sec = sec_heading.add_run(section_titles.get(sec, f"PHẦN {sec}."))
            r_sec.font.bold = True
            r_sec.font.size = Pt(11)
            r_sec.font.name = "Times New Roman"

        # Question Stem & Diagram / Table
        stem = q.get("stem", "")
        # Check if stem contains TikZ diagram
        tikz_match = re.search(r'\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\}', stem)
        # Check if stem contains LaTeX table array
        table_match = re.search(r'(?:\$\$\s*)?\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|tabular)\}(?:\s*\$\$)?', stem, re.DOTALL)

        if tikz_match:
            tikz_code = tikz_match.group(0)
            pre_text = stem[:tikz_match.start()].strip()
            post_text = stem[tikz_match.end():].strip()

            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(4)
            p_q.paragraph_format.space_after = Pt(2)
            add_math_text_to_paragraph(p_q, pre_text, bold_prefix=f"Câu {idx + 1}. ", default_font_size=11, math_format=math_format)

            # Insert TikZ Diagram
            try:
                from backend.services.tikz_renderer import render_tikz_to_png
                png_res = render_tikz_to_png(tikz_code)
                if png_res.get("success") and png_res.get("png_path"):
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(2)
                    p_img.paragraph_format.space_after = Pt(2)
                    doc.add_picture(png_res["png_path"], width=Inches(2.8))
            except Exception as img_err:
                logger.warning(f"Could not render TikZ for docx: {img_err}")

            if post_text:
                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(2)
                p_post.paragraph_format.space_after = Pt(2)
                add_math_text_to_paragraph(p_post, post_text, default_font_size=11, math_format=math_format)

        elif table_match:
            pre_text = stem[:table_match.start()].strip()
            post_text = stem[table_match.end():].strip()
            # Clean off any stray $$ delimiter left at edges
            pre_text = re.sub(r'\$\$\s*$', '', pre_text).strip()
            post_text = re.sub(r'^\s*\$\$', '', post_text).strip()

            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(4)
            p_q.paragraph_format.space_after = Pt(2)
            add_math_text_to_paragraph(p_q, pre_text, bold_prefix=f"Câu {idx + 1}. ", default_font_size=11, math_format=math_format)

            # Parse array rows and columns into a clean native Word table
            body = table_match.group(1).strip()
            is_variation_table = any(k in body for k in [r"\nearrow", r"\searrow", r"\infty", r"-\infty", r"+\infty"])
            lines = body.split(r"\\")
            grid = []
            for line in lines:
                cleaned = line.replace(r"\hline", "").strip()
                if not cleaned:
                    continue
                cells = [c.strip() for c in cleaned.split("&")]
                grid.append(cells)

            if grid:
                tbl = doc.add_table(rows=len(grid), cols=len(grid[0]))
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row_cells in enumerate(grid):
                    for c_idx, cell_text in enumerate(row_cells):
                        cell = tbl.cell(r_idx, c_idx)
                        if is_variation_table:
                            # Standard variation table borders: only horizontal dividers and right line of label column
                            b_bottom = "single" if r_idx in (0, 1) else "none"
                            b_right = "single" if c_idx == 0 else "none"
                            _set_cell_border(cell, top="none", bottom=b_bottom, left="none", right=b_right, sz="4")
                        else:
                            _set_cell_border(cell, top="single", bottom="single", left="single", right="single", sz="4")
                        cp = cell.paragraphs[0]
                        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cp.paragraph_format.space_before = Pt(2)
                        cp.paragraph_format.space_after = Pt(2)
                        ct = cell_text.strip()
                        if not ct:
                            # CRUCIAL: Empty cell stays empty! Never wrap into $$!
                            continue
                        if ct.startswith(r"\text{") and ct.endswith("}"):
                            ct = ct[6:-1].strip()
                        elif not ct.startswith("$"):
                            ct = f"${ct}$"
                        add_math_text_to_paragraph(cp, ct, default_font_size=10.5, math_format=math_format)

            if post_text:
                p_post = doc.add_paragraph()
                p_post.paragraph_format.space_before = Pt(2)
                p_post.paragraph_format.space_after = Pt(2)
                add_math_text_to_paragraph(p_post, post_text, default_font_size=11, math_format=math_format)

        else:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(4)
            p_q.paragraph_format.space_after = Pt(2)
            add_math_text_to_paragraph(p_q, stem, bold_prefix=f"Câu {idx + 1}. ", default_font_size=11, math_format=math_format)

        # Options / Sub-statements
        if fmt == "SINGLE_CHOICE" and q.get("options"):
            _add_options_adaptive(doc, q.get("options", []), default_font_size=11, math_format=math_format)

        elif fmt == "TRUE_FALSE_GROUP" and q.get("sub_statements"):
            for sub in q.get("sub_statements", []):
                p_sub = doc.add_paragraph()
                p_sub.paragraph_format.left_indent = Inches(0.25)
                p_sub.paragraph_format.space_before = Pt(1)
                p_sub.paragraph_format.space_after = Pt(1.5)
                add_math_text_to_paragraph(p_sub, sub.get("content", ""), bold_prefix=f"{sub.get('label')}) ", default_font_size=11, math_format=math_format)

        elif fmt == "SHORT_ANSWER":
            p_ans = doc.add_paragraph()
            p_ans.paragraph_format.left_indent = Inches(0.25)
            p_ans.paragraph_format.space_before = Pt(1)
            p_ans.paragraph_format.space_after = Pt(4)
            add_math_text_to_paragraph(p_ans, "................................................................", italic_prefix="Đáp số: ", default_font_size=11, math_format=math_format)

    # Footer Note
    p_end = doc.add_paragraph()
    p_end.paragraph_format.space_before = Pt(16)
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_end = p_end.add_run("─────────────────── HẾT ───────────────────")
    r_end.font.bold = True
    r_end.font.size = Pt(11)
    r_end.font.name = "Times New Roman"

    p_super = doc.add_paragraph()
    p_super.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_super.paragraph_format.space_after = Pt(6)
    r_sup = p_super.add_run("Thí sinh không được sử dụng tài liệu. Cán bộ coi thi không giải thích gì thêm.")
    r_sup.font.italic = True
    r_sup.font.size = Pt(10)
    r_sup.font.name = "Times New Roman"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return output_path


def generate_digitized_exam_pdf(
    questions: List[Dict[str, Any]],
    output_pdf: Path,
    title: str = "ĐỀ THI KHẢO THÍ",
    school_name: str = "SỞ GIÁO DỤC VÀ ĐÀO TẠO",
    subject_name: str = "Toán học",
    grade: str = "12",
    variant_code: str = "101",
    duration: int = 90,
    math_format: str = "mathtype"
) -> bool:
    """Generates an official high-fidelity print-quality PDF for digitized questions.
    Tier 1 (Preferred): Authentic LaTeX-grade PDF engine with CMU Serif typography and MathJax vector SVG.
    Tier 2 (Fallback): Word COM automation on Windows.
    """
    output_pdf = Path(output_pdf).resolve()
    from backend.services.latex_pdf_exporter import generate_digitized_exam_latex_pdf
    ok = generate_digitized_exam_latex_pdf(
        questions=questions,
        output_pdf=output_pdf,
        title=title,
        school_name=school_name,
        subject_name=subject_name,
        grade=grade,
        variant_code=variant_code,
        duration=duration
    )
    return bool(ok and output_pdf.exists() and output_pdf.stat().st_size > 1000)
