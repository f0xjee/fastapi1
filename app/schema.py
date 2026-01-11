import datetime
from typing import Literal

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    status: Literal["success"]


class IdResponse(BaseModel):
   id: int 
   
   
class CreateAdRequest(BaseModel): #параметры запросов
    headers: str
    req: str | None
    price: int
    author: str
    start_time: datetime.datetime
   
   
class CreateAdResponse(IdResponse): #параметры ответов
    pass


class UpdateAdRequest(BaseModel): #обновление запроса
    headers: str | None = None
    req: str | None = None
    price: int | None = None
    
    
class UpdateAdResponse(SuccessResponse): #обновление ответов
    pass


class GetAdResponse(BaseModel):
    id: int
    headers: str
    req: str
    price: int
    author: str
    start_time: datetime.datetime
    
    
class SearchAdRespone(BaseModel):
    results: list[GetAdResponse]
    
    
class DeleteAdResponse(SuccessResponse):
    pass