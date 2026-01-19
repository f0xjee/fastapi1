import datetime
from typing import Literal, Optional
from pydantic import BaseModel

class SuccessResponse(BaseModel):
    status: Literal["success"]

class IdResponse(BaseModel):
    id: int

class CreateAdRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    author: str

class CreateAdResponse(IdResponse):
    pass

class UpdateAdRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class UpdateAdResponse(SuccessResponse):
    pass

class GetAdResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author: str
    created_at: datetime.datetime

class SearchAdResponse(BaseModel):
    results: list[GetAdResponse]

class DeleteAdResponse(SuccessResponse):
    pass

class CreateUserRequest(BaseModel):
    username: str
    password: str
    group: Optional[str] = "user"

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GetUserResponse(BaseModel):
    id: int
    username: str
    group: str

