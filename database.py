import aiosqlite

import config


async def init_db():
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                coins INTEGER DEFAULT {config.START_BALANCE},
                games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                diamonds INTEGER DEFAULT 0
            )
            """
        )
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None


async def create_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?,?,?)",
            (user_id, username, first_name),
        )
        await db.commit()


async def ensure_user(user):
    """user - aiogram types.User"""
    data = await get_user(user.id)
    if not data:
        await create_user(user.id, user.username or "", user.first_name or "")
        data = await get_user(user.id)
    return data


async def update_coins(user_id: int, delta: int):
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("UPDATE users SET coins = coins + ? WHERE user_id=?", (delta, user_id))
        await db.commit()


async def add_game_result(user_id: int, won: bool):
    async with aiosqlite.connect(config.DB_PATH) as db:
        if won:
            await db.execute(
                "UPDATE users SET games=games+1, wins=wins+1 WHERE user_id=?", (user_id,)
            )
        else:
            await db.execute(
                "UPDATE users SET games=games+1, losses=losses+1 WHERE user_id=?", (user_id,)
            )
        await db.commit()


async def ensure_group(chat):
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO groups (chat_id, title) VALUES (?,?)",
            (chat.id, chat.title or ""),
        )
        await db.execute("UPDATE groups SET title=? WHERE chat_id=?", (chat.title or "", chat.id))
        await db.commit()


async def top_groups(limit: int = 7):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM groups ORDER BY diamonds DESC LIMIT ?", (limit,)
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]


async def add_diamonds(chat_id: int, amount: int):
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "UPDATE groups SET diamonds = diamonds + ? WHERE chat_id=?", (amount, chat_id)
        )
        await db.commit()
