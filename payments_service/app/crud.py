from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Payment, PaymentStatus
from .schemas import PaymentCreate
from sqlalchemy.exc import IntegrityError

async def get_payment(db: AsyncSession, payment_id: int):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalars().first()

async def get_payments(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Payment).offset(skip).limit(limit))
    return result.scalars().all()

async def create_payment(db: AsyncSession, payment: PaymentCreate, status: PaymentStatus):
    db_payment = Payment(order_id=payment.order_id, amount=payment.amount, status=status)
    db.add(db_payment)
    try:
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
    except IntegrityError:
        await db.rollback()
        return None

async def update_payment_status(db: AsyncSession, payment_id: int, status: PaymentStatus):
    db_payment = await get_payment(db, payment_id)
    if not db_payment:
        return None
    db_payment.status = status
    await db.commit()
    await db.refresh(db_payment)
    return db_payment
