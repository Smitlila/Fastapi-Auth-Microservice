from fastapi import APIRouter, Depends
from .deps import require_admin
from .models import User

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/dashboard")
def dashboard(_: User = Depends(require_admin)):
    return {
        "message": "Welcome, admin.",
        "metrics": {
            "users_total": "wire up a real metric later",
            "auth_events": "wire up later"
        }
    }
