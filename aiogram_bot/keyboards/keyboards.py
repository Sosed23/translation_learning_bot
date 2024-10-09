from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, InlineKeyboardMarkup
# from database.query import get_categories
# from database.query_postgresql import get_categories, get_category_product


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Обучение'),
                                     KeyboardButton(text='Перевод')]],
                           #  [KeyboardButton(text='📁 Оформить заказ'),
                           #   KeyboardButton(text='☎️ Контакты')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')
