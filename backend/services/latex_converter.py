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

import logging
import io
import os
import re
import struct
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("quesy.latex_converter")

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
# 1.5 Variation Table Array to Native TikZ tkz-tab Converter
# ---------------------------------------------------------------------------

def convert_variation_array_to_tkz_tab(text: str) -> str:
    """Converts legacy \\begin{array} variation tables into native TikZ tkz-tab code."""
    if not text or (r"\nearrow" not in text and r"\searrow" not in text):
        return text

    pattern = re.compile(
        r'(?:\$\$\s*)?\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?(.*?)\\end\{(?:array|tabular)\}(?:\s*\$\$)?',
        re.DOTALL
    )

    def _convert_match(m):
        full_match = m.group(0)
        body = m.group(1).strip()
        if not any(k in body for k in (r"\nearrow", r"\searrow", r"\infty", r"f'", r"y'")):
            return full_match

        raw_lines = [l.strip() for l in body.split(r'\\')]
        lines = []
        for l in raw_lines:
            cleaned = re.sub(r'\\hline', '', l).strip()
            if cleaned:
                lines.append(cleaned)

        if len(lines) < 2:
            return full_match

        grid = []
        for l in lines:
            cells = [c.strip() for c in l.split('&')]
            grid.append(cells)

        # 1. Row 0: x values
        row_x = grid[0]
        nodes_x = []
        for c in row_x[1:]:
            clean_c = c.replace('$', '').strip()
            if clean_c:
                nodes_x.append(clean_c)

        if not nodes_x:
            return full_match

        std_nodes_x = []
        for nx in nodes_x:
            if not nx.startswith('$'):
                std_nodes_x.append(f"${nx}$")
            else:
                std_nodes_x.append(nx)

        lbl_x = "$x$"
        lbl_fprime = "$f'(x)$"
        lbl_f = "$f(x)$"

        raw_lbl_0 = row_x[0].replace('$', '').strip()
        if raw_lbl_0:
            if 'x' in raw_lbl_0:
                lbl_x = "$x$"
            else:
                lbl_x = f"${raw_lbl_0}$"

        has_derivative_row = False
        signs = []
        if len(grid) >= 2:
            row_1 = grid[1]
            raw_lbl_1 = row_1[0].replace('$', '').strip()
            if any(k in raw_lbl_1 for k in ("f'", "y'", "g'")):
                has_derivative_row = True
                if "f'" in raw_lbl_1:
                    lbl_fprime = "$f'(x)$"
                elif "y'" in raw_lbl_1:
                    lbl_fprime = "$y'$"
                elif "g'" in raw_lbl_1:
                    lbl_fprime = "$g'(x)$"
                for c in row_1[1:]:
                    clean_c = c.replace('$', '').strip()
                    if clean_c in ('+', '-', '0', 'd', 'z', 't', '|', '||', r'\Vert'):
                        if clean_c in ('|', '||', r'\Vert'):
                            signs.append('d')
                        else:
                            signs.append(clean_c)
                    elif clean_c:
                        signs.append(clean_c)

        var_row_start = 2 if has_derivative_row else 1
        var_rows = grid[var_row_start:]
        has_asymptote = any(r'\Vert' in l or '||' in l for l in lines)

        n_nodes = len(nodes_x)
        node_values = {}
        node_asymptote_vals = {}

        for r_idx, row in enumerate(var_rows):
            cells = row[1:]
            for c_idx, cell in enumerate(cells):
                clean_c = cell.replace('$', '').strip()
                if not clean_c or clean_c in (r'\nearrow', r'\searrow', r'\Vert', '||', '|', 'f(x)', 'y', r"f'(x)", r"y'"):
                    continue

                total_cols = len(cells)
                if total_cols >= 2 * n_nodes - 1:
                    node_idx = round(c_idx / 2)
                else:
                    node_idx = round(c_idx * (n_nodes - 1) / max(1, total_cols - 1))

                node_idx = max(0, min(n_nodes - 1, node_idx))
                is_upper = (r_idx == 0 or (r_idx == 1 and '+\\infty' in clean_c))

                if node_idx not in node_values:
                    node_values[node_idx] = (clean_c, is_upper)
                else:
                    prev_val, prev_up = node_values[node_idx]
                    node_asymptote_vals[node_idx] = (prev_val, clean_c)

        tab_vars = []
        for i in range(n_nodes):
            if i in node_asymptote_vals:
                v1, v2 = node_asymptote_vals[i]
                tab_vars.append(f"+D-/${v1}$/${v2}$")
            elif i in node_values:
                val, is_up = node_values[i]
                prefix = "+" if is_up else "-"
                tab_vars.append(f"{prefix}/${val}$")
            else:
                prefix = "+" if (i % 2 == 1) else "-"
                tab_vars.append(f"{prefix}/$ $")

        valid_signs = [s for s in signs if s in ('+', '-', '0', 'd', 'z', 't')]
        if len(valid_signs) >= 3:
            line_str = ",".join(valid_signs)
            if not line_str.startswith(','): line_str = ',' + line_str
            if not line_str.endswith(','): line_str = line_str + ','
        else:
            if n_nodes == 4:
                line_str = ",+,0,-,0,+,"
            elif n_nodes == 3:
                line_str = ",-,0,+,"
            elif n_nodes == 5:
                line_str = ",-,0,+,0,-,0,+,"
            else:
                line_str = ",+,0,-,"

        var_str = ",".join(tab_vars)

        opt_style = ""
        if has_asymptote:
            opt_style = "  \\tikzset{double style/.append style = {double distance=2.5pt}}\n"

        tkz = (
            "\n\n\\begin{tikzpicture}\n"
            f"{opt_style}"
            "  \\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]\n"
            f"  {{{lbl_x}/.6, {lbl_fprime}/.6, {lbl_f}/2}}\n"
            f"  {{{','.join(std_nodes_x)}}}\n"
            f"  \\tkzTabLine{{{line_str}}}\n"
            f"  \\tkzTabVar{{{var_str}}}\n"
            "\\end{tikzpicture}\n\n"
        )
        return tkz

    return pattern.sub(_convert_match, text)


