import asyncio
import random

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config

router = Router()
_giveaways: dict[int, set] = {}  # message_id -> set(user_ids)


@router.message(Command("giveaway"))
async def cmd_giveaway(message: Message, command: CommandObject):
    prize = command.args or "Sovg'a"
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Qatnashish", callback_data="ga_join")
    sent = await message.answer(
        f"🎉 <b>Yangi giveaway!</b>\n\n🏆 Sovg'a: {prize}\n\nQatnashish uchun tugmani bosing!",
        reply_markup=kb.as_markup(),
    )
    _giveaways[sent.message_id] = set()
    await asyncio.sleep(config.GIVEAWAY_TIME)
    participants = _giveaways.pop(sent.message_id, set())
    if participants:
        winner_id = random.choice(list(participants))
        await message.answer(
            f"🏆 G'olib: <a href='tg://user?id={winner_id}'>shu yerda</a>! Tabriklaymiz 🎊"
        )
    else:
        await message.answer("😔 Hech kim qatnashmadi.")


@router.callback_query(F.data == "ga_join")
async def on_giveaway_join(call: CallbackQuery):
    parts = _giveaways.get(call.message.message_id)
    if parts is None:
        await call.answer("⏱ Giveaway tugagan.", show_alert=True)
        return
    parts.add(call.from_user.id)
    await call.answer("✅ Siz qatnashdingiz!")
