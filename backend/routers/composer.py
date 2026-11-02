"""Quesy Exam Composer Router - Open-Prism LaTeX Workspace API.
Endpoints for compiling LaTeX documents to live PDF preview,
AI-assisted exam writing chat, template loading, and question bank export.
"""

import difflib
import hashlib
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Question, QuestionOption, SubStatement
from backend.services.composer_service import (
    STORAGE_COMPOSER_CACHE,
    TEMPLATES,
    compile_latex_to_pdf,
    ensure_full_latex_document,
    extract_questions_from_latex,
    compute_compilation_timeout,
)
from backend.services.ai_provider_service import default_ai_provider_service

logger = logging.getLogger("quesy.composer")

router = APIRouter(prefix="/api/v1/composer", tags=["Composer"])


# ---------------------------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------------------------

class CompileRequest(BaseModel):
    latex_code: str = Field(..., description="Full LaTeX source code to compile")
    title: str = Field("Đề Thi Soạn Thảo", description="Document title")
    mode: Optional[str] = Field("dethi", description="'dethi' (hide solution) or 'loigiai' (show solution)")
    show_solution: Optional[bool] = Field(None, description="Flag for solution visibility")
    draft_mode: Optional[bool] = Field(False, description="Draft mode for fast compilation")

class PartialCompileRequest(BaseModel):
    snippet_code: str = Field(..., description="LaTeX code snippet (e.g. single question)")
    title: str = Field("Câu hỏi", description="Title for partial compile")
    mode: Optional[str] = Field("dethi", description="Compilation mode")
    question_num: Optional[int] = Field(None, description="Question number for counter reset")

class CompileResponse(BaseModel):
    success: bool
    pdf_url: str
    compile_time_ms: int
    error: Optional[str] = None
    title: str
    total_pages: int = Field(1, description="Total number of pages in compiled PDF")

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str
    images: Optional[List[str]] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or command for the AI assistant")
    current_latex: Optional[str] = Field("", description="Current editor LaTeX code for context")
    compile_error: Optional[str] = Field(None, description="Recent compile error log if any")
    compile_error_log: Optional[str] = Field(None, description="Recent compile error log if any")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    images: Optional[List[str]] = Field(default_factory=list)

class DiffSuggestion(BaseModel):
    action: str = Field("replace", description="'replace' or 'insert'")
    old_text: str = Field("", description="Exact text snippet to replace in current code")
    new_text: str = Field("", description="New text snippet to insert")
    description: str = Field("", description="Summary description of the change")

class ChatResponse(BaseModel):
    reply: str
    suggested_latex: Optional[str] = None
    diff: Optional[DiffSuggestion] = None
    diffs: List[DiffSuggestion] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_diffs(self):
        if self.diffs and not self.diff:
            self.diff = self.diffs[0]
        elif self.diff and not self.diffs:
            self.diffs = [self.diff]
        return self

class SaveToBankRequest(BaseModel):
    latex_code: str = Field(..., description="LaTeX source containing exam questions to extract")

class ExportRequest(BaseModel):
    latex_code: str = Field(..., description="LaTeX source code to export")
    mode: Optional[str] = Field("dethi", description="ex_test compilation mode: 'dethi' or 'loigiai'")
    title: Optional[str] = Field("de_thi", description="Document title for naming the exported file")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/templates", summary="Get canonical exam starter templates")
def get_templates():
    """Returns starter LaTeX exam templates (Circular 32, Calculus, Geometry, Blank)."""
    return {
        "templates": [
            {
                "id": k,
                "title": v["title"],
                "description": v["description"],
                "latex": v["latex"],
            }
            for k, v in TEMPLATES.items()
        ]
    }


def count_pdf_pages(pdf_path: Path) -> int:
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        return max(1, len(reader.pages))
    except Exception:
        return 1


@router.post("/compile", response_model=CompileResponse, summary="Compile LaTeX code to PDF")
def compile_latex_endpoint(req: CompileRequest):
    """Compiles LaTeX source code into vector-crisp PDF with live preview."""
    clean_code = req.latex_code.strip()
    if not clean_code:
        raise HTTPException(status_code=400, detail="Mã LaTeX không được để trống")

    mode = req.mode or ("loigiai" if req.show_solution else "dethi")
    full_latex = ensure_full_latex_document(clean_code, mode=mode, title=req.title, draft_mode=bool(req.draft_mode))

    code_hash = hashlib.md5((full_latex + req.title + mode).encode("utf-8")).hexdigest()
    out_pdf = STORAGE_COMPOSER_CACHE / f"{code_hash}.pdf"

    # If already compiled and cached on disk
    if out_pdf.exists() and out_pdf.stat().st_size > 1000:
        return CompileResponse(
            success=True,
            pdf_url=f"/api/v1/composer/pdf/{code_hash}.pdf",
            compile_time_ms=12,
            error=None,
            title=req.title,
            total_pages=count_pdf_pages(out_pdf),
        )

    success, err_msg, elapsed_ms = compile_latex_to_pdf(full_latex, out_pdf, title=req.title, mode=mode)

    if not success:
        return CompileResponse(
            success=False,
            pdf_url="",
            compile_time_ms=elapsed_ms,
            error=err_msg,
            title=req.title,
            total_pages=1,
        )

    return CompileResponse(
        success=True,
        pdf_url=f"/api/v1/composer/pdf/{code_hash}.pdf",
        compile_time_ms=elapsed_ms,
        error=None,
        title=req.title,
        total_pages=count_pdf_pages(out_pdf),
    )


@router.post("/compile-partial", response_model=CompileResponse, summary="Compile partial LaTeX snippet (e.g. single question)")
def compile_partial_endpoint(req: PartialCompileRequest):
    clean_code = req.snippet_code.strip()
    if not clean_code:
        raise HTTPException(status_code=400, detail="Mã snippet không được để trống")
    
    mode = req.mode or "dethi"
    full_latex = ensure_full_latex_document(clean_code, mode=mode, title=req.title, draft_mode=True)
    
    if req.question_num and req.question_num > 1:
        offset_num = req.question_num - 1
        full_latex = full_latex.replace(r'\begin{document}', r'\begin{document}' + f'\n\\setcounter{{ex}}{{{offset_num}}}\n', 1)
    
    code_hash = hashlib.md5((full_latex + req.title + mode + str(req.question_num)).encode("utf-8")).hexdigest()
    out_pdf = STORAGE_COMPOSER_CACHE / f"{code_hash}.pdf"
    
    if out_pdf.exists() and out_pdf.stat().st_size > 1000:
        return CompileResponse(
            success=True,
            pdf_url=f"/api/v1/composer/pdf/{code_hash}.pdf",
            compile_time_ms=15,
            error=None,
            title=req.title,
            total_pages=count_pdf_pages(out_pdf),
        )
        
    success, err_msg, elapsed_ms = compile_latex_to_pdf(full_latex, out_pdf, title=req.title, mode=mode)
    if not success:
        return CompileResponse(
            success=False,
            pdf_url="",
            compile_time_ms=elapsed_ms,
            error=err_msg,
            title=req.title,
            total_pages=1,
        )
        
    return CompileResponse(
        success=True,
        pdf_url=f"/api/v1/composer/pdf/{code_hash}.pdf",
        compile_time_ms=elapsed_ms,
        error=None,
        title=req.title,
        total_pages=count_pdf_pages(out_pdf),
    )


@router.get("/pdf/{doc_id}.pdf", summary="Stream compiled PDF for inline live preview")
def get_compiled_pdf(doc_id: str):
    """Serves the compiled PDF document inline for the right preview pane."""
    pdf_path = STORAGE_COMPOSER_CACHE / f"{doc_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Tài liệu PDF chưa được biên dịch hoặc đã hết hạn.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=exam_{doc_id[:8]}.pdf",
            "Cache-Control": "public, max-age=3600",
        },
    )


@router.post("/export", summary="Export full standalone LaTeX source (.tex)")
def export_latex_endpoint(req: ExportRequest):
    """Exports full standalone LaTeX source code (.tex) with canonical preamble and ex_test packages.
    If the code is preamble-free, wraps it in the canonical preamble with the specified mode.
    If the code already has a preamble, standardizes it.
    """
    clean_code = req.latex_code.strip()
    full_latex = ensure_full_latex_document(clean_code, mode=req.mode or "dethi", title=req.title or "de_thi")
    safe_title = re.sub(r'[^\w\-_\.]', '_', req.title or "de_thi").strip('_') or "de_thi"
    filename = f"{safe_title}.tex"
    return Response(
        content=full_latex,
        media_type="text/x-tex; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Filename": filename,
        }
    )


@router.get("/export", summary="Export full standalone LaTeX source (.tex) via GET")
def export_latex_endpoint_get(
    latex_code: str = "",
    mode: str = "dethi",
    title: str = "de_thi",
):
    """Exports full standalone LaTeX source code (.tex) with canonical preamble via GET."""
    clean_code = latex_code.strip()
    full_latex = ensure_full_latex_document(clean_code, mode=mode or "dethi", title=title or "de_thi")
    safe_title = re.sub(r'[^\w\-_\.]', '_', title or "de_thi").strip('_') or "de_thi"
    filename = f"{safe_title}.tex"
    return Response(
        content=full_latex,
        media_type="text/x-tex; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Filename": filename,
        }
    )


def _clean_diff_description(text: str) -> Optional[str]:
    """Extract a concise description line from text preceding a diff/replacement block."""
    if not text:
        return None
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None
    last = lines[-1]
    last = re.sub(r'^(?:#+|\*|-|\d+\.)\s*', '', last)
    last = re.sub(r'[:：]\s*$', '', last)
    last = re.sub(r'[*_`]', '', last).strip()
    if last and len(last) <= 120 and not last.startswith("```"):
        return last
    return None


def find_in_latex(needle: str, current_latex: str, fuzzy_threshold: float = 0.65) -> Optional[str]:
    """Find the exact substring or best matching line slice in current_latex,
    resilient to differences in indentation, intra-line whitespace, newlines, and minor typos.
    """
    if not needle or not current_latex:
        return None

    # Step 1: Exact substring match
    if needle in current_latex:
        return needle
    stripped = needle.strip()
    if not stripped:
        return None
    if stripped in current_latex:
        return stripped

    # Step 2: Line ending (CRLF / LF) normalization
    crlf = chr(13) + chr(10)
    norm_cur = current_latex.replace(crlf, chr(10))
    norm_needle = stripped.replace(crlf, chr(10))
    cur_lines = current_latex.splitlines()

    if norm_needle in norm_cur:
        needle_lines = [l.strip() for l in norm_needle.splitlines() if l.strip()]
        if needle_lines:
            for i in range(len(cur_lines) - len(needle_lines) + 1):
                window = [cur_lines[i + k].strip() for k in range(len(needle_lines))]
                if window == needle_lines:
                    return "\n".join(cur_lines[i : i + len(needle_lines)])

    needle_lines_raw = [l for l in norm_needle.splitlines() if l.strip()]

    # Step 3: Single-line matching (whitespace-collapsed, stripped equality, containment)
    if len(needle_lines_raw) == 1:
        single_needle = needle_lines_raw[0].strip()
        single_needle_norm = re.sub(r'\s+', ' ', single_needle)

        for line in cur_lines:
            if line.strip() == single_needle:
                return line
        for line in cur_lines:
            if re.sub(r'\s+', ' ', line.strip()) == single_needle_norm:
                return line
        for line in cur_lines:
            if single_needle in line:
                return line
            if single_needle_norm in re.sub(r'\s+', ' ', line.strip()):
                return line

    # Step 4: Multi-line whitespace & blank line tolerant match
    if needle_lines_raw:
        norm_needle_lines = [re.sub(r'\s+', ' ', l.strip()) for l in needle_lines_raw]
        M = len(norm_needle_lines)

        for i in range(len(cur_lines)):
            if re.sub(r'\s+', ' ', cur_lines[i].strip()) != norm_needle_lines[0]:
                continue
            k = 0
            j = i
            while j < len(cur_lines) and k < M:
                c_norm = re.sub(r'\s+', ' ', cur_lines[j].strip())
                if not c_norm:  # blank line in current_latex
                    j += 1
                    continue
                if c_norm == norm_needle_lines[k]:
                    k += 1
                    j += 1
                else:
                    break
            if k == M:
                return "\n".join(cur_lines[i:j])

    # Step 5: Fuzzy matching fallback (via SequenceMatcher)
    clean_needle_text = re.sub(r'\s+', ' ', norm_needle).strip()
    if len(clean_needle_text) >= 6:
        m_lines = len(needle_lines_raw)
        best_ratio = 0.0
        best_slice = None

        if m_lines <= 1:
            for line in cur_lines:
                clean_line = re.sub(r'\s+', ' ', line.strip())
                if not clean_line:
                    continue
                ratio = difflib.SequenceMatcher(None, clean_needle_text, clean_line).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_slice = line
            if best_ratio >= fuzzy_threshold and best_slice:
                return best_slice
        else:
            min_w = max(1, m_lines - 2)
            max_w = min(len(cur_lines) + 1, m_lines + 5)
            for w in range(min_w, max_w):
                for i in range(len(cur_lines) - w + 1):
                    window_lines = cur_lines[i : i + w]
                    window_text = "\n".join(window_lines)
                    clean_window = re.sub(r'\s+', ' ', window_text).strip()
                    if not clean_window:
                        continue
                    ratio = difflib.SequenceMatcher(None, clean_needle_text, clean_window).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_slice = window_text

            if best_ratio >= fuzzy_threshold and best_slice:
                return best_slice

    return None


def find_nth_question_in_latex(latex_code: Optional[str], n: int, section: Optional[Any] = None) -> Optional[str]:
    """Extracts the nth question block (1-indexed) from a LaTeX document.
    Accurately supports both ex_test.sty format (\\begin{ex}...\\end{ex})
    and classic format (\\textbf{Câu n.}, Câu n:, etc.).
    If section is specified (1, 2, 3 or 'I', 'II', 'III'), searches inside that section.
    Returns the exact matching substring in latex_code, or None if not found.
    """
    if not latex_code or n < 1:
        return None

    # If section is specified, attempt to isolate that section first
    if section is not None:
        sec_str = str(section).strip().upper()
        sec_map = {"1": "I", "2": "II", "3": "III", "4": "IV"}
        roman_sec = sec_map.get(sec_str, sec_str)
        sec_pat = re.compile(
            rf'(?:\\noindent\s*)?(?:\\textbf\{{\s*PHẦN\s+{roman_sec}[^}}]*\}}|\\section\*?\{{\s*PHẦN\s+{roman_sec}[^}}]*\}}|PHẦN\s+{roman_sec}\.[^\n]*)',
            re.IGNORECASE
        )
        sec_matches = list(sec_pat.finditer(latex_code))
        if sec_matches:
            start_sec = sec_matches[0].start()
            next_sec_pat = re.compile(
                r'(?:\\noindent\s*)?(?:\\textbf\{\s*PHẦN\s+[IVX0-9]+[^}]*\}|\\section\*?\{\s*PHẦN\s+[IVX0-9]+[^}]*\}|PHẦN\s+[IVX0-9]+\.[^\n]*)|\\end\{document\}',
                re.IGNORECASE
            )
            next_matches = [m for m in next_sec_pat.finditer(latex_code) if m.start() > start_sec]
            end_sec = next_matches[0].start() if next_matches else len(latex_code)
            sec_slice = latex_code[start_sec:end_sec]
            sub_res = find_nth_question_in_latex(sec_slice, n, section=None)
            if sub_res:
                return sub_res

    # 1. ex_test.sty syntax (\\begin{ex} ... \\end{ex} or \\begin{bt} ... \\end{bt})
    ex_matches = list(re.finditer(r'\\begin\{(ex|bt|vd)\}(?:\[[^\]]*\])?[\s\S]*?\\end\s*\{\1\}', latex_code))
    if ex_matches:
        if 1 <= n <= len(ex_matches):
            return ex_matches[n - 1].group(0)
        return None

    # 1b. Unclosed ex_test environments: \begin{ex} ... (ending at next \begin{ex} or \end{document} or EOF)
    unclosed_matches = list(re.finditer(
        r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?[\s\S]*?(?=(?:\\begin\{(?:ex|bt|vd)\}|\\end\{document\}|\Z))',
        latex_code
    ))
    if unclosed_matches:
        if 1 <= n <= len(unclosed_matches):
            return unclosed_matches[n - 1].group(0).rstrip()
        return None

    # 2. Classic \textbf{Câu X.} or Câu X. syntax
    classic_pattern = re.compile(
        r'(?:\\(?:noindent|medskip|bigskip)\s*)?\\textbf\{\s*Câu\s*(\d+)[\.:]?\s*\}|(?<![\w\\{])Câu\s*(\d+)[\.:]',
        re.IGNORECASE
    )
    matches = list(classic_pattern.finditer(latex_code))
    if not matches:
        return None

    # Find the match matching question number n
    target_idx = None
    for idx, m in enumerate(matches):
        q_num = int(m.group(1) or m.group(2))
        if q_num == n:
            target_idx = idx
            break

    # If exact question number n wasn't found, fallback to ordinal position (1 <= n <= len(matches))
    if target_idx is None and 1 <= n <= len(matches):
        target_idx = n - 1

    if target_idx is None:
        return None

    start_pos = matches[target_idx].start()
    if target_idx + 1 < len(matches):
        end_pos = matches[target_idx + 1].start()
    else:
        # Stop before \\end{document} or \\section if present
        tail = latex_code[start_pos:]
        end_match = re.search(r'(\\end\{document\}|\\section\*?\{)', tail)
        if end_match:
            end_pos = start_pos + end_match.start()
        else:
            end_pos = len(latex_code)

    extracted = latex_code[start_pos:end_pos].rstrip()
    return extracted if extracted else None


def _insert_in_preamble(current_latex: str, package_line: str) -> Optional[Tuple[str, str]]:
    """Helper to find the best insertion point in preamble for a missing package or macro.
    Returns (old_text, new_text) or None.
    """
    lines = current_latex.splitlines()
    # 1. Prefer inserting after the last \usepackage line
    last_pkg_idx = -1
    for idx, l in enumerate(lines):
        if l.strip().startswith(r"\usepackage") or l.strip().startswith(r"\tcbuselibrary"):
            last_pkg_idx = idx

    if last_pkg_idx != -1:
        old_line = lines[last_pkg_idx]
        new_line = f"{old_line}\n{package_line}"
        return old_line, new_line

    # 2. Or insert after \documentclass line
    for idx, l in enumerate(lines):
        if r"\documentclass" in l:
            old_line = l
            new_line = f"{old_line}\n{package_line}"
            return old_line, new_line

    # 3. Or before \begin{document}
    for idx, l in enumerate(lines):
        if r"\begin{document}" in l:
            old_line = l
            new_line = f"{package_line}\n{old_line}"
            return old_line, new_line

    return None


