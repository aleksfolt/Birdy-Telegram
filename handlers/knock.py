import json
import random
import time

import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery

from config import birds, birds_2
from database.knock_db import save_user_data, get_user_data
from database.mailing import add_chat, add_user
from database.premium_db import has_premium
from kb import cards_top_kb, back_cards

knock_router = Router()


@knock_router.message(F.text.func(lambda text: text.casefold() in [
    "кнок", "/knock", "/card", "🃏 кнок"]))
async def knock_cards_function(message: Message):
    user_id = message.from_user.id
    user_nickname = message.from_user.first_name

    user_data = await get_user_data(user_id, user_nickname)

    if message.chat.type in ["supergroup", "group"]:
        await add_chat(message.chat.id)
    elif message.chat.type == "private":
        await add_user(message.from_user.id)

    if await has_premium(user_id):
        default_wait = 14400
        random_number = random.randint(1, 100)
        if 0 <= random_number <= 14:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Легендарная"]
        elif 15 <= random_number <= 34:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Мифическая"]
        elif 35 <= random_number <= 49:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Сверхредкая"]
        else:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Редкая"]

    else:
        default_wait = 18000
        random_number = random.randint(1, 100)
        if 0 <= random_number <= 9:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Легендарная"]
        elif 10 <= random_number <= 24:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Мифическая"]
        elif 25 <= random_number <= 44:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Сверхредкая"]
        else:
            eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Редкая"]

    time_since_last_usage = time.time() - user_data['last_usage']

    if time_since_last_usage < default_wait:
        remaining_time = default_wait - time_since_last_usage
        remaining_hours = int(remaining_time // 3600)
        remaining_minutes = int((remaining_time % 3600) // 60)
        remaining_seconds = int(remaining_time % 60)
        await message.reply(
            f"Вам нужно передохнуть 😴 {remaining_hours} часов {remaining_minutes} минут {remaining_seconds} секунд перед следующим наблюдением за птичками!"
        )
        return

    if eligible_birds:
        chosen_bird = random.choice(eligible_birds)
        photo_data = chosen_bird['photo']

        chosen_bird_points = int(chosen_bird['points'])

        if chosen_bird['name'] in user_data['birds']:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_data,
                reply_to_message_id=message.message_id,
                caption=(f"🐦 Вам попалась повторка: {chosen_bird['name']}! Будут начислены только очки.\n\n"
                         f"✨ Редкость: {chosen_bird['rarity']}\n"
                         f"🎯 +{chosen_bird_points} очков!\n"
                         f"🌍 Обитание: {chosen_bird['place']}\n\n"
                         f"🏆 Всего поинтов: {user_data['points'] + chosen_bird_points}")

            )
            user_data['points'] += chosen_bird_points
            user_data['all_points'] += chosen_bird_points
        else:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=photo_data,
                reply_to_message_id=message.message_id,
                caption=(f"🎉 Вы огляделись и увидели новую птицу: {chosen_bird['name']}! 🐦\n\n"
                         f"✨ Редкость: {chosen_bird['rarity']}\n"
                         f"🎯 Очки: +{chosen_bird_points}\n"
                         f"🌍 Обитание: {chosen_bird['place']}")

            )
            user_data['birds'].append(chosen_bird['name'])
            user_data['points'] += chosen_bird_points
            user_data['all_points'] += chosen_bird_points

        user_data['last_usage'] = time.time()

        await save_user_data(user_data)


@knock_router.message(F.text.func(lambda text: text.casefold() in [
    "топ карточек", "/cards_top", "топ по карточкам", "🏆 топ карточек"]))
async def top_cards_function(message: Message):
    user_id = message.from_user.id
    await message.reply("Выберите топ:", reply_markup=await cards_top_kb(user_id))


@knock_router.callback_query(F.data.startswith("top_"))
async def top_cards(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    top = callback.data.split("_")[1]
    if top.startswith("points"):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(
                    'SELECT nickname, points FROM knock_users ORDER BY points DESC LIMIT 10') as cursor:
                rows = await cursor.fetchall()
                if rows:
                    top_message = "Топ 10 пользователей по количеству очков:\n\n"
                    for idx, (first_name, tea_count) in enumerate(rows, start=1):
                        top_message += f"{idx}. {first_name}: {tea_count} очков.\n"
                else:
                    top_message = "Список топ-10 пока пуст."
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id,
                                             text=top_message,
                                             reply_markup=await back_cards(user_id))
    elif top.startswith("cards"):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(
                    'SELECT nickname, birds FROM knock_users') as cursor:
                rows = await cursor.fetchall()
                if rows:
                    user_cards = [(nickname, len(json.loads(birds))) for nickname, birds in rows]
                    user_cards_sorted = sorted(user_cards, key=lambda x: x[1], reverse=True)[:10]

                    top_message = "Топ 10 пользователей по количеству карточек:\n\n"
                    for idx, (nickname, card_count) in enumerate(user_cards_sorted, start=1):
                        top_message += f"{idx}. {nickname}: {card_count} карточек.\n"
                else:
                    top_message = "Список топ-10 пока пуст."
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id,
                                             text=top_message,
                                             reply_markup=await back_cards(user_id))
    elif top.startswith("all"):
        async with aiosqlite.connect('database.db') as db:
            async with db.execute(
                    'SELECT nickname, all_points FROM knock_users ORDER BY all_points DESC LIMIT 10') as cursor:
                rows = await cursor.fetchall()
                if rows:
                    top_message = "Топ 10 пользователей по количеству очков за все время:\n\n"
                    for idx, (nickname, all_points) in enumerate(rows, start=1):
                        top_message += f"{idx}. {nickname}: {all_points} очков.\n"
                else:
                    top_message = "Список топ-10 пока пуст."
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id,
                                             text=top_message,
                                             reply_markup=await back_cards(user_id))

    elif top.startswith("back"):
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=callback.message.message_id,
                                             text="Выберите топ:",
                                             reply_markup=await cards_top_kb(user_id))
