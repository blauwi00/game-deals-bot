import aiohttp
import httpx
import requests
import asyncio
import logging
import random
from aiogram import Bot

# Логирование
logging.basicConfig(level=logging.INFO)

# Steam API URL (получаем список всех игр со скидками)
STEAM_API_URL = "https://store.steampowered.com/api/featuredcategories/"

# Функция получения всех скидок с резервными библиотеками
async def fetch_all_discounts():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(STEAM_API_URL, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logging.warning(f"❌ `aiohttp` не сработал: {e}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(STEAM_API_URL, timeout=10)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logging.warning(f"❌ `httpx` не сработал: {e}")

    try:
        response = requests.get(STEAM_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"❌ `requests` тоже не сработал: {e}")

    return None  # Если вообще ничего не сработало

# Функция обработки всех скидок
async def process_all_discounts():
    data = await fetch_all_discounts()
    if not data:
        return "🚫 Ошибка при получении скидок из Steam."

    all_discounts = []
    for deal in data.get("specials", {}).get("items", []):
        if deal.get("discount_percent", 0) > 0:  # Если есть скидка
            all_discounts.append(
                f"🎮 <b>{deal['name']}</b>\n"
                f"💰 <s>{deal['original_price']}</s> ➡️ {deal['final_price']} {deal['currency']}\n"
                f"🔥 Скидка: {deal['discount_percent']}%\n"
                f"🔗 <a href='{deal['link']}'>Купить в Steam</a>\n"
            )

    if not all_discounts:
        return "🚫 Нет актуальных скидок."

    return all_discounts  # Возвращаем ВСЕ скидки

# Функция выбора случайных 5 игр
async def get_random_discounts():
    all_discounts = await process_all_discounts()
    if isinstance(all_discounts, str):  # Ошибка
        return all_discounts

    random_discounts = random.sample(all_discounts, min(5, len(all_discounts)))  # Выбираем 5 случайных игр
    return "\n".join(random_discounts)

# Функция отправки поста в Telegram
async def send_discount_post(bot, chat_id):
    message = await get_random_discounts()
    post_image = "https://i.imgur.com/AhzG3kO.jpeg"
    await bot.send_photo(chat_id, post_image, caption=message, parse_mode="HTML")

# Основная функция (2 поста на тест)
async def test_run(bot, chat_id):
    for _ in range(2):  # Только для тестов
        await send_discount_post(bot, chat_id)
        await asyncio.sleep(10)

# Запуск бота
async def main():
    TELEGRAM_BOT_TOKEN = "ТОКЕН_БОТА"
    TELEGRAM_CHANNEL_ID = "@gamehunttm"

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await test_run(bot, TELEGRAM_CHANNEL_ID)

asyncio.run(main())