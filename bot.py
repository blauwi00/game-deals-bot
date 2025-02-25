import asyncio
import httpx
import os
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode

TOKEN = "7934109371:AAGZnZbBmLaw2Esap1vAEcI7Pd0YaJ6xQgc"
TELEGRAM_CHANNEL_ID = "@gamehunttm"
POSTER_URL = "https://i.imgur.com/AhzG3kO.jpeg"  # Ссылка на постер

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot)

# Храним старые скидки, чтобы отслеживать изменения
previous_deals = {}

# Функция для получения всех скидок со Steam
async def fetch_all_discounts():
    url = "https://store.steampowered.com/api/featuredcategories/"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка Steam API: Код {response.status_code}")
            return None

# Функция обработки скидок и фильтрации уникальных игр
async def process_all_discounts():
    global previous_deals
    data = await fetch_all_discounts()
    if not data:
        return "🚫 Ошибка при получении скидок из Steam."

    all_discounts = []
    for deal in data.get("specials", {}).get("items", []):
        if deal.get("discount_percent", 0) > 0:  # Проверяем, есть ли скидка
            game_id = deal.get("id")
            current_discount = deal.get("discount_percent", 0)

            # Проверяем, была ли уже эта игра и изменилась ли скидка
            if game_id in previous_deals:
                old_discount = previous_deals[game_id]
                if current_discount == old_discount:
                    continue  # Пропускаем повторяющиеся скидки
                discount_change = f" (раньше было {old_discount}%)"
            else:
                discount_change = ""

            # Обновляем данные о скидке
            previous_deals[game_id] = current_discount

            link = deal.get('link', 'https://store.steampowered.com/')  # Безопасный доступ, дефолтная ссылка
            all_discounts.append(
                f"🎮 <b>{deal['name']}</b>\n"
                f"💰 <s>{deal.get('original_price', '???')}</s> ➡️ {deal.get('final_price', '???')} {deal.get('currency', '')}\n"
                f"🔥 Скидка: {current_discount}%{discount_change}\n"
                f"🔗 <a href='{link}'>Купить в Steam</a>\n"
            )

    if not all_discounts:
        return "🚫 Нет актуальных скидок."

    return all_discounts  # Возвращаем ВСЕ скидки

# Функция отправки поста со скидками и постером
async def send_discount_post():
    discounts = await process_all_discounts()
    if isinstance(discounts, str):
        await bot.send_message(TELEGRAM_CHANNEL_ID, discounts)
        return

    message = "<b>🔥 Горячие скидки в Steam!</b>\n\n"
    message += "\n".join(discounts[:5])  # Ограничение 5 играми

    # Отправляем сообщение с постером
    await bot.send_photo(TELEGRAM_CHANNEL_ID, POSTER_URL, caption=message)

# Тестовая функция для проверки работы (отправляет 2 поста, затем стоп)
async def test_run():
    for _ in range(2):  # Отправит 2 поста и остановится
        await send_discount_post()
        await asyncio.sleep(10)

# Основной цикл бота
async def main():
    await test_run()  # Временно тестовый запуск
    # Раскомментировать ниже для постоянной работы:
    # while True:
    #     await send_discount_post()
    #     await asyncio.sleep(86400)  # Раз в день

asyncio.run(main())
