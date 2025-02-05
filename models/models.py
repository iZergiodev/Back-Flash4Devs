from bd.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey



class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String)
    last_name = Column(String)
     