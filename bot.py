import asyncio
from aiogram import Bot

# Вставь свои данные
TELEGRAM_BOT_TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Если канал приватный, вставь его ID в формате "-100XXXXXXXXXX"

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_test_message():
    try:
        await bot.send_message(TELEGRAM_CHANNEL_ID, "✅ Тестовый пост! Бот работает!")
        print("✅ Сообщение успешно отправлено!")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")

async def main():
    await send_test_message()

asyncio.run(main())
