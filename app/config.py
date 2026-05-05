import os


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./marathon.db")


settings = Settings()
