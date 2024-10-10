import aiosqlite


async def create_mailing_tables():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chats_and_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный идентификатор для каждой записи
                user_id TEXT UNIQUE,  -- Поле для хранения user_id, с уникальным ограничением
                chat_id TEXT UNIQUE  -- Поле для хранения chat_id, с уникальным ограничением
            )
        ''')
        await db.commit()


async def add_user(user_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            INSERT OR IGNORE INTO chats_and_users (user_id) VALUES (?)
        ''', (user_id,))
        await db.commit()


async def check_user_exists(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute("SELECT 1 FROM chats_and_users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return row is not None


async def add_chat(chat_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            INSERT OR IGNORE INTO chats_and_users (chat_id) VALUES (?)
        ''', (chat_id,))
        await db.commit()


async def get_all_users_and_chats():
    async with aiosqlite.connect('database.db') as db:
        async with db.execute('''
            SELECT user_id, chat_id FROM chats_and_users
        ''') as cursor:
            rows = await cursor.fetchall()
            users = [row[0] for row in rows if row[0]]
            chats = [row[1] for row in rows if row[1]]
            return users, chats


async def remove_user_from_db(user_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('DELETE FROM chats_and_users WHERE user_id = ?', (user_id,))
        await db.commit()


async def remove_chat_from_db(chat_id):
    async with aiosqlite.connect('database.db') as db:
        await db.execute('DELETE FROM chats_and_users WHERE chat_id = ?', (chat_id,))
        await db.commit()
