"""Authentication and user management API endpoints."""

from datetime import datetime, timezone
import hashlib
import secrets
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.schemas.auth import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyInfo,
    FavoriteCreateRequest,
    FavoriteResponse,
    OAuthSyncRequest,
    UserResponse,
)
from db.relational.models import User, UserAccount, UserApiKey, UserFavorite

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/oauth-sync", response_model=UserResponse, status_code=status.HTTP_200_OK)
def sync_oauth_user(payload: OAuthSyncRequest, db: Session = Depends(get_db_session)) -> User:
    """Synchronizes or provisions a user authenticated via an external OAuth provider (e.g. Google)."""
    # 1. Check if OAuth account already exists
    account_stmt = select(UserAccount).where(
        UserAccount.provider == payload.provider,
        UserAccount.provider_account_id == payload.provider_account_id,
    )
    account = db.scalars(account_stmt).first()

    if account is not None:
        user = db.get(User, account.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User account references non-existent user")
        # Update mutable fields if changed
        if payload.name and user.name != payload.name:
            user.name = payload.name
        if payload.avatar_url and user.avatar_url != payload.avatar_url:
            user.avatar_url = payload.avatar_url
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user

    # 2. Check if user with matching email already exists
    user_stmt = select(User).where(User.email == payload.email)
    user = db.scalars(user_stmt).first()

    if user is None:
        # Create new user
        user = User(
            email=payload.email,
            name=payload.name,
            avatar_url=payload.avatar_url,
            role="user",
            is_active=True,
        )
        db.add(user)
        db.flush()

    # Link OAuth account
    new_account = UserAccount(
        user_id=user.id,
        provider=payload.provider,
        provider_account_id=payload.provider_account_id,
    )
    db.add(new_account)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_profile(user_id: UUID, db: Session = Depends(get_db_session)) -> User:
    """Retrieves user profile information by ID."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/users/{user_id}/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(user_id: UUID, payload: ApiKeyCreateRequest, db: Session = Depends(get_db_session)) -> ApiKeyCreateResponse:
    """Generates a new secure API token for external API or MCP server access."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    random_secret = secrets.token_urlsafe(32)
    key_prefix = f"pk_live_{random_secret[:6]}"
    raw_key = f"pk_{random_secret}"
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    api_key = UserApiKey(
        user_id=user.id,
        name=payload.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return ApiKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        raw_key=raw_key,
        created_at=api_key.created_at,
    )


@router.get("/users/{user_id}/api-keys", response_model=list[ApiKeyInfo])
def list_api_keys(user_id: UUID, db: Session = Depends(get_db_session)) -> list[UserApiKey]:
    """Lists all API keys associated with a user."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = select(UserApiKey).where(UserApiKey.user_id == user_id).order_by(UserApiKey.created_at.desc())
    return list(db.scalars(stmt).all())


@router.post("/users/{user_id}/favorites", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(user_id: UUID, payload: FavoriteCreateRequest, db: Session = Depends(get_db_session)) -> UserFavorite:
    """Adds an entity to user favorites (e.g. bundestag_member or dossier)."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Idempotent check
    stmt = select(UserFavorite).where(
        UserFavorite.user_id == user_id,
        UserFavorite.entity_type == payload.entity_type,
        UserFavorite.entity_id == payload.entity_id,
    )
    existing = db.scalars(stmt).first()
    if existing is not None:
        return existing

    favorite = UserFavorite(
        user_id=user.id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


@router.get("/users/{user_id}/favorites", response_model=list[FavoriteResponse])
def list_favorites(user_id: UUID, db: Session = Depends(get_db_session)) -> list[UserFavorite]:
    """Lists all favorites saved by a user."""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    stmt = select(UserFavorite).where(UserFavorite.user_id == user_id).order_by(UserFavorite.created_at.desc())
    return list(db.scalars(stmt).all())


@router.delete("/users/{user_id}/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(user_id: UUID, favorite_id: UUID, db: Session = Depends(get_db_session)) -> None:
    """Removes an entity from user favorites."""
    stmt = select(UserFavorite).where(UserFavorite.id == favorite_id, UserFavorite.user_id == user_id)
    favorite = db.scalars(stmt).first()
    if favorite is not None:
        db.delete(favorite)
        db.commit()
