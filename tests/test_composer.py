"""Test suite for Quesy Exam Composer (Open-Prism Clone).
Tests template retrieval, LaTeX-to-PDF live compilation, AI writing copilot,
and Question Bank extraction.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.composer import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    DiffSuggestion,
    diagnose_compile_error,
    extract_all_diffs_from_text,
    extract_diff_from_text,
    find_in_latex,
    find_nth_question_in_latex,
)

client = TestClient(app)


def test_composer_templates():
    """Verify that canonical templates are provided for exam authoring."""
    res = client.get("/api/v1/composer/templates")
    assert res.status_code == 200
    data = res.json()
    assert "templates" in data
    assert len(data["templates"]) >= 3
    template_ids = [t["id"] for t in data["templates"]]
    assert "ex_test_standard_exam" in template_ids
    assert "circular_32_full_exam" in template_ids
    assert "variation_table_calculus" in template_ids
    assert "geometry_3d" in template_ids


def test_composer_compile_and_stream_pdf():
    """Verify compiling LaTeX code to PDF and streaming for live preview."""
    latex_code = r"""\documentclass{article}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}

\begin{document}
\section*{ĐỀ THI KIỂM TRA ĐẠI SỐ}

\textbf{Câu 1.} Cho hàm số $y = f(x)$ có bảng biến thiên:
\begin{tikzpicture}
  \tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
  {$x$/.6, $f'(x)$/.6, $f(x)$/2}
  {$-\infty$,$-2$,$1$,$+\infty$}
  \tkzTabLine{,+,0,-,0,+,}
  \tkzTabVar{-/$-\infty$,+/$4$,-/$-1$,+/$+\infty$}
\end{tikzpicture}

Hàm số đồng biến trên khoảng nào?

\textbf{A.} $(-\infty; -2)$ \qquad \textbf{B.} $(-2; 1)$ \qquad \textbf{C.} $(-1; 2)$ \qquad \textbf{D.} $(0; 1)$
\end{document}
"""
    res = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": latex_code, "title": "Đề Thi Đại Số"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["pdf_url"].startswith("/api/v1/composer/pdf/")
    assert data["compile_time_ms"] >= 0
    assert data["total_pages"] >= 1

    # Test PDF streaming endpoint
    pdf_res = client.get(data["pdf_url"])
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000
    assert pdf_res.content[:4] == b"%PDF"


def test_composer_chat_assistant():
    """Verify AI writing assistant responds with structured LaTeX advice and snippets."""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Tạo 1 câu hỏi bảng biến thiên hàm bậc 3 sử dụng tkz-tab",
            "current_latex": "\\begin{document}\\end{document}",
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 20
    assert "tkz-tab" in data["reply"] or "tkzTabInit" in data["reply"] or "tikzpicture" in data["reply"]


def test_composer_save_to_bank():
    """Verify extracting questions from LaTeX into the Question Bank."""
    latex_code = r"""\textbf{Câu 1.} Hàm số $y = \dfrac{2x-1}{x+1}$ có đường tiệm cận đứng là:
\textbf{A.} $x = -1$ \qquad \textbf{B.} $x = 1$ \qquad \textbf{C.} $y = 2$ \qquad \textbf{D.} $y = -1$

\textbf{Câu 2.} Cho hàm số $y = f(x)$. Xét tính đúng sai của các khẳng định sau:
a) Hàm số liên tục trên khoảng $(0; 1)$.
b) Đạo hàm cấp 1 luôn âm.
c) Có 2 điểm cực trị.
d) Giá trị nhỏ nhất bằng 0.
"""
    res = client.post(
        "/api/v1/composer/save-to-bank",
        json={"latex_code": latex_code}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["count"] >= 2


def test_composer_extest_syntax_save_to_bank():
    """Verify extracting questions from ex_test LaTeX syntax into Question Bank."""
    extest_code = r"""\begin{ex}
Cho hàm số $y = f(x)$ có bảng biến thiên. Số điểm cực trị là:
\choice
{\True $2$}
{$1$}
{$0$}
{$3$}
\begin{loigiai}
Hàm số bậc ba có 2 cực trị.
\end{loigiai}
\end{ex}

\begin{ex}
Các khẳng định sau đúng hay sai?
\choiceTF
{\True Hàm số liên tục trên khoảng $(0; 1)$.}
{Đạo hàm cấp 1 luôn âm.}
{\True Có 2 điểm cực trị.}
{Giá trị nhỏ nhất bằng 0.}
\end{ex}

\begin{ex}
Tính tích phân $I = \int_0^1 2x dx$.
\shortans{1}
\end{ex}
"""
    res = client.post(
        "/api/v1/composer/save-to-bank",
        json={"latex_code": extest_code}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["count"] == 3


def test_composer_chat_diff_suggestion():
    """Verify AI writing assistant returns targeted diff when user asks for text/font replacement."""
    latex_code = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\begin{document}
Hello World
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "chỉnh font từ 11 sang 12",
            "current_latex": latex_code,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "diff" in data and data["diff"] is not None
    assert data["diff"]["action"] == "replace"
    assert "11pt" in data["diff"]["old_text"]
    assert "12pt" in data["diff"]["new_text"]

    # Test alternate natural language phrasing "đổi font chữ thành 12"
    res2 = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "đổi font chữ thành 12",
            "current_latex": latex_code,
            "history": []
        }
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["diff"] is not None
    assert "11pt" in data2["diff"]["old_text"]
    assert "12pt" in data2["diff"]["new_text"]


# ---------------------------------------------------------------------------
# 2. Comprehensive Unit Tests: extract_diff_from_text
# ---------------------------------------------------------------------------

def test_extract_diff_diff_block_single_line():
    """extract_diff_from_text: Single-line diff in ```diff block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}
\begin{document}
\end{document}
"""
    reply_text = r"""Tôi đề xuất cập nhật tiêu đề kỳ thi:
```diff
- \title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}
+ \title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.action == "replace"
    assert diff.old_text == r"\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}"
    assert diff.new_text == r"\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}"
    assert "tiêu đề" in diff.description.lower() or "2026" in diff.description


def test_extract_diff_diff_block_multiline():
    """extract_diff_from_text: Multi-line diff in ```diff block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\begin{document}
\textbf{A.} $(-\infty; -1)$
\textbf{B.} $(-1; 2)$
\end{document}
"""
    reply_text = r"""```diff
- \textbf{A.} $(-\infty; -1)$
- \textbf{B.} $(-1; 2)$
+ \textbf{A.} $(-1; 2)$
+ \textbf{B.} $(2; +\infty)$
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.action == "replace"
    assert r"\textbf{A.} $(-\infty; -1)" in diff.old_text
    assert r"\textbf{B.} $(-1; 2)" in diff.old_text
    assert r"\textbf{A.} $(-1; 2)" in diff.new_text
    assert r"\textbf{B.} $(2; +\infty)" in diff.new_text


def test_extract_diff_diff_block_with_description():
    """extract_diff_from_text: Description parsed from text preceding diff block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[dethi]{ex_test}
\begin{document}
\end{document}
"""
    reply_text = r"""Chuyển sang chế độ in lời giải:
```diff
- \usepackage[dethi]{ex_test}
+ \usepackage[loigiai]{ex_test}
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\usepackage[dethi]{ex_test}"
    assert diff.new_text == r"\usepackage[loigiai]{ex_test}"
    assert "lời giải" in diff.description.lower()


def test_extract_diff_diff_block_git_headers():
    """extract_diff_from_text: Ignore git-style diff headers (--- and +++)."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\title{Đề Khảo Sát}
"""
    reply_text = r"""```diff
--- document.tex
+++ document.tex
- \title{Đề Khảo Sát}
+ \title{Đề Chính Thức 2026}
```"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\title{Đề Khảo Sát}"
    assert diff.new_text == r"\title{Đề Chính Thức 2026}"


def test_extract_diff_diff_block_no_trailing_newline():
    """extract_diff_from_text: Handle diff closing ``` without newline."""
    current_latex = r"""\documentclass[11pt]{article}"""
    reply_text = "```diff\n- \\documentclass[11pt]{article}\n+ \\documentclass[12pt]{article}```"
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\documentclass[11pt]{article}"
    assert diff.new_text == r"\documentclass[12pt]{article}"


def test_extract_diff_font_size_standard():
    """extract_diff_from_text: Font size heuristic from user_message (11pt -> 12pt)."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
"""
    diff = extract_diff_from_text("", current_latex, user_message="Đổi cỡ chữ toàn tài liệu sang 12pt")
    assert diff is not None
    assert diff.old_text == r"\documentclass[11pt,a4paper]{article}"
    assert diff.new_text == r"\documentclass[12pt,a4paper]{article}"
    assert "12pt" in diff.description


def test_extract_diff_font_size_without_existing_pt():
    """extract_diff_from_text: Font size added when documentclass has options but no pt."""
    current_latex = r"""\documentclass[a4paper]{article}
\usepackage{fontspec}
"""
    diff = extract_diff_from_text("", current_latex, user_message="chỉnh font 14pt")
    assert diff is not None
    assert diff.old_text == r"\documentclass[a4paper]{article}"
    assert diff.new_text == r"\documentclass[14pt,a4paper]{article}"
    assert "14pt" in diff.description


def test_extract_diff_font_size_bare_documentclass():
    """extract_diff_from_text: Font size added when documentclass has no bracket options."""
    current_latex = r"""\documentclass{article}
\begin{document}
\end{document}
"""
    diff = extract_diff_from_text("", current_latex, user_message="đổi size chữ thành 10pt")
    assert diff is not None
    assert diff.old_text == r"\documentclass{article}"
    assert diff.new_text == r"\documentclass[10pt]{article}"
    assert "10pt" in diff.description


def test_extract_diff_font_size_no_change_when_same():
    """extract_diff_from_text: Returns None if requested font size matches current document."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}"""
    diff = extract_diff_from_text("", current_latex, user_message="đổi cỡ chữ 12pt")
    assert diff is None


def test_extract_diff_string_replacement_old_new_multiline():
    """extract_diff_from_text: OLD: / NEW: multi-line proposal."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\begin{document}
\textbf{A.} $x = 1$
\textbf{B.} $x = 2$
\end{document}
"""
    reply_text = r"""Dưới đây là phương án sửa lại:
OLD:
\textbf{A.} $x = 1$
\textbf{B.} $x = 2$
NEW:
\textbf{A.} $x = -1$
\textbf{B.} $x = -2$
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.action == "replace"
    assert r"\textbf{A.} $x = 1" in diff.old_text
    assert r"\textbf{A.} $x = -1" in diff.new_text


def test_extract_diff_string_replacement_old_new_single_line():
    """extract_diff_from_text: OLD: ... NEW: ... single-line proposal."""
    current_latex = r"""\documentclass[12pt]{article}
\title{Đề Toán Học Kỳ 1}
"""
    reply_text = r"""OLD: \title{Đề Toán Học Kỳ 1}
NEW: \title{Đề Toán Học Kỳ 2}
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\title{Đề Toán Học Kỳ 1}"
    assert diff.new_text == r"\title{Đề Toán Học Kỳ 2}"


def test_extract_diff_string_replacement_search_replace():
    """extract_diff_from_text: SEARCH / REPLACE format block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[dethi]{ex_test}
"""
    reply_text = r"""Sửa gói lệnh hiển thị:
<<<<<<< SEARCH
\usepackage[dethi]{ex_test}
=======
\usepackage[solcolor]{ex_test}
>>>>>>> REPLACE
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\usepackage[dethi]{ex_test}"
    assert diff.new_text == r"\usepackage[solcolor]{ex_test}"
    assert "gói lệnh" in diff.description.lower() or "ai" in diff.description.lower()


def test_extract_diff_string_replacement_inline_vietnamese():
    """extract_diff_from_text: Inline natural language proposal in Vietnamese."""
    current_latex = r"""\documentclass[12pt]{article}
\section*{PHẦN I. Câu hỏi trắc nghiệm}
"""
    reply_text = 'Thay thế `\\section*{PHẦN I. Câu hỏi trắc nghiệm}` bằng `\\section*{PHẦN I. TRẮC NGHIỆM NHIỀU LỰA CHỌN}`'
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\section*{PHẦN I. Câu hỏi trắc nghiệm}"
    assert diff.new_text == r"\section*{PHẦN I. TRẮC NGHIỆM NHIỀU LỰA CHỌN}"


def test_extract_diff_string_replacement_inline_english():
    """extract_diff_from_text: Inline natural language proposal in English."""
    current_latex = r"""\documentclass[12pt]{article}
