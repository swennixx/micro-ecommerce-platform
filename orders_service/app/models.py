from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship, declarative_base
import enum
import datetime

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"

order_products = Table(
    "order_products",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id")),
    Column("product_id", Integer),
    Column("quantity", Integer, default=1)
)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    products = relationship("OrderProduct", back_populates="order", lazy="selectin")

class OrderProduct(Base):
    __tablename__ = "order_products_details"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)
    quantity = Column(Integer, default=1)
    order = relationship("Order", back_populates="products")
