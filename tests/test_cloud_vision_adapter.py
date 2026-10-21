"""Unit tests for AI Cloud Vision Adapter (Task AI-08)
Tests online provider integration (Gemini / OpenAI / Claude) and fallback behavior.
"""

import pytest
from backend.services.ai_provider_service import (
    AIProviderService,
    default_ai_provider_service,
    detect_provider,
    get_default_model,
    SYSTEM_PROMPT
)


def test_ai_provider_service_initialization():
    """Checks provider service defaults and configuration check."""
    from backend.config import settings
    orig_timeout = settings.AI_TIMEOUT
    try:
        settings.AI_TIMEOUT = 180.0
        service = AIProviderService()
        # Without API keys in test environment, is_configured should return False
        assert isinstance(service.is_configured(), bool)
        assert service.provider in ("gemini", "openai", "claude", "openrouter", "custom")
        assert service.timeout == 180.0
    finally:
        settings.AI_TIMEOUT = orig_timeout


def test_provider_detection_and_default_model():
    """Verifies default model lookup and provider detection."""
    from backend.config import settings
    orig_model = settings.AI_MODEL
    try:
        settings.AI_MODEL = ""
        assert get_default_model("gemini") == "gemini-1.5-flash"
        assert get_default_model("openai") == "gpt-4o"
        assert get_default_model("anthropic") == "claude-3-5-sonnet-20241022"
    finally:
        settings.AI_MODEL = orig_model


def test_system_prompt_contains_2025_standards():
    """Ensures AI prompt strictly guides Circular 32 and Decision 764."""
    assert "Thông tư 32/2018/TT-BGDĐT" in SYSTEM_PROMPT
    assert "Quyết định 764/QĐ-BGDĐT" in SYSTEM_PROMPT
    assert "SINGLE_CHOICE" in SYSTEM_PROMPT
    assert "TRUE_FALSE_GROUP" in SYSTEM_PROMPT
    assert "SHORT_ANSWER" in SYSTEM_PROMPT
    assert "LaTeX" in SYSTEM_PROMPT or "KaTeX" in SYSTEM_PROMPT


def test_ai_provider_parse_json_result():
    """Tests parsing and sanitization of LLM JSON response."""
    raw_markdown = '''```json
    {
      "exam_metadata": {"title": "Đề Khảo sát 2025"},
      "questions": [
        {
          "id": 1,
          "item_format": "SINGLE_CHOICE",
          "stem": "Cho hàm số $y = f(x)$.",
          "options": [
            {"label": "A", "content": "1", "is_correct": true},
            {"label": "B", "content": "2", "is_correct": false}
          ],
          "cognitive_level": "RECOGNITION"
        },
        {
          "id": 2,
          "item_format": "TRUE_FALSE_GROUP",
          "stem": "Cho tứ diện ABCD.",
          "sub_statements": [
            {"label": "a", "content": "Mệnh đề A", "is_true": true},
            {"label": "b", "content": "Mệnh đề B", "is_true": false}
          ],
          "cognitive_level": "COMPREHENSION"
        }
      ]
    }
    ```'''
    questions, avg_conf = default_ai_provider_service._parse_json_result(raw_markdown)
    assert len(questions) == 2
    assert questions[0]["item_format"] == "SINGLE_CHOICE"
    assert questions[0]["options"][0]["is_correct"] is True
    assert questions[1]["item_format"] == "TRUE_FALSE_GROUP"
    assert len(questions[1]["sub_statements"]) == 2
    assert avg_conf >= 80.0


def test_ai_provider_digitize_exam_when_unconfigured():
    """Verifies that digitize_exam raises ValueError with helpful message when unconfigured."""
    import pytest
    service = AIProviderService()
    service.api_key = ""
    with pytest.raises(ValueError, match="Chưa cấu hình API Key"):
        service.digitize_exam("dummy_path.pdf")
