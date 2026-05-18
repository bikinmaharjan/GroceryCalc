from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.models import Item, List, GroupMember, User

router = APIRouter()

@router.get("/lists/{list_id}/settlements/calculate")
async def calculate_settlements(list_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Total cost (only from non-admin users)
    stmt = select(func.sum(Item.cost)).join(User).where(Item.list_id == list_id, User.is_admin == False)
    result = await db.execute(stmt)
    total_cost = result.scalar() or 0
    
    # 2. Number of items (only from non-admin users)
    stmt = select(func.count(Item.id)).join(User).where(Item.list_id == list_id, User.is_admin == False)
    result = await db.execute(stmt)
    item_count = result.scalar() or 0
    
    # 3. Share per user (count non-admin users in group)
    list_obj = await db.get(List, list_id)
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
        
    stmt = select(func.count(GroupMember.id)).join(User).where(
        GroupMember.group_id == list_obj.group_id, 
        User.is_admin == False
    )
    result = await db.execute(stmt)
    member_count = result.scalar() or 1
    
    share_per_user = total_cost / member_count
    
    return {
        "total_cost": total_cost,
        "item_count": item_count,
        "share_per_user": share_per_user
    }

