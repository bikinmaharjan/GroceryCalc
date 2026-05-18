from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
import bcrypt

router = APIRouter()

class PasswordChange(BaseModel):
    new_password: str

@router.post("/change-password")
async def change_password(data: PasswordChange, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if data.new_password == "password123":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot use default password")
    
    hashed_pw = bcrypt.hashpw(data.new_password.encode('utf-8'), bcrypt.gensalt())
    current_user.password_hash = hashed_pw.decode('utf-8')
    current_user.must_change_password = False
    
    await db.commit()
    return {"status": "success"}
