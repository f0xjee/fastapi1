from fastapi import FastAPI
from sqlalchemy import select

import crud
import models
from constants import SUCCESS_RESPONSE
from schema import (CreateAdRequest, CreateAdResponse, DeleteAdResponse,
                    GetAdResponse, SearchAdRespone, UpdateAdRequest,
                    UpdateAdResponse)
from lifespan import lifespan
from dependancy import SessionDependency
from models import Session

import datetime

app = FastAPI(
    title="Todo API",
    lifespan=lifespan
)


    
@app.post('/api/v1/advertisement', response_model=CreateAdResponse)
async def create_ad(ad: CreateAdRequest, session: SessionDependency):
    ad_dict = ad.model_dump(exclude_unset=True) #model_dump делает словарик из туду, параметры которые не переданы он исключает
    ad_orm_obj = models.Ad(**ad_dict)
    await crud.add_item(session, ad_orm_obj)
    return ad_orm_obj.id_dict


@app.get('/api/v1/advertisement/{advertisement_id}', response_model=GetAdResponse)
async def get_ad(advertisement_id: int, session: SessionDependency):
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    return ad_orm_obj.dict


@app.get('/api/v1/advertisement?{query_string}', response_model=SearchAdRespone)
async def search_ad(session: SessionDependency, headers: str):
    query = (
        select(models.Ad)
        .where(models.Ad.headers == headers)
        .limit(10000)
    )
    ads = await session.scalars(query)
    return {"results": [ad.dict for ad in ads]}


@app.patch('/api/v1/advertisement/{advertisement_id}', response_model=UpdateAdResponse)
async def update_ad(advertisement_id: int, ad_data: UpdateAdRequest, session: SessionDependency):
    ad_dict = ad_data.model_dump(exclude_unset=True)
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    
    for field, value in ad_dict.items():
        setattr(ad_orm_obj, field, value)
    await crud.add_item(session, ad_orm_obj)
    return SUCCESS_RESPONSE


@app.delete('/api/v1/advertisement/{advertisement_id}', response_model=DeleteAdResponse)
async def delete_ad(advertisement_id: int, session: SessionDependency):
    ad_orm_obj = await crud.get_item_by_id(session, models.Ad, advertisement_id)
    await crud.delete_item(session, ad_orm_obj)
    return SUCCESS_RESPONSE