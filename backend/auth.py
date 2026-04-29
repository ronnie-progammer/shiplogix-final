"""Supabase-issued JWT verification for FastAPI.

Verifies HS256-signed Supabase access tokens against the project's JWT
secret (`SUPABASE_JWT_SECRET`). When the secret isn't configured we treat
the API as running in dev mode and emit a stub user so local hacking
without an auth provider still works. Production deployments MUST set
`SUPABASE_JWT_SECRET` and `AUTH_REQUIRED=1`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

JWT_ALGORITHM = "HS256"
JWT_AUDIENCE = "authenticated"

bearer = HTTPBearer(auto_error=False)


@dataclass
class AuthUser:
    user_id: str
    email: Optional[str]
    role: str
    tier: str = "free"
    is_anonymous: bool = False


def _jwt_secret() -> Optional[str]:
    return os.getenv("SUPABASE_JWT_SECRET")


def _auth_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "0") == "1"


def _decode(token: str) -> dict:
    secret = _jwt_secret()
    if not secret:
        raise JWTError("JWT secret not configured")
    return jwt.decode(
        token,
        secret,
        algorithms=[JWT_ALGORITHM],
        audience=JWT_AUDIENCE,
        options={"verify_aud": True},
    )


def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> AuthUser:
    """Returns the authenticated Supabase user for the current request.

    - If `AUTH_REQUIRED=1` and no/invalid token → 401
    - If `AUTH_REQUIRED=0` and no token → anonymous dev user
    - If a token IS supplied it is always validated and 401s on failure.
    """
    if creds is None or not creds.credentials:
        if _auth_required():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return AuthUser(
            user_id="dev-user",
            email="dev@local",
            role="authenticated",
            tier=os.getenv("DEV_DEFAULT_TIER", "pro"),
            is_anonymous=True,
        )

    try:
        payload = _decode(creds.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return AuthUser(
        user_id=str(payload.get("sub", "")),
        email=payload.get("email"),
        role=str(payload.get("role", "authenticated")),
        tier=str(payload.get("app_metadata", {}).get("tier", "free")),
    )


def require_tier(*allowed_tiers: str):
    """Dependency factory: require user.tier in `allowed_tiers`."""

    def _checker(user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if user.tier not in allowed_tiers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Tier '{user.tier}' not allowed; requires one of {list(allowed_tiers)}",
            )
        return user

    return _checker