\textbf{Câu 1.} Cho hàm số $f(x)$
"""
    reply_text = 'Replace `\\textbf{Câu 1.} Cho hàm số $f(x)$` with `\\textbf{Câu 1.} Cho hàm số liên tục $f(x)$`'
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\textbf{Câu 1.} Cho hàm số $f(x)$"
    assert diff.new_text == r"\textbf{Câu 1.} Cho hàm số liên tục $f(x)$"


def test_extract_diff_code_block_diff():
    """extract_diff_from_text: AI returns modified code block where SequenceMatcher identifies diff."""
    current_latex = r"""\documentclass[11pt]{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
"""
    reply_text = r"""Dưới đây là mã mới:
```latex
\documentclass[12pt]{article}
\usepackage{amsmath}
\begin{document}
Hello
\end{document}
```"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\documentclass[11pt]{article}"
    assert diff.new_text == r"\documentclass[12pt]{article}"


def test_extract_diff_negative_cases():
    """extract_diff_from_text: Negative / edge cases return None safely."""
    # Case 1: current_latex is None or empty
    assert extract_diff_from_text("```diff\n- a\n+ b\n```", None) is None
    assert extract_diff_from_text("```diff\n- a\n+ b\n```", "") is None

    # Case 2: old_text not in current_latex
    assert extract_diff_from_text(
        "```diff\n- non_existent_snippet\n+ replacement\n```",
        r"\documentclass{article}"
    ) is None

    # Case 3: old_text equals new_text
    assert extract_diff_from_text(
        "```diff\n- same_text\n+ same_text\n```",
        "same_text in code"
    ) is None

    # Case 4: Plain text explanation without diff or replacement proposal
    assert extract_diff_from_text(
        "Bạn nên thêm gói amssymb để viết các ký hiệu toán học như \\mathbb{R}.",
        r"\documentclass{article}"
    ) is None


# ---------------------------------------------------------------------------
# 3. Comprehensive Unit Tests: API /api/v1/composer/chat
# ---------------------------------------------------------------------------

def test_composer_chat_api_offline_font_change():
    """API /api/v1/composer/chat: Offline font change prompt returns diff suggestion."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\begin{document}
Hello World
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "đổi font chữ thành 12",
            "current_latex": current_latex,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["diff"] is not None
    assert data["diff"]["action"] == "replace"
    assert "11pt" in data["diff"]["old_text"]
    assert "12pt" in data["diff"]["new_text"]


def test_composer_chat_api_offline_solution_toggle():
    """API /api/v1/composer/chat: Toggling solution mode via prompt."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[dethi]{ex_test}
\begin{document}
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "hiện lời giải chi tiết",
            "current_latex": current_latex,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["diff"] is not None
    assert "[dethi]" in data["diff"]["old_text"]
    assert "[loigiai]" in data["diff"]["new_text"]


def test_composer_chat_api_offline_question_generation_extest():
    """API /api/v1/composer/chat: Generating ex_test question returns snippet."""
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "tạo câu hỏi bằng gói ex_test",
                "current_latex": r"\begin{document}\end{document}",
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "reply" in data
        assert "suggested_latex" in data and data["suggested_latex"] is not None
        assert r"\begin{ex}" in data["suggested_latex"]
        assert r"\choice" in data["suggested_latex"]


def test_composer_chat_api_offline_question_generation_true_false():
    """API /api/v1/composer/chat: Generating True/False question according to Decision 764."""
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "tạo câu hỏi đúng sai phần 2 theo chuẩn 764",
                "current_latex": r"\begin{document}\end{document}",
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "PHẦN II" in data["suggested_latex"]
        assert "đúng sai" in data["suggested_latex"].lower() or "đúng/sai" in data["suggested_latex"].lower()


def test_composer_chat_api_offline_question_generation_tikz_plot():
    """API /api/v1/composer/chat: Generating TikZ cubic graph question."""
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "tạo câu hỏi có đồ thị hàm số bậc 3",
                "current_latex": r"\begin{document}\end{document}",
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "tikzpicture" in data["suggested_latex"]


def test_composer_chat_api_offline_inline_string_replacement():
    """API /api/v1/composer/chat: User asks inline string replacement in prompt."""
    current_latex = r"""\documentclass[12pt]{article}
\title{KỲ THI NĂM 2025}
\begin{document}
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Thay thế '\\title{KỲ THI NĂM 2025}' thành '\\title{KỲ THI NĂM 2026}'",
            "current_latex": current_latex,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["diff"] is not None
    assert data["diff"]["old_text"] == r"\title{KỲ THI NĂM 2025}"
    assert data["diff"]["new_text"] == r"\title{KỲ THI NĂM 2026}"


def test_composer_chat_api_offline_empty_current_latex():
    """API /api/v1/composer/chat: Handles empty or None current_latex gracefully."""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Xin chào, bạn có thể giúp gì?",
            "current_latex": "",
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["diff"] is None


def test_composer_chat_api_offline_with_history():
    """API /api/v1/composer/chat: Handles previous chat history array properly."""
    history = [
        {"role": "user", "content": "Chào bạn"},
        {"role": "assistant", "content": "Chào bạn, tôi là Quesy AI Copilot."}
    ]
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Tạo câu hỏi bảng biến thiên",
            "current_latex": r"\begin{document}\end{document}",
            "history": history
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data


def test_composer_chat_api_mocked_ai_provider_diff_block():
    """API /api/v1/composer/chat: Mocked AI provider returning a ```diff block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\title{Đề Thi Khảo Sát}
\begin{document}
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-secret-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Tôi đề xuất đổi tiêu đề đề thi:\n\n"
                        "```diff\n"
                        "- \\title{Đề Thi Khảo Sát}\n"
                        "+ \\title{Đề Thi Tốt Nghiệp THPT 2026}\n"
                        "```"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Đổi tiêu đề sang Đề Thi Tốt Nghiệp THPT 2026",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["action"] == "replace"
            assert data["diff"]["old_text"] == r"\title{Đề Thi Khảo Sát}"
            assert data["diff"]["new_text"] == r"\title{Đề Thi Tốt Nghiệp THPT 2026}"
            assert "tiêu đề" in data["diff"]["description"].lower()


def test_composer_chat_api_mocked_ai_provider_old_new_block():
    """API /api/v1/composer/chat: Mocked AI provider returning an OLD/NEW block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\textbf{A.} $1$
\begin{document}
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-secret-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Sửa phương án A:\n"
                        "OLD:\n\\textbf{A.} $1$\n"
                        "NEW:\n\\textbf{A.} $2$"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Sửa phương án A thành 2",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["old_text"] == r"\textbf{A.} $1$"
            assert data["diff"]["new_text"] == r"\textbf{A.} $2$"


def test_composer_chat_api_mocked_ai_provider_search_replace():
    """API /api/v1/composer/chat: Mocked AI provider returning a SEARCH/REPLACE block."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[dethi]{ex_test}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-secret-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "<<<<<<< SEARCH\n"
                        "\\usepackage[dethi]{ex_test}\n"
                        "=======\n"
                        "\\usepackage[color]{ex_test}\n"
                        ">>>>>>> REPLACE"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Đổi sang gói màu color",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["old_text"] == r"\usepackage[dethi]{ex_test}"
            assert data["diff"]["new_text"] == r"\usepackage[color]{ex_test}"


def test_composer_chat_api_mocked_ai_provider_error_fallback():
    """API /api/v1/composer/chat: Fallback to local rule-based assistant on AI provider error."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\begin{document}
Hello
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-secret-key"
    mock_service.provider = "openai"

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = Exception("Connection timeout")

    # Simulate network failure or timeout in AI call
    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "đổi font chữ thành 12",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert "reply" in data
            assert data["diff"] is not None
            assert "11pt" in data["diff"]["old_text"]
            assert "12pt" in data["diff"]["new_text"]


# ---------------------------------------------------------------------------
# 4. Whitespace, Newline Tolerance & Fuzzy Matching Tests
# ---------------------------------------------------------------------------

def test_extract_diff_whitespace_intraline_discrepancy():
    """extract_diff_from_text: Handle intra-line whitespace and tab differences."""
    current_latex = r"""\documentclass[12pt]{article}
\begin{document}
  \textbf{Câu 1.}   Cho hàm số    $y = f(x)$
\end{document}
"""
    reply_text = r"""Tôi đề xuất sửa lại câu hỏi 1:
```diff
- \textbf{Câu 1.} Cho hàm số $y = f(x)
+ \textbf{Câu 1.} Cho hàm số liên tục $y = f(x)
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.action == "replace"
    assert diff.old_text == r"  \textbf{Câu 1.}   Cho hàm số    $y = f(x)$"
    assert "liên tục" in diff.new_text


def test_extract_diff_indentation_discrepancy_multiline():
    """extract_diff_from_text: Multi-line block with indentation discrepancy."""
    current_latex = r"""\begin{document}
    \begin{ex}
        \choice
            {\True $A = 1$}
            {$B = 2$}
            {$C = 3$}
            {$D = 4$}
    \end{ex}
\end{document}
"""
    reply_text = r"""Đổi đáp án đúng sang B:
```diff
- \choice
-     {\True $A = 1$}
-     {$B = 2$}
+ \choice
+     {$A = 1$}
+     {\True $B = 2$}
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert "{\\True $A = 1$}" in diff.old_text
    assert "{\\True $B = 2$}" in diff.new_text


def test_extract_diff_newline_discrepancy_blank_lines():
    """extract_diff_from_text: Code in current_latex has blank lines that diff omitted."""
    current_latex = r"""\begin{ex}

  \choice
    {\True $A$}

    {$B$}

\end{ex}
"""
    reply_text = r"""Cập nhật các lựa chọn:
```diff
- \begin{ex}
- \choice
- {\True $A$}
- {$B$}
- \end{ex}
+ \begin{ex}
+ \choice
+ {$A$}
+ {\True $B$}
+ \end{ex}
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert r"\choice" in diff.old_text
    assert r"{\True $B$}" in diff.new_text


def test_extract_diff_fuzzy_matching_slight_wording_variation():
    """extract_diff_from_text: Fuzzy matching when AI has minor wording differences."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\section*{PHẦN I. Câu hỏi trắc nghiệm nhiều phương án}
\begin{document}
\end{document}
"""
    reply_text = r"""Đổi tiêu đề phần I theo chuẩn mới:
```diff
- \section*{PHẦN I. Câu hỏi trắc nghiệm nhiều phương án lựa chọn}
+ \section*{PHẦN I. TRẮC NGHIỆM NHIỀU PHƯƠNG ÁN}
```
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert diff.old_text == r"\section*{PHẦN I. Câu hỏi trắc nghiệm nhiều phương án}"
    assert diff.new_text == r"\section*{PHẦN I. TRẮC NGHIỆM NHIỀU PHƯƠNG ÁN}"


def test_extract_diff_fuzzy_matching_search_replace_block():
    """extract_diff_from_text: SEARCH/REPLACE format with whitespace variation."""
    current_latex = r"""\documentclass[12pt]{article}
  \usepackage[dethi]{ex_test}
\begin{document}
"""
    reply_text = r"""<<<<<<< SEARCH
\usepackage[dethi]{ex_test}
=======
\usepackage[solcolor]{ex_test}
>>>>>>> REPLACE
"""
    diff = extract_diff_from_text(reply_text, current_latex)
    assert diff is not None
    assert r"\usepackage[dethi]{ex_test}" in diff.old_text
    assert diff.new_text == r"\usepackage[solcolor]{ex_test}"


def test_find_in_latex_direct_fuzzy_and_whitespace():
    """Direct unit tests for find_in_latex helper function."""
    current = r"""\documentclass[12pt]{article}
\begin{document}
    \title{KỲ THI THỬ 2026}
    \tkzTabInit[nocadre,  lgt=1.2, espcl=2.5]{$x$/1, $y$/1}
\end{document}
"""
    # 1. Whitespace within line
    needle_ws = r"\tkzTabInit[nocadre, lgt=1.2, espcl=2.5]{$x$/1, $y$/1}"
    res_ws = find_in_latex(needle_ws, current)
    assert res_ws is not None
    assert "tkzTabInit" in res_ws

    # 2. Indentation
    needle_indent = r"\title{KỲ THI THỬ 2026}"
    res_indent = find_in_latex(needle_indent, current)
    assert res_indent is not None
    assert "KỲ THI THỬ 2026" in res_indent

    # 3. Fuzzy match
    needle_fuzzy = r"\title{KỲ THI THỬ NĂM 2026}"
    res_fuzzy = find_in_latex(needle_fuzzy, current, fuzzy_threshold=0.7)
    assert res_fuzzy is not None
    assert "KỲ THI THỬ 2026" in res_fuzzy

    # 4. Negative case: completely unrelated text returns None
    assert find_in_latex(r"\section{HOÀN TOÀN KHÔNG TỒN TẠI}", current) is None
    assert find_in_latex("", current) is None
    assert find_in_latex(r"\title{test}", "") is None


# ---------------------------------------------------------------------------
# 5. API /api/v1/composer/chat: compile_error Diagnosis & Fix Diff Tests
# ---------------------------------------------------------------------------

def test_composer_chat_api_compile_error_missing_tikz():
    """API /api/v1/composer/chat: diagnose compile_error with missing tikz package."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{amsmath,amssymb}

\begin{document}
\begin{tikzpicture}
  \draw (0,0) -- (1,1);
\end{tikzpicture}
\end{document}
"""
    compile_err = "! LaTeX Error: Environment tikzpicture undefined.\nl.6 \\begin{tikzpicture}"
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Sửa lỗi biên dịch giúp tôi",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert "reply" in data
        assert data["diff"] is not None
        assert data["diff"]["action"] == "replace"
        assert r"\usepackage{amsmath,amssymb}" in data["diff"]["old_text"]
        assert r"\usepackage{tikz,tkz-tab}" in data["diff"]["new_text"]
        assert "tikz" in data["diff"]["description"].lower()


def test_composer_chat_api_compile_error_missing_extest():
    """API /api/v1/composer/chat: diagnose compile_error with missing ex_test package."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}

\begin{document}
\begin{ex}
Câu hỏi trắc nghiệm
\choice{$A$}{$B$}{$C$}{$D$}
\end{ex}
\end{document}
"""
    compile_err = "! LaTeX Error: Environment ex undefined.\nl.6 \\begin{ex}"
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Khắc phục lỗi biên dịch này",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert r"\usepackage[dethi]{ex_test}" in data["diff"]["new_text"]
        assert "ex_test" in data["diff"]["description"].lower() or "ex" in data["diff"]["description"].lower()


def test_composer_chat_api_compile_error_missing_amsmath():
    """API /api/v1/composer/chat: diagnose compile_error with missing amsmath package."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}

\begin{document}
Tính $I = \dfrac{1}{2}$
\end{document}
"""
    compile_err = "! Undefined control sequence.\nl.5 Tính $I = \\dfrac"
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Sửa lỗi",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert r"\usepackage{amsmath,amssymb}" in data["diff"]["new_text"]


def test_composer_chat_api_compile_error_unclosed_environment():
    """API /api/v1/composer/chat: diagnose compile_error with unclosed environment before \\end{document}."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage{amsmath,amssymb}
\usepackage{tikz}

\begin{document}
\begin{tikzpicture}
  \draw (0,0) -- (1,1);
\end{document}
"""
    compile_err = "! LaTeX Error: \\begin{tikzpicture} on input line 6 ended by \\end{document}."
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Sửa lỗi giúp tôi",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert data["diff"]["old_text"] == r"\end{document}"
        assert r"\end{tikzpicture}" in data["diff"]["new_text"]
        assert r"\end{document}" in data["diff"]["new_text"]


def test_composer_chat_api_compile_error_obsolete_vietnam_package():
    """API /api/v1/composer/chat: diagnose compile_error with obsolete vietnam package."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\begin{document}
Xin chào
\end{document}
"""
    compile_err = "! LaTeX Error: File 'vietnam.sty' not found."
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Sửa lỗi biên dịch",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert r"\usepackage[utf8]{vietnam}" in data["diff"]["old_text"]
        assert r"\usepackage{fontspec}" in data["diff"]["new_text"]


def test_composer_chat_api_compile_error_command_typo():
    """API /api/v1/composer/chat: diagnose compile_error with command typo \\fracc."""
    current_latex = r"""\documentclass[11pt,a4paper]{article}
\begin{document}
Tính tích phân $I = \fracc{1}{2}$.
\end{document}
"""
    compile_err = "! Undefined control sequence.\nl.3 Tính tích phân $I = \\fracc"
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Fix compile error",
                "current_latex": current_latex,
                "compile_error": compile_err,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert r"\fracc" in data["diff"]["old_text"]
        assert r"\dfrac" in data["diff"]["new_text"]


def test_composer_chat_api_compile_error_with_mocked_ai_provider():
    """API /api/v1/composer/chat: Mocked AI provider receives compile_error in prompt and returns diff."""
    current_latex = r"""\documentclass[12pt]{article}
\begin{document}
\invalidcommand{test}
\end{document}
"""
    compile_err = "! Undefined control sequence.\nl.3 \\invalidcommand{test}"
    mock_service = MagicMock()
    mock_service.api_key = "mock-api-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    captured_prompt = []

    def mock_post(endpoint, headers=None, json=None):
        nonlocal captured_prompt
        # Store user prompt content for assertion
        for msg in (json or {}).get("messages", []):
            if msg["role"] == "user":
                captured_prompt.append(msg["content"])
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Tôi đã phân tích lỗi biên dịch và đề xuất sửa dòng lỗi:\n\n"
                            "```diff\n"
                            "- \\invalidcommand{test}\n"
                            "+ % \\invalidcommand{test} (đã vô hiệu hóa)\n"
                            "```"
                        )
                    }
                }
            ]
        }
        return mock_resp

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = mock_post

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Sửa lỗi biên dịch này giúp tôi",
                    "current_latex": current_latex,
                    "compile_error": compile_err,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["old_text"] == r"\invalidcommand{test}"
            assert "% \\invalidcommand{test}" in data["diff"]["new_text"]
            # Verify compile_error was included in prompt sent to LLM
            assert any("LOG LỖI BIÊN DỊCH" in p or "invalidcommand" in p for p in captured_prompt)


def test_composer_chat_api_diff_with_whitespace_discrepancy():
    """API /api/v1/composer/chat: Editor code has irregular spaces/tabs, AI returns clean diff."""
    current_latex = r"""\documentclass[12pt]{article}
\begin{document}
    \textbf{Câu 1.}    Cho hàm số     $y = f(x)$
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-api-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Tôi đề xuất sửa lại như sau:\n\n"
                        "```diff\n"
                        "- \\textbf{Câu 1.} Cho hàm số $y = f(x)\n"
                        "+ \\textbf{Câu 1.} Cho hàm số liên tục $y = f(x)\n"
                        "```"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Sửa câu 1",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            # The matched old_text MUST match the editor buffer exact slice
            assert data["diff"]["old_text"] == r"    \textbf{Câu 1.}    Cho hàm số     $y = f(x)$"


# ---------------------------------------------------------------------------
# 7. Comprehensive Tests: Chat API Integrity & Frontend Display Decoupling
# ---------------------------------------------------------------------------

def test_composer_chat_api_contract_integrity_full_schema():
    """Verify Chat API response strictly adheres to ChatResponse schema: reply, diff, suggested_latex."""
    latex_code = r"""\documentclass[11pt,a4paper]{article}
\usepackage{amsmath}
\begin{document}
\title{ĐỀ KIỂM TRA TOÁN 12}
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "đổi cỡ chữ thành 12pt",
            "current_latex": latex_code,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data and isinstance(data["reply"], str) and len(data["reply"]) > 0
    assert "diff" in data and data["diff"] is not None
    assert "suggested_latex" in data
    # Validate DiffSuggestion contract
    diff = data["diff"]
    assert "action" in diff and diff["action"] == "replace"
    assert "old_text" in diff and diff["old_text"] in latex_code
    assert "new_text" in diff and "12pt" in diff["new_text"]
    assert "description" in diff and isinstance(diff["description"], str)


def test_composer_chat_api_frontend_decoupling_chat_reply_and_diff_coexist():
    """Verify reply holds conversational context while diff holds isolated operational replacement."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\begin{document}
\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}
\begin{ex}
Câu hỏi toán mẫu.
\choice{\True $1$}{$2$}{$3$}{$4$}
\end{ex}
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-api-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    assistant_explanation = (
        "Chào thầy cô, tôi đề xuất sửa lại tiêu đề cho năm 2026 và giữ nguyên các câu hỏi.\n\n"
        "```diff\n"
        "- \\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}\n"
        "+ \\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}\n"
        "```\n\n"
        "Thầy cô có thể nhấn nút Đồng ý trên thanh gợi ý để áp dụng."
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": assistant_explanation}}]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "cập nhật tiêu đề sang năm 2026",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            # 1. Reply text is preserved for chat thread display
            assert "Chào thầy cô, tôi đề xuất sửa lại tiêu đề" in data["reply"]
            assert "```diff" in data["reply"]
            # 2. Diff payload is cleanly isolated for editor pending diff banner
            assert data["diff"] is not None
            assert data["diff"]["action"] == "replace"
            assert data["diff"]["old_text"] == r"\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2025}"
            assert data["diff"]["new_text"] == r"\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}"
            # Ensure old_text does not contain diff marker "-"
            assert not data["diff"]["old_text"].startswith("-")
            # Ensure new_text does not contain diff marker "+"
            assert not data["diff"]["new_text"].startswith("+")
            # Verify clean application without affecting the rest of the document
            new_latex = current_latex.replace(data["diff"]["old_text"], data["diff"]["new_text"], 1)
            assert r"\title{KỲ THI THỬ TỐT NGHIỆP THPT NĂM 2026}" in new_latex
            assert r"\choice{\True $1$}{$2$}{$3$}{$4$}" in new_latex


def test_composer_chat_api_no_diff_for_creative_prompts():
    """Verify creation prompts do not produce false-positive replace diffs in the editor."""
    current_latex = r"""\documentclass[12pt,a4paper]{article}
\begin{document}
\textbf{Câu 1.} Cho hàm số $y=f(x)$.
\end{document}
"""
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Tạo 1 câu hỏi trắc nghiệm mới về hình học không gian Oxyz",
            "current_latex": current_latex,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    # Creative prompt MUST NOT generate a replacement diff that would prompt the editor banner
    assert data.get("diff") is None
    # Reply contains content or suggested latex snippet
    assert len(data["reply"]) > 0


def test_composer_chat_api_choice_option_switch_single_and_multiline():
    """Verify choice option switch produces exact choice replacement diff for both inline and multiline ex_test."""
    with patch("backend.routers.composer.default_ai_provider_service", None):
        # 1. Inline choice
        inline_latex = r"""\begin{ex}
Tính tích phân $I = \int_0^1 2x dx$.
\choice{$0$}{\True $1$}{$2$}{$3$}
\end{ex}
"""
        res1 = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "đổi đáp án đúng sang C",
                "current_latex": inline_latex,
                "history": []
            }
        )
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["diff"] is not None
        assert data1["diff"]["old_text"] == r"\choice{$0$}{\True $1$}{$2$}{$3$}"
        assert data1["diff"]["new_text"] == r"\choice{$0$}{$1$}{\True $2$}{$3$}"

        # 2. Multiline choice
        multiline_latex = r"""\begin{ex}
Tính tích phân $I = \int_0^1 2x dx$.
\choice
{$0$}
{\True $1$}
{$2$}
{$3$}
\end{ex}
"""
        res2 = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "đổi đáp án đúng sang D",
                "current_latex": multiline_latex,
                "history": []
            }
        )
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["diff"] is not None
        assert data2["diff"]["old_text"] in multiline_latex
        all_new = " ".join([d["new_text"] for d in data2.get("diffs", [data2["diff"]])])
        assert r"\True $3$" in all_new
        assert r"\True $1$" not in all_new


def test_composer_chat_api_multi_turn_history_preservation():
    """Verify multi-turn chat history does not corrupt diff extraction or state."""
    current_latex = r"""\documentclass[11pt]{article}
\begin{document}
\title{Đề Khảo Sát Toán}
\end{document}
"""
    history = [
        {"role": "user", "content": "Tài liệu này dùng font gì?"},
        {"role": "assistant", "content": "Tài liệu đang dùng cỡ chữ 11pt tiêu chuẩn."},
        {"role": "user", "content": "Hãy đổi cỡ chữ sang 12pt"}
    ]
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Hãy đổi cỡ chữ sang 12pt",
            "current_latex": current_latex,
            "history": history
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["diff"] is not None
    assert "11pt" in data["diff"]["old_text"]
    assert "12pt" in data["diff"]["new_text"]
    assert "reply" in data and len(data["reply"]) > 0


def test_composer_chat_api_special_latex_characters_diff_safety():
    """Verify diff extraction handles complex LaTeX equations, formulas with $, &, %, _, ^ safely."""
    current_latex = r"""\begin{document}
