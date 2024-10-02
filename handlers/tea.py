import random
import time

import aiosqlite
from aiogram import Router, F
from aiogram.types import Message
from html import escape
from database.premium_db import has_premium

tea_router = Router()
TIME_LIMIT = 600
tea_names = [
    "Зеленый чай",
    "Черный чай",
    "Белый чай",
    "Пуэр",
    "Оолонг",
    "Ройбуш",
    "Мате",
    "Травяной чай",
    "Фруктовый чай",
    "Каркаде",
    "Чай с лимоном",
    "Чай с молоком",
    "Чай с сахаром",
    "Синий чай",
    "Ку цяо",
    "Фиточаи",
    "Пеко"
]


@tea_router.message(F.text.casefold().in_(
    ["чай".casefold(), "/tea".casefold(), "/chai".casefold(), "☕️ чай".casefold()]))
async def handle_tea(message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    current_time = int(time.time())

    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT tea_count, last_used FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()

            if row:
                current_tea_count, last_used = row
                if current_time - last_used < TIME_LIMIT:
                    remaining_time = TIME_LIMIT - (current_time - last_used)
                    minutes, seconds = divmod(remaining_time, 60)
                    await message.reply(
                        f"Пожалуйста, подождите еще {minutes} минут {seconds} секунд перед следующей чашкой чая.")
                    return
            else:
                current_tea_count = 0
        if await has_premium(user_id):
            rand = 500
        else:
            rand = 200
        tea_count = random.randint(rand, 2000)
        random_tea = random.choice(tea_names)
        new_total_tea_count = current_tea_count + tea_count

        await db.execute('''
            INSERT INTO users (user_id, first_name, tea_count, last_used)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            tea_count = users.tea_count + excluded.tea_count, 
            last_used = excluded.last_used
        ''', (user_id, first_name, tea_count, current_time))
        await db.commit()
    print(message)
    await message.reply(f"{first_name}, вы успешно выпили чай!\n\n"
                        f"Выпито: {tea_count} мл.\n"
                        f"Чай: {random_tea}\n\n"
                        f"Всего выпито: {new_total_tea_count} мл.")


@tea_router.message(F.text.casefold().in_(
    ["топ чая", "чай топ", "чая топ", "⭐️ топ чая"]))
async def handle_top(message: Message):
    user_id = message.from_user.id

    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT first_name, tea_count FROM users ORDER BY tea_count DESC LIMIT 10') as cursor:
            top_rows = await cursor.fetchall()

        async with db.execute('''
            SELECT COUNT(*) + 1 FROM users WHERE tea_count > (SELECT tea_count FROM users WHERE user_id = ?)
        ''', (user_id,)) as cursor:
            user_position_row = await cursor.fetchone()

        async with db.execute('SELECT first_name, tea_count FROM users WHERE user_id = ?', (user_id,)) as cursor:
            user_info = await cursor.fetchone()

    if top_rows:
        top_message = "💫 Топ 10 пользователей по объему выпитого чая:\n\n"
        for idx, (first_name, tea_count) in enumerate(top_rows, start=1):
            top_message += f"{idx}. {escape(first_name)} - <b>{tea_count}</b> мл.\n"
    else:
        top_message = "Список топ-10 пока пуст.\n"

    if user_info:
        user_position = user_position_row[0] if user_position_row else "N/A"
        first_name, tea_count = user_info
        top_message += f"\n⏺️ Ваше место: {user_position}. {escape(first_name)} - <b>{tea_count}</b> мл."
    else:
        top_message += ""

    await message.answer(top_message, parse_mode="html")

