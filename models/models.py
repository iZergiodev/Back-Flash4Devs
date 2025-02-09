from bd.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey



class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
    level = Column(String)
     

class Flashcard(Base):
    __tablename__ = 'Flashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    solution = Column(String, nullable=False)
    difficult = Column(String, nullable=False)

class CodingFlashcard(Base):
    __tablename__ = 'CodingFlashcard'
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, nullable=False)
    category = Column(String, unique=True, nullable=False)
    solution = Column(String, nullable=False)
    difficult = Column(String, nullable=False)
    owner_id = Column(ForeignKey("User.id"))
