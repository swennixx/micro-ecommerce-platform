from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .database import SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session
