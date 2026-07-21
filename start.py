from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
import texts

router = Router()


@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message):
    await db.ensure_user(message.from_user)
    await message.answer(texts.START_TEXT, reply_markup=kb.main_menu_kb())


@router.callback_query(F.data == "premium_groups")
async def show_premium(call: CallbackQuery):
    groups = await db.top_groups()
    lines = []
    if not groups:
        lines.append("Hozircha premium guruhlar yo'q.")
    else:
        for i, g in enumerate(groups, 1):
            title = g["title"] or "Noma'lum guruh"
            lines.append(f"{i}. {title} — {g['diamonds']} 💎")
    text = "🎖 <b>Top premium guruhlar:</b>\n\n" + "\n".join(lines)
    await call.message.edit_text(text, reply_markup=kb.back_kb())
    await call.answer()


@router.callback_query(F.data == "back_main")
async def back_main(call: CallbackQuery):
    await call.message.edit_text(texts.START_TEXT, reply_markup=kb.main_menu_kb())
    await call.answer()
