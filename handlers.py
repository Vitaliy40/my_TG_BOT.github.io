from aiogram import F, Router
from aiogram.types import (Message, CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
                           LabeledPrice, PreCheckoutQuery)

from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboards as kb
from requests2 import (add_info_user_to_db, add_user_to_db, get_category_id_by_name, add_info_item_to_db,
                       get_item_photo_id_by_name, get_item_photo, get_username_by_tg_id, get_tg_id_by_name,
                       get_user_by_tg_id, get_number_cart_by_tg_id, get_items_by_category, update_user_data)
import io

from email.message import EmailMessage
from aiosmtplib import send

async def send_email(text):
    message = EmailMessage()
    message["From"] = "vitalikhudikz@gmail.com"
    message["To"] = "dyraksobaka0@gmail.com"
    message["Subject"] = "Оплата успішна"
    message.set_content(f"Оплата пройшла успішно!\n{text}")

    await send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        username="vitalikhudikz@gmail.com",
        password="imnm vmki whzn balj",
        start_tls=True
    )


def get_bot_and_token():
    from main import bot, API_TOKEN
    return bot, API_TOKEN

def get_bot():
    from main import bot
    return bot


user_item_index = {}
class Register(StatesGroup):
    name = State()
    user_name = State()
    user_cart_number = State()

class Change_Register(StatesGroup):
    new_name = State()
    new_card_number = State()
    new_user_name = State()
class Sell_Item(StatesGroup):
    name_item = State()
    description = State()
    price = State()
    item_photo = State()
    category = State()


photo_bytes = None

router = Router()

async def is_user_registered(tg_id: int) -> bool:
    user = await get_user_by_tg_id(tg_id)
    return user is not None

@router.message(CommandStart())
async def start(message: Message):
    await add_user_to_db(tg_id=message.from_user.id)
    await message.answer('Вітаю вас у нашому магазині Easy Buy!\nВи плануєте купляти товари чи продавати?',
                         reply_markup=kb.user_choice)

# Перший варіант якщо користувач хоче продавати товари:

@router.message(F.text == 'Продавати товари')
async def start(message: Message):
    await message.answer('Добре, тоді пропоную вам спочатку зареєструватися', reply_markup=kb.register)

@router.message(F.text == 'Реєстрація')
async def start_register(message: Message, state: FSMContext):
    if await is_user_registered(message.from_user.id):
        await message.answer("Ви вже зареєстровані.", reply_markup=kb.main_menu)
        return
    await state.set_state(Register.name)
    await message.answer("Для початку введіть своє ім'я")

@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.user_name)
    await message.answer("Чудово. Тепер введіть своє телеграм-ім'я(для прикладу:@user)")


@router.message(Register.user_name)
async def register_user_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await state.set_state(Register.user_cart_number)
    await message.answer("Чудово! Тепер введіть номер вашої картки")


@router.message(Register.user_cart_number)
async def register_cart_number(message: Message, state: FSMContext):

    user_cart_number = message.text

    if not user_cart_number.isdigit():
        await message.answer("Номер картки має містити тільки цифри. Спробуйте ще раз.")
        return

    user_data = await state.get_data()
    name = user_data.get("name")
    user_name = user_data.get("user_name")

    await add_info_user_to_db(
        username=user_name,
        user_cart_number=user_cart_number,
        tg_id=message.from_user.id
    )

    await message.answer(f"Ваша реєстрація завершена.\nВаше ім'я: {name};"
                         f"\nВаше телеграм-ім'я: {user_name};\nНомер картки: {user_cart_number}.",
                         reply_markup=kb.main_menu)
    await state.clear()

@router.message(F.text == 'Пошук товарів🔎')
async def category_selection(message: Message):
    await message.answer('Спочатку виберіть категорію товару', reply_markup=await kb.categories())


@router.message(F.text == 'Повторна реєстрація🔁')
async def user_changes_register(message: Message, state: FSMContext):
    await state.set_state(Change_Register.new_name)
    await message.answer("Введіть нове ім'я")

@router.message(Change_Register.new_name)
async def new_name(message: Message, state: FSMContext):
    await state.update_data(new_name=message.text)
    await state.set_state(Change_Register.new_user_name)
    await message.answer("Тепер введіть своє нове телеграм-ім'я")

@router.message(Change_Register.new_user_name)
async def new_username(message: Message, state: FSMContext):
    await state.update_data(new_user_name=message.text)
    await state.set_state(Change_Register.new_card_number)
    await message.answer('Тепер надішліть новий номер карточки')

@router.message(Change_Register.new_card_number)
async def new_card_number(message: Message, state: FSMContext):
    new_card_number = message.text

    if not new_card_number.isdigit():
        await message.answer('Номер карточки повинен містити тільки цифри')
        return

    user_data = await state.get_data()
    new_name = user_data.get('new_name')
    new_user_name = user_data.get('new_user_name')

    await update_user_data(tg_id=message.from_user.id,
                           new_name=new_name,
                           new_card_number=new_card_number,
                           new_user_name=new_user_name)

    await message.answer(f"Ваша реєстрація завершена.\nВаше ім'я: {new_name};"
                         f"\nВаше телеграм-ім'я: {new_user_name};\nНомер картки: {new_card_number}.",
                         reply_markup=kb.main_menu)
    await state.clear()

