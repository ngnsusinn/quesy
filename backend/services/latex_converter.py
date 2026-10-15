"""
LaTeX Converter Service for QUESY.

Provides:
- Sanitization and formatting of LaTeX strings.
- MathType MTEF / OLE decoding from DOCX files into clean LaTeX formulas.
- OMML (Office Math Markup Language) to LaTeX conversion for native Word equations.
- KaTeX renderability validation and delimiter balancing.
- Complete DOCX content extraction converting all formulas to LaTeX in-line.
"""

from __future__ import annotations

import io
import os
import re
import struct
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False


# ---------------------------------------------------------------------------
# 1. Unicode & Mathematical Symbol Mappings
# ---------------------------------------------------------------------------

UNICODE_MATH_MAP: Dict[str, str] = {
    "×": r"\times",
    "÷": r"\div",
    "≤": r"\le",
    "≥": r"\ge",
    "≠": r"\ne",
    "±": r"\pm",
    "∓": r"\mp",
    "≈": r"\approx",
    "≡": r"\equiv",
    "∈": r"\in",
    "∉": r"\notin",
    "⊂": r"\subset",
    "⊃": r"\supset",
    "⊆": r"\subseteq",
    "⊇": r"\supseteq",
    "∪": r"\cup",
    "∩": r"\cap",
    "∅": r"\emptyset",
    "∞": r"\infty",
    "→": r"\rightarrow",
    "←": r"\leftarrow",
    "⇒": r"\Rightarrow",
    "⇐": r"\Leftarrow",
    "⇔": r"\Leftrightarrow",
    "↔": r"\leftrightarrow",
    "∀": r"\forall",
    "∃": r"\exists",
    "∂": r"\partial",
    "∇": r"\nabla",
    "°": r"^\circ",
    "•": r"\cdot",
    "·": r"\cdot",
    "…": r"\dots",
    "⋯": r"\cdots",
    "⋱": r"\ddots",
    "⋮": r"\vdots",
    "ℝ": r"\mathbb{R}",
    "ℤ": r"\mathbb{Z}",
    "ℕ": r"\mathbb{N}",
    "ℚ": r"\mathbb{Q}",
    "ℂ": r"\mathbb{C}",
    # Greek lowercase
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "ε": r"\varepsilon",
    "θ": r"\theta",
    "λ": r"\lambda",
    "μ": r"\mu",
    "π": r"\pi",
    "ρ": r"\rho",
    "σ": r"\sigma",
    "τ": r"\tau",
    "φ": r"\varphi",
    "ω": r"\omega",
    # Greek uppercase
    "Δ": r"\Delta",
    "Γ": r"\Gamma",
    "Λ": r"\Lambda",
    "Σ": r"\Sigma",
    "Ω": r"\Omega",
    "Φ": r"\Phi",
}

SUPERSCRIPT_MAP: Dict[str, str] = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁺": "+", "⁻": "-", "⁼": "=", "⁽": "(", "⁾": ")", "ⁿ": "n"
}

SUBSCRIPT_MAP: Dict[str, str] = {
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "₊": "+", "₋": "-", "₌": "=", "₍": "(", "₎": ")"
}


# ---------------------------------------------------------------------------
# 2. LaTeX Sanitization & Normalization
# ---------------------------------------------------------------------------