\begin{align*}
f(x) &= \sqrt{x^2 + 1} + \dfrac{\alpha}{\beta} \\
g(x) &= 10\% \times \int_0^1 x^2 \, dx
\end{align*}
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = "mock-api-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    assistant_reply = (
        "Thay đổi công thức $f(x)$ sang căn bậc 3:\n\n"
        "```diff\n"
        "- f(x) &= \\sqrt{x^2 + 1} + \\dfrac{\\alpha}{\\beta} \\\\\n"
        "+ f(x) &= \\sqrt[3]{x^2 + 1} + \\dfrac{\\alpha}{\\beta} \\\\\n"
        "```\n"
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": assistant_reply}}]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "sửa f(x) thành căn bậc 3",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert r"\sqrt{x^2 + 1}" in data["diff"]["old_text"]
            assert r"\sqrt[3]{x^2 + 1}" in data["diff"]["new_text"]
            # Apply to latex
            applied = current_latex.replace(data["diff"]["old_text"], data["diff"]["new_text"])
            assert r"\sqrt[3]{x^2 + 1}" in applied


def test_composer_chat_api_large_latex_buffer_truncation_safety():
    """Verify large document (>25k characters) does not crash the chat API or diff extraction."""
    # Construct 30k char document
    repeated_content = "\\textbf{Câu hỏi:} Cho hình lập phương $ABCD.A'B'C'D'$.\\par\n" * 600
    large_latex = (
        "\\documentclass[11pt,a4paper]{article}\n"
        "\\title{ĐỀ THI TỔNG HỢP LỚN}\n"
        "\\begin{document}\n"
        + repeated_content +
        "\\title{ĐỀ THI TỔNG HỢP LỚN}\n"
        "\\end{document}\n"
    )
    assert len(large_latex) > 25000

    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "đổi font sang 12pt",
            "current_latex": large_latex,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["diff"] is not None
    assert "11pt" in data["diff"]["old_text"]
    assert "12pt" in data["diff"]["new_text"]


def test_composer_chat_api_empty_and_edge_inputs_resilience():
    """Verify chat API gracefully handles empty, none, or malformed latex buffers."""
    # Empty latex
    res1 = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "xin chào",
            "current_latex": "",
            "history": []
        }
    )
    assert res1.status_code == 200
    assert "reply" in res1.json()

    # None compile_error and empty history
    res2 = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "hướng dẫn soạn đề",
            "current_latex": "\\begin{document}\\end{document}",
            "compile_error": None,
            "history": []
        }
    )
    assert res2.status_code == 200
    assert "reply" in res2.json()


def test_composer_frontend_resizers_and_session_elements():
    """Verify frontend/index.html, style.css, and app.js implement all 4 requirements."""
    from pathlib import Path
    root = Path(__file__).parent.parent
    index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")
    style_css = (root / "frontend" / "static" / "style.css").read_text(encoding="utf-8")

    # Req 1: Bubble chat diff widget eliminated, diff relegated to editor
    assert "Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn" in app_js
    assert "diff-block-wrapper" not in app_js.split("formatAssistantContent(text, diff)")[1].split("insertB64Code")[0]
    assert "```diff" in app_js

    # Req 2: Multi-session storage, fresh greeting on new session, history inspection
    assert "quesy_composer_sessions" in app_js
    assert "archiveCurrentSession" in app_js
    assert "loadSession" in app_js
    assert "clearAllSessions" in app_js
    assert "toggleHistoryView" in app_js
    assert 'id="composer-ai-history-panel"' in index_html
    assert 'id="composer-ai-history-list"' in index_html

    # Req 3: Vertical drag resize for AI Assistant popup (clamp 20% to 90%, 60fps)
    assert 'id="composer-ai-resize-handle"' in index_html
    assert "composer-v-resizer" in index_html
    assert "initAIPopupResizer" in app_js
    assert ".composer-v-resizer" in style_css
    assert ".composer-resizing-v" in style_css
    assert "transition: none !important" in style_css

    # Req 4: Horizontal split resizer between left editor and right preview (clamp 25% to 75%, 60:40 reset)
    assert 'id="composer-split-container"' in index_html
    assert 'id="composer-left-col"' in index_html
    assert 'id="composer-right-col"' in index_html
    assert 'id="composer-split-resizer"' in index_html
    assert "initSplitResizer" in app_js
    assert "#composer-split-resizer" in style_css
    assert ".composer-resizing-h" in style_css
    assert "renderPDF" in app_js


def test_composer_ai_popup_single_resizer_handle_no_duplicates():
    """Verify that the AI assistant popup contains exactly ONE resize handle (no duplicate handles or clutter)."""
    from pathlib import Path
    root = Path(__file__).parent.parent
    index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")

    # 1. Exactly 1 id="composer-ai-resize-handle" in the entire index.html
    assert index_html.count('id="composer-ai-resize-handle"') == 1

    # 2. Inside #composer-ai-popup, verify only ONE vertical resizer exists (no duplicated top bar + center pill)
    popup_start = index_html.find('id="composer-ai-popup"')
    assert popup_start != -1
    popup_end = index_html.find('id="composer-pdf-scroll-container"', popup_start)
    popup_snippet = index_html[popup_start:popup_end]

    # Exactly one element with class composer-v-resizer inside the popup
    assert popup_snippet.count("composer-v-resizer") == 1
    assert popup_snippet.count("composer-ai-pill-handle") == 1
    assert popup_snippet.count("cursor-row-resize") == 1

    # 3. Handle connects to toggleAIPopupHeight with drag guard in app.js
    assert 'onclick="app.composer.toggleAIPopupHeight()"' in popup_snippet
    assert "toggleAIPopupHeight" in app_js
    assert "hasDragged" in app_js


def test_composer_preview_fit_to_width_and_zoom_anchoring():
    """Verify fitToWidth calculation and zoomPreview anchoring with center or cursor anchor points."""
    from pathlib import Path
    root = Path(__file__).parent.parent
    index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")

    # 1. fitToWidth exists and calculates responsive zoom factor
    assert "fitToWidth(fullRender = true)" in app_js
    assert "availableW = Math.max(100, scrollContainer.clientWidth - 32);" in app_js
    assert "fitScale = +(availableW / baseW).toFixed(2);" in app_js
    assert "this.zoomLevel = Math.max(0.2, Math.min(3.0, fitScale));" in app_js

    # 2. fitToWidth is wired to split resizing, ratio reset, and window resize
    assert "this.fitToWidth(false);" in app_js  # during split drag
    assert "this.fitToWidth(true);" in app_js   # on split drop / reset
    assert "window._composerSplitResizeBound" in app_js
    assert "window.addEventListener('resize'" in app_js

    # 3. zoomPreview supports anchoring (anchorPoint / center anchor)
    assert "zoomPreview(delta, anchorPoint = null)" in app_js
    assert "anchorPoint.clientX" in app_js
    assert "anchorPoint.clientY" in app_js
    # Fallback to container center anchor
    assert "originX = scrollContainer.clientWidth / 2;" in app_js
    assert "originY = scrollContainer.clientHeight / 2;" in app_js

    # 4. Proportional coordinate scaling with scroll preservation
    assert "ratio = newScale / oldScale;" in app_js
    assert "scrollContainer.scrollLeft = (oldScrollLeft + originX) * ratio - originX;" in app_js
    assert "scrollContainer.scrollTop = (oldScrollTop + originY) * ratio - originY;" in app_js

    # 5. Ctrl+wheel event binds focalPoint with cursor coordinates
    assert "zoomPreview(delta, { clientX: e.clientX, clientY: e.clientY })" in app_js

    # 6. Container styling in index.html allows smooth multi-directional scrolling without overflow clip
    assert 'id="composer-pdf-scroll-container"' in index_html
    assert 'overflow-x-auto' in index_html.split('id="composer-pdf-scroll-container"')[1].split('>')[0]
    assert 'overflow-x-hidden' not in index_html.split('id="composer-pdf-scroll-container"')[1].split('>')[0]
    assert 'min-w-full w-fit mx-auto origin-top' in index_html


def test_composer_api_and_ui_configuration_integrity():
    """Verify end-to-end API contracts and visual configuration integrity for Exam Composer."""
    # 1. Templates API Contract
    res_tpl = client.get("/api/v1/composer/templates")
    assert res_tpl.status_code == 200
    tpl_data = res_tpl.json()
    assert "templates" in tpl_data
    assert len(tpl_data["templates"]) >= 4
    for tpl in tpl_data["templates"]:
        assert "id" in tpl
        assert "title" in tpl
        assert "latex" in tpl
        assert len(tpl["latex"]) > 50

    # 2. LaTeX Live Compilation & Streaming Contract
    sample_latex = r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}
\textbf{Câu 1.} Khẳng định nào sau đây là đúng?
\end{document}
"""
    res_compile = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": sample_latex, "title": "Đề Khảo Sát"}
    )
    assert res_compile.status_code == 200
    comp_data = res_compile.json()
    assert comp_data["success"] is True
    assert "pdf_url" in comp_data
    assert comp_data["total_pages"] >= 1

    pdf_stream = client.get(comp_data["pdf_url"])
    assert pdf_stream.status_code == 200
    assert pdf_stream.headers["content-type"] == "application/pdf"
    assert pdf_stream.content.startswith(b"%PDF")

    # 3. Chat Copilot Contract
    res_chat = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Thêm câu trắc nghiệm Đúng/Sai theo chuẩn Bộ GD&ĐT",
            "current_latex": sample_latex,
            "history": []
        }
    )
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert "reply" in chat_data
    assert len(chat_data["reply"]) > 10

    # 4. Save to Question Bank Contract
    res_bank = client.post(
        "/api/v1/composer/save-to-bank",
        json={"latex_code": sample_latex}
    )
    assert res_bank.status_code == 200
    assert res_bank.json()["success"] is True

    # 5. UI Layout & Style Configuration Checks
    from pathlib import Path
    root = Path(__file__).parent.parent
    index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")

    # BIÊN DỊCH button uses Apple HIG blue #0071e3
    assert "#0071e3" in index_html
    assert "BIÊN DỊCH" in index_html

    # Zoom percentage indicator
    assert 'id="composer-zoom-display"' in index_html

    # Clamping constraints preserved in app.js
    assert "Math.min(90, Math.max(20, pct))" in app_js
    assert "Math.min(75, Math.max(25, pct))" in app_js
    assert "Math.max(0.4, Math.min(2.5," in app_js


def test_extract_all_diffs_multi_block():
    """Verify extract_all_diffs_from_text correctly extracts multiple diff blocks."""
    from backend.routers.composer import extract_all_diffs_from_text, ChatResponse

    current_latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[dethi]{ex_test}
\begin{document}
Câu 1: Cho hàm số $y=f(x)$.
\end{document}
"""
    reply = """Tôi đề xuất 2 thay đổi:
1. Đổi font:
```diff
- \\documentclass[11pt,a4paper]{article}
+ \\documentclass[12pt,a4paper]{article}
```

2. Đổi gói lệnh:
```diff
- \\usepackage[dethi]{ex_test}
+ \\usepackage[color]{ex_test}
```
"""
    diffs = extract_all_diffs_from_text(reply, current_latex)
    assert len(diffs) == 2
    assert diffs[0].new_text == r"\documentclass[12pt,a4paper]{article}"
    assert diffs[1].new_text == r"\usepackage[color]{ex_test}"

    # Verify ChatResponse sync
    resp = ChatResponse(reply=reply, diffs=diffs)
    assert resp.diff == diffs[0]
    assert resp.diffs == diffs


def test_extract_all_diffs_search_replace_and_old_new_multi():
    """Verify extract_all_diffs_from_text correctly extracts multiple SEARCH/REPLACE and OLD/NEW blocks."""
    from backend.routers.composer import extract_all_diffs_from_text

    current_latex = (
        "\\documentclass[12pt]{article}\n"
        "\\title{KỲ THI THỬ 2025}\n"
        "\\author{Thầy Nam}\n"
        "\\begin{document}\n"
        "Câu 1. Tính tích phân.\n"
        "\\end{document}\n"
    )
    # 1. Multiple SEARCH / REPLACE blocks
    sr1_open = "<" * 7 + " SEARCH\n"
    sr1_div = "=" * 7 + "\n"
    sr1_close = ">" * 7 + " REPLACE\n"
    sr_reply = (
        "Các thay đổi cần thực hiện:\n"
        + sr1_open
        + "\\title{KỲ THI THỬ 2025}\n"
        + sr1_div
        + "\\title{KỲ THI CHÍNH THỨC 2025}\n"
        + sr1_close
        + "\n"
        + sr1_open
        + "\\author{Thầy Nam}\n"
        + sr1_div
        + "\\author{Tổ Toán Tin}\n"
        + sr1_close
    )
    sr_diffs = extract_all_diffs_from_text(sr_reply, current_latex)
    assert len(sr_diffs) == 2
    assert sr_diffs[0].new_text == "\\title{KỲ THI CHÍNH THỨC 2025}"
    assert sr_diffs[1].new_text == "\\author{Tổ Toán Tin}"

    # 2. Multiple OLD / NEW blocks
    old_new_reply = (
        "Đề xuất điều chỉnh:\n"
        "OLD:\n"
        "\\title{KỲ THI THỬ 2025}\n"
        "NEW:\n"
        "\\title{ĐỀ THI KHẢO SÁT CHẤT LƯỢNG}\n\n"
        "OLD:\n"
        "\\author{Thầy Nam}\n"
        "NEW:\n"
        "\\author{Ban Chuyên Môn}\n"
    )
    on_diffs = extract_all_diffs_from_text(old_new_reply, current_latex)
    assert len(on_diffs) == 2
    assert on_diffs[0].new_text == "\\title{ĐỀ THI KHẢO SÁT CHẤT LƯỢNG}"
    assert on_diffs[1].new_text == "\\author{Ban Chuyên Môn}"


def test_composer_chat_api_returns_diffs_field():
    """Verify API /api/v1/composer/chat returns 'diffs' field containing full list of DiffSuggestion."""
    latex_code = (
        "\\documentclass[11pt,a4paper]{article}\n"
        "\\usepackage{amsmath}\n"
        "\\title{Đề Khảo Sát Toán 12}\n"
        "\\begin{document}\n"
        "Hello World\n"
        "\\end{document}\n"
    )
    # 1. Test single rule-based diff returns diffs list with length 1
    res = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "chỉnh font từ 11 sang 12",
            "current_latex": latex_code,
            "history": []
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "diffs" in data
    assert isinstance(data["diffs"], list)
    assert len(data["diffs"]) >= 1
    assert data["diff"] is not None
    assert data["diff"]["old_text"] == data["diffs"][0]["old_text"]
    assert data["diff"]["new_text"] == data["diffs"][0]["new_text"]

    # 2. Test mock multi-diff AI provider response returning complete diffs array
    ai_multi_reply = (
        "Dưới đây là các chỉnh sửa đề xuất:\n"
        "```diff\n"
        "- \\title{Đề Khảo Sát Toán 12}\n"
        "+ \\title{ĐỀ THI TỐT NGHIỆP THPT NĂM 2025}\n"
        "```\n\n"
        "```diff\n"
        "- \\usepackage{amsmath}\n"
        "+ \\usepackage{amsmath,amssymb}\n"
        "```\n"
    )
    mock_provider_resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": ai_multi_reply
                }
            }
        ]
    }
    with patch("backend.services.ai_provider_service.default_ai_provider_service.api_key", "sk-mock-key"), \
         patch("backend.services.ai_provider_service.default_ai_provider_service.provider", "openai"):
        with patch("backend.routers.composer.httpx.Client") as mock_client_cls:
            mock_instance = MagicMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_provider_resp
            mock_instance.post.return_value = mock_resp
            mock_client_cls.return_value.__enter__.return_value = mock_instance

            res_multi = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "Cập nhật tiêu đề và bổ sung gói amssymb",
                    "current_latex": latex_code,
                    "history": []
                }
            )
            assert res_multi.status_code == 200
            multi_data = res_multi.json()
            assert "diffs" in multi_data
            assert len(multi_data["diffs"]) == 2
            assert multi_data["diffs"][0]["new_text"] == "\\title{ĐỀ THI TỐT NGHIỆP THPT NĂM 2025}"
            assert multi_data["diffs"][1]["new_text"] == "\\usepackage{amsmath,amssymb}"
            assert multi_data["diff"] == multi_data["diffs"][0]


def test_composer_ui_multi_diff_banner_and_apply_all_elements():
    """Verify frontend HTML and JavaScript support multi-diff banner navigation (1/N) and 'Áp dụng tất cả'."""
    root = Path(__file__).parent.parent
    index_html = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")

    # 1. HTML Banner elements for multi-diff
    assert 'id="composer-pending-diff-banner"' in index_html
    assert 'id="composer-diff-nav-group"' in index_html
    assert 'id="composer-diff-counter"' in index_html
    assert 'onclick="app.composer.prevDiff()"' in index_html
    assert 'onclick="app.composer.nextDiff()"' in index_html

    # 2. HTML Apply All button
    assert 'id="composer-apply-all-btn"' in index_html
    assert 'onclick="app.composer.applyAllPendingDiffs()"' in index_html
    assert "Áp dụng tất cả" in index_html

    # 3. JavaScript state and multi-diff methods in app.js
    assert "pendingDiffs:" in app_js
    assert "currentDiffIndex:" in app_js
    assert "showPendingDiffs(" in app_js
    assert "renderPendingDiff" in app_js
    assert "prevDiff()" in app_js
    assert "nextDiff()" in app_js
    assert "applyAllPendingDiffs()" in app_js
    assert "applyCurrentDiff()" in app_js


def test_find_nth_question_in_latex_extest_and_classic():
    """Verify find_nth_question_in_latex accurately extracts question 1, 2, n
    from both ex_test.sty documents and classic 'Câu n.' documents.
    """
    # 1. ex_test.sty format with header, section, and multiple ex blocks
    extest_doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage[dethi]{ex_test}
\begin{document}
\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}

\begin{ex}
Cho hàm số $y = f(x)$ có bảng biến thiên. Hàm số đồng biến trên khoảng nào?
\choice{$(-\infty; -1)$}{\True $(-1; 2)$}{$(0; 2)$}{$(-\infty; 2)$}
\begin{loigiai}
Dựa vào bảng biến thiên, hàm số đồng biến trên $(-1; 2)$.
\end{loigiai}
\end{ex}

\begin{ex}[2D1-1.2-1]
Cho hàm số $y = x^3 - 3x^2 + 2$. Điểm cực đại của đồ thị hàm số là:
\choice{$(1; -1)$}{\True $(0; 2)$}{$(2; -2)$}{$(0; 0)$}
\end{ex}

