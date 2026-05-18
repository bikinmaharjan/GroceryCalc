from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import AuditLog
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/audit-logs")
async def get_audit_logs(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(AuditLog))
    return result.scalars().all()
