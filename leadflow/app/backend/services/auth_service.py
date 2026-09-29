"""
LeadFlow — Authentication Service
JWT + bcrypt password hashing + RBAC
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt, JWTError

from app.backend.models.domain import (
    UserDB, UserCreate, UserPublic, UserRole,
    LoginRequest, AuthToken, TokenPayload
)
from app.database.repositories.user_repo import UserRepository
from app.config import settings

logger = logging.getLogger(__name__)

# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    UserRole.ADMIN: 4,
    UserRole.SALES_MANAGER: 3,
    UserRole.SALES_EXECUTIVE: 2,
    UserRole.SUPPORT: 1,
}


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def create_jwt_token(payload: TokenPayload) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
    data = {
        "sub": payload.user_id,
        "email": payload.email,
        "role": payload.role.value,
        "name": payload.name,
        "exp": expire,
    }
    return jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_jwt_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return TokenPayload(
            user_id=payload["sub"],
            email=payload["email"],
            role=UserRole(payload["role"]),
            name=payload["name"],
        )
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


class AuthService:
    """Authentication and authorization service."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def login(self, request: LoginRequest) -> Optional[AuthToken]:
        """Authenticate user and return token."""
        user = self.user_repo.find_by_email(request.email)
        if not user:
            logger.warning(f"Login failed — user not found: {request.email}")
            return None

        if not user.is_active:
            logger.warning(f"Login failed — user inactive: {request.email}")
            return None

        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed — wrong password: {request.email}")
            return None

        self.user_repo.update_last_login(user.id)  # type: ignore

        payload = TokenPayload(
            user_id=user.id,  # type: ignore
            email=user.email,
            role=user.role,
            name=user.name,
        )
        token = create_jwt_token(payload)

        public = UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=datetime.utcnow(),
        )
        logger.info(f"User logged in: {user.email} ({user.role})")
        return AuthToken(access_token=token, user=public)

    def create_user(self, data: UserCreate) -> UserDB:
        """Create a new user."""
        existing = self.user_repo.find_by_email(data.email)
        if existing:
            raise ValueError(f"User with email {data.email} already exists")

        user = UserDB(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            is_active=data.is_active,
        )
        return self.user_repo.create(user)

    def can_access(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if a role has at least the required permission level."""
        return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 999)

    def is_admin(self, role: UserRole) -> bool:
        return role == UserRole.ADMIN

    def can_manage_users(self, role: UserRole) -> bool:
        return role == UserRole.ADMIN

    def can_import_leads(self, role: UserRole) -> bool:
        return role in (UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_EXECUTIVE)

    def can_view_analytics(self, role: UserRole) -> bool:
        return role in (UserRole.ADMIN, UserRole.SALES_MANAGER)

    def can_upload_recordings(self, role: UserRole) -> bool:
        return role in (UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_EXECUTIVE)

    def can_modify_leads(self, role: UserRole) -> bool:
        return role in (UserRole.ADMIN, UserRole.SALES_MANAGER, UserRole.SALES_EXECUTIVE)
