from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

import texts
from roles import ROLES

router = Router()


@router.message(Command("roles"))
async def cmd_roles(message: Message):
    lines = [texts.ROLES_TEXT_HEADER]
    for role in ROLES.values():
        lines.append(f"\n{role.emoji} <b>{role.name}</b>\n{role.description}")
    await message.answer("\n".join(lines))
