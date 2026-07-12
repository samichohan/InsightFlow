"""
db/database.py — PostgreSQL async connection + SQLAlchemy models.

Tables:
  users          → login/signup data
  projects       → each uploaded dataset = one project
  chat_messages  → full conversation history per project
  reports        → generated report metadata
  activity_logs  → tracks user actions (login, upload, etc.)
"""
import ssl

from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text,
    Integer, Float, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings


# ── Engine ───────────────────────────────────────────────────────────────────
ssl_context = ssl.create_default_context()
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "ssl": ssl_context
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# ── Base ─────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Models ───────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id          = Column(String, primary_key=True)          # UUID
    email       = Column(String, unique=True, nullable=False, index=True)
    username    = Column(String, unique=True, nullable=False)
    full_name   = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active   = Column(Boolean, default=False)            # False until email verified
    is_verified = Column(Boolean, default=False)
    profile_pic = Column(String, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    last_login  = Column(DateTime, nullable=True)

    projects    = relationship("Project", back_populates="user", cascade="all, delete")
    logs        = relationship("ActivityLog", back_populates="user", cascade="all, delete")


class Project(Base):
    __tablename__ = "projects"

    id              = Column(String, primary_key=True)
    user_id         = Column(String, ForeignKey("users.id"), nullable=False)
    name            = Column(String, nullable=False)
    filename        = Column(String, nullable=False)
    file_path       = Column(String, nullable=False)
    file_type       = Column(String, nullable=False)        # csv / xlsx / pdf ...
    file_size_mb    = Column(Float, nullable=True)
    total_rows      = Column(Integer, nullable=True)
    total_columns   = Column(Integer, nullable=True)
    quality_score   = Column(Float, nullable=True)
    column_metadata = Column(JSON, nullable=True)           # column names + dtypes
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user         = relationship("User", back_populates="projects")
    messages     = relationship("ChatMessage", back_populates="project", cascade="all, delete")
    reports      = relationship("Report", back_populates="project", cascade="all, delete")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id          = Column(String, primary_key=True)
    project_id  = Column(String, ForeignKey("projects.id"), nullable=False)
    role        = Column(String, nullable=False)            # "user" | "assistant"
    content     = Column(Text, nullable=False)
    agent_used  = Column(String, nullable=True)             # which agent answered
    chart_data  = Column(JSON, nullable=True)               # plotly json if chart generated
    created_at  = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="messages")


class Report(Base):
    __tablename__ = "reports"

    id          = Column(String, primary_key=True)
    project_id  = Column(String, ForeignKey("projects.id"), nullable=False)
    format      = Column(String, nullable=False)            # pdf / docx / pptx
    file_path   = Column(String, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="reports")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False)
    action      = Column(String, nullable=False)            # "upload", "chat", "report"...
    detail      = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logs")


# ── Session Dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables on startup (use Alembic for production migrations)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