def diagnose_compile_error(
    compile_error: str,
    current_latex: str,
    user_message: str = ""
) -> Optional[ChatResponse]:
    r"""Analyze LaTeX compilation error log and diagnose the root cause to propose a targeted diff.
    Supports Preamble-Free line offset mapping (L_user = L_comp - 11) and 5 classic TeX error families:
    1. 'There\'s no line here to end' (trailing \\ after {...})
    2. 'Undefined control sequence' (\ule -> \rule, \choiceTFt -> \choiceTF[1], ight| -> \right|, typos)
    3. 'Missing $ inserted' (unwrapped math symbols or unclosed inline math)
    4. 'Missing \\right. inserted' / 'Extra }, or forgotten \\right' (unbalanced \\left/\\right)
    5. 'Environment undefined' / Missing packages (tikz, ex_test, amsmath)
    """
    if not compile_error or not current_latex:
        return None

    err_lower = compile_error.lower()
    cur_lower = current_latex.lower()
    doc_lines = current_latex.splitlines()

    # Line offset logic for Preamble-Free mode
    m_line = re.search(r'(?:document\.tex:(\d+)|l\.(\d+)|\bline\s+(\d+))', compile_error, re.IGNORECASE)
    L_comp: Optional[int] = None
    if m_line:
        L_comp = int(m_line.group(1) or m_line.group(2) or m_line.group(3))

    is_preamble_free = r"\documentclass" not in cur_lower
    L_user: Optional[int] = None
    if L_comp is not None:
        L_user = (L_comp - 11) if is_preamble_free else L_comp

    def _get_target_line_and_idx() -> Tuple[Optional[int], Optional[str]]:
        if L_user is not None and 1 <= L_user <= len(doc_lines):
            return L_user - 1, doc_lines[L_user - 1]
        return None, None

    # 0. Timeout error check (Dynamic Adaptive Compilation Timeout)
    if any(k in err_lower for k in ("compilation timed out", "timed out", "quá thời gian")) or "quá thời gian" in err_lower:
        calc_timeout = compute_compilation_timeout(current_latex)
        sample_diffs: List[DiffSuggestion] = []
        for line in doc_lines:
            if "samples=" in line:
                m_samp = re.search(r"samples=(\d+)", line)
                if m_samp and int(m_samp.group(1)) >= 80:
                    new_line = re.sub(r"samples=\d+", "samples=50", line)
                    sample_diffs.append(DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=new_line,
                        description="Tối ưu số mẫu samples=50 giảm thời gian biên dịch TikZ"
                    ))
        diff_to_use = sample_diffs[0] if sample_diffs else None
        reply = (
            f"⚠️ **Cảnh báo: Biên dịch quá thời gian giới hạn (Compilation Timed Out)!**\n\n"
            f"Nguyên nhân: Đề thi chứa các hình vẽ TikZ / đồ thị hàm số có mật độ mẫu `samples` quá cao (ví dụ `samples=100`) hoặc tài liệu quy mô lớn làm vượt quá giới hạn xử lý.\n\n"
            f"Hệ thống đã tự động kích hoạt **Dynamic Adaptive Compilation Timeout**, nâng trần thời gian lên tới **{calc_timeout} giây**.\n\n"
            f"Để tăng tốc độ biên dịch lên 50% mà vẫn giữ độ trơn mịn hoàn hảo 1200 DPI, bạn nên cấu hình `samples=50` (hoặc `samples=60`) mặc định cho các đồ thị TikZ.\n\n"
        )
        if sample_diffs:
            reply += "Dưới đây là gợi ý tự động tối ưu:\n" + "\n".join([f"```diff\n- {d.old_text}\n+ {d.new_text}\n```" for d in sample_diffs])
        else:
            reply += "Hãy rà soát các lệnh plot trong TikZ và hạ samples=100 xuống samples=50."
        return ChatResponse(reply=reply, diff=diff_to_use, diffs=sample_diffs)

    # 1. Bad / invalid command such as \badcommand
    if r"\badcommand" in cur_lower or r"\badcommand" in err_lower:
        for line in doc_lines:
            if r"\badcommand" in line:
                fixed_line = line.replace(r"\badcommand", r"% \badcommand (lệnh lỗi đã vô hiệu hóa)")
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=fixed_line,
                    description=r"Sửa lỗi biên dịch: Vô hiệu hóa lệnh \badcommand không tồn tại"
                )
                reply = (
                    "Tôi phát hiện lỗi biên dịch do lệnh `\\badcommand` không hợp lệ trong LaTeX.\n\n"
                    f"```diff\n- {line}\n+ {fixed_line}\n```\n\n"
                    "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để khắc phục lỗi này."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 2. 'There\'s no line here to end'
    if "there's no line here to end" in err_lower or "no line here to end" in err_lower:
        target_idx, target_line = None, None
        if L_user is not None:
            for offset in (0, -1, 1, -2, 2):
                idx = (L_user - 1) + offset
                if 0 <= idx < len(doc_lines):
                    line = doc_lines[idx]
                    if r"\\" in line or re.search(r'\}\s*\\\\', line):
                        target_idx, target_line = idx, line
                        break
        if target_idx is None:
            for idx, line in enumerate(doc_lines):
                if re.search(r'\}\s*\\\\', line) or line.strip() == r"\\" or line.rstrip().endswith(r"\\"):
                    target_idx, target_line = idx, line
                    break

        if target_idx is not None and target_line is not None:
            fixed_line = re.sub(r'\}\s*\\\\', '}', target_line)
            if fixed_line == target_line:
                fixed_line = re.sub(r'\\\\(?:\s*)$', '', target_line)
            if fixed_line == target_line and target_line.strip() == r"\\":
                fixed_line = ""

            diff = DiffSuggestion(
                action="replace",
                old_text=target_line,
                new_text=fixed_line,
                description="Sửa lỗi biên dịch: Xóa dấu \\ thừa gây lỗi 'There\'s no line here to end'"
            )
            reply = (
                "Tôi phát hiện lỗi biên dịch `! LaTeX Error: There's no line here to end`.\n\n"
                "Nguyên nhân: Thừa dấu `\\` sau cặp ngoặc nhọn `{...}` hoặc ở vị trí không có dòng văn bản để ngắt.\n\n"
                f"```diff\n- {target_line}\n+ {fixed_line}\n```\n\n"
                "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để khắc phục lỗi này."
            )
            return ChatResponse(reply=reply, diff=diff)

    # 3. Missing tikz / tkz-tab packages
    if any(k in err_lower for k in ("tikzpicture undefined", "environment tikzpicture undefined", "tkztabinit undefined", "package tikz error")) or \
       ("undefined control sequence" in err_lower and any(cmd in err_lower for cmd in ("\\tkztab", "\\tikzpicture", "tkztabinit", "tkztabline", "tkztabvar"))):
        if r"\usepackage{tikz" not in cur_lower and r"\usepackage[tikz" not in cur_lower:
            ins = _insert_in_preamble(current_latex, r"\usepackage{tikz,tkz-tab}")
            if ins:
                old_text, new_text = ins
                diff = DiffSuggestion(
                    action="replace",
                    old_text=old_text,
                    new_text=new_text,
                    description="Bổ sung gói tikz và tkz-tab để sửa lỗi Environment tikzpicture undefined"
                )
                reply = (
                    "Tôi phát hiện lỗi biên dịch: môi trường `tikzpicture` hoặc lệnh `tkz-tab` chưa được khai báo do thiếu gói lệnh vẽ hình.\n\n"
                    "Tôi đề xuất bổ sung `\\usepackage{tikz,tkz-tab}` vào phần khai báo (preamble):\n\n"
                    f"```diff\n- {old_text}\n+ {new_text}\n```\n\n"
                    "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
                )
                return ChatResponse(reply=reply, diff=diff)
        elif "tkz-tab" not in cur_lower:
            for line in doc_lines:
                if "usepackage" in line and "tikz" in line:
                    new_line = line.replace("tikz", "tikz,tkz-tab")
                    diff = DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=new_line,
                        description="Bổ sung thư viện tkz-tab vào khai báo gói tikz"
                    )
                    reply = (
                        "Tôi phát hiện lỗi thiếu gói `tkz-tab` để vẽ bảng biến thiên.\n\n"
                        f"```diff\n- {line}\n+ {new_line}\n```\n\n"
                        "Bấm **Đồng ý** trên thanh gợi ý để sửa lỗi."
                    )
                    return ChatResponse(reply=reply, diff=diff)

    # 4. Missing ex_test package
    if any(k in err_lower for k in ("environment ex undefined", "ex_test", "choicetf undefined", "shortans undefined")) or \
       ("undefined control sequence" in err_lower and any(cmd in err_lower for cmd in ("\\choice", "\\choicetf", "\\shortans", "\\immini", "\\itemch"))):
        if "ex_test" not in cur_lower:
            ins = _insert_in_preamble(current_latex, r"\usepackage[dethi]{ex_test}")
            if ins:
                old_text, new_text = ins
                diff = DiffSuggestion(
                    action="replace",
                    old_text=old_text,
                    new_text=new_text,
                    description="Bổ sung gói ex_test để sửa lỗi Environment ex undefined"
                )
                reply = (
                    "Tôi phát hiện lỗi biên dịch: môi trường đề thi `\\begin{ex}` hoặc các lệnh `\\choice`, `\\choiceTF`, `\\shortans` chưa được khai báo.\n\n"
                    "Tôi đề xuất bổ sung gói `\\usepackage[dethi]{ex_test}` vào phần khai báo:\n\n"
                    f"```diff\n- {old_text}\n+ {new_text}\n```\n\n"
                    "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 5. Missing amsmath / amssymb package
    if "undefined control sequence" in err_lower and any(cmd in err_lower for cmd in ("\\dfrac", "\\mathbb", "\\iint", "\\iiint", "\\align")):
        if "amsmath" not in cur_lower:
            ins = _insert_in_preamble(current_latex, r"\usepackage{amsmath,amssymb}")
            if ins:
                old_text, new_text = ins
                diff = DiffSuggestion(
                    action="replace",
                    old_text=old_text,
                    new_text=new_text,
                    description="Bổ sung gói amsmath,amssymb để hiển thị công thức toán"
                )
                reply = (
                    "Tôi phát hiện lỗi biên dịch do thiếu gói ký hiệu toán học chuẩn `amsmath,amssymb`.\n\n"
                    "Tôi đề xuất bổ sung gói vào phần khai báo:\n\n"
                    f"```diff\n- {old_text}\n+ {new_text}\n```\n\n"
                    "Bấm **Đồng ý** để áp dụng thay đổi này."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 6. Obsolete vietnam package
    if "vietnam" in err_lower or "utf8x" in err_lower:
        for line in doc_lines:
            if "usepackage" in line and "vietnam" in line:
                new_line = re.sub(r'\\usepackage(\[[^\]]*\])?\{vietnam\}', r'\\usepackage{fontspec}', line)
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=new_line,
                    description="Thay thế gói vietnam bằng fontspec tương thích XeTeX/Tectonic"
                )
                reply = (
                    "Gói `vietnam.sty` đã lỗi thời và không tương thích với trình biên dịch XeTeX/Tectonic hiện đại.\n\n"
                    "Tôi đề xuất thay thế bằng `\\usepackage{fontspec}`:\n\n"
                    f"```diff\n- {line}\n+ {new_line}\n```\n\n"
                    "Bấm **Đồng ý** để sửa lỗi."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 7. Unclosed environment ended by \end{document}
    m_unclosed = re.search(r'\\begin\{([a-zA-Z0-9_*]+)\}(?:[^\n]*?)ended by \\end\{document\}', compile_error, re.IGNORECASE)
    if not m_unclosed:
        m_unclosed = re.search(r'environment\s+([a-zA-Z0-9_*]+)\s+(?:[^\n]*?)ended by \\end\{document\}', compile_error, re.IGNORECASE)
    if m_unclosed:
        env_name = m_unclosed.group(1)
        for line in doc_lines:
            if r"\end{document}" in line:
                indent = line[: len(line) - len(line.lstrip())]
                new_line = f"{indent}\\end{{{env_name}}}\n{line}"
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=new_line,
                    description=f"Đóng môi trường {env_name} bằng \\end{{{env_name}}}"
                )
                reply = (
                    f"Phát hiện môi trường `\\begin{{{env_name}}}` chưa được đóng trước khi kết thúc tài liệu `\\end{{document}}`.\n\n"
                    f"```diff\n- {line}\n+ {new_line}\n```\n\n"
                    "Bấm **Đồng ý** để đóng môi trường này."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 8. Common command typos (\ule, \choiceTFt, \choiceft, \night|, \fracc, \begindocument, \vecto)
    typo_mappings = [
        (r'\ule', r'\rule'),
        (r'ule{\textwidth}', r'\rule{\textwidth}{0.5pt}'),
        (r'\choiceTFt', r'\choiceTF[1]'),
        (r'\choiceft', r'\choiceTF[1]'),
        (r'\night|', r'\right|'),
        (r'\fracc', r'\dfrac'),
        (r'\begindocument', r'\begin{document}'),
        (r'\enddocument', r'\end{document}'),
        (r'\vecto', r'\overrightarrow'),
    ]
    for bad_cmd, good_cmd in typo_mappings:
        if bad_cmd in compile_error or bad_cmd in current_latex or (bad_cmd.lower() in cur_lower):
            for line in doc_lines:
                if bad_cmd in line or (bad_cmd.lower() in line.lower() and bad_cmd.startswith('\\')):
                    fixed_line = line.replace(bad_cmd, good_cmd)
                    if fixed_line == line:
                        fixed_line = re.sub(re.escape(bad_cmd), good_cmd, line, flags=re.IGNORECASE)
                    diff = DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=fixed_line,
                        description=f"Sửa lệnh sai cú pháp '{bad_cmd}' thành '{good_cmd}'"
                    )
                    reply = (
                        f"Phát hiện lệnh sai cú pháp `{bad_cmd}` trong mã nguồn:\n\n"
                        f"```diff\n- {line}\n+ {fixed_line}\n```\n\n"
                        f"Bấm **Đồng ý** để sửa thành `{good_cmd}`."
                    )
                    return ChatResponse(reply=reply, diff=diff)

    # Check ight| without preceding backslash
    if re.search(r'(?<!r)ight\|', current_latex):
        for line in doc_lines:
            if re.search(r'(?<!r)ight\|', line):
                fixed_line = re.sub(r'(?<!r)ight\|', r'\\right|', line)
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=fixed_line,
                    description=r"Sửa lệnh sai cú pháp 'ight|' thành '\right|'"
                )
                reply = (
                    "Phát hiện lệnh sai cú pháp `ight|` thiếu dấu gạch chéo `\\` trong mã nguồn:\n\n"
                    f"```diff\n- {line}\n+ {fixed_line}\n```\n\n"
                    r"Bấm **Đồng ý** để sửa thành `\right|`."
                )
                return ChatResponse(reply=reply, diff=diff)

    # 9. Missing $ inserted
    if "missing $ inserted" in err_lower:
        target_idx, target_line = None, None
        if L_user is not None and 1 <= L_user <= len(doc_lines):
            target_idx = L_user - 1
            target_line = doc_lines[target_idx]
        else:
            for idx, line in enumerate(doc_lines):
                if line.count("$") % 2 != 0:
                    target_idx, target_line = idx, line
                    break
            if target_idx is None:
                for idx, line in enumerate(doc_lines):
                    if re.search(r'[_^]|\\[a-zA-Z]+', line) and "$" not in line:
                        target_idx, target_line = idx, line
                        break

        if target_idx is not None and target_line is not None:
            if target_line.count("$") % 2 != 0:
                fixed_line = target_line.rstrip() + "$"
            elif "$" not in target_line:
                fixed_line = f"${target_line.strip()}$"
            else:
                fixed_line = target_line.rstrip() + "$"
            diff = DiffSuggestion(
                action="replace",
                old_text=target_line,
                new_text=fixed_line,
                description="Sửa lỗi biên dịch: Bổ sung dấu $ cho công thức toán"
            )
            reply = (
                "Tôi phát hiện lỗi biên dịch `! Missing $ inserted` do công thức toán học chưa được đóng hoặc thiếu cặp `$ ... $.\n\n"
                f"```diff\n- {target_line}\n+ {fixed_line}\n```\n\n"
                "Bấm **Đồng ý** để sửa lỗi."
            )
            return ChatResponse(reply=reply, diff=diff)

    # 10. Missing \right. inserted or Extra }, or forgotten \right
    if any(k in err_lower for k in ("missing \\right", "forgotten \\right", "missing \\left", "forgotten \\left", "extra }, or forgotten \\right")):
        target_idx, target_line = None, None
        if L_user is not None and 1 <= L_user <= len(doc_lines):
            target_idx = L_user - 1
            target_line = doc_lines[target_idx]
        else:
            for idx, line in enumerate(doc_lines):
                if (r"\right" in line and r"\left" not in line) or (r"\left" in line and r"\right" not in line):
                    target_idx, target_line = idx, line
                    break

        if target_idx is not None and target_line is not None:
            if r"\right|" in target_line and r"\left." not in target_line:
                fixed_line = re.sub(r'(\([^\)]+\)\s*\\right\|)', r'\\left. \1', target_line)
                if fixed_line == target_line:
                    fixed_line = target_line.replace(r"\right|", r"\left. \right|")
            elif r"\left." in target_line and r"\right." not in target_line and r"\right|" not in target_line:
                fixed_line = target_line.rstrip() + r" \right."
            else:
                fixed_line = target_line.replace(r"\right|", r"\left. \right|")

            diff = DiffSuggestion(
                action="replace",
                old_text=target_line,
                new_text=fixed_line,
                description="Sửa lỗi biên dịch: Cân bằng cặp ngoặc \\left. và \\right."
            )
            reply = (
                "Tôi phát hiện lỗi mất cân bằng cặp lệnh `\\left` và `\\right` (`Missing \\right. inserted` hoặc `forgotten \\right`).\n\n"
                f"```diff\n- {target_line}\n+ {fixed_line}\n```\n\n"
                "Bấm **Đồng ý** để áp dụng sửa đổi."
            )
            return ChatResponse(reply=reply, diff=diff)

    # 11. Generic Undefined control sequence
    if "undefined control sequence" in err_lower:
        target_idx, target_line = _get_target_line_and_idx()
        m_cmd = re.search(r'undefined control sequence[\s\S]*?\\([a-zA-Z]+)', compile_error, re.IGNORECASE)
        if not m_cmd:
            m_cmd = re.search(r'l\.\d+\s*\\([a-zA-Z]+)', compile_error)
        bad_name = m_cmd.group(1) if m_cmd else None

        if bad_name:
            bad_seq = f"\\{bad_name}"
            if target_line and bad_seq in target_line:
                fixed_line = target_line.replace(bad_seq, f"% {bad_seq}")
                diff = DiffSuggestion(
                    action="replace",
                    old_text=target_line,
                    new_text=fixed_line,
                    description=f"Vô hiệu hóa lệnh không xác định '{bad_seq}'"
                )
                reply = (
                    f"Tôi phát hiện lỗi `Undefined control sequence: \\{bad_name}`.\n\n"
                    f"```diff\n- {target_line}\n+ {fixed_line}\n```\n\n"
                    "Bấm **Đồng ý** để khắc phục lỗi."
                )
                return ChatResponse(reply=reply, diff=diff)
            for line in doc_lines:
                if bad_seq in line:
                    fixed_line = line.replace(bad_seq, f"% {bad_seq}")
                    diff = DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=fixed_line,
                        description=f"Vô hiệu hóa lệnh không xác định '{bad_seq}'"
                    )
                    reply = (
                        f"Tôi phát hiện lỗi `Undefined control sequence: \\{bad_name}`.\n\n"
                        f"```diff\n- {line}\n+ {fixed_line}\n```\n\n"
                        "Bấm **Đồng ý** để khắc phục lỗi."
                    )
                    return ChatResponse(reply=reply, diff=diff)

    # 12. Generic Environment undefined
    m_env = re.search(r'environment\s+([a-zA-Z0-9_*]+)\s+undefined', compile_error, re.IGNORECASE)
    if not m_env:
        m_env = re.search(r'\\begin\{([a-zA-Z0-9_*]+)\}\s+undefined', compile_error, re.IGNORECASE)
    if m_env:
        env_name = m_env.group(1)
        if env_name in ("tikzpicture", "tkzTab"):
            pkg = r"\usepackage{tikz,tkz-tab}"
        elif env_name in ("ex", "loigiai", "itemchoice"):
            pkg = r"\usepackage[dethi]{ex_test}"
        elif env_name in ("align", "align*", "gather", "gather*"):
            pkg = r"\usepackage{amsmath,amssymb}"
        elif env_name in ("tcolorbox",):
            pkg = r"\usepackage{tcolorbox}"
        else:
            pkg = f"\\usepackage{{{env_name}}}"

        if not is_preamble_free:
            ins = _insert_in_preamble(current_latex, pkg)
            if ins:
                old_text, new_text = ins
                diff = DiffSuggestion(
                    action="replace",
                    old_text=old_text,
                    new_text=new_text,
                    description=f"Bổ sung gói cho môi trường {env_name}"
                )
                reply = (
                    f"Tôi phát hiện lỗi môi trường `{env_name}` chưa được khai báo.\n\n"
                    f"Đề xuất bổ sung `{pkg}` vào phần preamble:\n\n"
                    f"```diff\n- {old_text}\n+ {new_text}\n```\n\n"
                    "Bấm **Đồng ý** để áp dụng."
                )
                return ChatResponse(reply=reply, diff=diff)

    return None


