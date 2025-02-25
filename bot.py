
import requests
import asyncio
import json
import os
from aiogram import Bot, types
from datetime import datetime

# Данные бота
TELEGRAM_BOT_TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или "-100XXXXXXXXXX" для приватного канала
POSTER_URL = "https://i.imgur.com/AhzG3kO.jpeg"  # Прямая ссылка на постер

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Файл для хранения старых скидок
DISCOUNTS_FILE = "discounts.json"

# Функция загрузки старых скидок
def load_old_discounts():
    if os.path.exists(DISCOUNTS_FILE):
        with open(DISCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Функция сохранения новых скидок
def save_discounts(discounts):
    with open(DISCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(discounts, f, ensure_ascii=False, indent=4)

# Функция получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        specials = data.get("specials", {}).get("items", [])
        print(f"Найдено {len(specials)} товаров в разделе скидок.")

        old_discounts = load_old_discounts()
        new_discounts = {}
        deals = []

        for game in specials:
            if game.get("discounted", False):
                discount = game.get("discount_percent", 0)
                if discount > 0:  # Любая скидка
                    name = game.get("name", "Без названия")
                    price_old = game.get("original_price", 0) / 100
                    price_new = game.get("final_price", 0) / 100
                    currency = game.get("currency", "USD")
                    link = f"https://store.steampowered.com/app/{game['id']}/"

                    # Проверяем, изменилась ли скидка
                    previous_discount = old_discounts.get(str(game["id"]), None)
                    discount_text = f"-{discount}%"
                    if previous_discount and previous_discount != discount:
                        discount_text += f" (Ранее было -{previous_discount}%)"

                    new_discounts[str(game["id"])] = discount  # Сохраняем текущую скидку

                    deals.append(
                        f"{name}\n"
                        f"{discount_text}\n"
                        f"{price_old} {currency} → {price_new} {currency}\n"
                        f"<a href='{link}'>Купить в Steam</a>"
                    )

            if len(deals) >= 5:  # Показываем 5 игр
                break

        save_discounts(new_discounts)  # Сохраняем скидки
        print(f"Итог: {len(deals)} игр прошло фильтр.")  

        return deals if deals else ["Скидок нет или API Steam не даёт данные."]
    
    else:
        print(f"Ошибка Steam API: Код {response.status_code}")
        return ["Ошибка при получении данных из Steam."]

# Функция отправки поста с картинкой
async def send_discount_post():
    deals = get_steam_deals()
    if deals:
        now = datetime.now().strftime("%H:%M")  # Добавляем текущее время в пост
        message = f"Время поста: {now}\n\n🔥 Горячие скидки в Steam!\n\n"
        message += "\n\n".join(deals)  # Объединяем 5 скидок в один пост

        # Отправляем пост со скидками + постером
        await bot.send_photo(TELEGRAM_CHANNEL_ID, photo=POSTER_URL, caption=message, parse_mode="HTML")
    else:
        print("Нет скидок для отправки!")

# Функция тестового запуска (2 поста, затем стоп)
async def test_run():
    for _ in range(2):  # Отправит 2 поста и остановится
        await send_discount_post()
        await asyncio.sleep(10)  # Ждём 10 секунд перед следующим постом (для тестов)

# Запуск бота (только на 2 поста)
async def main():
    await test_run()

asyncio.run(main())
