from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
import bcrypt

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    display_name: str

async def get_admin_user(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

@router.get("/users", dependencies=[Depends(get_admin_user)])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/users", dependencies=[Depends(get_admin_user)])
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_pw = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
    user = User(
        username=user_data.username,
        display_name=user_data.display_name,
        password_hash=hashed_pw.decode('utf-8'),
        must_change_password=True
    )
    db.add(user)
    await db.commit()
    return user

@router.post("/users/{user_id}/reset-password", dependencies=[Depends(get_admin_user)])
async def reset_password(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_pw = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt())
    user.password_hash = hashed_pw.decode('utf-8')
    user.must_change_password = True
    
    await db.commit()
    return {"status": "success"}
