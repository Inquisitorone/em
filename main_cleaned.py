
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
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
    confirmation = State()

@dp.message_handler(commands="start")
async def start_cmd(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Українська", "Русский", "English")
    await message.answer("Оберіть мову / Выберите язык / Choose language", reply_markup=kb)
    await OrderState.language.set()

@dp.message_handler(state=OrderState.language)
async def set_language(message: types.Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer("Введіть місто:")
    await OrderState.city.set()

# ... другие обработчики ...

@dp.message_handler(state=OrderState.order_number)
async def order_number(message: types.Message, state: FSMContext):
    await state.update_data(order_number=message.text)
    data = await state.get_data()
    summary = (
        f"Мова: {data['language'].upper()}
"
        f"Місто: {data['city']}
"
        f"VIN: {data['vin']}
"
        f"Dlink: {data['dlink']}
"
        f"Модель: {data['model']}
"
        f"Мова мультимедіа: {data['multimedia_lang']}
"
        f"Менеджер: {data['manager_name']}
"
        f"Телефон: {data['manager_phone']}
"
        f"Номер замовлення: {data['order_number']}"
    )
    confirm_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Скасувати")
    await message.answer("Перевірте дані:
" + summary, reply_markup=confirm_kb)
    await OrderState.confirmation.set()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
