import requests
import asyncio
import random
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from datetime import datetime, timedelta

# Токен бота и ID канала
TELEGRAM_BOT_TOKEN = "7934109371:AAFFYbz1eFHzKAANo_60YInoCwlLY-wQUrU"
TELEGRAM_CHANNEL_ID = "@gamehunttm"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

# Функция для получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        deals = []

        for game in data["specials"]["items"]:
            if "price_overview" in game:
                discount = game["price_overview"]["discount_percent"]
                if discount >= 50:  # Скидки от 50%
                    name = game["name"]
                    price_old = game["price_overview"]["initial"] / 100
                    price_new = game["price_overview"]["final"] / 100
                    link = f"https://store.steampowered.com/app/{game['id']}/"

                    deals.append(f"🎮 **{name}**\n🔥 -{discount}%\n💰 {price_old}€ → {price_new}€\n🔗 [Купить в Steam]({link})")
            
            if len(deals) >= 5:  # Ограничиваем 5 скидками
                break
        
        return deals
    else:
        return ["❌ Ошибка при получении данных из Steam."]

async def test_message():
    await bot.send_message(TELEGRAM_CHANNEL_ID, "✅ Бот работает!")
# Функция для отложенного постинга скидок 
async def post_deals():
    deals = get_steam_deals()
    if not deals:
        return

    # Генерируем 5 случайных времени в пределах дня
    now = datetime.now()
    post_times = [now.replace(hour=10, minute=0) + timedelta(hours=i * 4) for i in range(len(deals))]
    
    for i, deal in enumerate(deals):
        post_time = post_times[i]
        wait_time = (post_time - datetime.now()).total_seconds()
        
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        await bot.send_message(TELEGRAM_CHANNEL_ID, deal, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(5)  # Задержка между постами, чтобы Telegram не забанил

# Запуск планировщика
async def test_message():
    async def scheduler():
        while True:
            await post_deals()
            await asyncio.sleep(86400)  # Запускаем каждый день

# Запуск бота
async def main():
    asyncio.create_task(scheduler())

asyncio.run(main())
