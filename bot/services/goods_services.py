from sqlalchemy import select
from typing import Optional, List

from settings import SessionLocal
from bot.models import Goods


def get_goods(vendor_code: str) -> Optional[Goods]:
    with SessionLocal() as session:
        return session.execute(select(Goods).where(Goods.vendor_code == vendor_code)).scalar_one_or_none()


def get_all_goods() -> List[Goods]:
    with SessionLocal() as session:
        return session.execute(select(Goods)).scalars().all()