\begin{ex}
Giá trị lớn nhất của hàm số $f(x) = x^4 - 2x^2 + 3$ trên đoạn $[0; 2]$ bằng:
\choice{$3$}{\True $11$}{$2$}{$19$}
\end{ex}
\end{document}
"""
    # Extract Câu 1: must be exact first \begin{ex}...\end{ex}
    q1 = find_nth_question_in_latex(extest_doc, 1)
    assert q1 is not None
    assert q1.startswith(r"\begin{ex}")
    assert q1.endswith(r"\end{ex}")
    assert "Cho hàm số $y = f(x)$ có bảng biến thiên." in q1
    assert "Dựa vào bảng biến thiên, hàm số đồng biến trên $(-1; 2)$." in q1
    # Must NOT include section header or preamble or other questions
    assert r"\section*" not in q1
    assert "Thí sinh trả lời từ câu 1 đến câu 12" not in q1
    assert "Cho hàm số $y = x^3 - 3x^2 + 2$" not in q1

    # Extract Câu 2: must be \begin{ex}[2D1-1.2-1]...\end{ex}
    q2 = find_nth_question_in_latex(extest_doc, 2)
    assert q2 is not None
    assert q2.startswith(r"\begin{ex}[2D1-1.2-1]")
    assert q2.endswith(r"\end{ex}")
    assert "Cho hàm số $y = x^3 - 3x^2 + 2$" in q2
    assert "Cho hàm số $y = f(x)$" not in q2

    # Extract Câu 3:
    q3 = find_nth_question_in_latex(extest_doc, 3)
    assert q3 is not None
    assert "Giá trị lớn nhất của hàm số" in q3

    # Out of bounds & edge cases
    assert find_nth_question_in_latex(extest_doc, 4) is None
    assert find_nth_question_in_latex(extest_doc, 0) is None
    assert find_nth_question_in_latex(extest_doc, -1) is None
    assert find_nth_question_in_latex("", 1) is None
    assert find_nth_question_in_latex(None, 1) is None

    # 2. Classic format with \textbf{Câu n.}
    classic_doc = r"""\documentclass{article}
\begin{document}
\section*{ĐỀ THI ĐẠI SỐ}

\textbf{Câu 1.} Cho hàm số $y=f(x)$ liên tục trên $\mathbb{R}$.
\textbf{A.} $1$ \qquad \textbf{B.} $2$ \qquad \textbf{C.} $3$ \qquad \textbf{D.} $4$

\textbf{Câu 2.} Khối đa diện đều loại $\{3; 3\}$ có bao nhiêu đỉnh?
\textbf{A.} $4$ \qquad \textbf{B.} $6$ \qquad \textbf{C.} $8$ \qquad \textbf{D.} $12$

\textbf{Câu 3.} Cho hình lăng trụ tam giác $ABC.A'B'C'$.
\textbf{A.} $V$ \qquad \textbf{B.} $2V$ \qquad \textbf{C.} $3V$ \qquad \textbf{D.} $4V$
\end{document}
"""
    cq1 = find_nth_question_in_latex(classic_doc, 1)
    assert cq1 is not None
    assert cq1.startswith(r"\textbf{Câu 1.}")
    assert r"liên tục trên $\mathbb{R}$" in cq1
    assert r"\textbf{Câu 2.}" not in cq1
    assert r"\section*" not in cq1

    cq2 = find_nth_question_in_latex(classic_doc, 2)
    assert cq2 is not None
    assert cq2.startswith(r"\textbf{Câu 2.}")
    assert "Khối đa diện đều loại" in cq2
    assert r"\textbf{Câu 3.}" not in cq2

    cq3 = find_nth_question_in_latex(classic_doc, 3)
    assert cq3 is not None
    assert cq3.startswith(r"\textbf{Câu 3.}")
    assert "Cho hình lăng trụ tam giác" in cq3
    assert r"\end{document}" not in cq3

    assert find_nth_question_in_latex(classic_doc, 4) is None

    # 3. Classic format with Câu 1: and \noindent\textbf{Câu 2:}
    colon_doc = r"""\documentclass{article}
\begin{document}
Câu 1: Hàm số nào đồng biến trên $\mathbb{R}$?
A. $y=x^3+x$  B. $y=x^2$  C. $y=x^4$  D. $y=-x$

\noindent\textbf{Câu 2:} Đồ thị hàm số có bao nhiêu tiệm cận?
A. $1$  B. $2$  C. $3$  D. $0$
\end{document}
"""
    col1 = find_nth_question_in_latex(colon_doc, 1)
    assert col1 is not None
    assert "Hàm số nào đồng biến" in col1
    assert "tiệm cận" not in col1

    col2 = find_nth_question_in_latex(colon_doc, 2)
    assert col2 is not None
    assert "tiệm cận" in col2


def test_extract_all_diffs_replace_nth_question_prompt():
    """Verify prompt 'Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi'
    produces exact DiffSuggestion replacing Question 1 without touching Question 2.
    """
    latex_code = r"""\documentclass[11pt,a4paper]{article}
\usepackage[dethi]{ex_test}
\begin{document}

\begin{ex}
Cho hàm số bậc ba $y = f(x)$ có đồ thị như hình bên. Hàm số đồng biến trên khoảng nào?
\choice
{\True $(-\infty; -1)$}
{$(-1; 2)$}
{$(0; 2)$}
{$(-\infty; 2)$}
\begin{loigiai}
Dựa vào đồ thị hàm số đồng biến trên $(-\infty; -1)$.
\end{loigiai}
\end{ex}

\begin{ex}
Khối lăng trụ đứng có diện tích đáy $B = 6$ và chiều cao $h = 3$. Thể tích khối lăng trụ bằng:
\choice
{$6$}
{\True $18$}
{$9$}
{$2$}
\end{ex}

\end{document}
"""
    prompt = "Soạn 1 câu đơn điệu hàm số mức dễ thay thế câu 1 đi"
    ai_reply = r"""Dưới đây là câu hỏi đơn điệu hàm số mới mức độ nhận biết để thay thế cho câu 1:
```latex
\begin{ex}
Cho hàm số $y = x^3 - 3x^2 + 1$. Hàm số đã cho đồng biến trên khoảng nào dưới đây?
\choice
{\True $(2; +\infty)$}
{$(0; 2)$}
{$(-\infty; 2)$}
{$(0; +\infty)$}
\begin{loigiai}
Ta có $y' = 3x^2 - 6x = 3x(x - 2) > 0 \Leftrightarrow x < 0$ hoặc $x > 2$.
Do đó hàm số đồng biến trên khoảng $(2; +\infty)$.
\end{loigiai}
\end{ex}
```
Bạn có thể áp dụng ngay thay đổi này vào đề thi!"""

    diffs = extract_all_diffs_from_text(ai_reply, latex_code, user_message=prompt)
    assert len(diffs) == 1
    diff = diffs[0]
    assert diff.action == "replace"
    # old_text must match Question 1 exactly
    expected_old_q1 = find_nth_question_in_latex(latex_code, 1)
    assert diff.old_text == expected_old_q1
    assert "Cho hàm số bậc ba" in diff.old_text
    # Question 2 must NOT be in old_text
    assert "Khối lăng trụ đứng" not in diff.old_text
    assert "Cho hàm số $y = x^3 - 3x^2 + 1$" in diff.new_text
    assert "câu 1" in diff.description.lower()

    # Simulate applying the diff to latex_code
    applied = latex_code.replace(diff.old_text, diff.new_text)
    # Question 1 is replaced
    assert "Cho hàm số bậc ba" not in applied
    assert "Cho hàm số $y = x^3 - 3x^2 + 1$" in applied
    # Question 2 is perfectly preserved
    assert "Khối lăng trụ đứng có diện tích đáy $B = 6$" in applied
    assert r"\end{document}" in applied

    # 2. Test replacing Question 2
    prompt_q2 = "Thay thế câu 2 bằng một câu tính thể tích chóp"
    ai_reply_q2 = r"""Dưới đây là câu hỏi thay thế câu 2:
```latex
\begin{ex}
Cho khối chóp $S.ABC$ có đáy $ABC$ là tam giác vuông tại $B$, $AB=a$, $BC=2a$. Cạnh bên $SA \perp (ABC)$ và $SA=3a$. Thể tích của khối chóp bằng:
\choice
{$6a^3$}
{$2a^3$}
{\True $a^3$}
{$3a^3$}
\end{ex}
```"""
    diffs_q2 = extract_all_diffs_from_text(ai_reply_q2, latex_code, user_message=prompt_q2)
    assert len(diffs_q2) == 1
    assert diffs_q2[0].old_text == find_nth_question_in_latex(latex_code, 2)
    assert "Khối lăng trụ đứng" in diffs_q2[0].old_text
    assert "Cho hàm số bậc ba" not in diffs_q2[0].old_text
    assert "Cho khối chóp $S.ABC$" in diffs_q2[0].new_text

    # 3. Test API endpoint /api/v1/composer/chat with mocked AI provider
    mock_resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": ai_reply
                }
            }
        ]
    }
    with patch("backend.services.ai_provider_service.default_ai_provider_service.api_key", "sk-test-key"), \
         patch("backend.services.ai_provider_service.default_ai_provider_service.provider", "openai"):
        with patch("backend.routers.composer.httpx.Client") as mock_client_cls:
            mock_inst = MagicMock()
            mock_http_resp = MagicMock()
            mock_http_resp.status_code = 200
            mock_http_resp.json.return_value = mock_resp
            mock_inst.post.return_value = mock_http_resp
            mock_client_cls.return_value.__enter__.return_value = mock_inst

            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": prompt,
                    "current_latex": latex_code,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["old_text"] == expected_old_q1
            assert "Cho hàm số $y = x^3 - 3x^2 + 1$" in data["diff"]["new_text"]
            assert len(data["diffs"]) == 1


def test_composer_chat_no_diff_safety_no_swallowed_code_and_no_false_positive():
    """Verify that when AI response has no diff instructions or is purely conversational,
    backend returns diff=None, diffs=[], and frontend never swallows code or displays false positives.
    """
    latex_code = r"""\documentclass[11pt,a4paper]{article}
\begin{document}
\textbf{Câu 1.} Cho hàm số $y = f(x)$.
\textbf{A.} $1$ \textbf{B.} $2$ \textbf{C.} $3$ \textbf{D.} $4$
\end{document}
"""
    # 1. Informative explanation response (no code block, no diff)
    info_prompt = "Giải thích tính đơn điệu của hàm số bậc ba khi $a > 0$"
    info_reply = (
        "Khi hệ số $a > 0$, nếu $\\Delta' \\le 0$ thì đạo hàm $y' \\ge 0$ với mọi $x$, "
        "khi đó hàm số đồng biến trên toàn bộ $\\mathbb{R}$."
    )
    diffs_info = extract_all_diffs_from_text(info_reply, latex_code, user_message=info_prompt)
    assert diffs_info == []

    # 2. API chat endpoint with informative query returns diff=None, diffs=[]
    mock_info_resp = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": info_reply
                }
            }
        ]
    }
    with patch("backend.services.ai_provider_service.default_ai_provider_service.api_key", "sk-test-key"), \
         patch("backend.services.ai_provider_service.default_ai_provider_service.provider", "openai"):
        with patch("backend.routers.composer.httpx.Client") as mock_client_cls:
            mock_inst = MagicMock()
            mock_http_resp = MagicMock()
            mock_http_resp.status_code = 200
            mock_http_resp.json.return_value = mock_info_resp
            mock_inst.post.return_value = mock_http_resp
            mock_client_cls.return_value.__enter__.return_value = mock_inst

            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": info_prompt,
                    "current_latex": latex_code,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is None
            assert data["diffs"] == []
            assert info_reply in data["reply"]

    # 3. Creative generation prompt without replacement target must return diffs=[]
    gen_prompt = "Tạo 1 câu hỏi mới về hình học phẳng"
    gen_reply = (
        "Dưới đây là một câu hỏi mới để bạn tham khảo:\n"
        "```latex\n"
        "\\begin{ex}\n"
        "Cho tam giác $ABC$ đều cạnh $a$. Tính diện tích tam giác.\n"
        "\\end{ex}\n"
        "```"
    )
    diffs_gen = extract_all_diffs_from_text(gen_reply, latex_code, user_message=gen_prompt)
    assert diffs_gen == []

    # 4. Parity check with frontend logic in app.js
    root = Path(__file__).parent.parent
    app_js = (root / "frontend" / "static" / "app.js").read_text(encoding="utf-8")
    # Verify findNthQuestionInLatex is exposed on composer
    assert "findNthQuestionInLatex(latexCode, n)" in app_js
    # Verify frontend only calls showPendingDiffs when diffs.length > 0
    assert "if (diffs.length) {" in app_js
    assert "this.showPendingDiffs(diffs);" in app_js
    # Verify renderPendingDiff rejects if pendingDiffs is empty
    assert "!this.pendingDiffs || !this.pendingDiffs.length" in app_js


# ---------------------------------------------------------------------------
# 11. Tests for Question Replacement Bug Fix & Editor Display Sync
# ---------------------------------------------------------------------------

def test_find_nth_question_in_latex_comprehensive():
    """Verify find_nth_question_in_latex handles closed ex, unclosed ex, and classic question blocks."""
    from backend.routers.composer import find_nth_question_in_latex

    # 1. Closed ex_test environments
    doc_closed = r"""\documentclass{article}
\usepackage[dethi]{ex_test}
\begin{document}
\begin{ex}[Đề mẫu 1]
Câu hỏi 1: Tìm nguyên hàm của $f(x)=2x$.
\choice{$x^2+C$}{\True $x^2$}{$2+C$}{$x+C$}
\begin{loigiai}
$\int 2x dx = x^2 + C$.
\end{loigiai}
\end{ex}

\begin{ex}
Câu hỏi 2: Tính giới hạn.
\choice{\True $0$}{$1$}{$2$}{$\infty$}
\end{ex}
\end{document}"""

    q1 = find_nth_question_in_latex(doc_closed, 1)
    assert q1 is not None
    assert "Câu hỏi 1" in q1
    assert q1.startswith(r"\begin{ex}[Đề mẫu 1]")
    assert q1.endswith(r"\end{ex}")

    q2 = find_nth_question_in_latex(doc_closed, 2)
    assert q2 is not None
    assert "Câu hỏi 2" in q2
    assert q2.startswith(r"\begin{ex}")
    assert q2.endswith(r"\end{ex}")

    assert find_nth_question_in_latex(doc_closed, 3) is None
    assert find_nth_question_in_latex(doc_closed, 0) is None
    assert find_nth_question_in_latex(doc_closed, -1) is None

    # 2. Classic format: \textbf{Câu N.} and Câu N:
    doc_classic = r"""\begin{document}
\textbf{Câu 1.} Cho hàm số $y=f(x)$.
\textbf{A.} 1 \textbf{B.} 2 \textbf{C.} 3 \textbf{D.} 4

\textbf{Câu 2.} Cho hình chóp $S.ABC$.
a) SA vuông góc...
b) Thể tích...
\end{document}"""

    cq1 = find_nth_question_in_latex(doc_classic, 1)
    assert cq1 is not None
    assert r"\textbf{Câu 1.}" in cq1
    assert "Cho hàm số" in cq1
    assert "Câu 2" not in cq1

    cq2 = find_nth_question_in_latex(doc_classic, 2)
    assert cq2 is not None
    assert r"\textbf{Câu 2.}" in cq2
    assert "hình chóp" in cq2


def test_extract_all_diffs_question_replacement_patterns():
    """Verify question replacement triggers correctly on various user phrasing and AI block formats."""
    from backend.routers.composer import extract_all_diffs_from_text

    doc = r"""\documentclass{article}
\usepackage[dethi]{ex_test}
\begin{document}
\begin{ex}
Câu 1 cũ: Tính đạo hàm của $y = \sin x$.
\choice{\True $\cos x$}{$-\cos x$}{$\sin x$}{$-\sin x$}
\end{ex}

\begin{ex}
Câu 2 cũ: Tính tích phân $\int_0^1 x dx$.
\choice{\True $\dfrac{1}{2}$}{$1$}{$2$}{$0$}
\end{ex}
\end{document}"""

    # Scenario A: "thay thế câu 1" with ```latex ... ``` response
    reply_latex = r"""Dưới đây là câu hỏi mới thay thế:
```latex
\begin{ex}
Câu 1 mới: Tính đạo hàm của $y = e^x$.
\choice{\True $e^x$}{$-e^x$}{$e^{-x}$}{$1$}
\end{ex}
```"""
    diffs1 = extract_all_diffs_from_text(reply_latex, doc, user_message="thay thế câu 1 bằng câu đạo hàm hàm mũ")
    assert len(diffs1) == 1
    assert diffs1[0].action == "replace"
    assert "Câu 1 cũ" in diffs1[0].old_text
    assert "Câu 1 mới" in diffs1[0].new_text
    assert "Thay thế Câu 1" in diffs1[0].description

    # Scenario B: "thay câu 2" with ```diff ... ``` response
    reply_diff = r"""Dưới đây là phần thay đổi:
```diff
- \begin{ex}
- Câu 2 cũ: Tính tích phân $\int_0^1 x dx$.
- \choice{\True $\dfrac{1}{2}$}{$1$}{$2$}{$0$}
- \end{ex}
+ \begin{ex}
+ Câu 2 mới: Tính tích phân $\int_0^1 2x dx$.
+ \choice{\True $1$}{$2$}{$0$}{$-1$}
+ \end{ex}
```"""
    diffs2 = extract_all_diffs_from_text(reply_diff, doc, user_message="thay câu 2 bằng câu tích phân khác")
    assert len(diffs2) == 1
    assert diffs2[0].action == "replace"
    assert "Câu 2 cũ" in diffs2[0].old_text
    assert "Câu 2 mới" in diffs2[0].new_text

    # Scenario C: "replace question 1"
    diffs3 = extract_all_diffs_from_text(reply_latex, doc, user_message="replace question 1 with an exponential function")
    assert len(diffs3) == 1
    assert "Câu 1 cũ" in diffs3[0].old_text


def test_composer_chat_api_replace_question_offline():
    """Verify Chat API generates replace diff targeting the nth question in offline fallback mode."""
    latex_code = r"""\documentclass[12pt]{article}
\usepackage[dethi]{ex_test}
\begin{document}
\begin{ex}
Câu hỏi 1 gốc trong đề thi.
\choice{\True A}{B}{C}{D}
\end{ex}

\begin{ex}
Câu hỏi 2 gốc trong đề thi.
\choice{A}{\True B}{C}{D}
\end{ex}
\end{document}"""

    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "thay thế câu 1 bằng câu hỏi cực trị bảng biến thiên",
                "current_latex": latex_code,
                "history": []
            }
        )
        assert res.status_code == 200
        data = res.json()
        assert data["diff"] is not None
        assert data["diff"]["action"] == "replace"
        assert "Câu hỏi 1 gốc trong đề thi" in data["diff"]["old_text"]
        assert "Câu hỏi 2 gốc trong đề thi" not in data["diff"]["old_text"]
        assert "Thay thế Câu 1" in data["diff"]["description"]
        assert "diffs" in data and len(data["diffs"]) >= 1


def test_composer_chat_api_replace_question_mocked_ai():
    """Verify Chat API extracts correct replacement diff when AI returns code fence for replacing question 2."""
    latex_code = r"""\documentclass[12pt]{article}
