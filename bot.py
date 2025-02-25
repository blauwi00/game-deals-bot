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
MIN_DISCOUNT = 10  # Минимальный процент скидки для публикации
MAX_GAMES = 10  # Сколько игр показывать в одном посте

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

# Функция получения всех скидок из Steam API
def get_all_steam_deals():
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"  # Получаем список всех игр
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        all_apps = data.get("applist", {}).get("apps", [])
        print(f"Всего игр в Steam: {len(all_apps)}")

        game_ids = [str(game["appid"]) for game in all_apps]
        return game_ids[:5000]  # Ограничиваем выбор 5000 играми для скорости
    else:
        print(f"Ошибка Steam API: Код {response.status_code}")
        return []

# Функция получения детальных скидок
def get_steam_deals():
    game_ids = get_all_steam_deals()
    if not game_ids:
        return ["Не удалось получить список игр из Steam API."]

    url = f"https://store.steampowered.com/api/appdetails?appids={','.join(game_ids)}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        old_discounts = load_json(DISCOUNTS_FILE)
        last_posted_games = load_json(LAST_POSTED_FILE)
        new_discounts = {}
        deals = []
        selected_games = []

        for game_id, details in data.items():
            if details.get("success"):
                game_data = details.get("data", {})
                if "price_overview" in game_data and "discount_percent" in game_data["price_overview"]:
                    discount = game_data["price_overview"]["discount_percent"]
                    if discount >= MIN_DISCOUNT:
                        name = game_data.get("name", "Без названия")
                        price_old = game_data["price_overview"].get("initial", 0) / 100
                        price_new = game_data["price_overview"].get("final", 0) / 100
                        currency = game_data["price_overview"].get("currency", "USD")
                        link = f"https://store.steampowered.com/app/{game_id}/"
                        image = game_data.get("header_image", POSTER_URL)

                        # Проверяем прошлую скидку
                        previous_discount = old_discounts.get(game_id, None)
                        discount_text = f"-{discount}%"
                        if previous_discount and previous_discount != discount:
                            discount_text += f" (Ранее было -{previous_discount}%)"

                        # Дата окончания скидки
                        discount_expiration = game_data.get("price_overview", {}).get("discount_expiration", None)
                        if discount_expiration:
                            expiration_date = datetime.utcfromtimestamp(discount_expiration).strftime("%d.%m.%Y")
                            expiration_text = f"⏳ Скидка до {expiration_date}"
                        else:
                            expiration_text = "⏳ Дата окончания неизвестна"

                        # Доступные платформы
                        platforms = []
                        if game_data.get("platforms", {}).get("windows"):
                            platforms.append("🖥 Windows")
                        if game_data.get("platforms", {}).get("mac"):
                            platforms.append("🍏 Mac")
                        if game_data.get("platforms", {}).get("linux"):
                            platforms.append("🐧 Linux")
                        platforms_text = " | ".join(platforms) if platforms else "Платформа неизвестна"

                        # Проверяем, публиковали ли уже эту игру
                        if game_id not in last_posted_games:
                            new_discounts[game_id] = discount
                            selected_games.append(game_id)

                            deals.append(
                                {
                                    "name": name,
                                    "discount": discount_text,
                                    "price_old": price_old,
                                    "price_new": price_new,
                                    "currency": currency,
                                    "platforms": platforms_text,
                                    "expiration": expiration_text,
                                    "link": link,
                                    "image": image
                                }
                            )

                        if len(deals) >= MAX_GAMES:
                            break

        save_json(DISCOUNTS_FILE, new_discounts)  # Сохраняем скидки
        save_json(LAST_POSTED_FILE, selected_games)  # Запоминаем опубликованные игры
        print(f"Итог: {len(deals)} игр прошло фильтр.")  

        return deals if deals else ["Скидок нет или API Steam не даёт данные."]
    
    else:
        print(f"Ошибка Steam API: Код {response.status_code}")
        return ["Ошибка при получении данных из Steam."]

# Функция отправки поста с постером в одном сообщении
async def send_discount_post():
    deals = get_steam_deals()
    if isinstance(deals, list) and isinstance(deals[0], str):
        print("Нет скидок для отправки!")
        return

    message = "<b>🔥 Горячие скидки в Steam!</b>\n\n"
    for deal in deals:
        message += f"<b>{deal['name']}</b>\n"
        message += f"{deal['discount']}\n"
        message += f"{deal['price_old']} {deal['currency']} → {deal['price_new']} {deal['currency']}\n"
        message += f"{deal['platforms']}\n"
        message += f"{deal['expiration']}\n"
        message += f"<a href='{deal['link']}'>🎮 Купить в Steam</a>\n\n"

    message += "📌 Подпишись, чтобы не пропустить новые скидки!"

    # Отправляем пост со скидками и постером (в одном сообщении)
    await bot.send_photo(TELEGRAM_CHANNEL_ID, photo=POSTER_URL, caption=message, parse_mode="HTML")

# Запуск бота (2 поста, затем стоп)
async def test_run():
    for _ in range(2):  # Отправит 2 поста и остановится
        await send_discount_post()
        await asyncio.sleep(10)

# Запуск
async def main():
    await test_run()
    await bot.session.close()  # Закрываем клиентскую сессию

asyncio.run(main())
