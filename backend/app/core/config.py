from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os

class Settings(BaseSettings):
    # Server
    APP_ENV: str = Field(default="dev")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # PostgreSQL
    POSTGRES_DSN: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/ai_video")

    # Storage directories (relative to project root by default)
    STORAGE_ROOT: str = Field(default=os.path.join(os.getcwd(), "storage"))
    ASSETS_DIR: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "storage", "assets"))
    OUTPUTS_DIR: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "storage", "outputs"))
    SRT_DIR: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "storage", "srt"))
    COVERS_DIR: str = Field(default_factory=lambda: os.path.join(os.getcwd(), "storage", "covers"))

    # Providers (Volcengine)
    VOLCENGINE_API_BASE: str = Field(default="", description="Volcengine API Base, e.g., https://open.volcengineapi.com")
    VOLCENGINE_API_KEY: str = Field(default="", description="Volcengine API Key")
    VOLCENGINE_LLM_MODEL: str = Field(default="doubao-pro-4k", description="Default Volcengine (Doubao) LLM model")
    VOLCENGINE_TTS_VOICE: str = Field(default="zh_male_1", description="Default TTS voice id")
    VOLCENGINE_TTS_SPEED: float = Field(default=1.0, description="TTS speed")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://127.0.0.1:5173"])

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()