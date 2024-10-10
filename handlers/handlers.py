import random

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from config import birds, birds_2
from database.knock_db import get_user_data, save_user_data, user_exists_knock
from database.mailing import add_chat, add_user, check_user_exists
from database.premium_db import get_premium_user, has_premium
from database.tea_db import user_exists_tea
from filters.FloodWait import RateLimitFilter
from kb import profile_kb, cards_kb, rarity_kb, cool_card_kb, start_keyboard

handlers_router = Router()


@handlers_router.message(CommandStart())
async def start_command(message: Message, command: CommandObject):
    if command.args is not None:
        user_id = message.from_user.id
        base = await check_user_exists(user_id)
        tea_base = await user_exists_tea(user_id)
        knock_base = await user_exists_knock(user_id)
        if not base and not tea_base or not knock_base:
            await message.answer(user_id=command.args, text="У вас новый реферал! (система рефералов еще не готова)")
        else:
            pass
    else:
        first_name = message.from_user.first_name
        text = (f"👋 {first_name}, добро пожаловать в Birdy.\n\n"
                f"👾 Тут ты можешь пить чай и соревноваться за место в топе, собирать карточки и просто наслаждаться ботом.\n\n"
                f"🐦‍⬛️ Бот будет улучшаться и обновляться с каждым разом.\n\n")
        if message.chat.type in ["supergroup", "group"]:
            await add_chat(message.chat.id)
            text += "⚙️ Для получения всех команд напишите /help."
            await message.reply(text)
        elif message.chat.type == "private":
            await add_user(message.from_user.id)
            await message.answer(text, reply_markup=await start_keyboard())


@handlers_router.message(Command("help"))
async def help_command(message: Message):
    if message.chat.type in ["supergroup", "group"]:
        await add_chat(message.chat.id)
    elif message.chat.type == "private":
        await add_user(message.from_user.id)

    text = '''
👋 *Добро пожаловать! Вот список доступных команд:*

📋 *Основные команды:*
- `/profile`, `бпрофиль` — ваш профиль.
- `/chai`, `чай`, — выпить чай.
- `/knock`, `кнок` — получить карту (наблюдение за птичками).

📊 *Топы:*
- `/chai_top`, `топ чая` — топ по выпитому чаю.
- `/cards_top`, `топ карточек` — топ карточек по поинтам и количеству.
    '''
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)


@handlers_router.message(RateLimitFilter(1), F.text.casefold().in_(
    ["бпрофиль".casefold(), "/profile".casefold(), "бирди профиль".casefold(), "👤 бпрофиль".casefold()]))
async def birdy_profile(message: Message):
    if message.chat.type in ["supergroup", "group"]:
        await add_chat(message.chat.id)
    elif message.chat.type == "private":
        await add_user(message.from_user.id)
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    prem_text = await get_premium_user(user_id)
    user_data = await get_user_data(user_id, first_name)
    count_birds = len(user_data['birds'])

    user_profile_photos = await message.bot.get_user_profile_photos(user_id, limit=1)
    if user_profile_photos.photos:
        photo = user_profile_photos.photos[0][-1]
        file_id = photo.file_id

        photo_cache = file_id
    else:
        photo_cache = 'https://tinypic.host/images/2024/07/08/avatar.jpg'

    caption = (f"🏡 Личный профиль {first_name} {last_name}\n"
               f"🃏 Собрано {count_birds} карточек из {len(birds_2)} возможных.\n"
               f"🏆 Баланс поинтов: {user_data['points']}\n"
               f"💎 Премиум: {prem_text}")
    await message.bot.send_photo(chat_id=message.chat.id, photo=photo_cache, caption=caption,
                                 reply_markup=await profile_kb(user_id))


@handlers_router.callback_query(F.data.startswith("cards:"))
async def show_cards(callback: CallbackQuery):
    data = callback.data.split(":")
    user_id = data[1]
    user_nickname = callback.from_user.first_name
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    try:
        await callback.bot.send_message(chat_id=callback.from_user.id,
                                        text="Выберите редкость карточек, которые хотите посмотреть:",
                                        reply_markup=await rarity_kb())
        if callback.message.chat.type in ["group", "supergroup"]:
            await callback.bot.send_message(chat_id=callback.message.chat.id,
                                            text=f"{user_nickname}, карточки отправлены вам в личные сообщения!")
        else:
            pass
    except Exception:
        await callback.answer("Напишите боту что-то в личные сообщения, чтобы отправить вам карточки!", show_alert=True)


