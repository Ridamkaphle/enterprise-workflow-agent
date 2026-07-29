"""Environment-based application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_env: str = "development"
    log_level: str = "INFO"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/workflow_agent"

    # MCP
    mcp_server_url: str = "http://localhost:8080"

    # External integrations (OAuth tokens / API keys via env)
    slack_bot_token: str | None = None
    github_token: str | None = None
    jira_api_token: str | None = None
    gmail_credentials_path: str | None = None


settings = Settings()
