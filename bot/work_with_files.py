import os
from datetime import date
import zipfile
from PIL import Image
import py7zr
from sqlalchemy.exc import IntegrityError
import pandas as pd
from telebot.types import File

from settings import engine, bot
from global_vars import FOLDER_FOR_UNPACK_IMAGES, FOLDER_FOR_SAVING_MANAGER_REPORTS
from bot.services.categories_services import add_categories


def load_file(file_name: str, file_info: File) -> None:
    downloaded_file = bot.download_file(file_info.file_path)

    with open(file_name, 'wb') as f:
        f.write(downloaded_file)


def generate_order_report() -> str:
    stmt = (
        'SELECT o.id as order_id, u.full_name, u.phone_number, g.vendor_code, g.name, g.price, ol.quantity, '
        '(g.price*ol.quantity) as "Total, uah" '
        'FROM order_lines as ol '
        'JOIN orders as o ON ol.order_id = o.id '
        'JOIN users as u ON u.telegram_id = o.telegram_user_id '
        'JOIN goods as g ON g.id = ol.goods_id '
        'WHERE o.paid = true '
        'ORDER BY o.id')

    file_name = f'Замовлення_за_{date.today().strftime("%Y_%m_%d")}.xlsx'
    file_path = os.path.join(FOLDER_FOR_SAVING_MANAGER_REPORTS, file_name)
    print(file_path)
    orders_df = pd.read_sql(stmt, con=engine)
    orders_df.to_excel(file_path, index=False)

    return file_path


def delete_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def handle_images(file_name: str) -> str:

    file_path = os.path.join(os.getcwd(), file_name)

    if file_name.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(FOLDER_FOR_UNPACK_IMAGES)

    elif file_name.endswith('.7z'):
        with py7zr.SevenZipFile(file_path, mode='r') as zip_ref:
            zip_ref.extractall(FOLDER_FOR_UNPACK_IMAGES)

    delete_file(file_path)

    for image in os.listdir(FOLDER_FOR_UNPACK_IMAGES):
        opened_image = Image.open(os.path.join(FOLDER_FOR_UNPACK_IMAGES, image))
        resized_image = opened_image.resize((300, 250))
        resized_image.save(os.path.join(FOLDER_FOR_UNPACK_IMAGES, image))

    reply_to = 'Фото завантаженi успiшно'

    return reply_to


def load_menu(file_name: str) -> str:
    file_path = os.path.join(os.getcwd(), file_name)
    try:
        df = pd.read_excel(file_name, names=['vendor_code', 'name', 'weight', 'category', 'price'])

        df.insert(loc=0, column='id', value=list(range(1, len(df)+1)))
        df['load_date'] = date.today()

        categories = df['category'].unique().tolist()
        categories_dict = dict(zip(categories, range(1, len(categories)+1)))
        add_categories(categories)
        df['category'] = df['category'].apply(lambda x: categories_dict[x])

        df.to_sql('goods', con=engine, if_exists='append', index=False)

        reply_to = ('Меню завантажено успішно.'
                    ' Тепер завантaжте фото страв.'
                    ' Найменування повинне бути таким як її vendor_code.')
    except IntegrityError:
        reply_to = 'Vendor_code повинен бути унiкальним'
    except Exception as e:
        reply_to = 'Некоректний формат меню'

    delete_file(file_path)

    return reply_to






