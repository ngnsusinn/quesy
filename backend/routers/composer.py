"""Quesy Exam Composer Router - Open-Prism LaTeX Workspace API.
Endpoints for compiling LaTeX documents to live PDF preview,
AI-assisted exam writing chat, template loading, and question bank export.
"""

import hashlib
import logging
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

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or command for the AI assistant")
    current_latex: Optional[str] = Field("", description="Current editor LaTeX code for context")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
    suggested_latex: Optional[str] = None

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
        )

    success, err_msg, elapsed_ms = compile_latex_to_pdf(clean_code, out_pdf, title=req.title)

    if not success:
        return CompileResponse(
            success=False,
            pdf_url="",
            compile_time_ms=elapsed_ms,
            error=err_msg,
            title=req.title,
        )

    return CompileResponse(
        success=True,
        pdf_url=f"/api/v1/composer/pdf/{code_hash}.pdf",
        compile_time_ms=elapsed_ms,
        error=None,
        title=req.title,
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


@router.post("/chat", response_model=ChatResponse, summary="AI LaTeX Writing Copilot (assistant-ui clone)")
def composer_chat_endpoint(req: ChatRequest):
    """Interactive AI Assistant specifically tuned for authoring Vietnamese high-school math exams."""
    system_prompt = (
        "Bạn là Trợ lý Soạn thảo Đề thi & LaTeX Chuyên nghiệp (Quesy AI Copilot), lấy cảm hứng từ open-prism.\n"
        "Nhiệm vụ của bạn là hỗ trợ giáo viên Toán tại Việt Nam soạn thảo đề thi chất lượng cao theo chuẩn Thông tư 32/2018/TT-BGDĐT và Quyết định 764/QĐ-BGDĐT (Định dạng 2025).\n\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1. Luôn sử dụng mã LaTeX chuẩn với font CMU Serif / Computer Modern.\n"
        "2. Bảng biến thiên BẮT BUỘC dùng TikZ package tkz-tab (\\tkzTabInit, \\tkzTabLine, \\tkzTabVar). Không dùng \\begin{array} cho bảng biến thiên!\n"
        "3. Đồ thị hàm số và hình học BẮT BUỘC dùng khối \\begin{tikzpicture} ... \\end{tikzpicture}.\n"
        "4. Mọi công thức toán inline bọc trong $...$, phân số dùng \\dfrac, vectơ dùng \\overrightarrow{AB}.\n"
        "5. Cấu trúc đề thi 3 phần chuẩn QĐ 764:\n"
        "   - PHẦN I: Trắc nghiệm 4 lựa chọn (A, B, C, D)\n"
        "   - PHẦN II: Trắc nghiệm Đúng/Sai 4 ý (a, b, c, d)\n"
        "   - PHẦN III: Trắc nghiệm Trả lời ngắn\n\n"
        "HƯỚNG DẪN TRẢ LỜI:\n"
        "- Trả lời ngắn gọn, súc tích bằng tiếng Việt.\n"
        "- Đưa ra mã LaTeX hoàn chỉnh trong khối ```latex ... ``` để giáo viên có thể bấm 1-click chèn vào tài liệu."
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
                        return ChatResponse(reply=reply_text)

    except Exception as e:
        logger.warning(f"AI Provider call failed: {e}. Falling back to rule-based assistant.")

    # Smart offline / local fallback generator if AI provider is unconfigured or network failed
    user_msg_lower = req.message.lower()

    if any(k in user_msg_lower for k in ("bảng biến thiên", "bbt", "tkz-tab", "cực trị")):
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
