from pydantic_settings import BaseSettings, SettingsConfigDict
# Get the absolute path to the root directory


class Settings(BaseSettings):
	# Самые Важные настройки
	DEBUG: bool

	JWT_SECRET_KEY: str
	JWT_ALGORITHM: str

	BASE_URL: str
	ADMIN_PANEL_SECRET: str

	DB_URL: str
	TEST_DB_URL: str

	ADMIN_NAME: str
	ADMIN_EMAIL: str
	ADMIN_PASSWORD: str

	SMTP_HOST: str
	SMTP_PORT: int
	SMTP_USER: str
	SMTP_PASSWORD: str

	model_config = SettingsConfigDict(
		env_file='.dev.env',
		env_file_encoding='utf-8',
	)


settings = Settings()
