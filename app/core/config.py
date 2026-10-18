from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # اطلاعات JWT
    SECRET_KEY: str = "یک-کلید-مخفی-بسیار-قوی-که-در-محیط-واقعی-باید-تغییر-کند"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 روز

    # اطلاعات دیتابیس
    DATABASE_URL: str = "sqlite:///./walk_project.db"

    class Config:
        env_file = ".env"


settings = Settings()