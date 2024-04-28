import time
import schedule

from settings import bot
from bot.user import send_message_to_user
from bot.bot_message import clean_message_chat
from bot.services import user_services, different_services, bot_message_services
from bot.work_with_files import generate_order_report


def update_system() -> None:
    all_users = user_services.get_all_users()

    for user in all_users:
        chat_id = user.telegram_id
        clean_message_chat(chat_id, ['clean', 'menu', 'basket', 'invoice'])
        if user.manager:
            file_path = generate_order_report()
            report = open(file_path, 'rb')
            document_sent = bot.send_document(chat_id, report)
            bot_message_services.create_message(document_sent.chat.id, document_sent.message_id, 'clean')
        else:
            send_message_to_user(
                chat_id=chat_id,
                text='Наступне меню з\'явиться завтра пiсля 10 години ранку',
                mark='clean'
            )

        [
            different_services.truncate_table(table)
            for table in
            ('order_lines', 'orders', 'goods', 'goods_categories')
         ]


def schedule_actions():
    schedule.every().day.at('18:00').do(update_system)
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule_actions()
