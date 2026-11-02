"""
Comprehensive Automated Test Suite for Composer AI Copilot:
1. Flexible Search & Replace (with and without quotes, duration, school, variable, choices).
2. Four Pedagogical & Regulations Q&A Scenarios:
   - Scenario A: MoET Decision 764 & 2025 Exam Structure & Circular 32.
   - Scenario B: Syntax of ex_test.sty (\\choiceTF[1], \\choice, \\shortans) & Centered TikZ/tkz-tab.
   - Scenario C: Exam progress analysis (analyze_exam_progress) & stats report.
   - Scenario D: Pedagogical question solution guide (explain_question_pedagogy).
3. Anti-regression negative assertions: Q&A queries never return irrelevant exam templates or unwanted diffs.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.routers.composer import router as composer_router

app = FastAPI()
app.include_router(composer_router)
from backend.routers.composer import (
    parse_flexible_replace_command,
    is_qa_request,
    analyze_exam_progress,
    explain_question_pedagogy,
    generate_exam_statistics_report,
    generate_question_solution_guide,
    generate_syntax_qa_response,
    generate_regulations_qa_response,
    extract_all_diffs_from_text,
    ChatRequest,
)

client = TestClient(app)


# ==============================================================================
# SECTION 1: FLEXIBLE SEARCH & REPLACE (WITH & WITHOUT QUOTES)
# ==============================================================================

class TestFlexibleReplaceParser:
    """Tests for parse_flexible_replace_command parsing Vietnamese natural language commands."""

    def test_quoted_commands(self):
        # Double quotes
        res = parse_flexible_replace_command('tìm và thay thế "f(x)" bằng "g(x)"')
        assert res == ("f(x)", "g(x)")

        # Single quotes
        res = parse_flexible_replace_command("thay thế 'x^2' thành 'x^3'")
        assert res == ("x^2", "x^3")

        # Curly quotes
        res = parse_flexible_replace_command("đổi “sin(x)” sang “cos(x)”")
        assert res == ("sin(x)", "cos(x)")

        # Backticks
        res = parse_flexible_replace_command("sửa `\\alpha` với `\\beta`")
        assert res == ("\\alpha", "\\beta")

    def test_unquoted_commands_natural_vietnamese(self):
        # Mẫu 1: "tìm và thay thế X thành/bằng/sang/bởi Y"
        res = parse_flexible_replace_command("tìm và thay thế biến x thành biến t")
        assert res == ("biến x", "biến t")

        res = parse_flexible_replace_command("tìm và thay thế Hà Nội bằng TP Hồ Chí Minh")
        assert res == ("Hà Nội", "TP Hồ Chí Minh")

        # Mẫu 2: "thay thế X bằng/thành/sang/bởi Y"
        res = parse_flexible_replace_command("thay thế thời gian làm bài bằng 60 phút")
        assert res == ("thời gian làm bài", "60 phút")

        # Mẫu 3: "thay X bằng/thành/sang/bởi Y"
        res = parse_flexible_replace_command("thay tên trường thành THPT Chuyên Quốc Học")
        assert res == ("tên trường", "THPT Chuyên Quốc Học")

        res = parse_flexible_replace_command("hãy thay 90 phút bằng 45 phút!")
        assert res == ("90 phút", "45 phút")

        # Mẫu 4: "đổi X sang/thành/bằng Y"
        res = parse_flexible_replace_command("đổi m = 1 sang m = 2")
        assert res == ("m = 1", "m = 2")

        # Mẫu 5: "sửa X thành/sang/bằng Y"
        res = parse_flexible_replace_command("sửa điểm cực đại thành điểm cực tiểu.")
        assert res == ("điểm cực đại", "điểm cực tiểu")

        # Mẫu 6: "chuyển X sang/thành Y"
        res = parse_flexible_replace_command("chuyển x > 0 sang x >= 0")
        assert res == ("x > 0", "x >= 0")

    def test_negative_cases_for_parser(self):
        assert parse_flexible_replace_command("") is None
        assert parse_flexible_replace_command("   ") is None
        assert parse_flexible_replace_command("hôm nay thời tiết rất đẹp") is None
        assert parse_flexible_replace_command("thay") is None
        assert parse_flexible_replace_command("sửa đề thi") is None
        assert parse_flexible_replace_command("hướng dẫn giải câu 1") is None


class TestTargetedDiffExtraction:
    """Tests for extract_all_diffs_from_text handling targeted domain edits."""

    def test_duration_change(self):
        latex = r"""\noindent
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}\\
  \textbf{MÔN: TOÁN}\\
  \textit{Thời gian làm bài: 90 phút (không kể thời gian phát đề)}
