from bd.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = "users"
    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")
    profile_image = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    custom_flashcards = relationship("CustomFlashcard", back_populates="user", cascade="all, delete-orphan")
    good_answers = Column(Integer, default=0)
    bad_answers = Column(Integer, default=0)
    level = Column(String(50), default="Beginner")
    rating_interview_front_react = Column(String(50), default="N/A")
    rating_interview_backend_python = Column(String(50), default="N/A")

class Flashcard(Base):
    __tablename__ = 'Flashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficult = Column(String, nullable=False)

class CodingFlashcard(Base):
    __tablename__ = 'CodingFlashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficult = Column(String, nullable=False)

class CustomFlashcard(Base):
    __tablename__ = "custom_flashcards"
    id = Column(Integer, primary_key=True)
    question = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False)
    category = Column(String(100))
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="custom_flashcards")

class EntrevistaFrontEndReact(Base):
    __tablename__ = 'frontendreact'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)

class EntrevistaBackEndPython(Base):
    __tablename__ = 'backendpython'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)