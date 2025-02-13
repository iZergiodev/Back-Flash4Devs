from enum import Enum
import os
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import google.generativeai as genai
from models.models import (
    CustomFlashcard, EntrevistaBackEndPython, EntrevistaFrontEndReact,
    User as UserModel, Flashcard as FlashCardModel, CodingFlashcard
)
from bd.database import SessionLocal

load_dotenv()

# Configuración del router
router = APIRouter(
    prefix='/card',
    tags=['Flashcards']
)

# Dependencias
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modelos Pydantic para solicitudes

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class CreateCardRequest(BaseModel):
    question: str
    category: str
    solution: str
    difficult: DifficultyLevel

class CreateCodingCardRequest(BaseModel):
    question: str
    category: str
    difficult: DifficultyLevel

class CreateCustomCardRequest(BaseModel):
    question: str
    solution: str
    category: str
    difficult: DifficultyLevel

class CreateFrontendReactQuestionRequest(BaseModel):
    question: str

class CreateBackendPythonQuestionRequest(BaseModel):
    question: str



# Funciones de utilidad
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Rutas para Flashcards
@router.post('/register', status_code=status.HTTP_201_CREATED, summary="Register a flashcard")
def register_flashcard(db: db_dependency, create_card_request: CreateCardRequest):
    new_card = FlashCardModel(
        question=create_card_request.question,
        category=create_card_request.category,
        solution=create_card_request.solution,
        difficult=create_card_request.difficult
    )
    db.add(new_card)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({"message": "Flashcard created successfully"})
    )

@router.get('/by-id/{id}', status_code=status.HTTP_200_OK, summary="Get a flashcard by ID")
def get_flashcard_by_id(db: db_dependency, id: str):
    card = db.query(FlashCardModel).filter(FlashCardModel.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(card))

@router.get('/by-category/{category}', status_code=status.HTTP_200_OK, summary="Get flashcards by category")
def get_flashcards_by_category(db: db_dependency, category: str):
    cards = db.query(FlashCardModel).filter(FlashCardModel.category == category).all()
    if not cards:
        raise HTTPException(status_code=404, detail="No flashcards found for the specified category")
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(cards))

@router.put('/update/{id}', status_code=status.HTTP_200_OK, summary="Update flashcard by ID")
def update_flashcard(db: db_dependency, id: int, update_card_request: CreateCardRequest):
    card_to_update = db.query(FlashCardModel).filter(FlashCardModel.id == id).first()
    if not card_to_update:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    card_to_update.question = update_card_request.question
    card_to_update.category = update_card_request.category
    card_to_update.solution = update_card_request.solution
    card_to_update.difficult = update_card_request.difficult
    
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"message": "Flashcard updated successfully"})
    )

@router.get('/questions', summary="Get random flashcards by category and difficulty")
def get_random_questions(
    db: db_dependency,
    tech: str,
    difficult: Optional[DifficultyLevel] = Query(None, description="Filtrar por dificultad (opcional)"),
    limit: int = Query(20)
):
    query = db.query(FlashCardModel).filter(FlashCardModel.category == tech)

    if difficult:
        query = query.filter(FlashCardModel.difficult == difficult)

    random_flashcards = (
        query.order_by(func.random())
        .limit(limit)
        .all()
    )

    if not random_flashcards:
        raise HTTPException(
            status_code=404,
            detail="No flashcards found for the specified category and difficulty"
        )
    
    result = [
        {
            "id": flashcard.id,
            "question": flashcard.question,
            "category": flashcard.category,
            "solution": flashcard.solution,
            "difficult": flashcard.difficult,
        }
        for flashcard in random_flashcards
    ]
    
    return result



# Rutas para Coding Flashcards
@router.post('/register-codingcard', status_code=status.HTTP_201_CREATED, summary="Register a coding flashcard")
def register_coding_flashcard(db: db_dependency, create_card_request: CreateCodingCardRequest):
    new_card = CodingFlashcard(
        question=create_card_request.question,
        category=create_card_request.category,
        difficult=create_card_request.difficult
    )
    db.add(new_card)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({"message": "Coding Flashcard created successfully"})
    )

@router.get('/coding-questions', summary="Get random coding flashcards by category")
def get_random_coding_questions(db: db_dependency, tech: str, limit: int = Query(20)):
    random_flashcards = (
        db.query(CodingFlashcard)
        .filter(CodingFlashcard.category == tech)
        .order_by(func.random())
        .limit(limit)
        .all()
    )

    if not random_flashcards:
        raise HTTPException(status_code=404, detail="No coding flashcards found for the specified category")
    
    result = [
        {
            "id": flashcard.id,
            "question": flashcard.question,
            "category": flashcard.category,
            "difficult": flashcard.difficult,
        }
        for flashcard in random_flashcards
    ]
    
    return result