\end{minipage}"""
        diffs = extract_all_diffs_from_text("", latex, user_message="đổi thời gian làm bài thành 45 phút")
        assert len(diffs) == 1
        d = diffs[0]
        assert "90 phút" in d.old_text
        assert "45 phút" in d.new_text
        assert "45 phút" in d.description

    def test_school_name_change(self):
        latex = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO HÀ NỘI}\\
  \textbf{TRƯỜNG THPT CHU VĂN AN}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}"""
        diffs = extract_all_diffs_from_text("", latex, user_message="thay tên trường thành THPT Lương Thế Vinh")
        assert len(diffs) == 1
        d = diffs[0]
        assert "CHU VĂN AN" in d.old_text
        assert "Lương Thế Vinh" in d.new_text or "LƯƠNG THẾ VINH" in d.new_text

    def test_department_name_change(self):
        latex = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO HÀ NỘI}\\
  \textbf{TRƯỜNG THPT ...}\\
  \textbf{ĐỀ CHÍNH THỨC}
\end{minipage}"""
        diffs = extract_all_diffs_from_text("", latex, user_message="đổi tên sở thành TP HỒ CHÍ MINH")
        assert len(diffs) == 1
        d = diffs[0]
        assert "HÀ NỘI" in d.old_text
        assert "TP HỒ CHÍ MINH" in d.new_text

    def test_variable_replacement(self):
        latex = r"""\begin{ex}
Tính tích phân $I = \int_0^1 (2x + 1) \, dx$.
\choice
{\True $2$}
{$1$}
{$3$}
{$0$}
\end{ex}"""
        diffs = extract_all_diffs_from_text("", latex, user_message="thay biến x thành biến t")
        assert len(diffs) == 1
        d = diffs[0]
        assert "x" in d.old_text
        assert "t" in d.new_text

    def test_choice_option_switch_targeted_question(self):
        latex = r"""\begin{ex}
