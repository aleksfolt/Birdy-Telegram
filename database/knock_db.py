import json

import aiosqlite


async def create_knock_cards_tables():
    async with aiosqlite.connect('database.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS knock_users (
                user_id INTEGER PRIMARY KEY,
                nickname TEXT NOT NULL,
                points INTEGER NOT NULL,
                all_points INTEGER NOT NULL,  -- Общее количество заработанных очков
                last_usage REAL NOT NULL,
                birds TEXT NOT NULL  -- Хранение карточек в формате JSON
            )
        ''')
        await db.commit()


async def get_user_data(user_id, nickname):
    async with aiosqlite.connect('database.db') as db:
        async with db.execute(
                'SELECT points, all_points, last_usage, nickname, birds FROM knock_users WHERE user_id = ?',
                (user_id,)) as cursor:
            row = await cursor.fetchone()

            if row is None:
                return {
                    'user_id': user_id,
                    'nickname': nickname,
                    'birds': [],
                    'points': 0,
                    'all_points': 0,
                    'last_usage': 0
                }

            points, all_points, last_usage, saved_nickname, birds_json = row

            if saved_nickname != nickname:
                await db.execute('UPDATE knock_users SET nickname = ? WHERE user_id = ?', (nickname, user_id))
                await db.commit()

            birds = json.loads(birds_json)

            return {
                'user_id': user_id,
                'nickname': nickname,
                'birds': birds,
                'points': points,
                'all_points': all_points,
                'last_usage': last_usage
            }


async def save_user_data(user_data):
    async with aiosqlite.connect('database.db') as db:
        birds_json = json.dumps(user_data['birds'])

        await db.execute('''
            INSERT INTO knock_users (user_id, nickname, points, all_points, last_usage, birds)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET 
            points = excluded.points,
            all_points = excluded.all_points,  -- Обновляем общее количество очков
            last_usage = excluded.last_usage,
            nickname = excluded.nickname,
            birds = excluded.birds  -- Обновляем JSON с птицами
        ''', (user_data['user_id'], user_data['nickname'], user_data['points'], user_data['all_points'],
              user_data['last_usage'], birds_json))
        await db.commit()
