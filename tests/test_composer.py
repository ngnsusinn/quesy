"""Test suite for Quesy Exam Composer (Open-Prism Clone).
Tests template retrieval, LaTeX-to-PDF live compilation, AI writing copilot,
and Question Bank extraction.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.routers.composer import DiffSuggestion, extract_diff_from_text, find_in_latex

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
