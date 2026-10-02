"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.database.session import get_db
from app.models.db_models import User, UserRole
from app.schemas.schemas import LoginRequest, UserCreate
from app.core.security import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(request: LoginRequest, db = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is deactivated")
    
    role_val = user.get("role", "VIEWER")
    if hasattr(role_val, "value"):
        role_val = role_val.value
    role_str = str(role_val)

    token = create_access_token({"sub": user.get("username"), "role": role_str})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.get("id", 1),
            "username": user.get("username"),
            "email": user.get("email"),
            "role": role_str,
            "is_active": user.get("is_active", True),
            "created_at": str(user.get("created_at")),
        }
    }


@router.post("/register")
def register(user_in: UserCreate, db = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        role=user_in.role.value if hasattr(user_in.role, "value") else str(user_in.role),
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    return {
        "id": new_user.get("id"),
        "username": new_user.get("username"),
        "email": new_user.get("email"),
        "role": str(new_user.get("role")),
        "is_active": True,
        "created_at": str(new_user.get("created_at")),
    }
