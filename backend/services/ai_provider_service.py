"""
AI Online Digitization Service for Quesy
Supports OpenAI, Google Gemini, Anthropic Claude, OpenRouter, and OpenAI-compatible custom endpoints.
Conforms to MoET Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT (format 2025).
"""

import os
import io
import re
import json
import base64
import logging
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

import httpx

from backend.config import settings
from backend.services.latex_converter import sanitize_latex, repair_math_delimiters
from backend.services.tagging_service import auto_tag_question

logger = logging.getLogger("quesy.ai_provider")

SYSTEM_PROMPT = r"""Bạn là Chuyên gia Khảo thí và Số hóa Đề thi hàng đầu Việt Nam theo chuẩn Chương trình GDPT 2018 (Thông tư 32/2018/TT-BGDĐT) và Cấu trúc đề thi mới của Bộ GD&ĐT (Quyết định 764/QĐ-BGDĐT định dạng 2025).

Nhiệm vụ của bạn là đọc toàn bộ nội dung đề thi (văn bản hoặc hình ảnh) được cung cấp, nhận diện và trích xuất cấu trúc đề thi một cách trung thực, đầy đủ và trả về định dạng JSON thuần túy.

QUY TẮC CẤU TRÚC 3 PHẦN THI THEO QUYẾT ĐỊNH 764/QĐ-BGDĐT:
1. PHẦN I: Câu trắc nghiệm nhiều phương án lựa chọn (item_format: "SINGLE_CHOICE")
   - Thí sinh chọn 01 phương án đúng trong 4 phương án A, B, C, D.
   - Chỉ có đúng duy nhất 1 phương án có is_correct: true.
   - Option Anchor Rule: Nếu phương án mang tính phủ định/tổng hợp ("Không có đáp án nào", "Tất cả các ý trên đều đúng/sai", "Cả A và B đều đúng",...) thì đánh dấu is_fixed: true.

2. PHẦN II: Câu trắc nghiệm Đúng/Sai (item_format: "TRUE_FALSE_GROUP")
   - Mỗi câu gồm phần dẫn (stem) và đúng 4 ý khẳng định phụ a), b), c), d) (mảng sub_statements).
   - Mỗi ý khẳng định con có nhãn "a", "b", "c", "d", thuộc tính is_true: true hoặc false, kèm lời giải giải thích tính đúng sai (explanation).

3. PHẦN III: Câu trắc nghiệm trả lời ngắn (item_format: "SHORT_ANSWER")
   - Thí sinh điền kết quả số hoặc chuỗi.
   - short_answer_value: chuỗi hoặc số đáp án đúng (ví dụ: "12", "-3.5").
   - tolerance: dung sai (mặc định 0.0 hoặc 0.01).

QUY TẮC CÔNG THỨC TOÁN HỌC & KÝ HIỆU (CHUẨN BẮT BUỘC):
1. Dấu ngoặc mở/đóng: BẮT BUỘC dùng \left và \right cho tất cả các loại dấu ngoặc:
   - Ngoặc tròn: \left( ... \right) (ví dụ: \left(x - 1\right), f\left(x\right), \left(1; 2\right))
   - Ngoặc vuông: \left[ ... \right] (ví dụ: \left[0; 3\right], \left[-2; 5\right))
   - Ngoặc nhọn: \left\{ ... \right\} (ví dụ: \left\{1; 2\right\}; TUYỆT ĐỐI không viết double backslash \\{ hay \left\\{)
2. Số thập phân:
   - Trong phần NỘI DUNG ĐỀ BÀI (stem): BẮT BUỘC viết dưới dạng dấu phẩy đặt trong ngoặc nhọn {,} để không bị lỗi khoảng trắng trong KaTeX (ví dụ: 15{,}25, 0{,}5, -3{,}14; TUYỆT ĐỐI KHÔNG viết 15.25 hay 15,25).
   - Trong phần ĐÁP ÁN (options A, B, C, D và short_answer_value): TUYỆT ĐỐI KHÔNG dùng dấu ngoặc nhọn {} cho số thập phân! Viết số thập phân thông thường dạng "15,25" hoặc "3,9" (không viết 15{,}25 hay 3{,}9).
3. Phân số: BẮT BUỘC dùng \dfrac thay vì \frac (ví dụ: \dfrac{a}{b}, \dfrac{1}{2}, \dfrac{-b}{2a}).
4. Dấu vectơ: BẮT BUỘC dùng \overrightarrow thay vì \vec (ví dụ: \overrightarrow{u}, \overrightarrow{AB}, \overrightarrow{a}, \overrightarrow{0}).
5. QUY TẮC CHỮ HOA/THƯỜNG CỦA PHƯƠNG ÁN (OPTIONS):
   - Trường 'content' của phương án KHÔNG được lặp lại tiền tố nhãn 'A.', 'B.', 'C.', 'D.' (chỉ ghi content: '1' hoặc '$x = 1$', TUYỆT ĐỐI KHÔNG ghi content: 'A. 1'). Nhãn 'A', 'B', 'C', 'D' được lưu riêng ở trường 'label'.
   - Chỉ in hoa chữ cái đầu câu của phương án, TUYỆT ĐỐI KHÔNG VIẾT IN HOA TOÀN BỘ cả câu (ví dụ: viết 'Hàm số đồng biến trên khoảng...' thay vì 'HÀM SỐ ĐỒNG BIẾN TRÊN KHOẢNG...').
- Toàn bộ công thức toán, biến số, phân số, căn thức, vectơ, ma trận, tập hợp, bất phương trình PHẢI được định dạng chuẩn LaTeX đặt trong cặp dấu ${...}$ (ví dụ: ${y = x^3 - 3x + 1}$, ${\overrightarrow{u} = \left(1; 2; -3
ight)}$, ${\dfrac{a}{b}}$, ${\mathbb{R}}$, ${\ge}$, ${\in}$, ${\overrightarrow{IJ} = \dfrac{1}{2}\left(\overrightarrow{CD} + \overrightarrow{AD} + \overrightarrow{DB}
ight)}$). BẮT BUỘC bọc công thức trong ${...}$.
- Tuyệt đối không để sót ký tự rác chữ Hán hay mã nhị phân lỗi.

QUY TẮC NHẬN DIỆN VÀ TÁI TẠO ĐỒ THỊ, HÌNH VẼ, BẢNG BIẾN THIÊN BẰNG TIKZ / ARRAY (CHUẨN BẮT BUỘC):
1. ĐỒ THỊ HÀM SỐ & HÌNH HỌC (BẮT BUỘC DÙNG MÃ TIKZ):
   - Khi câu hỏi trong đề thi có chứa Đồ thị hàm số (hàm bậc ba, hàm phân thức, hàm bậc bốn trùng phương, parabol, tương giao đồ thị, đạo hàm f'(x)), Hình học không gian (hình chóp, lăng trụ, nón, trụ, cầu) hoặc Hình học toạ độ Oxy/Oxyz:
   - BẮT BUỘC PHẢI TÁI TẠO LẠI HÌNH VẼ ĐÓ DƯỚI DẠNG MÃ TIKZ \begin{tikzpicture} ... \end{tikzpicture} VÀ NHÚNG TRỰC TIẾP VÀO PHẦN stem (HOẶC VÀO TỪNG PHƯƠNG ÁN options NẾU LÀ CÂU HỎI NHẬN DẠNG ĐỒ THỊ A, B, C, D).
   - QUY TẮC TOÁN HỌC CHÍNH XÁC KHI DỰNG ĐỒ THỊ:
     + MÀU SẮC ĐƯỜNG NÉT: Đường cong đồ thị BẮT BUỘC vẽ bằng màu ĐEN: \draw[thick, black, smooth] ..., TUYỆT ĐỐI KHÔNG DÙNG MÀU BLUE HOẶC MÀU KHÁC (đáp ứng chuẩn in ấn thi cử). Các đường tiệm cận, đường dóng tọa độ vẽ bằng nét đứt \draw[dashed, thick] ...
     + CHỮ VÀ SỐ TRONG ĐỒ THỊ: TOÀN BỘ nhãn trục, gốc tọa độ, số liệu, tên hàm số BẮT BUỘC viết trong LaTeX math mode: \node[below left] at (0,0) {$O$};, node[right] {$x$}, node[above] {$y$}, node[below] {$-4$}, node[left] {$6$}, node {$y=f(x)$}. TUYỆT ĐỐI KHÔNG viết số hay chữ dạng text trần (như {0}, {x}, {y}, {-4}).
     + ĐỘ PHỦ ĐỒ THỊ (DOMAIN VÀ LIMITS): Đường cong hàm số BẮT BUỘC PHẢI ĐƯỢC VẼ TRÀN HẾT PHẠM VI 2 TRỤC TỌA ĐỘ (từ x_min đến x_max của trục Ox, và vươn sát lên y_max, chìm sát xuống y_min của trục Oy).
       * Đối với hàm phân thức có tiệm cận đứng x = x0: Nhánh trái vẽ từ mép trái x_min đến (x0 - 0.2); Nhánh phải vẽ từ (x0 + 0.2) đến mép phải x_max. Tuyệt đối không được ngắt cụt lơ lửng đồ thị ở giữa chừng.
     + KHUNG HÌNH (BOUNDING BOX & CLIP): Khung \clip (xmin - 1.2, ymin - 1.2) rectangle (xmax + 1.2, ymax + 1.2); PHẢI ĐỦ RỘNG để bao trọn toàn bộ các điểm cực trị, nhánh đồ thị, đường dóng nét đứt, mũi tên trục và nhãn tên trục $x, y, O$ mà không bị cắt cụt (crop) mất bất kỳ chi tiết nào.
     + CÂU HỎI NHẬN DIỆN ĐỒ THỊ Ở 4 PHƯƠNG ÁN A, B, C, D: BẮT BUỘC CẢ 4 HÌNH ĐỀU PHẢI CÓ ĐẦY ĐỦ VẠCH CHIA TỌA ĐỘ VÀ SỐ LIỆU ĐỒNG BỘ ĐỂ ĐỐI CHIẾU (không được hình có số, hình bị mất số). Dùng khối TikZ thu nhỏ \begin{tikzpicture}[scale=0.22, font=\tiny, >=stealth] ... \end{tikzpicture}.
     + TUYỆT ĐỐI KHÔNG bọc thẻ \begin{center} hay \end{center} quanh TikZ (hệ thống tự động căn giữa).
   - TUYỆT ĐỐI KHÔNG BỎ QUA HÌNH VẼ, ĐỒ THỊ! Mọi câu hỏi có hình minh họa đều phải có khối mã TikZ tương ứng để hệ thống biên dịch hiển thị đồ thị vector SVG sắc nét.
2. BẢNG BIẾN THIÊN & BẢNG SỐ LIỆU:
   - Đối với BẢNG BIẾN THIÊN / BẢNG XÉT DẤU:
     + Cách 1 (Khuyến nghị - TikZ vector chuẩn đẹp): Dùng khối TikZ package tkz-tab:
       \begin{tikzpicture}
       \tkzTabInit[nocadre]{$x$/.6,$f'(x)$/.6,$f(x)$/2}{$-\infty$,$x_1$,$x_2$,$+\infty$}
       \tkzTabLine{,-,0,+,0,-,}
       \tkzTabVar{+/ $+\infty$, -/$-2$, +/$4$, -/$-\infty$}
       \end{tikzpicture}
       (Đối với tiệm cận đứng, dùng +D-/$+\infty$/$-\infty$ hoặc -D+).
     + Cách 2 (Mảng KaTeX): Bọc chuẩn trong display math KaTeX: $$\begin{array}{|c|c|...|} \hline ... \hline \end{array}$$
   - TUYỆT ĐỐI KHÔNG để thiếu dấu đóng $$ và không viết lệnh \left bên trong thẻ text \text{...}.

QUY TẮC PHÂN LOẠI CHUẨN THÔNG TƯ 32/2018/TT-BGDĐT (KHÔNG PHÂN CHIA BỘ SÁCH):
- subject: Môn học (mặc định "Toán học")
- grade: Khối lớp (ví dụ "12", "11", "10")
- strand: Mạch nội dung ("Số, Đại số & Giải tích", "Hình học & Đo lường", "Thống kê & Xác suất")
- topic: Tên chủ đề (ví dụ "Ứng dụng đạo hàm để khảo sát hàm số", "Phương pháp toạ độ trong không gian")
- lesson: Bài học tương ứng
- learning_outcome_code: Mã Yêu cầu cần đạt chuẩn (ví dụ: TOAN12.GT.01, TOAN12.GT.02, TOAN12.HH.01, TOAN12.XS.01)
- cognitive_level: Mức độ nhận thức ("RECOGNITION" - Biết, "COMPREHENSION" - Hiểu, "APPLICATION" - Vận dụng)
- problem_archetype: Dạng bài toán (ví dụ: "Cực trị hàm bậc ba", "Tiệm cận đồ thị", "Tích vô hướng hai vectơ")

ĐỊNH DẠNG ĐẦU RA YÊU CẦU:
Trả về DUY NHẤT một đối tượng JSON hợp lệ (không kèm văn bản giải thích ngoài JSON):
{
  "exam_metadata": {
    "title": "Tên kỳ thi",
    "subject": "Toán học",
    "grade": "12",
    "duration_minutes": 90
  },
  "questions": [
    {
      "id": 1,
      "code": "EXTRACT-001",
      "item_format": "SINGLE_CHOICE",
      "cognitive_level": "RECOGNITION",
      "strand": "Số, Đại số & Giải tích",
      "topic": "Ứng dụng đạo hàm để khảo sát hàm số",
      "lesson": "Cực trị của hàm số",
      "learning_outcome_code": "TOAN12.GT.01",
      "problem_archetype": "Cực trị hàm bậc 3",
      "stem": "Nội dung câu hỏi...",
      "options": [
        { "label": "A", "content": "Nội dung A", "is_correct": true, "is_fixed": false },
        { "label": "B", "content": "Nội dung B", "is_correct": false, "is_fixed": false },
        { "label": "C", "content": "Nội dung C", "is_correct": false, "is_fixed": false },
        { "label": "D", "content": "Nội dung D", "is_correct": false, "is_fixed": false }
      ],
      "explanation": "Lời giải chi tiết...",
      "confidence": 98.0
    }
  ]
}
"""

