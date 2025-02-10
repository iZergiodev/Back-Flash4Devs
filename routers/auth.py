import os
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from models.models import User as UserModel
from bd.database import SessionLocal
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload

load_dotenv()

router = APIRouter(
     prefix='/api',
     tags=['Auth']
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/login')

class CreateUserRequest(BaseModel):
    email: str
    password: str
    name: str
    last_name: str

class Token(BaseModel):
     access_token: str
     token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(email: str, password: str, db):
     user = db.query(UserModel).filter(UserModel.email == email).first()
     if not user:
          return False
     if not bcrypt_context.verify(password, user.hashed_password):
          return False
     return user

def create_token(id: int, expires_delta: timedelta):
     encode = {'id': id}
     expires = datetime.now(timezone.utc) + expires_delta
     encode.update({'exp': expires})
     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
     try:
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
          id: int = payload.get('id')
          if id is None:
               raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
          return {'id': id}
     except JWTError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
          
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post('/register', status_code=status.HTTP_201_CREATED, summary="Register a User")
def register(db: db_dependency ,create_user_request: CreateUserRequest):

    existing_user = db.query(UserModel).filter(UserModel.email == create_user_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )

    newUser = UserModel(
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        name=create_user_request.name,
        last_name=create_user_request.last_name
    )
    db.add(newUser)
    db.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder({"message": "User created successfully"}))



class LoginUserRequest(BaseModel):
    email: str
    password: str

     
@router.post('/login', response_model=Token, summary="Login User")
def login(form_data:LoginUserRequest ,db: db_dependency):
        user = authenticate_user(form_data.email, form_data.password, db)
        if not user:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        token = create_token(user.id, timedelta(minutes=10080) )
        return {'access_token': token, 'token_type': 'bearer'}

@router.get('/user/{user_id}', summary="Get a User by ID")
def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int):
     if user is None:
          raise HTTPException(status_code=401, detail='Authentification failed')
     user_from_database = db.query(UserModel).filter(UserModel.id == user_id).first()
     return user_from_database


cloudinary.config(
     cloud_name="dxkrekuq7",
     api_key="162572424771848",
     api_secret="_GtgsZGFvtz08uJcj-LdK5pLIWU"
)

@router.post('/upload/')
async def upload_profile_image(
    user: user_dependency,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        result = upload(file.file)
        image_url = result["secure_url"]

        user_from_db = db.query(UserModel).filter(UserModel.id == user["id"]).first()
        if not user_from_db:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        user_from_db.profile_image = image_url
        db.commit()

        return {"url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))