"""
AI Online Digitization Service for Quesy
Supports OpenAI, Google Gemini, Anthropic Claude, OpenRouter, and OpenAI-compatible custom endpoints.
Conforms to MoET Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT (format 2025).
"""

import os
import io
import json
import base64
import logging
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

import httpx

from backend.config import settings
from backend.services.latex_converter import sanitize_latex, repair_math_delimiters

logger = logging.getLogger("quesy.ai_provider")

SYSTEM_PROMPT = """Bạn là Chuyên gia Khảo thí và Số hóa Đề thi hàng đầu Việt Nam theo chuẩn Chương trình GDPT 2018 (Thông tư 32/2018/TT-BGDĐT) và Cấu trúc đề thi mới của Bộ GD&ĐT (Quyết định 764/QĐ-BGDĐT định dạng 2025).

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

QUY TẮC CÔNG THỨC TOÁN HỌC & KÝ HIỆU:
- Toàn bộ công thức toán, biến số, phân số, căn thức, vectơ, ma trận, tập hợp, bất phương trình PHẢI được định dạng chuẩn LaTeX/KaTeX đặt trong cặp dấu $...$ (ví dụ: $y = x^3 - 3x + 1$, $\\vec{u} = (1; 2; -3)$, $\\frac{a}{b}$, $\\mathbb{R}$, $\\ge$, $\\in$).
- Tuyệt đối không để sót ký tự rác chữ Hán hay mã nhị phân lỗi.

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


class AIProviderService:
    """Service to send exam documents (text, images, PDFs) to external AI LLM providers."""

    def __init__(self):
        self.provider = detect_provider()
        self.api_key = settings.AI_API_KEY
        self.model = get_default_model(self.provider)
        self.base_url = settings.AI_BASE_URL
        self.timeout = 180.0

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

        data = json.loads(cleaned)
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

            std_q: Dict[str, Any] = {
                "id": qid,
                "code": code,
                "question_number": qid,
                "item_format": fmt,
                "cognitive_level": cog,
                "strand": q.get("strand", "Số, Đại số & Giải tích"),
                "topic": q.get("topic", "Khảo sát và vẽ đồ thị hàm số"),
                "lesson": q.get("lesson", "Khảo sát hàm số"),
                "learning_outcome_code": q.get("learning_outcome_code", "TOAN12.GT.01"),
                "problem_archetype": q.get("problem_archetype", "Dạng toán cơ bản"),
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
                std_q["short_answer_value"] = str(q.get("short_answer_value", ""))
                std_q["tolerance"] = float(q.get("tolerance", 0.0))

            standardized.append(std_q)
            total_conf += conf

        avg_conf = round(total_conf / max(1, len(standardized)), 1)
        return standardized, avg_conf


default_ai_provider_service = AIProviderService()
