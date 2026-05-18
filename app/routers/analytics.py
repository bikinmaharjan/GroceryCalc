from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database import get_db
from app.models import Item, List, User
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/analytics")
async def get_analytics(group_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Total spent in the group
    total_stmt = select(func.sum(Item.cost)).join(List).where(List.group_id == group_id)
    total_res = await db.execute(total_stmt)
    total_spent = total_res.scalar() or 0.0
    
    # 2. Total items added
    count_stmt = select(func.count(Item.id)).join(List).where(List.group_id == group_id)
    count_res = await db.execute(count_stmt)
    total_items = count_res.scalar() or 0
    
    # 3. Total spent per user (cumulative)
    user_stmt = (
        select(User.display_name, func.sum(Item.cost).label("total"))
        .join(Item)
        .join(List)
        .where(List.group_id == group_id)
        .group_by(User.display_name)
        .order_by(func.sum(Item.cost).desc())
    )
    user_res = await db.execute(user_stmt)
    user_totals = [{"user": row[0], "total": row[1]} for row in user_res.all()]
    
    # 4. Total spent per category
    cat_stmt = (
        select(Item.category, func.sum(Item.cost).label("total"), func.count(Item.id).label("count"))
        .join(List)
        .where(List.group_id == group_id)
        .group_by(Item.category)
    )
    cat_res = await db.execute(cat_stmt)
    category_totals = [{"category": row[0], "total": row[1], "count": row[2]} for row in cat_res.all()]
    
    # 5. Monthly spending trend
    trend_stmt = (
        select(func.strftime('%Y-%m', Item.created_at).label("month"), func.sum(Item.cost).label("total"))
        .join(List)
        .where(List.group_id == group_id)
        .group_by("month")
        .order_by("month")
    )
    trend_res = await db.execute(trend_stmt)
    monthly_trend = [{"month": row[0], "total": row[1]} for row in trend_res.all()]

    # 6. Top 10 items
    top_items_stmt = (
        select(Item.description, Item.cost)
        .join(List)
        .where(List.group_id == group_id)
        .order_by(Item.cost.desc())
        .limit(10)
    )
    top_items_res = await db.execute(top_items_stmt)
    top_items = [{"description": row[0], "cost": row[1]} for row in top_items_res.all()]
    
    return {
        "total_spent": total_spent,
        "total_items": total_items,
        "user_totals": user_totals,
        "category_totals": category_totals,
        "monthly_trend": monthly_trend,
        "top_items": top_items
    }

