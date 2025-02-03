from fastapi import FastAPI, Request, HTTPException, Depends # type: ignore
from pydantic import BaseModel
import uvicorn  # type: ignore
from user_jwt import createToken, validateToken
from fastapi.responses import JSONResponse  # type: ignore
from fastapi.security import HTTPBearer  # type: ignore
from bd.database import Session, engine, Base
from models.user import User as UserModel
from fastapi.encoders import jsonable_encoder  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
import os

app = FastAPI(
    title='Flash4Devs API',
    description='https://github.com/iZergiodev/Flash4Devs',
    version= '0.0.1'
)

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BearerJWT(HTTPBearer):
    async def __call__(self, request:Request):
        auth = await super().__call__(request)
        data = validateToken(auth.credentials)
        if data['email'] != 'sergio@sergio.com':
            raise HTTPException(status_code=403, detail = 'Credenciales incorrectas')


class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    last_name: str

class UserLogin(BaseModel):
    email: str
    password: str


@app.get('/', tags=['inicio'])
def read_root():
    return {'Hello': 'world'}


@app.post('/api/register', tags=['Auth'])
def register(user: UserRegister):
    db = Session()
    newUser = UserModel(**user.dict())
    db.add(newUser)
    db.commit()
    return JSONResponse(status_code=201, content=jsonable_encoder({"message": "User created successfully"}))


@app.post('/api/login', tags=['Auth'])
def login(user: UserLogin):
    db = Session()
    try:
        data= db.query(UserModel).filter(UserModel.email == user.email).first()
        if not data:
            return JSONResponse(status_code=404, content={'message': 'Email o contraseña incorrecta'})
        if data.email == user.email and data.password == user.password:
            token: str = createToken(user.dict())
            return JSONResponse(status_code=200 ,content={'Token': token})
        raise HTTPException(status_code=401, detail="Email o contraseña incorrecta")
    finally:
        db.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)