"""
schemas/schemas.py — All Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    full_name: Optional[str] = None
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


# ── User ─────────────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_verified: bool
    profile_pic: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=30)


# ── Project ───────────────────────────────────────────────────────────────────
class ProjectResponse(BaseModel):
    id: str
    name: str
    filename: str
    file_type: str
    file_size_mb: Optional[float]
    total_rows: Optional[int]
    total_columns: Optional[int]
    quality_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Chat ─────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    project_id: str


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    agent_used: Optional[str]
    chart_data: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analysis ──────────────────────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    project_id: str
    date_column: str
    value_column: str
    periods_ahead: int = Field(default=3, ge=1, le=12)
    use_polynomial: bool = False


class ReportRequest(BaseModel):
    project_id: str
    format: str = Field(default="pdf", pattern="^(pdf|docx|pptx)$")


class CleanRequest(BaseModel):
    project_id: str
    strategy: str = Field(default="auto", pattern="^(auto|drop)$")


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardStatsResponse(BaseModel):
    total_projects: int
    total_reports: int
    total_chats: int
    last_login: Optional[datetime]
    recent_projects: List[ProjectResponse]
