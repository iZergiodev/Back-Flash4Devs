from bd.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
    level = Column(String)
    profile_image = Column(String)

    good_answers = Column(Integer, default=0)
    regular_answers = Column(Integer, default=0)  
    bad_answers = Column(Integer, default=0) 

    custom_flashcards = relationship("CustomFlashcard", back_populates="owner", cascade="all, delete-orphan")
     

class Flashcard(Base):
    __tablename__ = 'Flashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
    solution = Column(String, nullable=False)
    difficult = Column(String, nullable=False)

class CodingFlashcard(Base):
    __tablename__ = 'CodingFlashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    category = Column(String, nullable=False)
    difficult = Column(String, nullable=False)


class CustomFlashcard(Base):
    __tablename__ = 'CustomFlashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    solution = Column(String, nullable=False)
    category = Column(String)
    difficult = Column(String)

    owner_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    owner = relationship("User", back_populates="custom_flashcards")