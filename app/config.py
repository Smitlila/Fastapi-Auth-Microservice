from pydantic import BaseModel
import os

class Settings(BaseModel):
    APP_NAME: str = "SecureAuthX"
    ENV: str = os.getenv("ENV", "dev")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/secureauthx"
    )

    ACCESS_TOKEN_TTL_MIN: int = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "15"))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "30"))

    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "secureauthx")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_SUPER_SECRET")
    JWT_ALG: str = os.getenv("JWT_ALG", "HS256")

settings = Settings()
