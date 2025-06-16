import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Set TELEGRAM_API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"Echo: {message.text}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True
@dp.message_handler(state=OrderState.order_number)
async def set_order_number(message: types.Message, state: FSMContext):
    if message.text != "Пропустити":
        await state.update_data(order_number=message.text)
    else:
        await state.update_data(order_number="Немає")
    data = await state.get_data()
    summary = (
        f"Мова: {data['language'].upper()}\n"
        f"Місто: {data['city']}\n"
        f"VIN: {data['vin']}\n"
        f"Dlink: {data['dlink']}\n"
        f"Модель: {data['model']}\n"
        f"Мова мультимедіа: {data['multimedia_lang']}\n"
        f"Менеджер: {data['manager_name']}\n"
        f"Телефон: {data['manager_phone']}\n"
        f"Номер замовлення: {data['order_number']}"
    )
    confirm_kb = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Підтвердити", "Скасувати")
    await message.answer(f"Перевірте дані:\n\n{summary}", reply_markup=confirm_kb)
    await OrderState.confirm.set()

)