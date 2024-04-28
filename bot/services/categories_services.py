from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List

from settings import SessionLocal
from bot.models import GoodsCategory


def get_all_category() -> List[GoodsCategory]:
    with SessionLocal() as session:
        return session.execute(select(GoodsCategory.name)).scalars().all()


def add_categories(categories: list) -> None:
    with SessionLocal() as session:
        session.add_all([GoodsCategory(id=index, name=category) for index, category in enumerate(categories, start=1)])
        session.commit()


def get_dishes_from_category(category: str) -> GoodsCategory:
    with SessionLocal() as session:
        stmt = select(GoodsCategory).where(GoodsCategory.name == category).options(joinedload(GoodsCategory.goodss))
        return session.execute(stmt).unique().scalar_one_or_none()


