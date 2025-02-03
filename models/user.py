from bd.database import Base

from sqlalchemy import Column, Integer, String



class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
    