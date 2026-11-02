"""
Pytest global test configuration and fixtures.
Ensures deterministic environment variables for AI provider across local and CI runner environments.
"""

import os
import pytest
from backend.services.ai_provider_service import default_ai_provider_service

# Match .github/workflows/ci.yml environment variables
os.environ.setdefault("AI_PROVIDER", "gemini")
os.environ.setdefault("AI_API_KEY", "")
os.environ.setdefault("PYTHONPATH", ".")


@pytest.fixture(autouse=True)
def reset_default_ai_provider_env(monkeypatch):
    """Ensure tests run with unconfigured AI provider unless test explicitly mocks or configures it."""
    # If the global service has an active live connection from a local .env, reset it to clean state
    orig_key = default_ai_provider_service.api_key
    orig_provider = default_ai_provider_service.provider
    orig_url = default_ai_provider_service.base_url

    # Check if this test specifically mocks default_ai_provider_service
    # If not, ensure clean defaults
    if not os.environ.get("USE_LIVE_AI"):
        monkeypatch.setattr(default_ai_provider_service, "api_key", os.environ.get("AI_API_KEY", ""))
        monkeypatch.setattr(default_ai_provider_service, "provider", os.environ.get("AI_PROVIDER", "gemini"))
        if default_ai_provider_service.provider == "gemini":
            monkeypatch.setattr(default_ai_provider_service, "base_url", "")

    yield
