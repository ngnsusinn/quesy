import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")

# Storage Directories
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
ASSETS_DIR = STORAGE_DIR / "assets"
EXPORTS_DIR = STORAGE_DIR / "exports"

# Ensure all critical storage paths exist
for _path in [STORAGE_DIR, UPLOADS_DIR, ASSETS_DIR, EXPORTS_DIR]:
    _path.mkdir(parents=True, exist_ok=True)


class Settings:
    """Application Configuration Settings for Quesy."""

    # Application Information
    APP_NAME: str = "Quesy"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DESCRIPTION: str = (
        "AI-Powered Exam Management & Standardization Platform conforming to "
        "Vietnam MoET Circular 32/2018/TT-BGDDT and Decision 764/QD-BGDDT (2025 format)."
    )

    # Environment & Security
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "quesy-super-secret-key-production-change-required"
    )

    # Database Configuration
    # Defaults to local SQLite in storage/ directory, PostgreSQL fully compatible
    DEFAULT_SQLITE_PATH: Path = STORAGE_DIR / "quesy.db"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
    )

    # Storage Paths
    BASE_DIR: Path = BASE_DIR
    STORAGE_DIR: Path = STORAGE_DIR
    UPLOADS_DIR: Path = UPLOADS_DIR
    ASSETS_DIR: Path = ASSETS_DIR
    EXPORTS_DIR: Path = EXPORTS_DIR

    # Uploads & Assets Limits
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    ALLOWED_EXTENSIONS: List[str] = [
        ".docx",
        ".doc",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
    ]

    # AI & Vector Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_DIM: int = 1536
    SIMILARITY_WARN_THRESHOLD: float = 0.80
    SIMILARITY_BLOCK_THRESHOLD: float = 0.90

    # Online AI Provider Configuration (Loaded from .env)
    # Supported: openai | gemini | anthropic | openrouter | custom
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "").lower()
    AI_API_KEY: str = (
        os.getenv("AI_API_KEY", "")
        or os.getenv("GEMINI_API_KEY", "")
        or os.getenv("OPENAI_API_KEY", "")
        or os.getenv("ANTHROPIC_API_KEY", "")
        or os.getenv("OPENROUTER_API_KEY", "")
    )
    AI_MODEL: str = os.getenv("AI_MODEL", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "")
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "8192"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.1"))
    AI_TIMEOUT: float = float(os.getenv("AI_TIMEOUT", "300.0"))

    # MathJax LaTeX Engine settings
    USE_MATHJAX: bool = os.getenv("USE_MATHJAX", "true").lower() in ("true", "1", "yes")

    # Decision 764/QĐ-BGDĐT Stepwise Scoring Rule for True/False 4-Statement Questions
    # 1 correct = 0.1, 2 correct = 0.25, 3 correct = 0.5, 4 correct = 1.0 (per 1.0 point scale)
    TF_STEPWISE_POINTS: dict = {
        1: 0.10,
        2: 0.25,
        3: 0.50,
        4: 1.00,
    }


settings = Settings()
