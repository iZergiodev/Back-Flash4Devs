import os
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from fastapi.responses import JSONResponse 
from pydantic import BaseModel
from sqlalchemy import func
from models.models import User as UserModel, Flashcard as FlashCardModel, CodingFlashcard
from bd.database import SessionLocal
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

router = APIRouter(
     prefix='/card',
     tags=['Flashcards']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class CreateCardRequest(BaseModel):
    question: str
    category: str
    solution: str
    difficult: str

class CreateCodingCardRequest(BaseModel):
    question: str
    category: str
    difficult: str


@router.post('/register', status_code=status.HTTP_201_CREATED, summary="Register a flashcard")
def get_flashcards_by_category(db: db_dependency ,create_card_request: CreateCardRequest):

    newCard = FlashCardModel(
        question=create_card_request.question,
        category=create_card_request.category,
        solution=create_card_request.solution,
        difficult = create_card_request.difficult
    )
    db.add(newCard)
    db.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder({"message": "Flashcard created successfully"}))

@router.get('/by-id/{id}', status_code=status.HTTP_200_OK,  summary="Get a flashcard by ID")
def register(db: db_dependency ,id: str):

    cards_by_category = db.query(FlashCardModel).filter(FlashCardModel.id == id).all()

    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(cards_by_category))


@router.get('/by-category/{category}', status_code=status.HTTP_200_OK, summary="Get flashcard by category")
def register(db: db_dependency ,category: str):

    cards_by_category = db.query(FlashCardModel).filter(FlashCardModel.category == category).all()

    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(cards_by_category))



@router.put('/update/{id}', status_code=status.HTTP_200_OK, summary="Update flashcard by id")
def get_flashcards_by_category(db: db_dependency , id: int, update_card_request: CreateCardRequest):

    card_to_update = db.query(FlashCardModel).filter(FlashCardModel.id == id).first()
    if card_to_update is None:
        raise HTTPException(status_code=404, detail='Flashcard not found')

    card_to_update.question = update_card_request.question
    card_to_update.category = update_card_request.category
    card_to_update.solution = update_card_request.solution
    card_to_update.difficult = update_card_request.difficult
    
    db.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder({"message": "Flashcard updated successfully"}))


@router.get('/questions')
def get_random_questions(db: db_dependency, tech: str, limit: int = Query(20)):
        random_flashcards = (
            db.query(FlashCardModel)
            .filter(FlashCardModel.category == tech)
            .order_by(func.random())
            .limit(limit)
            .all()
        )

        if not random_flashcards:
            raise HTTPException(status_code=404, detail="No se encontraron flashcards para la categoría especificada")
        
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

@router.get('/coding-questions')
def get_random_coding_questions(db: db_dependency, tech: str, limit: int = Query(20)):
        random_flashcards = (
            db.query(CodingFlashcard)
            .filter(CodingFlashcard.category == tech)
            .order_by(func.random())
            .limit(limit)
            .all()
        )

        if not random_flashcards:
            raise HTTPException(status_code=404, detail="No se encontraron flashcards para la categoría especificada")
        
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


@router.post('/register-codingcard', status_code=status.HTTP_201_CREATED, summary="Register a flashcard")
def get_flashcards_by_category(db: db_dependency ,create_card_request: CreateCodingCardRequest):

    newCard = CodingFlashcard(
        question=create_card_request.question,
        category=create_card_request.category,
        difficult = create_card_request.difficult
    )
    db.add(newCard)
    db.commit()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder({"message": "Coding Flashcard created successfully"}))