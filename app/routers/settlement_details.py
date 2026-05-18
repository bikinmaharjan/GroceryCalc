import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.models import Item, List, GroupMember, User, Settlement
from app.dependencies import get_current_user
from collections import defaultdict

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/lists/{list_id}/settlements/details")
async def get_settlement_details(list_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Get List and check if it exists
        list_obj = await db.get(List, list_id)
        if not list_obj:
            raise HTTPException(status_code=404, detail="List not found")
            
        # 2. Get items and users, but ONLY for non-admin users
        stmt = select(Item, User.username, User.display_name).join(User).where(Item.list_id == list_id, User.is_admin == False)
        result = await db.execute(stmt)
        rows = result.all()
        
        # 3. Get all non-admin members
        stmt_members = select(User.username, User.display_name).join(GroupMember).where(GroupMember.group_id == list_obj.group_id, User.is_admin == False)
        members_result = await db.execute(stmt_members)
        member_data = [{"username": r[0], "display_name": r[1]} for r in members_result.all()]
        member_count = len(member_data)
        
        total_cost = 0
        user_totals = defaultdict(float)
        user_items = defaultdict(list)
        
        # Initialize all members with 0
        for m in member_data:
            user_totals[m["username"]] = 0.0
        
        for item, username, display_name in rows:
            total_cost += item.cost
            user_totals[username] += item.cost
            user_items[username].append({"description": item.description, "cost": item.cost})
            
        share_per_user = total_cost / member_count if member_count > 0 else 0
        
        # Calculate balances and simple debts
        settlements = []
        creditors = []
        debtors = []
    
        for m in member_data:
            username = m["username"]
            paid = user_totals[username]
            balance = paid - share_per_user
            if abs(balance) < 0.01:
                balance = 0.0
                
            settlements.append({
                "user": m["display_name"],
                "total_paid": paid,
                "balance": balance,
                "items": user_items[username]
            })
            
            if balance > 0:
                creditors.append({"username": m["username"], "display_name": m["display_name"], "amount": balance})
            elif balance < 0:
                debtors.append({"username": m["username"], "display_name": m["display_name"], "amount": abs(balance)})
    
        # Simplify debts
        transactions = []
        d = 0
        c = 0
        
        # Fetch payments to determine status
        payment_stmt = select(Settlement.user_id, Settlement.to_user_id, func.sum(Settlement.amount_paid)).where(Settlement.list_id == list_id).group_by(Settlement.user_id, Settlement.to_user_id)
        payment_res = await db.execute(payment_stmt)
        payments_made = defaultdict(float)
        for row in payment_res.all():
            payments_made[(row[0], row[1])] = row[2] or 0.0
    
        # Map username to user_id for payment check
        user_id_map = {}
        stmt_users = select(User.id, User.username)
        user_res = await db.execute(stmt_users)
        for row in user_res.all():
            user_id_map[row[1]] = row[0]
    
        while d < len(debtors) and c < len(creditors):
            amount = min(debtors[d]["amount"], creditors[c]["amount"])
            
            from_user = debtors[d]["username"]
            to_user = creditors[c]["username"]
            
            # Determine status based on payments
            from_id = user_id_map.get(from_user)
            to_id = user_id_map.get(to_user)
            paid_amount = payments_made.get((from_id, to_id), 0.0)
            
            status = "pending"
            if paid_amount >= amount:
                status = "paid"
                
            transactions.append({
                "from": from_user,
                "from_name": debtors[d]["display_name"],
                "to": to_user,
                "to_name": creditors[c]["display_name"],
                "amount": amount,
                "status": status
            })
            debtors[d]["amount"] -= amount
            creditors[c]["amount"] -= amount
            if debtors[d]["amount"] < 0.01: d += 1
            if creditors[c]["amount"] < 0.01: c += 1
            
        return {
            "total_cost": total_cost,
            "member_count": member_count,
            "share_per_user": share_per_user,
            "settlements": settlements,
            "transactions": transactions
        }
    except Exception as e:
        logger.exception(f"Error getting settlement details for list {list_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