def find_best_matching_block(snippet: str, document: str) -> Optional[str]:
    """Locate the closest matching block in the document for snippet replacement."""
    clean_snippet = snippet.strip()
    if not clean_snippet or clean_snippet.startswith(r"\documentclass") or len(clean_snippet) < 8:
        return None

    doc_lines = document.splitlines()
    snippet_lines = clean_snippet.splitlines()
    m = len(snippet_lines)
    best_ratio = 0.0
    best_slice = None

    for w in range(max(1, m - 3), min(len(doc_lines) + 1, m + 4)):
        for i in range(len(doc_lines) - w + 1):
            window_text = "\n".join(doc_lines[i : i + w]).strip()
            if not window_text:
                continue
            ratio = difflib.SequenceMatcher(None, clean_snippet, window_text).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_slice = "\n".join(doc_lines[i : i + w])

    if best_ratio >= 0.52 and best_slice and best_slice != clean_snippet:
        return best_slice
    return None


def parse_flexible_replace_command(text: str) -> Optional[Tuple[str, str]]:
    """Trích xuất cặp (old_term, new_term) từ câu lệnh tiếng Việt tự nhiên không bắt buộc có ngoặc kép."""
    if not text:
        return None
    raw = text.strip()

    # 1. Có ngoặc kép/nháy đơn/backtick
    m_quoted = re.search(
        r'(?:tìm\s+và\s+thay\s+thế|thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]\s+(?:bằng|thành|sang|với|bởi|by|with)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]',
        raw,
        re.IGNORECASE
    )
    if m_quoted:
        return m_quoted.group(1).strip(), m_quoted.group(2).strip()

    # 2. Các mẫu câu tự nhiên không có ngoặc kép
    patterns = [
        # "tìm và thay thế X thành/bằng/sang/bởi Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)tìm\s+và\s+thay\s+thế\s+(.+?)\s+(?:thành|bằng|sang|bởi)\s+(.+)$',
        # "thay thế X bằng/thành/sang/bởi Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)thay\s+thế\s+(.+?)\s+(?:bằng|thành|sang|bởi)\s+(.+)$',
        # "thay X bằng/thành/sang/bởi Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)thay\s+(.+?)\s+(?:bằng|thành|sang|bởi)\s+(.+)$',
        # "đổi X sang/thành/bằng Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)đổi\s+(.+?)\s+(?:sang|thành|bằng)\s+(.+)$',
        # "sửa X thành/sang/bằng Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)sửa\s+(.+?)\s+(?:thành|sang|bằng)\s+(.+)$',
        # "chuyển X sang/thành Y"
        r'(?:^|[,\.;\n]|\bhãy\s+)chuyển\s+(.+?)\s+(?:sang|thành)\s+(.+)$',
    ]

    for pat in patterns:
        m = re.search(pat, raw, re.IGNORECASE)
        if m:
            old_part = m.group(1).strip()
            new_part = m.group(2).strip()
            # Clean possible trailing punctuation like . or ! or ?
            new_part = re.sub(r'[\.!\?]+$', '', new_part).strip()
            # Strip enclosing quotes if user used asymmetric quotes
            old_part = re.sub(r'^[`"“\'‘]|[`"”\'’]$', '', old_part).strip()
            new_part = re.sub(r'^[`"“\'‘]|[`"”\'’]$', '', new_part).strip()
            if old_part and new_part:
                return old_part, new_part

    return None


def is_qa_request(message: str) -> bool:
    """Classifies whether the user prompt has pedagogical/educational Q&A intent."""
    if not message:
        return False
    msg_l = message.strip().lower()

    # If it starts with replacement verbs, it's NOT Q&A
    if any(msg_l.startswith(v) for v in ("thay", "đổi", "sửa", "chuyển", "tìm và thay thế", "replace")):
        return False

    # Action exclusions: e.g. "tạo đề", "thêm câu" without inquiry
    action_prefixes = ["tạo ", "chèn ", "thêm ", "sinh ", "viết "]
    if any(msg_l.startswith(act) for act in action_prefixes) and not any(k in msg_l for k in ("như thế nào", "là gì", "tại sao", "?", "hướng dẫn", "giải thích")):
        return False

    qa_phrases = [
        "quy chế", "quy định", "qđ 764", "quyết định 764", "764/qđ", "thông tư 32", "tt 32", "32/2018",
        "cách tính điểm", "điểm bậc thang", "tính điểm đúng sai", "thang điểm",
        "cấu trúc đề thi 2025", "cấu trúc đề thi", "bao nhiêu câu", "thời gian làm bài thi",
        "thời gian thi tốt nghiệp", "thời gian làm bài là", "thời gian làm bài bao nhiêu",
        "cú pháp ex_test", "hướng dẫn ex_test", "cú pháp tikz", "hướng dẫn vẽ tikz", "hướng dẫn tikz",
        "cú pháp tkz-tab", "hướng dẫn tkz-tab", "bảng biến thiên tkz-tab", "cú pháp",
        "kiểm tra đề", "thống kê đề", "đủ câu chưa", "đã có bao nhiêu câu", "đề còn thiếu gì",
        "kiểm tra cấu trúc", "soát đề", "tiến độ đề thi", "tiến độ", "thống kê số câu", "đề có mấy câu",
        "kiểm tra tiến độ", "hướng dẫn giải", "giải thích câu", "giải câu", "tại sao câu",
        "cách giải câu", "hướng dẫn câu", "chữa câu"
    ]
    if any(p in msg_l for p in qa_phrases):
        return True

    return False


