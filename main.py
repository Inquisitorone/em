
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Set TELEGRAM_API_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class OrderState(StatesGroup):
    language = State()
    city = State()
    vin = State()
    dlink = State()
    model = State()
    multimedia_lang = State()
    manager_name = State()
    manager_phone = State()
    order_number = State()
    confirm = State()

LANGUAGES = {"Українська": "ua", "Русский": "ru", "English": "en"}

CITIES = [
    "Вінниця", "Дніпро", "Житомир", "Запоріжжя", "Івано-Франківськ", "Київ", "Кропивницький",
    "Луцьк", "Львів", "Миколаїв", "Одеса", "Полтава", "Рівне", "Суми", "Тернопіль",
    "Ужгород", "Харків", "Херсон", "Хмельницький", "Черкаси", "Чернівці", "Чернігів"
]

DLINK_MODELS = {
    "Dlink 3": ["Qin Plus DM-i, EV", "Song Pro", "Yuan Plus", "Song Max", "Destroyer 05", "Dolphins", "Tang Dm-i"],
    "Dlink 4": ["Han 22", "Tang 22", "Song Plus", "Song Champ", "Frigate 07", "Seal EV"],
    "Dlink 5": ["Song Plus", "Song L DMI", "Seal", "Sealion 07"]
}

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    buttons = [types.KeyboardButton(text=lang) for lang in LANGUAGES]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons)
    await message.answer("Оберіть мову / Choose language / Выберите язык:", reply_markup=keyboard)
    await OrderState.language.set()

@dp.message_handler(state=OrderState.language)
async def set_language(message: types.Message, state: FSMContext):
    if message.text not in LANGUAGES:
        return await message.reply("Будь ласка, оберіть мову з клавіатури.")
    await state.update_data(language=LANGUAGES[message.text])
    lang = LANGUAGES[message.text]
    greeting = {
        "ua": "Вас вітає Бот компанії ЕM. Я створений для допомоги в комунікації між менеджерами та виконавцем послуг.",
        "ru": "Вас приветствует Бот компании ЕМ. Я создан для помощи в коммуникации между менеджерами и исполнителем услуг.",
        "en": "Welcome to EM Company Bot. I am designed to assist in communication between managers and service providers."
    }
    await message.answer(greeting[lang], reply_markup=types.ReplyKeyboardRemove())

    cities_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in CITIES:
        cities_kb.add(types.KeyboardButton(text=city))
    await message.answer("Оберіть місто:", reply_markup=cities_kb)
    await OrderState.city.set()

@dp.message_handler(state=OrderState.city)
async def set_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Введіть VIN код:", reply_markup=types.ReplyKeyboardRemove())
    await OrderState.vin.set()

@dp.message_handler(state=OrderState.vin)
async def set_vin(message: types.Message, state: FSMContext):
    await state.update_data(vin=message.text)
    dlink_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    dlink_kb.add("Dlink 3", "Dlink 4", "Dlink 5")
    await message.answer("Оберіть версію мультимедіа:", reply_markup=dlink_kb)
    await OrderState.dlink.set()

@dp.message_handler(state=OrderState.dlink)
async def set_dlink(message: types.Message, state: FSMContext):
    if message.text not in DLINK_MODELS:
        return await message.reply("Будь ласка, оберіть Dlink із запропонованих.")
    await state.update_data(dlink=message.text)
    model_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for model in DLINK_MODELS[message.text]:
        model_kb.add(model)
    await message.answer("Оберіть модель автомобіля:", reply_markup=model_kb)
    await OrderState.model.set()

@dp.message_handler(state=OrderState.model)
async def set_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    lang_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("UA", "RU")
    await message.answer("Оберіть мову встановлення мультимедіа:", reply_markup=lang_kb)
    await OrderState.multimedia_lang.set()

@dp.message_handler(state=OrderState.multimedia_lang)
async def set_multimedia_lang(message: types.Message, state: FSMContext):
    await state.update_data(multimedia_lang=message.text)
    await message.answer("Введіть ПІБ менеджера:", reply_markup=types.ReplyKeyboardRemove())
    await OrderState.manager_name.set()

@dp.message_handler(state=OrderState.manager_name)
async def set_manager_name(message: types.Message, state: FSMContext):
    await state.update_data(manager_name=message.text)
    await message.answer("Введіть номер телефону менеджера:")
    await OrderState.manager_phone.set()

@dp.message_handler(state=OrderState.manager_phone)
async def set_manager_phone(message: types.Message, state: FSMContext):
    await state.update_data(manager_phone=message.text)
    skip_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Пропустити")
    await message.answer("Введіть номер замовлення або натисніть 'Пропустити':", reply_markup=skip_kb)
    await OrderState.order_number.set()

@dp.message_handler(state=OrderState.order_number)
async def set_order_number(message: types.Message, state: FSMContext):
    if message.text != "Пропустити":
        await state.update_data(order_number=message.text)
    else:
        await state.update_data(order_number="Немає")
    data = await state.get_data()
    summary = (
        f"Мова: {data['language'].upper()}"
"
        f"Місто: {data['city']}"
"
        f"VIN: {data['vin']}"
"
        f"Dlink: {data['dlink']}"
"
        f"Модель: {data['model']}"
"
        f"Мова мультимедіа: {data['multimedia_lang']}"
"
        f"Менеджер: {data['manager_name']}"
"
        f"Телефон: {data['manager_phone']}"
"
        f"Номер замовлення: {data['order_number']}"
    )
    confirm_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Скасувати")
    await message.answer("Перевірте дані:
" + summary, reply_markup=confirm_kb)
    await OrderState.confirm.set()

@dp.message_handler(state=OrderState.confirm)
async def confirm_order(message: types.Message, state: FSMContext):
    if message.text == "Підтвердити":
        await message.answer("Замовлення збережено. Дякуємо!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Операцію скасовано.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