\usepackage[dethi]{ex_test}
\begin{document}
\begin{ex}
Câu 1: $1+1=2$.
\choice{\True $2$}{$1$}{$3$}{$4$}
\end{ex}

\begin{ex}
Câu 2: $2+2=4$.
\choice{\True $4$}{$2$}{$5$}{$6$}
\end{ex}
\end{document}"""

    mock_service = MagicMock()
    mock_service.api_key = "mock-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    new_q2 = r"""\begin{ex}
Câu 2 mới: Tính tích phân $I = \int_0^1 3x^2 dx$.
\choice{\True $1$}{$2$}{$3$}{$0$}
\end{ex}"""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": f"Dưới đây là câu hỏi mới thay thế cho Câu 2:\n\n```latex\n{new_q2}\n```"
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "thay thế câu 2 bằng câu tính tích phân",
                    "current_latex": latex_code,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["action"] == "replace"
            assert "Câu 2: $2+2=4$." in data["diff"]["old_text"]
            assert "Câu 2 mới: Tính tích phân" in data["diff"]["new_text"]
            assert "Thay thế Câu 2" in data["diff"]["description"]


# ---------------------------------------------------------------------------
# Preamble-Free Question Editor Tests
# ---------------------------------------------------------------------------

def test_ensure_full_latex_document_wraps_pure_question():
    """Verify ensure_full_latex_document wraps pure question code with full exam preamble."""
    from backend.services.composer_service import ensure_full_latex_document

    pure_question = r"""\begin{ex}
Cho hàm số $y = f(x)$ xác định trên $\mathbb{R}$.
\choice
{\True $A$}
{$B$}
{$C$}
{$D$}
\begin{loigiai}
Lời giải chi tiết cho câu hỏi.
\end{loigiai}
\end{ex}"""

    wrapped = ensure_full_latex_document(pure_question)
    assert r"\documentclass" in wrapped
    assert "fontspec" in wrapped
    assert "amsmath" in wrapped
    assert "tikz" in wrapped
    assert "tkz-tab" in wrapped
    assert r"\usepackage[dethi]{ex_test}" in wrapped
    assert r"\begin{document}" in wrapped
    assert r"\end{document}" in wrapped
    assert r"Cho hàm số $y = f(x)$" in wrapped


def test_ensure_full_latex_document_loigiai_mode():
    """Verify ensure_full_latex_document respects loigiai mode to reveal solutions."""
    from backend.services.composer_service import ensure_full_latex_document

    pure_question = r"""\begin{ex}
Tính giới hạn $\lim_{x \to 0} \frac{\sin x}{x}$.
\shortans{1}
\begin{loigiai}
Áp dụng công thức cơ bản: $\lim_{x \to 0} \frac{\sin x}{x} = 1$.
\end{loigiai}
\end{ex}"""

    wrapped = ensure_full_latex_document(pure_question, mode="loigiai")
    assert r"\documentclass" in wrapped
    assert "fontspec" in wrapped
    assert "amsmath" in wrapped
    assert "tikz" in wrapped
    assert "tkz-tab" in wrapped
    assert r"\usepackage[loigiai]{ex_test}" in wrapped
    assert r"\usepackage[dethi]{ex_test}" not in wrapped
    assert r"\begin{document}" in wrapped
    assert r"\end{document}" in wrapped
    assert r"\shortans{1}" in wrapped


def test_ensure_full_latex_document_backward_compatibility():
    r"""Verify documents that already have \documentclass are not double-wrapped."""
    from backend.services.composer_service import ensure_full_latex_document

    existing_doc = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}
\usepackage[dethi]{ex_test}

\begin{document}
\section*{ĐỀ THI GỐC}
\begin{ex}
Câu hỏi có sẵn documentclass.
\choice{\True $1$}{$2$}{$3$}{$4$}
\end{ex}
\end{document}"""

    processed = ensure_full_latex_document(existing_doc)
    assert processed.count(r"\documentclass") == 1
    assert processed.count(r"\begin{document}") == 1
    assert processed.count(r"\end{document}") == 1
    assert r"\section*{ĐỀ THI GỐC}" in processed

    # Mode switch on existing doc with [dethi]
    processed_lg = ensure_full_latex_document(existing_doc, mode="loigiai")
    assert processed_lg.count(r"\documentclass") == 1
    assert r"\usepackage[loigiai]{ex_test}" in processed_lg
    assert r"\usepackage[dethi]{ex_test}" not in processed_lg


def test_compile_pure_question_latex_to_pdf():
    """Verify compiling pure question LaTeX (no documentclass) to live PDF."""
    pure_latex = r"""\begin{ex}
Cho tứ diện $ABCD$. Gọi $M$ là trung điểm cạnh $AB$. Khẳng định nào sau đây đúng?
\choice
{\True $\vec{MA} + \vec{MB} = \vec{0}$}
{$\vec{MA} - \vec{MB} = \vec{0}$}
{$\vec{MA} = \vec{MB}$}
{$\vec{AB} = 2\vec{MA}$}
\begin{loigiai}
Vì $M$ là trung điểm của $AB$ nên $\vec{MA} + \vec{MB} = \vec{0}$.
\end{loigiai}
\end{ex}"""

    res = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": pure_latex, "title": "Đề Thuần Preamble-Free"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["pdf_url"].startswith("/api/v1/composer/pdf/")
    assert data["total_pages"] >= 1

    pdf_res = client.get(data["pdf_url"])
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000
    assert pdf_res.content[:4] == b"%PDF"


def test_compile_backward_compatibility_full_document():
    """Verify documents with existing documentclass continue to compile smoothly."""
    full_latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage{tikz,tkz-tab}
\usepackage[dethi]{ex_test}

\begin{document}
\section*{KIỂM TRA CHẤT LƯỢNG}
\begin{ex}
Hàm số $y = x^4 - 2x^2$ có bao nhiêu điểm cực trị?
\choice
{\True $3$}
{$1$}
{$2$}
{$0$}
\begin{loigiai}
$y' = 4x^3 - 4x = 4x(x^2 - 1) = 0 \Leftrightarrow x \in \{0; \pm 1\}$. Vậy có 3 điểm cực trị.
\end{loigiai}
\end{ex}
\end{document}"""

    res = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": full_latex, "title": "Đề Đã Có Documentclass"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["pdf_url"].startswith("/api/v1/composer/pdf/")

    pdf_res = client.get(data["pdf_url"])
    assert pdf_res.status_code == 200
    assert pdf_res.content[:4] == b"%PDF"


def test_templates_preamble_free_clean_extest():
    """Verify templates returned by /templates are preamble-free clean ex_test question code."""
    res = client.get("/api/v1/composer/templates")
    assert res.status_code == 200
    data = res.json()
    assert "templates" in data
    assert len(data["templates"]) >= 4

    for tpl in data["templates"]:
        latex = tpl["latex"]
        # Must be preamble-free (no documentclass or begin{document})
        assert r"\documentclass" not in latex, f"Template {tpl['id']} still contains \\documentclass"
        assert r"\begin{document}" not in latex, f"Template {tpl['id']} still contains \\begin{{document}}"
        assert r"\end{document}" not in latex, f"Template {tpl['id']} still contains \\end{{document}}"
        assert r"\usepackage" not in latex, f"Template {tpl['id']} still contains \\usepackage"

        # Must contain clean ex_test question markup
        assert r"\begin{ex}" in latex, f"Template {tpl['id']} should contain clean \\begin{{ex}} markup"


def test_composer_export_endpoint_post_pure_latex():
    """Verify POST /api/v1/composer/export wraps pure LaTeX into a full standalone .tex file."""
    pure_latex = r"""\begin{ex}
Nghiệm của phương trình $2^x = 8$ là:
\choice
{\True $x = 3$}
{$x = 4$}
{$x = 2$}
{$x = 1$}
\begin{loigiai}
Ta có $2^x = 8 = 2^3 \Leftrightarrow x = 3$.
\end{loigiai}
\end{ex}"""

    res = client.post(
        "/api/v1/composer/export",
        json={"latex_code": pure_latex, "mode": "dethi", "title": "De Thi Thu"}
    )
    assert res.status_code == 200
    assert "text/x-tex" in res.headers["content-type"]
    text = res.text
    assert r"\documentclass[12pt,a4paper]{article}" in text
    assert r"\usepackage{fontspec}" in text
    assert r"\usepackage{amsmath,amssymb,amsfonts}" in text
    assert r"\usepackage{multicol}" in text
    assert r"\usepackage{tikz,tkz-tab}" in text
    assert r"\usepackage{tcolorbox}" in text
    assert r"\usepackage[dethi]{ex_test}" in text
    assert r"\begin{document}" in text
    assert r"\end{document}" in text
    assert "2^x = 8" in text


def test_composer_export_endpoint_loigiai_mode():
    """Verify exporting with mode='loigiai' embeds [loigiai] package option."""
    pure_latex = r"""\begin{ex}
Tính đạo hàm của $y = x^2$.
\shortans{2x}
\begin{loigiai}
$(x^2)' = 2x$.
\end{loigiai}
\end{ex}"""

    res = client.post(
        "/api/v1/composer/export",
        json={"latex_code": pure_latex, "mode": "loigiai", "title": "Loi Giai Chi Tiet"}
    )
    assert res.status_code == 200
    text = res.text
    assert r"\usepackage[loigiai]{ex_test}" in text
    assert r"\usepackage[dethi]{ex_test}" not in text


def test_composer_export_endpoint_get():
    """Verify GET /api/v1/composer/export also supports exporting standalone .tex."""
    res = client.get(
        "/api/v1/composer/export",
        params={"latex_code": r"\begin{ex}Cau hoi\end{ex}", "mode": "dethi", "title": "TestGet"}
    )
    assert res.status_code == 200
    assert r"\documentclass" in res.text
    assert r"\usepackage[dethi]{ex_test}" in res.text


def test_composer_chat_api_gemini_provider_empty_or_mocked_key():
    """Verify API /api/v1/composer/chat works when AI_PROVIDER='gemini' and AI_API_KEY='' (or mocked)."""
    current_latex = r"""\documentclass[12pt]{article}
\begin{document}
\title{Đề Thi Gemini Test}
\end{document}
"""
    mock_service = MagicMock()
    mock_service.api_key = ""  # Empty api_key simulating CI state
    mock_service.provider = "gemini"
    mock_service.model = "gemini-1.5-flash"
    mock_service.base_url = ""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Tôi đề xuất cập nhật tiêu đề cho Gemini:\n\n"
                        "```diff\n"
                        "- \\title{Đề Thi Gemini Test}\n"
                        "+ \\title{Đề Thi Gemini Chính Thức 2026}\n"
                        "```"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post(
                "/api/v1/composer/chat",
                json={
                    "message": "cập nhật tiêu đề",
                    "current_latex": current_latex,
                    "history": []
                }
            )
            assert res.status_code == 200
            data = res.json()
            assert data["diff"] is not None
            assert data["diff"]["old_text"] == r"\title{Đề Thi Gemini Test}"
            assert data["diff"]["new_text"] == r"\title{Đề Thi Gemini Chính Thức 2026}"
            assert mock_client.post.call_args[0][0] == "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"


# ---------------------------------------------------------------------------
# 14. Comprehensive Unit Tests: National Exam 2025 Headers, 3 Sections & Templates
# ---------------------------------------------------------------------------

def test_composer_national_exam_2025_templates_frontend():
    """Verify that all 5 National Exam 2025 templates are correctly registered in frontend code."""
    app_js_path = Path("frontend/static/app.js")
    assert app_js_path.exists(), "frontend/static/app.js must exist"
    app_js = app_js_path.read_text(encoding="utf-8")

    # 1. header_quocgia template
    assert "'header_quocgia':" in app_js
    assert "begin{minipage}[t]{0.38" in app_js or "begin{minipage}[t]{0.58" in app_js
    assert "KỲ THI TỐT NGHIỆP THPT NĂM 2025" in app_js
    assert "Mã đề" in app_js or "MÃ ĐỀ" in app_js

    # 2. section_phan1 template
    assert "'section_phan1':" in app_js
    assert "PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn" in app_js
    assert "Thí sinh trả lời từ câu 1 đến câu 12" in app_js

    # 3. section_phan2 template
    assert "'section_phan2':" in app_js
    assert "PHẦN II. Câu trắc nghiệm đúng sai" in app_js
    assert "Thí sinh trả lời từ câu 1 đến câu 4" in app_js

    # 4. section_phan3 template
    assert "'section_phan3':" in app_js
    assert "PHẦN III. Câu trắc nghiệm trả lời ngắn" in app_js
    assert "Thí sinh trả lời từ câu 1 đến câu 6" in app_js

    # 5. dethi_quocgia_full template
    assert "'dethi_quocgia_full':" in app_js
    assert "choice" in app_js
    assert "choiceTF" in app_js
    assert "shortans" in app_js

    # Verify dropdown options in frontend/index.html
    index_html_path = Path("frontend/index.html")
    assert index_html_path.exists(), "frontend/index.html must exist"
    index_html = index_html_path.read_text(encoding="utf-8")
    assert "CẤU TRÚC ĐỀ THI QUỐC GIA 2025" in index_html
    assert "insertTemplate('header_quocgia')" in index_html
    assert "insertTemplate('section_phan1')" in index_html
    assert "insertTemplate('section_phan2')" in index_html
    assert "insertTemplate('section_phan3')" in index_html
    assert "insertTemplate('dethi_quocgia_full')" in index_html


def test_composer_ensure_full_latex_document_national_exam_structures():
    """Verify ensure_full_latex_document packages 2-column header and 3 sections with exam preamble."""
    from backend.services.composer_service import ensure_full_latex_document

    header_snippet = r"""\noindent
\begin{minipage}[t]{0.55\textwidth}
  \textbf{SỞ GD\&ĐT HÀ NỘI}\\
  \textbf{TRƯỜNG THPT CHUYÊN}
\end{minipage}
\begin{minipage}[t]{0.45\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{Môn thi: TOÁN HỌC}\\
  \textit{Thời gian làm bài: 90 phút}
\end{minipage}
\vspace{0.3cm}
\begin{center}
  \textbf{MÃ ĐỀ THI: 101}
\end{center}"""

    # 1. Wrap pure header in dethi mode
    doc = ensure_full_latex_document(header_snippet, mode="dethi", title="Đề Thi Quốc Gia")
    assert r"\documentclass[12pt,a4paper]{article}" in doc
    assert r"\usepackage{fontspec}" in doc
    assert r"\usepackage[dethi]{ex_test}" in doc
    assert r"\usepackage{tcolorbox}" in doc
    assert r"\begin{document}" in doc
    assert r"\end{document}" in doc
    assert r"\begin{minipage}[t]{0.55\textwidth}" in doc
    assert r"KỲ THI TỐT NGHIỆP THPT NĂM 2025" in doc

    # 2. Wrap pure header in loigiai mode
    doc_sol = ensure_full_latex_document(header_snippet, mode="loigiai", title="Lời Giải")
    assert r"\usepackage[loigiai]{ex_test}" in doc_sol
    assert r"\usepackage[dethi]{ex_test}" not in doc_sol

    # 3. Full 3-section exam wrapping
    full_exam_code = header_snippet + r"""
\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
\begin{ex}
Câu hỏi trắc nghiệm
\choice
{A}
{\True B}
{C}
{D}
\end{ex}

\section*{PHẦN II. Câu trắc nghiệm đúng sai}
\begin{ex}
Câu hỏi đúng sai
\choiceTF
{\True Đúng}
{Sai}
{\True Đúng}
{Sai}
\end{ex}

\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}
\begin{ex}
Câu hỏi ngắn
\shortans{42}
\end{ex}"""

    doc_full = ensure_full_latex_document(full_exam_code, mode="dethi")
    assert r"\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}" in doc_full
    assert r"\section*{PHẦN II. Câu trắc nghiệm đúng sai}" in doc_full
    assert r"\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}" in doc_full
    assert r"\shortans{42}" in doc_full


def test_composer_chat_api_national_exam_fallbacks():
    """Verify composer chat endpoint handles 2-column header and 3-section requests with rule-based fallback."""
    # 1. Header request
    res_header = client.post(
        "/api/v1/composer/chat",
        json={"message": "Tạo header 2 cột đề thi chuẩn Bộ GD", "current_latex": "", "history": []}
    )
    assert res_header.status_code == 200
    data_header = res_header.json()
    assert "minipage" in data_header.get("suggested_latex", "")
    assert "KỲ THI TỐT NGHIỆP THPT" in data_header["suggested_latex"] or "2025" in data_header["suggested_latex"] or "SỞ GD" in data_header["suggested_latex"]
    assert "Mã đề" in data_header["suggested_latex"] or "MÃ ĐỀ" in data_header["suggested_latex"]

    # 2. Header request via "tiêu đề 2 cột"
    res_col2 = client.post(
        "/api/v1/composer/chat",
        json={"message": "tạo tiêu đề 2 cột cho trường thpt", "current_latex": "", "history": []}
    )
    assert res_col2.status_code == 200
    data_col2 = res_col2.json()
    assert "minipage" in data_col2.get("suggested_latex", "")

    # 3. Section 1 request
    res_s1 = client.post(
        "/api/v1/composer/chat",
        json={"message": "thêm phần 1 trắc nghiệm 4 lựa chọn", "current_latex": "", "history": []}
    )
    assert res_s1.status_code == 200
    data_s1 = res_s1.json()
    assert "PHẦN I" in data_s1["suggested_latex"]
    assert r"\choice" in data_s1["suggested_latex"]

    # 4. Section 2 request
    res_s2 = client.post(
        "/api/v1/composer/chat",
        json={"message": "soạn phần 2 đúng sai 4 khẳng định", "current_latex": "", "history": []}
    )
    assert res_s2.status_code == 200
    data_s2 = res_s2.json()
    assert "PHẦN II" in data_s2["suggested_latex"]
    assert r"\choiceTF" in data_s2["suggested_latex"]
    assert r"\begin{itemchoice}" in data_s2["suggested_latex"]

    # 5. Section 3 request
    res_s3 = client.post(
        "/api/v1/composer/chat",
        json={"message": "tạo phần 3 trắc nghiệm trả lời ngắn", "current_latex": "", "history": []}
    )
    assert res_s3.status_code == 200
    data_s3 = res_s3.json()
    assert "PHẦN III" in data_s3["suggested_latex"]
    assert r"\shortans" in data_s3["suggested_latex"]

    # 6. Full 3-part exam request
    res_full = client.post(
        "/api/v1/composer/chat",
        json={"message": "tạo trọn bộ đề thi chuẩn quốc gia 2025 với 3 phần", "current_latex": "", "history": []}
    )
    assert res_full.status_code == 200
    data_full = res_full.json()
    full_latex = data_full["suggested_latex"]
    assert "minipage" in full_latex
    assert "PHẦN I" in full_latex
    assert "PHẦN II" in full_latex
    assert "PHẦN III" in full_latex
    assert r"\choice" in full_latex
    assert r"\choiceTF" in full_latex
    assert r"\shortans" in full_latex


def test_compile_latex_source_to_html_national_sections_and_styling():
    """Verify compile_latex_source_to_html renders Section H2 and omits uppercase text-transform."""
    from backend.services.composer_service import compile_latex_source_to_html

    sample_latex = r"""\documentclass[12pt]{article}