def clean_variation_array(latex_str: str) -> str:
    """Normalizes variation table array column specifications.
    Removes outer vertical bars | and rogue internal bars between interval values,
    leaving strictly ONE vertical divider after the first label column (e.g. c|ccccccc).
    """
    def _clean_cols(m):
        col_spec = m.group(1).strip()
        body = m.group(2)
        if any(sym in body for sym in (r"\nearrow", r"\searrow", r"-\infty", r"+\infty", r"\infty", r"f'", r"y'")):
            pure_cols = col_spec.replace("|", "").strip()
            norm_col = pure_cols[0] + "|" + pure_cols[1:] if pure_cols else "c|ccccccc"
            return f"\\begin{{array}}{{{norm_col}}}{body}\\end{{array}}"
        return m.group(0)

    return re.sub(r'\\begin\{array\}\{([^}]+)\}([\s\S]*?)\\end\{array\}', _clean_cols, latex_str)


# ---------------------------------------------------------------------------
# 2. LaTeX Sanitization & Normalization
# ---------------------------------------------------------------------------

def sanitize_latex(text: str) -> str:
    """
    Sanitize and normalize LaTeX formulas and surrounding Vietnamese educational text.
    - Standardizes inline delimiters to $...$ and block delimiters to $$...$$.\n    - Replaces unicode math symbols with standard LaTeX macros.\n    - Normalizes unicode superscripts/subscripts.\n    - Automatically adds backslashes to standard math functions (sin, cos, ln, lim, etc.).\n    - Fixes malformed commands and delimiter spacing.\n    """
    if not text:
        return ""

    s = text

    # -1. Automatically convert any legacy/AI \\begin{array} variation table into native TikZ tkz-tab
    s = convert_variation_array_to_tkz_tab(s)

    # 0. Clean off any redundant \begin{center} and \end{center} tags
    s = re.sub(r'\\+(?:begin|end)\{center\}', '', s)

    # 0. Extract and protect any \begin{tikzpicture} ... \end{tikzpicture} blocks
    # TikZ code contains drawing commands and coordinates that must NOT be altered by math rules
    tikz_blocks = []
    def _protect_tikz(m):
        raw_tikz = m.group(0).strip()
        # Clean off any outer $$ if accidentally wrapped around tikzpicture
        raw_tikz = re.sub(r'^\$\$?', '', raw_tikz).strip()
        raw_tikz = re.sub(r'\$\$?$', '', raw_tikz).strip()
        raw_tikz = re.sub(r'\\+(?:begin|end)\{center\}', '', raw_tikz).strip()
        tikz_blocks.append(raw_tikz)
        return f"__LATEX_TIKZ_BLOCK_{len(tikz_blocks) - 1}__"

    s = re.sub(r'\\?\$*\s*\\+begin\{tikzpicture\}[\s\S]*?\\+end\{tikzpicture\}\s*\\?\$*', _protect_tikz, s)

    # 1. Normalize block delimiters \[ ... \] to $$ ... $$
    s = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', s, flags=re.DOTALL)

    # 2. Normalize inline delimiters \( ... \) to $ ... $
    s = re.sub(r'\\\((.*?)\\\)', r'$\1$', s, flags=re.DOTALL)

    # 3. Convert tabular to array and auto-wrap / auto-close array environments with $$
    s = re.sub(r'\\begin\{tabular\}\s*(\{[^{}]*\})', r'$$\\begin{array}\1', s)
    s = re.sub(r'\\end\{tabular\}', r'\\end{array}$$', s)

    # Auto-close \begin{array}...\end{array} if opened with $$ but missing closing $$
    s = re.sub(
        r'(\$\$\s*\\begin\{(?:array|matrix|pmatrix|bmatrix|vmatrix|cases)\}[\s\S]*?\\end\{(?:array|matrix|pmatrix|bmatrix|vmatrix|cases)\})(?!\s*\$\$)',
        lambda m: m.group(1) + '$$',
        s
    )

    # Auto-wrap \begin{array}...\end{array} if not wrapped in $$ at all
    s = re.sub(
        r'(?<!\$)\\begin\{(array|matrix|pmatrix|bmatrix|vmatrix|cases)\}([\s\S]*?)\\end\{\1\}(?!\$)',
        lambda m: f"$${m.group(0)}$$",
        s
    )

    # 3.5 Normalize variation table array column specs: strip outer and rogue internal vertical bars '|'
    s = clean_variation_array(s)

    # 4. Handle unicode superscripts and subscripts outside or inside math
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

        # Normalize fractions \frac {a} {b} -> \dfrac{a}{b} (Rule: always \dfrac instead of \frac)
        res = re.sub(r'\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}', r'\\dfrac{\1}{\2}', res)
        res = re.sub(r'(?<![a-zA-Z])\\frac(?![a-zA-Z])', lambda m: r'\dfrac', res)

        # Standardize vectors: always \overrightarrow instead of \vec
        res = re.sub(r'\\vec\s*\{([^{}]+)\}', lambda m: rf'\overrightarrow{{{m.group(1)}}}', res)
        res = re.sub(r'\\vec\s*([a-zA-Z0-9])', lambda m: rf'\overrightarrow{{{m.group(1)}}}', res)
        res = re.sub(r'(?<![a-zA-Z])\\vec(?![a-zA-Z])', lambda m: r'\overrightarrow', res)

        # Standardize decimal numbers: write decimal commas as {,} (e.g. 15,25 -> 15{,}25)
        res = re.sub(r'(?<=\d)[\.,](?=\d)', '{,}', res)

        # Protect \text{...} from math bracket conversion (\left is illegal in text mode!)
        text_blocks = []
        def _protect_text_mode(m):
            inner = m.group(1)
            # Remove any \left / \right if accidentally present inside \text{}
            inner = re.sub(r'\\(?:left|right)\s*([()\[\]{}|.]?)', r'\1', inner)
            inner = re.sub(r'\\(?:left|right)\b', '', inner)
            text_blocks.append(inner)
            return f"__LATEX_TEXT_BLOCK_{len(text_blocks) - 1}__"

        res = re.sub(r'\\text\{([^{}]*)\}', _protect_text_mode, res)

        # Normalize excessive backslashes before curly braces (\+{ -> \{ and \+} -> \})
        res = re.sub(r'\\+([{}])', r'\\\1', res)

        # Standardize brackets: always \left and \right for (, ), [, ], \{, \}
        res = re.sub(r'\\sqrt\[([^\[\]]+)\]', r'__SQRT_ROOT_OPT_\1__', res)
        res = re.sub(r'\\left\s*\(', '__LEFT_PAREN__', res)
        res = re.sub(r'\\right\s*\)', '__RIGHT_PAREN__', res)
        res = re.sub(r'\\left\s*\[', '__LEFT_BRACKET__', res)
        res = re.sub(r'\\right\s*\]', '__RIGHT_BRACKET__', res)
        res = re.sub(r'\\left\s*\\\{', '__LEFT_BRACE__', res)
        res = re.sub(r'\\right\s*\\\}', '__RIGHT_BRACE__', res)
        res = re.sub(r'\\left\.', '__LEFT_DOT__', res)
        res = re.sub(r'\\right\.', '__RIGHT_DOT__', res)

        res = re.sub(r'\\\{', r'\\left\\{', res)
        res = re.sub(r'\\\}', r'\\right\\}', res)
        res = res.replace('(', r'\left(').replace(')', r'\right)')
        res = res.replace('[', r'\left[').replace(']', r'\right]')

        res = res.replace('__LEFT_PAREN__', r'\left(')
        res = res.replace('__RIGHT_PAREN__', r'\right)')
        res = res.replace('__LEFT_BRACKET__', r'\left[')
        res = res.replace('__RIGHT_BRACKET__', r'\right]')
        res = res.replace('__LEFT_BRACE__', r'\left\{')
        res = res.replace('__RIGHT_BRACE__', r'\right\}')
        res = res.replace('__LEFT_DOT__', r'\left.')
        res = res.replace('__RIGHT_DOT__', r'\right.')
        res = re.sub(r'__SQRT_ROOT_OPT_(.*?)__', r'\\sqrt[\1]', res)

        # Clean any accidental double \left or \right
        res = re.sub(r'(?:\\left\s*)+(\\left)', r'\1', res)
        res = re.sub(r'(?:\\right\s*)+(\\right)', r'\1', res)
        # Ensure single backslash before set braces \{ and \}
        res = re.sub(r'\\+([{}])', r'\\\1', res)

        # Restore \text{...}
        for idx, orig_text in enumerate(text_blocks):
            res = res.replace(f"__LATEX_TEXT_BLOCK_{idx}__", f"\\text{{{orig_text}}}")

        # Fix double backslashes that were accidentally escaped (except linebreaks \\)
        res = re.sub(r'\\\\([a-zA-Z]+)', r'\\\1', res)

        # Clean multiple spaces inside formula
        res = re.sub(r'[ \t]+', ' ', res).strip()
        return res

    # Process $$...$$ display math
    def replace_display(match: re.Match) -> str:
        content = match.group(1)
        cleaned = sanitize_math_content(content)
        # Flatten newlines inside display math to spaces so KaTeX text nodes remain unbroken across HTML breaks
        flattened = re.sub(r'\r?\n', ' ', cleaned)
        return f"$${flattened}$$"

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

    # 6. Merge adjacent inline $...$ $...$ (strictly without touching $$ display math)
    while True:
        new_s = re.sub(r'(?<!\$)\$([^$]+)\$(?!\$)\s*(?<!\$)\$([^$]+)\$(?!\$)', r'$\1 \2$', s)
        if new_s == s:
            break
        s = new_s

    # 7. Clean up redundant spaces around inline math delimiters only
    # Ensure space before inline $ if preceded by letter/number
    s = re.sub(r'([a-zA-Z0-9\u00C0-\u024F\u1EA0-\u1EF9])(?<!\$)\$(?!\$)', r'\1 $', s)
    # Ensure space after inline $ if followed by letter/number
    s = re.sub(r'(?<!\$)\$(?!\$)([a-zA-Z0-9\u00C0-\u024F\u1EA0-\u1EF9])', r'$ \1', s)

    # Re-normalize $$
    s = s.replace('$ $', '$$')
    s = re.sub(r'[ \t]{2,}', ' ', s)

    # Restore protected TikZ blocks
    for idx, raw_tikz in enumerate(tikz_blocks):
        s = s.replace(f"__LATEX_TIKZ_BLOCK_{idx}__", raw_tikz)

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

