from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        if db.scalar(select(User).where(User.email == payload.email)):
            raise HTTPException(status_code=409, detail="Email is already registered")

        role = db.scalar(select(Role).where(Role.name == "researcher"))
        if role is None:
            role = Role(name="researcher", description="Default research user", is_system=True)
            db.add(role)
            db.flush()

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception(
            "database_error path=/api/v1/auth/register"
        )
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable. Check the backend database connection.",
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.scalar(select(User).where(User.email == payload.email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            expires_in=settings.access_token_expire_minutes * 60,
        )
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception(
            "database_error path=/api/v1/auth/login"
        )
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable. Check the backend database connection.",
        ) from exc
