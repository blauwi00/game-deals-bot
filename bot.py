import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, types
from datetime import datetime
import random

# 🔑 Токен и канал
TOKEN = "ТВОЙ_ТОКЕН"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

# 🔍 API ссылки
STEAM_API_URL = "https://store.steampowered.com/api/featuredcategories/"
EPIC_API_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

# 📌 Постер для каждого поста
POSTER_IMAGE = "https://i.imgur.com/AhzG3kO.jpeg"

# 🎯 Логирование
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 📌 Функция получения скидок с Steam API
async def get_steam_discounts():
    async with aiohttp.ClientSession() as session:
        async with session.get(STEAM_API_URL) as response:
            if response.status != 200:
                logging.error(f"Ошибка Steam API: {response.status}")
                return []
            data = await response.json()
            if "specials" not in data:
                return []

            discounts = []
            for game in data["specials"]["items"]:
                if game.get("discount_percent", 0) > 0:
                    discounts.append({
                        "name": game["name"],
                        "discount": game["discount_percent"],
                        "price_old": game["original_price"] / 100 if game["original_price"] else "Не указана",
                        "price_new": game["final_price"] / 100 if game["final_price"] else "Бесплатно",
                        "link": f"https://store.steampowered.com/app/{game['id']}",
                        "source": "Steam"
                    })
            return discounts

# 📌 Функция получения скидок с Epic Games Store API
async def get_epic_discounts():
    async with aiohttp.ClientSession() as session:
        async with session.get(EPIC_API_URL) as response:
            if response.status != 200:
                logging.error(f"Ошибка Epic Games API: {response.status}")
                return []
            data = await response.json()
            games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
            
            discounts = []
            for game in games:
                title = game.get("title", "Неизвестная игра")
                price_info = game.get("price", {}).get("totalPrice", {})
                discount = price_info.get("discountPercentage", 0)

                if discount > 0:  # Только игры со скидками
                    price_old = price_info.get("originalPrice", 0) / 100
                    price_new = price_info.get("discountPrice", 0) / 100
                    game_link = f"https://store.epicgames.com/p/{game['productSlug']}"

                    discounts.append({
                        "name": title,
                        "discount": discount,
                        "price_old": price_old,
                        "price_new": price_new,
                        "link": game_link,
                        "source": "Epic Games"
                    })
            return discounts

# 📌 Генерация сообщения со скидками
async def generate_discount_message():
    steam_discounts = await get_steam_discounts()
    epic_discounts = await get_epic_discounts()
    
    all_discounts = steam_discounts + epic_discounts
    if not all_discounts:
        return "🚫 Нет актуальных скидок.", None

    # Выбираем 5 случайных скидок
    selected_deals = random.sample(all_discounts, min(5, len(all_discounts)))

    message = "<b>🔥 Горячие скидки в Steam и Epic Games:</b>\n\n"

    for deal in selected_deals:
        price_info = f"<s>{deal['price_old']} USD</s> ➡ {deal['price_new']} USD"
        message += (
            f"🎮 <b>{deal['name']}</b>\n"
            f"💲 {price_info}\n"
            f"🔥 Скидка: {deal['discount']}%\n"
            f"📌 Источник: {deal['source']}\n"
            f"🔗 <a href='{deal['link']}'>Купить в магазине</a>\n\n"
        )

    return message, POSTER_IMAGE

# 📌 Функция отправки поста
async def send_discount_post():
    message, post_image = await generate_discount_message()
    if not message:
        return

    await bot.send_photo(TELEGRAM_CHANNEL_ID, photo=post_image, caption=message)

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