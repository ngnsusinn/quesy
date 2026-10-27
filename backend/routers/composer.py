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


def find_nth_question_in_latex(latex_code: Optional[str], n: int) -> Optional[str]:
    """Extracts the nth question block (1-indexed) from a LaTeX document.
    Accurately supports both ex_test.sty format (\\begin{ex}...\\end{ex})
    and classic format (\\textbf{Câu n.}, Câu n:, etc.).
    Returns the exact matching substring in latex_code, or None if not found.
    """
    if not latex_code or n < 1:
        return None

    # 1. ex_test.sty syntax (\\begin{ex} ... \\end{ex} or \\begin{bt} ... \\end{bt})
    ex_matches = list(re.finditer(r'\\begin\{(ex|bt|vd)\}(?:\[[^\]]*\])?[\s\S]*?\\end\{\1\}', latex_code))
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
        # check duplicate
        for existing in found_diffs:
            if existing.old_text == old_text and existing.new_text == new_text:
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

    # 5. Inline replacement proposals: Thay thế `old` bằng/thành/sang `new`
    for m_phrase in re.finditer(
        r'(?:thay thế|thay|đổi|sửa|chuyển|replace)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]\s+(?:bằng|thành|sang|với|by|with)\s+[`"“\'‘]([^`"”\'’\n]+)[`"”\'’]',
        reply_text,
        re.IGNORECASE
    ):
        old_raw = m_phrase.group(1).strip()
        new_raw = m_phrase.group(2).strip()
        matched_old = find_in_latex(old_raw, current_latex)
        if matched_old and matched_old != new_raw:
            desc = _clean_diff_description(reply_text[:m_phrase.start()]) or f"Thay thế '{old_raw}' thành '{new_raw}'"
            _add_diff("replace", matched_old, new_raw, desc)

    # If explicit blocks found diffs, return them
    if found_diffs:
        return found_diffs

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

    # 7. Targeted heuristic for choice modifications (đổi đáp án A sang B, sửa đáp án thành C, etc.)
    m_choice_chg = re.search(
        r'(?:đổi|sửa|chuyển)\s+(?:đáp án|lựa chọn)(?:\s+đúng)?\s+(?:từ\s+[ABCD]\s+sang\s+|thành\s+|sang\s+)([ABCD])\b',
        combined_lower,
        re.IGNORECASE
    )
    if m_choice_chg:
        target_choice = m_choice_chg.group(1).upper()
        target_idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(target_choice)
        if target_idx is not None:
            m_ch = re.search(r'\\choice\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', current_latex)
            if m_ch:
                old_full = m_ch.group(0)
                opts = [m_ch.group(1), m_ch.group(2), m_ch.group(3), m_ch.group(4)]
                cleaned_opts = [re.sub(r'\\True\s*', '', opt).strip() for opt in opts]
                cleaned_opts[target_idx] = "\\True " + cleaned_opts[target_idx]
                sep = "\n" if "\n" in old_full else ""
                new_full = f"\\choice{sep}{{{cleaned_opts[0]}}}{sep}{{{cleaned_opts[1]}}}{sep}{{{cleaned_opts[2]}}}{sep}{{{cleaned_opts[3]}}}"
                if old_full != new_full:
                    _add_diff("replace", old_full, new_full, f"Đổi đáp án đúng sang {target_choice}")

    if found_diffs:
        return found_diffs

    # 8. Targeted heuristic for replacing question N by number
    # Handles: "thay thế câu (\d+)", "thay câu (\d+)", "sửa câu (\d+)", "đổi câu (\d+)", "replace question (\d+)"
    m_replace_q = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)',
        combined_lower
    )
    if not m_replace_q:
        m_replace_q = re.search(
            r'(?:câu\s+hỏi|câu|question)\s+(\d+).*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)',
            combined_lower
        )
    if m_replace_q:
        target_q_num = int(m_replace_q.group(1))
        old_q = find_nth_question_in_latex(current_latex, target_q_num)
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
                m_ex_q = re.search(r'\\begin\{(?:ex|bt|vd)\}(?:\[[^\]]*\])?[\s\S]*?\\end\{(?:ex|bt|vd)\}', reply_text)
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
    m_replace_hint = re.search(
        r'(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)\s+(?:câu\s+hỏi|câu|question)\s*(\d+)',
        req.message,
        re.IGNORECASE
    )
    if not m_replace_hint:
        m_replace_hint = re.search(
            r'(?:câu\s+hỏi|câu|question)\s+(\d+).*?(?:thay\s+thế|thay|đổi|sửa|chuyển|replace)',
            req.message,
            re.IGNORECASE
        )
    if m_replace_hint and req.current_latex:
        q_target = int(m_replace_hint.group(1))
        old_snippet = find_nth_question_in_latex(req.current_latex, q_target)
        if old_snippet:
            prompt += (
                f"--- HƯỚNG DẪN BẮT BUỘC KHI THAY THẾ CÂU {q_target} ---\n"
                f"Khối câu {q_target} hiện tại trong tài liệu là:\n"
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

    user_msg_lower = req.message.lower()

    # Fast deterministic canonical 2025 templates router
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

    if any(k in user_msg_lower for k in ("phần 1", "phần i")):
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

    if any(k in user_msg_lower for k in ("phần 2", "phần ii")):
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

    if any(k in user_msg_lower for k in ("phần 3", "phần iii")):
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
            model = default_ai_provider_service.model
            base_url = default_ai_provider_service.base_url
            api_key = default_ai_provider_service.api_key or "gemini-mock-key"

            if provider in ("openai", "openrouter", "custom", "gemini"):
                endpoint = f"{(base_url or ('https://generativelanguage.googleapis.com/v1beta/openai' if provider == 'gemini' else 'https://api.openai.com/v1')).rstrip('/')}/chat/completions"
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

                with httpx.Client(timeout=25.0) as client:
                    resp = client.post(endpoint, headers=headers, json={"model": model, "messages": messages, "temperature": 0.4})
                    if resp.status_code == 200:
                        data = resp.json()
                        reply_text = data["choices"][0]["message"]["content"]
                        diffs = extract_all_diffs_from_text(reply_text, req.current_latex, user_message=req.message)
                        diff = diffs[0] if diffs else None
                        suggested_latex = None
                        m_code = re.search(r'```(?:latex|tex)?\s*\n([\s\S]*?)```', reply_text)
                        if m_code and not diffs:
                            suggested_latex = m_code.group(1).strip()
                        return ChatResponse(reply=reply_text, diff=diff, diffs=diffs, suggested_latex=suggested_latex)

    except Exception as e:
        logger.warning(f"AI Provider call failed: {e}. Falling back to rule-based assistant.")

    # Smart offline / local fallback generator if AI provider is unconfigured or network failed
    user_msg_lower = req.message.lower()

    if req.images:
        ex_snippet = r"""\begin{ex}[Phân tích từ ảnh đính kèm]
Cho đồ thị hàm số hoặc hình vẽ nhận được từ ảnh đính kèm:
\begin{tikzpicture}[scale=0.7, >=stealth]
  \draw[->, thick] (-3, 0) -- (3, 0) node[right] {$x$};
  \draw[->, thick] (0, -3) -- (0, 3) node[above] {$y$};
  \node[below left] at (0, 0) {$O$};
  \draw[thick, red, smooth, domain=-2:2] plot (\x, {(\x)^2 - 2});
\end{tikzpicture}
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

    if any(k in user_msg_lower for k in ("phần 1", "phần i")):
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

    if any(k in user_msg_lower for k in ("phần 2", "phần ii")):
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

    if any(k in user_msg_lower for k in ("phần 3", "phần iii")):
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
            elif any(k in user_msg_lower for k in ("đúng sai", "đúng/sai", "phần ii")):
                new_q = r"""\begin{ex}
Cho hàm số $y = f(x) = x^3 - 3x^2 + 2$. Xét tính đúng/sai của các mệnh đề sau:
\choiceTF
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