def sanitize_latex(text: str) -> str:
    """
    Sanitize and normalize LaTeX formulas and surrounding Vietnamese educational text.
    - Standardizes inline delimiters to $...$ and block delimiters to $$...$$.
    - Replaces unicode math symbols with standard LaTeX macros.
    - Normalizes unicode superscripts/subscripts.
    - Automatically adds backslashes to standard math functions (sin, cos, ln, lim, etc.).
    - Fixes malformed commands and delimiter spacing.
    """
    if not text:
        return ""

    s = text

    # 1. Normalize block delimiters \[ ... \] to $$ ... $$
    s = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', s, flags=re.DOTALL)

    # 2. Normalize inline delimiters \( ... \) to $ ... $
    s = re.sub(r'\\\((.*?)\\\)', r'$\1$', s, flags=re.DOTALL)

    # 3. Handle unicode superscripts and subscripts outside or inside math
    for uni, repl in SUPERSCRIPT_MAP.items():
        if uni in s:
            # If after a letter/digit, replace with ^{repl}
            s = re.sub(r'([A-Za-z0-9])' + re.escape(uni), r'\1^{' + repl + '}', s)
            s = s.replace(uni, '^{' + repl + '}')

    for uni, repl in SUBSCRIPT_MAP.items():
        if uni in s:
            s = re.sub(r'([A-Za-z0-9])' + re.escape(uni), r'\1_{' + repl + '}', s)
            s = s.replace(uni, '_{' + repl + '}')

    # 4. Process math expressions inside delimiters vs regular text
    def sanitize_math_content(math_str: str) -> str:
        res = math_str
        # Replace unicode math symbols
        for u_char, tex in UNICODE_MATH_MAP.items():
            if u_char in res:
                res = res.replace(u_char, f" {tex} ")

        # Fix missing backslashes on functions: sin, cos, tan, cot, ln, log, lim, max, min, exp, det
        res = re.sub(
            r'(?<![\\A-Za-z])(sin|cos|tan|cot|ln|log|lim|max|min|exp|det)(?![A-Za-z])',
            r'\\\1',
            res
        )

        # Fix sqrt syntax like √(x + 1) -> \sqrt{x + 1}
        res = re.sub(r'√\s*\((.*?)\)', r'\\sqrt{\1}', res)
        res = re.sub(r'√\s*([A-Za-z0-9]+)', r'\\sqrt{\1}', res)
        res = res.replace("√", r"\sqrt")

        # Normalize fractions \frac {a} {b} -> \frac{a}{b}
        res = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'\\frac{\1}{\2}', res)

        # Fix double backslashes that were accidentally escaped (except linebreaks \\)
        res = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', res)

        # Clean multiple spaces inside formula
        res = re.sub(r'[ \t]+', ' ', res).strip()
        return res

    # Process $$...$$ display math
    def replace_display(match: re.Match) -> str:
        content = match.group(1)
        cleaned = sanitize_math_content(content)
        return f"$${cleaned}$$"

    s = re.sub(r'\$\$(.*?)\$\$', replace_display, s, flags=re.DOTALL)

    # Process $...$ inline math
    def replace_inline(match: re.Match) -> str:
        content = match.group(1)
        cleaned = sanitize_math_content(content)
        return f"${cleaned}$"

    # Match single $...$ not preceded or followed by $
    s = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', replace_inline, s, flags=re.DOTALL)

    # 5. Unicode math symbols that might still be outside math delimiters:
    # If standard math symbols like ≤, ≥, ∈, ≠ appear outside $, convert them along with surrounding expression
    for u_char, tex in UNICODE_MATH_MAP.items():
        if u_char in s:
            s = s.replace(u_char, f" ${tex}$ ")

    # 6. Merge adjacent $...$ $...$
    while True:
        new_s = re.sub(r'\$([^$]+)\$\s*\$([^$]+)\$', r'$\1 \2$', s)
        if new_s == s:
            break
        s = new_s

    # 7. Clean up redundant spaces around math delimiters
    # Ensure space before $ if preceded by letter/number
    s = re.sub(r'([a-zA-Z0-9\u00C0-\u024F\u1EA0-\u1EF9])\$', r'\1 $', s)
    # Ensure space after $ if followed by letter/number
    s = re.sub(r'\$([a-zA-Z0-9\u00C0-\u024F\u1EA0-\u1EF9])', r'$ \1', s)

    # Re-normalize $$
    s = s.replace('$ $', '$$').replace('$$ ', '$$').replace(' $$', '$$')
    s = re.sub(r'[ \t]{2,}', ' ', s)

    return s.strip()


# ---------------------------------------------------------------------------
# 3. Delimiter Balancing & KaTeX Validation
# ---------------------------------------------------------------------------

def repair_math_delimiters(text: str) -> str:
    """
    Ensure math delimiters ($ and $$) and grouping brackets inside formulas are balanced.
    If an unclosed single $ is detected at the end of a sentence or line, closes it.
    """
    if not text:
        return ""

    # Check for unescaped dollar signs
    # Exclude currency like $100 if preceded by space and followed by pure number with no matching $
    chars = list(text)
    in_math = False
    in_display = False
    i = 0
    n = len(chars)
    repaired: List[str] = []

    while i < n:
        # Check $$
        if i + 1 < n and chars[i] == '$' and chars[i + 1] == '$':
            if in_display:
                in_display = False
            else:
                in_display = True
            repaired.append('$$')
            i += 2
            continue
        elif chars[i] == '$':
            if in_math:
                in_math = False
            else:
                in_math = True
            repaired.append('$')
            i += 1
            continue
        else:
            repaired.append(chars[i])
            i += 1

    result = "".join(repaired)

    # If unclosed display math, close at end
    if in_display:
        result += "$$"
    # If unclosed inline math, close at end
    elif in_math:
        result += "$"

    # Now balance brackets inside math expressions
    def balance_formula_brackets(formula: str) -> str:
        open_curlies = formula.count('{') - formula.count(r'\{')
        close_curlies = formula.count('}') - formula.count(r'\}')
        if open_curlies > close_curlies:
            formula = formula + ('}' * (open_curlies - close_curlies))
        elif close_curlies > open_curlies:
            formula = ('{' * (close_curlies - open_curlies)) + formula

        # Balance \left and \right
        lefts = len(re.findall(r'\\left\b', formula))
        rights = len(re.findall(r'\\right\b', formula))
        if lefts > rights:
            formula = formula + (r'\right.' * (lefts - rights))
        elif rights > lefts:
            formula = (r'\left.' * (rights - lefts)) + formula

        return formula

    def fix_inline(m: re.Match) -> str:
        content = m.group(1)
        return f"${balance_formula_brackets(content)}$"

    def fix_display(m: re.Match) -> str:
        content = m.group(1)
        return f"$${balance_formula_brackets(content)}$$"

    result = re.sub(r'\$\$(.*?)\$\$', fix_display, result, flags=re.DOTALL)
    result = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', fix_inline, result, flags=re.DOTALL)

    return result


