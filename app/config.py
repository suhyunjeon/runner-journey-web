import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./marathon.db")

    def __init__(self) -> None:
        self.database_url = self._normalize_database_url(self.database_url)

    def _normalize_database_url(self, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://") and "+psycopg" not in value:
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


settings = Settings()
