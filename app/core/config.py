"""
Application configuration matching Career_Path .NET project database.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide settings loaded from environment / .env."""

    # ── AI backend (Groq) ────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_max_tokens: int = 2048

    # ── File upload constraints ──────────────────────────────
    allowed_extensions: set[str] = {".pdf", ".docx"}
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10 MB

    # ── Server ────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database (SQL Server - Career_Path) ──────────────────
    db_server: str = "db38948.public.databaseasp.net"
    db_name: str = "db38948"
    db_user: str = "db38948"
    db_password: str = "M?i98zJ=T!d4"
    db_driver: str = "ODBC Driver 17 for SQL Server"
    
    @property
    def database_url(self) -> str:
        """Build SQLAlchemy connection string for SQL Server."""
        return (
            f"mssql+pyodbc://{self.db_user}:{self.db_password}"
            f"@{self.db_server}/{self.db_name}"
            f"?driver={self.db_driver.replace(' ', '+')}"
            f"&Encrypt=no&MultipleActiveResultSets=True"
        )

    # ── pydantic-settings config ──────────────────────────────
    model_config = {"env_file": ".env", "extra": "ignore"}


# Singleton instance
settings = Settings()