def validate_katex(latex_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate whether a LaTeX formula string can be rendered by KaTeX.
    Returns:
        (is_valid: bool, error_message: str | None)
    """
    if not latex_str or not latex_str.strip():
        return True, None

    raw = latex_str.strip()
    # Strip wrapping delimiters if present
    if raw.startswith("$$") and raw.endswith("$$") and len(raw) >= 4:
        raw = raw[2:-2].strip()
    elif raw.startswith("$") and raw.endswith("$") and len(raw) >= 2:
        raw = raw[1:-1].strip()

    # 1. Balanced curly braces check
    open_curlies = raw.count('{') - raw.count(r'\{')
    close_curlies = raw.count('}') - raw.count(r'\}')
    if open_curlies != close_curlies:
        return False, f"Unbalanced curly braces: {open_curlies} open vs {close_curlies} close"

    # 2. Balanced \left and \right
    lefts = len(re.findall(r'\\left\b', raw))
    rights = len(re.findall(r'\\right\b', raw))
    if lefts != rights:
        return False, f"Mismatched \\left and \\right delimiters ({lefts} vs {rights})"

    # 3. Balanced environments \begin{env} ... \end{env}
    begins = re.findall(r'\\begin\{([a-zA-Z0-9*]+)\}', raw)
    ends = re.findall(r'\\end\{([a-zA-Z0-9*]+)\}', raw)
    if begins != ends:
        return False, f"Mismatched LaTeX environments: \\begin{{{begins}}} vs \\end{{{ends}}}"

    # 4. Check for invalid or unescaped characters
    # Isolated trailing backslash
    if raw.endswith('\\') and not raw.endswith(r'\\'):
        return False, "Trailing isolated backslash in LaTeX string"

    # 5. Try latex2mathml if available
    if HAS_LATEX2MATHML:
        try:
            # We wrap with simple math
            latex2mathml.converter.convert(raw)
        except Exception as e:
            # If latex2mathml fails, check if it's a fatal syntax error
            err_msg = str(e)
            return False, f"KaTeX/MathML parse error: {err_msg}"

    return True, None


# ---------------------------------------------------------------------------
# 4. OMML (Office Math Markup Language) to LaTeX Converter
# ---------------------------------------------------------------------------

OMML_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class OMML2LaTeX:
    """
    Converts Word native OMML (<m:oMath>, <m:oMathPara>) elements into clean LaTeX.
    """

    @classmethod
    def convert(cls, element: ET.Element) -> str:
        tag = element.tag.replace(OMML_NS, "").replace(W_NS, "")
        latex_parts: List[str] = []

        if tag in ("oMath", "oMathPara"):
            for child in element:
                latex_parts.append(cls.convert(child))
            res = "".join(latex_parts).strip()
            return res

        elif tag == "r":
            # Run of text
            for child in element:
                ctag = child.tag.replace(OMML_NS, "").replace(W_NS, "")
                if ctag == "t":
                    txt = child.text or ""
                    # Handle symbols in text run
                    latex_parts.append(cls._sanitize_run_text(txt))
            return "".join(latex_parts)

        elif tag == "f":
            # Fraction: num / den
            num = ""
            den = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "num":
                    num = "".join(cls.convert(c) for c in child)
                elif ctag == "den":
                    den = "".join(cls.convert(c) for c in child)
            return rf"\frac{{{num.strip()}}}{{{den.strip()}}}"

        elif tag == "sSup":
            # Superscript: base^sup
            base = ""
            sup = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "e":
                    base = "".join(cls.convert(c) for c in child)
                elif ctag == "sup":
                    sup = "".join(cls.convert(c) for c in child)
            return f"{{{base.strip()}}}^{{{sup.strip()}}}"

        elif tag == "sSub":
            # Subscript: base_sub
            base = ""
            sub = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "e":
                    base = "".join(cls.convert(c) for c in child)
                elif ctag == "sub":
                    sub = "".join(cls.convert(c) for c in child)
            return f"{{{base.strip()}}}_{{{sub.strip()}}}"

        elif tag == "sSubSup":
            # Subscript and Superscript: base_sub^sup
            base = ""
            sub = ""
            sup = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "e":
                    base = "".join(cls.convert(c) for c in child)
                elif ctag == "sub":
                    sub = "".join(cls.convert(c) for c in child)
                elif ctag == "sup":
                    sup = "".join(cls.convert(c) for c in child)
            return f"{{{base.strip()}}}_{{{sub.strip()}}}^{{{sup.strip()}}}"

        elif tag == "rad":
            # Radical / Square root
            deg = ""
            e_val = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "deg":
                    deg = "".join(cls.convert(c) for c in child).strip()
                elif ctag == "e":
                    e_val = "".join(cls.convert(c) for c in child).strip()
            if deg:
                return rf"\sqrt[{deg}]{{{e_val}}}"
            return rf"\sqrt{{{e_val}}}"

        elif tag == "nary":
            # Integrals, Summations, Products
            op = r"\int"
            sub = ""
            sup = ""
            e_val = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "naryPr":
                    chr_elem = child.find(f"{OMML_NS}chr")
                    if chr_elem is not None:
                        val = chr_elem.attrib.get(f"{OMML_NS}val", "∫")
                        if val == "∑":
                            op = r"\sum"
                        elif val == "∏":
                            op = r"\prod"
                        elif val == "∬":
                            op = r"\iint"
                        elif val == "∮":
                            op = r"\oint"
                        elif val == "∫":
                            op = r"\int"
                elif ctag == "sub":
                    sub = "".join(cls.convert(c) for c in child).strip()
                elif ctag == "sup":
                    sup = "".join(cls.convert(c) for c in child).strip()
                elif ctag == "e":
                    e_val = "".join(cls.convert(c) for c in child).strip()

            lims = ""
            if sub and sup:
                lims = f"_{{{sub}}}^{{{sup}}}"
            elif sub:
                lims = f"_{{{sub}}}"
            elif sup:
                lims = f"^{{{sup}}}"

            return f"{op}{lims} {e_val}"

        elif tag == "d":
            # Delimiters (brackets, parentheses, abs)
            beg_chr = "("
            end_chr = ")"
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "dPr":
                    beg_elem = child.find(f"{OMML_NS}begChr")
                    if beg_elem is not None:
                        beg_chr = beg_elem.attrib.get(f"{OMML_NS}val", "(")
                    end_elem = child.find(f"{OMML_NS}endChr")
                    if end_elem is not None:
                        end_chr = end_elem.attrib.get(f"{OMML_NS}val", ")")

            inner_content = []
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "e":
                    inner_content.append("".join(cls.convert(c) for c in child))

            inner_str = " ".join(inner_content).strip()

            # Map delimiter characters to LaTeX
            left_map = {"(": r"\left(", "[": r"\left[", "{": r"\left\{", "|": r"\left|", "": r"\left."}
            right_map = {")": r"\right)", "]": r"\right]", "}": r"\right\}", "|": r"\right|", "": r"\right."}

            l_delim = left_map.get(beg_chr, rf"\left{beg_chr}")
            r_delim = right_map.get(end_chr, rf"\right{end_chr}")
            return f"{l_delim} {inner_str} {r_delim}"

        elif tag == "m":
            # Matrix
            rows = []
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "mr":
                    cols = []
                    for c_e in child:
                        if c_e.tag.replace(OMML_NS, "") == "e":
                            cols.append("".join(cls.convert(c) for c in c_e).strip())
                    rows.append(" & ".join(cols))
            matrix_body = " \\\\ \n".join(rows)
            return f"\\begin{{matrix}}\n{matrix_body}\n\\end{{matrix}}"

        elif tag in ("bar", "acc"):
            # Overline / vector
            val = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "e":
                    val = "".join(cls.convert(c) for c in child).strip()
            if tag == "bar":
                return rf"\overline{{{val}}}"
            return rf"\vec{{{val}}}"

        elif tag in ("limLow", "func"):
            # Limit or math function
            f_name = r"\lim"
            lim_val = ""
            e_val = ""
            for child in element:
                ctag = child.tag.replace(OMML_NS, "")
                if ctag == "fName":
                    f_name = "".join(cls.convert(c) for c in child).strip()
                elif ctag == "lim":
                    lim_val = "".join(cls.convert(c) for c in child).strip()
                elif ctag == "e":
                    e_val = "".join(cls.convert(c) for c in child).strip()

            if lim_val:
                return rf"{f_name}_{{{lim_val}}} {e_val}"
            return rf"{f_name}{e_val}"

        else:
            # Fallback: recurse into children
            for child in element:
                latex_parts.append(cls.convert(child))
            return "".join(latex_parts)

    @classmethod
    def _sanitize_run_text(cls, txt: str) -> str:
        for u_char, tex in UNICODE_MATH_MAP.items():
            if u_char in txt:
                txt = txt.replace(u_char, f" {tex} ")
        return txt


def convert_omml_to_latex(omml_input: Union[str, ET.Element]) -> str:
    """
    Convert an OMML XML string or ElementTree Element into a clean LaTeX expression.
    """
    if isinstance(omml_input, str):
        # Remove default namespace prefixes if needed or parse with namespaces
        root = ET.fromstring(omml_input)
    else:
        root = omml_input

    res = OMML2LaTeX.convert(root)
    return sanitize_latex(f"${res}$")


# ---------------------------------------------------------------------------
# 5. MathType MTEF Binary Parser
# ---------------------------------------------------------------------------

class MTEFParser:
    """
    Decoder for MathType Equation Format (MTEF) streams version 3 and 5.
    Converts MTEF binary records into standard LaTeX.
    """

    RECORD_END = 0
    RECORD_LINE = 1
    RECORD_CHAR = 2
    RECORD_TMPL = 3
    RECORD_PILE = 4
    RECORD_MATRIX = 5
    RECORD_EMBEL = 6
    RECORD_RULER = 7
    RECORD_FONT = 8
    RECORD_COLOR = 9

    # Template selector codes
    TM_ROOT = 5
    TM_FRACT = 6
    TM_UBAR = 7
    TM_OBAR = 8
    TM_ARROW = 9
    TM_INTEG = 10
    TM_SUM = 11
    TM_PROD = 12
    TM_COPROD = 13
    TM_UNION = 14
    TM_INTER = 15
    TM_SUP = 16
    TM_SUB = 17
    TM_SUBSUP = 18
    TM_LIM = 19
    TM_BOX = 20
    TM_PAREN = 1
    TM_BRACE = 2
    TM_BRACK = 3
    TM_BAR = 4

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.version = 5
        self.platform = 1
        self.product = 0

    def parse(self) -> str:
        if len(self.data) < 5:
            return ""

        # Parse MTEF Header
        self.version = self.data[self.pos]
        self.platform = self.data[self.pos + 1]
        self.product = self.data[self.pos + 2]
        self.pos += 5

        # Process top-level records until end
        output: List[str] = []
        while self.pos < len(self.data):
            rec = self._parse_record()
            if rec:
                output.append(rec)
        return "".join(output).strip()

    def _read_byte(self) -> int:
        if self.pos >= len(self.data):
            return 0
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _read_uint16(self) -> int:
        if self.pos + 2 > len(self.data):
            self.pos = len(self.data)
            return 0
        val = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return val

    def _read_null_string(self) -> str:
        start = self.pos
        while self.pos < len(self.data) and self.data[self.pos] != 0:
            self.pos += 1
        s = self.data[start:self.pos].decode("latin-1", errors="ignore")
        if self.pos < len(self.data) and self.data[self.pos] == 0:
            self.pos += 1
        return s

    def _parse_record(self) -> str:
        if self.pos >= len(self.data):
            return ""

        tag_byte = self._read_byte()
        rec_type = tag_byte & 0x0F
        options = tag_byte >> 4

        if rec_type == self.RECORD_END:
            return ""

        elif rec_type == self.RECORD_LINE:
            # LINE options
            # If line has nudge (0x08), skip dx, dy
            if options & 0x08:
                self.pos += 2  # dx, dy
            # If null line (0x01)
            if options & 0x01:
                return ""

            parts: List[str] = []
            while self.pos < len(self.data):
                if self.data[self.pos] & 0x0F == self.RECORD_END:
                    self._read_byte()  # consume END
                    break
                rec_val = self._parse_record()
                if rec_val:
                    parts.append(rec_val)
            return "".join(parts)

        elif rec_type == self.RECORD_CHAR:
            # CHAR options, font position, character code
            font_pos = self._read_byte()
            if self.version >= 5:
                char_val = self._read_uint16()
            else:
                char_val = self._read_byte()

            # Embellishments
            embel_str = ""
            if options & 0x01:
                while self.pos < len(self.data):
                    emb = self._read_byte()
                    if emb == 0:
                        break
                    if emb == 1:
                        embel_str += "'"
                    elif emb == 2:
                        embel_str += "''"
                    elif emb == 5:
                        embel_str = r"\bar"
                    elif emb == 6:
                        embel_str = r"\vec"

            char_str = self._char_to_latex(char_val)
            if embel_str:
                if embel_str.startswith("\\"):
                    return f"{embel_str}{{{char_str}}}"
                return f"{char_str}{embel_str}"
            return char_str

        elif rec_type == self.RECORD_TMPL:
            # Template record
            selector = self._read_byte()
            variation = self._read_uint16()
            return self._parse_template(selector, variation)

        elif rec_type == self.RECORD_PILE:
            parts = []
            while self.pos < len(self.data):
                if self.data[self.pos] & 0x0F == self.RECORD_END:
                    self._read_byte()
                    break
                rec_val = self._parse_record()
                if rec_val:
                    parts.append(rec_val)
            return " \\\\ ".join(parts)

        elif rec_type == self.RECORD_MATRIX:
            rows = self._read_byte()
            cols = self._read_byte()
            cells = []
            while self.pos < len(self.data):
                if self.data[self.pos] & 0x0F == self.RECORD_END:
                    self._read_byte()
                    break
                rec_val = self._parse_record()
                if rec_val:
                    cells.append(rec_val)
            return "\\begin{matrix} " + " & ".join(cells) + " \\end{matrix}"

        elif rec_type == self.RECORD_FONT:
            self._read_byte()  # font def
            self._read_null_string()  # font name
            return ""

        elif rec_type == self.RECORD_COLOR:
            self._read_byte()
            return ""

        elif rec_type == self.RECORD_RULER:
            n_stops = self._read_byte()
            self.pos += n_stops * 3
            return ""

        return ""

    def _parse_template(self, selector: int, variation: int) -> str:
        lines: List[str] = []
        while self.pos < len(self.data):
            if self.data[self.pos] & 0x0F == self.RECORD_END:
                self._read_byte()
                break
            rec_val = self._parse_record()
            lines.append(rec_val)

        if selector == self.TM_ROOT:
            if len(lines) >= 2 and variation != 0:
                return rf"\sqrt[{lines[0]}]{{{lines[1]}}}"
            arg = lines[0] if lines else ""
            return rf"\sqrt{{{arg}}}"

        elif selector == self.TM_FRACT:
            num = lines[0] if len(lines) > 0 else ""
            den = lines[1] if len(lines) > 1 else ""
            return rf"\frac{{{num}}}{{{den}}}"

        elif selector == self.TM_SUP:
            sup = lines[0] if lines else ""
            return f"^{{{sup}}}"

        elif selector == self.TM_SUB:
            sub = lines[0] if lines else ""
            return f"_{{{sub}}}"

        elif selector == self.TM_SUBSUP:
            sub = lines[0] if len(lines) > 0 else ""
            sup = lines[1] if len(lines) > 1 else ""
            return f"_{{{sub}}}^{{{sup}}}"

        elif selector == self.TM_INTEG:
            low = lines[0] if len(lines) > 0 else ""
            upp = lines[1] if len(lines) > 1 else ""
            integrand = lines[2] if len(lines) > 2 else ""
            if low and upp:
                return rf"\int_{{{low}}}^{{{upp}}} {{{integrand}}}"
            return rf"\int {{{integrand}}}"

        elif selector == self.TM_SUM:
            low = lines[0] if len(lines) > 0 else ""
            upp = lines[1] if len(lines) > 1 else ""
            arg = lines[2] if len(lines) > 2 else ""
            return rf"\sum_{{{low}}}^{{{upp}}} {{{arg}}}"

        elif selector == self.TM_PROD:
            low = lines[0] if len(lines) > 0 else ""
            upp = lines[1] if len(lines) > 1 else ""
            arg = lines[2] if len(lines) > 2 else ""
            return rf"\prod_{{{low}}}^{{{upp}}} {{{arg}}}"

        elif selector == self.TM_PAREN:
            inner = lines[0] if lines else ""
            return rf"\left( {inner} \right)"

        elif selector == self.TM_BRACK:
            inner = lines[0] if lines else ""
            return rf"\left[ {inner} \right]"

        elif selector == self.TM_BRACE:
            inner = lines[0] if lines else ""
            return rf"\left\{{ {inner} \right\}}"

        elif selector == self.TM_BAR:
            inner = lines[0] if lines else ""
            return rf"\left| {inner} \right|"

        elif selector == self.TM_ARROW:
            inner = lines[0] if lines else ""
            return rf"\vec{{{inner}}}"

        elif selector == self.TM_OBAR:
            inner = lines[0] if lines else ""
            return rf"\overline{{{inner}}}"

        elif selector == self.TM_UBAR:
            inner = lines[0] if lines else ""
            return rf"\underline{{{inner}}}"

        elif selector == self.TM_LIM:
            target = lines[0] if len(lines) > 0 else ""
            expr = lines[1] if len(lines) > 1 else ""
            return rf"\lim_{{{target}}} {{{expr}}}"

        elif selector == self.TM_BOX:
            inner = lines[0] if lines else ""
            return f"{{{inner}}}"

        # Default fallback: concatenate sub-lines
        return " ".join(lines)

    def _char_to_latex(self, char_code: int) -> str:
        # Standard ASCII
        if 0x20 <= char_code <= 0x7E:
            ch = chr(char_code)
            if ch == '\\':
                return r"\backslash "
            elif ch in ('{', '}'):
                return rf"\{ch}"
            return ch

        # Common unicode symbols
        code_map = {
            0x00B1: r"\pm ",
            0x2213: r"\mp ",
            0x00D7: r"\times ",
            0x00F7: r"\div ",
            0x2264: r"\le ",
            0x2265: r"\ge ",
            0x2260: r"\ne ",
            0x2248: r"\approx ",
            0x221E: r"\infty ",
            0x2208: r"\in ",
            0x2209: r"\notin ",
            0x2282: r"\subset ",
            0x2283: r"\supset ",
            0x222A: r"\cup ",
            0x2229: r"\cap ",
            0x2205: r"\emptyset ",
            0x2192: r"\rightarrow ",
            0x21D2: r"\Rightarrow ",
            0x21D4: r"\Leftrightarrow ",
            0x2212: "-",
            0x03C0: r"\pi ",
            0x03B1: r"\alpha ",
            0x03B2: r"\beta ",
            0x03B3: r"\gamma ",
            0x03B4: r"\delta ",
            0x03B8: r"\theta ",
            0x03BB: r"\lambda ",
            0x03BC: r"\mu ",
            0x03C3: r"\sigma ",
            0x03C9: r"\omega ",
            0x0394: r"\Delta ",
            0x211D: r"\mathbb{R}",
            0x2124: r"\mathbb{Z}",
            0x2115: r"\mathbb{N}",
            0x211A: r"\mathbb{Q}",
            0x2102: r"\mathbb{C}",
        }
        if char_code in code_map:
            return code_map[char_code]

        try:
            return chr(char_code)
        except (ValueError, OverflowError):
            return ""


def decode_mtef(mtef_bytes: bytes) -> str:
    """
    Search and decode MathType MTEF stream from raw OLE binary bytes.
    Returns clean LaTeX string surrounded by $...$.
    """
    if not mtef_bytes:
        return ""

    # MathType MTEF header signatures:
    # Version 3, 5, or 2; Windows (1) or Mac (0); Product (1 or 0)
    signatures = [
        b"\x05\x01\x01",
        b"\x03\x01\x01",
        b"\x05\x01\x00",
        b"\x03\x01\x00",
        b"\x02\x01\x01",
    ]

    mtef_slice = None
    for sig in signatures:
        idx = mtef_bytes.find(sig)
        if idx != -1:
            mtef_slice = mtef_bytes[idx:]
            break

    # If no header signature found, check if it has a 28-byte OLE equation native header
    if mtef_slice is None and len(mtef_bytes) > 28:
        # Check at offset 28
        for sig in signatures:
            if mtef_bytes[28:31] == sig:
                mtef_slice = mtef_bytes[28:]
                break

    if not mtef_slice:
        return ""

    parser = MTEFParser(mtef_slice)
    latex_result = parser.parse()
    if latex_result:
        return sanitize_latex(f"${latex_result}$")
    return ""


def extract_mathtype_from_docx(docx_file: Union[str, bytes, io.BytesIO]) -> Dict[str, str]:
    """
    Extracts all MathType OLE binary objects from a DOCX zip archive and decodes them to LaTeX formulas.
    Returns:
        Dict mapping part name (e.g. 'word/embeddings/oleObject1.bin') to decoded LaTeX '$...$'.
    """
    results: Dict[str, str] = {}
    zf = zipfile.ZipFile(docx_file) if not isinstance(docx_file, zipfile.ZipFile) else docx_file

    for name in zf.namelist():
        if name.startswith("word/embeddings/") and (name.endswith(".bin") or name.endswith(".ole")):
            raw_data = zf.read(name)
            formula_tex = decode_mtef(raw_data)
            if formula_tex:
                results[name] = formula_tex

    return results


# ---------------------------------------------------------------------------
# 6. Complete DOCX Content Extractor with Math & Layout
# ---------------------------------------------------------------------------

def extract_and_convert_docx_content(docx_path: str) -> str:
    """
    Reads a DOCX file, converts all OMML math equations and MathType OLE objects to LaTeX,
    and returns a structured Markdown string preserving document flow.
    """
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"File not found: {docx_path}")

    with zipfile.ZipFile(docx_path, "r") as zf:
        # 1. Decode MathType OLE embeddings
        mathtype_map = extract_mathtype_from_docx(zf)

        # 2. Parse relationships to map rId -> target embedding
        rid_to_embedding: Dict[str, str] = {}
        if "word/_rels/document.xml.rels" in zf.namelist():
            rels_xml = zf.read("word/_rels/document.xml.rels")
            rels_root = ET.fromstring(rels_xml)
            for rel in rels_root:
                r_id = rel.attrib.get("Id")
                target = rel.attrib.get("Target", "")
                if target:
                    # Normalize target path
                    clean_target = "word/" + target.lstrip("/") if not target.startswith("word/") else target
                    rid_to_embedding[r_id] = clean_target

        # 3. Read word/document.xml
        doc_xml = zf.read("word/document.xml")
        root = ET.fromstring(doc_xml)

    lines: List[str] = []

    # Iterate through paragraphs and tables
    body = root.find(f"{W_NS}body")
    if body is None:
        return ""

    for elem in body:
        tag = elem.tag.replace(W_NS, "")
        if tag == "p":
            para_text = _extract_paragraph_with_math(elem, rid_to_embedding, mathtype_map)
            if para_text.strip():
                lines.append(para_text.strip())
        elif tag == "tbl":
            # Table conversion
            tbl_lines = _extract_table_with_math(elem, rid_to_embedding, mathtype_map)
            if tbl_lines:
                lines.extend(tbl_lines)

    full_text = "\n\n".join(lines)
    return sanitize_latex(full_text)


def _extract_paragraph_with_math(
    p_elem: ET.Element,
    rid_map: Dict[str, str],
    mathtype_map: Dict[str, str]
) -> str:
    """Extracts text, inline OMML math, display OMML math, and MathType equations from a paragraph."""
    parts: List[str] = []

    for child in p_elem:
        child_tag = child.tag

        # OMML inline equation
        if child_tag == f"{OMML_NS}oMath":
            tex = OMML2LaTeX.convert(child)
            if tex.strip():
                parts.append(f" ${tex.strip()}$ ")

        # OMML display equation
        elif child_tag == f"{OMML_NS}oMathPara":
            tex = OMML2LaTeX.convert(child)
            if tex.strip():
                parts.append(f"\n\n$${tex.strip()}$$\n\n")

        # Word Run <w:r>
        elif child_tag == f"{W_NS}r":
            # Check for embedded drawing or OLE object
            ole_tex = _find_ole_in_run(child, rid_map, mathtype_map)
            if ole_tex:
                parts.append(f" {ole_tex} ")
            else:
                for c in child:
                    ctag = c.tag.replace(W_NS, "")
                    if ctag == "t":
                        parts.append(c.text or "")
                    elif ctag == "br":
                        parts.append("\n")

        # Direct drawing or object
        elif child_tag in (f"{W_NS}drawing", f"{W_NS}object"):
            ole_tex = _find_ole_in_element(child, rid_map, mathtype_map)
            if ole_tex:
                parts.append(f" {ole_tex} ")

    return "".join(parts)


def _extract_table_with_math(
    tbl_elem: ET.Element,
    rid_map: Dict[str, str],
    mathtype_map: Dict[str, str]
) -> List[str]:
    """Converts a Word table to Markdown table lines."""
    rows: List[List[str]] = []
    for tr in tbl_elem.findall(f"{W_NS}tr"):
        row_cells: List[str] = []
        for tc in tr.findall(f"{W_NS}tc"):
            cell_texts = []
            for p in tc.findall(f"{W_NS}p"):
                txt = _extract_paragraph_with_math(p, rid_map, mathtype_map)
                if txt.strip():
                    cell_texts.append(txt.strip())
            row_cells.append(" ".join(cell_texts).replace("\n", " ").replace("|", "/"))
        rows.append(row_cells)

    if not rows:
        return []

    # Format as Markdown table
    col_count = max(len(r) for r in rows) if rows else 0
    if col_count == 0:
        return []

    # Normalize row lengths
    for r in rows:
        while len(r) < col_count:
            r.append("")

    table_lines: List[str] = []
    # Header
    table_lines.append("| " + " | ".join(rows[0]) + " |")
    table_lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for r in rows[1:]:
        table_lines.append("| " + " | ".join(r) + " |")

    return table_lines


def _find_ole_in_run(
    r_elem: ET.Element,
    rid_map: Dict[str, str],
    mathtype_map: Dict[str, str]
) -> Optional[str]:
    for obj in r_elem.iter():
        tag = obj.tag.split("}")[-1]
        if tag in ("OLEObject", "object"):
            r_id = obj.attrib.get(f"{{{W_NS.rstrip('}')}}}id") or obj.attrib.get(
                "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
            )
            if r_id and r_id in rid_map:
                target = rid_map[r_id]
                if target in mathtype_map:
                    return mathtype_map[target]
    return None


def _find_ole_in_element(
    elem: ET.Element,
    rid_map: Dict[str, str],
    mathtype_map: Dict[str, str]
) -> Optional[str]:
    return _find_ole_in_run(elem, rid_map, mathtype_map)
