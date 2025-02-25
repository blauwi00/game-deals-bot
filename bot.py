import asyncio
import httpx
import json
import datetime
import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 Токен бота и канал
TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

# 🔹 Региональные коды валют
REGIONS = {
    "us": "USD",
    "eu": "EUR",
    "ru": "RUB",
    "ua": "UAH",
    "br": "BRL"
}

# 🔹 Ссылки на API
STEAM_API_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
STEAMDB_API_URL = "https://steamdb.info/api/GetCurrentDeals"
ALT_STORES_API_URL = "https://some-alternative-store.com/api/deals"

# 🔹 Создаем бота и диспетчер
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# 🔹 Функция получения скидок
async def fetch_discounts():
    async with httpx.AsyncClient() as client:
        try:
            # 🟢 Получаем данные из Steam API
            steam_response = await client.get(STEAM_API_URL)
            steam_data = steam_response.json()
            
            # 🟢 Получаем данные из SteamDB
            steamdb_response = await client.get(STEAMDB_API_URL)
            steamdb_data = steamdb_response.json()
            
            # 🟢 Получаем данные из альтернативных магазинов
            alt_response = await client.get(ALT_STORES_API_URL)
            alt_data = alt_response.json()
            
            # 🔹 Объединяем данные из всех источников
            all_deals = steam_data.get("deals", []) + steamdb_data.get("deals", []) + alt_data.get("deals", [])
            
            return all_deals
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []

# 🔹 Фильтрация и подготовка скидок
async def process_discounts():
    deals = await fetch_discounts()
    processed_deals = []
    
    for deal in deals:
        try:
            game_name = deal.get("name", "Неизвестная игра")
            discount = deal.get("discount_percent", 0)
            original_price = deal.get("original_price", 0) / 100  # Переводим из центов в валюту
            final_price = deal.get("final_price", 0) / 100
            expiration = deal.get("discount_expiration", "Неизвестно")
            source = deal.get("source", "Steam")  # Steam, SteamDB или альтернативный магазин
            
            # 🔹 Проверка, что скидка не 0%
            if discount > 0:
                processed_deals.append({
                    "name": game_name,
                    "discount": discount,
                    "price_old": original_price,
                    "price_new": final_price,
                    "expiration": expiration,
                    "source": source,
                    "link": deal.get("link", "#")
                })

        except Exception as e:
            print(f"Ошибка при обработке скидки: {e}")
    
    return processed_deals[:5]  # Ограничиваем 5 скидками

# 🔹 Отправка поста в Telegram
async def send_discount_post():
    deals = await process_discounts()
    
    if not deals:
        await bot.send_message(TELEGRAM_CHANNEL_ID, "🚫 Нет актуальных скидок.")
        return
    
    message = "<b>🔥 Горячие скидки в Steam и других магазинах!</b>\n\n"
    
    for deal in deals:
        message += f"<b>{deal['name']}</b>\n"
        message += f"💰 <s>{deal['price_old']} USD</s> ➡️ {deal['price_new']} USD\n"
        message += f"🔥 Скидка: {deal['discount']}%\n"
        message += f"⏳ Действует до: {deal['expiration']}\n"
        message += f"📌 Источник: {deal['source']}\n"
        
        # 🔹 Создаем кнопки
        buttons = InlineKeyboardMarkup(row_width=2)
        buttons.add(
            InlineKeyboardButton(f"🛒 Купить за {deal['price_new']} USD", url=deal["link"]),
            InlineKeyboardButton("📊 Сравнить цены", url=f"https://steamdb.info/app/{deal['link'].split('/')[-1]}/")
        )

        # 🔹 Отправка сообщений с кнопками
        await bot.send_message(TELEGRAM_CHANNEL_ID, message, reply_markup=buttons)
    
    # 🔹 Добавляем постер
    await bot.send_photo(TELEGRAM_CHANNEL_ID, photo="https://i.imgur.com/AhzG3kO.jpeg")

# 🔹 Планировщик постов
async def scheduler():
    while True:
        await send_discount_post()
        await asyncio.sleep(180)  # 3 минуты

# 🔹 Запуск бота
async def main():
    asyncio.create_task(scheduler())
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
