import requests
import asyncio
from aiogram import Bot
from datetime import datetime

# Твои данные
TELEGRAM_BOT_TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или "-100XXXXXXXXXX" для приватного канала

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Функция получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        deals = []

        for game in data["specials"]["items"]:
            if "price_overview" in game:
                discount = game["price_overview"]["discount_percent"]
                if discount >= 50:  # Фильтруем скидки от 50%
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

# Функция отправки тестового поста
async def send_test_post():
    deals = get_steam_deals()
    if deals:
        now = datetime.now().strftime("%H:%M")  # Добавляем текущее время в пост
        message = f"🕒 Время поста: {now}\n\n🎮 🔥 Горячие скидки в Steam! 🔥\n\n"
        message += "\n\n".join(deals)  # Объединяем 5 скидок в один пост
        await bot.send_message(TELEGRAM_CHANNEL_ID, message, parse_mode="Markdown")

# Запуск бота
async def main():
    await send_test_post()  # Отправляем тестовый пост

asyncio.run(main())