# якщо користувач хоче купляти товари:

@router.message(F.text == 'Купляти товари')
async def start_2(message: Message):
    await message.answer('Ви в головному меню', reply_markup=kb.main_menu)

@router.message(F.text == 'Продати товар💳')
async def sell_item(message: Message, state: FSMContext):
    await state.set_state(Sell_Item.name_item)
    await message.answer("Введіть ім'я товару")

@router.message(Sell_Item.name_item)
async def item_price(message: Message, state: FSMContext):
    await state.update_data(name_item=message.text)
    await state.set_state(Sell_Item.price)
    await message.answer('Введіть ціну вашого товару')

@router.message(Sell_Item.price)
async def item_description(message: Message, state: FSMContext):
    price = message.text
    if not price.isdigit():
        await message.answer('Ціна товару має містити числа')
        return
    else:
        await state.update_data(price=price)
        await state.set_state(Sell_Item.description)
        await message.answer('Введіть короткий опис вашого товару')

@router.message(Sell_Item.description)
async def item_Photo(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(Sell_Item.item_photo)
    await message.answer('Тепер відправте фото вашого товару')

@router.message(Sell_Item.item_photo)
async def item_category(message: Message, state: FSMContext):
    global photo_bytes
    if not message.photo:
        await message.answer("Будь ласка, надішліть фото.")
        return

    if len(message.photo) < 2:
        await message.answer("Будь ласка, надішліть фото в достатньому розмірі.")
        return

    item_photo = message.photo[-1]
    await state.update_data(item_photo=item_photo)
    file_info = await message.bot.get_file(item_photo.file_id)
    file = await message.bot.download_file(file_info.file_path)

    photo_bytes = file.read()
    await state.update_data(item_photo=photo_bytes)

    await message.answer('Виберіть категорію товару', reply_markup=await kb.categories2())
    await state.set_state(Sell_Item.category)

@router.message(Sell_Item.category)
async def end_sell(message: Message, state: FSMContext):
    category_name = message.text
    if category_name not in ['Одяг', 'Взуття', 'Електроніка та гаджети', 'Меблі та товари для дому', 'Іграшки',
                             'Автотовари', 'Книги та медіа', 'Продукти харчування', 'Інше']:
        await message.answer("Будь ласка, виберіть категорію, натиснувши на кнопку.")
        return

    category = await get_category_id_by_name(category_name)

    item_data = await state.get_data()
    name = item_data.get("name_item")
    description = item_data.get("description")
    price = item_data.get("price")
    item_photo = item_data.get("item_photo")


    try:
        await add_info_item_to_db(name=name, description=description, price=price, category=category,
                                  item_photo=item_photo, tg_id=message.from_user.id)
    except ValueError as e:
        await message.answer(str(e))

    item_id = await get_item_photo_id_by_name(name)
    photo_bytes = await get_item_photo(item_id)

    photo = io.BytesIO(photo_bytes)
    photo.seek(0)
    input_file = BufferedInputFile(photo.read(), filename="photo.jpg")
    user_name = await get_username_by_tg_id(tg_id=message.from_user.id)
    user_cart_number = await get_number_cart_by_tg_id(tg_id=message.from_user.id)
    await message.answer_photo(input_file, caption=f"Назва товару: {name}\nЦіна товару: {price}грн"
                                                   f"\nОпис товару: {description}"
                                                   f"\nІнформація про продавця цього товару:"
                                                   f"\nUsername користувача: {user_name}"
                                                   f"\nНомер карточки: {user_cart_number}")

    await state.clear()

@router.message(F.text == 'На головну')
async def menu(message: Message):
    await message.answer('Ви зараз в головному меню', reply_markup=kb.main_menu)

@router.message(F.text == 'Пошук товарів🔎')
async def search_item(message: Message):
    await message.answer('Виберіть категорію товару', reply_markup=await kb.categories())

@router.callback_query(F.data.startswith('category_'))
async def show_items(callback: CallbackQuery):
    try:
        category_id = int(callback.data.split('_')[1])
    except IndexError:
        await callback.answer("Неправильний формат даних.")
        return
    items = await get_items_by_category(category_id)
    user_id = callback.from_user.id

    if items:
        user_item_index[user_id] = 0
        item = items[0]

        tg_id = await get_tg_id_by_name(name=item.name)

        user_name = await get_username_by_tg_id(tg_id=tg_id)
        user_cart_number = await get_number_cart_by_tg_id(tg_id=tg_id)
        item_id = await get_item_photo_id_by_name(item.name)
        photo_bytes = await get_item_photo(item_id)
        photo = io.BytesIO(photo_bytes)
        photo.seek(0)
        input_file = BufferedInputFile(photo.read(), filename="photo.jpg")

        search_process = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton
                                                                (text='Оплатити💵',
                                                                 callback_data=f'Pay_{category_id}')],
                                                               [InlineKeyboardButton
                                                                (text='Додати до корзини🧺', callback_data='tray')],
                                                               [InlineKeyboardButton
                                                                (text='Наступний товар➡️',
                                                                 callback_data=f'next_item_{category_id}')]],
                                              resize_keyboard=True)

        await callback.message.answer_photo(input_file, caption=f"Назва товару: {item.name}"
                                                                f"\nЦіна товару: {item.price}грн"
                                                                f"\nОпис товару: {item.description}"
                                                                f"\nІнфо про продавця:"
                                                                f"\nUsername користувача: {user_name}"
                                                                f"\nНомер карточки користувача: {user_cart_number}",
                                            reply_markup=search_process)
    else:
        await callback.message.answer('Нажаль товар не було знайдено, або в цій категорії немає товарів')

