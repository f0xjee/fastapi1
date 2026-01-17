from fastapi import FastAPI
from sqlalchemy import select

import crud
import models
from constants import SUCCESS_RESPONSE
from schema import (CreateAdRequest, CreateAdResponse, DeleteAdResponse,
                    GetAdResponse, SearchAdResponse, UpdateAdRequest,
                    UpdateAdResponse)
from lifespan import lifespan
from app.dependency import SessionDependency
from models import Session

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
