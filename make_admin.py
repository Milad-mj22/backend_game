"""
اسکریپت ساخت ادمین
Usage: python make_admin.py <username>
"""
import sys
from app.database import SessionLocal
from app.models.user import User


def make_admin(username: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ کاربر '{username}' یافت نشد")
            return
        user.is_admin = True
        db.commit()
        print(f"✅ کاربر '{username}' با موفقیت ادمین شد")
    finally:
        db.close()


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Usage: python make_admin.py <username>")
    #     sys.exit(1)
    make_admin('test')