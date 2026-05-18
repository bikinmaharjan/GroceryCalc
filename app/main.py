from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, groups, lists, items, settlements, shopping, admin_stats, admin_groups, admin_users, admin_group_update, admin_group_members, change_password, item_management, settlements_calc, settlement_details, files, analytics, audit
import os
import bcrypt
from sqlalchemy.future import select
from .models import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Admin Bootstrapping
    from .database import SessionLocal
    async with SessionLocal() as session:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_display_name = os.getenv("ADMIN_DISPLAY_NAME", "Administrator")
        
        result = await session.execute(select(User).where(User.username == admin_username))
        if not result.scalar_one_or_none():
            hashed_pw = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                username=admin_username,
                password_hash=hashed_pw,
                display_name=admin_display_name,
                is_admin=True,
                must_change_password=True
            )
            session.add(admin_user)
            await session.commit()
            print(f"Admin user {admin_username} created successfully.")

app.include_router(auth.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(lists.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(item_management.router, prefix="/api")
app.include_router(settlements.router, prefix="/api")
app.include_router(settlements_calc.router, prefix="/api")
app.include_router(settlement_details.router, prefix="/api")
app.include_router(shopping.router, prefix="/api")
app.include_router(admin_stats.router, prefix="/api")
app.include_router(admin_groups.router, prefix="/api/admin")
app.include_router(admin_users.router, prefix="/api/admin")
app.include_router(admin_group_update.router, prefix="/api/admin")
app.include_router(admin_group_members.router, prefix="/api/admin")
app.include_router(audit.router, prefix="/api/admin")
app.include_router(change_password.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}