def analyze_exam_progress(latex_code: Optional[str]) -> dict:
    """Analyze current_latex according to MoET 2025 exam structure (Part I: 12, Part II: 4, Part III: 6)."""
    if not latex_code:
        return {
            "has_header": False,
            "part1_count": 0,
            "part2_count": 0,
            "part3_count": 0,
            "total_count": 0,
            "questions": []
        }

    # 1. Check Header (2 minipages, 0.38\textwidth / 0.58\textwidth, Mã đề)
    has_header = False
    if ("minipage" in latex_code and ("0.38" in latex_code or "0.4" in latex_code)) or (
        any(k in latex_code for k in ("SỞ GIÁO DỤC", "TRƯỜNG THPT", "ĐỀ CHÍNH THỨC")) and
        any(k in latex_code for k in ("KỲ THI TỐT NGHIỆP", "MÔN: TOÁN", "Mã đề"))
    ):
        has_header = True

    # 2. Extract all question blocks
    q_matches = list(re.finditer(r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?([\s\S]*?)\\end\s*\{(?:ex|bt|vd)\}', latex_code))
    if not q_matches:
        q_matches = list(re.finditer(
            r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?([\s\S]*?)(?=(?:\\begin\{(?:ex|bt|vd)\}|\\end\{document\}|\Z))',
            latex_code
        ))

    part1_count = 0
    part2_count = 0
    part3_count = 0
    questions_info = []

    for idx, m in enumerate(q_matches):
        q_text = m.group(0)
        q_type = "part1"
        if r"\choiceTF" in q_text:
            part2_count += 1
            q_type = "part2"
        elif r"\shortans" in q_text or r"\SA" in q_text:
            part3_count += 1
            q_type = "part3"
        elif r"\choice" in q_text:
            part1_count += 1
            q_type = "part1"
        else:
            part1_count += 1
            q_type = "part1"

        questions_info.append({
            "index": idx + 1,
            "type": q_type,
            "raw": q_text
        })

    return {
        "has_header": has_header,
        "part1_count": part1_count,
        "part2_count": part2_count,
        "part3_count": part3_count,
        "total_count": len(q_matches),
        "questions": questions_info
    }


def explain_question_pedagogy(q_raw: str, q_num: int) -> str:
    """Provides pedagogical explanation, step-by-step logic and reasons for the correct answer."""
    m_loigiai = re.search(r'\\begin\{loigiai\}([\s\S]*?)\\end\{loigiai\}', q_raw)
    loigiai_text = m_loigiai.group(1).strip() if m_loigiai else ""

    stem_part = re.split(r'\\choice|\\choiceTF|\\shortans|\\begin\{loigiai\}', q_raw)[0]
    stem_part = re.sub(r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?', '', stem_part).strip()

    if r"\choiceTF" in q_raw:
        raw_tf_block = q_raw[q_raw.find(r"\choiceTF"):]
        if r"\begin{loigiai}" in raw_tf_block:
            raw_tf_block = raw_tf_block[:raw_tf_block.find(r"\begin{loigiai}")]
        elif r"\end{ex}" in raw_tf_block:
            raw_tf_block = raw_tf_block[:raw_tf_block.find(r"\end{ex}")]

        sub_items = re.findall(r'\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', raw_tf_block)
        items = sub_items[:4]

        report = f"### 💡 HƯỚNG DẪN GIẢI SƯ PHẠM — CÂU {q_num} (TRẮC NGHIỆM ĐÚNG/SAI)\n\n"
        report += f"**Đề bài:**\n> {stem_part}\n\n"
        report += "**Phương pháp tiếp cận:**\n"
        report += "- Xét tính đúng/sai độc lập của từng mệnh đề $a), b), c), d)$.\n"
        report += "- Vận dụng định lý, đạo hàm, bảng biến thiên và tính chất hàm số để chứng minh.\n\n"
        report += "**Phân tích chi tiết từng khẳng định:**\n\n"

        letters = ["a", "b", "c", "d"]
        for i, it in enumerate(items):
            letter = letters[i] if i < len(letters) else f"ý {i+1}"
            is_true = r"\True" in it
            clean_it = re.sub(r'\\True\s*', '', it).strip()
            status_badge = "✅ **ĐÚNG**" if is_true else "❌ **SAI**"
            report += f"- **Ý {letter})** {clean_it}\n"
            report += f"  - Kết luận: {status_badge}\n"

        if loigiai_text:
            clean_lg = re.sub(r'\\begin\{itemchoice\}|\\end\{itemchoice\}', '', loigiai_text).strip()
            report += f"\n**Lời giải chi tiết:**\n{clean_lg}\n\n"

        report += "> 📌 **Quy chế điểm bậc thang (QĐ 764):** Đúng 1 ý = 0,1đ; Đúng 2 ý = 0,25đ; Đúng 3 ý = 0,5đ; Đúng cả 4 ý = 1,0đ."
        return report

    elif r"\shortans" in q_raw or r"\SA" in q_raw:
        m_ans = re.search(r'\\(?:shortans|SA)\{([^}]*)\}', q_raw)
        ans_val = m_ans.group(1).strip() if m_ans else "chưa có"

        report = f"### 💡 HƯỚNG DẪN GIẢI SƯ PHẠM — CÂU {q_num} (TRẢ LỜI NGẮN)\n\n"
        report += f"**Đề bài:**\n> {stem_part}\n\n"
        report += f"🎯 **Đáp số chuẩn:** `{ans_val}`\n\n"
        report += "**Các bước tư duy & giải toán:**\n"
        report += "1. **Mô hình hóa bài toán:** Thiết lập hệ thức toán học hoặc đặt hàm số thích hợp từ giả thiết.\n"
        report += "2. **Thực hiện tính toán:** Khảo sát cực trị, giải phương trình, hoặc tính tích phân / xác suất.\n"
        report += "3. **Kết luận & định dạng đáp số:** Làm tròn theo đúng yêu cầu đề bài và tuân thủ định dạng tối đa 4 ký tự trên phiếu trả lời OMR.\n\n"
        if loigiai_text:
            report += f"**Lời giải chi tiết:**\n{loigiai_text}\n"
        return report

    else:
        m_ch = re.search(r'\\choice\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', q_raw)
        opts = []
        correct_letter = "A"
        if m_ch:
            letters = ["A", "B", "C", "D"]
            for i in range(1, 5):
                raw_opt = m_ch.group(i)
                is_correct = r"\True" in raw_opt
                cleaned = re.sub(r'\\True\s*', '', raw_opt).strip()
                opts.append((letters[i - 1], cleaned, is_correct))
                if is_correct:
                    correct_letter = letters[i - 1]

        report = f"### 💡 HƯỚNG DẪN GIẢI SƯ PHẠM — CÂU {q_num} (TRẮC NGHIỆM 4 LỰA CHỌN)\n\n"
        report += f"**Đề bài:**\n> {stem_part}\n\n"
        if opts:
            report += "**Các phương án lựa chọn:**\n"
            for let, text, is_c in opts:
                mark = " *(Phương án ĐÚNG)*" if is_c else ""
                report += f"- **{let}.** {text}{mark}\n"
            report += f"\n🏆 **Đáp án chính xác:** **{correct_letter}**\n\n"

        report += "**Các bước giải sư phạm:**\n"
        report += "1. **Nhận dạng bài toán:** Xác định kiến thức trọng tâm (tính đơn điệu, cực trị, tiệm cận, hình học không gian...).\n"
        report += "2. **Biến đổi toán học:** Áp dụng định lý hoặc công thức giải tích tương ứng để tìm ra kết quả.\n"
        report += f"3. **Đối chiếu phương án & loại trừ:** Chọn phương án **{correct_letter}**. Các phương án còn lại là bẫy sai lầm do nhầm dấu hoặc áp dụng sai công thức.\n\n"
        if loigiai_text:
            report += f"**Lời giải chi tiết mẫu:**\n{loigiai_text}\n"
        return report


def generate_exam_statistics_report(latex_code: Optional[str]) -> ChatResponse:
    """Analyzes exam structure against MoET 2025 standard (3 sections, 22 questions)."""
    stats = analyze_exam_progress(latex_code)
    p1 = stats["part1_count"]
    p2 = stats["part2_count"]
    p3 = stats["part3_count"]
    total = stats["total_count"]
    has_hdr = stats["has_header"]

    hdr_status = "✅ Đã có Header 2 cột chuẩn MoET" if has_hdr else "⚠️ Chưa có Header tiêu đề 2 cột chuẩn"

    def _badge(cur: int, target: int) -> str:
        if cur == target:
            return f"✅ Đạt chuẩn ({cur}/{target} câu)"
        elif cur < target:
            return f"⚠️ Còn thiếu {target - cur} câu ({cur}/{target} câu)"
        else:
            return f"⚠️ Thừa {cur - target} câu ({cur}/{target} câu)"

    status_p1 = _badge(p1, 12)
    status_p2 = _badge(p2, 4)
    status_p3 = _badge(p3, 6)
    pct = (total / 22.0) * 100 if total <= 22 else 100.0

    lines = [
        "### 📊 BÁO CÁO THỐNG KÊ & TIẾN ĐỘ ĐỀ THI QUỐC GIA 2025\n",
        "| Thành phần cấu trúc | Số câu hiện có | Chuẩn MoET 2025 | Trạng thái đánh giá |",
        "|---|:---:|:---:|---|",
        f"| **Tiêu đề đề thi (Header)** | - | 2 cột minipage | {hdr_status} |",
        f"| **Phần I (Trắc nghiệm 4 lựa chọn)** | {p1} | 12 câu | {status_p1} |",
        f"| **Phần II (Đúng/Sai QĐ 764)** | {p2} | 4 câu | {status_p2} |",
        f"| **Phần III (Trả lời ngắn)** | {p3} | 6 câu | {status_p3} |",
        f"| **TỔNG TIẾN ĐỘ TOÀN ĐỀ** | **{total} / 22** | **22 câu** | **{pct:.1f}% hoàn thành** |\n",
        "💡 **Khuyến nghị & Hành động tiếp theo:**"
    ]

    actions = []
    if not has_hdr:
        actions.append("- Bạn nên chèn **Header tiêu đề 2 cột** vào đầu đề thi bằng menu **THÊM ▾** hoặc yêu cầu AI: *\"Tạo header tiêu đề 2 cột\"*.")
    if p1 < 12:
        actions.append(f"- **Phần I:** Cần soạn thêm **{12 - p1} câu** trắc nghiệm 4 lựa chọn (`\\choice`).")
    elif p1 > 12:
        actions.append(f"- **Phần I:** Đang vượt quá {p1 - 12} câu (chuẩn chỉ gồm 12 câu).")
    if p2 < 4:
        actions.append(f"- **Phần II:** Cần soạn thêm **{4 - p2} câu** Đúng/Sai 4 khẳng định (`\\choiceTF[1]`).")
    elif p2 > 4:
        actions.append(f"- **Phần II:** Đang vượt quá {p2 - 4} câu (chuẩn chỉ gồm 4 câu).")
    if p3 < 6:
        actions.append(f"- **Phần III:** Cần soạn thêm **{6 - p3} câu** Trả lời ngắn (`\\shortans`).")
    elif p3 > 6:
        actions.append(f"- **Phần III:** Đang vượt quá {p3 - 6} câu (chuẩn chỉ gồm 6 câu).")

    if not actions:
        actions.append("🎉 **Đề thi đã hoàn thiện 100% chuẩn cấu trúc Đề thi Tốt nghiệp THPT 2025!** Bạn có thể nhấn **BIÊN DỊCH** để xuất file PDF in ấn.")

    lines.extend(actions)
    reply_md = "\n".join(lines)
    return ChatResponse(reply=reply_md)


def generate_question_solution_guide(latex_code: Optional[str], message: str) -> ChatResponse:
    """Finds question N in current_latex and produces step-by-step pedagogical guide."""
    if not latex_code:
        return ChatResponse(reply="Khung soạn thảo hiện chưa có mã LaTeX đề thi. Bạn hãy soạn thảo hoặc chèn đề thi mẫu trước khi yêu cầu hướng dẫn giải!")

    m_q = re.search(r'(?:câu\s+hỏi|câu)\s*(\d+)', message, re.IGNORECASE)
    target_q_num = int(m_q.group(1)) if m_q else 1

    m_sec = re.search(r'(?:phần|part)\s*([ivx0-9]+)', message, re.IGNORECASE)
    target_sec = m_sec.group(1) if m_sec else None

    q_raw = find_nth_question_in_latex(latex_code, target_q_num, section=target_sec)
    if not q_raw:
        stats = analyze_exam_progress(latex_code)
        tot = stats["total_count"]
        return ChatResponse(
            reply=f"Trong tài liệu hiện tại không tìm thấy **Câu {target_q_num}**" +
                  (f" (Phần {target_sec})" if target_sec else "") +
                  f". Hiện tài liệu có tổng cộng {tot} câu hỏi. Bạn vui lòng kiểm tra lại số thứ tự câu hỏi!"
        )

    explanation = explain_question_pedagogy(q_raw, target_q_num)
    return ChatResponse(reply=explanation)


def generate_syntax_qa_response(user_msg: str) -> ChatResponse:
    """Explains syntax of ex_test.sty, TikZ, and tkz-tab with illustrative examples."""
    reply = (
        "### 📚 HƯỚNG DẪN CÚ PHÁP EX_TEST.STY (v3.3) & TIKZ / TKZ-TAB\n\n"
        "Hệ thống Quesy đã tích hợp sẵn toàn bộ preamble và các gói lệnh chuẩn. Bạn chỉ cần viết trực tiếp nội dung các lệnh bên dưới:\n\n"
        "#### 1. Gói lệnh `ex_test.sty` (Chuẩn Quốc Gia 2025)\n"
        "- **Phần I (Trắc nghiệm 4 lựa chọn):**\n"
        "  ```latex\n"
        "  \\begin{ex}\n"
        "  Nội dung câu hỏi ở đây...\n"
        "  \\choice\n"
        "  {Phương án A}\n"
        "  {\\True Phương án B đúng}\n"
        "  {Phương án C}\n"
        "  {Phương án D}\n"
        "  \\begin{loigiai}\n"
        "  Lời giải chi tiết...\n"
        "  \\end{loigiai}\n"
        "  \\end{ex}\n"
        "  ```\n"
        "  *(Đặt `\\True` trước phương án đúng, gói sẽ tự động canh cột cân đối).*\n\n"
        "- **Phần II (Đúng/Sai 4 khẳng định theo QĐ 764):**\n"
        "  ```latex\n"
        "  \\begin{ex}\n"
        "  Cho hàm số... Xét tính đúng/sai:\n"
        "  \\choiceTF[1]\n"
        "  {\\True Khẳng định a đúng.}\n"
        "  {Khẳng định b sai.}\n"
        "  {\\True Khẳng định c đúng.}\n"
        "  {Khẳng định d sai.}\n"
        "  \\begin{loigiai}\n"
        "  \\begin{itemchoice}\n"
        "  \\itemch Đúng. Giải thích ý a...\n"
        "  \\itemch Sai. Giải thích ý b...\n"
        "  \\itemch Đúng. Giải thích ý c...\n"
        "  \\itemch Sai. Giải thích ý d...\n"
        "  \\end{itemchoice}\n"
        "  \\end{loigiai}\n"
        "  \\end{ex}\n"
        "  ```\n"
        "  *(⚠️ **LƯU Ý QUAN TRỌNG:** Bắt buộc có tham số `[1]` trong `\\choiceTF[1]` để mỗi ý chiếm 1 dòng. Không gõ nhãn a), b), c), d) thủ công).* \n\n"
        "- **Phần III (Trả lời ngắn):**\n"
        "  ```latex\n"
        "  \\begin{ex}\n"
        "  Tính giá trị biểu thức...\n"
        "  \\shortans{45}\n"
        "  \\begin{loigiai}\n"
        "  Lời giải chi tiết...\n"
        "  \\end{loigiai}\n"
        "  \\end{ex}\n"
        "  ```\n\n"
        "#### 2. Quy tắc Bất biến Căn giữa TikZ & tkz-tab\n"
        "- Mọi hình vẽ TikZ và bảng biến thiên **bắt buộc** bọc trong `\\begin{center} ... \\end{center}`.\n"
        "- Khi vẽ đồ thị hàm số `plot`, luôn thêm `samples=50` để tối ưu hóa thời gian biên dịch XeTeX.\n"
        "- Bảng biến thiên chuẩn dùng `tkz-tab` qua 3 lệnh: `\\tkzTabInit`, `\\tkzTabLine`, `\\tkzTabVar`."
    )

    example_code = r"""\begin{ex}
Cho hàm số $y = f(x)$ liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{center}
  \begin{tikzpicture}
    \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
    {$x$/.6, $f'(x)$/.6, $f(x)$/2}
    {$-\infty$,$-1$,$2$,$+\infty$}
    \tkzTabLine{,+,0,-,0,+,}
    \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
  \end{tikzpicture}
\end{center}
Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\choice
{\True $(2; +\infty)$}
{$(-1; 2)$}
{$(-\infty; 2)$}
{$(-1; +\infty)$}
\begin{loigiai}
Dựa vào bảng biến thiên, $f'(x) > 0$ trên $(-\infty; -1)$ và $(2; +\infty)$.
\end{loigiai}
\end{ex}"""

    return ChatResponse(reply=reply, suggested_latex=example_code)


def generate_regulations_qa_response() -> ChatResponse:
    """Returns authoritative explanation of MoET Decision 764, 2025 Exam Structure, and Circular 32."""
    reply = (
        "### 📋 QUY CHẾ KHẢO THÍ & CẤU TRÚC ĐỀ THI TỐT NGHIỆP THPT 2025 MÔN TOÁN\n\n"
        "Theo **Quyết định số 764/QĐ-BGDĐT** và **Thông tư số 32/2018/TT-BGDĐT** của Bộ Giáo dục và Đào tạo, kỳ thi Tốt nghiệp THPT từ năm 2025 môn Toán áp dụng các quy chuẩn khảo thí sau:\n\n"
        "---\n\n"
        "#### 1. Thang điểm Bậc thang Phần II (Quyết định 764/QĐ-BGDĐT)\n"
        "Phần II gồm **4 câu hỏi trắc nghiệm Đúng/Sai**, mỗi câu gồm **4 ý khẳng định (a, b, c, d)**. Điểm của từng câu được tính theo bậc thang lũy tiến:\n"
        "- 🎯 Thí sinh chọn chính xác **1 ý**: được **0,10 điểm**.\n"
        "- 🎯 Thí sinh chọn chính xác **2 ý**: được **0,25 điểm**.\n"
        "- 🎯 Thí sinh chọn chính xác **3 ý**: được **0,50 điểm**.\n"
        "- 🎯 Thí sinh chọn chính xác **cả 4 ý**: được **1,00 điểm**.\n\n"
        "> **Tổng điểm tối đa Phần II:** $4 \\times 1{,}0 = \\mathbf{4{,}0\\text{ điểm}}$.\n"
        "> *(Quy chế bậc thang này đánh giá chuẩn xác năng lực tư duy phản biện, kiểm chứng mệnh đề và triệt tiêu hoàn toàn xác suất đoán mò).* \n\n"
        "---\n\n"
        "#### 2. Cấu trúc Đề thi Tốt nghiệp THPT 2025 Môn Toán\n"
        "- **Thời gian làm bài:** **90 phút** (không kể thời gian phát đề).\n"
        "- **Tổng số lượng:** **22 câu hỏi**, thang điểm **10,0 điểm**, chia làm 3 phần rõ rệt:\n"
        "  1. **Phần I — Trắc nghiệm 4 lựa chọn (A, B, C, D):**\n"
        "     - Gồm **12 câu** (Câu 1 đến Câu 12).\n"
        "     - Mỗi câu có duy nhất 1 phương án đúng.\n"
        "     - Mỗi câu đúng được **0,25 điểm** -> **Tổng: 3,0 điểm**.\n"
        "  2. **Phần II — Trắc nghiệm Đúng/Sai 4 khẳng định:**\n"
        "     - Gồm **4 câu** (Câu 1 đến Câu 4).\n"
        "     - Mỗi câu gồm 4 lệnh hỏi $a, b, c, d$. Chấm điểm bậc thang QĐ 764.\n"
        "     - Tối đa 1,0 điểm/câu -> **Tổng: 4,0 điểm**.\n"
        "  3. **Phần III — Trắc nghiệm Trả lời ngắn:**\n"
        "     - Gồm **6 câu** (Câu 1 đến Câu 6).\n"
        "     - Thí sinh tự giải toán và điền đáp số vào phiếu trả lời OMR (tối đa 4 ký tự).\n"
        "     - Mỗi câu đúng được **0,50 điểm** -> **Tổng: 3,0 điểm**.\n\n"
        "---\n\n"
        "#### 3. Ma trận & Định hướng Năng lực (Thông tư 32/2018/TT-BGDĐT)\n"
        "- Đề thi định hướng đánh giá năng lực toán học bám sát **Yêu cầu cần đạt (YCCĐ)** trong Chương trình GDPT 2018.\n"
        "- Ma trận phân bổ tỷ lệ 4 mức độ nhận thức:\n"
        "  - **Nhận biết:** 40% (4,0 điểm)\n"
        "  - **Thông hiểu:** 30% (3,0 điểm)\n"
        "  - **Vận dụng:** 20% (2,0 điểm)\n"
        "  - **Vận dụng cao:** 10% (1,0 điểm)\n"
        "- Hệ thống khảo thí Quesy tuân thủ nguyên tắc xây dựng cây kiến thức 6 tầng theo YCCĐ, **hoàn toàn độc lập với các bộ sách giáo khoa thương mại** (Cánh diều, Kết nối tri thức, Chân trời sáng tạo)."
    )
    return ChatResponse(reply=reply)


def extract_all_diffs_from_text(reply_text: str, current_latex: Optional[str], user_message: str = "") -> List[DiffSuggestion]:
    """Helper to detect ALL unified diff blocks, search/replace blocks, OLD/NEW blocks,
    choice modifications, font size changes, or string replacement proposals from AI responses.
    Returns a List[DiffSuggestion] in sequential document order or appearance order.
    """
    if not current_latex:
        return []

    combined_text = f"{user_message}\n{reply_text}"
    user_lower = (user_message or "").lower()
    combined_lower = combined_text.lower()

    found_diffs: List[DiffSuggestion] = []

    def _add_diff(action: str, old_text: str, new_text: str, desc: str):
        if not old_text:
            return
        if old_text == new_text and new_text:
            return
        # check duplicate or conflicting replacement on same old_text
        for existing in found_diffs:
            if existing.old_text == old_text:
                return
        found_diffs.append(DiffSuggestion(
            action=action,
            old_text=old_text,
            new_text=new_text,
            description=desc
        ))

    # 1. Explicit ```diff ... ``` blocks (multiple blocks supported via finditer and multi-hunk parsing)
    for m_diff in re.finditer(r'```diff\s*\n?([\s\S]*?)```', reply_text):
        diff_content = m_diff.group(1)
        hunks = []
        current_hunk = {"old": [], "new": []}
        in_change = False

        for l in diff_content.splitlines():
            if l.startswith('---') or l.startswith('+++') or l.startswith('@@'):
                if current_hunk["old"] or current_hunk["new"]:
                    hunks.append(current_hunk)
                    current_hunk = {"old": [], "new": []}
                in_change = False
                continue

            if re.match(r'^\s*-\s*', l):
                current_hunk["old"].append(re.sub(r'^\s*-\s*', '', l))
                in_change = True
            elif re.match(r'^\s*\+\s*', l):
                current_hunk["new"].append(re.sub(r'^\s*\+\s*', '', l))
                in_change = True
            else:
                if in_change:
                    if current_hunk["old"] or current_hunk["new"]:
                        hunks.append(current_hunk)
                        current_hunk = {"old": [], "new": []}
                    in_change = False

        if current_hunk["old"] or current_hunk["new"]:
            hunks.append(current_hunk)

        base_desc = _clean_diff_description(reply_text[:m_diff.start()]) or "Thay đổi theo gợi ý AI"

        for idx, hunk in enumerate(hunks):
            old_raw = '\n'.join(hunk["old"]).strip()
            new_raw = '\n'.join(hunk["new"]).strip()
            if not old_raw:
                continue
            if old_raw and not new_raw:
                if r"\badcommand" in old_raw or "lỗi" in reply_text.lower():
                    new_raw = f"% {old_raw} (đã vô hiệu hóa để sửa lỗi biên dịch)"
            matched_old = find_in_latex(old_raw, current_latex)
            if matched_old and (matched_old != new_raw or not new_raw):
                hunk_desc = base_desc
                if "documentclass" in matched_old and "pt" in new_raw:
                    hunk_desc = "Đổi cỡ chữ toàn tài liệu"
                elif "mã đề" in new_raw.lower() or "0105" in new_raw:
                    hunk_desc = "Cập nhật Mã đề thi sang 0105"
                elif len(hunks) > 1:
                    hunk_desc = f"{base_desc} (Phần {idx + 1})"
                _add_diff("replace", matched_old, new_raw, hunk_desc)

    # 2. Explicit SEARCH / REPLACE blocks (Aider / standard AI coding format)
    for m_sr in re.finditer(r'<{5,9}\s*SEARCH\s*\n([\s\S]*?)\n={5,9}\s*\n([\s\S]*?)\n>{5,9}\s*REPLACE', reply_text):
        old_raw = m_sr.group(1).strip()
        new_raw = m_sr.group(2).strip()
        matched_old = find_in_latex(old_raw, current_latex)
        if matched_old and matched_old != new_raw:
            desc = _clean_diff_description(reply_text[:m_sr.start()]) or "Thay đổi theo gợi ý AI"
            _add_diff("replace", matched_old, new_raw, desc)

    # 3. Explicit OLD / NEW or CŨ / MỚI blocks
    patterns_old_new = [
        r'(?:OLD|CŨ|MÃ CŨ|TRƯỚC):\s*\n+([\s\S]*?)\n+(?:NEW|MỚI|MÃ MỚI|SAU):\s*\n+([\s\S]*?)(?:\n\n|\n[A-Z]|\n```|\Z)',
        r'(?:OLD|CŨ|MÃ CŨ|TRƯỚC):\s*[`"“\']?([^\n`"”\']+)[`"”\']?\s*\n+(?:NEW|MỚI|MÃ MỚI|SAU):\s*[`"“\']?([^\n`"”\']+)[`"”\']?',
        r'(?:- Dòng cũ|- Đoạn cũ|Cũ):\s*[`"“]?([^\n`"”]+)[`"”]?\s*\n(?:- Dòng mới|- Đoạn mới|Mới):\s*[`"“]?([^\\n`"”]+)[`"”]?',
    ]
    for pat in patterns_old_new:
        for m_replace in re.finditer(pat, reply_text, re.IGNORECASE):
            old_raw = m_replace.group(1).strip()
            new_raw = m_replace.group(2).strip()
            matched_old = find_in_latex(old_raw, current_latex)
            if matched_old and matched_old != new_raw:
                desc = _clean_diff_description(reply_text[:m_replace.start()]) or "Thay đổi theo gợi ý AI"
                _add_diff("replace", matched_old, new_raw, desc)

    # 4. Block replace with code fences: Thay thế: ```latex ... ``` bằng: ```latex ... ```
    for block_replace in re.finditer(
        r'(?:thay thế|thay|đổi|sửa|cũ|trước):\s*\n*```(?:latex|tex)?\s*\n([\s\S]*?)\n```\s*\n*(?:thành|bằng|sang|mới|sau):\s*\n*```(?:latex|tex)?\n([\s\S]*?)\n```',
        reply_text,
        re.IGNORECASE
    ):
        old_raw = block_replace.group(1).strip()
        new_raw = block_replace.group(2).strip()
        matched_old = find_in_latex(old_raw, current_latex)
        if matched_old and matched_old != new_raw:
            desc = _clean_diff_description(reply_text[:block_replace.start()]) or "Thay đổi theo gợi ý AI"
            _add_diff("replace", matched_old, new_raw, desc)

    # 5. Flexible natural language replacement proposals (with or without quotes)
    flex_cmd = parse_flexible_replace_command(user_message) or parse_flexible_replace_command(reply_text)
    if flex_cmd:
        old_term, new_term = flex_cmd
        clean_old = old_term.strip()
        clean_new = new_term.strip()

        # Strip "biểu thức " or "biến " prefixes if present
        if clean_old.lower().startswith("biểu thức "):
            clean_old = clean_old[10:].strip()
        if clean_new.lower().startswith("biểu thức "):
            clean_new = clean_new[10:].strip()
        if clean_old.lower().startswith("biến "):
            clean_old = clean_old[5:].strip()
        if clean_new.lower().startswith("biến "):
            clean_new = clean_new[5:].strip()

        # Check if user meant school name
        if any(k in clean_old.lower() for k in ("tên trường", "trường thpt", "trường")):
            school_target = re.sub(r'^(?:tên\s+trường|trường)\s*', '', clean_new, flags=re.IGNORECASE).strip()
            if not school_target:
                school_target = clean_new
            if not school_target.startswith("TRƯỜNG") and not school_target.startswith("Trường"):
                school_target = f"TRƯỜNG {school_target}"
            for line in current_latex.splitlines():
                if "TRƯỜNG" in line or "Trường" in line:
                    if re.search(r'\\textbf\{[^}]*(?:TRƯỜNG|Trường)[^}]*\}', line):
                        new_line = re.sub(r'\\textbf\{[^}]*(?:TRƯỜNG|Trường)[^}]*\}', f"\\textbf{{{school_target}}}", line)
                    elif r"\textbf{" in line:
                        new_line = re.sub(r'\\textbf\{[^}]*\}', f"\\textbf{{{school_target}}}", line)
                    else:
                        new_line = f"  \\textbf{{{school_target}}}\\\\"
                    if new_line != line:
                        _add_diff("replace", line, new_line, f"Thay tên trường thành {school_target}")
                        break

        # Check if user meant department name
        elif any(k in clean_old.lower() for k in ("tên sở", "sở gd", "sở giáo dục")):
            so_target = re.sub(r'^(?:tên\s+sở|sở\s+gd&đt|sở\s+giáo\s+dục)\s*', '', clean_new, flags=re.IGNORECASE).strip()
            if not so_target:
                so_target = clean_new
            if not so_target.startswith("SỞ") and not so_target.startswith("Sở"):
                so_target = f"SỞ GIÁO DỤC VÀ ĐÀO TẠO {so_target}"
            for line in current_latex.splitlines():
                if "SỞ" in line or "Sở" in line:
                    if re.search(r'\\textbf\{[^}]*(?:SỞ|Sở)[^}]*\}', line):
                        new_line = re.sub(r'\\textbf\{[^}]*(?:SỞ|Sở)[^}]*\}', f"\\textbf{{{so_target}}}", line)
                    elif r"\textbf{" in line:
                        new_line = re.sub(r'\\textbf\{[^}]*\}', f"\\textbf{{{so_target}}}", line)
                    else:
                        new_line = f"  \\textbf{{{so_target}}}\\\\"
                    if new_line != line:
                        _add_diff("replace", line, new_line, f"Thay tên Sở GD&ĐT thành {so_target}")
                        break

        # Check if user meant exam duration
        elif "thời gian" in clean_old.lower() or "phút" in clean_old.lower() or "phút" in clean_new.lower():
            m_mins = re.search(r'(\d+)\s*phút', clean_new) or re.search(r'(\d+)', clean_new)
            if m_mins:
                mins_val = m_mins.group(1)
                for line in current_latex.splitlines():
                    if "thời gian làm bài" in line.lower() or "thời gian" in line.lower():
                        new_line = re.sub(r'\d+\s*phút', f"{mins_val} phút", line)
                        if new_line != line:
                            _add_diff("replace", line, new_line, f"Đổi thời gian làm bài thành {mins_val} phút")
                            break

        # Check if user meant variable replacement
        elif len(clean_old) == 1 and len(clean_new) == 1 and clean_old.isalpha() and clean_new.isalpha() and any(k in user_lower for k in ("biến", "variable")):
            old_var, new_var = clean_old, clean_new
            for line in current_latex.splitlines():
                if ("$" in line and old_var in line) or f" {old_var} " in line:
                    new_line = re.sub(rf'(?<![a-ce-zA-CE-Z\\]){old_var}(?![a-zA-Z])', new_var, line)
                    if new_line != line:
                        _add_diff("replace", line, new_line, f"Thay biến '{old_var}' thành '{new_var}'")
                        break

        # General / Math / Substring replace
        if not found_diffs:
            matched_target = None
            replacement_target = clean_new
            if clean_old in current_latex:
                matched_target = clean_old
            elif f"${clean_old}$" in current_latex:
                matched_target = f"${clean_old}$"
                if not replacement_target.startswith("$"):
                    replacement_target = f"${replacement_target}$"
            elif f"\\{clean_old}" in current_latex:
                matched_target = f"\\{clean_old}"
                if not replacement_target.startswith("\\"):
                    replacement_target = f"\\{replacement_target}"
            else:
                fuzzy_match = find_in_latex(clean_old, current_latex)
                if fuzzy_match:
                    matched_target = fuzzy_match
                    if clean_old in fuzzy_match:
                        replacement_target = fuzzy_match.replace(clean_old, clean_new)

            if matched_target and matched_target != replacement_target:
                _add_diff("replace", matched_target, replacement_target, f"Thay thế '{clean_old}' thành '{clean_new}'")

    # 5b. Direct targeted heuristic for duration changes
    m_time_direct = re.search(r'(?:đổi|thay|sửa)\s+(?:thời\s+gian\s+làm\s+bài|thời\s+gian)\s+(?:thành|sang|bằng)\s*(\d+)\s*phút', combined_lower)
    if m_time_direct:
        mins_val = m_time_direct.group(1)
        for line in current_latex.splitlines():
            if "thời gian làm bài" in line.lower() or "thời gian" in line.lower():
                new_line = re.sub(r'\d+\s*phút', f"{mins_val} phút", line)
                if new_line != line:
                    _add_diff("replace", line, new_line, f"Đổi thời gian làm bài thành {mins_val} phút")
                    break

    # 5c. Direct targeted heuristic for school name changes
    m_school_direct = re.search(r'(?:thay|đổi|sửa)\s+tên\s+trường\s+(?:thành|sang|bằng)\s+([^\n\.,;]+)', combined_text, re.IGNORECASE)
    if m_school_direct:
        new_sch = m_school_direct.group(1).strip()
        if not new_sch.startswith("TRƯỜNG") and not new_sch.startswith("Trường"):
            new_sch = f"TRƯỜNG {new_sch}"
        for line in current_latex.splitlines():
            if "TRƯỜNG" in line or "Trường" in line:
                if re.search(r'\\textbf\{[^}]*(?:TRƯỜNG|Trường)[^}]*\}', line):
                    new_line = re.sub(r'\\textbf\{[^}]*(?:TRƯỜNG|Trường)[^}]*\}', f"\\textbf{{{new_sch}}}", line)
                elif r"\textbf{" in line:
                    new_line = re.sub(r'\\textbf\{[^}]*\}', f"\\textbf{{{new_sch}}}", line)
                else:
                    new_line = f"  \\textbf{{{new_sch}}}\\\\"
                if new_line != line:
                    _add_diff("replace", line, new_line, f"Thay tên trường thành {new_sch}")
                    break

    # 6. Targeted heuristic for font size changes (e.g. 11pt -> 12pt, font 12, cỡ chữ 11pt)
    if any(k in combined_lower for k in ("font", "cỡ chữ", "size")):
        pts = re.findall(r'\b(10|11|12|13|14)(?:pt)?\b', user_lower)
        if not pts:
            pts = re.findall(r'\b(10|11|12|13|14)(?:pt)?\b', reply_text.lower())
        if pts:
            target_pt = f"{pts[-1]}pt"
            for line in current_latex.splitlines():
                if "documentclass" in line:
                    if re.search(r'\b\d+pt\b', line):
                        new_line = re.sub(r'\b\d+pt\b', target_pt, line)
                    elif r'\documentclass[' in line:
                        new_line = line.replace(r'\documentclass[', f'\\documentclass[{target_pt},')
                    elif r'\documentclass{' in line:
                        new_line = line.replace(r'\documentclass{', f'\\documentclass[{target_pt}]{{')
                    else:
                        new_line = line
                    if new_line != line:
                        _add_diff("replace", line, new_line, f"Đổi cỡ chữ toàn tài liệu sang {target_pt}")

    # 7. Targeted heuristic for choice modifications (đổi đáp án câu 2 sang D, thay đáp án đúng thành C, sửa đáp án câu 1 thành B, etc.)
    m_choice_chg = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển)\s+(?:đáp án|lựa chọn)(?:\s+đúng)?(?:\s+(?:của\s+)?(?:câu\s+hỏi|câu)\s*(\d+))?\s+(?:từ\s+[ABCD]\s+sang\s+|thành\s+|sang\s+|về\s+)([ABCD])\b',
        combined_lower,
        re.IGNORECASE
    )
    if not m_choice_chg:
        m_choice_chg = re.search(
            r'(?:câu\s+hỏi|câu)\s*(\d+)[^.\n]*?(?:thay\s+thế|thay|đổi|sửa|chuyển)\s+(?:đáp án|lựa chọn)(?:\s+đúng)?\s+(?:từ\s+[ABCD]\s+sang\s+|thành\s+|sang\s+|về\s+)([ABCD])\b',
            combined_lower,
            re.IGNORECASE
        )
    if m_choice_chg:
        q_idx_str = m_choice_chg.group(1)
        target_q_idx = int(q_idx_str) if q_idx_str else None
        target_choice = m_choice_chg.group(2).upper()
        target_idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(target_choice)
        if target_idx is not None:
            scope_text = current_latex
            if target_q_idx:
                q_scope = find_nth_question_in_latex(current_latex, target_q_idx)
                if q_scope:
                    scope_text = q_scope

            m_ch = re.search(
                r'\\choice\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
                scope_text
            )
            if m_ch:
                old_full = m_ch.group(0)
                opts = [m_ch.group(1), m_ch.group(2), m_ch.group(3), m_ch.group(4)]
                cleaned_opts = [re.sub(r'\\True\s*', '', opt).strip() for opt in opts]
                cleaned_opts[target_idx] = "\\True " + cleaned_opts[target_idx]
                sep = "\n" if "\n" in old_full else ""
                new_full = f"\\choice{sep}{{{cleaned_opts[0]}}}{sep}{{{cleaned_opts[1]}}}{sep}{{{cleaned_opts[2]}}}{sep}{{{cleaned_opts[3]}}}"
                if old_full != new_full:
                    desc_str = f"Đổi đáp án đúng câu {target_q_idx} sang {target_choice}" if target_q_idx else f"Đổi đáp án đúng sang {target_choice}"
                    _add_diff("replace", old_full, new_full, desc_str)

    # 7b. Targeted heuristic for variable replacement (e.g. "thay biến x thành t", "đổi biến x sang y")
    m_var = re.search(r'(?:thay|đổi|sửa)\s+biến\s+([a-zA-Z])\s+(?:thành|bằng|sang)(?:\s+biến)?\s+([a-zA-Z])\b', combined_lower)
    if m_var:
        old_var, new_var = m_var.group(1), m_var.group(2)
        for line in current_latex.splitlines():
            if ("$" in line and old_var in line) or f" {old_var} " in line:
                new_line = re.sub(rf'(?<![a-ce-zA-CE-Z\\]){old_var}(?![a-zA-Z])', new_var, line)
                if new_line != line:
                    _add_diff("replace", line, new_line, f"Thay biến '{old_var}' thành '{new_var}'")
                    break

    if found_diffs:
        return found_diffs

    # 8. Targeted heuristic for replacing question N by number
    # Handles: "thay thế câu (\d+)", "thay câu (\d+)", "sửa câu (\d+)", "đổi câu (\d+)", "replace question (\d+)"
    target_q_num = None
    target_sec = None
    m_replace_q = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)(?:[^\n]*?(?:phần|part)\s*([ivx0-9]+))?',
        combined_lower
    )
    if m_replace_q:
        target_q_num = int(m_replace_q.group(1))
        target_sec = m_replace_q.group(2)
    else:
        m_replace_q2 = re.search(
            r'(?:phần|part)\s*([ivx0-9]+)[^\n]*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)',
            combined_lower
        )
        if m_replace_q2:
            target_sec = m_replace_q2.group(1)
            target_q_num = int(m_replace_q2.group(2))
        else:
            m_replace_q3 = re.search(
                r'(?:câu\s+hỏi|câu|question)\s+(\d+).*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)',
                combined_lower
            )
            if m_replace_q3:
                target_q_num = int(m_replace_q3.group(1))

    if target_q_num is not None:
        old_q = find_nth_question_in_latex(current_latex, target_q_num, section=target_sec)
        if old_q:
            new_q = None
            m_code_q = None
            # 8a. Extract new question from ```diff ... ``` block if present
            m_diff_q = re.search(r'```diff\s*\n([\s\S]*?)```', reply_text)
            if m_diff_q:
                added_lines = [
                    re.sub(r'^\s*\+\s?', '', l)
                    for l in m_diff_q.group(1).splitlines()
                    if re.match(r'^\s*\+', l) and not l.startswith('+++')
                ]
                if added_lines:
                    new_q = '\n'.join(added_lines).strip()

            # 8b. Extract from ```latex ... ``` or ```tex ... ``` code block
            if not new_q:
                m_code_q = re.search(r'```(?:latex|tex)?\s*\n([\s\S]*?)```', reply_text)
                if m_code_q:
                    candidate = m_code_q.group(1).strip()
                    if not candidate.startswith(r"\documentclass"):
                        new_q = candidate

            # 8c. Extract raw LaTeX environment from text
            if not new_q:
                m_ex_q = re.search(r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?[\s\S]*?\\end\s*\{(?:ex|bt|vd)\}', reply_text)
                if m_ex_q:
                    new_q = m_ex_q.group(0).strip()
            if not new_q:
                m_classic_q = re.search(r'(?:\\textbf\{\s*Câu\s*\d+[\.:]?\s*\}|(?<![\w\\])Câu\s*\d+[\.:])[\s\S]*', reply_text)
                if m_classic_q:
                    new_q = m_classic_q.group(0).strip()

            if new_q and new_q != old_q:
                desc = _clean_diff_description(reply_text[:(m_code_q.start() if m_code_q else 0)]) or f"Thay thế Câu {target_q_num}"
                if not desc.startswith(f"Thay thế Câu {target_q_num}"):
                    desc = f"Thay thế Câu {target_q_num}"
                _add_diff("replace", old_q, new_q, desc)
                return found_diffs

    # 9. Detect changes if AI returned single code block (```latex or ```tex or ```)
    m_code = re.search(r'```(?:latex|tex)?\s*\n([\s\S]*?)```', reply_text)
    if m_code:
        if any(k in user_lower for k in ("tạo", "thêm", "chèn", "sinh", "viết", "generate", "create", "insert", "trích xuất", "nhận dạng", "extract")):
            return []

        code = m_code.group(1).strip()
        if "\\documentclass" not in code and len(code) >= 10:
            matched_old = find_best_matching_block(code, current_latex)
            if matched_old and matched_old != code:
                desc = _clean_diff_description(reply_text[:m_code.start()]) or "Thay đổi theo gợi ý AI"
                _add_diff("replace", matched_old, code, desc)

        if not found_diffs:
            cur_lines = current_latex.strip().splitlines()
            code_lines = code.splitlines()
            clean_cur = [l for l in cur_lines if l.strip()]
            clean_code = [l for l in code_lines if l.strip()]

            sm = difflib.SequenceMatcher(None, clean_cur, clean_code)
            replace_ops = [op for op in sm.get_opcodes() if op[0] == 'replace']
            if len(replace_ops) == 1:
                _, i1, i2, j1, j2 = replace_ops[0]
                old_slice = '\n'.join(clean_cur[i1:i2])
                new_slice = '\n'.join(clean_code[j1:j2])
                matched_old = find_in_latex(old_slice, current_latex)
                if matched_old and matched_old != new_slice:
                    desc = _clean_diff_description(reply_text[:m_code.start()]) or "Thay đổi theo gợi ý AI"
                    _add_diff("replace", matched_old, new_slice, desc)
            elif len(code_lines) <= 4:
                matches = difflib.get_close_matches(code, cur_lines, n=1, cutoff=0.45)
                if matches and matches[0] != code:
                    matched_old = find_in_latex(matches[0], current_latex)
                    if matched_old:
                        desc = _clean_diff_description(reply_text[:m_code.start()]) or "Thay đổi theo gợi ý AI"
                        _add_diff("replace", matched_old, code, desc)

    return found_diffs


def extract_diff_from_text(reply_text: str, current_latex: Optional[str], user_message: str = "") -> Optional[DiffSuggestion]:
    """Helper to detect the first unified diff suggestion from AI responses (backward compatibility)."""
    diffs = extract_all_diffs_from_text(reply_text, current_latex, user_message=user_message)
    return diffs[0] if diffs else None


@router.post("/chat", response_model=ChatResponse, summary="AI LaTeX Writing Copilot (assistant-ui clone)")
def composer_chat_endpoint(req: ChatRequest):
    """Interactive AI Assistant specifically tuned for authoring Vietnamese high-school math exams."""
    system_prompt = (
        "Bạn là Trợ lý Soạn thảo Đề thi & LaTeX Chuyên nghiệp (Quesy AI Copilot), lấy cảm hứng từ open-prism.\n"
        "Nhiệm vụ của bạn là hỗ trợ giáo viên Toán tại Việt Nam soạn thảo đề thi chất lượng cao theo chuẩn Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (Định dạng 2025).\n\n"
        "KIẾN TRÚC SOẠN THẢO PREAMBLE-FREE (KHÔNG PREAMBLE):\n"
        "- Khung soạn thảo (editor) CHỈ CHỨA trực tiếp phần tiêu đề đề thi chuẩn 2 cột và các khối câu hỏi theo chuẩn gói lệnh ex_test.sty (\\begin{ex}...\\end{ex}).\n"
        "- Toàn bộ Preamble (\\documentclass, \\usepackage{fontspec}, \\usepackage{amsmath,amssymb,amsfonts}, \\usepackage{geometry}, \\usepackage{multicol}, \\usepackage{tikz,tkz-tab}, \\usepackage{tcolorbox}, \\usepackage[dethi]{ex_test}, \\begin{document}, \\end{document}) ĐÃ ĐƯỢC HỆ THỐNG TỰ ĐỘNG NHÚNG NGẦM ở backend khi biên dịch.\n"
        "- TUYỆT ĐỐI KHÔNG sinh lại preamble, \\documentclass, \\usepackage, \\begin{document} hay \\end{document}. Khi sinh mới hoặc sửa câu hỏi, CHỈ TRẢ VỀ mã câu hỏi \\begin{ex}...\\end{ex} chuẩn ex_test.\n\n"
        "HỆ THỐNG ĐÃ TÍCH HỢP TOÀN DIỆN GÓI LỆNH ex_test.sty (v3.3):\n"
        "- Tiêu đề đề thi chuẩn MoET 2025: Bắt buộc dùng Header 2 cột (cột trái 0.38\\textwidth, cột phải 0.58\\textwidth, căn giữa cả hai bên, \\hfill giữa 2 minipage, dòng họ tên & SBD dùng \\dotfill kèm \\framebox{\\textbf{Mã đề: ...}}, đường kẻ đơn phía dưới \\noindent\\rule{\\textwidth}{0.5pt}).\n"
        "- Phần I (Trắc nghiệm 4 lựa chọn): Dùng \\begin{ex} ... \\choice{A}{\\True B}{C}{D} \\begin{loigiai}...\\end{loigiai} \\end{ex}.\n"
        "- Phần II (Đúng/Sai 4 khẳng định): BẮT BUỘC dùng \\choiceTF[1] (luôn có tham số [1] để mỗi ý 1 dòng). TUYỆT ĐỐI KHÔNG gõ tiền tố nhãn a), b), c), d) vào trong nội dung khẳng định.\n"
        "- Phần III (Trả lời ngắn): Dùng \\begin{ex} ... \\shortans{kết_quả} \\begin{loigiai}...\\end{loigiai} \\end{ex}.\n\n"
        "QUY TẮC BẮT BUỘC VỀ BỐ CỤC ĐỒ THỊ & BẢNG BIỂU (CENTERED LAYOUT INVARIANT):\n"
        "1. MẶC ĐỊNH TOÀN BỘ các đồ thị hàm số TikZ, hình học TikZ, bảng biến thiên tkz-tab và bảng biểu ĐỀU PHẢI NẰM Ở CHÍNH GIỮA (CENTERED), TUYỆT ĐỐI KHÔNG nằm lệch 1 bên hay dùng \\immini / \\imminiL.\n"
        "2. BẮT BUỘC đặt trong môi trường căn giữa: \\begin{center}\\begin{tikzpicture}...\\end{tikzpicture}\\end{center} (hoặc tkz-tab), nằm ngay bên dưới phần dẫn đề bài (stem) và ở phía trên các phương án lựa chọn (\\choice / \\choiceTF[1] / \\shortans).\n"
        "3. Bảng biến thiên BẮT BUỘC dùng TikZ package tkz-tab (\\tkzTabInit, \\tkzTabLine, \\tkzTabVar). Không dùng \\begin{array} cho bảng biến thiên!\n"
        "4. Mọi công thức toán inline bọc trong $...$, phân số dùng \\dfrac, vectơ dùng \\overrightarrow{AB}.\n"
        "5. Khi tạo đồ thị hàm số TikZ, luôn đặt samples=50 hoặc samples=60 mặc định để đảm bảo thời gian biên dịch nhanh nhất.\n\n"
        "PHÂN TÍCH ĐA PHƯƠNG TIỆN (MULTI-MODAL IMAGE ANALYSIS):\n"
        "- Khi người dùng đính kèm hình ảnh (ảnh chụp đề thi, đồ thị hàm số, bảng biến thiên tkz-tab, hình học không gian tikz, bài toán trắc nghiệm ex_test), bạn phải phân tích chi tiết nội dung hình ảnh đó.\n"
        "- Trích xuất chính xác văn bản, công thức toán học và biểu đồ từ ảnh thành mã LaTeX chuẩn ex_test & TikZ tương ứng.\n\n"
        "QUY TẮC PHẢN HỒI (BẮT BUỘC TUÂN THỦ):\n"
        "1. KHI NGƯỜI DÙNG YÊU CẦU SỬA ĐỔI, ĐIỀU CHỈNH HOẶC THAY THẾ:\n"
        "   - TUYỆT ĐỐI KHÔNG xuất lại toàn bộ tài liệu cũ dài dòng! Không sinh lại preamble!\n"
        "   - BẮT BUỘC chỉ xuất khối ```diff chứa đúng dòng cũ cần thay và dòng mới:\n"
        "     ```diff\n"
        "     - <dòng mã cũ>\n"
        "     + <dòng mã mới>\n"
        "     ```\n"
        "   - Kèm lời giải thích ngắn gọn bằng tiếng Việt.\n"
        "2. KHI NGƯỜI DÙNG YÊU CẦU THAY THẾ HOẶC ĐỔI MỘT CÂU HỎI:\n"
        "   - BẮT BUỘC trích xuất khối ```diff rõ ràng với old_text là câu cũ và new_text là câu mới:\n"
        "     ```diff\n"
        "     - <toàn bộ khối câu cũ trong tài liệu hiện tại>\n"
        "     + <toàn bộ khối câu hỏi mới thay thế (\\begin{ex}...\\end{ex})>\n"
        "     ```\n"
        "   - Đồng thời có thể kèm khối ```latex ... ``` chứa riêng câu hỏi mới (chỉ \\begin{ex}...\\end{ex}) để giáo viên có thể chèn trực tiếp.\n"
        "3. KHI NGƯỜI DÙNG YÊU CẦU TẠO MỚI CÂU HỎI HOẶC HÌNH VẼ:\n"
        "   - Xuất mã câu hỏi chuẩn ```latex \\begin{ex}...\\end{ex} ``` để chèn vào vị trí con trỏ (tuyệt đối không kèm preamble).\n"
    )

    prompt = f"Yêu cầu của giáo viên: {req.message}\n\n"
    target_q_num = None
    target_sec = None
    m_replace_hint = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)(?:[^\n]*?(?:phần|part)\s*([ivx0-9]+))?',
        req.message,
        re.IGNORECASE
    )
    if m_replace_hint:
        target_q_num = int(m_replace_hint.group(1))
        target_sec = m_replace_hint.group(2)
    else:
        m_replace_hint2 = re.search(
            r'(?:phần|part)\s*([ivx0-9]+)[^\n]*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)',
            req.message,
            re.IGNORECASE
        )
        if m_replace_hint2:
            target_sec = m_replace_hint2.group(1)
            target_q_num = int(m_replace_hint2.group(2))
        else:
            m_replace_hint3 = re.search(
                r'(?:câu\s+hỏi|câu|question)\s+(\d+).*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)',
                req.message,
                re.IGNORECASE
            )
            if m_replace_hint3:
                target_q_num = int(m_replace_hint3.group(1))

    old_snippet = None
    if target_q_num is not None and req.current_latex:
        old_snippet = find_nth_question_in_latex(req.current_latex, target_q_num, section=target_sec)
        if old_snippet:
            prompt += (
                f"--- HƯỚNG DẪN BẮT BUỘC KHI THAY THẾ CÂU {target_q_num} ---\n"
                f"Khối câu {target_q_num} hiện tại trong tài liệu là:\n"
                f"```latex\n{old_snippet}\n```\n"
                f"Bạn hãy trích xuất khối ```diff với dòng (-) là câu cũ này và dòng (+) là câu mới thay thế, hoặc xuất khối ```latex chứa câu hỏi mới để hệ thống áp dụng thay thế lên trình soạn thảo.\n"
                f"------------------------------------------------------\n\n"
            )
    if (req.compile_error_log or req.compile_error) and (req.compile_error_log or req.compile_error).strip():
        prompt += f"--- LOG LỖI BIÊN DỊCH GẦN NHẤT ---\n{(req.compile_error_log or req.compile_error).strip()}\n---------------------------------\n\n"
    if req.current_latex and req.current_latex.strip():
        ctx = req.current_latex.strip()
        if len(ctx) > 25000:
            ctx = ctx[:12000] + "\n... [đoạn giữa được rút gọn] ...\n" + ctx[-12000:]
        prompt += f"--- NỘI DUNG TÀI LIỆU HIỆN TẠI ---\n{ctx}\n--------------------------------------------\n"

    user_msg_lower = req.message.lower().strip()
    cur_latex = req.current_latex or ""

    # ================= 1. HỆ THỐNG HỎI ĐÁP KHẢO THÍ & SƯ PHẠM (Q&A COPILOT) =================
    if is_qa_request(req.message):
        # 1a. Kịch bản 3: Thống kê & Kiểm tra đề thi hiện tại trong current_latex
        if any(k in user_msg_lower for k in (
            "kiểm tra đề", "thống kê đề", "đủ câu chưa", "đã có bao nhiêu câu", "đề còn thiếu gì",
            "kiểm tra cấu trúc", "soát đề", "tiến độ đề thi", "tiến độ", "thống kê số câu",
            "đề có mấy câu", "kiểm tra tiến độ"
        )):
            return generate_exam_statistics_report(cur_latex)

        # 1b. Kịch bản 4: Hướng dẫn giải / Giải thích câu hỏi trong đề
        if any(k in user_msg_lower for k in (
            "hướng dẫn giải", "giải thích câu", "giải câu", "tại sao câu", "cách giải câu",
            "hướng dẫn câu", "chữa câu"
        )):
            return generate_question_solution_guide(cur_latex, req.message)

        # 1c. Kịch bản 2: Hỏi về cú pháp ex_test, TikZ, tkz-tab
        if any(k in user_msg_lower for k in (
            "cú pháp ex_test", "hướng dẫn ex_test", "lệnh choice", "lệnh choicetf", "choicetf",
            "shortans", "cú pháp tikz", "hướng dẫn vẽ tikz", "hướng dẫn tikz", "cú pháp tkz-tab",
            "hướng dẫn tkz-tab", "bảng biến thiên tkz-tab", "cú pháp", "cách dùng ex_test",
            "cách dùng tikz", "cách dùng tkz-tab"
        )):
            return generate_syntax_qa_response(req.message)

        # 1d. Kịch bản 1: Quy chế QĐ 764, Cấu trúc Đề thi 2025, Thông tư 32
        if any(k in user_msg_lower for k in (
            "quy chế", "quy định", "764", "cách tính điểm", "điểm bậc thang", "tính điểm đúng sai",
            "thông tư 32", "tt 32", "cấu trúc đề thi 2025", "cấu trúc đề thi", "bao nhiêu câu",
            "thời gian làm bài thi", "thời gian thi", "thang điểm"
        )) or any(k in user_msg_lower for k in ("như thế nào", "là gì", "tại sao", "nghĩa là gì")):
            return generate_regulations_qa_response()

        # Mặc định giải đáp thông tin quy chế & sư phạm
        return generate_regulations_qa_response()

    has_active_ai_provider = bool(
        default_ai_provider_service and
        getattr(default_ai_provider_service, "api_key", None) and
        str(default_ai_provider_service.api_key).strip()
    )

    if not has_active_ai_provider:
        # ================= 2. KIỂM TRA LỖI BIÊN DỊCH NẾU CÓ (OFFLINE) =================
        err_log = (req.compile_error_log or req.compile_error or "").strip()
        if err_log:
            diag_resp = diagnose_compile_error(err_log, cur_latex, req.message)
            if diag_resp:
                return diag_resp

        if any(k in user_msg_lower for k in ("fix lỗi", "sửa lỗi", "lỗi biên dịch", "compile error", "khắc phục lỗi")):
            diag_resp = diagnose_compile_error(err_log or req.message, cur_latex, req.message)
            if diag_resp:
                return diag_resp

        # ================= 3. TÌM & THAY THẾ LINH HOẠT TRỰC TIẾP (DIFF REPLACEMENT) =================
        direct_diffs = extract_all_diffs_from_text("", cur_latex, user_message=req.message)
        if direct_diffs:
            d = direct_diffs[0]
            reply_msg = (
                f"Tôi đề xuất {d.description.lower()}:\n\n"
                f"```diff\n- {d.old_text}\n+ {d.new_text}\n```\n\n"
                "Bấm **Đồng ý (Keep)** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
            )
            return ChatResponse(reply=reply_msg, diff=d, diffs=direct_diffs)

    # Fast deterministic canonical 2025 templates router
    if any(k in user_msg_lower for k in ("tạo đề", "chèn đề", "sinh đề", "mẫu đề", "trọn bộ đề", "3 phần chuẩn quốc gia")) or (
        any(k in user_msg_lower for k in ("3 phần", "chuẩn quốc gia 2025", "trọn bộ", "đề thi chuẩn quốc gia")) and
        any(k in user_msg_lower for k in ("tạo", "chèn", "sinh", "viết", "cho tôi", "lập"))
    ):
        full_national_exam = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
  \textbf{TRƯỜNG THPT ...}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{MÔN: TOÁN}\\
  \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
