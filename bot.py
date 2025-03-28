import asyncio
import os
import requests
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = os.getenv("BOT_TOKEN", "8146086235:AAFltQPui1QuiEZQyJBL7AowRDzFAvwmFvU")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://nalchik-map-production.up.railway.app")
API_URL = os.getenv("API_URL", "https://nalchik-map-production.up.railway.app")
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1118374415"))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            paid INTEGER DEFAULT 0,
            expires_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

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
            """<b>🔒 Доступ ограничен</b>

Для доступа к карте необходимо оформить подписку.""",
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
    expires = (datetime.now() + timedelta(days=30)).isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, username, paid, expires_at) VALUES (?, ?, 1, ?)",
              (user_id, "—", expires))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Доступ выдан пользователю {user_id} до {expires[:10]}")

async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

