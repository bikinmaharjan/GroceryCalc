import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.database import DATABASE_URL

SYNC_URL = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")
engine = create_engine(SYNC_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

user = db.query(User).filter_by(username="admin").first()
if user:
    print(f"User found: {user.username}")
    print(f"Stored hash: {user.password_hash}")
    # Try to verify
    is_valid = bcrypt.checkpw("admin123".encode('utf-8'), user.password_hash.encode('utf-8'))
    print(f"Verification: {is_valid}")
else:
    print("User not found")
db.close()
