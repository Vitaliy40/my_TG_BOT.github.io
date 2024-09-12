from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from requests2 import get_categories


user_choice = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Продавати товари')],
                                            [KeyboardButton(text='Купляти товари')]], resize_keyboard=True,
                                  input_field_placeholder='Зробіть вибір')

register = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Реєстрація')]], resize_keyboard=True,
                               input_field_placeholder='Нажміть на кнопку')

keyboard_builder = ReplyKeyboardBuilder()

buttons = (KeyboardButton(text='Пошук товарів🔎'), KeyboardButton(text='Корзина🧺'), KeyboardButton(text='Про бота🤖'),
           KeyboardButton(text='Повторна реєстрація🔁'), KeyboardButton(text='Продати товар💳'))

keyboard_builder.add(*buttons)
keyboard_builder.adjust(1, 3)
main_menu = keyboard_builder.as_markup(resize_keyboard=True)
async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))

    keyboard.add(InlineKeyboardButton(text='На головну', callback_data='to_main'))
    return keyboard.adjust(3).as_markup()

async def categories2():
    all_categories = await get_categories()
    keyboard = ReplyKeyboardBuilder()

    for category in all_categories:
        keyboard.add(KeyboardButton(text=category.name))

    keyboard.add(KeyboardButton(text='На головну'))
    return keyboard.adjust(3).as_markup()