\begin{document}
\section*{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn}
Nội dung phần I...

\section*{PHẦN II. Câu trắc nghiệm đúng sai - Xét tính Đúng/Sai}
Nội dung phần II...

\section*{PHẦN III. Câu trắc nghiệm trả lời ngắn}
Nội dung phần III...
\end{document}"""

    html = compile_latex_source_to_html(sample_latex, default_title="Đề Thi Thử 2025")
    assert "<!DOCTYPE html>" in html
    assert "CMU Serif" in html
    assert '<h2 class="latex-section">PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn</h2>' in html
    assert '<h2 class="latex-section">PHẦN II. Câu trắc nghiệm đúng sai - Xét tính Đúng/Sai</h2>' in html
    assert '<h2 class="latex-section">PHẦN III. Câu trắc nghiệm trả lời ngắn</h2>' in html

    # Verify that text-transform: uppercase is NOT enforced on .latex-section
    assert "text-transform: uppercase;" not in html


def test_compile_latex_source_to_html_minipage_and_layout_elements():
    """Verify compile_latex_source_to_html supports minipage, hfill, dotfill, and box commands."""
    from backend.services.composer_service import compile_latex_source_to_html

    sample_layout = r"""\documentclass[12pt]{article}
\begin{document}
\noindent
\begin{minipage}[t]{0.55\textwidth}
  \textbf{SỞ GD\&ĐT TP. HỒ CHÍ MINH}
\end{minipage}
\begin{minipage}[t]{0.45\textwidth}
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}
\end{minipage}

\hfill
\dotfill
\rule{5cm}{0.4pt}
\framebox{MÃ ĐỀ 101}
\fbox{HẾT}
\end{document}"""

    html = compile_latex_source_to_html(sample_layout, default_title="Bố cục 2 cột")
    # Verify minipage width inline-block styling is present
    assert '<div style="display: inline-block' in html
    assert "&lt;div" not in html
    assert '<hr style="width:' in html
    assert "0.55\\textwidth" in html or "0.55\textwidth" in html
    assert "0.45\\textwidth" in html or "0.45\textwidth" in html
    # Verify hfill float: right
    assert "float: right;" in html
    # Verify dotfill border-bottom dotted
    assert "border-bottom: 1px dotted" in html
    # Verify framebox/fbox solid border
    assert "border: 1px solid #000;" in html


def test_composer_frontend_compact_bar_styling():
    """Verify compact bar has Apple purple focus ring/glow and proper CSS hierarchy."""
    css_path = Path("frontend/static/style.css")
    assert css_path.exists(), "frontend/static/style.css must exist"
    css = css_path.read_text(encoding="utf-8")

    # Verify CSS selector for compact bar focus-within
    assert "#composer-ai-compact-bar:focus-within" in css or "#composer-compact-input" in css
    # Verify Apple Purple styling presence (#a855f7 or rgba)
    assert "#a855f7" in css or "rgba(168, 85, 247" in css or "168, 85, 247" in css


def test_composer_national_exam_2025_header_centering_and_single_bottom_rule():
    r"""Verify that National Exam 2025 Header uses 0.38/0.58 ratio, \centering on both sides,
    omits the top rule, and keeps only a single bottom rule below candidate metadata."""
    import re
    app_js_path = Path("frontend/static/app.js")
    assert app_js_path.exists(), "frontend/static/app.js must exist"
    app_js = app_js_path.read_text(encoding="utf-8")

    # Extract header_quocgia template
    m = re.search(r"'header_quocgia':\s*`([\s\S]*?)`", app_js)
    assert m is not None, "header_quocgia template must exist in app.js"
    header_tex = m.group(1)

    # 1. Verify ratio 0.38\textwidth (left) and 0.58\textwidth (right)
    assert "0.38" in header_tex and "minipage" in header_tex
    assert "0.58" in header_tex and "minipage" in header_tex

    # 2. Verify \centering on both columns
    assert "hfill" in header_tex
    parts = re.split(r"\\+hfill", header_tex)
    assert len(parts) >= 2, "Header must have two columns separated by hfill"
    left_col, right_col = parts[0], parts[1]
    assert "centering" in left_col, "Left column must have centering"
    assert "centering" in right_col, "Right column must have centering"

    # 3. Verify top rule is removed (no rule before candidate metadata)
    idx_candidate = header_tex.find("Họ và tên thí sinh")
    assert idx_candidate != -1, "Candidate metadata line must exist"
    assert "rule" not in header_tex[:idx_candidate], "Top rule above candidate info must be omitted"

    # 4. Verify single bottom rule below candidate metadata
    candidate_and_below = header_tex[idx_candidate:]
    assert "rule" in candidate_and_below and "0.5pt" in candidate_and_below, "Single bottom rule below candidate info"
    assert "framebox" in candidate_and_below or "fbox" in candidate_and_below


def test_composer_national_exam_2025_section_textbf_textit_format():
    r"""Verify that 2025 sections use \noindent\textbf{PHẦN ...} \textit{...} and discard \section*."""
    import re
    app_js_path = Path("frontend/static/app.js")
    app_js = app_js_path.read_text(encoding="utf-8")

    # Section 1
    m1 = re.search(r"'section_phan1':\s*`([\s\S]*?)`", app_js)
    assert m1 is not None
    s1 = m1.group(1)
    assert "PHẦN I." in s1
    assert "noindent" in s1
    assert "textbf{" in s1
    assert "textit{" in s1
    assert "section*" not in s1

    # Section 2
    m2 = re.search(r"'section_phan2':\s*`([\s\S]*?)`", app_js)
    assert m2 is not None
    s2 = m2.group(1)
    assert "PHẦN II." in s2
    assert "noindent" in s2
    assert "textbf{" in s2
    assert "textit{" in s2
    assert "section*" not in s2

    # Section 3
    m3 = re.search(r"'section_phan3':\s*`([\s\S]*?)`", app_js)
    assert m3 is not None
    s3 = m3.group(1)
    assert "PHẦN III." in s3
    assert "noindent" in s3
    assert "textbf{" in s3
    assert "textit{" in s3
    assert "section*" not in s3


def test_composer_sync_section_question_counts_comprehensive():
    """Verify sync_section_question_counts correctly updates 'từ câu 1 đến câu {count}'
    across Part I (e.g. 11 questions), Part II (4 questions), Part III (6 questions),
    supports classic \\textbf{Câu} syntax, and leaves text untouched when count is 0."""
    from backend.services import composer_service

    assert hasattr(composer_service, "sync_section_question_counts"), (
        "Function 'sync_section_question_counts' must be implemented in backend/services/composer_service.py"
    )
    sync_func = getattr(composer_service, "sync_section_question_counts")

    # Case 1: Part I with 11 questions (\\begin{ex}) -> updates to "từ câu 1 đến câu 11"
    latex_part1 = (
        r"\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} "
        r"\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}"
        + "\n"
        + "\n".join([rf"\begin{{ex}}\nCâu hỏi {i}\n\choice\n{{A}}\n{{\True B}}\n{{C}}\n{{D}}\n\end{{ex}}" for i in range(1, 12)])
    )
    res1 = sync_func(latex_part1)
    assert "từ câu 1 đến câu 11" in res1
    assert "từ câu 1 đến câu 12" not in res1

    # Case 2: Part II with 4 questions (\\begin{ex}) -> updates to "từ câu 1 đến câu 4"
    latex_part2 = (
        r"\noindent\textbf{PHẦN II. Câu trắc nghiệm đúng sai.} "
        r"\textit{Thí sinh trả lời từ câu 1 đến câu 5. Trong mỗi ý a), b), c), d) ở mỗi câu, thí sinh chọn đúng hoặc sai.}"
        + "\n"
        + "\n".join([rf"\begin{{ex}}\nCâu đúng sai {i}\n\choiceTF\n{{\True Đúng}}\n{{Sai}}\n{{\True Đúng}}\n{{Sai}}\n\end{{ex}}" for i in range(1, 5)])
    )
    res2 = sync_func(latex_part2)
    assert "từ câu 1 đến câu 4" in res2
    assert "từ câu 1 đến câu 5" not in res2

    # Case 3: Part III with 6 questions (\\begin{ex}) -> updates to "từ câu 1 đến câu 6"
    latex_part3 = (
        r"\noindent\textbf{PHẦN III. Câu trắc nghiệm trả lời ngắn.} "
        r"\textit{Thí sinh trả lời từ câu 1 đến câu 8.}"
        + "\n"
        + "\n".join([rf"\begin{{ex}}\nCâu ngắn {i}\n\shortans{{{i}}}\n\end{{ex}}" for i in range(1, 7)])
    )
    res3 = sync_func(latex_part3)
    assert "từ câu 1 đến câu 6" in res3
    assert "từ câu 1 đến câu 8" not in res3

    # Case 4: Classic \\textbf{Câu X.} questions (without \\begin{ex})
    latex_classic = (
        r"\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} "
        r"\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}"
        + "\n"
        + "\n".join([
            rf"\textbf{{Câu {i}.}} Nội dung câu {i}... "
            r"\textbf{A.} $1$ \quad \textbf{B.} $2$ \quad \textbf{C.} $3$ \quad \textbf{D.} $4$"
            for i in range(1, 8)
        ])
    )
    res_classic = sync_func(latex_classic)
    assert "từ câu 1 đến câu 7" in res_classic
    assert "từ câu 1 đến câu 12" not in res_classic

    # Case 5: Zero questions -> leaves count string untouched (does not corrupt into "từ câu 1 đến câu 0")
    latex_empty = (
        r"\noindent\textbf{PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.} "
        r"\textit{Thí sinh trả lời từ câu 1 đến câu 12. Mỗi câu hỏi thí sinh chỉ chọn một phương án.}"
        + "\nChưa có câu hỏi nào được thêm."
    )
    res_empty = sync_func(latex_empty)
    assert "từ câu 1 đến câu 12" in res_empty
    assert "từ câu 1 đến câu 0" not in res_empty


def test_compile_latex_source_to_html_header_038_058_and_centering():
    """Verify compile_latex_source_to_html correctly styles 0.38/0.58 columns with text-align: center."""
    from backend.services.composer_service import compile_latex_source_to_html

    header_tex = r"""\documentclass{article}
\begin{document}
\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT}
\end{minipage}
\noindent\\rule{\textwidth}{0.5pt}
\end{document}"""

    html = compile_latex_source_to_html(header_tex, default_title="Đề thi 2025")
    assert "<!DOCTYPE html>" in html
    assert "0.38" in html or "38" in html
    assert "0.58" in html or "58" in html
    assert "text-align: center;" in html
    assert "<hr" in html











def test_composer_all_backend_and_frontend_templates_compilation_and_syntax():
    r"""TC-COMP-28: Verify all canonical templates in backend TEMPLATES and frontend EX_TEST_TEMPLATES
    compile cleanly without syntax errors, typos (\ule, \choiceTFt, ight|), and have valid LaTeX/HTML output.
    """
    import re
    from backend.services.composer_service import TEMPLATES, compile_latex_source_to_html

    # 1. Verify backend TEMPLATES
    assert len(TEMPLATES) >= 4
    for tmpl_id, tmpl_data in TEMPLATES.items():
        latex = tmpl_data.get("latex", "")
        assert len(latex) > 20, f"Template {tmpl_id} has empty latex"
        # Check for typos
        assert r"\ule{\textwidth}" not in latex, f"Typo ule found in backend template {tmpl_id}"
        assert r"\choiceTFt" not in latex, f"Typo \\choiceTFt found in backend template {tmpl_id}"
        assert not re.search(r'(?<!r)ight\|', latex), f"Typo ight| found in backend template {tmpl_id}"
        
        # Test HTML preview rendering
        html = compile_latex_source_to_html(latex, default_title=tmpl_data.get("title", ""))
        assert "<!DOCTYPE html>" in html
        assert len(html) > 500

    # 2. Verify frontend EX_TEST_TEMPLATES
    app_js_path = Path(__file__).resolve().parent.parent / "frontend" / "static" / "app.js"
    assert app_js_path.exists(), "frontend/static/app.js must exist"
    app_js_content = app_js_path.read_text(encoding="utf-8")

    # Check for forbidden typos in app.js
    assert r"\ule{\textwidth}" not in app_js_content and r"\\ule{" not in app_js_content
    assert r"\choiceTFt" not in app_js_content
    assert not re.search(r'(?<!r)ight\|', app_js_content)

    # Extract template strings from EX_TEST_TEMPLATES
    m_extest = re.search(r'EX_TEST_TEMPLATES\s*:\s*\{([\s\S]*?)\n\s*\},', app_js_content)
    assert m_extest is not None, "Could not locate EX_TEST_TEMPLATES in app.js"
    extest_body = m_extest.group(1)

    # Validate that templates render without crashing
    dethi_full_match = re.search(r"'dethi_quocgia_full'\s*:\s*`([\s\S]*?)`", extest_body)
    assert dethi_full_match is not None
    dethi_full_latex = dethi_full_match.group(1)
    assert "rule" in dethi_full_latex and "0.5pt" in dethi_full_latex
    assert "choiceTF[1]" in dethi_full_latex
    # Ensure choiceTF block in template has no trailing \\ after braces
    m_tf = re.search(r'choiceTF(?:\[1\])?([\s\S]*?)begin\{loigiai\}', dethi_full_latex)
    if m_tf:
        assert "}\\\\" not in m_tf.group(1)

    html_dethi = compile_latex_source_to_html(dethi_full_latex, default_title="Đề thi 2025")
    assert "<!DOCTYPE html>" in html_dethi
    assert "PHẦN I" in html_dethi
    assert "PHẦN II" in html_dethi
    assert "PHẦN III" in html_dethi


def test_composer_true_false_choiceTF1_syntax_and_html_rendering():
    r"""TC-COMP-30: Verify True/False questions strictly enforce \choiceTF[1] single-column 100% width,
    prohibit trailing backslashes '\\' after {...}, and compile to proper HTML previews.
    """
    import re
    from backend.services.composer_service import TEMPLATES, compile_latex_source_to_html

    # 1. Check all backend templates with True/False questions
    for tmpl_id, tmpl in TEMPLATES.items():
        latex = tmpl.get("latex", "")
        if r"\choiceTF" in latex:
            # Enforce [1] parameter
            assert r"\choiceTF[1]" in latex, f"Template {tmpl_id} must use \\choiceTF[1]"
            # Prohibit \\ immediately after option closing braces
            lines = latex.splitlines()
            for idx, line in enumerate(lines):
                if line.strip().startswith(r"\choiceTF"):
                    for opt_line in lines[idx + 1 : idx + 5]:
                        assert not re.search(r'\}\s*\\\\', opt_line), (
                            f"Trailing \\ found after brace in {tmpl_id}: {opt_line}"
                        )

    # 2. Test HTML preview rendering for \choiceTF[1]
    tf_sample = r"""\begin{ex}
Xét tính đúng sai của các khẳng định sau:
\choiceTF[1]
{\True Mệnh đề A đúng.}
{Mệnh đề B sai.}
{\True Mệnh đề C đúng.}
{Mệnh đề D sai.}
\begin{loigiai}
Lời giải chi tiết.
\end{loigiai}
\end{ex}"""

    html = compile_latex_source_to_html(tf_sample)
    assert "width: 100%" in html or "display: block" in html
    assert "[Đ]" in html
    assert "[S]" in html
    assert "a)" in html
    assert "b)" in html
    assert "c)" in html
    assert "d)" in html
    assert 'width: 48%' not in html


def test_composer_chat_api_compile_error_log_payload_support():
    """TC-COMP-29: Verify AI Copilot accepts both compile_error_log and compile_error keys in payload."""
    cur_latex = r"""\begin{ex}
Cho hàm số $y = f(x)$.
\badcommand
\end{ex}"""

    # 1. Using new compile_error_log field
    res1 = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "Sửa lỗi biên dịch giúp tôi",
            "current_latex": cur_latex,
            "compile_error_log": "! Undefined control sequence. \nl.15 \\badcommand",
            "history": []
        }
    )
    assert res1.status_code == 200
    data1 = res1.json()
    assert "reply" in data1
    assert data1["diff"] is not None
    assert data1["diff"]["action"] == "replace"
    assert "\\badcommand" in data1["diff"]["old_text"]

    # 2. Using legacy compile_error field
    res2 = client.post(
        "/api/v1/composer/chat",
        json={
            "message": "fix lỗi",
            "current_latex": cur_latex,
            "compile_error": "! Undefined control sequence. \nl.15 \\badcommand",
            "history": []
        }
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["diff"] is not None
    assert data2["diff"]["action"] == "replace"


def test_composer_compile_error_preamble_free_line_offset_mapping():
    """TC-COMP-29: Verify Preamble-Free line offset mapping L_user = L_comp - 11."""
    preamble_free_latex = (
        r"\begin{ex}" + "\n"
        r"Cho hàm số $y = f(x)$." + "\n"
        r"\choiceTF[1]" + "\n"
        r"{\True Khẳng định a.}\\" + "\n"
        r"{Khẳng định b.}" + "\n"
        r"{\True Khẳng định c.}" + "\n"
        r"{Khẳng định d.}" + "\n"
        r"\end{ex}"
    )

    # L_comp = 15 -> L_user = 15 - 11 = 4
    compile_log = "! LaTeX Error: There's no line here to end.\nl.15 {\\True Khẳng định a.}\\\\"

    res = diagnose_compile_error(
        compile_error=compile_log,
        current_latex=preamble_free_latex,
        user_message="fix lỗi biên dịch"
    )
    assert res is not None
    assert res.diff is not None
    assert res.diff.action == "replace"
    assert res.diff.old_text == r"{\True Khẳng định a.}\\"
    assert res.diff.new_text == r"{\True Khẳng định a.}"

    # Full document with \documentclass (offset should NOT be applied)
    full_latex = (
        r"\documentclass{article}" + "\n"
        r"\begin{document}" + "\n"
        r"\begin{ex}" + "\n"
        r"{\True Khẳng định a.}\\" + "\n"
        r"\end{ex}" + "\n"
        r"\end{document}"
    )
    compile_log_full = "error: document.tex:4: There's no line here to end."
    res_full = diagnose_compile_error(
        compile_error=compile_log_full,
        current_latex=full_latex,
        user_message="fix error"
    )
    assert res_full is not None
    assert res_full.diff is not None
    assert res_full.diff.old_text == r"{\True Khẳng định a.}\\"
    assert res_full.diff.new_text == r"{\True Khẳng định a.}"


def test_composer_compile_error_diagnosis_five_classic_families():
    r"""TC-COMP-29: Verify diagnose_compile_error correctly diagnoses all 5 classic TeX error families:
    1. There's no line here to end
    2. Undefined control sequence (typos: \ule, \choiceTFt, ight|)
    3. Missing $ inserted
    4. Missing 
