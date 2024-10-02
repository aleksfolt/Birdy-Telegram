from aiogram import Router, types
from aiogram.types import InlineQueryResultCachedPhoto

from config import birds_2
from database.knock_db import get_user_data

inline_router = Router()


@inline_router.inline_query()
async def inline_handler(inline_query: types.InlineQuery):
    user_id = inline_query.from_user.id
    query_text = inline_query.query.strip().lower()
    user_data = await get_user_data(user_id, inline_query.from_user.first_name)

    user_birds = user_data['birds']
    card_found = False
    photo_file_id = None

    for bird in user_birds:
        if bird.lower() == query_text:
            card_found = True
            break

    if card_found:
        for bird_data in birds_2:
            if bird_data['name'].lower() == query_text:
                photo_file_id = bird_data['photo']
                break

        caption = (f"Птичка пользователя {inline_query.from_user.first_name}.\n\n"
                   f"📛 Название: {bird_data['name']}.\n\n"
                   f"🎴 Редкость: {bird_data['rarity']}.\n"
                   f"🌄 Обитание: {bird_data['place']}.\n")

        if 'points' in bird_data:
            caption += f"💯 Поинты: {bird_data['points']}"

        if photo_file_id:
            photo = InlineQueryResultCachedPhoto(
                id=query_text,
                photo_file_id=photo_file_id,
                caption=caption
            )
            await inline_query.answer([photo], is_personal=True)
        else:
            pass
    else:
        await inline_query.answer(
            results=[],
            cache_time=5,
            switch_pm_text="У вас нет такой карточки.",
            switch_pm_parameter="start"
        )

    results = []
    await inline_query.answer(results, cache_time=1)
