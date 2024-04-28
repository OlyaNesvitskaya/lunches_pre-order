from telebot.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, ReplyKeyboardMarkup, InlineKeyboardButton

from botlog import logger
from bot.services import user_services, bot_message_services
from bot.bot_message import delete_message_in_bot, clean_message_chat, bot
from bot.menu import generate_menu_text


def save_user_full_name(message: Message) -> None:
    delete_message_in_bot(message.chat.id, message.message_id)
    clean_message_chat(message.chat.id, ['clean', 'basket'])
    user_full_name = message.text.split()

    if len(user_full_name) >= 2 and len(user_full_name[0]) >= 3 and len(user_full_name[1]) >= 3:
        user_services.add_full_name_to_user(telegram_id=message.chat.id, full_name=message.text)
        bot_message_services.create_message(message.chat.id, message.message_id, 'clean')
        send_message_to_user(
            chat_id=message.chat.id,
            text=f'Привiт, {message.text}.\nНатисни на кнопку нижче, щоб побачити меню.',
            mark='clean',
            parse_mode=None,
            reply_markup=InlineKeyboardMarkup().add(*[
                InlineKeyboardButton(text=generate_menu_text(), callback_data='Menu')
            ])
        )
    else:
        send_message_to_user(
            chat_id=message.chat.id,
            text='Напишіть, як ми можемо до вас звертатися (Iм\'я Прiзвище)',
            mark='clean',
            parse_mode=None,
            reply_markup=ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, save_user_full_name)


def create_user(message: Message) -> None:

    if message.content_type == 'contact':
        delete_message_in_bot(message.chat.id, message.message_id)
        clean_message_chat(message.chat.id, ['clean', 'basket'])

        user_services.create_user(
            telegram_id=message.chat.id,
            phone_number=message.contact.phone_number.replace('+', '')
        )
        get_full_name(message)


def get_full_name(message: Message):
    delete_message_in_bot(message.chat.id, message.message_id)
    clean_message_chat(message.chat.id, ['clean', 'basket'])

    send_message_to_user(
        chat_id=message.chat.id,
        text='Напишіть, як ми можемо до вас звертатися (Iм\'я Прiзвище).',
        mark='clean',
        parse_mode=None,
        reply_markup=ReplyKeyboardRemove()
    )

    bot.register_next_step_handler(message, save_user_full_name)


def send_message_to_user(
        chat_id: int,
        text: str,
        mark: str = None,
        parse_mode: str = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove = None
) -> None:

    try:
        message_sent = bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)
        bot_message_services.create_message(message_sent.chat.id, message_sent.message_id, mark)
    except Exception as e:
        logger.exception(e)