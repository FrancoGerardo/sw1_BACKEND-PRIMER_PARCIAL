from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    correo: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    correo: str
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SalaBase(BaseModel):
    title: str
    description: Optional[str] = None
    xml: Optional[str] = None

class SalaCreate(SalaBase):
    pass

class SalaUpdate(SalaBase):
    pass

class SalaResponse(SalaBase):
    id: int
    tokenS: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserSalaBase(BaseModel):
    user_id: int
    salas_id: int

class UserSalaCreate(UserSalaBase):
    pass

class UserSalaResponse(UserSalaBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None