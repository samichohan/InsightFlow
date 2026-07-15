"""api/auth.py — Authentication routes (signup, login, email verify, forgot password)."""

from unittest import result
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db, User
from app.core.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    create_email_token, create_reset_token,
    decode_token, get_current_user
)
from app.schemas.schemas import (
    SignupRequest, LoginRequest, TokenResponse,
    RefreshRequest, ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, UserResponse, UpdateProfileRequest
)
from app.core.logging_config import logger
from app.core.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Signup ────────────────────────────────────────────────────────────────────
@router.post("/signup", status_code=201)
async def signup(
    request: SignupRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):

    try:
        print(request)    
        print("Signup:", request.email, request.username)
        # Check email exists
        
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        

        # Check username exists
        result = await db.execute(
        select(User).where(User.username == request.username)
            )

        existing_username = result.scalar_one_or_none()

        print("existing_username =", existing_username)

        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

        
        user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            hashed_password=hash_password(request.password),
            is_active=True,
            is_verified=False,   # needs email verification
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Generate verification token
        token = create_email_token(user.id)

        await send_verification_email(
            user.email,
            token
        )

        logger.info(f"New user registered: {user.email}")

        # In production, send email with this token
        # For development, return token directly so user can verify immediately
        return {
            "message": "Account created successfully! Please verify your email.",
            "user_id": user.id,
                            # Remove in production, send via email
        }


    except Exception as e:
        print("ERROR:", repr(e))
        raise

# ── Verify Email ──────────────────────────────────────────────────────────────
@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if payload.get("type") != "email_verify":
        raise HTTPException(400, "Invalid verification token")

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully! You can now login."}


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")

    if not user.is_active:
        raise HTTPException(401, "Account is deactivated")
    
    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in."
        )


    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_verified": user.is_verified,
            "profile_pic": user.profile_pic,
        }
    )


# ── Refresh Token ─────────────────────────────────────────────────────────────
@router.post("/refresh")
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(400, "Invalid refresh token")

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "User not found")

    new_access = create_access_token({"sub": user.id})
    new_refresh = create_refresh_token({"sub": user.id})

    return {"access_token": new_access, "refresh_token": new_refresh}


# ── Forgot Password ───────────────────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if user:
        token = create_reset_token(user.id)
        # In production, send token via email
        # For dev, return it directly
        return {"message": "Password reset link sent!", "reset_token": token}

    return {"message": "If this email exists, a reset link has been sent."}


# ── Reset Password ────────────────────────────────────────────────────────────
@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(request.token)
    if payload.get("type") != "password_reset":
        raise HTTPException(400, "Invalid reset token")

    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    user.hashed_password = hash_password(request.new_password)
    await db.commit()
    return {"message": "Password reset successfully! You can now login."}


# ── Change Password ───────────────────────────────────────────────────────────
@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")

    current_user.hashed_password = hash_password(request.new_password)
    await db.commit()
    return {"message": "Password changed successfully!"}


# ── Profile ───────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me")
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if request.full_name is not None:
        current_user.full_name = request.full_name
    if request.username is not None:
        result = await db.execute(select(User).where(User.username == request.username))
        if result.scalar_one_or_none():
            raise HTTPException(400, "Username already taken")
        current_user.username = request.username
    await db.commit()
    return {"message": "Profile updated successfully"}


# ── Delete Account ────────────────────────────────────────────────────────────
@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(current_user)
    await db.commit()
    return {"message": "Account deleted successfully"}