SYSTEM_PROMPT_PASS1_TEXT = SYSTEM_PROMPT + r"""

QUY TẮC ĐẶC BIỆT CHO HÌNH VẼ, ĐỒ THỊ, BẢNG BIỂU (PIPELINE 2-PASS):
Trên tài liệu đã được đánh dấu trực quan các khung nhãn định danh như [FIGURE_1], [FIGURE_2], [TABLE_1]...
1. Bạn TUYỆT ĐỐI KHÔNG vẽ lại hình, KHÔNG cố sinh mã TikZ phức tạp trong lượt này.
2. Tại vị trí xuất hiện của hình vẽ hoặc bảng biểu trong đề bài (stem) hoặc phương án (options), bạn chỉ cần chèn đúng thẻ placeholder tương ứng: {{FIGURE_1}}, {{FIGURE_2}}, {{TABLE_1}}...
3. Tập trung 100% vào việc bóc tách chính xác câu chữ, công thức toán học, nhãn A, B, C, D, tính đúng/sai và lời giải.
"""

SYSTEM_PROMPT_PASS2_FIGURE = r"""Bạn là Chuyên gia Đồ họa Toán học LaTeX & TikZ hàng đầu.
Nhiệm vụ của bạn là quan sát kỹ bức ảnh được cung cấp (chứa một hình vẽ hình học, đồ thị hàm số, hoặc bảng số liệu/bảng biến thiên) và chuyển đổi thành mã nguồn LaTeX chuẩn mực:
1. Nếu là ĐỒ THỊ HÀM SỐ hoặc HÌNH HỌC:
   - Hãy xuất mã \begin{tikzpicture} ... \end{tikzpicture} hoàn chỉnh, tự chứa.
   - Thể hiện rõ hệ trục tọa độ Ox, Oy, mũi tên, các điểm gốc O, các tọa độ đặc biệt, tiệm cận (nét đứt), đường cong hàm số mượt mà.
2. Nếu là BẢNG BIẾN THIÊN hoặc BẢNG SỐ LIỆU:
   - Hãy xuất mã \begin{array}{...} ... \end{array} chuẩn KaTeX, sử dụng các mũi tên \nearrow, \searrow, các giá trị giới hạn, hàng x, y', y.
Chỉ trả về duy nhất khối mã LaTeX/TikZ (hoặc bọc trong ```latex ... ```), không kèm lời giải thích rườm rà.
"""