ight. inserted / Extra }, or forgotten 
ight
    5. Environment undefined
    """
    # 1. Family 1: There's no line here to end
    latex_family1 = r"""\begin{ex}
Tính toán biểu thức:
\choiceTF[1]
{\True Phương án 1}\\
{Phương án 2}
{\True Phương án 3}
{Phương án 4}
\end{ex}"""
    err1 = "! LaTeX Error: There's no line here to end. \nl.14 {\\True Phương án 1}\\\\"
    res1 = diagnose_compile_error(err1, latex_family1)
    assert res1 is not None
    assert res1.diff is not None
    assert r"\\" not in res1.diff.new_text
    assert "There's no line here to end" in res1.reply

    # 2. Family 2: Undefined control sequence
    # 2a: \ule -> \rule
    latex_ule = r"""\noindent
\ule{\textwidth}{0.5pt}
\section*{Đề thi}"""
    err_ule = "! Undefined control sequence. \nl.2 \\ule"
    res_ule = diagnose_compile_error(err_ule, latex_ule)
    assert res_ule is not None
    assert res_ule.diff is not None
    assert r"\rule" in res_ule.diff.new_text

    # 2b: \choiceTFt -> \choiceTF[1]
    latex_choicetft = r"""\begin{ex}
\choiceTFt
{\True a}
{b}
{\True c}
{d}
\end{ex}"""
    err_choicetft = "! Undefined control sequence. \nl.13 \\choiceTFt"
    res_choicetft = diagnose_compile_error(err_choicetft, latex_choicetft)
    assert res_choicetft is not None
    assert res_choicetft.diff is not None
    assert r"\choiceTF[1]" in res_choicetft.diff.new_text

    # 2c: ight| -> \right|
    latex_right = r"""\begin{loigiai}
$I = (x^2 + x) ight|_0^2 = 6$.
\end{loigiai}"""
    err_right = "! Undefined control sequence. \nl.13 ight"
    res_right = diagnose_compile_error(err_right, latex_right)
    assert res_right is not None
    assert res_right.diff is not None
    assert r"\right|_0^2" in res_right.diff.new_text

    # 3. Family 3: Missing $ inserted
    latex_missing_dollar = r"""\begin{ex}
Cho hàm số y = x^2 + 2x.
\choice
{\True 1}
{2}
{3}
{4}
\end{ex}"""
    err_dollar = "! Missing $ inserted. \nl.13 Cho hàm số y = x^2 + 2x."
    res_dollar = diagnose_compile_error(err_dollar, latex_missing_dollar)
    assert res_dollar is not None
    assert res_dollar.diff is not None
    assert "$" in res_dollar.diff.new_text
    assert "Missing $" in res_dollar.reply

    # 4. Family 4: Missing \right. inserted / forgotten \right
    latex_unbalanced_right = r"""\begin{loigiai}
$I = (x^2 + 1) \right|_0^1 = 2$.
\end{loigiai}"""
    err_unbalanced = "! Missing \\right. inserted. \nl.13 $I = (x^2 + 1) \\right|_0^1 = 2$."
    res_unbalanced = diagnose_compile_error(err_unbalanced, latex_unbalanced_right)
    assert res_unbalanced is not None
    assert res_unbalanced.diff is not None
    assert r"\left." in res_unbalanced.diff.new_text

    # 5. Family 5: Environment undefined
    latex_env = r"""\documentclass{article}