SYMBOL_GREEK_MAP = {
    ord('a'): r'\alpha', ord('b'): r'\beta', ord('g'): r'\gamma', ord('d'): r'\delta',
    ord('e'): r'\epsilon', ord('z'): r'\zeta', ord('h'): r'\eta', ord('q'): r'\theta',
    ord('i'): r'\iota', ord('k'): r'\kappa', ord('l'): r'\lambda', ord('m'): r'\mu',
    ord('n'): r'\nu', ord('x'): r'\xi', ord('p'): r'\pi', ord('r'): r'\rho',
    ord('s'): r'\sigma', ord('t'): r'\tau', ord('u'): r'\upsilon', ord('f'): r'\phi',
    ord('c'): r'\chi', ord('y'): r'\psi', ord('w'): r'\omega',
    ord('G'): r'\Gamma', ord('D'): r'\Delta', ord('Q'): r'\Theta',
    ord('L'): r'\Lambda', ord('X'): r'\Xi', ord('P'): r'\Pi',
    ord('S'): r'\Sigma', ord('F'): r'\Phi', ord('Y'): r'\Psi', ord('W'): r'\Omega',
    0xa3: r'\le ', 0xb3: r'\ge ', 0xb9: r'\ne ', 0xae: r'\rightarrow ',
    0xdb: r'\Leftrightarrow ', 0xde: r'\Rightarrow ', 0xc7: r'\cap ', 0xc8: r'\cup ',
    0xce: r'\in ', 0xcf: r'\notin ', 0xcc: r'\subset ', 0xcd: r'\supset ',
    0xc6: r'\emptyset ', 0xa5: r'\infty ', 0xb1: r'\pm ', 0xb0: r'^\circ ',
}


