from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from bd.database import get_db
from routers.auth import verify_token
from schemas import UserCreate
from models import User  

router = APIRouter()

@router.post("/api/user")
def create_or_update_user(user_data: UserCreate, db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    user_id = token_data["sub"]

    user = db.query(User).filter(User.id == user_id).first()

    if user:
        # Atualiza os dados do usuário
        user.email = user_data.email
        user.name = user_data.name
        user.last_name = user_data.last_name
        user.profile_image = user_data.profile_image
    else:
        # Cria novo usuário
        user = User(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            last_name=user_data.last_name,
            profile_image=user_data.profile_image
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user
