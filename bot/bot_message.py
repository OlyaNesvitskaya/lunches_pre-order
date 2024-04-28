from botlog import logger
from bot.services import bot_message_services
from settings import bot


def delete_message_in_bot(chat_id: int, message_id: int) -> None:

    try:
        is_deleted_message = bot.delete_message(chat_id, message_id)
    except Exception as e:
        is_deleted_message = str(e).find('message to delete not found') > 0
        if not is_deleted_message:
            logger.exception(f'Не удалось удалить сообщение {str(e)}')

    if is_deleted_message:
        bot_message_services.delete_by_chat_id_and_message_id(chat_id, message_id)


def clean_message_chat(chat_id: int, marks: list = None) -> None:
    messages = bot_message_services.get_message(chat_id, marks)
    for message in messages:
        delete_message_in_bot(chat_id, message.message_id)
        bot_message_services.delete_message(message)