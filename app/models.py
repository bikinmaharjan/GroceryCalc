from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    display_name = Column(String)
    is_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    lists = relationship("List", back_populates="group")
    members = relationship("GroupMember", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    group = relationship("Group", back_populates="members")
    user = relationship("User")

class List(Base):
    __tablename__ = "lists"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    name = Column(String)
    month = Column(Integer)
    year = Column(Integer)
    status = Column(String, default="active") # active|archived
    split_type = Column(String, default="equal") # equal|custom
    is_settling = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)
    group = relationship("Group", back_populates="lists")
    items = relationship("Item", back_populates="list")
    settlements = relationship("Settlement", back_populates="list")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    cost = Column(Float)
    category = Column(String)
    date_purchased = Column(DateTime)
    notes = Column(String, nullable=True)
    receipt_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    list = relationship("List", back_populates="items")
    user = relationship("User")

class Settlement(Base):
    __tablename__ = "settlements"
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    amount_owed = Column(Float)
    amount_paid = Column(Float, default=0.0)
    is_settled = Column(Boolean, default=False)
    settled_at = Column(DateTime, nullable=True)
    list = relationship("List", back_populates="settlements")
    user = relationship("User", foreign_keys=[user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

class ShoppingItem(Base):
    __tablename__ = "shopping_items"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    category = Column(String)
    notes = Column(String, nullable=True)
    quantity = Column(String)
    is_purchased = Column(Boolean, default=False)
    purchased_at = Column(DateTime, nullable=True)
    purchased_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    linked_item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    target_type = Column(String)
    target_id = Column(Integer)
    details = Column(String)
    ip = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