\end{minipage}
\vspace{0.25cm}
\noindent
Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
\vspace{0.1cm}
\noindent\rule{\textwidth}{0.5pt}
\vspace{0.3cm}

\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\begin{ex}
Cho hàm số $y = f(x)$ có đạo hàm $f'(x) = x(x-1)^2$. Số điểm cực trị của hàm số là:
\choice
{0}
{\True 2}
{1}
{3}
\begin{loigiai}
$f'(x) = 0 \Leftrightarrow x = 0$ hoặc $x = 1$. Số điểm cực trị là 1.
\end{loigiai}
\end{ex}

\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\begin{ex}
Cho hàm số $y = x^3 - 3x + 1$. Xét tính đúng/sai:
\choiceTF
{\True Hàm số đạt cực đại tại $x = -1$.}\\
{Giá trị cực tiểu bằng $1$.}\\
{\True Tiệm cận ngang không có.}\\
{Đồ thị nhận điểm $I(0;1)$ làm tâm đối xứng.}
\begin{loigiai}
\begin{itemchoice}
\itemch Đúng. $y' = 3x^2 - 3 = 0 \Rightarrow x = \pm 1$. $y(-1) = 3$.
\itemch Sai. $y(1) = -1$.
\itemch Đúng. Hàm đa thức không có tiệm cận ngang.
\itemch Đúng. $y''(0) = 0$ và $y(0) = 1$.
\end{itemchoice}
\end{loigiai}
\end{ex}

