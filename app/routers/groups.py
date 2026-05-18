from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Group, GroupMember
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/my-groups")
async def get_my_groups(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(Group).join(GroupMember).where(GroupMember.user_id == current_user.id))
    return result.scalars().all()
