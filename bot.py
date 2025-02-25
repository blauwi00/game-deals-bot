import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Твой токен бота и ID канала
TOKEN = "ТВОЙ_ТОКЕН"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 📌 Создаем клавиатуру с кнопками
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("📜 Список команд"))
keyboard.add(KeyboardButton("🔔 Подписаться на скидки"))
keyboard.add(KeyboardButton("🌎 Выбрать валюту"))

# 📜 Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("👋 Привет! Я бот, который следит за скидками в Steam!\nВыбери действие:", reply_markup=keyboard)

# 📜 Обработчик кнопки "Список команд"
@dp.message_handler(lambda message: message.text == "📜 Список команд")
async def command_list(message: types.Message):
    commands = "📌 Доступные команды:\n" \
               "🔄 /update – обновить скидки\n" \
               "📌 /top – топ-5 скидок\n" \
               "🕵 /find <название> – поиск игры\n" \
               "🎲 /random – случайная скидка\n" \
               "🌎 /currency – выбрать валюту\n" \
               "🔔 /subscribe – подписка на скидки"
    await message.reply(commands)

# 🔔 Обработчик кнопки "Подписаться на скидки"
@dp.message_handler(lambda message: message.text == "🔔 Подписаться на скидки")
async def subscribe(message: types.Message):
    await message.reply("✅ Ты подписан на уведомления! Теперь будешь получать лучшие скидки!")

# 🌎 Обработчик кнопки "Выбрать валюту"
@dp.message_handler(lambda message: message.text == "🌎 Выбрать валюту")
async def choose_currency(message: types.Message):
    await message.reply("🌎 Выбери валюту:\n💵 USD\n💶 EUR\n💴 JPY\n🇷🇺 RUB\n💰 Другую (напиши свою валюту)")

# 🚀 Запуск бота
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)