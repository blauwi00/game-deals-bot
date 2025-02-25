import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import random

# Твой токен и ID канала
TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# API URL для Steam и SteamDB
STEAM_API_URL = "https://store.steampowered.com/api/featuredcategories/"
STEAMDB_API_URL = "https://steamdb.info/api/GetPriceOverview/"

# 📌 Функция получения скидок с Steam API
async def get_steam_discounts():
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_API_URL) as response:
            if response.status != 200:
                logging.error(f"Ошибка Steam API: {response.status}")
                return []
            data = await response.json()
            if "specials" not in data:
                logging.warning("Steam API не вернул список скидок!")
                return []

            discounts = []
            for game in data["specials"]["items"]:
                if game.get("discount_percent", 0) > 0:  # Если есть скидка
                    discounts.append({
                        "name": game["name"],
                        "discount": game["discount_percent"],
                        "price_old": game["original_price"] / 100 if game["original_price"] else "Не указана",
                        "price_new": game["final_price"] / 100 if game["final_price"] else "Бесплатно",
                        "link": f"https://store.steampowered.com/app/{game['id']}",
                        "source": "Steam"
                    })
            return discounts

# 📌 Функция получения скидок с SteamDB API
async def get_steamdb_discounts(app_id):
    async with aiohttp.ClientSession() as session:
        params = {"appid": app_id}
        async with session.get(STEAMDB_API_URL, params=params) as response:
            if response.status != 200:
                logging.error(f"Ошибка SteamDB API: {response.status}")
                return None
            data = await response.json()
            if "data" not in data:
                return None

            return {
                "regions": data["data"]["prices"],
                "source": "SteamDB"
            }

# 📌 Генерация сообщения со скидками
async def generate_discount_message():
    steam_discounts = await get_steam_discounts()
    if not steam_discounts:
        return "🚫 Нет актуальных скидок."

    # Выбираем 5 случайных скидок для поста
    selected_deals = random.sample(steam_discounts, min(5, len(steam_discounts)))

    message = "<b>🔥 Горячие скидки в Steam:</b>\n\n"
    buttons = InlineKeyboardMarkup(row_width=2)

    for deal in selected_deals:
        steamdb_info = await get_steamdb_discounts(deal["link"].split("/")[-1])
        price_info = f"<s>{deal['price_old']} USD</s> ➡ {deal['price_new']} USD"
        region_prices = ""

        if steamdb_info:
            for region, price in steamdb_info["regions"].items():
                region_prices += f"\n🇦🇷 {region}: {price} USD"

        message += (
            f"🎮 <b>{deal['name']}</b>\n"
            f"💲 {price_info}\n"
            f"🔥 Скидка: {deal['discount']}%\n"
            f"🗺 Региональные цены:{region_prices}\n"
            f"📌 Источник: {deal['source']}\n\n"
        )

        # Кнопки
        buttons.add(
            InlineKeyboardButton(f"🛒 Купить за {deal['price_new']} USD", url=deal["link"]),
            InlineKeyboardButton("📊 Сравнить цены", url=f"https://steamdb.info/app/{deal['link'].split('/')[-1]}/")
        )

    return message, buttons

# 📌 Функция отправки поста
async def send_discount_post():
    message, buttons = await generate_discount_message()
    await bot.send_message(TELEGRAM_CHANNEL_ID, message, reply_markup=buttons)
    await bot.send_photo(TELEGRAM_CHANNEL_ID, photo="https://i.imgur.com/AhzG3kO.jpeg")  # Постер

# 📌 Планировщик постов (раз в 3 минуты)
async def scheduler():
    while True:
        await send_discount_post()
        await asyncio.sleep(180)  # 3 минуты

# 📌 Запуск бота
async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
