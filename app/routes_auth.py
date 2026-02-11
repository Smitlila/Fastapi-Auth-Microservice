from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import get_db
from .models import User, RefreshToken
from .schemas import RegisterIn, LoginIn, TokenOut, RefreshIn, LogoutIn
from .security import hash_password, verify_password, make_access_token, make_refresh_token, decode_token
from .rate_limit import rate_limit

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", dependencies=[Depends(rate_limit("register", 10, 60))], response_model=TokenOut)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=body.email, password_hash=hash_password(body.password), is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)

    access = make_access_token(user.id, user.is_admin)
    refresh_token, jti, exp = make_refresh_token(user.id)

    db.add(RefreshToken(token_jti=jti, user_id=user.id, revoked=False, expires_at=exp))
    db.commit()

    return TokenOut(access_token=access, refresh_token=refresh_token)

@router.post("/login", dependencies=[Depends(rate_limit("login", 15, 60))], response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    access = make_access_token(user.id, user.is_admin)
    refresh_token, jti, exp = make_refresh_token(user.id)

    db.add(RefreshToken(token_jti=jti, user_id=user.id, revoked=False, expires_at=exp))
    db.commit()

    return TokenOut(access_token=access, refresh_token=refresh_token)

@router.post("/refresh", dependencies=[Depends(rate_limit("refresh", 30, 60))], response_model=TokenOut)
def refresh(body: RefreshIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if payload.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Wrong token type")

    jti = payload.get("jti")
    user_id = int(payload["sub"])

    rt = db.scalar(select(RefreshToken).where(RefreshToken.token_jti == jti))
    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Rotate refresh token: revoke old, mint new
    rt.revoked = True
    access = make_access_token(user.id, user.is_admin)
    new_refresh, new_jti, exp = make_refresh_token(user.id)

    db.add(RefreshToken(token_jti=new_jti, user_id=user.id, revoked=False, expires_at=exp))
    db.commit()

    return TokenOut(access_token=access, refresh_token=new_refresh)

@router.post("/logout", dependencies=[Depends(rate_limit("logout", 30, 60))])
def logout(body: LogoutIn, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        # If already invalid/expired, treat as logged out
        return {"ok": True}

    if payload.get("typ") != "refresh":
        return {"ok": True}

    jti = payload.get("jti")
    rt = db.scalar(select(RefreshToken).where(RefreshToken.token_jti == jti))
    if rt and not rt.revoked:
        rt.revoked = True
        db.commit()
    return {"ok": True}
