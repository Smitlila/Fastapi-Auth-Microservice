from fastapi import APIRouter, Depends
from .deps import get_current_user
from .schemas import MeOut
from .models import User

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user)):
    return MeOut(id=user.id, email=user.email, is_admin=user.is_admin, is_active=user.is_active)
