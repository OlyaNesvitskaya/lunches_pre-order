import time
from datetime import date

from telebot import ExceptionHandler

from telebot.types import (
    CallbackQuery, Message, BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from bot import work_with_files
from bot.basket import adding_dish_to_basket, deleting_dish_in_basket, show_basket
from bot.bot_message import delete_message_in_bot, clean_message_chat
from botlog import logger
from settings import init_db
from global_vars import (
    CALLBACK_PREFIX_FOR_CATEGORIES,
    CALLBACK_PREFIX_FOR_PAY,
    CALLBACK_PREFIX_FOR_DELETING_ORDER_LINE,
    CALLBACK_PREFIX_FOR_GOODS_ORDER
)
from bot.menu import generate_menu_text, generate_menu_keyboard, show_all_dishes_from_selected_category
from bot.order import pay_for_order, show_all_orders
from bot.services import user_services, bot_message_services, categories_services, goods_services
from bot.user import send_message_to_user, create_user, get_full_name
from bot.work_with_files import generate_order_report, load_file
from settings import bot


class ExHandler(ExceptionHandler):
    def handle(self, error):
        logger.exception(error)


bot.exception_handler = ExHandler()
info_command = BotCommand(command='info', description='Iнформацiя')
start_command = BotCommand(command='start', description='Start')
bot.set_my_commands([info_command, start_command])


@bot.message_handler(commands=['info'])
def send_info(message: Message) -> None:
    delete_message_in_bot(message.chat.id, message.message_id)
    clean_message_chat(message.chat.id, ['clean', 'basket'])
    chat_id = message.chat.id
    user = user_services.get_user_by_telegram_id(chat_id)

    if user and user.manager is True:
        file_path = generate_order_report()
        report = open(file_path, 'rb')
        document_sent = bot.send_document(chat_id, report)
        bot_message_services.create_message(document_sent.chat.id, document_sent.message_id, 'clean')
    else:
        send_message_to_user(
            chat_id=chat_id,
            text='Привiт!\nЯ бот для предзамовлень обiдiв.\nСподiваюсь буду тобi корисним.\n'
                 'Замовлення приймаються по будням з 12:00 до 18:00.',
            mark='clean'
        )


@bot.message_handler(commands=['start'])
def send_hello(message: Message) -> None:
    clean_message_chat(message.chat.id, ['clean', 'basket'])

    chat_id = message.chat.id
    user_db = user_services.get_user_by_telegram_id(chat_id)

    if not user_db:
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
        phone_number_button = KeyboardButton(text="Вiдправити номер телефону", request_contact=True)
        keyboard.add(phone_number_button)
        send_message_to_user(
            chat_id=chat_id,
            text='Ласкаво просимо, ми ще не знайомі, будь ласка, дайте мені номер телефону для реєстрації',
            mark='clean',
            parse_mode=None,
            reply_markup=keyboard
        )
        bot.register_next_step_handler(message, create_user)

    elif user_db.phone_number and (not user_db.full_name):
        get_full_name(message)

    else:
        show_menu(message)


@bot.message_handler(commands=['menu'])
def show_menu(message: Message) -> None:
    chat_id = message.chat.id

    if user_services.get_user_by_telegram_id(chat_id):
        if message.entities is not None:
            delete_message_in_bot(chat_id, message.message_id)
            clean_message_chat(chat_id)
        categories = categories_services.get_all_category()

        if categories:
            send_message_to_user(
                chat_id=chat_id,
                text=generate_menu_text(),
                mark='menu',
                parse_mode=None,
                reply_markup=generate_menu_keyboard(categories)
            )
        else:
            send_message_to_user(
                chat_id=chat_id,
                text='Меню ще не завантажено. Зачекайте будь-ласка.',
                mark='clean'
            )


@bot.message_handler(content_types=['text'])
def get_text_message(message: Message) -> None:
    """
        In this handler you can assign or remove a manager.
    """
    chat_id = message.chat.id
    delete_message_in_bot(chat_id, message.message_id)
    clean_message_chat(chat_id, ['clean'])

    if message.text.startswith('appmg-'):
        manager_phone_number = message.text.replace('appmg-', '')
        user = user_services.get_user_by_phone_number(manager_phone_number)
        if user:
            user_services.access_manager(user, is_manager=True)
            send_message_to_user(chat_id=chat_id, text='Менеджер призначений', mark='clean')
        else:
            send_message_to_user(chat_id=chat_id,
                                 text='Користувач з таким номером у нас не зареєстрований',
                                 mark='clean')

    elif message.text.startswith('remmg-'):
        manager_phone_number = message.text.replace('remmg-', '')
        user = user_services.get_user_by_phone_number(manager_phone_number)
        if user:
            user_services.access_manager(user, is_manager=False)
            send_message_to_user(chat_id=chat_id, text='Менеджер відсторонений', mark='clean')
        else:
            send_message_to_user(chat_id=chat_id,
                                 text='Користувач з таким номером у нас не зареєстрований',
                                 mark='clean')


@bot.message_handler(content_types=['document'])
def load_document(message: Message) -> None:
    """
        In this handler you can load menu or image archive that stores images of dishes.
    """
    if user_services.get_manager(message.chat.id):
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)

        delete_message_in_bot(message.chat.id, message.message_id)
        reply_to = 'Цей формат завантажувати не дозволяється'
        if (message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                and file_name == "Меню.xlsx"):

            for goods in goods_services.get_all_goods():
                if goods.load_date == date.today():
                    reply_to = 'Цього дня меню вже завантажено.'
                    break
            else:
                load_file(file_name, file_info)
                reply_to = work_with_files.load_menu(file_name)

            if 'Меню завантажено успішно.' in reply_to:
                users = user_services.get_all_users()
                for user in users:
                    send_message_to_user(
                        chat_id=user.telegram_id,
                        text=generate_menu_text(),
                        mark='menu',
                        reply_markup=generate_menu_keyboard(categories_services.get_all_category())
                    )

        elif file_name == 'Меню.zip' or file_name.endswith('Меню.7z'):
            load_file(file_name, file_info)
            reply_to = work_with_files.handle_images(file_name)

        delete_message_in_bot(message.chat.id, message.message_id)
        clean_message_chat(message.chat.id, ['clean'])

        send_message_to_user(
            chat_id=message.chat.id,
            text=reply_to,
            mark='clean'
        )


