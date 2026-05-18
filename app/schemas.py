from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    display_name: str

class User(UserBase):
    id: int
    is_admin: bool
    must_change_password: bool

    class Config:
        from_attributes = True

class ShoppingItemCreate(BaseModel):
    group_id: int
    description: str
    category: str
    notes: Optional[str] = None
    quantity: str

class ShoppingItem(ShoppingItemCreate):
    id: int
    created_by_id: int
    is_purchased: bool
    purchased_at: Optional[datetime] = None
    purchased_by_id: Optional[int] = None
    linked_item_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
