from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from app.database import get_db
from app.models import List, Item, User, GroupMember
from app.dependencies import get_current_user
from datetime import datetime
from collections import defaultdict

router = APIRouter()

@router.get("/lists/active")
async def get_active_lists(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(List).where(List.group_id == group_id, List.status == "active"))
    return result.scalars().all()

@router.get("/lists/archived")
async def get_archived_lists(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(List).where(List.group_id == group_id, List.status == "archived"))
    lists = result.scalars().all()
    
    archived_data = []
    for l in lists:
        # 1. Get all members of the group to calculate share
        member_stmt = select(User.display_name).join(GroupMember).where(GroupMember.group_id == l.group_id)
        member_res = await db.execute(member_stmt)
        members = member_res.scalars().all()
        member_count = len(members)
        
        # 2. Calculate total cost
        cost_res = await db.execute(select(func.sum(Item.cost)).where(Item.list_id == l.id))
        total_cost = cost_res.scalar() or 0.0
        share_per_user = total_cost / member_count if member_count > 0 else 0.0
        
        # 3. Calculate per-user totals
        user_res = await db.execute(
            select(User.display_name, func.sum(Item.cost))
            .join(Item)
            .where(Item.list_id == l.id)
            .group_by(User.display_name)
        )
        user_payments = {r[0]: (r[1] or 0.0) for r in user_res.all()}
        
        # 4. Calculate balances and simplify debts
        creditors = []
        debtors = []
        
        for m_name in members:
            paid = user_payments.get(m_name, 0.0)
            balance = paid - share_per_user
            if abs(balance) < 0.01: balance = 0.0
            
            if balance > 0:
                creditors.append({"user": m_name, "amount": balance})
            elif balance < 0:
                debtors.append({"user": m_name, "amount": abs(balance)})
        
        transactions = []
        d_idx, c_idx = 0, 0
        while d_idx < len(debtors) and c_idx < len(creditors):
            amount = min(debtors[d_idx]["amount"], creditors[c_idx]["amount"])
            transactions.append({
                "from": debtors[d_idx]["user"],
                "to": creditors[c_idx]["user"],
                "amount": amount
            })
            debtors[d_idx]["amount"] -= amount
            creditors[c_idx]["amount"] -= amount
            if debtors[d_idx]["amount"] < 0.01: d_idx += 1
            if creditors[c_idx]["amount"] < 0.01: c_idx += 1
            
        archived_data.append({
            "id": l.id,
            "name": l.name,
            "archived_at": l.archived_at,
            "total_cost": total_cost,
            "share_per_user": share_per_user,
            "user_payments": [{"user": u, "paid": p} for u, p in user_payments.items()],
            "transactions": transactions
        })
        
    return archived_data

@router.put("/lists/{list_id}")
async def rename_list(list_id: int, name: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
    
    list_obj.name = name
    await db.commit()
    return list_obj

@router.post("/lists")
async def create_list(group_id: int, name: str = None, db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()
    month = now.month
    year = now.year
    if not name:
        name = f"List {month}/{year}"
    new_list = List(group_id=group_id, name=name, month=month, year=year)
    db.add(new_list)
    await db.commit()
    return new_list

@router.post("/lists/{list_id}/settle")
async def start_settlement(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
    
    list_obj.is_settling = True
    await db.commit()
    return list_obj

@router.post("/lists/{list_id}/cancel-settlement")
async def cancel_settlement(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
    
    list_obj.is_settling = False
    await db.commit()
    return list_obj


@router.post("/lists/{list_id}/archive")
async def archive_list(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
    
    list_obj.status = "archived"
    list_obj.archived_at = datetime.utcnow()
    list_obj.is_settling = False
    await db.commit()
    return list_obj

@router.delete("/lists/{list_id}")
async def delete_list(list_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(List).where(List.id == list_id))
    list_obj = result.scalar_one_or_none()
    if not list_obj:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Verify user is a member of the group
    stmt = select(GroupMember).where(
        GroupMember.group_id == list_obj.group_id, 
        GroupMember.user_id == current_user.id
    )
    member_result = await db.execute(stmt)
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Delete associated items
    await db.execute(delete(Item).where(Item.list_id == list_id))
    
    # Delete the list
    await db.delete(list_obj)
    await db.commit()
    return {"status": "success"}