@router.callback_query(F.data.startswith('next_item_'))
async def show_next_item(callback: CallbackQuery):
    try:
        category_id = int(callback.data.split('_')[2])
    except IndexError:
        await callback.answer("Неправильний формат даних.")
        return
    items = await get_items_by_category(category_id)
    user_id = callback.from_user.id

    if user_id in user_item_index:
        user_item_index[user_id] += 1

        if user_item_index[user_id] >= len(items):
            user_item_index[user_id] = 0

        current_index = user_item_index[user_id]
        item = items[current_index]

        tg_id = await get_tg_id_by_name(name=item.name)
        user_name = await get_username_by_tg_id(tg_id=tg_id)
        user_cart_number = await get_number_cart_by_tg_id(tg_id=tg_id)
        item_id = await get_item_photo_id_by_name(item.name)
        photo_bytes = await get_item_photo(item_id)
        photo = io.BytesIO(photo_bytes)
        photo.seek(0)
        input_file = BufferedInputFile(photo.read(), filename="photo.jpg")

        search_process = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton
                                                                (text='Оплатити💵',
                                                                 callback_data=f'Pay_{category_id}')],
                                                               [InlineKeyboardButton
                                                                (text='Додати до корзини🧺', callback_data='tray')],
                                                               [InlineKeyboardButton
                                                                (text='Наступний товар➡️',
                                                                 callback_data=f'next_item_{category_id}')],
                                                               [InlineKeyboardButton(text='До меню',
                                                                                     callback_data='to_main')]],
                                              resize_keyboard=True)

        await callback.message.answer_photo(input_file, caption=f"Назва товару: {item.name}"
                                                      f"\nЦіна товару: {item.price}грн"
                                                      f"\nОпис товару: {item.description}"
                                                      f"\nІнфо про продавця:"
                                                      f"\nUsername користувача: {user_name}"
                                                      f"\nНомер карточки користувача: {user_cart_number}",
                                            reply_markup=search_process)

@router.callback_query(F.data.startswith('Pay_'))
async def pay_for_item(callback: CallbackQuery):
    try:
        parts = callback.data.split('_')

        if len(parts) != 2:
            raise IndexError("Помилка: недостатньо частин у callback.data")

        category_id = int(parts[1])
    except IndexError:
        await callback.answer("Помилка в даних запиту.")
        return
    except ValueError:
        await callback.answer("Невірний формат даних.")
        return

    bot, API_TOKEN = get_bot_and_token()
    user_id = callback.from_user.id
    item_index = user_item_index.get(user_id, 0)
    CURRENCY = "UAH"
    items = await get_items_by_category(category_id)
    item = items[item_index]

    prices = [LabeledPrice(label=item.name, amount=item.price * 100)]

    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=item.name,
        description=item.description,
        payload='payment_payload',
        provider_token=API_TOKEN,
        start_parameter='test-payment',
        currency=CURRENCY,
        prices=prices,
        need_name=True,  # Запит імені користувача
        need_phone_number=True,  # Запит номера телефону
        need_email=True,  # Запит електронної пошти
        need_shipping_address=True  # Запит адреси доставки
    )

@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    bot = get_bot()
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.content_type == 'successful_payment')
async def successful_payment_handler(message: Message):
    payment_info = message.successful_payment
    currency = payment_info.currency
    total_amount = payment_info.total_amount / 100
    order_info = payment_info.order_info
    name = order_info.name if order_info.name else "Не вказано"
    phone = order_info.phone_number if order_info.phone_number else "Не вказано"
    shipping_address = order_info.shipping_address

    if shipping_address:
        city = shipping_address.city if shipping_address.city else "Місто не вказано"
        address = (
            f"{shipping_address.country_code}, "
            f"{shipping_address.state}, "
            f"{city}, "
            f"{shipping_address.street_line1}, "
            f"{shipping_address.street_line2 if shipping_address.street_line2 else ''}, "
            f"{shipping_address.post_code}"
        )
    else:
        city = "Місто не вказано"
        address = "Адреса не вказана"

    await message.answer("Дякуємо за вашу оплату!", reply_markup=kb.main_menu)
    text = (f'Ось інфо про покупця:\nЦіна товару становила: {total_amount}{currency}\nІмя покупця: {name}'
            f'\nНомер телефону користувача: {phone}\nАдреса: {city}')

    await send_email(text)

@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.message.answer('Ви в головному меню', reply_markup=kb.main_menu)



















