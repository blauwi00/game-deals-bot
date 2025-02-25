import asyncio
import aiohttp
import json
import datetime
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

# Твой Telegram-бот
TOKEN = "ТВОЙ_ТОКЕН"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

# Список отправленных игр
sent_games = {}

# Функция получения скидок из Steam API
async def get_steam_discounts():
    url = "https://store.steampowered.com/api/featuredcategories/"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    all_deals = []

                    # Проходим по разделам скидок
                    for category in data["specials"]["items"]:
                        game = {
                            "name": category["name"],
                            "discount": category["discount_percent"],
                            "price_old": category["original_price"] / 100 if category.get("original_price") else None,
                            "price_new": category["final_price"] / 100 if category.get("final_price") else None,
                            "link": f"https://store.steampowered.com/app/{category['id']}",
                            "image": category.get("header_image", ""),
                        }
                        all_deals.append(game)

                    return all_deals[:30]  # Берем топ 30 скидок (больше выборки)
                else:
                    print("Ошибка Steam API:", response.status)
                    return []
        except Exception as e:
            print("Ошибка при получении данных из Steam:", str(e))
            return []

# Функция выбора 5 случайных скидок без повторов
def get_unique_discounts(all_deals):
    global sent_games
    unique_deals = []
    
    for deal in all_deals:
        game_id = deal["link"]
        new_discount = deal["discount"]
        
        if game_id not in sent_games:
            sent_games[game_id] = new_discount
            unique_deals.append(deal)
        
        elif sent_games[game_id] != new_discount:
            deal["previous_discount"] = sent_games[game_id]
            sent_games[game_id] = new_discount
            unique_deals.append(deal)

        if len(unique_deals) == 5:
            break

    return unique_deals

# Функция формирования поста
def create_message(deals):
    message = "<b>🔥 Горячие скидки в Steam!</b>\n\n"
    
    for deal in deals:
        message += f"🎮 <b>{deal['name']}</b>\n"
        message += f"💰 {deal['price_old']} USD ➜ <b>{deal['price_new']} USD</b>\n"
        message += f"🔥 Скидка: <b>{deal['discount']}%</b>\n"
        if "previous_discount" in deal:
            message += f"🔄 (Прошлая скидка: {deal['previous_discount']}%)\n"
        message += f"🔗 <a href='{deal['link']}'>Купить в Steam</a>\n\n"

    message += "📌 Подписывайся, чтобы не пропускать скидки!\n"
    return message

# Функция отправки поста
async def send_discount_post():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    
    all_deals = await get_steam_discounts()
    unique_deals = get_unique_discounts(all_deals)

    if unique_deals:
        message = create_message(unique_deals)
        await bot.send_photo(TELEGRAM_CHANNEL_ID, "https://i.imgur.com/AhzG3kO.jpeg", caption=message, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(TELEGRAM_CHANNEL_ID, "🚫 Нет актуальных скидок.")

# Планировщик постов (раз в 30 минут)
async def scheduler():
    while True:
        await send_discount_post()
        await asyncio.sleep(1800)  # 30 минут

# Запуск бота
async def main():
    asyncio.create_task(scheduler())
    await asyncio.Event().wait()

asyncio.run(main())