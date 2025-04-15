from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from routers.auth import verify_token
from bd.database import get_db, Base, engine
from models.models import User
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://front-flash4-devs.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class UserCreate(BaseModel):
    id: str
    email: Optional[str] = None  # Alterado para aceitar null
    name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "user"
    profile_image: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: Optional[str]
    name: Optional[str]
    last_name: Optional[str]
    role: str
    profile_image: Optional[str]

class UserStats(BaseModel):
    good_answers: int
    bad_answers: int
    level: str
    rating_interview_front_react: str
    rating_interview_backend_python: str

class UploadResponse(BaseModel):
    url: str

# Endpoints
@app.get("/api/user/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    if payload["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@app.post("/api/user", response_model=dict)
async def create_user(user: UserCreate, payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    print("Recebido em /api/user:", user.dict())  # Log para depuração
    if payload["sub"] != user.id:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    existing_user = db.query(User).filter(User.id == user.id).first()
    if existing_user:
        existing_user.email = user.email or existing_user.email
        existing_user.name = user.name or existing_user.name
        existing_user.last_name = user.last_name or existing_user.last_name
        existing_user.profile_image = user.profile_image or existing_user.profile_image
        existing_user.role = user.role
    else:
        db_user = User(**user.dict())
        db.add(db_user)
    db.commit()
    return {"success": True}

@app.put("/api/user/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    user: UserCreate,
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    if payload["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    return {"success": True}

@app.get("/card/user-stats", response_model=UserStats)
async def get_user_stats(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    stats = {
        "good_answers": user.good_answers,
        "bad_answers": user.bad_answers,
        "level": user.level,
        "rating_interview_front_react": user.rating_interview_front_react,
        "rating_interview_backend_python": user.rating_interview_backend_python
    }
    return stats

@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(payload: dict = Depends(verify_token)):
    user_id = payload["sub"]
    # Lógica de upload (ex.: salvar no S3)
    return {"url": "https://exemplo.com/imagem.jpg"}

@app.get("/health")
async def health_check():
    return {"status": "OK"}