from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .database import SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session

# Заглушка для проверки прав администратора (реализовать интеграцию с Users Service)
async def get_current_admin_user():
    # TODO: Проверять JWT и роль через Users Service
    raise HTTPException(status_code=403, detail="Not enough permissions (admin only)")
