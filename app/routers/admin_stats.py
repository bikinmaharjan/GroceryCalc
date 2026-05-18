from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.models import User, Group

router = APIRouter()

@router.get("/admin/stats/users")
async def get_user_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(User.id)))
    return {"count": result.scalar()}

@router.get("/admin/stats/groups")
async def get_group_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Group.id)))
    return {"count": result.scalar()}
