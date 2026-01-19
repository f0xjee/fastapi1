from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select

import crud
import models
from constants import SUCCESS_RESPONSE
from schema import (CreateAdRequest, CreateAdResponse, DeleteAdResponse,
            GetAdResponse, IdResponse, SearchAdResponse, SuccessResponse, UpdateAdRequest,
            UpdateAdResponse)
from lifespan import lifespan
from app.dependency import SessionDependency
from models import Session, User
from security import get_password_hash, create_access_token, verify_password
from dependency import get_current_user, check_permissions
from schema import CreateUserRequest, LoginRequest, TokenResponse, GetUserResponse

import datetime


app = FastAPI(
    title="Todo API",
    lifespan=lifespan
)


@app.post('/advertisement', response_model=CreateAdResponse)
async def create_ad(ad: CreateAdRequest, session: SessionDependency):
    ad_dict = ad.model_dump(exclude_unset=True)
    ad_orm_obj = models.Ad(**ad_dict)
    await crud.add_item(session, ad_orm_obj)
    return ad_orm_obj.id_dict

@app.get('/advertisement/{advertisement_id}', response_model=GetAdResponse)
async def get_ad(advertisement_id: int, session: SessionDependency):
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    return ad_orm_obj.dict

@app.get('/advertisement', response_model=SearchAdResponse)
async def search_ad(
    session: SessionDependency,
    title: str | None = None,
    description: str | None = None,
    author: str | None = None,
    price: float | None = None,
    limit: int = 100,
    offset: int = 0
):
    query = select(models.Ad)
    
    conditions = []
    if title:
        conditions.append(models.Ad.title.ilike(f"%{title}%"))
    if description:
        conditions.append(models.Ad.description.ilike(f"%{description}%"))
    if author:
        conditions.append(models.Ad.author.ilike(f"%{author}%"))
    if price:
        conditions.append(models.Ad.price == price)
    
    if conditions:
        query = query.where(*conditions)
    
    query = query.limit(limit).offset(offset)
    ads = await session.scalars(query)
    return {"results": [ad.dict for ad in ads]}

@app.patch('/advertisement/{advertisement_id}', response_model=UpdateAdResponse)
async def update_ad(advertisement_id: int, ad_data: UpdateAdRequest, session: SessionDependency):
    ad_dict = ad_data.model_dump(exclude_unset=True)
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    
    for field, value in ad_dict.items():
        setattr(ad_orm_obj, field, value)
    await crud.add_item(session, ad_orm_obj)
    return SUCCESS_RESPONSE

@app.delete('/advertisement/{advertisement_id}', response_model=DeleteAdResponse)
async def delete_ad(advertisement_id: int, session: SessionDependency):
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    await crud.delete_item(session, ad_orm_obj)
    return SUCCESS_RESPONSE


@app.post('/login', response_model=TokenResponse)
async def login(login_data: LoginRequest, session: SessionDependency):
    query = select(User).where(User.username == login_data.username)
    result = await session.scalars(query)
    user = result.first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post('/user', response_model=IdResponse)
async def create_user(user_data: CreateUserRequest, session: SessionDependency):
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_orm_obj = User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.id_dict

@app.get('/user/{user_id}', response_model=GetUserResponse)
async def get_user(user_id: int, session: SessionDependency):
    user_orm_obj = await crud.get_item_by_id(session, User, user_id)
    return user_orm_obj.dict


@app.patch('/user/{user_id}', response_model=SuccessResponse)
async def update_user(
    user_id: int,
    user_data: CreateUserRequest,
    session: SessionDependency,
    current_user: User = Depends(get_current_user)
):
    await check_permissions(current_user, owner_id=user_id)
    user_dict = user_data.model_dump(exclude_unset=True)
    if "password" in user_dict:
        user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_orm_obj = await crud.get_item_by_id(session, User, user_id)
    for field, value in user_dict.items():
        setattr(user_orm_obj, field, value)
    await crud.add_item(session, user_orm_obj)
    return SUCCESS_RESPONSE
