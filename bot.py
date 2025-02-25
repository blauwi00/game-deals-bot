import requests
import asyncio
import json
import os
import random
from aiogram import Bot
from datetime import datetime

# Данные бота
TELEGRAM_BOT_TOKEN = "ТВОЙ_НОВЫЙ_ТОКЕН"
TELEGRAM_CHANNEL_ID = "@gamehunttm"  # Или "-100XXXXXXXXXX" для приватного канала
POSTER_URL = "https://i.imgur.com/AhzG3kO.jpeg"  # Прямая ссылка на постер

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Файлы для хранения данных
DISCOUNTS_FILE = "discounts.json"
LAST_POSTED_FILE = "last_posted.json"

# Функция загрузки сохранённых скидок
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Функция сохранения скидок
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция получения скидок из Steam API
def get_steam_deals():
    url = "https://store.steampowered.com/api/featuredcategories/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        specials = data.get("specials", {}).get("items", [])
        print(f"Найдено {len(specials)} товаров в разделе скидок.")

        old_discounts = load_json(DISCOUNTS_FILE)
        last_posted_games = load_json(LAST_POSTED_FILE)
        new_discounts = {}
        deals = []
        selected_games = []

        # Перемешиваем список игр
        random.shuffle(specials)

        for game in specials:
            if game.get("discounted", False):
                game_id = str(game["id"])
                discount = game.get("discount_percent", 0)

                # Игры не должны повторяться подряд
                if discount > 0 and game_id not in last_posted_games:
                    name = game.get("name", "Без названия")
                    price_old = game.get("original_price", 0) / 100
                    price_new = game.get("final_price", 0) / 100
                    currency = game.get("currency", "USD")
                    link = f"https://store.steampowered.com/app/{game['id']}/"

                    # Проверяем прошлую скидку
                    previous_discount = old_discounts.get(game_id, None)
                    discount_text = f"-{discount}%"
                    if previous_discount and previous_discount != discount:
                        discount_text += f" (Ранее было -{previous_discount}%)"

                    # Дата окончания скидки
                    discount_expiration = game.get("discount_expiration", None)
                    if discount_expiration:
                        expiration_date = datetime.utcfromtimestamp(discount_expiration).strftime("%d.%m.%Y")
                        expiration_text = f"⏳ Скидка до {expiration_date}"
                    else:
                        expiration_text = "⏳ Дата окончания неизвестна"

                    # Доступные платформы
                    platforms = []
                    if game.get("windows_available"):
                        platforms.append("🖥 Windows")
                    if game.get("mac_available"):
                        platforms.append("🍏 Mac")
                    if game.get("linux_available"):
                        platforms.append("🐧 Linux")
                    platforms_text = " | ".join(platforms) if platforms else "Платформа неизвестна"

                    # Запоминаем новую скидку
                    new_discounts[game_id] = discount
                    selected_games.append(game_id)

                    # Добавляем игру в список поста
                    deals.append(
                        f"<b>{name}</b>\n"
                        f"{discount_text}\n"
                        f"{price_old} {currency} → {price_new} {currency}\n"
                        f"{platforms_text}\n"
                        f"{expiration_text}\n"
                        f"<a href='{link}'>🎮 Купить в Steam</a>"
                    )

            if len(deals) >= 5:  # Ограничиваем 5 играми в посте
                break

        save_json(DISCOUNTS_FILE, new_discounts)  # Сохраняем скидки
        save_json(LAST_POSTED_FILE, selected_games)  # Запоминаем, какие игры публиковали
        print(f"Итог: {len(deals)} игр прошло фильтр.")  

        return deals if deals else ["Скидок нет или API Steam не даёт данные."]
    
    else:
        print(f"Ошибка Steam API: Код {response.status_code}")
        return ["Ошибка при получении данных из Steam."]

# Функция отправки поста с постером в одном сообщении
async def send_discount_post():
    deals = get_steam_deals()
    if deals:
        now = datetime.now().strftime("%H:%M")  # Время поста
        message = f"<b>🔥 Горячие скидки в Steam!</b>\n\n"
        message += "\n\n".join(deals)  # Объединяем 5 скидок в один пост
        message += "\n\n📌 Подпишись, чтобы не пропустить новые скидки!"

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
    await bot.session.close()  # Закрываем клиентскую сессию

asyncio.run(main())