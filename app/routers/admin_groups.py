from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Group
from app.dependencies import get_current_user

router = APIRouter()

async def get_admin_user(current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user

@router.get("/groups", dependencies=[Depends(get_admin_user)])
async def get_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Group))
    return result.scalars().all()

@router.post("/groups", dependencies=[Depends(get_admin_user)])
async def create_group(name: str, db: AsyncSession = Depends(get_db)):
    group = Group(name=name)
    db.add(group)
    await db.commit()
    return group
