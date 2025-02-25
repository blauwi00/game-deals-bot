import requests
import asyncio
import json
import os
import random
from aiogram import Bot
from datetime import datetime

# Данные бота
TELEGRAM_BOT_TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или "-100XXXXXXXXXX" для приватного канала
POSTER_URL = "https://i.imgur.com/AhzG3kO.jpeg"  # Прямая ссылка на постер

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Файл для хранения старых скидок
DISCOUNTS_FILE = "discounts.json"
LAST_POSTED_FILE = "last_posted.json"  # Для хранения ID последних опубликованных игр

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

# Функция загрузки списка ранее опубликованных игр
def load_last_posted():
    if os.path.exists(LAST_POSTED_FILE):
        with open(LAST_POSTED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Функция сохранения списка опубликованных игр
def save_last_posted(game_ids):
    with open(LAST_POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(game_ids, f, ensure_ascii=False, indent=4)

# Функция получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        specials = data.get("specials", {}).get("items", [])
        print(f"Найдено {len(specials)} товаров в разделе скидок.")

        old_discounts = load_old_discounts()
        last_posted_games = load_last_posted()
        new_discounts = {}
        deals = []
        selected_games = []

        # Перемешиваем список игр, чтобы каждый раз выбирать случайные
        random.shuffle(specials)

        for game in specials:
            if game.get("discounted", False):
                game_id = str(game["id"])
                discount = game.get("discount_percent", 0)
                if discount > 0 and game_id not in last_posted_games:  # Игры не должны повторяться подряд
                    name = game.get("name", "Без названия")
                    price_old = game.get("original_price", 0) / 100
                    price_new = game.get("final_price", 0) / 100
                    currency = game.get("currency", "USD")
                    link = f"https://store.steampowered.com/app/{game['id']}/"

                    # Проверяем, изменилась ли скидка
                    previous_discount = old_discounts.get(game_id, None)
                    discount_text = f"-{discount}%"
                    if previous_discount and previous_discount != discount:
                        discount_text += f" (Ранее было -{previous_discount}%)"

                    new_discounts[game_id] = discount  # Сохраняем текущую скидку
                    selected_games.append(game_id)

                    deals.append(
                        f"{name}\n"
                        f"{discount_text}\n"
                        f"{price_old} {currency} → {price_new} {currency}\n"
                        f"<a href='{link}'>Купить в Steam</a>"
                    )

            if len(deals) >= 5:  # Ограничиваем до 5 игр в посте
                break

        save_discounts(new_discounts)  # Сохраняем скидки
        save_last_posted(selected_games)  # Запоминаем, какие игры публиковали
        print(f"Итог: {len(deals)} игр прошло фильтр.")  

        return deals if deals else ["Скидок нет или API Steam не даёт данные."]
    
    else:
        print(f"Ошибка Steam API: Код {response.status_code}")
        return ["Ошибка при получении данных из Steam."]

# Функция отправки поста с постером в одном сообщении
async def send_discount_post():
    deals = get_steam_deals()
    if deals:
        now = datetime.now().strftime("%H:%M")  # Добавляем текущее время в пост
        message = f"Время поста: {now}\n\n🔥 Горячие скидки в Steam!\n\n"
        message += "\n\n".join(deals)  # Объединяем 5 скидок в один пост

        # Отправляем пост со скидками и постером (в одном сообщении)
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
    await bot.session.close()  # Закрываем клиентскую сессию, чтобы избежать утечек

asyncio.run(main())
