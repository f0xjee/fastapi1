import datetime

import config
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_async_engine(config.PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    
    @property
    def id_dict(self):
        return {"id": self.id}
    

#headers заголовок
#req описание
#price цена
#author автор
#start_time дата создания

class Ad(Base):
    __tablename__ = "ad"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headers: Mapped[str] = mapped_column(String, index=True)
    req: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    author: Mapped[str] = mapped_column(String)
    start_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    
    @property
    def dict(self):
        return {
            "id": self.id,
            "headers": self.headers,
            "req": self.req,
            "price": self.price,
            "author": self.author,
            "start_time": self.start_time.isoformat(),
        }
        
        
ORM_OBJ = Ad
ORM_CLS = type[Ad]
        
        
async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        
async def close_orm():
    await engine.dispose()