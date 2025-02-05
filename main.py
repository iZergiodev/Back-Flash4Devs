from fastapi import FastAPI, Request, HTTPException # type: ignore
import uvicorn  # type: ignore
from fastapi.security import HTTPBearer  # type: ignore
from bd.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
import os
from dotenv import load_dotenv
from routers import auth

load_dotenv()


app = FastAPI(
    title='Flash4Devs API',
    description='https://github.com/iZergiodev/Flash4Devs',
    version= '0.0.1'
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

origins = [
    "http://localhost:5173",
    "https://front-flash4-devs.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get('/', tags=['inicio'])
def read_root():
    return {'Hello': 'world'}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)