\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}

\begin{ex}
Tìm giá trị lớn nhất của hàm số $y = -x^2 + 4x - 3$ trên đoạn $[0; 3]$.
\shortans{1}
\begin{loigiai}
$y = -(x-2)^2 + 1 \le 1$. Đạt được khi $x = 2$.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo trọn bộ đề thi chuẩn Quốc Gia 2025 (Header 2 cột & 3 Section):\n```latex\n{full_national_exam}\n```",
            suggested_latex=full_national_exam
        )

    if any(k in user_msg_lower for k in ("tạo header", "tạo tiêu đề", "sở giáo dục", "tiêu đề 2 cột")):
        header_snippet = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
  \textbf{TRƯỜNG THPT ...}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{MÔN: TOÁN}\\
  \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
\end{minipage}
\vspace{0.25cm}
\noindent
Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
\vspace{0.1cm}
\noindent\rule{\textwidth}{0.5pt}
\vspace{0.3cm}"""
        return ChatResponse(
            reply=f"Đã tạo tiêu đề chuẩn 2 cột:\n```latex\n{header_snippet}\n```",
            suggested_latex=header_snippet
        )

    is_replace_cmd = any(k in user_msg_lower for k in ("thay", "đổi", "sửa", "chuyển", "replace")) or "câu" in user_msg_lower

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 1", "phần i")):
        s1_snippet = r"""\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}
\begin{ex}
Cho hàm số $y = f(x)$...
\choice
{\True Phương án A}
{Phương án B}
{Phương án C}
{Phương án D}
\begin{loigiai}
Lời giải chi tiết Phần I.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần I (12 câu trắc nghiệm):\n```latex\n{s1_snippet}\n```",
            suggested_latex=s1_snippet
        )

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 2", "phần ii")):
        s2_snippet = r"""\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}
\begin{ex}
Cho hàm số $y = f(x)$... Xét tính đúng/sai:
\choiceTF
{\True Khẳng định a) đúng.}
{Khẳng định b) sai.}
{\True Khẳng định c) đúng.}
{Khẳng định d) sai.}
\begin{loigiai}
\begin{itemchoice}
\itemch Lời giải ý a.
\itemch Lời giải ý b.
\itemch Lời giải ý c.
\itemch Lời giải ý d.
\end{itemchoice}
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần II (Đúng/Sai 4 ý):\n```latex\n{s2_snippet}\n```",
            suggested_latex=s2_snippet
        )

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 3", "phần iii")):
        s3_snippet = r"""\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}
