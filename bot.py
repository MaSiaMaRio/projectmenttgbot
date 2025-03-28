import asyncio
import os
import requests
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.getenv("BOT_TOKEN", "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nalchik-map-production.up.railway.app")
API_URL = os.getenv("API_URL", "https://nalchik-map-production.up.railway.app")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1118374415"))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(lambda message: message.text == "/start")
async def handle_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "—"

    try:
        response = requests.get(f"{API_URL}/check_access", params={"user_id": user_id})
        access = response.json().get("access", False)
    except:
        access = False

    if access:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗺 Открыть карту", web_app=WebAppInfo(url=WEBAPP_URL))]
        ])
        await message.answer(f"Добро пожаловать! Ваш user_id: {user_id}", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить доступ", url="https://t.me/YourPaymentBot")]
        ])
        await message.answer(
            f"<b>🔒 Доступ ограничен</b>\n\nВаш user_id: {user_id}",
            reply_markup=kb
        )

@dp.message(lambda message: message.text.startswith("/give"))
async def give_access(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Нет доступа")

    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("❗ Используй: /give <user_id>")

    user_id = parts[1]
    username = "—"
    expires = (datetime.now() + timedelta(days=30)).isoformat()

    try:
        response = requests.post(f"{API_URL}/set_access", json={
            "user_id": user_id,
            "username": username,
            "expires_at": expires
        })
        if response.status_code == 200:
            await message.answer(f"✅ Доступ выдан пользователю {user_id} до {expires[:10]}")
        else:
            await message.answer("❌ Ошибка при передаче доступа на сервер")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
