import asyncio
import logging
import os
import time

import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile

from database.knock_db import create_knock_cards_tables
from database.mailing import create_mailing_tables
from database.premium_db import create_premium_table, add_premium_user
from database.tea_db import create_tea_table
from handlers.admin import adm_router
from handlers.handlers import handlers_router
from handlers.inline_knock import inline_router
from handlers.knock import knock_router
from handlers.premium import premium_router
from handlers.tea import tea_router


async def reset_cooldown_user(user_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('UPDATE knock_users SET last_usage = 0 WHERE user_id = ?', (user_id,))
        await db.commit()


async def create_birds_with_file_ids(bot, chat_id, directory):
    files = os.listdir(directory)

    birds = []

    for file_name in files:
        file_path = os.path.join(directory, file_name)

        if os.path.isfile(file_path):
            photo = FSInputFile(file_path)
            message = await bot.send_photo(chat_id=chat_id, photo=photo)
            file_id = message.photo[-1].file_id

            bird = {
                'rarity': 'some rarity',
                'name': os.path.splitext(file_name)[0],
                'place': 'some place',
                'photo': file_id,
                'points': 'some_points'
            }
            birds.append(bird)

            print(f"File ID for {file_name}: {file_id}")

            time.sleep(3)
        else:
            print(f"Файл {file_path} не найден или не является файлом.")

    return birds


async def main():
    await create_tea_table()
    await create_knock_cards_tables()
    await create_mailing_tables()
    await create_premium_table()
    bot = Bot(token="7236929257:AAFacKzb-DKoerdeya0liwcZ4i0CaaAX7mk")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(handlers_router, tea_router, knock_router, adm_router, premium_router, inline_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