Câu 1: Hàm số $y = f(x)$ đồng biến trên khoảng nào?
\choice
{\True $(-\infty; 1)$}
{$(1; 2)$}
{$(2; 3)$}
{$(3; +\infty)$}
\end{ex}
\begin{ex}
Câu 2: Số điểm cực trị của hàm số là:
\choice
{0}
{\True 1}
{2}
{3}
\end{ex}"""
        # Switch question 1 correct choice to D
        diffs = extract_all_diffs_from_text("", latex, user_message="đổi đáp án câu 1 sang D")
        assert len(diffs) == 1
        d = diffs[0]
        assert r"\True $(-\infty; 1)$" in d.old_text
        assert r"\True $(3; +\infty)$" in d.new_text
        assert "sang D" in d.description


# ==============================================================================
# SECTION 2: FOUR Q&A COPILOT SCENARIOS (REGULATIONS, SYNTAX, STATS, PEDAGOGY)
# ==============================================================================

class TestQACopilotScenarios:
    """Tests for the 4 pedagogical Q&A scenarios in Composer Copilot."""

    # --------------------------------------------------------------------------
    # Scenario A: MoET Regulations (QĐ 764 & Structure 2025 & Circular 32)
    # --------------------------------------------------------------------------
    @pytest.mark.parametrize("prompt", [
        "Quy chế QĐ 764 quy định cách tính điểm như thế nào?",
        "Cấu trúc đề thi 2025 gồm bao nhiêu câu?",
        "Thời gian làm bài thi tốt nghiệp môn Toán là bao nhiêu phút?",
        "Quy định thang điểm bậc thang câu hỏi đúng sai 764/QĐ-BGDĐT",
        "Thông tư 32 quy định ma trận năng lực ra sao?",
    ])
    def test_scenario_a_regulations_qa(self, prompt):
        assert is_qa_request(prompt) is True

        res = client.post(
            "/api/v1/composer/chat",
            json={"message": prompt, "current_latex": "", "history": []}
        )
        assert res.status_code == 200
        data = res.json()
        reply = data["reply"]

        # Assert authoritative legal & pedagogical content
        assert "764/QĐ-BGDĐT" in reply or "Quyết định" in reply
        assert "0,10 điểm" in reply or "0,1" in reply
        assert "0,25 điểm" in reply or "0,25" in reply
        assert "0,50 điểm" in reply or "0,5" in reply
        assert "1,00 điểm" in reply or "1,0" in reply
        assert "22 câu" in reply
        assert "90 phút" in reply
        assert "Thông tư số 32" in reply or "YCCĐ" in reply

        # Anti-regression: Must NEVER return an exam code template or diff
        assert data.get("diff") is None
        assert data.get("diffs") == []
        assert data.get("suggested_latex") is None
        assert r"\documentclass" not in reply

    # --------------------------------------------------------------------------
    # Scenario B: Syntax Guide for ex_test.sty, TikZ & tkz-tab
    # --------------------------------------------------------------------------
    @pytest.mark.parametrize("prompt", [
        "Hướng dẫn cú pháp ex_test",
        "Cú pháp lệnh choice và choicetf trong ex_test",
        "Hướng dẫn vẽ TikZ và bảng biến thiên tkz-tab",
        r"Cú pháp \shortans",
    ])
    def test_scenario_b_syntax_qa(self, prompt):
        assert is_qa_request(prompt) is True

        res = client.post(
            "/api/v1/composer/chat",
            json={"message": prompt, "current_latex": "", "history": []}
        )
        assert res.status_code == 200
        data = res.json()
        reply = data["reply"]

        # Assert correct package requirements
        assert "ex_test.sty" in reply
        assert r"\choice" in reply
        assert r"\choiceTF[1]" in reply  # Enforce [1] parameter rule
        assert r"\shortans" in reply
        assert r"\begin{center}" in reply  # Centered layout invariant
        assert "samples=50" in reply  # Samples rule
        assert "tkz-tab" in reply

        # Anti-regression: Must not contain unwanted diffs
        assert data.get("diff") is None
        assert data.get("diffs") == []

    # --------------------------------------------------------------------------
    # Scenario C: Exam Structure & Progress Statistics
    # --------------------------------------------------------------------------
    def test_scenario_c_analyze_exam_progress_unit(self):
        # 1. Empty latex
        empty_res = analyze_exam_progress("")
        assert empty_res["total_count"] == 0
        assert empty_res["has_header"] is False

        # 2. Perfect 22-question exam
        sample_exam = r"""\noindent
\begin{minipage}[t]{0.38\textwidth}
  \centering
  \textbf{SỞ GIÁO DỤC VÀ ĐÀO TẠO}\\
  \textbf{Mã đề: 0101}
\end{minipage}
\hfill
\begin{minipage}[t]{0.58\textwidth}
  \centering
  \textbf{KỲ THI TỐT NGHIỆP THPT NĂM 2025}
\end{minipage}

