import prettytable as pt
from typing import List
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.bot_message import clean_message_chat, delete_message_in_bot
from global_vars import CALLBACK_PREFIX_FOR_PAY, CALLBACK_PREFIX_FOR_DELETING_ORDER_LINE, \
    CALLBACK_PREFIX_FOR_GOODS_ORDER
from bot.services import goods_services, order_services, order_line_services
from bot.user import send_message_to_user


def generate_basket_table(data: List[tuple]) -> tuple[int, pt.PrettyTable]:
    table = pt.PrettyTable(['№', 'Страва', 'К-сть', 'Цiна, од.', 'Сума'])
    table.align['Страва'] = 'l'
    table.border = False
    table.header_style = 'upper'
    order_price = 0

    for index, row in enumerate(data, start=1):
        order_price += row[3] * row[2]
        name = row[1] if len(row[1]) < 15 else "".join((row[1][:12], '...'))
        table.add_row([index, name, row[2], row[3], row[4]])

    return order_price, table


def show_basket(message: Message) -> None:
    if message.caption is None:
        delete_message_in_bot(message.chat.id, message.message_id)
        clean_message_chat(message.chat.id, ['clean'])

    user_telegram_id = message.chat.id
    order_db = order_services.get_order(user_telegram_id)

    if not order_db:
        send_message_to_user(message.chat.id, 'Страви ще не вибранi(', 'clean')
    else:
        ordered_dishes = order_services.get_cart(user_telegram_id)
        order_price, table = generate_basket_table(ordered_dishes)
        delete_buttons = [
            InlineKeyboardButton(
                text=index,
                callback_data=''.join((CALLBACK_PREFIX_FOR_DELETING_ORDER_LINE, str(line[0]))))
            for index, line in enumerate(ordered_dishes, start=1)
        ]
        pay_button = InlineKeyboardButton(
            text=f'Оплатити 💳\n({order_price} грн.)',
            callback_data="".join((CALLBACK_PREFIX_FOR_PAY, str(order_db.id), '-', str(order_price))))

        markup_inline = InlineKeyboardMarkup(row_width=8)
        markup_inline.add(*delete_buttons)
        markup_inline.row(*[pay_button])

        clean_message_chat(message.chat.id, marks=['basket', 'invoice'])

        text = (f'Замовляете ще ➡️ корзина оновлюватиметься.\nПеревiрка замовлення ➡️ перехiд до оплати.'
                f' <pre>{table}</pre>'
                f' Будь-яку страву в замовленнi можна видалити за вiдповiдним номером в заказi.🔻🔻🔻')

        send_message_to_user(
            chat_id=message.chat.id,
            text=text,
            mark='basket',
            parse_mode='HTML',
            reply_markup=markup_inline
        )


def adding_dish_to_basket(chat_id: int, vendor_code_with_prefix: str) -> None:
    vendor_code = vendor_code_with_prefix.replace(CALLBACK_PREFIX_FOR_GOODS_ORDER, '')
    order_db = order_services.get_order(chat_id)
    goods_db = goods_services.get_goods(vendor_code)

    if order_db:
        db_order_lines = order_line_services.get_order_lines(order_db.id)
        needed_order_line = [line for line in db_order_lines if line.goods_id == goods_db.id]

        if needed_order_line:
            order_line_services.change_quantity_in_order_line(needed_order_line[0],
                                                              needed_order_line[0].quantity + 1)
        else:
            order_line_services.add_order_line(order_id=order_db.id, goods_id=goods_db.id, quantity=1)
    else:
        order_db = order_services.create_order(chat_id)
        order_line_services.add_order_line(order_id=order_db.id, goods_id=goods_db.id, quantity=1)

    send_message_to_user(chat_id, f'<b>+ {goods_db.name}</b>', 'clean', parse_mode='HTML')


def deleting_dish_in_basket(chat_id: int, order_line_id_with_prefix: str) -> None:
    order_line_id = int(order_line_id_with_prefix.replace(CALLBACK_PREFIX_FOR_DELETING_ORDER_LINE, ''))

    order_line_db = order_line_services.get_order_line(order_line_id)
    order_line_services.delete_order_line(order_line_db)

    order_db = order_services.get_order(chat_id)
    order_lines_db = order_line_services.get_order_lines(order_db.id)

    if len(order_lines_db) == 0:
        order_services.delete_order(order_db)

    clean_message_chat(chat_id, marks=['invoice'])
