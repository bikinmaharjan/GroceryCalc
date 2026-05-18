from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Settlement, List, User
from pydantic import BaseModel

router = APIRouter()

class Payment(BaseModel):
    from_username: str
    to_username: str
    amount: float

@router.post("/lists/{list_id}/settlements/mark-paid")
async def mark_paid(list_id: int, payment: Payment, db: AsyncSession = Depends(get_db)):
    # Resolve usernames to IDs
    from_res = await db.execute(select(User.id).where(User.username == payment.from_username))
    from_user = from_res.scalar_one_or_none()
    
    to_res = await db.execute(select(User.id).where(User.username == payment.to_username))
    to_user = to_res.scalar_one_or_none()
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")

    settlement = Settlement(
        list_id=list_id,
        user_id=from_user,
        to_user_id=to_user,
        amount_paid=payment.amount,
        is_settled=True
    )
    db.add(settlement)
    await db.commit()
    return {"status": "success"}