# Rutas para Custom Flashcards
@router.post('/register-custom', status_code=status.HTTP_201_CREATED, summary="Create custom flashcard")
def create_custom_flashcard(
    create_card_request: CreateCustomCardRequest,
    db: db_dependency,
    current_user: UserModel = Depends(get_current_user)
):
    new_custom_card = CustomFlashcard(
        question=create_card_request.question,
        solution=create_card_request.solution,
        category=create_card_request.category,
        difficult=create_card_request.difficult,
        owner_id=current_user.id
    )
    db.add(new_custom_card)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({"message": "Custom Flashcard created successfully"})
    )

@router.get('/custom-questions', summary="Get random custom flashcards by category")
def get_random_custom_questions(
    db: db_dependency,
    tech: str,
    limit: int = Query(10),
    current_user: UserModel = Depends(get_current_user)
):
    random_custom_flashcards = (
        db.query(CustomFlashcard)
        .filter(CustomFlashcard.category == tech, CustomFlashcard.owner_id == current_user.id)
        .order_by(func.random())
        .limit(limit)
        .all()
    )

    if not random_custom_flashcards:
        raise HTTPException(status_code=404, detail="No custom flashcards found for the specified category")
    
    result = [
        {
            "id": flashcard.id,
            "question": flashcard.question,
            "solution": flashcard.solution,
            "category": flashcard.category,
            "difficult": flashcard.difficult,
        }
        for flashcard in random_custom_flashcards
    ]
    
    return result

# Rutas para EntrevistaFrontEndReact
@router.post('/frontend-react', status_code=status.HTTP_201_CREATED, summary="Create a frontend React interview question")
def create_frontend_react_question(
    create_request: CreateFrontendReactQuestionRequest,
    db: db_dependency
):
    new_question = EntrevistaFrontEndReact(
        question=create_request.question
    )
    db.add(new_question)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({"message": "Frontend React question created successfully"})
    )

@router.get('/frontend-react', status_code=status.HTTP_200_OK, summary="Get all frontend React interview questions")
def get_all_frontend_react_questions(db: db_dependency):
    questions = db.query(EntrevistaFrontEndReact).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No frontend React questions found")
    
    result = [
        {
            "id": question.id,
            "question": question.question,
        }
        for question in questions
    ]
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))

# Rutas para EntrevistaBackEndPython
@router.post('/backend-python', status_code=status.HTTP_201_CREATED, summary="Create a backend Python interview question")
def create_backend_python_question(
    create_request: CreateBackendPythonQuestionRequest,
    db: db_dependency
):
    new_question = EntrevistaBackEndPython(
        question=create_request.question
    )
    db.add(new_question)
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder({"message": "Backend Python question created successfully"})
    )

@router.get('/backend-python', status_code=status.HTTP_200_OK, summary="Get all backend Python interview questions")
def get_all_backend_python_questions(db: db_dependency):
    questions = db.query(EntrevistaBackEndPython).all()
    if not questions:
        raise HTTPException(status_code=404, detail="No backend Python questions found")
    
    result = [
        {
            "id": question.id,
            "question": question.question,
        }
        for question in questions
    ]
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))



#User Estadísticas

class UpdateUserAnswersRequest(BaseModel):
    good_answers: int = 0
    regular_answers: int = 0
    bad_answers: int = 0

@router.put('/update-user-answers', status_code=status.HTTP_200_OK, summary="Update user answers")
def update_user_answers(
    update_request: UpdateUserAnswersRequest,
    db: db_dependency,
    current_user: UserModel = Depends(get_current_user)
):
    # Obtener el usuario actual
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar las respuestas
    user.good_answers += update_request.good_answers
    user.regular_answers += update_request.regular_answers
    user.bad_answers += update_request.bad_answers

    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"message": "User answers updated successfully"})
    )

class UpdateUserLevelRequest(BaseModel):
    level: str

@router.put('/update-user-level', status_code=status.HTTP_200_OK, summary="Update user level")
def update_user_level(
    update_request: UpdateUserLevelRequest,
    db: db_dependency,
    current_user: UserModel = Depends(get_current_user)
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.level = update_request.level
    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"message": "User level updated successfully"})
    )

#interview

class UpdateInterviewRatingRequest(BaseModel):
    rating: int
    interview_type: str

@router.put('/update-interview-rating', status_code=status.HTTP_200_OK, summary="Update interview rating")
def update_interview_rating(
    update_request: UpdateInterviewRatingRequest,
    db: db_dependency,
    current_user: UserModel = Depends(get_current_user)
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if update_request.interview_type == "frontend_react":
        user.rating_interview_front_react += update_request.rating
    elif update_request.interview_type == "backend_python":
        user.rating_interview_backend_python += update_request.rating
    else:
        raise HTTPException(status_code=400, detail="Tipo de entrevista no válido")

    db.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"message": "Interview rating updated successfully"})
    )