from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from telebot import TeleBot
from os import environ

from bot.models import Base

load_dotenv()

bot = TeleBot(environ.get('TELEGRAM_TOKEN'))

DATABASE_URL = (f"mysql+pymysql://root:{environ.get('MYSQL_ROOT_PASSWORD')}"
                f"@{environ.get('DB_HOST')}/{environ.get('MYSQL_DATABASE')}")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
     bind=engine, expire_on_commit=False
)


def init_db():
    Base.metadata.create_all(bind=engine)
