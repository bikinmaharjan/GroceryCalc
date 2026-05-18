from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import User
from app.utils.jwt import create_access_token
import bcrypt
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        result = await db.execute(select(User).where(User.username == form_data.username))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
        if not user.password_hash:
            logger.warning(f"User {form_data.username} has no password hash")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
        if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"User {form_data.username} logged in successfully")
        return {
            "access_token": token, 
            "token_type": "bearer",
            "must_change_password": user.must_change_password,
            "is_admin": user.is_admin
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during login for {form_data.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