"""
        # Add 12 Part I questions
        for i in range(12):
            sample_exam += f"\\begin{{ex}}\nCâu {i+1}: ...\n\\choice{{A}}{{\\True B}}{{C}}{{D}}\n\\end{{ex}}\n"
        # Add 4 Part II questions
        for i in range(4):
            sample_exam += f"\\begin{{ex}}\nCâu {i+1}: ...\n\\choiceTF[1]{{\\True a}}{{b}}{{\\True c}}{{d}}\n\\end{{ex}}\n"
        # Add 6 Part III questions
        for i in range(6):
            sample_exam += f"\\begin{{ex}}\nCâu {i+1}: ...\n\\shortans{{10}}\n\\end{{ex}}\n"

        stats = analyze_exam_progress(sample_exam)
        assert stats["has_header"] is True
        assert stats["part1_count"] == 12
        assert stats["part2_count"] == 4
        assert stats["part3_count"] == 6
        assert stats["total_count"] == 22

    @pytest.mark.parametrize("prompt", [
        "Kiểm tra tiến độ đề thi hiện tại",
        "Thống kê số câu trong đề thi",
        "Đề thi này đã đủ câu chưa?",
        "Kiểm tra cấu trúc đề",
    ])
    def test_scenario_c_progress_report_api(self, prompt):
        assert is_qa_request(prompt) is True

        partial_exam = r"""\begin{ex}
Câu 1: ...
\choice{A}{\True B}{C}{D}
\end{ex}
\begin{ex}
Câu 2: ...
\choiceTF[1]{\True a}{b}{\True c}{d}
\end{ex}"""

        res = client.post(
            "/api/v1/composer/chat",
            json={"message": prompt, "current_latex": partial_exam, "history": []}
        )
        assert res.status_code == 200
        data = res.json()
        reply = data["reply"]

        # Must contain tabular evaluation
        assert "BÁO CÁO THỐNG KÊ & TIẾN ĐỘ" in reply
        assert "Phần I (Trắc nghiệm 4 lựa chọn)" in reply
        assert "Phần II (Đúng/Sai QĐ 764)" in reply
        assert "Phần III (Trả lời ngắn)" in reply
        assert "2 / 22" in reply
        assert "Còn thiếu" in reply

        # Anti-regression: Must not overwrite user code or return template
        assert data.get("diff") is None
        assert data.get("diffs") == []

    # --------------------------------------------------------------------------
    # Scenario D: Pedagogical Question Solution Guide
    # --------------------------------------------------------------------------
    def test_scenario_d_explain_question_pedagogy_unit(self):
        # Part I question
        q1 = r"""\begin{ex}
Cho hàm số $y = f(x)$ có bảng biến thiên. Số điểm cực trị của hàm số là:
\choice
{0}
{\True 2}
{1}
{3}
\begin{loigiai}
Đạo hàm đổi dấu 2 lần nên hàm số có 2 điểm cực trị.
\end{loigiai}
\end{ex}"""
        exp1 = explain_question_pedagogy(q1, 1)
        assert "CÂU 1 (TRẮC NGHIỆM 4 LỰA CHỌN)" in exp1
        assert "Đáp án chính xác" in exp1 and "**B**" in exp1
        assert "Các bước giải sư phạm" in exp1

        # Part II question
        q2 = r"""\begin{ex}
