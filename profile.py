from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import database as db
import texts

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = await db.ensure_user(message.from_user)
    text = texts.PROFILE_TEXT.format(
        name=message.from_user.full_name,
        uid=message.from_user.id,
        coins=user["coins"],
        games=user["games"],
        wins=user["wins"],
        losses=user["losses"],
    )
    await message.answer(text)
