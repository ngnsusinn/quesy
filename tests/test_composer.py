"""Test suite for Quesy Exam Composer (Open-Prism Clone).
Tests template retrieval, LaTeX-to-PDF live compilation, AI writing copilot,
and Question Bank extraction.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.composer import DiffSuggestion, extract_diff_from_text

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
        assert "Đúng/Sai" in data["suggested_latex"]


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
