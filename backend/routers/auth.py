from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_active_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "TEACHER"  # TEACHER, STUDENT, ADMIN

class LoginRequest(BaseModel):
    email: str
    password: str

class OAuthLoginRequest(BaseModel):
    email: str
    full_name: str
    oauth_provider: str  # google, github
    oauth_id: Optional[str] = None
    avatar_url: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role or "TEACHER",
        oauth_provider="local"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider
        }
    }

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider
        }
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "avatar_url": current_user.avatar_url,
        "oauth_provider": current_user.oauth_provider
    }

@router.post("/oauth/google", response_model=TokenResponse)
def oauth_google(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            role="TEACHER",
            oauth_provider="google",
            oauth_id=payload.oauth_id,
            avatar_url=payload.avatar_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if payload.avatar_url:
            user.avatar_url = payload.avatar_url
        if payload.full_name:
            user.full_name = payload.full_name
        db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider
        }
    }

@router.post("/oauth/github", response_model=TokenResponse)
def oauth_github(payload: OAuthLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            role="TEACHER",
            oauth_provider="github",
            oauth_id=payload.oauth_id,
            avatar_url=payload.avatar_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if payload.avatar_url:
            user.avatar_url = payload.avatar_url
        if payload.full_name:
            user.full_name = payload.full_name
        db.commit()

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "oauth_provider": user.oauth_provider
        }
    }

@router.post("/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}
