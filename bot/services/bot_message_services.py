from sqlalchemy import select, and_
from typing import List

from settings import SessionLocal
from bot.models import BotMessage


def get_message(chat_id: int, marks: list = None) -> List[BotMessage]:
    with SessionLocal() as session:
        if marks:
            statement = select(BotMessage).where(and_(BotMessage.chat_id == chat_id, BotMessage.mark.in_(marks)))
        else:
            statement = select(BotMessage).where(BotMessage.chat_id == chat_id)
        return session.execute(statement).scalars().all()


def create_message(chat_id: int, message_id: int, mark: str) -> None:
    with SessionLocal() as session:
        new_message = BotMessage(chat_id=chat_id, message_id=message_id, mark=mark)
        session.add(new_message)
        session.commit()


def delete_message(message: BotMessage) -> None:
    with SessionLocal() as session:
        session.delete(message)
        session.commit()


def delete_by_chat_id_and_message_id(chat_id: int, message_id: int) -> None:
    with SessionLocal() as session:
        statement = select(BotMessage).where(and_(BotMessage.chat_id == chat_id, BotMessage.message_id == message_id))
        bot_message = session.execute(statement).scalar_one_or_none()
        if bot_message:
            session.delete(bot_message)
            session.commit()


