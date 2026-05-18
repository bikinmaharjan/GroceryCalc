from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User
from app.database import DATABASE_URL
import bcrypt

# Adapt DATABASE_URL for sync engine
SYNC_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
engine = create_engine(SYNC_URL)
SessionLocal = sessionmaker(bind=engine)

def seed():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    if not db.query(User).filter_by(username="admin").first():
        hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        admin = User(
            username="admin",
            password_hash=hashed_pw.decode('utf-8'),
            display_name="Admin",
            is_admin=True,
            must_change_password=True
        )
        db.add(admin)
        db.commit()
    db.close()

if __name__ == "__main__":
    seed()
