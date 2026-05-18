from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import GroupMember
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/groups/{group_id}/members")
async def get_group_members(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GroupMember).where(GroupMember.group_id == group_id))
    return result.scalars().all()
