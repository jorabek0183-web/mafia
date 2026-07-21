from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import config
import database as db
import texts

router = Router()


@router.message(Command("kurs"))
async def cmd_kurs(message: Message):
    await message.answer(texts.KURS_TEXT.format(rate=config.GOLD_RATE))


@router.message(Command("adddiamond"))
async def cmd_adddiamond(message: Message, command: CommandObject):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    try:
        amount = int(command.args)
    except (TypeError, ValueError):
        await message.answer("Foydalanish: /adddiamond 10")
        return
    await db.add_diamonds(message.chat.id, amount)
    await message.answer(f"💎 {amount} olmos qo'shildi.")
