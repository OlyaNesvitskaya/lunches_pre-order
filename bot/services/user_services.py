from typing import Optional, List
from sqlalchemy import select, and_

from settings import SessionLocal
from bot.models import User


def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    with SessionLocal() as session:
        return session.execute(select(User).where(User.telegram_id == telegram_id)).scalar_one_or_none()


def get_user_by_phone_number(phone_number: str) -> Optional[User]:
    with SessionLocal() as session:
        return session.execute(select(User).where(User.phone_number == phone_number)).scalar_one_or_none()


def get_all_users() -> List[User]:
    with SessionLocal() as session:
        return session.execute(select(User)).scalars().all()


def create_user(telegram_id: int, phone_number: str) -> None:
    with SessionLocal() as session:
        new_user = User(telegram_id=telegram_id, phone_number=phone_number)
        session.add(new_user)
        session.commit()


def add_full_name_to_user(telegram_id: int, full_name: str) -> None:
    with SessionLocal() as session:
        user_db = get_user_by_telegram_id(telegram_id)
        setattr(user_db, 'full_name', full_name)
        session.add(user_db)
        session.commit()


def access_manager(user: User, is_manager: bool) -> None:
    with SessionLocal() as session:
        setattr(user, 'manager', is_manager)
        session.add(user)
        session.commit()


def get_managers() -> List[User]:
    with SessionLocal() as session:
        statement = select(User).where(User.manager.is_(True))
        return session.execute(statement).scalars().all()


def get_manager(telegram_id: int) -> Optional[User]:
    with SessionLocal() as session:
        statement = select(User).where(and_(User.telegram_id == telegram_id, User.manager.is_(True)))
        return session.execute(statement).scalar_one_or_none()