def detect_provider() -> str:
    """Detects active AI provider based on settings and environment keys."""
    if settings.AI_PROVIDER:
        return settings.AI_PROVIDER.lower()

    key = settings.AI_API_KEY or ""
    if key.startswith("AIza") or os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if key.startswith("sk-ant") or os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if key.startswith("sk-or") or os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    return "openai"


def get_default_model(provider: str) -> str:
    """Returns sensible default model name for provider if not explicitly configured."""
    if settings.AI_MODEL:
        return settings.AI_MODEL

    model_defaults = {
        "gemini": "gemini-1.5-flash",
        "anthropic": "claude-3-5-sonnet-20241022",
        "openrouter": "google/gemini-2.0-flash-exp:free",
        "openai": "gpt-4o",
    }
    return model_defaults.get(provider, "gpt-4o")


def file_to_base64_data_url(file_path: Union[str, Path]) -> Tuple[str, str]:
    """Reads a file and returns its mime type and raw base64 string."""
    p = Path(file_path)
    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        ext = p.suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
        }
        mime = mime_map.get(ext, "application/octet-stream")

    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return mime, b64


def repair_llm_json(s: str) -> str:
    """Repairs unescaped LaTeX backslashes and unescaped newlines inside JSON strings
    so that json.loads always succeeds even when LLM emits raw TeX syntax like \\dfrac, \\left.
    """
    start_brace = s.find('{')
    start_bracket = s.find('[')
    if start_brace == -1 and start_bracket == -1:
        return s
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start = start_brace
        end = s.rfind('}') + 1
    else:
        start = start_bracket
        end = s.rfind(']') + 1

    if end <= start:
        return s

    s = s[start:end]

    out = []
    in_string = False
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]
        if not in_string:
            if ch == '"':
                in_string = True
            out.append(ch)
            i += 1
        else:
            if ch == '"':
                in_string = False
                out.append(ch)
                i += 1
            elif ch == '\\':
                if i + 1 >= n:
                    out.append(r'\\')
                    i += 1
                    continue
                next_ch = s[i + 1]

                # Check for LaTeX commands starting with backslash followed by letters
                if next_ch in 'ftbrn' and i + 2 < n and s[i + 2].isalpha():
                    out.append(r'\\')
                    i += 1
                elif next_ch in '"\\/bfnrt':
                    out.append(ch)
                    out.append(next_ch)
                    i += 2
                elif next_ch == 'u' and i + 5 < n and all(c in '0123456789abcdefABCDEF' for c in s[i+2:i+6]):
                    out.append(s[i:i+6])
                    i += 6
                else:
                    # Invalid escape sequence in JSON (e.g. \d, \l, \s, \c, \h, \a, \{, \})
                    out.append(r'\\')
                    i += 1
            elif ch == '\n':
                out.append(r'\n')
                i += 1
            elif ch == chr(13):  # Carriage return
                i += 1
            elif ch == '\t':
                out.append(r'\t')
                i += 1
            else:
                out.append(ch)
                i += 1

    return "".join(out)


