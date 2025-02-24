import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

# Токен бота и ID канала
TELEGRAM_BOT_TOKEN = "7934109371:AAFFYbz1eFHzKAANo_60YInoCwlLY-wQUrU"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или -100XXXXXXXXXX для приватного канала

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Функция отправки чисел от 1 до 100
async def send_numbers():
    for number in range(1, 101):  # Отправляем числа от 1 до 100
        await bot.send_message(TELEGRAM_CHANNEL_ID, f"{number}")
        await asyncio.sleep(5)  # Пауза 5 секунд между постами (можно изменить)

# Запуск бота
async def main():
    await send_numbers()  # Запускаем отправку чисел

asyncio.run(main())
