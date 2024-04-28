import os
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.bot_message import clean_message_chat
from botlog import logger
from global_vars import CALLBACK_PREFIX_FOR_CATEGORIES, FOLDER_FOR_UNPACK_IMAGES, CALLBACK_PREFIX_FOR_GOODS_ORDER
from bot.services import categories_services, bot_message_services
from settings import bot


def generate_menu_text() -> str:
    text = '🍞🍅🥒🧀🥦🌶️ МЕНЮ 🍞🍅🥒🧀🥦🌶️'
    return text


def generate_menu_keyboard(categories: list) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=category,
            callback_data=''.join((CALLBACK_PREFIX_FOR_CATEGORIES, category))) for category in categories
    ]
    basket = InlineKeyboardButton(text='🛒 Кошик', callback_data='Basket')
    all_orders = InlineKeyboardButton(text='✅ Мої замовлення', callback_data='All_orders')
    markup_inline = InlineKeyboardMarkup()
    markup_inline.add(*buttons)
    markup_inline.add(basket, all_orders)

    return markup_inline


def show_all_dishes_from_selected_category(chat_id: int, category_with_prefix: str) -> None:
    clean_message_chat(chat_id, ['clean', 'basket', 'invoice'])
    category = category_with_prefix.replace(CALLBACK_PREFIX_FOR_CATEGORIES, '')
    dishes_list = categories_services.get_dishes_from_category(category).goodss
    for dish in dishes_list:
        food_image = os.listdir(FOLDER_FOR_UNPACK_IMAGES)
        image_name = [image for image in food_image if image.startswith(dish.vendor_code)]
        image_name = image_name[0] if image_name else os.path.join(FOLDER_FOR_UNPACK_IMAGES, 'НЕТ ФОТО.png')
        with open(os.path.join(FOLDER_FOR_UNPACK_IMAGES, image_name), 'rb') as image:
            buttons = (
                        InlineKeyboardButton(
                            text='Замовити',
                            callback_data=''.join((CALLBACK_PREFIX_FOR_GOODS_ORDER, dish.vendor_code))
                        ),
            )
            try:
                photo_sent = bot.send_photo(
                    chat_id,
                    image,
                    caption=f'<b>{dish.name}</b>, {dish.weight}\n\n<b>Цiна:</b> {dish.price} грн.',
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(row_width=2).add(*buttons),
                )
                bot_message_services.create_message(photo_sent.chat.id, photo_sent.message_id, 'clean')
            except Exception as e:
                logger.error(e)

    clean_message_chat(chat_id, ['menu'])

