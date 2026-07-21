import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, BotCommandScopeAllPrivateChats

import config
from database import init_db
from handlers import admin, game_actions, giveaway, lobby, profile, roles_cmd, start


async def set_commands(bot: Bot):
    private_cmds = [
        BotCommand(command="start", description="O'yinni boshlash"),
        BotCommand(command="profile", description="Profilingizni ko'rish (Shaxsiy chatda)"),
        BotCommand(command="roles", description="O'yin rollarini ko'rish"),
    ]
    group_cmds = [
        BotCommand(command="start", description="O'yinni boshlash"),
        BotCommand(command="game", description="O'yin yaratish"),
        BotCommand(command="vsgame", description="Jamoaviy o'yin yaratish"),
        BotCommand(command="sgame", description="Sotqin rejimida o'yin yaratish"),
        BotCommand(command="pgame", description="Para rejimida o'yin yaratish"),
        BotCommand(command="p2game", description="Para2 rejimida o'yin yaratish"),
        BotCommand(command="zgame", description="Zombie rejimida o'yin yaratish"),
        BotCommand(command="roles", description="O'yin rollarini ko'rish"),
        BotCommand(command="giveaway", description="Yangi giveaway sozlash"),
        BotCommand(command="stop", description="O'yinni to'xtatish"),
        BotCommand(command="reload", description="Guruh ma'lumotlarini yangilash"),
        BotCommand(command="kurs", description="Hozirgi oltin kursi"),
    ]
    await bot.set_my_commands(private_cmds, scope=BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(group_cmds, scope=BotCommandScopeAllGroupChats())


async def main():
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(roles_cmd.router)
    dp.include_router(admin.router)
    dp.include_router(giveaway.router)
    dp.include_router(lobby.router)
    dp.include_router(game_actions.router)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
