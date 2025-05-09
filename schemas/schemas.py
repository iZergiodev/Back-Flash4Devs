from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: Optional[str]
    name: str
    last_name: Optional[str]
    profile_image: Optional[str]