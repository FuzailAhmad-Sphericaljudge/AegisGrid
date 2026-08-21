from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Boolean
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    first_name = Column(String(100), default="")
    last_name = Column(String(100), default="")
    profile_bio = Column(Text, default="")
    profile_phone = Column(String(20), default="")
    avatar = Column(Text, default="")  # base64 encoded image
    profile_complete = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(80), nullable=False)
    asset_type = Column(String(80), nullable=False)
    criticality = Column(Integer, default=50)
    vulnerability = Column(Integer, default=50)
    exposure = Column(Integer, default=50)
    behavioral = Column(Integer, default=0)
    status = Column(String(40), default="healthy")
    description = Column(Text, default="")

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    protocol = Column(String(80), default="TCP")
    trust_level = Column(Integer, default=50)

class Threat(Base):
    __tablename__ = "threats"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    severity = Column(String(30), default="medium")
    score = Column(Float, default=50)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    status = Column(String(40), default="active")
    source = Column(String(120), default="simulated telemetry")
    details = Column(Text, default="")

class Recovery(Base):
    __tablename__ = "recovery"
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"))
    service = Column(String(255), nullable=False)
    progress = Column(Integer, default=0)
    status = Column(String(40), default="in_progress")
    eta_minutes = Column(Integer, default=30)

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(50), default="desktop")
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, default="")
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_trusted = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(80), default="")
    resource_id = Column(Integer, default=0)
    status = Column(String(20), default="success")
    ip_address = Column(String(45), default="")
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    notification_type = Column(String(50), default="info")
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    priority = Column(String(20), default="normal")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
