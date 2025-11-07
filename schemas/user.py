from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class UserIn(BaseModel):
    name: str
    email: str
    age: int
    password: str  # Optional password for update
    refresh_token: str

class UserOut(BaseModel):
    name: str
    email: str
    age: int
    id: str

    model_config = ConfigDict(from_attributes=True)

class SignUpData(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    age: Optional[int] = None


class LoginData(BaseModel):
    email: str
    password: str