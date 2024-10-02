import time
from datetime import datetime
import aiosqlite

async def create_premium_table():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS premium_users (
                user_id INTEGER PRIMARY KEY,
                premium_time INTEGER NOT NULL
            )
        ''')
        await db.commit()


async def add_premium_user(user_id: int, days: int):
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT premium_time FROM premium_users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            current_premium_time = row[0]
            if current_premium_time < int(time.time()):
                new_premium_time = int(time.time()) + days * 86400
            else:
                new_premium_time = current_premium_time + days * 86400
        else:
            new_premium_time = int(time.time()) + days * 86400


        await db.execute('''
            INSERT INTO premium_users (user_id, premium_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET premium_time = excluded.premium_time
        ''', (user_id, new_premium_time))
        await db.commit()


async def remove_premium_user(user_id: int):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('DELETE FROM premium_users WHERE user_id = ?', (user_id,))
        await db.commit()


async def get_premium_user(user_id: int):
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT premium_time FROM premium_users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            premium_time = row[0]
            current_time = int(time.time())

            if premium_time < current_time:
                await remove_premium_user(user_id)
                return "истек."

            premium_end_date = datetime.fromtimestamp(premium_time).strftime('%Y-%m-%d')
            return f"активен до {premium_end_date}."
        else:
            return "не активен."


async def has_premium(user_id: int) -> bool:
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('SELECT premium_time FROM premium_users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            premium_time = row[0]
            current_time = int(time.time())
            return premium_time > current_time
        return False
