from aiogram import Router, F
from aiogram.types import CallbackQuery

from game_state import get_game

router = Router()

NIGHT_PREFIXES = {
    "na_mafia": "mafia",
    "na_doctor": "doctor",
    "na_detective": "detective",
    "na_maniac": "maniac",
    "na_zombie": "zombie",
}


@router.callback_query(F.data.startswith(tuple(NIGHT_PREFIXES.keys())))
async def on_night_action(call: CallbackQuery):
    prefix, chat_id_s, target_id_s = call.data.split(":")
    chat_id, target_id = int(chat_id_s), int(target_id_s)
    game = get_game(chat_id)
    if not game or game.state != "night":
        await call.answer("⏱ Vaqt tugagan.", show_alert=True)
        return
    actor = game.get_player(call.from_user.id)
    if not actor or not actor.alive:
        await call.answer("Siz bu o'yinda emassiz.", show_alert=True)
        return
    role_key = NIGHT_PREFIXES[prefix]
    game.night_actions.setdefault(role_key, {})[call.from_user.id] = target_id
    await call.message.edit_text("✅ Tanlovingiz qabul qilindi.")
    await call.answer()


@router.callback_query(F.data.startswith("vote:"))
async def on_vote(call: CallbackQuery):
    _, chat_id_s, target_id_s = call.data.split(":")
    chat_id, target_id = int(chat_id_s), int(target_id_s)
    game = get_game(chat_id)
    if not game or game.state != "voting":
        await call.answer("⏱ Ovoz berish tugagan.", show_alert=True)
        return
    voter = game.get_player(call.from_user.id)
    if not voter or not voter.alive:
        await call.answer("Siz ovoz bera olmaysiz.", show_alert=True)
        return
    game.votes[call.from_user.id] = target_id
    await call.answer("🗳 Ovozingiz qabul qilindi.")
