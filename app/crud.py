from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import ORM_CLS, ORM_OBJ


async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
        await session.refresh(item)
    except IntegrityError as err:
        await session.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Item already exists or constraint violation: {str(err)}"
        )
    except Exception as err:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(err)}"
        )


async def get_item_by_id(
    session: AsyncSession, orm_cls: ORM_CLS, item_id: int
) -> ORM_OBJ:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
    return orm_obj


async def delete_item(session: AsyncSession, item: ORM_OBJ):
    await session.delete(item)
    try:
        await session.commit()
    except Exception as err:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(err)}"
        )