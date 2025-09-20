
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, crud, deps
from app.database import engine
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)

import asyncio
from app.grpc_server import serve as grpc_serve

app = FastAPI(title="Products Service")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = structlog.get_logger()

@app.on_event("startup")
async def start_grpc_server():
    loop = asyncio.get_event_loop()
    loop.create_task(grpc_serve())

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

product_created = Counter('product_created_total', 'Total created products')

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/products", response_model=list[schemas.ProductRead])
@limiter.limit("10/minute")
async def list_products(request: Request, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(deps.get_db)):
    return await crud.get_products(db, skip, limit)

@app.get("/products/{product_id}", response_model=schemas.ProductRead)
@limiter.limit("10/minute")
async def get_product(request: Request, product_id: int, db: AsyncSession = Depends(deps.get_db)):
    product = await crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=schemas.ProductRead, status_code=201)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(deps.get_db)):
    db_product = await crud.create_product(db, product)
    if not db_product:
        raise HTTPException(status_code=400, detail="Product already exists")
    product_created.inc()
    logger.info("product_created", name=product.name)
    return db_product

@app.put("/products/{product_id}", response_model=schemas.ProductRead)
async def update_product(product_id: int, product: schemas.ProductUpdate, db: AsyncSession = Depends(deps.get_db), current_admin=Depends(deps.get_current_admin_user)):
    db_product = await crud.update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.delete("/products/{product_id}", response_model=schemas.ProductRead)
async def delete_product(product_id: int, db: AsyncSession = Depends(deps.get_db), current_admin=Depends(deps.get_current_admin_user)):
    db_product = await crud.delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
