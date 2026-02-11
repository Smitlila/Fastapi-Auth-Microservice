from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
import secrets
import hashlib

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def _now() -> datetime:
    return datetime.now(timezone.utc)

def make_access_token(user_id: int, is_admin: bool) -> str:
    exp = _now() + timedelta(minutes=settings.ACCESS_TOKEN_TTL_MIN)
    payload = {
        "sub": str(user_id),
        "adm": bool(is_admin),
        "iss": settings.JWT_ISSUER,
        "typ": "access",
        "exp": exp,
        "iat": _now(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def make_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """
    Returns (token, jti, expires_at)
    """
    jti_raw = secrets.token_urlsafe(32)
    jti = hashlib.sha256(jti_raw.encode("utf-8")).hexdigest()
    exp = _now() + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)

    payload = {
        "sub": str(user_id),
        "iss": settings.JWT_ISSUER,
        "typ": "refresh",
        "jti": jti,
        "exp": exp,
        "iat": _now(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, jti, exp

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALG],
        issuer=settings.JWT_ISSUER,
        options={"require": ["exp", "iss", "typ", "sub"]},
    )
