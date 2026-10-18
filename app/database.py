from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# آدرس دیتابیس SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./walk_project.db"

# ساخت Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # فقط برای SQLite لازم است
)

# ساخت Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base برای مدل‌ها
Base = declarative_base()


# Dependency برای گرفتن Session در هر درخواست
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()