from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import Product
from .schemas import ProductCreate, ProductUpdate
from sqlalchemy.exc import IntegrityError
from .redis_cache import get_product_from_cache, set_product_to_cache
import json

async def get_product(db: AsyncSession, product_id: int):
    cached = await get_product_from_cache(product_id)
    if cached:
        return Product(**json.loads(cached))
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if product:
        await set_product_to_cache(product_id, json.dumps({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock
        }))
    return product

async def get_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_product(db: AsyncSession, product: ProductCreate):
    db_product = Product(**product.dict())
    db.add(db_product)
    try:
        await db.commit()
        await db.refresh(db_product)
        return db_product
    except IntegrityError:
        await db.rollback()
        return None

async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate):
    db_product = await get_product(db, product_id)
    if not db_product:
        return None
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    await db.commit()
    await db.refresh(db_product)
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    db_product = await get_product(db, product_id)
    if not db_product:
        return None
    await db.delete(db_product)
    await db.commit()
    return db_product