Cho hàm số bậc ba $y = f(x)$. Xét tính đúng/sai:
\choiceTF[1]
{\True Hàm số đồng biến trên $(1; 3)$.}
{Đồ thị hàm số không có tâm đối xứng.}
{\True Đạo hàm $f'(x) = 3x^2 - 6x$.}
{Giá trị cực tiểu bằng $0$.}
\begin{loigiai}
Lời giải câu 2.
\end{loigiai}
\end{ex}"""
        exp2 = explain_question_pedagogy(q2, 2)
        assert "CÂU 2 (TRẮC NGHIỆM ĐÚNG/SAI)" in exp2
        assert "✅ **ĐÚNG**" in exp2
        assert "❌ **SAI**" in exp2
        assert "QĐ 764" in exp2

        # Part III question
        q3 = r"""\begin{ex}
Tính giá trị của biểu thức $P = \int_0^1 2x \, dx$.
\shortans{1}
\begin{loigiai}
Ta có $P = x^2|_0^1 = 1$.
\end{loigiai}
\end{ex}"""
        exp3 = explain_question_pedagogy(q3, 3)
        assert "CÂU 3 (TRẢ LỜI NGẮN)" in exp3
        assert "Đáp số chuẩn" in exp3 and "`1`" in exp3
        assert "Các bước tư duy & giải toán" in exp3

    @pytest.mark.parametrize("prompt,target_q", [
        ("Hướng dẫn giải câu 1", 1),
        ("Giải thích câu 2", 2),
        ("Chữa câu 1 giúp tôi", 1),
    ])
    def test_scenario_d_question_guide_api(self, prompt, target_q):
        assert is_qa_request(prompt) is True

        exam_latex = r"""\begin{ex}
Câu 1: Hàm số $y = 2x + 1$ có hệ số góc bằng bao nhiêu?
\choice
{1}
{\True 2}
{3}
{0}
\end{ex}
\begin{ex}
Câu 2: Cho hàm số $f(x)$. Xét tính đúng sai:
\choiceTF[1]
{\True Ý a đúng}
{Ý b sai}
{\True Ý c đúng}
{Ý d sai}
\end{ex}"""

        res = client.post(
            "/api/v1/composer/chat",
            json={"message": prompt, "current_latex": exam_latex, "history": []}
        )
        assert res.status_code == 200
        data = res.json()
        reply = data["reply"]

        assert f"CÂU {target_q}" in reply
        assert "HƯỚNG DẪN GIẢI SƯ PHẠM" in reply

        # Anti-regression
        assert data.get("diff") is None
        assert data.get("diffs") == []

    def test_scenario_d_question_out_of_bounds_resilience(self):
        exam_latex = r"""\begin{ex}
Câu 1: $1 + 1 = 2$.
\choice{\True A}{B}{C}{D}
\end{ex}"""
        # User asks for question 99 which does not exist
        res = client.post(
            "/api/v1/composer/chat",
            json={"message": "Hướng dẫn giải câu 99", "current_latex": exam_latex, "history": []}
        )
        assert res.status_code == 200
        data = res.json()
        assert "không tìm thấy **Câu 99**" in data["reply"]
        assert "tổng cộng 1 câu hỏi" in data["reply"]


# ==============================================================================
# SECTION 3: NEGATIVE & INTENT CLASSIFICATION INTEGRITY
# ==============================================================================

class TestIntentClassificationSafety:
    """Ensures action commands are NOT misclassified as Q&A and general math isn't hijacked."""

    def test_action_prompts_not_hijacked_as_qa(self):
        # Action requests to create questions
        assert is_qa_request("Tạo câu hỏi về tích phân từng phần") is False
        assert is_qa_request("Thêm câu trắc nghiệm Đúng/Sai") is False
        assert is_qa_request("Chèn đề thi chuẩn 2025") is False
        assert is_qa_request("Sinh câu hỏi hình học không gian") is False
        assert is_qa_request("Viết đề khảo sát") is False

    def test_replacement_prompts_not_hijacked_as_qa(self):
        assert is_qa_request("Thay câu 1 bằng câu hỏi đạo hàm") is False
        assert is_qa_request("Đổi thời gian làm bài thành 45 phút") is False
        assert is_qa_request("Sửa đáp án câu 2 sang D") is False
        assert is_qa_request("Chuyển sang chế độ lời giải") is False

    def test_general_math_prompt_preserves_assistant_flow(self):
        # General question about math theory
        assert is_qa_request("Giải thích tính đơn điệu của hàm số bậc ba khi a > 0") is False
