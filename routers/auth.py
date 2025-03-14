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

class UpdateUserRequest(BaseModel):
    email: str | None = None
    password: str | None = None
    name: str | None = None
    last_name: str | None = None
    role: str | None = None
    level: str | None = None
    linkedin: str | None = None
    github: str | None = None
    x: str | None = None

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

@router.get('/users', summary="Get all users")
def get_user_by_id( db: db_dependency):
     user_from_database = db.query(UserModel).all()
     return user_from_database

@router.get('/user/{user_id}', summary="Get a User by ID")
def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int):
     if user is None:
          raise HTTPException(status_code=401, detail='Authentification failed')
     user_from_database = db.query(UserModel).filter(UserModel.id == user_id).first()
     return user_from_database

@router.delete('/user/{user_id}', summary="Delete user by ID")
def delete_user_by_id(user: user_dependency, db: db_dependency, user_id: int):
     if user is None:
          raise HTTPException(status_code=401, detail='User not found')
     current_user = db.query(UserModel).filter(UserModel.id == user['id']).first()
     if current_user.role != 'admin' and current_user.id != user_id:
          raise HTTPException(status_code=403, detail='Not authorized to edit this user')
     user_from_database = db.query(UserModel).filter(UserModel.id == user_id).first()
     db.delete(user_from_database)
     db.commit()
     return {"message": "User deleted successfully", "user_id": user_id}

@router.put('/user/{user_id}', summary="Edit user")
def update_user(
    user: user_dependency,
    db: db_dependency,
    user_id: int,
    update_user_request: UpdateUserRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    # Buscar el usuario en la base de datos
    user_to_update = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail='User not found')

    # Verificar permisos: solo un admin o el propio usuario puede editar
    current_user = db.query(UserModel).filter(UserModel.id == user['id']).first()
    if current_user.role != 'admin' and current_user.id != user_id:
        raise HTTPException(status_code=403, detail='Not authorized to edit this user')

    # Actualizar solo los campos proporcionados en la solicitud
    if update_user_request.email is not None:
        # Verificar si el nuevo email ya está en uso por otro usuario
        existing_user = db.query(UserModel).filter(UserModel.email == update_user_request.email, UserModel.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail='Email already registered')
        user_to_update.email = update_user_request.email

    if update_user_request.password is not None:
        user_to_update.hashed_password = bcrypt_context.hash(update_user_request.password)

    if update_user_request.name is not None:
        user_to_update.name = update_user_request.name

    if update_user_request.last_name is not None:
        user_to_update.last_name = update_user_request.last_name

    if update_user_request.role is not None:
        # Opcional: restringir la edición del rol solo a admins
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail='Only admins can change roles')
        user_to_update.role = update_user_request.role

    if update_user_request.level is not None:
        user_to_update.level = update_user_request.level

    if update_user_request.linkedin is not None:
        user_to_update.linkedin = update_user_request.linkedin

    if update_user_request.github is not None:
        user_to_update.github = update_user_request.github

    if update_user_request.x is not None:
        user_to_update.x = update_user_request.x

    # Guardar los cambios en la base de datos
    db.commit()
    db.refresh(user_to_update)  # Refrescar el objeto para obtener los datos actualizados

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"message": "User updated successfully", "user": user_to_update})
    )


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