from pandas import DataFrame
from telebot.types import Message

from bot.basket import generate_basket_table
from bot.bot_message import clean_message_chat, delete_message_in_bot
from global_vars import CALLBACK_PREFIX_FOR_PAY
from bot.services import order_services, bot_message_services, user_services
from bot.user import send_message_to_user
from settings import bot


def pay_for_order(chat_id: int, order_id_and_payment_amount_with_prefix: str) -> None:
    order_id, payment_amount = order_id_and_payment_amount_with_prefix.replace(
                        CALLBACK_PREFIX_FOR_PAY, '').split('-')
    clean_message_chat(chat_id, marks=['invoice'])
    '''
    correct_payment = int(payment_amount) * 100
    try:
        res = bot.send_invoice(
            chat_id,
            title='Оплатить ' + str(payment_amount) + '',
            description='_',
            provider_token='410694247:TEST:fc6c3e76-48a2-4855-bed5-f83fe437014b',
            currency='uah',
            prices=[LabeledPrice("title", correct_payment)],
            start_parameter='time-machine-example',
            invoice_payload='some-invoice-payload-for-our-internal-use'
        )
        services.create_message(res.chat.id, res.message_id, 'invoice')
    except Exception as e:
        logger.error(e)'''
    order_services.set_paid_in_order(int(order_id))
    sending_message = bot.send_message(chat_id, text='Оплата пройшла успiшно')
    bot_message_services.create_message(sending_message.chat.id, sending_message.message_id, 'clean')
    send_notification_to_manager_about_new_order(order_id)
    clean_message_chat(sending_message.chat.id, ['basket', 'invoice'])


def show_all_orders(message: Message) -> None:
    delete_message_in_bot(message.chat.id, message.message_id)
    clean_message_chat(message.chat.id, ['clean', 'basket'])
    chat_id = message.chat.id
    orders = order_services.get_cart(chat_id, paid=True)

    if orders:

        df = DataFrame(orders)
        for i, v in df.groupby('id'):
            price, table = generate_basket_table(v.values.tolist())
            text = (f'Замовлення на сумму {price} грн.'
                    f' <pre>{table}</pre>')

            send_message_to_user(
                chat_id=chat_id,
                text=text,
                mark='clean',
                parse_mode='HTML',
            )
    else:
        send_message_to_user(
            chat_id=chat_id,
            text='Наразi у вас немає оплачених замовлень.',
            mark='clean'
        )


def send_notification_to_manager_about_new_order(order_id: int) -> None:
    text = f'Створено нове замовлення № {order_id}.'
    managers = user_services.get_managers()

    for manager in managers:
        send_message_to_user(
            chat_id=manager.telegram_id,
            text=text,
            mark='clean'
        )