@handlers_router.callback_query(F.data.startswith("select_rarity:"))
async def select_rarity(callback: CallbackQuery):
    rarity = callback.data.split(":")[1]
    user_data = await get_user_data(callback.from_user.id, callback.from_user.first_name)

    user_birds = [bird for bird in user_data['birds'] if
                  next(b["rarity"] for b in birds_2 if b["name"] == bird) == rarity]

    if not user_birds:
        await callback.answer(f"У вас нет карточек категории '{rarity}'")
        return

    current_bird_name = user_birds[0]
    current_bird = next(bird for bird in birds_2 if bird["name"] == current_bird_name)
    caption = (f"🃏 Карточка {current_bird['name']}\n"
               f"Раритет: {current_bird['rarity']}\n"
               f"Место обитания: {current_bird['place']}\n")
    if 'points' in current_bird:
        caption += f"Очки: {current_bird['points']}"

    keyboard = await cards_kb(str(callback.from_user.id), 0, len(user_birds), rarity, current_bird_name)

    await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=current_bird['photo'], caption=caption,
                                  reply_markup=keyboard)
    await callback.answer()


@handlers_router.callback_query(F.data.startswith("ccards:"))
async def show_cards(callback: CallbackQuery):
    data = callback.data.split(":")
    rarity = data[1]
    current_index = int(data[2])

    user_data = await get_user_data(callback.from_user.id, callback.from_user.first_name)

    user_birds = [bird for bird in user_data['birds'] if
                  next(b["rarity"] for b in birds_2 if b["name"] == bird) == rarity]

    if not user_birds:
        await callback.answer(f"У вас нет такой редкости.")
        return

    current_bird_name = user_birds[current_index]
    current_bird = next(bird for bird in birds_2 if bird["name"] == current_bird_name)

    caption = (f"🃏 Карточка {current_bird['name']}\n"
               f"Раритет: {current_bird['rarity']}\n"
               f"Место обитания: {current_bird['place']}\n")
    if 'points' in current_bird:
        caption += f"Очки: {current_bird['points']}"

    keyboard = await cards_kb(str(callback.from_user.id), current_index, len(user_birds), rarity, current_bird_name)
    photo = current_bird['photo']
    media = InputMediaPhoto(media=photo, caption=caption)

    if callback.message.photo:
        await callback.message.edit_media(media=media, reply_markup=keyboard)
    else:
        await callback.message.edit_caption(caption=caption, reply_markup=keyboard)

    await callback.answer()

@handlers_router.callback_query(F.data.startswith("cool_card:"))
async def cool_card_handler(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    first_name = callback.from_user.first_name
    user_data = await get_user_data(callback.from_user.id, first_name)
    if await has_premium(int(user_id)):
        price = 45000
    else:
        price = 50000
    await callback.message.reply(f"🃏 Купить лимитку. Цена: {price} pts.\n"
                                 f"👛 Баланс pts: {user_data['points']}",
                                 reply_markup=await cool_card_kb(callback.from_user.id))


@handlers_router.callback_query(F.data.startswith("buy_cool_card:"))
async def buy_cool_card(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return

    first_name = callback.from_user.first_name
    user_data = await get_user_data(callback.from_user.id, first_name)
    if await has_premium(int(user_id)):
        price = 45000
    else:
        price = 50000
    if user_data['points'] >= price:
        excluded_birds = ["Птица бог воды", "Птица бог огня", "Птица бог камня", "Птица бог грома",
                          "Птица бог растений"]
        eligible_birds = [bird for bird in birds_2 if bird["rarity"] == "Крутка" and bird["name"] not in excluded_birds]

        if not eligible_birds:
            await callback.answer(f"{first_name}, вы уже собрали все крутки, поздравляю!")
            return

        chosen_bird = None
        attempt_count = 0
        while attempt_count < 100:
            chosen_bird = random.choice(eligible_birds)
            if chosen_bird['name'] not in user_data['birds']:
                break
            attempt_count += 1

        if chosen_bird and chosen_bird['name'] not in user_data['birds']:
            user_data['birds'].append(chosen_bird['name'])
            user_data['points'] -= price

            await save_user_data(user_data)

            photo_data = chosen_bird['photo']
            await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo_data,
                                          caption=f"{first_name}, вам выпала {chosen_bird['name']}!")
        else:
            await callback.bot.send_message(chat_id=callback.message.chat.id,
                                            text=f"{first_name}, вы уже собрали все крутки.")
    else:
        await callback.answer("Не достаточно очков для покупки!", show_alert=True)


@handlers_router.callback_query(F.data.startswith("ref:"))
async def ref_handler(callback: CallbackQuery):
    user_id = callback.data.split(":")[1]
    if user_id != str(callback.from_user.id):
        await callback.answer("Вы арестованы, руки вверх!")
        return
    await callback.message.reply(f"Ваша реферальная ссылка:\n"
                                 f"https://t.me/birdy_ibot?start={user_id}", disable_web_page_preview=True)