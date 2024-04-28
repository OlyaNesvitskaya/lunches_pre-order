from datetime import date
from typing import Optional, List
from sqlalchemy import select, and_, text

from settings import SessionLocal
from bot.models import Order


def get_order(telegram_user_id: int) -> Optional[Order]:
    with SessionLocal() as session:
        q = session.execute(
            select(Order).where(
                and_(Order.telegram_user_id == telegram_user_id, Order.created_date == date.today(),
                     Order.paid.is_(False))))
        return q.scalar_one_or_none()


def create_order(telegram_user_id: int) -> Order:
    with SessionLocal() as session:
        new_order = Order(telegram_user_id=telegram_user_id)
        session.add(new_order)
        session.flush()
        session.commit()
        return new_order


def delete_order(order: Order) -> None:
    with SessionLocal() as session:
        session.delete(order)
        session.commit()


def set_paid_in_order(order_id: int) -> None:
    with SessionLocal() as session:
        stmt = text(f'UPDATE orders SET paid=1 WHERE id=:order_id')
        session.execute(stmt, params={'order_id': order_id})
        session.commit()


def get_cart(telegram_user_id: int, paid: bool = 0) -> List[tuple]:
    first_column = "o.id" if paid else "ol.id"
    with SessionLocal() as session:
        statement = text(f'SELECT {first_column}, g.name, ol.quantity, g.price, (ol.quantity * g.price) as total_price '
                         f'FROM goods as g '
                         f'JOIN order_lines as ol ON g.id = ol.goods_id '
                         f'JOIN orders as o ON ol.order_id = o.id '
                         f'WHERE o.telegram_user_id = :telegram_user_id AND o.paid = :paid;')
        params = dict(telegram_user_id=telegram_user_id, paid=paid)
        return session.execute(statement, params=params).fetchall()