\begin{document}
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
\end{document}"""
    err_env = "! LaTeX Error: Environment tikzpicture undefined."
    res_env = diagnose_compile_error(err_env, latex_env)
    assert res_env is not None
    assert res_env.diff is not None
    assert r"\usepackage{tikz,tkz-tab}" in res_env.diff.new_text


# ===========================================================================
# TC-COMP-30 to TC-COMP-38: Multi-modal AI Chat with Image Attachment
# ===========================================================================

def test_composer_pydantic_models_images_field():
    """TC-COMP-30: Verify Pydantic models ChatMessage and ChatRequest support the 'images' field.
    Tests default factory, explicit empty list, single and multiple base64 data URLs.
    """
    # 1. ChatMessage defaults and customizations
    msg_default = ChatMessage(role="user", content="Hello AI")
    assert msg_default.images == []
    assert msg_default.role == "user"
    assert msg_default.content == "Hello AI"

    msg_empty = ChatMessage(role="assistant", content="Reply", images=[])
    assert msg_empty.images == []

    sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    msg_with_img = ChatMessage(role="user", content="Analyze this chart", images=[sample_b64])
    assert msg_with_img.images is not None
    assert len(msg_with_img.images) == 1
    assert msg_with_img.images[0] == sample_b64

    msg_multi_img = ChatMessage(
        role="user",
        content="Two images",
        images=["data:image/png;base64,img1", "data:image/jpeg;base64,img2"]
    )
    assert msg_multi_img.images is not None
    assert len(msg_multi_img.images) == 2
    assert msg_multi_img.images[0] == "data:image/png;base64,img1"
    assert msg_multi_img.images[1] == "data:image/jpeg;base64,img2"

    # 2. ChatRequest defaults, serialization, and history preservation
    req_default = ChatRequest(message="Generate question")
    assert req_default.images == []
    assert req_default.history == []

    req_with_img = ChatRequest(
        message="Extract formula from image",
        current_latex=r"\begin{document}\end{document}",
        images=[sample_b64]
    )
    assert req_with_img.images is not None
    assert len(req_with_img.images) == 1
    assert req_with_img.images[0].startswith("data:image/png;base64,")

    req_full = ChatRequest(
        message="Follow-up on previous problem",
        history=[msg_with_img, ChatMessage(role="assistant", content="Here is the question")],
        images=["data:image/png;base64,img_step2"]
    )
    assert req_full.history is not None
    assert len(req_full.history) == 2
    assert req_full.history[0].images == [sample_b64]
    assert req_full.images is not None
    assert req_full.images == ["data:image/png;base64,img_step2"]

    # Model dump / JSON serialization check
    dumped = req_full.model_dump()
    assert "images" in dumped
    assert dumped["images"] == ["data:image/png;base64,img_step2"]
    assert dumped["history"][0]["images"] == [sample_b64]


def test_composer_chat_api_multimodal_offline_fallback():
    """TC-COMP-31: Verify POST /api/v1/composer/chat offline fallback when images are attached.
    Ensures smart offline generator recognizes image presence and produces an ex_test question
    with TikZ graph or variation table snippet.
    """
    sample_b64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    payload = {
        "message": "Trích xuất câu hỏi trắc nghiệm từ ảnh đồ thị đính kèm",
        "current_latex": r"\begin{document}" + "\n" + r"\end{document}",
        "images": [sample_b64]
    }

    # Force AI provider to None to test local / offline deterministic fallback
    with patch("backend.routers.composer.default_ai_provider_service", None):
        res = client.post("/api/v1/composer/chat", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert "reply" in data
        assert "phân tích hình ảnh đính kèm" in data["reply"].lower()
        assert r"\begin{ex}[Phân tích từ ảnh đính kèm]" in data["reply"]
        assert "tikzpicture" in data["reply"]
        assert r"\choice" in data["reply"]
        assert r"\begin{loigiai}" in data["reply"]

        # Verify suggested_latex
        assert data["suggested_latex"] is not None
        assert r"\begin{ex}[Phân tích từ ảnh đính kèm]" in data["suggested_latex"]

        # Verify diff suggestion
        assert data["diff"] is not None
        assert data["diff"]["action"] == "replace"
        assert r"\begin{ex}[Phân tích từ ảnh đính kèm]" in data["diff"]["new_text"]
        assert "ảnh đính kèm" in data["diff"]["description"].lower()


def test_composer_chat_api_multimodal_mocked_ai_single_image():
    """TC-COMP-32: Verify POST /api/v1/composer/chat with 1 image when calling AI Provider.
    Checks that user message content is formatted as multi-modal content blocks:
    [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": img_url}}].
    """
    mock_service = MagicMock()
    mock_service.api_key = "mock-multimodal-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o"
    mock_service.base_url = "https://api.openai.com/v1"

    ai_generated_latex = r"""\begin{ex}
Cho hàm số $y = x^2 - 2x$ có đồ thị parabol như trong ảnh. Đỉnh của parabol là:
\choice
{\True $(1; -1)$}
{$(0; 0)$}
{$(2; 0)$}
{$(-1; 3)$}
\begin{loigiai}
Toạ độ đỉnh $I(-\frac{b}{2a}; -\frac{\Delta}{4a}) = (1; -1)$.
\end{loigiai}
\end{ex}"""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": f"Dưới đây là câu hỏi chuẩn hoá từ ảnh đồ thị:\n\n```latex\n{ai_generated_latex}\n```"
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    test_image_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    payload = {
        "message": "Trích xuất câu hỏi từ ảnh",
        "current_latex": r"\begin{document}\end{document}",
        "images": [test_image_url]
    }

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post("/api/v1/composer/chat", json=payload)
            assert res.status_code == 200
            data = res.json()

            # Verify client.post was called with multi-modal content payload
            assert mock_client.post.called
            call_args, call_kwargs = mock_client.post.call_args
            sent_json = call_kwargs["json"]
            assert sent_json["model"] == "gpt-4o"
            assert "messages" in sent_json

            # Find user message in sent payload
            user_msg = next((m for m in sent_json["messages"] if m["role"] == "user"), None)
            assert user_msg is not None
            assert isinstance(user_msg["content"], list), "User content must be a multimodal list of blocks"
            assert len(user_msg["content"]) == 2

            # Block 0: Text prompt
            assert user_msg["content"][0]["type"] == "text"
            assert "Yêu cầu của giáo viên: Trích xuất câu hỏi từ ảnh" in user_msg["content"][0]["text"]

            # Block 1: Image URL block
            assert user_msg["content"][1]["type"] == "image_url"
            assert user_msg["content"][1]["image_url"]["url"] == test_image_url

            # Verify response parsing
            assert data["suggested_latex"] is not None
            assert "y = x^2 - 2x" in data["suggested_latex"]


def test_composer_chat_api_multimodal_mocked_ai_multiple_images_and_history():
    """TC-COMP-33: Verify POST /api/v1/composer/chat handles multiple images and preserves conversation history.
    Checks multi-modal content array with 1 text block + N image_url blocks.
    """
    mock_service = MagicMock()
    mock_service.api_key = "mock-gemini-key"
    mock_service.provider = "gemini"
    mock_service.model = "gemini-2.0-flash"
    mock_service.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Đã tổng hợp 2 ảnh thành câu hỏi so sánh 2 đồ thị."
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    img1 = "data:image/png;base64,firstImageData"
    img2 = "data:image/jpeg;base64,secondImageData"
    payload = {
        "message": "So sánh 2 đồ thị hàm số từ 2 ảnh này",
        "current_latex": r"\begin{document}\end{document}",
        "history": [
            {"role": "user", "content": "Ảnh 1 là hàm gì?"},
            {"role": "assistant", "content": "Ảnh 1 là hàm bậc ba."}
        ],
        "images": [img1, img2]
    }

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post("/api/v1/composer/chat", json=payload)
            assert res.status_code == 200

            call_args, call_kwargs = mock_client.post.call_args
            sent_messages = call_kwargs["json"]["messages"]

            # Check history preservation
            roles = [m["role"] for m in sent_messages]
            assert "system" in roles
            assert roles[-3] == "user" and sent_messages[-3]["content"] == "Ảnh 1 là hàm gì?"
            assert roles[-2] == "assistant" and sent_messages[-2]["content"] == "Ảnh 1 là hàm bậc ba."

            # Check active user message has 1 text block + 2 image_url blocks
            last_msg = sent_messages[-1]
            assert last_msg["role"] == "user"
            content = last_msg["content"]
            assert isinstance(content, list)
            assert len(content) == 3
            assert content[0]["type"] == "text"
            assert content[1]["type"] == "image_url" and content[1]["image_url"]["url"] == img1
            assert content[2]["type"] == "image_url" and content[2]["image_url"]["url"] == img2


def test_composer_chat_api_multimodal_empty_images_backward_compatibility():
    """TC-COMP-34: Verify POST /api/v1/composer/chat when images list is empty or omitted.
    Ensures message content remains a plain string for backward compatibility with text-only prompts.
    """
    mock_service = MagicMock()
    mock_service.api_key = "mock-openai-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Chào bạn, tôi sẵn sàng hỗ trợ."}}]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    # Explicit images=[]
    payload = {
        "message": "Viết câu hỏi lượng giác đơn giản",
        "current_latex": r"\begin{document}\end{document}",
        "images": []
    }

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post("/api/v1/composer/chat", json=payload)
            assert res.status_code == 200

            call_args, call_kwargs = mock_client.post.call_args
            sent_messages = call_kwargs["json"]["messages"]
            last_msg = sent_messages[-1]
            assert last_msg["role"] == "user"
            assert isinstance(last_msg["content"], str), "When no images are provided, content must be a plain string"


def test_composer_chat_api_multimodal_mocked_ai_diff_extraction():
    """TC-COMP-35: Verify POST /api/v1/composer/chat extracts diffs accurately when AI responds
    to image replacement requests with a diff block.
    """
    mock_service = MagicMock()
    mock_service.api_key = "mock-key"
    mock_service.provider = "openai"
    mock_service.model = "gpt-4o-mini"
    mock_service.base_url = "https://api.openai.com/v1"

    current_latex = r"""\begin{ex}
Câu hỏi cũ cần thay thế.
\end{ex}"""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Tôi đã thay thế câu hỏi cũ bằng câu hỏi trích xuất từ ảnh:\n\n"
                        "```diff\n"
                        "- \\begin{ex}\n"
                        "- Câu hỏi cũ cần thay thế.\n"
                        "- \\end{ex}\n"
                        "+ \\begin{ex}[Trích xuất từ ảnh]\n"
                        "+ Câu hỏi mới từ ảnh đồ thị.\n"
                        "+ \\end{ex}\n"
                        "```"
                    )
                }
            }
        ]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    payload = {
        "message": "Thay thế câu hỏi này bằng câu hỏi trong ảnh",
        "current_latex": current_latex,
        "images": ["data:image/png;base64,sample"]
    }

    with patch("backend.routers.composer.default_ai_provider_service", mock_service):
        with patch("backend.routers.composer.httpx.Client", return_value=mock_client):
            res = client.post("/api/v1/composer/chat", json=payload)
            assert res.status_code == 200
            data = res.json()

            assert data["diff"] is not None
            assert data["diff"]["action"] == "replace"
            assert "Câu hỏi cũ cần thay thế" in data["diff"]["old_text"]
            assert "Trích xuất từ ảnh" in data["diff"]["new_text"]
            assert len(data["diffs"]) >= 1


def test_composer_multimodal_frontend_dom_elements():
    """TC-COMP-36: Verify existence and attributes of all image attachment DOM elements in frontend/index.html.
    Checks image thumbnail tray, file input, attach button, and image lightbox modal.
    """
    html_path = Path("frontend/index.html")
    assert html_path.exists(), "frontend/index.html must exist"
    content = html_path.read_text(encoding="utf-8")

    # 1. Attached images thumbnail container
    assert 'id="composer-attached-images-container"' in content
    assert 'class="hidden flex items-center space-x-2 pb-2 overflow-x-auto select-none"' in content

    # 2. Hidden file input for image upload
    assert 'id="composer-chat-image-input"' in content
    assert 'type="file"' in content
    assert 'accept="image/*"' in content
    assert 'multiple' in content
    assert 'onchange="app.composer.handleImageFileSelect(event)"' in content

    # 3. Attach button triggering file input click
    assert "document.getElementById('composer-chat-image-input').click()" in content
    assert 'data-lucide="image"' in content

    # 4. Lightbox Modal for enlarged view
    assert 'id="composer-image-lightbox"' in content
    assert 'id="composer-lightbox-img"' in content
    assert "app.composer.closeLightbox(event)" in content
    assert "app.composer.closeLightbox()" in content


def test_composer_multimodal_frontend_app_js_methods_and_flow():
    """TC-COMP-37: Verify all JavaScript multi-modal image methods and event handling in frontend/static/app.js.
    Checks state initialization, file select, rendering, lightbox, submit payload, and key listeners.
    """
    js_path = Path("frontend/static/app.js")
    assert js_path.exists(), "frontend/static/app.js must exist"
    content = js_path.read_text(encoding="utf-8")

    # 1. State initialization
    assert "attachedImages: []" in content

    # 2. Core handler methods
    assert "handleImageFileSelect(e)" in content
    assert "addAttachedImage(dataUrl, name)" in content
    assert "removeAttachedImage(id)" in content
    assert "renderAttachedImages()" in content
    assert "openLightbox(src)" in content
    assert "closeLightbox(e)" in content

    # 3. Payload construction in submitChat()
    assert "attachedImagesCopy.map(img => img.dataUrl)" in content
    assert "this.attachedImages = [];" in content
    assert "images: imagePayloads" in content or "images: imagePayloads.length ? imagePayloads : undefined" in content

    # 4. Chat history rendering with image thumbnail grid
    assert "composer-chat-image-grid" in content
    assert "composer-chat-image-thumb" in content
    assert "app.composer.openLightbox" in content

    # 5. Keyboard shortcut listener for Esc key closing lightbox
    assert "e.key === 'Escape'" in content
    assert "this.closeLightbox();" in content


def test_composer_multimodal_css_styling():
    """TC-COMP-38: Verify CSS classes and styles for multi-modal image chips and lightboxes in frontend/static/style.css."""
    css_path = Path("frontend/static/style.css")
    assert css_path.exists(), "frontend/static/style.css must exist"
    content = css_path.read_text(encoding="utf-8")

    # Scrollbar customization
    assert "#composer-attached-images-container::-webkit-scrollbar" in content

    # Image chip thumbnail
    assert ".composer-image-chip" in content
    assert ".composer-image-chip img" in content
    assert ".composer-image-chip-remove" in content
    assert ".composer-image-chip:hover .composer-image-chip-remove" in content

    # Chat bubble image grid and thumbnail
    assert '.composer-chat-image-grid' in content
    assert '.composer-chat-image-thumb' in content


def test_composer_compute_compilation_timeout_adaptive_scaling():
    """TC-COMP-34: Verify compute_compilation_timeout dynamic adaptive scaling behavior.

    Validates:
    1. Empty latex source -> returns minimum floor of 60 seconds.
    2. Short text without TikZ diagrams -> returns minimum floor of 60 seconds.
    3. Medium document with some TikZ diagrams -> scales appropriately above 60s.
    4. Large complex exam with many TikZ / tkz-tab blocks -> scales up towards upper ceiling of 240 seconds.
    5. Extremely massive document -> strictly clamped to upper limit of 240 seconds.
    """
    from backend.services.composer_service import compute_compilation_timeout

    # 1. Empty or whitespace source
    assert compute_compilation_timeout("") == 60
    assert compute_compilation_timeout("   \n\t") == 60

    # 2. Short document without TikZ
    short_plain = "Short plain text without any TikZ block or diagram."
    assert compute_compilation_timeout(short_plain) == 60

    # 3. Intermediate scaling
    # 3 TikZ blocks, 2500 chars -> 45 + 30 + 10 = 85s
    tikz_block = r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}" + "\n"
    mid_doc = (tikz_block * 3) + ("a" * 2500)
    assert compute_compilation_timeout(mid_doc) == 85

    # 4. Large document with 10 TikZ and tkz-tab blocks
    tkz_tab_block = r"\begin{tikzpicture}\tkzTabInit{$x$/1}{$1$}\end{tikzpicture}" + "\n"
    large_doc = (tikz_block * 5) + (tkz_tab_block * 5) + ("x" * 15000)
    t_large = compute_compilation_timeout(large_doc)
    assert 180 <= t_large <= 240

    # 5. Massive document hitting the 240s upper clamp ceiling
    massive_doc = (tikz_block * 25) + ("y" * 50000)
    assert compute_compilation_timeout(massive_doc) == 240


def test_composer_diagnose_compile_error_timeout_and_samples_optimization():
    """TC-COMP-35: Verify diagnose_compile_error diagnoses 'Compilation timed out'
    and proposes targeted diffs reducing TikZ samples=100 down to samples=50.
    """
    from backend.routers.composer import diagnose_compile_error

    # Scenario A: Timeout error with TikZ plot using samples=100
    err_timeout = "Error: Compilation timed out after 60 seconds while building document"
    latex_code = (
        r"\documentclass{article}" + "\n"
        r"\usepackage{tikz}" + "\n"
        r"\begin{document}" + "\n"
        r"\begin{tikzpicture}" + "\n"
        r"  \draw[domain=0:5, samples=100] plot(\x, {sin(\x)});" + "\n"
        r"\end{tikzpicture}" + "\n"
        r"\end{document}"
    )

    resp = diagnose_compile_error(err_timeout, latex_code)
    assert resp is not None
    assert "Compilation Timed Out" in resp.reply
    assert "Dynamic Adaptive Compilation Timeout" in resp.reply
    assert "samples=50" in resp.reply
    assert resp.diff is not None
    assert resp.diff.action == "replace"
    assert "samples=100" in resp.diff.old_text
    assert "samples=50" in resp.diff.new_text
    assert len(resp.diffs) == 1

    # Scenario B: Multiple plots with samples >= 80 (e.g. 100, 120)
    multi_latex = (
        r"\begin{tikzpicture}" + "\n"
        r"  \draw[domain=0:5, samples=100] plot(\x, {sin(\x)});" + "\n"
        r"  \draw[domain=-2:2, samples=120] plot(\x, {cos(\x)});" + "\n"
        r"\end{tikzpicture}"
    )
    resp_multi = diagnose_compile_error("timed out", multi_latex)
    assert resp_multi is not None
    assert resp_multi.diff is not None
    assert len(resp_multi.diffs) == 2
    assert "samples=50" in resp_multi.diffs[0].new_text
    assert "samples=50" in resp_multi.diffs[1].new_text

    # Scenario C: Timeout error but no samples >= 80 found
    no_samples_latex = (
        r"\begin{tikzpicture}" + "\n"
        r"  \draw[domain=0:5] plot(\x, {sin(\x)});" + "\n"
        r"\end{tikzpicture}"
    )
    resp_no_samp = diagnose_compile_error("biên dịch quá thời gian quy định", no_samples_latex)
    assert resp_no_samp is not None
    assert "Compilation Timed Out" in resp_no_samp.reply
    assert resp_no_samp.diff is None
    assert resp_no_samp.diffs == []


def test_composer_compile_large_viet_duc_exam_pdf_success(tmp_path):
    """TC-COMP-36 / Verification: Verify large exam (THPT Việt Đức mid-term 12)
    with 12 MC, 4 TF, 6 ShortAns and multiple TikZ plots compiles cleanly
    with dynamic timeout scaling to a valid vector PDF.
    """
    import json
    import urllib.request
    from unittest.mock import patch, MagicMock
    from backend.services.composer_service import (
        compute_compilation_timeout,
        compile_with_remote_tectonic_api,
    )

    # 1. Load Viet Duc exam content from local attachment or test fixture
    attachment_path = Path(r"C:\Users\ngnsusinn\AppData\Local\hermes\attachments\pasted_content_2026-10-25_11-09-13-679_36e9d2.txt")
    fixture_path = Path(__file__).resolve().parent / "fixtures" / "viet_duc_exam.tex"

    if attachment_path.exists():
        content = attachment_path.read_text(encoding="utf-8")
    elif fixture_path.exists():
        content = fixture_path.read_text(encoding="utf-8")
    else:
        assert False, "Neither attachment nor fixture viet_duc_exam.tex found"

    assert len(content) > 10000, "Viet Duc exam must be substantial (>10k chars)"
    assert "TRƯỜNG THPT VIỆT ĐỨC" in content
    assert "Mã đề thi: 0108" in content

    # 2. Check dynamic adaptive timeout scaling
    calc_timeout = compute_compilation_timeout(content)
    # 23k+ chars and 10+ TikZ diagrams must scale to upper limit (240s)
    assert calc_timeout >= 200, f"Expected calc_timeout >= 200s, got {calc_timeout}s"

    # 3. Verify Remote Tectonic API payload and execution contract
    out_pdf = tmp_path / "viet_duc_output.pdf"

    # Check if real armbian:8090 service is responsive
    armbian_alive = False
    try:
        with urllib.request.urlopen("http://armbian:8090/health", timeout=0.8) as hresp:
            if hresp.status == 200:
                armbian_alive = True
    except Exception:
        armbian_alive = False

    if armbian_alive:
        # Live compilation test against armbian:8090
        ok, err, ms = compile_with_remote_tectonic_api(content, out_pdf, title="Đề THPT Việt Đức 2026")
        assert ok is True, f"Live compilation failed: {err}"
        assert out_pdf.exists(), "Output PDF must exist"
        pdf_bytes = out_pdf.read_bytes()
        assert pdf_bytes.startswith(b"%PDF"), "Must be a valid PDF vector header"
        assert len(pdf_bytes) > 500, f"PDF file size too small: {len(pdf_bytes)} bytes"
        assert ms > 0
        # Clean up out_pdf before mock test verification
        out_pdf.unlink(missing_ok=True)

    # CI Runner isolated mock test: verify payload carries timeout_s: calc_timeout and returns valid PDF
    mock_response = MagicMock()
    mock_response.status = 200
    fake_pdf = b"%PDF-1.5 \n%Fake Valid PDF Content for CI runner testing\n" + b"X" * 600 + b"\n%%EOF"
    mock_response.read.return_value = fake_pdf
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        ok, err, ms = compile_with_remote_tectonic_api(
            content,
            out_pdf,
            title="Đề THPT Việt Đức 2026",
            api_url="http://armbian:8090/compile",
        )
        assert ok is True, f"Mock compilation failed: {err}"
        assert out_pdf.exists(), "Output PDF must exist after mock compilation"
        written_bytes = out_pdf.read_bytes()
        assert written_bytes.startswith(b"%PDF")
        assert len(written_bytes) > 500
        assert written_bytes == fake_pdf

        # Verify the request payload sent to the remote API
        assert mock_urlopen.call_count >= 1
        sent_req = mock_urlopen.call_args[0][0]
        assert isinstance(sent_req, urllib.request.Request)
        assert isinstance(sent_req.data, bytes)
        payload_data = json.loads(sent_req.data.decode("utf-8"))
        assert "timeout_s" in payload_data
        assert payload_data["timeout_s"] == calc_timeout
        assert payload_data["timeout_s"] >= 200
        # Also verify socket buffer timeout passed to urlopen
        socket_timeout = mock_urlopen.call_args[1].get("timeout")
        assert socket_timeout == calc_timeout + 15
        assert socket_timeout >= 215


def test_composer_system_prompt_centered_diagrams_invariant():
    """Verify system_prompt in backend/routers/composer.py strictly enforces
    Centered Layout Invariant, requires \\begin{center}\\begin{tikzpicture},
    prohibits default \\immini, recommends samples=50/60, enforces \\choiceTF[1]
    without label prefixes in content, and standardizes MoET 2025 2-column header.
    """
    import inspect
    from backend.routers.composer import composer_chat_endpoint

    # 1. Inspect source of composer_chat_endpoint
    source = inspect.getsource(composer_chat_endpoint)
    assert "system_prompt" in source, "system_prompt must be defined in composer_chat_endpoint"

    # 2. Intercept actual system_prompt payload delivered via httpx.Client.post
    mock_service = MagicMock()
    mock_service.api_key = "mock-secret-key"
    mock_service.provider = "gemini"
    mock_service.model = "gemini-2.5-flash"
    mock_service.base_url = "https://generativelanguage.googleapis.com/v1beta/openai"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Sample LLM reply"}}]
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = mock_resp

    captured_system_prompt = None
    with patch("backend.routers.composer.default_ai_provider_service", mock_service), \
         patch("backend.routers.composer.httpx.Client", return_value=mock_client):
        res = client.post(
            "/api/v1/composer/chat",
            json={
                "message": "Tạo một câu hỏi trắc nghiệm hàm số bậc 3 có đồ thị TikZ",
                "current_latex": r"\begin{document}\end{document}",
                "history": [],
            },
        )
        assert res.status_code == 200
        assert mock_client.post.called, "httpx.Client.post must be called when provider is active"
        json_payload = mock_client.post.call_args[1].get("json") or {}
        messages = json_payload.get("messages", [])
        assert len(messages) >= 1
        assert messages[0]["role"] == "system"
        captured_system_prompt = messages[0]["content"]

    assert captured_system_prompt is not None, "Failed to capture system_prompt from chat endpoint"

    # 3. Assert Centered Layout Invariant rules
    assert "CENTERED LAYOUT INVARIANT" in captured_system_prompt
    assert r"\begin{center}\begin{tikzpicture}" in captured_system_prompt
    assert r"\end{tikzpicture}\end{center}" in captured_system_prompt
    assert (
        "TUYỆT ĐỐI KHÔNG nằm lệch 1 bên hay dùng \\immini" in captured_system_prompt
        or "TUYỆT ĐỐI KHÔNG nằm lệch 1 bên hay dùng \\\\immini" in captured_system_prompt
    )
    assert "samples=50" in captured_system_prompt

    # 4. Assert True/False \\choiceTF[1] standardization
    assert r"\choiceTF[1]" in captured_system_prompt
    assert "TUYỆT ĐỐI KHÔNG gõ tiền tố nhãn a), b), c), d) vào trong nội dung khẳng định" in captured_system_prompt

    # 5. Assert MoET 2025 2-column header standardization
    assert "0.38" in captured_system_prompt and "0.58" in captured_system_prompt
    assert r"\dotfill" in captured_system_prompt
    assert "Mã đề:" in captured_system_prompt
    assert "0.5pt" in captured_system_prompt


def test_ai_provider_system_prompt_centered_diagrams():
    """Verify SYSTEM_PROMPT and SYSTEM_PROMPT_PASS2_FIGURE in ai_provider_service.py
    enforce Centered Layout Invariant and ban label prefixes in sub_statements.
    """
    from backend.services.ai_provider_service import SYSTEM_PROMPT, SYSTEM_PROMPT_PASS2_FIGURE

    # 1. Check SYSTEM_PROMPT
    assert "CENTERED LAYOUT INVARIANT" in SYSTEM_PROMPT
    assert r"\begin{center}\begin{tikzpicture}" in SYSTEM_PROMPT
    assert r"\end{tikzpicture}\end{center}" in SYSTEM_PROMPT
    assert "TUYỆT ĐỐI KHÔNG dùng \\immini" in SYSTEM_PROMPT or "TUYỆT ĐỐI KHÔNG dùng \\\\immini" in SYSTEM_PROMPT
    assert "samples=50" in SYSTEM_PROMPT
    assert "TUYỆT ĐỐI CẤM gõ tiền tố nhãn a), b), c), d)" in SYSTEM_PROMPT
    assert "sub_statements" in SYSTEM_PROMPT

    # 2. Check SYSTEM_PROMPT_PASS2_FIGURE
    assert r"\begin{center}\begin{tikzpicture}" in SYSTEM_PROMPT_PASS2_FIGURE
    assert r"\end{tikzpicture}\end{center}" in SYSTEM_PROMPT_PASS2_FIGURE
    assert "samples=50" in SYSTEM_PROMPT_PASS2_FIGURE
    assert "tkz-tab" in SYSTEM_PROMPT_PASS2_FIGURE
    assert r"\begin{center}\begin{tikzpicture}...\end{tikzpicture}\end{center}" in SYSTEM_PROMPT_PASS2_FIGURE


def test_composer_templates_centered_diagrams_no_immini():
    """Verify TEMPLATES in composer_service.py and EX_TEST_TEMPLATES in app.js
    strictly use centered TikZ diagrams, contain NO \\immini in question templates,
    and successfully compile to PDF.
    """
    import re
    from backend.services.composer_service import TEMPLATES

    # 1. Test backend TEMPLATES['ex_test_standard_exam']
    assert "ex_test_standard_exam" in TEMPLATES
    tmpl_quocgia = TEMPLATES["ex_test_standard_exam"]["latex"]
    assert r"\immini" not in tmpl_quocgia, "ex_test_standard_exam must not contain \\immini"
    assert r"\begin{center}" in tmpl_quocgia
    assert r"\begin{tikzpicture}" in tmpl_quocgia
    assert "samples=50" in tmpl_quocgia
    assert r"\choiceTF[1]" in tmpl_quocgia
    assert "0.38" in tmpl_quocgia and "0.58" in tmpl_quocgia
    assert "rule" in tmpl_quocgia and "0.5pt" in tmpl_quocgia

    # Compile ex_test_standard_exam to PDF
    res_qg = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": tmpl_quocgia, "title": "Đề thi Chuẩn Quốc Gia 2025"}
    )
    assert res_qg.status_code == 200
    data_qg = res_qg.json()
    assert data_qg["success"] is True
    assert data_qg["pdf_url"].startswith("/api/v1/composer/pdf/")
    assert data_qg["total_pages"] >= 1

    # 2. Test backend TEMPLATES['circular_32_full_exam']
    assert "circular_32_full_exam" in TEMPLATES
    tmpl_tt32 = TEMPLATES["circular_32_full_exam"]["latex"]
    assert r"\immini" not in tmpl_tt32, "circular_32_full_exam must not contain \\immini"
    assert r"\begin{center}" in tmpl_tt32
    assert r"\begin{tikzpicture}" in tmpl_tt32
    assert "samples=50" in tmpl_tt32
    assert r"\choiceTF[1]" in tmpl_tt32

    # Compile circular_32_full_exam to PDF
    res_tt32 = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": tmpl_tt32, "title": "Đề thi Chuẩn Thông tư 32"}
    )
    assert res_tt32.status_code == 200
    data_tt32 = res_tt32.json()
    assert data_tt32["success"] is True
    assert data_tt32["pdf_url"].startswith("/api/v1/composer/pdf/")
    assert data_tt32["total_pages"] >= 1

    # 3. Test frontend app.js EX_TEST_TEMPLATES and fallback currentLatex
    app_js_path = Path(__file__).resolve().parent.parent / "frontend" / "static" / "app.js"
    assert app_js_path.exists()
    app_js_content = app_js_path.read_text(encoding="utf-8")

    # dethi_quocgia_full must NOT contain \immini and MUST use \choiceTF[1]
    m_extest = re.search(r'EX_TEST_TEMPLATES\s*:\s*\{([\s\S]*?)\n\s*\},', app_js_content)
    assert m_extest is not None
    extest_body = m_extest.group(1)

    m_dethi_full = re.search(r"'dethi_quocgia_full'\s*:\s*`([\s\S]*?)`", extest_body)
    assert m_dethi_full is not None
    dethi_full_code = m_dethi_full.group(1)
    clean_dethi_full = dethi_full_code.replace('\\\\', '\\')
    assert r"\immini" not in clean_dethi_full, "dethi_quocgia_full must not contain \\immini"
    assert r"\choiceTF[1]" in clean_dethi_full
    assert "0.38" in clean_dethi_full and "0.58" in clean_dethi_full
    assert "rule" in clean_dethi_full and "0.5pt" in clean_dethi_full

    # Compile dethi_quocgia_full to PDF
    res_fe = client.post(
        "/api/v1/composer/compile",
        json={"latex_code": clean_dethi_full, "title": "Đề thi Quốc Gia 2025 Frontend"}
    )
    assert res_fe.status_code == 200
    data_fe = res_fe.json()
    assert data_fe["success"] is True
    assert data_fe["pdf_url"].startswith("/api/v1/composer/pdf/")

    # extest_immini snippet must use centered diagram and samples=50
    m_immini_snip = re.search(r"'extest_immini'\s*:\s*`([\s\S]*?)`", app_js_content)
    assert m_immini_snip is not None
    immini_body = m_immini_snip.group(1)
    assert r"\immini{" not in immini_body, "extest_immini snippet must not contain \\immini{"
    assert r"\begin{center}" in immini_body
    assert "samples=50" in immini_body

    # extest_choiceTF snippet must use \choiceTF[1] without label prefixes a), b)
    m_choicetf_snip = re.search(r"'extest_choiceTF'\s*:\s*`([\s\S]*?)`", app_js_content)
    assert m_choicetf_snip is not None
    choicetf_body = m_choicetf_snip.group(1)
    assert r"\choiceTF[1]" in choicetf_body
    assert "a)" not in choicetf_body
    assert "b)" not in choicetf_body

    # Fallback this.currentLatex must NOT contain \immini and MUST have centered tikz
    assert "Cho hàm số bậc ba $y = f(x)$ có đồ thị như hình bên." in app_js_content
    m_fallback = re.search(r"this\.currentLatex\s*=\s*`[\\/]*noindent[\s\S]*?\\end\{ex\}\s*`", app_js_content)
    assert m_fallback is not None, "Fallback this.currentLatex must be updated to 2-column header"
    fallback_code = m_fallback.group(0)
    assert r"\immini" not in fallback_code, "Fallback this.currentLatex must not contain \\immini"
    assert "begin{center}" in fallback_code
    assert "samples=50" in fallback_code



