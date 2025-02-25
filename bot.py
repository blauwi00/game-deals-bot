import asyncio
import logging
import random
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

# 🔹 Задаём параметры бота
TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"
STEAM_API_URL = "https://store.steampowered.com/api/featuredcategories/"
POSTER_URL = "https://i.imgur.com/AhzG3kO.jpeg"  # Твой постер

# 🔹 Логирование (для отладки)
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# 🔹 Функция для получения всех скидок из Steam
async def fetch_discounts():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(STEAM_API_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    games = []

                    # Проходим по всем категориям скидок
                    for category in data.get("specials", {}).get("items", []):
                        if category.get("discounted", False):
                            game = {
                                "name": category["name"],
                                "original_price": category["original_price"] / 100 if category.get("original_price") else None,
                                "final_price": category["final_price"] / 100 if category.get("final_price") else None,
                                "discount": category["discount_percent"],
                                "link": f"https://store.steampowered.com/app/{category['id']}",
                                "image": category.get("header_image", ""),
                            }
                            games.append(game)

                    return games
                else:
                    logging.error(f"Ошибка Steam API: Код {response.status}")
                    return []
        except Exception as e:
            logging.error(f"Ошибка при получении данных: {e}")
            return []

# 🔹 Фильтруем и выбираем случайные скидки
async def get_random_discounts():
    all_discounts = await fetch_discounts()
    if not all_discounts:
        return None
    
    random.shuffle(all_discounts)  # Перемешиваем список
    return all_discounts[:5]  # Берём 5 случайных скидок

# 🔹 Функция для отправки поста
async def send_discount_post():
    discounts = await get_random_discounts()
    
    if not discounts:
        await bot.send_message(TELEGRAM_CHANNEL_ID, "🚫 Нет актуальных скидок.")
        return

    # Формируем текст поста
    message = "<b>🔥 Горящие скидки в Steam!</b>\n\n"
    for deal in discounts:
        message += (
            f"🎮 <b>{deal['name']}</b>\n"
            f"💰 <s>{deal['original_price']:.2f} USD</s> ➡️ {deal['final_price']:.2f} USD\n"
            f"🔥 Скидка: {deal['discount']}%\n"
            f"🔗 <a href='{deal['link']}'>Купить в Steam</a>\n\n"
        )

    message += "📌 Подписывайся, чтобы не пропустить новые скидки!"

    # Отправляем пост с картинкой-постером
    await bot.send_photo(TELEGRAM_CHANNEL_ID, POSTER_URL, caption=message)

# 🔹 Функция запуска бота по расписанию (раз в 30 минут)
async def schedule_posts():
    while True:
        await send_discount_post()
        await asyncio.sleep(1800)  # 1800 секунд = 30 минут

# 🔹 Запуск бота
async def main():
    asyncio.create_task(schedule_posts())
    await asyncio.sleep(9999999)  # Держим бота активным

asyncio.run(main())
