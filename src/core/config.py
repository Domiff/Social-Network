from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).parent.parent.parent


class AppSettings(BaseSettings):
    IS_DEBUG: bool = Field(default=True)
    IS_DOCKERIZED: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class DBSettings(AppSettings):
    SQLITE_URL: str = "sqlite+aiosqlite:///db.sqlite3"

    POSTGRES_DB: str = "POSTGRES_DB"
    POSTGRES_USER: str = "POSTGRES_USER"
    POSTGRES_PASSWORD: str = "POSTGRES_PASSWORD"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    def get_pg_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_post_init(self, __context) -> None:
        object.__setattr__(
            self,
            "DB_URL",
            self.get_pg_url() if self.IS_DOCKERIZED else self.SQLITE_URL,
        )


class CORSSettings(AppSettings):
    ALLOW_CREDENTIALS: bool
    ALLOW_ORIGINS: list[str]
    ALLOW_METHODS: list[str]


class AuthSettings(BaseSettings):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


class Settings(AppSettings):
    app: AppSettings = AppSettings()
    db: DBSettings = DBSettings()
    cors: CORSSettings = CORSSettings()
    auth: AuthSettings = AuthSettings()


settings = Settings()
