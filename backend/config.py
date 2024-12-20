from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the absolute path to the root directory

class Settings(BaseSettings):
    JWT_SECRET: str

    BASE_URL: str
    ADMIN_PANEL_SECRET: str

    DB_URL: str
    TEST_DB_URL: str

    ADMIN_NAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    DEBUG: bool

    HTTP_SECURE: bool
    model_config = SettingsConfigDict(
        env_file=".dev.env",
        env_file_encoding="utf-8",
    )


settings = Settings()
