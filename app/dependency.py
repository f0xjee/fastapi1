from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, User
from security import decode_access_token
import crud

async def get_session() -> AsyncSession:  # type: ignore
    async with Session() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_session)]

async def get_current_user(
    session: AsyncSession,
    authorization: str = Header(None)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await crud.get_item_by_id(session, User, int(user_id))
    return user

async def check_permissions(
    current_user: User,
    required_group: Optional[str] = None,
    owner_id: Optional[int] = None
):
    if required_group == "admin" and current_user.group != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if owner_id and current_user.id != owner_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
