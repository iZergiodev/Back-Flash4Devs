from fastapi import FastAPI, Request, HTTPException # type: ignore
from pydantic import BaseModel
import uvicorn  # type: ignore
from fastapi.security import HTTPBearer  # type: ignore
from bd.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
import os
from dotenv import load_dotenv
from routers import auth
from routers import flashcards
import google.generativeai as genai


load_dotenv()


app = FastAPI(
    title='Flash4Devs API',
    description='https://github.com/iZergiodev/Flash4Devs',
    version= '0.0.1'
)

Base.metadata.create_all(bind=engine)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("La variable de entorno GOOGLE_API_KEY no está definida.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

app.include_router(auth.router)
app.include_router(flashcards.router)

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


class ChatRequest(BaseModel):
    system_prompt: str
    user_message: str

@app.post("/chat/")
async def chat_with_gemini(request: ChatRequest):
    try:
        full_prompt = f"{request.system_prompt}\n\nUsuario: {request.user_message}"

        response = model.generate_content(full_prompt)
        return {"generated_text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

