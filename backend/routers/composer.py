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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Question, QuestionOption, SubStatement
from backend.services.composer_service import (
    STORAGE_COMPOSER_CACHE,
    TEMPLATES,
    compile_latex_to_pdf,
    extract_questions_from_latex,
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

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or command for the AI assistant")
    current_latex: Optional[str] = Field("", description="Current editor LaTeX code for context")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class DiffSuggestion(BaseModel):
    action: str = Field("replace", description="'replace' or 'insert'")
    old_text: str = Field("", description="Exact text snippet to replace in current code")
    new_text: str = Field("", description="New text snippet to insert")
    description: str = Field("", description="Summary description of the change")

class ChatResponse(BaseModel):
    reply: str
    suggested_latex: Optional[str] = None
    diff: Optional[DiffSuggestion] = None

class SaveToBankRequest(BaseModel):
    latex_code: str = Field(..., description="LaTeX source containing exam questions to extract")


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

    code_hash = hashlib.md5((clean_code + req.title).encode("utf-8")).hexdigest()
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

    success, err_msg, elapsed_ms = compile_latex_to_pdf(clean_code, out_pdf, title=req.title)

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


def extract_diff_from_text(reply_text: str, current_latex: Optional[str], user_message: str = "") -> Optional[DiffSuggestion]:
    """Helper to detect unified diff blocks, OLD/NEW blocks, or diffs in code blocks from AI responses."""
    if not current_latex:
        return None

    user_lower = user_message.lower()

    # 1. Targeted heuristic for font size changes (e.g. 11pt -> 12pt, font 12, cỡ chữ 11pt)
    if any(k in user_lower for k in ("font", "cỡ chữ", "size")):
        pts = re.findall(r'\b(10|11|12|13|14)(?:pt)?\b', user_lower)
        if pts:
            target_pt = f"{pts[-1]}pt"
            for line in current_latex.splitlines():
                if "documentclass" in line:
                    if re.search(r'\b\d+pt\b', line):
                        new_line = re.sub(r'\b\d+pt\b', target_pt, line)
                    else:
                        new_line = re.sub(r'\\documentclass\[', f'\\documentclass[{target_pt},', line)
                    if new_line != line:
                        return DiffSuggestion(
                            action="replace",
                            old_text=line,
                            new_text=new_line,
                            description=f"Đổi cỡ chữ toàn tài liệu sang {target_pt}"
                        )

    # 2. Explicit ```diff ... ``` blocks
    m_diff = re.search(r'```diff\s*\n\s*-\s*([^\n]+(?:\n\s*-[^\n]+)*)\s*\n\s*\+\s*([^\n]+(?:\n\s*\+[^\n]+)*)\s*\n```', reply_text)
    if m_diff:
        old_lines = [re.sub(r'^\s*-\s*', '', l) for l in m_diff.group(1).split('\n')]
        new_lines = [re.sub(r'^\s*\+\s*', '', l) for l in m_diff.group(2).split('\n')]
        old_text = '\n'.join(old_lines)
        new_text = '\n'.join(new_lines)
        if old_text and old_text in current_latex and old_text != new_text:
            return DiffSuggestion(action="replace", old_text=old_text, new_text=new_text, description="Thay đổi theo gợi ý AI")

    # 3. Explicit OLD: / NEW: blocks
    m_replace = re.search(r'OLD:\s*\n([\s\S]*?)\nNEW:\s*\n([\s\S]*?)(?:\n|$)', reply_text)
    if m_replace:
        old_text = m_replace.group(1).strip()
        new_text = m_replace.group(2).strip()
        if old_text and old_text in current_latex and old_text != new_text:
            return DiffSuggestion(action="replace", old_text=old_text, new_text=new_text, description="Thay đổi theo gợi ý AI")

    # 4. Detect changes if AI returned code block (```latex or ```tex or ```)
    m_code = re.search(r'```(?:latex|tex)?\s*\n([\s\S]*?)```', reply_text)
    if m_code:
        code = m_code.group(1).strip()
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
            if old_slice in current_latex and old_slice != new_slice:
                return DiffSuggestion(action="replace", old_text=old_slice, new_text=new_slice, description="Thay đổi theo gợi ý AI")
        elif len(code_lines) <= 4:
            matches = difflib.get_close_matches(code, cur_lines, n=1, cutoff=0.45)
            if matches and matches[0] != code:
                return DiffSuggestion(action="replace", old_text=matches[0], new_text=code, description="Thay đổi theo gợi ý AI")

    return None


@router.post("/chat", response_model=ChatResponse, summary="AI LaTeX Writing Copilot (assistant-ui clone)")
def composer_chat_endpoint(req: ChatRequest):
    """Interactive AI Assistant specifically tuned for authoring Vietnamese high-school math exams."""
    system_prompt = (
        "Bạn là Trợ lý Soạn thảo Đề thi & LaTeX Chuyên nghiệp (Quesy AI Copilot), lấy cảm hứng từ open-prism.\n"
        "Nhiệm vụ của bạn là hỗ trợ giáo viên Toán tại Việt Nam soạn thảo đề thi chất lượng cao theo chuẩn Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (Định dạng 2025).\n\n"
        "HỆ THỐNG ĐÃ TÍCH HỢP TOÀN DIỆN GÓI LỆNH ex_test.sty (v3.3):\n"
        "- Khai báo: \\usepackage[dethi]{ex_test} (hoặc [color], [loigiai], [solcolor]) cùng \\usepackage{fontspec}.\n"
        "- Phần I (Trắc nghiệm 4 lựa chọn): Dùng \\begin{ex} ... \\choice{A}{\\True B}{C}{D} \\begin{loigiai}...\\end{loigiai} \\end{ex}.\n"
        "- Phần II (Đúng/Sai 4 khẳng định): Dùng \\begin{ex} ... \\choiceTF{\\True a)...}{b)...}{\\True c)...}{d)...} \\begin{loigiai}\\begin{itemchoice}\\itemch...\\end{itemchoice}\\end{loigiai} \\end{ex}.\n"
        "- Phần III (Trả lời ngắn): Dùng \\begin{ex} ... \\shortans{kết_quả} \\begin{loigiai}...\\end{loigiai} \\end{ex}.\n"
        "- Chèn hình song song chữ: Dùng \\immini{Văn bản câu hỏi}{Mã hình TikZ} (hình bên phải) hoặc \\imminiL (hình bên trái).\n\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. Luôn sử dụng mã LaTeX chuẩn với font CMU Serif / Computer Modern (dùng \\usepackage{fontspec}).\n"
        "2. Bảng biến thiên BẮT BUỘC dùng TikZ package tkz-tab (\\tkzTabInit, \\tkzTabLine, \\tkzTabVar). Không dùng \\begin{array} cho bảng biến thiên!\n"
        "3. Đồ thị hàm số và hình học BẮT BUỘC dùng khối \\begin{tikzpicture} ... \\end{tikzpicture}.\n"
        "4. Mọi công thức toán inline bọc trong $...$, phân số dùng \\dfrac, vectơ dùng \\overrightarrow{AB}.\n\n"
        "QUY TẮC PHẢN HỒI (BẮT BUỘC TUÂN THỦ):\n"
        "1. KHI NGƯỜI DÙNG YÊU CẦU SỬA ĐỔI, ĐIỀU CHỈNH HOẶC THAY THẾ (như đổi font, sửa tiêu đề, đổi đáp án):\n"
        "   - TUYỆT ĐỐI KHÔNG xuất lại toàn bộ tài liệu cũ dài dòng!\n"
        "   - BẮT BUỘC chỉ xuất khối ```diff chứa đúng dòng cũ cần thay và dòng mới:\n"
        "     ```diff\n"
        "     - <dòng mã cũ>\n"
        "     + <dòng mã mới>\n"
        "     ```\n"
        "   - Kèm lời giải thích ngắn gọn bằng tiếng Việt.\n"
        "2. KHI NGƯỜI DÙNG YÊU CẦU TẠO MỚI CÂU HỎI HOẶC HÌNH VẼ:\n"
        "   - Xuất mã LaTeX tự chứa trong khối ```latex ... ``` để chèn vào vị trí con trỏ.\n"
    )

    prompt = f"Yêu cầu của giáo viên: {req.message}\n\n"
    if req.current_latex and req.current_latex.strip():
        # Truncate context to last 2000 chars if very long
        ctx = req.current_latex.strip()
        if len(ctx) > 3000:
            ctx = ctx[-3000:]
        prompt += f"--- NỘI DUNG TÀI LIỆU HIỆN TẠI (TRÍCH ĐOẠN) ---\n{ctx}\n--------------------------------------------\n"

    # Attempt to query configured AI provider
    try:
        if default_ai_provider_service and default_ai_provider_service.api_key:
            # We can use the configured provider
            import httpx
            provider = default_ai_provider_service.provider
            model = default_ai_provider_service.model
            base_url = default_ai_provider_service.base_url

            if provider in ("openai", "openrouter", "custom"):
                endpoint = f"{(base_url or 'https://api.openai.com/v1').rstrip('/')}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {default_ai_provider_service.api_key}",
                    "Content-Type": "application/json"
                }
                messages = [{"role": "system", "content": system_prompt}]
                if req.history:
                    for h in req.history[-4:]:
                        messages.append({"role": h.role, "content": h.content})
                messages.append({"role": "user", "content": prompt})

                with httpx.Client(timeout=25.0) as client:
                    resp = client.post(endpoint, headers=headers, json={"model": model, "messages": messages, "temperature": 0.4})
                    if resp.status_code == 200:
                        data = resp.json()
                        reply_text = data["choices"][0]["message"]["content"]
                        diff = extract_diff_from_text(reply_text, req.current_latex, user_message=req.message)
                        return ChatResponse(reply=reply_text, diff=diff)

    except Exception as e:
        logger.warning(f"AI Provider call failed: {e}. Falling back to rule-based assistant.")

    # Smart offline / local fallback generator if AI provider is unconfigured or network failed
    user_msg_lower = req.message.lower()

    # Targeted edits (diff replacements)
    cur_latex = req.current_latex or ""
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
        latex_snippet = r"""\textbf{Câu hỏi.} Cho hàm số $y = f(x)$ liên tục trên $\mathbb{R}$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}
Điểm cực đại của đồ thị hàm số đã cho là:
\textbf{A.} $(-2; 4)$ \qquad \textbf{B.} $(1; -1)$ \qquad \textbf{C.} $(-2; -1)$ \qquad \textbf{D.} $(1; 4)$"""
        reply = (
            "Dưới đây là mẫu câu hỏi bảng biến thiên sử dụng gói `tkz-tab` chuẩn mẫu vector của Bộ Giáo dục:\n\n"
            f"```latex\n{latex_snippet}\n```\n\n"
            "Bạn có thể nhấn **Chèn vào con trỏ** để đưa câu hỏi này trực tiếp vào đề thi!"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    elif any(k in user_msg_lower for k in ("đúng sai", "đúng/sai", "phần ii", "phần 2", "764")):
        latex_snippet = r"""\section*{PHẦN II. Câu trắc nghiệm Đúng/Sai}
\textit{Thí sinh trả lời từ câu 1 đến câu 4. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}

\textbf{Câu 1.} Cho hàm số bậc ba $y = f(x) = ax^3 + bx^2 + cx + d$ ($a \neq 0$). Xét tính Đúng/Sai của các khẳng định sau:

a) Đồ thị hàm số bậc ba luôn có tâm đối xứng là điểm uốn.

b) Nếu hàm số có hai điểm cực trị thì tích các giá trị cực trị luôn âm.

c) Hàm số luôn có đạo hàm cấp hai liên tục trên $\mathbb{R}$.

d) Điểm cực trị của hàm số là nghiệm của phương trình $f'(x) = 0$."""
        reply = (
            "Dưới đây là mẫu câu hỏi trắc nghiệm Đúng/Sai 4 khẳng định theo đúng Quyết định 764/QĐ-BGDĐT:\n\n"
            f"```latex\n{latex_snippet}\n```"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    elif any(k in user_msg_lower for k in ("đồ thị", "tikz", "bậc ba", "bậc 3")):
        latex_snippet = r"""\textbf{Câu hỏi.} Cho hàm số $y = f(x)$ có đồ thị như hình vẽ bên:
\begin{tikzpicture}[scale=0.7, >=stealth]
  \clip (-3.8, -5.5) rectangle (4.2, 5.5);
  \draw[->, thick] (-3.5, 0) -- (3.8, 0) node[right] {$x$};
  \draw[->, thick] (0, -5) -- (0, 5) node[above] {$y$};
  \node[below left] at (0, 0) {$O$};
  \draw[dashed] (-1, 0) node[below] {$-1$} -- (-1, 4) -- (0, 4) node[left] {$4$};
  \draw[dashed] (2, 0) node[above] {$2$} -- (2, -3) -- (0, -3) node[left] {$-3$};
  \draw[thick, black, smooth, samples=100, domain=-2.5:3.2] plot (\x, {(\x)^3 - 1.5*(\x)^2 - 6*(\x) + 0.5});
  \fill (-1, 4) circle (1.5pt);
  \fill (2, -3) circle (1.5pt);
\end{tikzpicture}
Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\textbf{A.} $(-1; 2)$ \qquad \textbf{B.} $(-\infty; -1)$ \qquad \textbf{C.} $(0; 2)$ \qquad \textbf{D.} $(-2; 1)$"""
        reply = (
            "Dưới đây là mẫu câu hỏi đồ thị hàm bậc ba bằng mã TikZ chuẩn vector:\n\n"
            f"```latex\n{latex_snippet}\n```"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)

    else:
        latex_snippet = r"""\textbf{Câu hỏi.} Cho hàm số $y = \dfrac{2x-1}{x+1}$. Tìm phương trình các đường tiệm cận của đồ thị hàm số.

\textbf{A.} $x = -1, y = 2$ \qquad \textbf{B.} $x = 1, y = 2$ \qquad \textbf{C.} $x = -1, y = -1$ \qquad \textbf{D.} $x = 2, y = -1$"""
        reply = (
            f"Tôi đã tiếp nhận yêu cầu: **\"{req.message}\"**.\n\n"
            "Dưới đây là đoạn mã LaTeX được tạo tự động theo chuẩn đề thi của Bộ GD&ĐT:\n\n"
            f"```latex\n{latex_snippet}\n```\n\n"
            "Bạn có thể bấm **Chèn vào con trỏ** để áp dụng ngay vào khung soạn thảo!"
        )
        return ChatResponse(reply=reply, suggested_latex=latex_snippet)


@router.post("/save-to-bank", summary="Extract questions from LaTeX and save to Quesy Question Bank")
def save_to_question_bank(req: SaveToBankRequest, db: Session = Depends(get_db)):
    """Parses questions from the active LaTeX document and commits them into the database."""
    questions_data = extract_questions_from_latex(req.latex_code)
    if not questions_data:
        return {"success": False, "count": 0, "message": "Không tìm thấy câu hỏi hợp lệ trong định dạng LaTeX (cần dạng \\textbf{Câu X.})."}

    saved_count = 0
    for q_data in questions_data:
        try:
            q = Question(
                stem=q_data["stem"],
                item_format=q_data.get("item_format", "SINGLE_CHOICE"),
                short_answer_key=q_data.get("short_answer_value") or q_data.get("short_answer_key"),
                tolerance=q_data.get("tolerance", 0.0),
                cognitive_level=q_data.get("cognitive_level", "RECOGNITION"),
                status="DRAFT"
            )
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
        "count": saved_count,
        "message": f"Đã lưu thành công {saved_count} câu hỏi vào Ngân hàng câu hỏi của hệ thống."
    }
