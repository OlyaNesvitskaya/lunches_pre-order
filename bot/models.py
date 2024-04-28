from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from datetime import date


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(30), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    manager: Mapped[bool] = mapped_column(default=False)


class GoodsCategory(Base):
    __tablename__ = 'goods_categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    goodss = relationship('Goods', cascade="all, delete-orphan")


class Goods(Base):
    __tablename__ = 'goods'
    id: Mapped[int] = mapped_column(primary_key=True)
    vendor_code: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[int] = mapped_column(ForeignKey("goods_categories.id"))
    price: Mapped[int] = mapped_column(nullable=False)
    load_date: Mapped[date] = mapped_column(Date, default=date.today())

    def __str__(self):
        return f'Страва "{self.name}" з категорії "{self.category}"'


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    created_date: Mapped[date] = mapped_column(
        Date, default=date.today()
    )
    paid: Mapped[bool] = mapped_column(default=False)
    order_lines = relationship('OrderLine', cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = 'order_lines'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    goods_id: Mapped[int] = mapped_column(ForeignKey("goods.id"))
    quantity: Mapped[int] = mapped_column(nullable=False)
    good = relationship('Goods')


class BotMessage(Base):
    __tablename__ = 'bot_messages'
    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column()
    message_id: Mapped[int] = mapped_column()
    mark: Mapped[str] = mapped_column(String(30))

