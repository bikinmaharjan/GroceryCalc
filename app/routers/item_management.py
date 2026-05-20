from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel
from app.database import get_db
from app.models import Item, List
from app.dependencies import get_current_user

router = APIRouter()

class ItemUpdate(BaseModel):
    description: str
    cost: float
    category: str | None = None

@router.put("/items/{item_id}")
async def update_item(item_id: int, data: ItemUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Check if list is settling
    result = await db.execute(select(List).where(List.id == item.list_id))
    list_obj = result.scalar_one_or_none()
    if list_obj and list_obj.is_settling:
        raise HTTPException(status_code=403, detail="List is currently settling; items cannot be updated")
    
    item.description = data.description
    item.cost = data.cost
    if data.category is not None:
        item.category = data.category
    await db.commit()
    return item

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    item = await db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Check if list is settling
    result = await db.execute(select(List).where(List.id == item.list_id))
    list_obj = result.scalar_one_or_none()
    if list_obj and list_obj.is_settling:
        raise HTTPException(status_code=403, detail="List is currently settling; items cannot be deleted")
    
    await db.delete(item)
    await db.commit()
    return {"status": "success"}
