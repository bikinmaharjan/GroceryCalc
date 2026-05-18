from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Item, List
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/items")
async def get_items(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify user has access to this list's group
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
        
    # Filter items by current user
    result = await db.execute(select(Item).where(Item.list_id == list_id, Item.user_id == current_user.id))
    return result.scalars().all()

@router.post("/items")
async def create_item(list_id: int, description: str, cost: float, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # Verify user belongs to the group of the list
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    
    if not list_obj:
        raise HTTPException(status_code=400, detail="List not found")
        
    if list_obj.is_settling:
        raise HTTPException(status_code=403, detail="List is currently settling; items cannot be added")
        
    item = Item(list_id=list_id, user_id=current_user.id, description=description, cost=cost)
    db.add(item)
    await db.commit()
    return item