class MTEFParser:
    """Decoder for MathType Equation Format (MTEF) streams version 3 and 5.
    Converts MTEF binary records into standard clean LaTeX.
    """

    def __init__(self, data: bytes):
        self.data = data
        if len(data) > 28 and data[0] == 28 and data[1] == 0:
            self.data = data[28:]
        idx = -1
        for sig in [b"\x05\x01\x00", b"\x05\x01\x01", b"\x03\x01\x01", b"\x03\x01\x00", b"\x02\x01\x01"]:
            i = self.data.find(sig)
            if i != -1:
                idx = i
                break
        if idx != -1:
            self.data = self.data[idx:]
        self.pos = 0
        self.version = 5

    def parse(self) -> str:
        if len(self.data) < 5:
            return ""

        self.version = self.data[0]
        # Check if this is a simple/mock MTEF stream without DSMT header
        if self.data.find(b"\x0f\x0c") == -1 and (len(self.data) > 5 and self.data[5] in (1, 4)):
            return self._parse_simple()

        self.pos = 5
        # Skip null-terminated application key (e.g. "DSMT7\0")
        while self.pos < len(self.data) and self.data[self.pos] != 0:
            self.pos += 1
        self.pos += 1  # null byte
        if self.pos < len(self.data):
            self.pos += 1  # equation options byte

        if self.version >= 5:
            # Skip definition records until the equation body (LINE or PILE)
            while self.pos < len(self.data):
                tag = self.data[self.pos]
                if tag in (1, 4):  # Start of LINE or PILE
                    break
                self.pos += 1
                if tag == 19:  # ENCODING_DEF
                    while self.pos < len(self.data) and self.data[self.pos] != 0:
                        self.pos += 1
                    self.pos += 1
                elif tag == 17:  # FONT_DEF
                    self.pos += 1
                    while self.pos < len(self.data) and self.data[self.pos] != 0:
                        self.pos += 1
                    self.pos += 1
                elif tag == 18:  # EQN_PREFS
                    idx12 = self.data.find(b"\x0c", self.pos)
                    if idx12 != -1 and idx12 < self.pos + 120:
                        self.pos = idx12
                    else:
                        break
                elif tag == 12:  # FONT_STYLE_DEF
                    self.pos += 24
                    if self.pos < len(self.data) and self.data[self.pos] == 10:
                        self.pos += 1
                    break

        parts: List[str] = []
        while self.pos < len(self.data):
            tag = self._read_byte()
            if tag == 0:  # END
                break
            val = self._parse_record(tag)
            if val:
                parts.append(val)
        return "".join(parts).strip()

    def _parse_simple(self) -> str:
        pos = 5
        data = self.data
        version = self.version

        def read_b():
            nonlocal pos
            if pos >= len(data):
                return 0
            v = data[pos]
            pos += 1
            return v

        def read_u16():
            nonlocal pos
            if pos + 2 > len(data):
                pos = len(data)
                return 0
            v = struct.unpack_from("<H", data, pos)[0]
            pos += 2
            return v

        def parse_rec():
            nonlocal pos
            if pos >= len(data):
                return ""
            tag_byte = read_b()
            rec_type = tag_byte & 0x0F
            if rec_type == 0:
                return ""
            elif rec_type == 1:
                parts = []
                while pos < len(data):
                    if data[pos] & 0x0F == 0:
                        read_b()
                        break
                    p = parse_rec()
                    if p:
                        parts.append(p)
                return "".join(parts)
            elif rec_type == 2:
                read_b()  # font_pos
                char_val = read_u16() if version >= 5 else read_b()
                return chr(char_val) if 32 <= char_val <= 126 else ""
            elif rec_type == 3:
                sel = read_b()
                read_u16()  # var
                lines = []
                while pos < len(data):
                    if data[pos] & 0x0F == 0:
                        read_b()
                        break
                    lines.append(parse_rec())
                if sel in (6, 10, 11):
                    n = lines[0] if len(lines) > 0 else ""
                    d = lines[1] if len(lines) > 1 else ""
                    return rf"\frac{{{n}}}{{{d}}}"
                return "".join(lines)
            return ""

        out = []
        while pos < len(data):
            r = parse_rec()
            if r:
                out.append(r)
        return "".join(out).strip()

    def _read_byte(self) -> int:
        if self.pos >= len(self.data):
            return 0
        b = self.data[self.pos]
        self.pos += 1
        return b

    def _read_u16(self) -> int:
        if self.pos + 2 > len(self.data):
            self.pos = len(self.data)
            return 0
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def _parse_record(self, tag: int) -> str:
        if tag == 0:
            return ""

        rec_type = tag if self.version >= 5 else (tag & 0x0F)
        opts = self._read_byte() if self.version >= 5 else (tag >> 4)
        if opts & 0x08:  # nudge
            self.pos += 2

        if rec_type == 1:  # LINE
            parts: List[str] = []
            while self.pos < len(self.data):
                child_tag = self._read_byte()
                if child_tag == 0:  # END of line
                    break
                p = self._parse_record(child_tag)
                if p:
                    parts.append(p)
            return "".join(parts)

        elif rec_type == 2:  # CHAR
            typeface = self._read_byte()
            char_code = self._read_u16() if self.version >= 5 else self._read_byte()
            if opts & 0x04:  # user point size
                self._read_byte()

            emb = ""
            if opts & 0x01:  # embellishments
                while self.pos < len(self.data):
                    e = self._read_byte()
                    if e == 0:
                        break
                    if e == 6:
                        emb = r"\vec"
                    elif e == 5:
                        emb = r"\bar"
                    elif e == 1:
                        emb = "'"
                    elif e == 2:
                        emb = "''"

            # Character conversion
            ch = ""
            if char_code == 0x2212:
                ch = "-"
            elif char_code == 0x2264:
                ch = r"\le "
            elif char_code == 0x2265:
                ch = r"\ge "
            elif char_code == 0x2260:
                ch = r"\ne "
            elif char_code == 0x20D7:
                ch = ""  # combining vector arrow
            elif char_code in (0xEF02, 0xEF03, 0xEF04):
                ch = " "
            elif typeface in (132, 134, 135) and char_code in SYMBOL_GREEK_MAP:
                ch = SYMBOL_GREEK_MAP[char_code]
            elif 32 <= char_code <= 126:
                c_ascii = chr(char_code)
                if c_ascii == "\\":
                    ch = r"\backslash "
                elif c_ascii in ("{", "}"):
                    ch = f"\\{c_ascii}"
                else:
                    ch = c_ascii
            else:
                try:
                    c = chr(char_code)
                    ch = c if c.isprintable() else ""
                except Exception:
                    ch = ""

            if emb:
                if emb.startswith("\\"):
                    ch = f"{emb}{{{ch}}}"
                else:
                    ch = f"{ch}{emb}"
            return ch

        elif rec_type == 3:  # TMPL
            sel = self._read_byte()
            var = self._read_byte()
            if var & 0x80:
                var = (var & 0x7F) | (self._read_byte() << 8)
            tmpl_opts = self._read_byte()

            sublines: List[str] = []
            while self.pos < len(self.data):
                child_tag = self._read_byte()
                if child_tag == 0:  # END of template
                    break
                p = self._parse_record(child_tag)
                sublines.append(p)

            if sel in (28, 14):  # SUP
                inner = sublines[0] if sublines else ""
                return f"^{{{inner}}}"
            elif sel in (29, 13):  # SUB
                inner = sublines[0] if sublines else ""
                return f"_{{{inner}}}"
            elif sel in (30, 15):  # SUBSUP
                s1 = sublines[0] if len(sublines) > 0 else ""
                s2 = sublines[1] if len(sublines) > 1 else ""
                return f"_{{{s1}}}^{{{s2}}}"
            elif sel == 31:  # OVER ARROW
                inner = sublines[0] if sublines else ""
                return f"\\vec{{{inner}}}"
            elif sel in (10, 11):  # FRACT
                s1 = sublines[0] if len(sublines) > 0 else ""
                s2 = sublines[1] if len(sublines) > 1 else ""
                return f"\\frac{{{s1}}}{{{s2}}}"
            elif sel in (9, 5):  # ROOT
                inner = sublines[0] if sublines else ""
                return f"\\sqrt{{{inner}}}"
            elif sel in (1, 2, 3, 4):
                pairs = {1: ("(", ")"), 2: (r"\{", r"\}"), 3: ("[", "]"), 4: ("|", "|")}
                l, r = pairs.get(sel, ("(", ")"))
                return f"{l}{sublines[0] if sublines else ''}{r}"
            return "".join(sublines)

        elif rec_type in (4, 10):  # PILE
            parts: List[str] = []
            while self.pos < len(self.data):
                ct = self._read_byte()
                if ct == 0:
                    break
                p = self._parse_record(ct)
                if p:
                    parts.append(p)
            return "".join(parts)

        elif rec_type == 16:  # RULER
            self.pos += 6
            return ""

        elif rec_type in (8, 9, 11, 12, 13, 14, 15):
            self._read_byte()
            return ""

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
    Uses olefile to extract the true 'Equation Native' stream if present, preventing sector desynchronization.
    Returns:
        Dict mapping part name (e.g. 'word/embeddings/oleObject1.bin') to decoded LaTeX '$...$'.
    """
    results: Dict[str, str] = {}
    zf = zipfile.ZipFile(docx_file) if not isinstance(docx_file, zipfile.ZipFile) else docx_file

    for name in zf.namelist():
        if name.startswith("word/embeddings/") and (name.endswith(".bin") or name.endswith(".ole")):
            raw_data = zf.read(name)
            formula_tex = ""
            # Try olefile stream extraction first
            try:
                import olefile
                if olefile.isOleFile(io.BytesIO(raw_data)):
                    ole = olefile.OleFileIO(io.BytesIO(raw_data))
                    for stream_name in ["Equation Native", "\x03Equation Native"]:
                        if ole.exists(stream_name):
                            st_data = ole.openstream(stream_name).read()
                            formula_tex = decode_mtef(st_data)
                            break
                    ole.close()
            except Exception as ole_err:
                logger.debug(f"olefile stream extraction fallback for {name}: {ole_err}")

            if not formula_tex:
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
    """Converts a Word table to text lines or Markdown table lines."""
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

    # Check if table represents multiple-choice options or header info
    all_cells_flat = [c.strip() for r in rows for c in r if c and c.strip()]
    is_option_table = any(re.match(r"^[A-Da-d][\.\)]", c) for c in all_cells_flat)
    is_header_table = any(kw in " ".join(all_cells_flat).lower() for kw in ["họ và tên", "số báo danh", "mã đề", "thời gian làm bài", "đề thi gồm"])

    if is_option_table or is_header_table:
        return all_cells_flat

    # Format as Markdown table for true data tables
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
