
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .models import Order, OrderProduct, OrderStatus
from .schemas import OrderCreate, OrderRead, OrderProductRead, OrderStatus
from sqlalchemy.exc import IntegrityError

async def get_order(db: AsyncSession, order_id: int):
    result = await db.execute(
        select(Order).options(selectinload(Order.products)).where(Order.id == order_id)
    )
    return result.scalars().first()

async def get_orders(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Order).options(selectinload(Order.products)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_order(db: AsyncSession, order: OrderCreate, total_price: float):
    db_order = Order(user_id=order.user_id, total_price=total_price)
    db.add(db_order)
    await db.flush()
    for p in order.products:
        db.add(OrderProduct(order_id=db_order.id, product_id=p.product_id, quantity=p.quantity))
    try:
        await db.commit()
        # Получить все OrderProduct для этого заказа
        result = await db.execute(select(OrderProduct).where(OrderProduct.order_id == db_order.id))
        products = result.scalars().all()
        products_read = [OrderProductRead(id=prod.id, product_id=prod.product_id, quantity=prod.quantity) for prod in products]
        order_read = OrderRead(
            id=db_order.id,
            user_id=db_order.user_id,
            total_price=db_order.total_price,
            status=db_order.status,
            products=products_read
        )
        return order_read
    except IntegrityError:
        await db.rollback()
        return None

async def update_order_status(db: AsyncSession, order_id: int, status: OrderStatus):
    db_order = await get_order(db, order_id)
    if not db_order:
        return None
    db_order.status = status
    await db.commit()
    await db.refresh(db_order)
    return db_order