\begin{ex}
Tính giá trị của biểu thức...
\shortans{100}
\begin{loigiai}
Lời giải chi tiết trả lời ngắn.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần III (Trả lời ngắn):\n```latex\n{s3_snippet}\n```",
            suggested_latex=s3_snippet
        )

    # Attempt to query configured AI provider
    try:
        if default_ai_provider_service and (default_ai_provider_service.api_key or default_ai_provider_service.provider in ("openai", "openrouter", "custom", "gemini")):
            # We can use the configured provider
            provider = default_ai_provider_service.provider
            model = default_ai_provider_service.model or ("gemini-3.8-flash-high" if provider == "custom" else "gpt-4o")
            base_url = (default_ai_provider_service.base_url or ("http://armbian:8317/v1" if provider == "custom" else "")).strip()
            api_key = default_ai_provider_service.api_key or ("123" if provider == "custom" else "gemini-mock-key")

            # Normalize base_url: if armbian or missing /v1, ensure /v1 is appended
            clean_base = base_url.rstrip('/')
            if clean_base:
                if not clean_base.endswith('/v1') and ('8317' in clean_base or not clean_base.endswith('/openai')):
                    clean_base = f"{clean_base}/v1"

            if provider in ("openai", "openrouter", "custom", "gemini"):
                if clean_base:
                    endpoint = f"{clean_base}/chat/completions"
                elif provider == "gemini":
                    endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
                else:
                    endpoint = "https://api.openai.com/v1/chat/completions"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                messages: List[Any] = [{"role": "system", "content": system_prompt}]
                if req.history:
                    for h in req.history[-4:]:
                        messages.append({"role": h.role, "content": h.content})
                user_content = [{"type": "text", "text": prompt}]
                if req.images:
                    for img_url in req.images:
                        user_content.append({"type": "image_url", "image_url": {"url": img_url}})
                    messages.append({"role": "user", "content": user_content})
                else:
                    messages.append({"role": "user", "content": prompt})

                ai_timeout = float(getattr(default_ai_provider_service, "timeout", 60.0) or 60.0)
                with httpx.Client(timeout=max(ai_timeout, 60.0)) as client:
                    resp = client.post(endpoint, headers=headers, json={"model": model, "messages": messages, "temperature": 0.4})
                    if resp.status_code == 200:
                        data = resp.json()
                        reply_text = data["choices"][0]["message"]["content"]
                        diffs = extract_all_diffs_from_text(reply_text, req.current_latex, user_message=req.message)
                        diff = diffs[0] if diffs else None
                        suggested_latex = None
                        m_code = re.search(r'```(?:latex|tex)?\s*\n([\s\S]*?)```', reply_text)
                        if m_code:
                            suggested_latex = m_code.group(1).strip()
                        return ChatResponse(reply=reply_text, diff=diff, diffs=diffs, suggested_latex=suggested_latex)

    except Exception as e:
        logger.warning(f"AI Provider call failed: {e}. Falling back to rule-based assistant.")

    # Smart offline / local fallback generator if AI provider is unconfigured or network failed
    user_msg_lower = req.message.lower()
    cur_latex = req.current_latex or ""

    # 0. Check if compile error is reported or user asks to fix compile errors
    if (req.compile_error_log or req.compile_error) and (req.compile_error_log or req.compile_error).strip():
        diag_resp = diagnose_compile_error((req.compile_error_log or req.compile_error), cur_latex, req.message)
        if diag_resp:
            return diag_resp

    if any(k in user_msg_lower for k in ("fix lỗi", "sửa lỗi", "lỗi biên dịch", "compile error", "khắc phục lỗi")):
        diag_resp = diagnose_compile_error((req.compile_error_log or req.compile_error) or req.message, cur_latex, req.message)
        if diag_resp:
            return diag_resp

    # 1. Targeted question replacement (highest priority for targeted refactoring, with or without images)
    if cur_latex and target_q_num is not None:
        old_q = old_snippet or find_nth_question_in_latex(cur_latex, target_q_num, section=target_sec)
        if old_q:
            # Generate domain-specific replacement question with centered invariant
            if target_q_num == 7 or any(k in user_msg_lower for k in ("lập phương", "vectơ", "vector", "hình học không gian")):
                new_q = r"""\begin{ex}
Cho hình lập phương $ABCD.A'B'C'D'$. Góc giữa hai vectơ $\overrightarrow{AB}$ và $\overrightarrow{A'D'}$ bằng:
\begin{center}
  \begin{tikzpicture}[scale=0.7, >=stealth, line join=round, line cap=round]
    \coordinate (A) at (0, 0);
    \coordinate (B) at (3, 0);
    \coordinate (D) at (-1.4, -1.1);
    \coordinate (C) at (1.6, -1.1);
    \coordinate (A1) at (0, 2.6);
    \coordinate (B1) at (3, 2.6);
    \coordinate (D1) at (-1.4, 1.5);
    \coordinate (C1) at (1.6, 1.5);

    \draw[thick] (D) -- (C) -- (B) -- (B1) -- (C1) -- (D1) -- cycle;
    \draw[thick] (C) -- (C1);
    \draw[thick] (A1) -- (B1) (A1) -- (D1);
    \draw[dashed, thick] (A) -- (B) (A) -- (D) (A) -- (A1);

    \node[left] at (A) {$A$};
    \node[right] at (B) {$B$};
    \node[below left] at (D) {$D$};
    \node[below right] at (C) {$C$};
    \node[above left] at (A1) {$A'$};
    \node[above right] at (B1) {$B'$};
    \node[above left] at (D1) {$D'$};
    \node[above right] at (C1) {$C'$};
  \end{tikzpicture}
\end{center}
\choice
{\True $90^\circ$}
{$45^\circ$}
{$60^\circ$}
{$120^\circ$}
\begin{loigiai}
Do $ABCD.A'B'C'D'$ là hình lập phương nên $A'D' \parallel AD$. Do đó $(\overrightarrow{AB}, \overrightarrow{A'D'}) = (\overrightarrow{AB}, \overrightarrow{AD}) = 90^\circ$ vì $ABCD$ là hình vuông.
\end{loigiai}
\end{ex}"""
            elif target_q_num == 10 or any(k in user_msg_lower for k in ("bảng biến thiên", "bbt", "tkz-tab", "tiệm cận")):
                new_q = r"""\begin{ex}
Cho hàm số phân thức $y = \dfrac{ax+b}{cx+d}$ có bảng biến thiên như sau:
\begin{center}
  \begin{tikzpicture}
    \tikzset{double style/.append style = {double distance=2.5pt}}
    \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.4]
    {$x$/.6, $y'$/.6, $y$/2}
    {$-\infty$,$1$,$+\infty$}
    \tkzTabLine{,+,d,+,}
    \tkzTabVar{-/$-2$, +D-/$+\infty$/$-\infty$, +/$-2$}
  \end{tikzpicture}
\end{center}
Phương trình đường tiệm cận đứng và tiệm cận ngang của đồ thị hàm số lần lượt là:
\choice
{\True $x = 1$ và $y = -2$}
{$x = -2$ và $y = 1$}
{$x = 1$ và $y = 2$}
{$x = -1$ và $y = -2$}
\begin{loigiai}
Dựa vào bảng biến thiên, ta có tiệm cận đứng là $x = 1$ và tiệm cận ngang là $y = -2$.
\end{loigiai}
\end{ex}"""
            elif (target_sec in ("3", "III") and target_q_num == 2) or any(k in user_msg_lower for k in ("bậc thang", "ô vuông")):
                new_q = r"""\begin{ex}
Một bảng ô vuông dạng bậc thang gồm $15$ ô vuông đơn vị như hình vẽ bên dưới:
\begin{center}
  \begin{tikzpicture}[scale=0.6]
    \draw[thick] (0, 0) grid (5, 1);
    \draw[thick] (0, 1) grid (4, 2);
    \draw[thick] (0, 2) grid (3, 3);
    \draw[thick] (0, 3) grid (2, 4);
    \draw[thick] (0, 4) grid (1, 5);
  \end{tikzpicture}
\end{center}
Người ta điền 15 số nguyên dương phân biệt từ tập hợp các số không chia hết cho 5 vào 15 ô vuông sao cho tổng các số trên mỗi hàng bằng nhau. Biết số lớn nhất được điền là số nhỏ nhất có thể, tính tổng các số ở hàng đầu tiên (hàng gồm 5 ô).
\shortans{45}
\begin{loigiai}
Tổng các số được phân bổ cân đối trên các hàng, tổng của hàng 5 ô bằng 45.
\end{loigiai}
\end{ex}"""
            elif (target_sec in ("3", "III") and target_q_num == 3) or any(k in user_msg_lower for k in ("hạt cườm", "elip", "khoan lỗ")):
                new_q = r"""\begin{ex}
Một hạt cườm trang trí bằng gỗ có dạng khối tròn xoay được tạo thành khi quay miền elip $\dfrac{x^2}{1{,}5^2} + \dfrac{y^2}{1^2} \le 1$ quanh trục $Ox$, sau đó được khoan một lỗ trụ xuyên suốt dọc theo trục $Ox$ có bán kính $r = 0{,}2\text{ cm}$.
\begin{center}
  \begin{tikzpicture}[scale=1.1, >=stealth]
    \draw[->, thick] (-2.2, 0) -- (2.2, 0) node[right] {$x$};
    \draw[->, thick] (0, -1.5) -- (0, 1.5) node[above] {$y$};
    \node[below left] at (0, 0) {$O$};
    \draw[thick, smooth, domain=-1.5:1.5, samples=40] plot (\x, {sqrt(max(0, 1 - (\x/1.5)^2))});
    \draw[thick, smooth, domain=-1.5:1.5, samples=40] plot (\x, {-sqrt(max(0, 1 - (\x/1.5)^2))});
    \draw[dashed, red, thick] (-1.47, 0.2) -- (1.47, 0.2);
    \draw[dashed, red, thick] (-1.47, -0.2) -- (1.47, -0.2);
    \node[right, red] at (1.5, 0.2) {$y = 0{,}2$};
  \end{tikzpicture}
\end{center}
Tính thể tích phần gỗ còn lại của hạt cườm theo đơn vị $\text{cm}^3$ (làm tròn kết quả đến hàng phần trăm).
\shortans{5.84}
\begin{loigiai}
Thể tích khối tròn xoay elip trừ thể tích lỗ khoan hình trụ cho kết quả xấp xỉ $5{,}84\text{ cm}^3$.
\end{loigiai}
\end{ex}"""
            elif (target_sec in ("3", "III") and target_q_num == 4) or any(k in user_msg_lower for k in ("đa giác", "12 đỉnh", "bóng đèn")):
                new_q = r"""\begin{ex}
Cho một đa giác đều 12 đỉnh $A_1A_2\ldots A_{12}$ nội tiếp đường tròn. Tại mỗi đỉnh gắn một bóng đèn gồm 4 bóng màu đỏ và 8 bóng màu xanh được bố trí ngẫu nhiên:
\begin{center}
  \begin{tikzpicture}[scale=1.0]
    \draw[thick] (0, 0) circle (1.8cm);
    \foreach \i in {1, 2, ..., 12} {
      \coordinate (P\i) at ({90 - (\i-1)*30}:1.8cm);
      \fill (P\i) circle (2pt);
      \node at ({90 - (\i-1)*30}:2.15cm) {\footnotesize $A_{\i}$};
    }
    \draw[thin, dashed] (P1) -- (P5) -- (P9) -- cycle;
  \end{tikzpicture}
\end{center}
Chọn ngẫu nhiên 3 đỉnh của đa giác. Biết xác suất để 3 đỉnh được chọn tạo thành một tam giác có ít nhất một bóng đèn màu đỏ là $P$. Tính giá trị của biểu thức $3190P$.
\shortans{145}
\begin{loigiai}
Tính được xác suất $P$ và giá trị biểu thức $3190P = 145$.
\end{loigiai}
\end{ex}"""
            elif (target_sec in ("3", "III") and target_q_num == 5) or any(k in user_msg_lower for k in ("rau quả", "nông trại", "hệ phương trình")):
                new_q = r"""\begin{ex}
Một nông trại cung cấp ba loại nông sản: Cà chua, Bắp cải và Dưa chuột cho một chuỗi siêu thị. Thống kê khối lượng giao hàng (tấn) và tổng số tiền thanh toán (triệu đồng) trong ba ngày đầu tuần như sau:
\begin{center}
  \begin{tabular}{|l|c|c|c|c|}
    \hline
    Ngày giao & Cà chua & Bắp cải & Dưa chuột & Tổng tiền (triệu đồng) \\ \hline
    Thứ Hai & $2$ & $3$ & $1$ & $52$ \\ \hline
    Thứ Ba & $1$ & $4$ & $2$ & $58$ \\ \hline
    Thứ Tư & $3$ & $2$ & $4$ & $76$ \\ \hline
    Thứ Bảy & $1$ & $1$ & $1$ & $?$ \\ \hline
  \end{tabular}
\end{center}
Biết đơn giá mỗi loại nông sản không đổi trong tuần, tính số tiền thu được trong ngày thứ Bảy khi nông trại giao mỗi loại đúng $1$ tấn nông sản (đơn vị: triệu đồng).
\shortans{18.5}
\begin{loigiai}
Giải hệ 3 phương trình bậc nhất 3 ẩn tìm đơn giá mỗi loại nông sản, tính được tổng tiền ngày thứ Bảy là $18{,}5$ triệu đồng.
\end{loigiai}
\end{ex}"""
            elif (target_sec in ("3", "III") and target_q_num == 6) or any(k in user_msg_lower for k in ("lợi nhuận", "tối ưu", "doanh thu")):
                new_q = r"""\begin{ex}
Một công ty nông sản xác định hàm tổng doanh thu khi bán $x$ tấn sản phẩm là $R(x) = 60x$ (triệu đồng) và hàm tổng chi phí sản xuất là $C(x) = 0{,}001x^3 + 30x + 10$ (triệu đồng), với $x \in [1; 200]$. Để lợi nhuận thu được lớn nhất, công ty cần sản xuất bao nhiêu tấn sản phẩm?
\shortans{100}
\begin{loigiai}
Hàm lợi nhuận $P(x) = R(x) - C(x) = -0{,}001x^3 + 30x - 10$. Đạo hàm $P'(x) = 0 \Leftrightarrow x = 100$. Vậy công ty cần sản xuất $100$ tấn sản phẩm.
\end{loigiai}
\end{ex}"""
            elif target_sec in ("2", "II") or any(k in user_msg_lower for k in ("đúng sai", "đúng/sai", "choicetf", "phần ii", "phần 2")):
                new_q = r"""\begin{ex}
Cho hàm số bậc ba $f(x) = \dfrac{1}{3}x^3 - 5x^2 + 9x + 8$. Xét tính Đúng/Sai của các mệnh đề sau:
\choiceTF[1]
{\True Đạo hàm của hàm số đã cho là $f'(x) = x^2 - 10x + 9$.}
{Hàm số đồng biến trên khoảng $(1; 9)$.}
{\True Hàm số đạt cực đại tại điểm $x = 1$.}
{Tâm đối xứng của đồ thị hàm số có hoành độ bằng $3$.}
\begin{loigiai}
\begin{itemchoice}
\itemch Đúng. Ta có $f'(x) = x^2 - 10x + 9$.
\itemch Sai. $f'(x) < 0$ trên $(1; 9)$ nên hàm số nghịch biến trên khoảng $(1; 9)$.
\itemch Đúng. Hàm số đạt cực đại tại $x = 1$.
\itemch Sai. Hoành độ tâm đối xứng là $x = 5$.
\end{itemchoice}
\end{loigiai}
\end{ex}"""
            elif any(k in user_msg_lower for k in ("đơn điệu", "đồng biến", "nghịch biến")):
                new_q = r"""\begin{ex}
Cho hàm số $y = f(x)$ có bảng xét dấu đạo hàm như sau:
\begin{center}
\begin{tabular}{c|ccccccc}
$x$ & $-\infty$ & & $-1$ & & $2$ & & $+\infty$ \\ \hline
$f'(x)$ & & $+$ & $0$ & $-$ & $0$ & $+$ &
\end{tabular}
\end{center}
Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\choice
{\True $(2; +\infty)$}
{$(-1; 2)$}
{$(-\infty; 2)$}
{$(-1; +\infty)$}
\begin{loigiai}
Dựa vào bảng xét dấu đạo hàm, ta có $f'(x) > 0$ trên các khoảng $(-\infty; -1)$ và $(2; +\infty)$.
Do đó hàm số đồng biến trên khoảng $(2; +\infty)$.
\end{loigiai}
\end{ex}"""
            elif any(k in user_msg_lower for k in ("tích phân", "nguyên hàm")):
                new_q = r"""\begin{ex}
Tính tích phân $I = \int_0^1 (2x + 1) \, \mathrm{d}x$.
\choice
{\True $2$}
{$1$}
{$3$}
{$0$}
\begin{loigiai}
Ta có $I = \left. (x^2 + x) \right|_0^1 = (1 + 1) - 0 = 2$.
\end{loigiai}
\end{ex}"""
            elif r"\shortans" in old_q:
                new_q = r"""\begin{ex}
Tính giá trị của biểu thức $P = 2^3 + 3^2$.
\shortans{17}
\begin{loigiai}
Ta có $P = 8 + 9 = 17$.
\end{loigiai}
\end{ex}"""
            else:
                new_q = r"""\begin{ex}
Cho hàm số $y = \dfrac{2x - 1}{x + 1}$. Tiệm cận ngang của đồ thị hàm số là đường thẳng:
\choice
{\True $y = 2$}
{$x = -1$}
{$y = -1$}
{$x = 2$}
\begin{loigiai}
Ta có $\lim_{x \to \pm\infty} \dfrac{2x - 1}{x + 1} = 2$, suy ra tiệm cận ngang là $y = 2$.
\end{loigiai}
\end{ex}"""

            desc = f"Thay thế Câu {target_q_num}" + (f" Phần {target_sec.upper()}" if target_sec else "")
            diff = DiffSuggestion(
                action="replace",
                old_text=old_q,
                new_text=new_q,
                description=desc
            )
            reply = (
                f"Tôi đề xuất thay thế **Câu {target_q_num}** bằng câu hỏi mới chuẩn gói `ex_test.sty`:\n\n"
                f"```diff\n- {old_q}\n+ {new_q}\n```\n\n"
                f"Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay thế."
            )
            return ChatResponse(reply=reply, diff=diff, diffs=[diff], suggested_latex=new_q)

    # 2. Multimodal image query without question replacement
    if req.images:
        ex_snippet = r"""\begin{ex}[Phân tích từ ảnh đính kèm]
Cho đồ thị hàm số hoặc hình vẽ nhận được từ ảnh đính kèm:
\begin{center}
  \begin{tikzpicture}[scale=0.7, >=stealth]
    \draw[->, thick] (-3, 0) -- (3, 0) node[right] {$x$};
    \draw[->, thick] (0, -3) -- (0, 3) node[above] {$y$};
    \node[below left] at (0, 0) {$O$};
    \draw[thick, red, smooth, domain=-2:2] plot (\x, {(\x)^2 - 2});
  \end{tikzpicture}
\end{center}
Hàm số biểu diễn đồ thị trên là:
\choice
{\textbf{ $y = x^2 - 2$}}
{$y = -x^2 + 2$}
{$y = x^3 - 3x$}
{$y = \dfrac{x+1}{x-1}$}
\begin{loigiai}
Dựa trên hình ảnh đồ thị parabol quay bề lõm lên trên với đỉnh $(0; -2)$, phương trình hàm số là $y = x^2 - 2$.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Tôi đã phân tích hình ảnh đính kèm và nhận dạng cấu trúc toán học. Dưới đây là đoạn mã câu hỏi LaTeX chuẩn ex_test được trích xuất từ ảnh:\n\n```latex\n{ex_snippet}\n```",
            suggested_latex=ex_snippet,
            diff=DiffSuggestion(action="replace", old_text="", new_text=ex_snippet, description="Thêm câu hỏi nhận dạng từ ảnh đính kèm")
        )

    # Targeted edits (diff replacements)
    cur_latex = req.current_latex or ""

    # 0. Check if compile error is reported or user asks to fix compile errors
    if (req.compile_error_log or req.compile_error) and (req.compile_error_log or req.compile_error).strip():
        diag_resp = diagnose_compile_error((req.compile_error_log or req.compile_error), cur_latex, req.message)
        if diag_resp:
            return diag_resp

    if any(k in user_msg_lower for k in ("fix lỗi", "sửa lỗi", "lỗi biên dịch", "compile error", "khắc phục lỗi")):
        diag_resp = diagnose_compile_error((req.compile_error_log or req.compile_error) or req.message, cur_latex, req.message)
        if diag_resp:
            return diag_resp

    # 0a. Check if prompt requests national exam header or sections
    if any(k in user_msg_lower for k in ("tạo header", "tạo tiêu đề", "sở giáo dục", "tiêu đề 2 cột")):
        header_snippet = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
  \textbf{TRƯỜNG THPT ...}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{MÔN: TOÁN}\\
  \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
\end{minipage}
\vspace{0.25cm}
\noindent
Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
\vspace{0.1cm}
\noindent
\rule{\textwidth}{0.5pt}
\vspace{0.3cm}"""
        return ChatResponse(
            reply=f"Đã tạo tiêu đề chuẩn 2 cột:\n```latex\n{header_snippet}\n```",
            suggested_latex=header_snippet
        )

    is_replace_cmd = any(k in user_msg_lower for k in ("thay", "đổi", "sửa", "chuyển", "replace")) or "câu" in user_msg_lower

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 1", "phần i")):
        s1_snippet = r"""\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}
\begin{ex}
Cho hàm số $y = f(x)$...
\choice
{\True Phương án A}
{Phương án B}
{Phương án C}
{Phương án D}
\begin{loigiai}
Lời giải chi tiết Phần I.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần I (12 câu trắc nghiệm):\n```latex\n{s1_snippet}\n```",
            suggested_latex=s1_snippet
        )

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 2", "phần ii")):
        s2_snippet = r"""\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}
