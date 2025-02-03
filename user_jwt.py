import jwt
import os
from dotenv import load_dotenv

load_dotenv()


def createToken(data: dict):
    token: str = jwt.encode(payload=data, key=os.getenv("SECRET_KEY"), algorithm='HS256')
    return token

def validateToken(token:str) -> dict:
    data: dict = jwt.decode(token, key=os.getenv("SECRET_KEY"), algorithms=['HS256'])
    return data