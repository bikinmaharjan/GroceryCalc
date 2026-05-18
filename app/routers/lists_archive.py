from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.database import get_db
from app.models import List, Item, Settlement, GroupMember
from app.dependencies import get_current_user
from app.routers.settlement_details import get_settlement_details

router = APIRouter()

@router.post("/lists/{list_id}/archive")
async def archive_list(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    # 1. Check if settled
    settlement_data = await get_settlement_details(list_id, db)
    if settlement_data["transactions"]:
        raise HTTPException(status_code=400, detail="Cannot archive: debts remain unsettled")
    
    # 2. Archive current
    current_list = await db.get(List, list_id)
    if not current_list:
        raise HTTPException(status_code=404, detail="List not found")
        
    current_list.status = "archived"
    current_list.archived_at = datetime.utcnow()
    
    # 3. Create new list
    new_month = (current_list.month % 12) + 1
    new_year = current_list.year + (1 if new_month == 1 else 0)
    
    new_list = List(
        group_id=current_list.group_id,
        name=f"List {new_month}/{new_year}",
        month=new_month,
        year=new_year,
        status="active"
    )
    db.add(new_list)
    await db.commit()
    return {"status": "success", "new_list_id": new_list.id}
