import requests
import asyncio
from aiogram import Bot
from datetime import datetime
import json

# Данные бота
TELEGRAM_BOT_TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или "-100XXXXXXXXXX" для приватного канала

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Функция получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("✅ Steam API ответило успешно!")

        try:
            specials = data.get("specials", {}).get("items", [])
            print(f"🛒 Найдено {len(specials)} товаров в разделе скидок.")

            deals = []
            for game in specials:
                if game.get("discounted", False):  # Проверяем, есть ли скидка
                    discount = game.get("discount_percent", 0)
                    if discount >= 50:  # Фильтруем скидки от 50%
                        name = game.get("name", "Без названия")
                        price_old = game.get("original_price", 0) / 100
                        price_new = game.get("final_price", 0) / 100
                        link = f"https://store.steampowered.com/app/{game['id']}/"

                        deals.append(f"🎮 **{name}**\n🔥 -{discount}%\n💰 {price_old}€ → {price_new}€\n🔗 [Купить в Steam]({link})")

                if len(deals) >= 5:  # Ограничиваем 5 скидками
                    break

            print(f"📌 Итог: {len(deals)} игр прошло фильтр.")  # Показываем, сколько игр бот реально отправит
            return deals if deals else ["❌ Скидок нет или API Steam не даёт данные."]
        
        except Exception as e:
            print(f"❌ Ошибка при обработке API Steam: {e}")
            return ["❌ Ошибка при обработке данных из Steam."]
    
    else:
        print(f"❌ Ошибка Steam API: Код {response.status_code}")
        return ["❌ Ошибка при получении данных из Steam."]

# Функция отправки поста со скидками
async def send_discount_post():
    deals = get_steam_deals()
    if deals:
        now = datetime.now().strftime("%H:%M")  # Добавляем текущее время в пост
        message = f"🕒 Время поста: {now}\n\n🎮 🔥 Горячие скидки в Steam! 🔥\n\n"
        message += "\n\n".join(deals)  # Объединяем 5 скидок в один пост
        await bot.send_message(TELEGRAM_CHANNEL_ID, message, parse_mode="Markdown")
    else:
        print("❌ Нет скидок для отправки!")

# Запуск бота
async def main():
    await send_discount_post()  # Отправляем пост со скидками

asyncio.run(main())
