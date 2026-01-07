"""
Global configuration for LangGraph Runner.

Uses pydantic-settings for validated configuration from environment variables.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Compute project root once for default paths
_PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # API Keys
    OPENAI_API_KEY: SecretStr

    # Model settings
    MODEL_ID: str = Field(
        default="gpt-5.2-2025-12-11", description="Primary model for synthesis/agent"
    )
    ROUTER_MODEL_ID: str = Field(
        default="gpt-5.2-2025-12-11", description="Model for classification/routing"
    )
    DEFAULT_TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0)

    # Embedding settings
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-large")

    # Retrieval settings
    RETRIEVAL_K: int = Field(default=10, ge=1, le=20)
    RETRIEVAL_MAX_DISTANCE: float | None = Field(
        default=None,
        description="Max distance threshold for retrieval (lower = more similar). None to disable.",
    )
    CHUNK_SIZE: int = Field(default=600, ge=100, le=4000)
    CHUNK_OVERLAP: int = Field(default=150, ge=0)

    # Path settings
    DATA_DIR: Path = Field(default=_PROJECT_ROOT / "data")
    PDF_DIR: Path = Field(default=_PROJECT_ROOT / "data" / "pdfs")
    CHROMA_DIR: Path = Field(default=_PROJECT_ROOT / "data" / "chroma_db")

    DEFAULT_GRAPH: str = Field(default="jpm_react_agent")

    # Checkpointer settings
    CHECKPOINTER_TYPE: Literal["memory", "postgres"] = Field(
        default="memory",
        description="Checkpointer type for conversation memory",
    )
    POSTGRES_URI: str | None = Field(
        default=None,
        description="PostgreSQL connection URI (required if CHECKPOINTER_TYPE=postgres)",
    )

    # Logging settings
    LOG_LEVEL: str = Field(default="info")
    JSON_LOGS: bool = Field(default=False)

    @field_validator("CHUNK_OVERLAP")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Ensure CHUNK_OVERLAP is less than CHUNK_SIZE."""
        chunk_size = info.data.get("CHUNK_SIZE", 1000)
        if v >= chunk_size:
            raise ValueError(
                f"CHUNK_OVERLAP ({v}) must be less than CHUNK_SIZE ({chunk_size})"
            )
        return v

    @model_validator(mode="after")
    def ensure_directories_exist(self) -> "Settings":
        """Create data directories if they don't exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PDF_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        return self


settings = Settings()
