
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
import random
# import httpx  # Для интеграции с Orders Service (TODO)


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Payments Service")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = structlog.get_logger()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

payment_created = Counter('payment_created_total', 'Total created payments')

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/payments", response_model=list[schemas.PaymentRead])
@limiter.limit("10/minute")
async def list_payments(request: Request, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(deps.get_db)):
    return await crud.get_payments(db, skip, limit)

@app.get("/payments/{payment_id}", response_model=schemas.PaymentRead)
async def get_payment(payment_id: int, db: AsyncSession = Depends(deps.get_db)):
    payment = await crud.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.post("/payments", response_model=schemas.PaymentRead, status_code=201)
@limiter.limit("10/minute")
async def create_payment(request: Request, payment: schemas.PaymentCreate, db: AsyncSession = Depends(deps.get_db)):
    # Эмуляция оплаты: случайный успех/неудача
    status = models.PaymentStatus.success if random.random() > 0.2 else models.PaymentStatus.failed
    db_payment = await crud.create_payment(db, payment, status)
    if not db_payment:
        raise HTTPException(status_code=400, detail="Payment creation failed")
    payment_created.inc()
    logger.info("payment_created", order_id=payment.order_id, status=status)
    # TODO: Интеграция с Orders Service для обновления статуса заказа
    return db_payment

@app.put("/payments/{payment_id}/status", response_model=schemas.PaymentRead)
async def update_payment_status(payment_id: int, status: schemas.PaymentStatus, db: AsyncSession = Depends(deps.get_db)):
    db_payment = await crud.update_payment_status(db, payment_id, status)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
