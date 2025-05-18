from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/me")
def read_current_user(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username
    }
