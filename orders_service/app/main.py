
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, crud, deps
from app.products_grpc_client import ProductsGrpcClient
from app.database import engine
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Orders Service")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = structlog.get_logger()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

order_created = Counter('order_created_total', 'Total created orders')

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/orders", response_model=list[schemas.OrderRead])
@limiter.limit("10/minute")
async def list_orders(request: Request, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(deps.get_db)):
    return await crud.get_orders(db, skip, limit)

@app.get("/orders/{order_id}", response_model=schemas.OrderRead)
async def get_order(order_id: int, db: AsyncSession = Depends(deps.get_db)):
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", status_code=201)
@limiter.limit("10/minute")
async def create_order(request: Request, order: schemas.OrderCreate, db: AsyncSession = Depends(deps.get_db)):
    grpc_client = ProductsGrpcClient()
    total_price = 0.0
    # Получаем цену каждого продукта через gRPC
    for p in order.products:
        product = await grpc_client.get_product(p.product_id)
        if not product or not hasattr(product, 'price'):
            raise HTTPException(status_code=404, detail=f"Product {p.product_id} not found")
        total_price += product.price * p.quantity
    # Создать заказ и продукты
    from app.models import Order, OrderProduct
    db_order = Order(user_id=order.user_id, total_price=total_price)
    db.add(db_order)
    await db.flush()
    for p in order.products:
        db.add(OrderProduct(order_id=db_order.id, product_id=p.product_id, quantity=p.quantity))
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Order creation failed")
    # Получить все OrderProduct для этого заказа
    from app.models import OrderProduct
    result = await db.execute(
        __import__('sqlalchemy').future.select(OrderProduct).where(OrderProduct.order_id == db_order.id)
    )
    products = result.scalars().all()
    # Собрать ответ вручную
    response = {
        "id": db_order.id,
        "user_id": db_order.user_id,
        "total_price": db_order.total_price,
        "status": str(db_order.status),
        "products": [
            {"id": prod.id, "product_id": prod.product_id, "quantity": prod.quantity}
            for prod in products
        ]
    }
    order_created.inc()
    logger.info("order_created", user_id=order.user_id)
    return response

@app.put("/orders/{order_id}/status", response_model=schemas.OrderRead)
async def update_order_status(order_id: int, status: schemas.OrderStatus, db: AsyncSession = Depends(deps.get_db)):
    db_order = await crud.update_order_status(db, order_id, status)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