@bot.callback_query_handler(func=lambda callback: True)
def check_callback(callback: CallbackQuery) -> None:
    chat_id = callback.message.chat.id

    if not user_services.get_user_by_telegram_id(chat_id):
        send_hello(callback.message)
    else:
        edit_message_reply_markup(bot, callback.message)
        data = callback.data

        if data.startswith(CALLBACK_PREFIX_FOR_CATEGORIES):
            show_all_dishes_from_selected_category(chat_id, data)
            show_menu(callback.message)

        elif data.startswith(CALLBACK_PREFIX_FOR_GOODS_ORDER):
            adding_dish_to_basket(chat_id, data)

        elif data.startswith(CALLBACK_PREFIX_FOR_DELETING_ORDER_LINE):
            deleting_dish_in_basket(chat_id, data)
            show_basket(callback.message)

        elif callback.data.startswith(CALLBACK_PREFIX_FOR_PAY):
            pay_for_order(chat_id, data)

        elif data == 'Basket':
            show_menu(callback.message)
            show_basket(callback.message)

        elif data == 'All_orders':
            show_menu(callback.message)
            show_all_orders(callback.message)

        elif data == 'Menu':
            show_menu(callback.message)


def edit_message_reply_markup(bot, message: Message):

    try:
        reply_markup = message.reply_markup
        if reply_markup is not None and len(reply_markup.keyboard) > 0:
            reply_markup.keyboard[0][0].text = reply_markup.keyboard[0][0].text + ' '
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.id, reply_markup=reply_markup)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":

    init_db()
    logger.info('База данных инициализирована')

    while True:
        try:
            logger.info('Запуск бота')
            bot.polling(none_stop=True, interval=1, timeout=30)

        except Exception as e:
            time.sleep(5)
            logger.error(e)

        continue


