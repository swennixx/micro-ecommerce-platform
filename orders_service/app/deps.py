from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session

# Заглушка для получения текущего пользователя (реализовать интеграцию с Users Service)
async def get_current_user():
    # TODO: Проверять JWT через Users Service
    raise HTTPException(status_code=401, detail="Not authenticated")
