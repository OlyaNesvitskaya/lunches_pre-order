from sqlalchemy import select
from typing import Optional, List

from settings import SessionLocal
from bot.models import OrderLine


def get_order_lines(order_id: int) -> List[OrderLine]:
    with SessionLocal() as session:
        return session.execute(select(OrderLine).where(OrderLine.order_id == order_id)).scalars().all()


def get_order_line(order_line_id: int) -> Optional[OrderLine]:
    with SessionLocal() as session:
        return session.get(OrderLine, order_line_id)


def add_order_line(order_id: int, goods_id: int, quantity: int) -> None:
    with SessionLocal() as session:
        new_ol = OrderLine(order_id=order_id, goods_id=goods_id, quantity=quantity)
        session.add(new_ol)
        session.commit()


def change_quantity_in_order_line(order_line: OrderLine, quantity: int) -> None:
    with SessionLocal() as session:
        setattr(order_line, 'quantity', quantity)
        session.add(order_line)
        session.commit()


def delete_order_line(order_line: OrderLine) -> None:
    with SessionLocal() as session:
        session.delete(order_line)
        session.commit()