def normalize_option_text(text: str) -> str:
    """Cleans option text:
    1. Removes redundant leading label prefixes ('A. ', 'A) ', 'A - ') to avoid 'A. A. 1'.
    2. Converts accidental ALL-CAPS text to standard sentence case (only capitalize first character).
    """
    if not text:
        return ""
    s = text.strip()
    # Strip leading label prefix like "A. ", "A) ", "a. ", "A - "
    s = re.sub(r'^[A-Da-d][\.\)\:\-\/]\s*', '', s).strip()

    # If the non-math text is all uppercase, convert to sentence case
    parts = re.split(r'(\$[^\$]+\$)', s)
    for idx, part in enumerate(parts):
        if not part.startswith('$') and len(part.strip()) > 2:
            letters = [c for c in part if c.isalpha()]
            if letters and all(c.isupper() for c in letters):
                parts[idx] = part[0].upper() + part[1:].lower()
    return "".join(parts).strip()


class AIProviderService:
    """Service to send exam documents (text, images, PDFs) to external AI LLM providers."""

    def __init__(self):
        self.provider = detect_provider()
        self.api_key = settings.AI_API_KEY
        self.model = get_default_model(self.provider)
        self.base_url = settings.AI_BASE_URL
        self.timeout = getattr(settings, "AI_TIMEOUT", 180.0)

    def is_configured(self) -> bool:
        """Returns True if an external AI API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def digitize_exam(
        self,
        document_text: str = "",
        image_paths: Optional[List[Union[str, Path]]] = None,
        pdf_path: Optional[Union[str, Path]] = None,
        filename: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Sends the exam content to the configured AI Provider and returns structured questions.
        """
        if not self.is_configured():
            raise ValueError(
                "Chưa cấu hình API Key trong file .env (AI_API_KEY, GEMINI_API_KEY, hoặc OPENAI_API_KEY). "
                "Vui lòng thêm API Key vào file .env để kích hoạt AI bóc tách trực tuyến!"
            )

        logger.info(
            f"Dispatching exam digitization to AI Provider: {self.provider.upper()} | Model: {self.model} | File: {filename or 'unknown'}"
        )

        image_paths = image_paths or []

        if self.provider == "gemini":
            return self._call_gemini(document_text, image_paths, pdf_path)
        elif self.provider == "anthropic":
            return self._call_anthropic(document_text, image_paths, pdf_path)
        elif self.provider == "openrouter":
            return self._call_openai_compatible(
                document_text,
                image_paths,
                pdf_path,
                base_url=self.base_url or "https://openrouter.ai/api/v1",
                extra_headers={"HTTP-Referer": "http://localhost:8000", "X-Title": "Quesy Exam Manager"}
            )
        else:
            # Default to OpenAI or custom compatible endpoint
            base = self.base_url or "https://api.openai.com/v1"
            return self._call_openai_compatible(document_text, image_paths, pdf_path, base_url=base)

    def _call_openai_compatible(
        self,
        text: str,
        image_paths: List[Union[str, Path]],
        pdf_path: Optional[Union[str, Path]],
        base_url: str,
        extra_headers: Optional[Dict[str, str]] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Calls OpenAI or OpenRouter or custom OpenAI-compatible API."""
        endpoint = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        user_content: List[Dict[str, Any]] = []

        prompt_text = "Dưới đây là nội dung đề thi cần số hóa theo chuẩn Thông tư 32 và QĐ 764:\n\n"
        if text.strip():
            prompt_text += text.strip() + "\n\n"
        prompt_text += "Hãy phân tích đề thi và trả về định dạng JSON đúng theo schema đã hướng dẫn."

        user_content.append({"type": "text", "text": prompt_text})

        # Add images if available
        for img_p in image_paths:
            p = Path(img_p)
            if p.exists():
                mime, b64 = file_to_base64_data_url(p)
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"}
                })

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content if len(user_content) > 1 else prompt_text}
            ],
            "temperature": settings.AI_TEMPERATURE,
            "max_tokens": settings.AI_MAX_TOKENS,
        }

        # Request JSON output where supported
        if "gpt" in self.model.lower() or "json" in self.model.lower():
            payload["response_format"] = {"type": "json_object"}

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"AI API error (HTTP {resp.status_code}): {resp.text}")

            result = resp.json()
            raw_reply = result["choices"][0]["message"]["content"]
            return self._parse_json_result(raw_reply)

    def _call_gemini(
        self,
        text: str,
        image_paths: List[Union[str, Path]],
        pdf_path: Optional[Union[str, Path]]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Calls Google Gemini generateContent API (supports native PDF and images)."""
        model_name = self.model or "gemini-1.5-flash"
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"

        parts: List[Dict[str, Any]] = []

        # If PDF exists, Gemini can ingest PDF natively
        if pdf_path and Path(pdf_path).exists():
            mime, b64 = file_to_base64_data_url(pdf_path)
            parts.append({
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": b64
                }
            })

        # Add any extracted images
        for img_p in image_paths:
            p = Path(img_p)
            if p.exists():
                mime, b64 = file_to_base64_data_url(p)
                parts.append({
                    "inline_data": {
                        "mime_type": mime,
                        "data": b64
                    }
                })

        prompt_instruction = f"{SYSTEM_PROMPT}\n\nNỘI DUNG ĐỀ THI:\n{text}\n\nHãy xuất kết quả bóc tách dạng JSON:"
        parts.append({"text": prompt_instruction})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": settings.AI_TEMPERATURE,
                "response_mime_type": "application/json"
            }
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(endpoint, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API error (HTTP {resp.status_code}): {resp.text}")

            result = resp.json()
            raw_reply = result["candidates"][0]["content"]["parts"][0]["text"]
            return self._parse_json_result(raw_reply)

    def _call_anthropic(
        self,
        text: str,
        image_paths: List[Union[str, Path]],
        pdf_path: Optional[Union[str, Path]]
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Calls Anthropic Claude Messages API."""
        endpoint = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        content_parts: List[Dict[str, Any]] = []

        if pdf_path and Path(pdf_path).exists():
            mime, b64 = file_to_base64_data_url(pdf_path)
            content_parts.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": b64
                }
            })

        for img_p in image_paths:
            p = Path(img_p)
            if p.exists():
                mime, b64 = file_to_base64_data_url(p)
                content_parts.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime,
                        "data": b64
                    }
                })

        prompt_text = "Dưới đây là nội dung đề thi cần số hóa:\n\n"
        if text.strip():
            prompt_text += text.strip() + "\n\n"
        prompt_text += "Hãy phân tích đề thi và trả về định dạng JSON thuần túy theo hướng dẫn."
        content_parts.append({"type": "text", "text": prompt_text})

        payload = {
            "model": self.model or "claude-3-5-sonnet-20241022",
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": content_parts}],
            "max_tokens": settings.AI_MAX_TOKENS,
            "temperature": settings.AI_TEMPERATURE,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Anthropic API error (HTTP {resp.status_code}): {resp.text}")

            result = resp.json()
            raw_reply = result["content"][0]["text"]
            return self._parse_json_result(raw_reply)

    def _parse_json_result(self, raw_text: str) -> Tuple[List[Dict[str, Any]], float]:
        """Parses and sanitizes LLM JSON reply into Quesy standard question models."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except Exception as first_err:
            logger.info(f"Direct JSON parse failed ({first_err}), repairing unescaped LaTeX backslashes...")
            repaired = repair_llm_json(cleaned)
            data = json.loads(repaired)
        questions_raw = data.get("questions", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

        standardized: List[Dict[str, Any]] = []
        total_conf = 0.0

        for idx, q in enumerate(questions_raw):
            qid = q.get("id") or idx + 1
            code = q.get("code") or f"EXTRACT-{qid:03d}"
            stem = sanitize_latex(repair_math_delimiters(q.get("stem", "")))
            fmt = q.get("item_format", "SINGLE_CHOICE")
            cog = q.get("cognitive_level", "RECOGNITION")

            raw_conf = q.get("confidence") or q.get("confidence_score") or 95.0
            conf = raw_conf if raw_conf > 1.0 else raw_conf * 100.0

            # Run auto-tagging to refine YCCD, lesson, and problem archetype
            raw_opts = [str(opt.get("content", "")) for opt in q.get("options", [])]
            auto_tags = auto_tag_question(stem=stem, options=raw_opts, subject="Toán học", grade="12")
            yccd = q.get("learning_outcome_code")
            lesson = q.get("lesson")
            topic = q.get("topic")
            strand = q.get("strand")
            archetype = q.get("problem_archetype")

            # If learning_outcome_code is missing or default "TOAN12.GT.01", override with accurately detected tag
            if (not yccd or yccd == "TOAN12.GT.01") and auto_tags.get("learning_outcome_code"):
                yccd = auto_tags["learning_outcome_code"]
                lesson = auto_tags.get("lesson") or lesson
                topic = auto_tags.get("topic") or topic
                strand = auto_tags.get("strand") or strand
                archetype = auto_tags.get("problem_archetype") or archetype

            std_q: Dict[str, Any] = {
                "id": qid,
                "code": code,
                "question_number": qid,
                "item_format": fmt,
                "cognitive_level": cog,
                "strand": strand or "Số, Đại số & Giải tích",
                "topic": topic or "Khảo sát và vẽ đồ thị hàm số",
                "lesson": lesson or "Khảo sát hàm số",
                "learning_outcome_code": yccd or "TOAN12.GT.01",
                "problem_archetype": archetype or "Dạng toán cơ bản",
                "stem": stem,
                "explanation": sanitize_latex(repair_math_delimiters(q.get("explanation", ""))),
                "confidence": round(conf, 1),
                "confidence_score": round(conf, 1),
                "confidence_badge": "GREEN" if conf >= 95 else ("YELLOW" if conf >= 80 else "RED")
            }

            if fmt == "SINGLE_CHOICE":
                opts = []
                for o_idx, opt in enumerate(q.get("options", [])):
                    c = sanitize_latex(repair_math_delimiters(str(opt.get("content", ""))))
                    # Do not use {,} brackets for decimal numbers in answers
                    c = c.replace("{,}", ",")
                    # Normalize option text: strip redundant "A. " and normalize all-caps
                    c = normalize_option_text(c)
                    lbl = opt.get("label", chr(65 + o_idx))
                    opts.append({
                        "label": lbl,
                        "content": c,
                        "is_correct": bool(opt.get("is_correct", False)),
                        "is_fixed": bool(opt.get("is_fixed", False))
                    })
                std_q["options"] = opts

            elif fmt == "TRUE_FALSE_GROUP":
                subs = []
                for s_idx, sub in enumerate(q.get("sub_statements", [])):
                    c = sanitize_latex(repair_math_delimiters(str(sub.get("content", ""))))
                    lbl = sub.get("label", chr(97 + s_idx))
                    subs.append({
                        "label": lbl,
                        "content": c,
                        "is_true": bool(sub.get("is_true", False)),
                        "explanation": sanitize_latex(repair_math_delimiters(str(sub.get("explanation", ""))))
                    })
                std_q["sub_statements"] = subs

            elif fmt == "SHORT_ANSWER":
                raw_short = str(q.get("short_answer_value", "")).strip()
                # Clean any LaTeX formatting or curly brackets from short answers: 3{,}9 -> 3,9
                clean_short = raw_short.replace("{,}", ",").replace("{", "").replace("}", "").replace("$", "").strip()
                std_q["short_answer_value"] = clean_short
                std_q["tolerance"] = float(q.get("tolerance", 0.0))

            standardized.append(std_q)
            total_conf += conf

        avg_conf = round(total_conf / max(1, len(standardized)), 1)
        return standardized, avg_conf

    def convert_figure_to_latex(
        self,
        figure_crop_path: Union[str, Path],
        figure_type: str = "diagram"
    ) -> str:
        """Converts an isolated cropped diagram or table image into valid LaTeX/TikZ code."""
        if not self.is_configured():
            return ""

        p = Path(figure_crop_path).resolve()
        if not p.exists():
            return ""

        prompt_instruction = (
            "Dưới đây là một ảnh cắt rời chứa hình vẽ hoặc bảng số liệu trong đề thi toán. "
            "Hãy phân tích và viết mã LaTeX / TikZ chuẩn mực để vẽ lại:"
        )

        try:
            mime, b64 = file_to_base64_data_url(p)
            if self.provider == "gemini":
                model_name = self.model or "gemini-1.5-flash"
                endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                parts = [
                    {"inline_data": {"mime_type": mime, "data": b64}},
                    {"text": f"{SYSTEM_PROMPT_PASS2_FIGURE}\n\n{prompt_instruction}"}
                ]
                payload = {
                    "contents": [{"parts": parts}],
                    "generationConfig": {"temperature": 0.1}
                }
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                        return self._clean_latex_output(raw)
            else:
                base = self.base_url or "https://api.openai.com/v1"
                endpoint = f"{base.rstrip('/')}/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT_PASS2_FIGURE},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_instruction},
                            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                        ]
                    }
                ]
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(endpoint, headers=headers, json={"model": self.model, "messages": messages, "temperature": 0.1})
                    if resp.status_code == 200:
                        raw = resp.json()["choices"][0]["message"]["content"]
                        return self._clean_latex_output(raw)
        except Exception as e:
            logger.warning(f"Failed to generate LaTeX for figure {p.name}: {e}")
        return ""

    def _clean_latex_output(self, raw_text: str) -> str:
        """Strips markdown code fences and returns pure LaTeX code."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text

    def digitize_exam_2pass(
        self,
        annotated_page_images: List[Union[str, Path]],
        detected_figures: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """2-Pass Decoupled Exam Digitization:
        Pass 1: Reads text structure and question items with visual landmark placeholders.
        Pass 2: Converts cropped diagrams & tables to dedicated LaTeX/TikZ code.
        Stitching: Merges LaTeX or falls back to cropped WebP images safely.
        """
        # Pass 1: Digitize text and question structure
        orig_sys = globals().get("SYSTEM_PROMPT")
        try:
            globals()["SYSTEM_PROMPT"] = SYSTEM_PROMPT_PASS1_TEXT
            questions, avg_conf = self.digitize_exam(
                document_text="",
                image_paths=annotated_page_images,
                pdf_path=None,
                filename=filename
            )
        finally:
            if orig_sys:
                globals()["SYSTEM_PROMPT"] = orig_sys

        # Pass 2: Process all detected figures in parallel to maximize speed
        from concurrent.futures import ThreadPoolExecutor, as_completed

        figure_latex_map: Dict[str, str] = {}
        valid_figures = [
            fig for fig in detected_figures
            if fig.get("crop_path") and Path(str(fig["crop_path"])).exists()
        ]

        if valid_figures:
            max_workers = min(6, len(valid_figures))
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_fig = {
                    executor.submit(
                        self.convert_figure_to_latex,
                        fig["crop_path"],
                        fig.get("type", "diagram")
                    ): fig for fig in valid_figures
                }
                for future in as_completed(future_to_fig):
                    fig = future_to_fig[future]
                    fig_id = str(fig.get("id", ""))
                    try:
                        latex_code = future.result()
                        if latex_code:
                            figure_latex_map[fig_id] = latex_code
                    except Exception as ex:
                        logger.warning(f"Parallel figure conversion error for {fig_id}: {ex}")

        # Stitching & Fallback
        stitched_questions = self.stitch_figures(questions, detected_figures, figure_latex_map)
        return stitched_questions, avg_conf

    def stitch_figures(
        self,
        questions: List[Dict[str, Any]],
        detected_figures: List[Dict[str, Any]],
        figure_latex_map: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Replaces {{FIGURE_X}} or {{TABLE_X}} tokens with verified LaTeX/TikZ or safe image fallback."""
        from backend.services.tikz_renderer import render_tikz_to_svg

        fig_dict: Dict[str, Dict[str, Any]] = {str(f.get("id", "")): f for f in detected_figures if f.get("id")}

        for q in questions:
            stem = q.get("stem", "")
            for fig_id, fig_info in fig_dict.items():
                tags_to_check = [f"{{{{{fig_id}}}}}", f"[{fig_id}]", f"{{{{ {fig_id} }}}}"]
                has_tag = any(tag in stem for tag in tags_to_check)

                if has_tag:
                    latex_code = figure_latex_map.get(str(fig_id), "").strip()
                    replacement = ""

                    # Verify TikZ code if it is a tikzpicture
                    if "\\begin{tikzpicture}" in latex_code:
                        render_res = render_tikz_to_svg(latex_code)
                        if render_res.get("success"):
                            replacement = f"\n\n{latex_code}\n\n"
                        else:
                            # Fallback to cropped image asset
                            crop_url = str(fig_info.get("crop_url", ""))
                            replacement = f'\n\n<div class="crop-figure-fallback my-3 text-center"><img src="{crop_url}" class="max-h-72 inline-block rounded border border-slate-200" alt="{fig_id}"/></div>\n\n'
                    elif "\\begin{array}" in latex_code or "\\begin{tabular}" in latex_code:
                        clean_arr = latex_code if latex_code.startswith("$$") else f"$${latex_code}$$"
                        replacement = f"\n\n{clean_arr}\n\n"
                    else:
                        # Fallback to image tag
                        crop_url = str(fig_info.get("crop_url", ""))
                        if crop_url:
                            replacement = f'\n\n<div class="crop-figure-fallback my-3 text-center"><img src="{crop_url}" class="max-h-72 inline-block rounded border border-slate-200" alt="{fig_id}"/></div>\n\n'

                    if replacement:
                        for tag in tags_to_check:
                            stem = stem.replace(tag, replacement)

            q["stem"] = stem

            # Also check options
            for opt in q.get("options", []):
                opt_content = str(opt.get("content", ""))
                for fig_id, fig_info in fig_dict.items():
                    tags_to_check = [f"{{{{{fig_id}}}}}", f"[{fig_id}]"]
                    for tag in tags_to_check:
                        if tag in opt_content:
                            latex_code = figure_latex_map.get(str(fig_id), "").strip()
                            if latex_code:
                                opt_content = opt_content.replace(tag, f" {latex_code} ")
                            else:
                                crop_url = str(fig_info.get("crop_url", ""))
                                opt_content = opt_content.replace(tag, f'<img src="{crop_url}" class="inline-block max-h-36"/>')
                    opt["content"] = opt_content

        return questions


default_ai_provider_service = AIProviderService()
