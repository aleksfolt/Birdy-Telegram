import aiosqlite


async def create_tea_table():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                tea_count INTEGER NOT NULL,
                last_used INTEGER NOT NULL
            )
        ''')
        await db.commit()


async def user_exists_tea(user_id):
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return row is not None
