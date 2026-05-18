from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import ShoppingItem
from app.dependencies import get_current_user

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import ShoppingItem, Item
from app.dependencies import get_current_user
from app.schemas import ShoppingItemCreate, ShoppingItem as ShoppingItemSchema
from datetime import datetime

router = APIRouter()

@router.get("/shopping")
async def get_shopping_items(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShoppingItem).where(ShoppingItem.group_id == group_id))
    return result.scalars().all()

@router.post("/shopping", response_model=ShoppingItemSchema)
async def create_shopping_item(item: ShoppingItemCreate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    new_item = ShoppingItem(**item.dict(), created_by_id=current_user.id)
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

@router.put("/shopping/{item_id}", response_model=ShoppingItemSchema)
async def update_shopping_item(item_id: int, item_update: ShoppingItemCreate, db: AsyncSession = Depends(get_db)):
    item = await db.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_update.dict().items():
        setattr(item, key, value)
        
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/shopping/{item_id}")
async def delete_shopping_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(ShoppingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await db.delete(item)
    await db.commit()
    return {"status": "deleted"}

@router.post("/shopping/{item_id}/purchase")
async def purchase_shopping_item(item_id: int, cost: float, list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    shopping_item = await db.get(ShoppingItem, item_id)
    if not shopping_item:
        raise HTTPException(status_code=404, detail="Shopping item not found")
    
    # Create item
    new_item = Item(
        list_id=list_id,
        user_id=current_user.id,
        description=shopping_item.description,
        cost=cost,
        category=shopping_item.category,
        date_purchased=datetime.utcnow()
    )
    db.add(new_item)
    
    # Update shopping item
    shopping_item.is_purchased = True
    shopping_item.purchased_at = datetime.utcnow()
    shopping_item.purchased_by_id = current_user.id
    shopping_item.linked_item_id = new_item.id
    
    await db.commit()
    return {"status": "purchased", "item_id": new_item.id}
