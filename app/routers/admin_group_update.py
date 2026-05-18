from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel
from app.database import get_db
from app.models import Group, GroupMember
from app.dependencies import get_current_user

router = APIRouter()

class GroupUpdate(BaseModel):
    name: str
    user_ids: list[int]

async def get_admin_user(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

@router.put("/groups/{group_id}", dependencies=[Depends(get_admin_user)])
async def update_group(group_id: int, data: GroupUpdate, db: AsyncSession = Depends(get_db)):
    group = await db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.name = data.name
    
    # Update members
    await db.execute(delete(GroupMember).where(GroupMember.group_id == group_id))
    for uid in data.user_ids:
        db.add(GroupMember(group_id=group_id, user_id=uid))
        
    await db.commit()
    return group