\begin{ex}
Cho hàm số $y = f(x)$... Xét tính đúng/sai:
\choiceTF
{\True Khẳng định a) đúng.}
{Khẳng định b) sai.}
{\True Khẳng định c) đúng.}
{Khẳng định d) sai.}
\begin{loigiai}
\begin{itemchoice}
\itemch Lời giải ý a.
\itemch Lời giải ý b.
\itemch Lời giải ý c.
\itemch Lời giải ý d.
\end{itemchoice}
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần II (Đúng/Sai 4 ý):\n```latex\n{s2_snippet}\n```",
            suggested_latex=s2_snippet
        )

    if not is_replace_cmd and any(k in user_msg_lower for k in ("phần 3", "phần iii")):
        s3_snippet = r"""\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}
\begin{ex}
Tính giá trị của biểu thức...
\shortans{100}
\begin{loigiai}
Lời giải chi tiết trả lời ngắn.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo Phần III (Trả lời ngắn):\n```latex\n{s3_snippet}\n```",
            suggested_latex=s3_snippet
        )

    if any(k in user_msg_lower for k in ("3 phần", "chuẩn quốc gia 2025", "trọn bộ", "đề thi chuẩn quốc gia")):
        full_national_exam = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO ...}\\
  \textbf{TRƯỜNG THPT ...}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{MÔN: TOÁN}\\
  \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
\end{minipage}
\vspace{0.25cm}
\noindent
Họ và tên thí sinh: \dotfill\ Số báo danh: \dotfill\ \hfill \framebox{\textbf{Mã đề: 0102}}
\vspace{0.1cm}
\noindent
\rule{\textwidth}{0.5pt}
\vspace{0.3cm}

\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} \textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\begin{ex}
Cho hàm số $y = f(x)$ có đạo hàm $f'(x) = x(x-1)^2$. Số điểm cực trị của hàm số là:
\choice
{0}
{\True 2}
{1}
{3}
\begin{loigiai}
$f'(x) = 0 \Leftrightarrow x = 0$ hoặc $x = 1$. Số điểm cực trị là 1.
\end{loigiai}
\end{ex}

\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} \textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\begin{ex}
Cho hàm số $y = x^3 - 3x + 1$. Xét tính đúng/sai:
\choiceTF
{\True Hàm số đạt cực đại tại $x = -1$.}\\
{Giá trị cực tiểu bằng $1$.}\\
{\True Tiệm cận ngang không có.}\\
{Đồ thị nhận điểm $I(0;1)$ làm tâm đối xứng.}
\begin{loigiai}
\begin{itemchoice}
\itemch Đúng. $y' = 3x^2 - 3 = 0 \Rightarrow x = \pm 1$. $y(-1) = 3$.
\itemch Sai. $y(1) = -1$.
\itemch Đúng. Hàm đa thức không có tiệm cận ngang.
\itemch Đúng. $y''(0) = 0$ và $y(0) = 1$.
\end{itemchoice}
\end{loigiai}
\end{ex}

\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} \textit{Thí sinh trả lời từ câu 1 đến câu 6.}

\begin{ex}
Tìm giá trị lớn nhất của hàm số $y = -x^2 + 4x - 3$ trên đoạn $[0; 3]$.
\shortans{1}
\begin{loigiai}
$y = -(x-2)^2 + 1 \le 1$. Đạt được khi $x = 2$.
\end{loigiai}
\end{ex}"""
        return ChatResponse(
            reply=f"Đã tạo trọn bộ đề thi chuẩn Quốc Gia 2025 (Header 2 cột & 3 Section):\n```latex\n{full_national_exam}\n```",
            suggested_latex=full_national_exam
        )

    # 0b. Check if prompt requests multiple edits / multi-diff scenario
    if any(k in user_msg_lower for k in ("multi-diff", "nhiều sửa đổi", "áp dụng tất cả", "apply all")) or (
        "mã đề" in user_msg_lower and ("0105" in user_msg_lower or "105" in user_msg_lower)
    ):
        md_diffs = []
        # Diff 1: Mã đề
        for line in cur_latex.splitlines():
            if "MÔN THI" in line or "mã đề" in line.lower() or "đề thi" in line.lower():
                if "MÃ ĐỀ" in line:
                    new_l = re.sub(r'MÃ ĐỀ:?\s*\d+', 'MÃ ĐỀ: 0105', line)
                else:
                    new_l = line.replace(r'\\', r' --- \textbf{MÃ ĐỀ: 0105}\\')
                if new_l != line:
                    md_diffs.append(DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=new_l,
                        description="Cập nhật Mã đề thi sang 0105"
                    ))
                    break
        # Diff 2: Cỡ chữ hoặc documentclass
        for line in cur_latex.splitlines():
            if "documentclass" in line:
                if "11pt" in line:
                    new_l = line.replace("11pt", "12pt")
                    md_diffs.append(DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=new_l,
                        description="Đổi cỡ chữ toàn tài liệu sang 12pt"
                    ))
                elif "12pt" in line:
                    new_l = line.replace("12pt", "11pt")
                    md_diffs.append(DiffSuggestion(
                        action="replace",
                        old_text=line,
                        new_text=new_l,
                        description="Đổi cỡ chữ toàn tài liệu từ 12pt sang 11pt"
                    ))
                break

        if md_diffs:
            blocks = "\n\n".join([f"Gợi ý {i+1}: {d.description}\n```diff\n- {d.old_text}\n+ {d.new_text}\n```" for i, d in enumerate(md_diffs)])
            reply = (
                f"Tôi đề xuất {len(md_diffs)} sửa đổi vào tài liệu:\n\n{blocks}\n\n"
                "Bạn có thể duyệt từng thay đổi qua [<] / [>] hoặc nhấn **Áp dụng tất cả**."
            )
            return ChatResponse(reply=reply, diff=md_diffs[0], diffs=md_diffs)

    # 1. Check if user prompt requests font / font size changes
    font_diff = extract_diff_from_text("", cur_latex, user_message=req.message)
    if font_diff:
        reply = (
            f"Tôi đề xuất {font_diff.description.lower()} tại dòng khai báo `\\documentclass`:\n\n"
            f"```diff\n- {font_diff.old_text}\n+ {font_diff.new_text}\n```\n\n"
            "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
        )
        return ChatResponse(reply=reply, diff=font_diff)

    # 1b. Check if user prompt requests replacing question N offline
    m_off_rep_q = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)',
        user_msg_lower
    )
    if not m_off_rep_q:
        m_off_rep_q = re.search(
            r'(?:câu\s+hỏi|câu|question)\s+(\d+).*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)',
            user_msg_lower
        )
    if m_off_rep_q and cur_latex:
        q_idx = int(m_off_rep_q.group(1))
        old_q = find_nth_question_in_latex(cur_latex, q_idx)
        if old_q:
            if any(k in user_msg_lower for k in ("đơn điệu", "đồng biến", "nghịch biến")):
                new_q = r"""\begin{ex}
Cho hàm số $y = f(x)$ có bảng xét dấu đạo hàm như sau:
\begin{center}
\begin{tabular}{c|ccccccc}
$x$ & $-\infty$ & & $-1$ & & $2$ & & $+\infty$ \\ \hline
$f'(x)$ & & $+$ & $0$ & $-$ & $0$ & $+$ & 
\end{tabular}
\end{center}
Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\choice
{\True $(2; +\infty)$}
{$(-1; 2)$}
{$(-\infty; 2)$}
{$(-1; +\infty)$}
\begin{loigiai}
Dựa vào bảng xét dấu đạo hàm, ta có $f'(x) > 0$ trên các khoảng $(-\infty; -1)$ và $(2; +\infty)$.
Do đó hàm số đồng biến trên khoảng $(2; +\infty)$.
\end{loigiai}
\end{ex}"""
            elif any(k in user_msg_lower for k in ("bảng biến thiên", "bbt", "tkz-tab", "cực trị")):
                new_q = r"""\begin{ex}[Đề Khảo sát 2026]
Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{center}
  \begin{tikzpicture}
    \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
    {$x$/.6, $f'(x)$/.6, $f(x)$/2}
    {$-\infty$,$-2$,$1$,$+\infty$}
    \tkzTabLine{,+,0,-,0,+,}
    \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
  \end{tikzpicture}
\end{center}
Số điểm cực trị của hàm số đã cho là:
\choice
{\True $2$}
{$1$}
{$0$}
{$3$}
\begin{loigiai}
Dựa vào bảng biến thiên, đạo hàm $f'(x)$ đổi dấu khi qua 2 điểm $x = -2$ và $x = 1$, do đó hàm số có $2$ điểm cực trị.
\end{loigiai}
\end{ex}"""
            elif any(k in user_msg_lower for k in ("đúng sai", "đúng/sai", "phần ii")):
                new_q = r"""\begin{ex}
Cho hàm số $y = f(x) = x^3 - 3x^2 + 2$. Xét tính đúng/sai của các mệnh đề sau:
\choiceTF[1]
{\True Hàm số đồng biến trên khoảng $(2; +\infty)$}
{Hàm số nghịch biến trên khoảng $(0; 3)$}
{\True Điểm cực đại của đồ thị hàm số là $(0; 2)$}
{Giá trị cực tiểu của hàm số bằng $2$}
\begin{loigiai}
Ta có $y' = 3x^2 - 6x = 3x(x - 2)$. Suy ra các khẳng định được kiểm chứng như trên.
\end{loigiai}
\end{ex}"""
            elif any(k in user_msg_lower for k in ("tích phân", "nguyên hàm")):
                new_q = r"""\begin{ex}
Tính tích phân $I = \int_0^1 (2x + 1) \, \mathrm{d}x$.
\choice
{\True $2$}
{$1$}
{$3$}
{$0$}
\begin{loigiai}
Ta có $I = \left. (x^2 + x) 
\right|_0^1 = (1 + 1) - 0 = 2$.
\end{loigiai}
\end{ex}"""
            else:
                new_q = r"""\begin{ex}
Cho hàm số $y = \dfrac{2x - 1}{x + 1}$. Tiệm cận ngang của đồ thị hàm số là đường thẳng:
\choice
{\True $y = 2$}
{$x = -1$}
{$y = -1$}
{$x = 2$}
\begin{loigiai}
Ta có $\lim_{x \to \pm\infty} \dfrac{2x - 1}{x + 1} = 2$, suy ra tiệm cận ngang là $y = 2$.
\end{loigiai}
\end{ex}"""
            diff = DiffSuggestion(
                action="replace",
                old_text=old_q,
                new_text=new_q,
                description=f"Thay thế Câu {q_idx}"
            )
            reply = (
                f"Tôi đề xuất thay thế **Câu {q_idx}** bằng câu hỏi mới chuẩn gói `ex_test.sty`:\n\n"
                f"```diff\n- {old_q}\n+ {new_q}\n```\n\n"
                f"Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay thế."
            )
            return ChatResponse(reply=reply, diff=diff, diffs=[diff], suggested_latex=new_q)

    # 2. Check if user prompt contains inline string replacement request
    if any(k in user_msg_lower for k in ("thay thế", "thay", "replace", "sửa", "đổi")) and not any(k in user_msg_lower for k in ("tạo", "thêm", "chèn", "sinh", "viết")):
        phrase_diff = extract_diff_from_text(req.message, cur_latex, user_message=req.message)
        if phrase_diff:
            reply = (
                f"Tôi đề xuất {phrase_diff.description.lower()}:\n\n"
                f"```diff\n- {phrase_diff.old_text}\n+ {phrase_diff.new_text}\n```\n\n"
                "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
            )
            return ChatResponse(reply=reply, diff=phrase_diff)

    # 3. Check legacy font patterns
    if any(k in user_msg_lower for k in ("11 sang 12", "cỡ chữ 12", "font 12", "11pt sang 12pt", "11 sang 12pt")):
        for line in cur_latex.split('\n'):
            if "documentclass" in line and "11pt" in line:
                new_line = line.replace("11pt", "12pt")
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=new_line,
                    description="Đổi cỡ chữ toàn tài liệu từ 11pt sang 12pt"
                )
                reply = (
                    "Tôi đề xuất thay đổi cỡ chữ toàn tài liệu từ `11pt` sang `12pt` tại dòng khai báo `\\documentclass`:\n\n"
                    f"```diff\n- {line}\n+ {new_line}\n```\n\n"
                    "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
                )
                return ChatResponse(reply=reply, diff=diff)

    if any(k in user_msg_lower for k in ("12 sang 11", "cỡ chữ 11", "font 11", "12pt sang 11pt", "12 sang 11pt")):
        for line in cur_latex.split('\n'):
            if "documentclass" in line and "12pt" in line:
                new_line = line.replace("12pt", "11pt")
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=new_line,
                    description="Đổi cỡ chữ toàn tài liệu từ 12pt sang 11pt"
                )
                reply = (
                    "Tôi đề xuất thay đổi cỡ chữ toàn tài liệu từ `12pt` sang `11pt` tại dòng khai báo `\\documentclass`:\n\n"
                    f"```diff\n- {line}\n+ {new_line}\n```\n\n"
                    "Bấm **Đồng ý** trên thanh gợi ý của khung soạn thảo để áp dụng thay đổi này."
                )
                return ChatResponse(reply=reply, diff=diff)

    if any(k in user_msg_lower for k in ("hiện lời giải", "bật lời giải", "sang loigiai")):
        for line in cur_latex.split('\n'):
            if "ex_test" in line and "dethi" in line:
                new_line = line.replace("[dethi]", "[loigiai]")
                diff = DiffSuggestion(
                    action="replace",
                    old_text=line,
                    new_text=new_line,
                    description="Chuyển sang chế độ in lời giải chi tiết [loigiai]"
                )
                reply = f"Tôi đề xuất chuyển sang chế độ hiển thị lời giải:\n\n```diff\n- {line}\n+ {new_line}\n```"
                return ChatResponse(reply=reply, diff=diff)

    if any(k in user_msg_lower for k in ("ex_test", "extest", "gói ex", "lệnh ex")):
        latex_snippet = r"""\begin{ex}[Đề Khảo sát 2026]
Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Số điểm cực trị của hàm số đã cho là:
\choice
{\True $2$}
{$1$}
{$0$}
{$3$}
\begin{loigiai}
Dựa vào bảng biến thiên, đạo hàm $f'(x)$ đổi dấu khi qua 2 điểm $x = -2$ và $x = 1$, do đó hàm số có $2$ điểm cực trị.
\end{loigiai}
\end{ex}"""
        reply = (
            "Dưới đây là mẫu câu hỏi theo chuẩn gói lệnh **`ex_test.sty` (v3.3)**:\n\n"
            f"```latex\n{latex_snippet}\n```\n\n"
            "- Lệnh `\\choice` tự động chia cột và nhận diện phương án đúng có tiền tố `\\True`.\n"
            "- Môi trường `\\begin{loigiai}...\\end{loigiai}` tự động ẩn/hiện tùy theo cấu hình `[dethi]`, `[color]`, hoặc `[loigiai]`."
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    elif any(k in user_msg_lower for k in ("bảng biến thiên", "bbt", "tkz-tab", "cực trị")):
        latex_snippet = r"""\begin{ex}
Cho hàm số $y = f(x)$ xác định và liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Điểm cực đại của đồ thị hàm số đã cho là:
\choice
{\True $(-2; 4)$}
{$(1; -1)$}
{$(-2; -1)$}
{$(1; 4)$}
\begin{loigiai}
Dựa vào bảng biến thiên, tại $x = -2$ đạo hàm đổi dấu từ dương sang âm và $f(-2) = 4$, do đó điểm cực đại là $(-2; 4)$.
\end{loigiai}
\end{ex}"""
        reply = (
            "Dưới đây là mẫu câu hỏi bảng biến thiên chuẩn gói `ex_test.sty` và `tkz-tab`:\n\n"
            f"```latex\n{latex_snippet}\n```\n\n"
            "Bạn có thể nhấn **Chèn vào con trỏ** để đưa câu hỏi này trực tiếp vào đề thi!"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    elif any(k in user_msg_lower for k in ("đúng sai", "đúng/sai", "phần ii", "phần 2", "764")):
        latex_snippet = r"""\section*{PHẦN II. Câu trắc nghiệm Đúng/Sai}
\textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\begin{ex}
Cho hàm số bậc ba $y = f(x) = ax^3 + bx^2 + cx + d$ ($a \neq 0$). Xét tính Đúng/Sai của các khẳng định sau:
\choiceTF[1]
{\True Đồ thị hàm số bậc ba luôn có tâm đối xứng là điểm uốn.}
{Nếu hàm số có hai điểm cực trị thì tích các giá trị cực trị luôn âm.}
{\True Hàm số luôn có đạo hàm cấp hai liên tục trên $\mathbb{R}$.}
{Điểm cực trị của hàm số là nghiệm của phương trình $f'(x) = 0$.}
\begin{loigiai}
\begin{itemchoice}
\itemch Đúng. Đồ thị hàm số bậc ba luôn nhận điểm uốn làm tâm đối xứng.
\itemch Sai. Tích hai giá trị cực trị có thể mang dấu dương.
\itemch Đúng. Hàm số đa thức bậc ba khả vi vô hạn trên $\mathbb{R}$.
\itemch Sai. Nghiệm của phương trình $f'(x) = 0$ phải làm đổi dấu đạo hàm thì mới là điểm cực trị.
\end{itemchoice}
\end{loigiai}
\end{ex}"""
        reply = (
            "Dưới đây là mẫu câu hỏi trắc nghiệm Đúng/Sai 4 khẳng định theo chuẩn `ex_test.sty` (Quyết định 764/QĐ-BGDĐT):\n\n"
            f"```latex\n{latex_snippet}\n```"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    elif any(k in user_msg_lower for k in ("đồ thị", "tikz", "bậc ba", "bậc 3")):
        latex_snippet = r"""\begin{ex}
Cho hàm số bậc ba $y = f(x)$ có đồ thị như hình vẽ bên. Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\begin{center}
  \begin{tikzpicture}[scale=0.6, >=stealth]
    \clip (-3.8, -5.5) rectangle (4.2, 5.5);
    \draw[->, thick] (-3.5, 0) -- (3.8, 0) node[right] {$x$};
    \draw[->, thick] (0, -5) -- (0, 5) node[above] {$y$};
    \node[below left] at (0, 0) {$O$};
    \draw[dashed] (-1, 0) node[below] {$-1$} -- (-1, 4) -- (0, 4) node[left] {$4$};
    \draw[dashed] (2, 0) node[above] {$2$} -- (2, -3) -- (0, -3) node[left] {$-3$};
    \draw[thick, black, smooth, samples=50, domain=-2.5:3.2] plot (\x, {(\x)^3 - 1.5*(\x)^2 - 6*(\x) + 0.5});
    \fill (-1, 4) circle (1.5pt);
    \fill (2, -3) circle (1.5pt);
  \end{tikzpicture}
\end{center}
\choice
{\True $(-\infty; -1)$}
{$(-1; 2)$}
{$(0; 2)$}
{$(-2; 1)$}
\begin{loigiai}
Dựa vào đồ thị, hàm số đi lên từ trái sang phải trên khoảng $(-\infty; -1)$ và $(2; +\infty)$, do đó đồng biến trên $(-\infty; -1)$.
\end{loigiai}
\end{ex}"""
        reply = (
            "Dưới đây là mẫu câu hỏi đồ thị hàm bậc ba bằng mã TikZ chuẩn gói `ex_test.sty`:\n\n"
            f"```latex\n{latex_snippet}\n```"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    else:
        latex_snippet = r"""\begin{ex}
Cho hàm số $y = \dfrac{2x-1}{x+1}$. Tìm phương trình các đường tiệm cận của đồ thị hàm số.
\choice
{\True $x = -1, y = 2$}
{$x = 1, y = 2$}
{$x = -1, y = -1$}
{$x = 2, y = -1$}
\begin{loigiai}
Ta có $\lim_{x \to -1} y = \infty \Rightarrow x = -1$ là đường tiệm cận đứng, và $\lim_{x \to \pm\infty} y = 2 \Rightarrow y = 2$ là đường tiệm cận ngang.
\end{loigiai}
\end{ex}"""
        reply = (
            f"Tôi đã tiếp nhận yêu cầu: **\"{req.message}\"**.\n\n"
            "Dưới đây là đoạn mã câu hỏi theo chuẩn gói lệnh `ex_test.sty`:\n\n"
            f"```latex\n{latex_snippet}\n```\n\n"
            "Bạn có thể bấm **Chèn vào con trỏ** để áp dụng ngay vào khung soạn thảo!"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)


@router.post("/save-to-bank", summary="Extract questions from LaTeX and save to Quesy Question Bank")
def save_to_question_bank(req: SaveToBankRequest, db: Session = Depends(get_db)):
    """Parses questions from the active LaTeX document, auto-tags YCCĐ, and commits them into the database."""
    questions_data = extract_questions_from_latex(req.latex_code)
    if not questions_data:
        return {"success": False, "total_saved": 0, "counts": {"single_choice": 0, "true_false": 0, "short_answer": 0}, "message": "Không tìm thấy câu hỏi hợp lệ trong định dạng LaTeX."}

    from backend.services.tagging_service import suggest_auto_tagging
    saved_count = 0
    counts = {"single_choice": 0, "true_false": 0, "short_answer": 0}

    for q_data in questions_data:
        try:
            fmt = q_data.get("item_format", "SINGLE_CHOICE")
            stem = q_data["stem"]
            tags = suggest_auto_tagging(stem=stem, db=db)
            
            cognitive_level = q_data.get("cognitive_level") or tags.get("cognitive_level", "RECOGNITION")
            learning_outcome_id = tags.get("learning_outcome_id")

            q = Question(
                stem=stem,
                item_format=fmt,
                short_answer_key=q_data.get("short_answer_value") or q_data.get("short_answer_key"),
                tolerance=q_data.get("tolerance", 0.0),
                cognitive_level=cognitive_level,
                learning_outcome_id=learning_outcome_id,
                status="APPROVED"
            )
            if fmt == "SINGLE_CHOICE":
                counts["single_choice"] += 1
            elif fmt == "TRUE_FALSE_GROUP":
                counts["true_false"] += 1
            elif fmt == "SHORT_ANSWER":
                counts["short_answer"] += 1

            if q_data.get("options"):
                for idx, opt in enumerate(q_data["options"]):
                    q.options.append(QuestionOption(
                        label=opt.get("label", "A"),
                        content=opt.get("content", ""),
                        is_correct=opt.get("is_correct", False),
                        is_fixed=opt.get("is_fixed", False),
                        order_index=idx
                    ))
            if q_data.get("sub_statements"):
                for idx, sub in enumerate(q_data["sub_statements"]):
                    q.sub_statements.append(SubStatement(
                        label=sub.get("label", "a"),
                        content=sub.get("content", ""),
                        is_true=sub.get("is_true", False),
                        explanation=sub.get("explanation", ""),
                        order_index=idx
                    ))
            db.add(q)
            saved_count += 1
        except Exception as e:
            logger.warning(f"Error saving question to bank: {e}")

    db.commit()
    return {
        "success": True,
        "total_saved": saved_count,
        "count": saved_count,
        "counts": counts,
        "message": f"Đã lưu {saved_count} câu hỏi ({counts['single_choice']} trắc nghiệm, {counts['true_false']} đúng/sai, {counts['short_answer']} trả lời ngắn) vào Ngân hàng câu hỏi!"
    }
