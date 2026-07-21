from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import config
import database as db
import engine
import keyboards as kb
import texts
from game_state import create_game, end_game, get_game
from roles import MODE_NAMES

router = Router()

GROUP_CHAT_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}


async def _create_lobby(message: Message, mode: str):
    if message.chat.type == ChatType.PRIVATE:
        await message.answer("⚠️ Bu buyruq faqat guruhda ishlaydi.")
        return
    if get_game(message.chat.id):
        await message.answer("⚠️ Bu guruhda allaqachon faol o'yin yoki lobby mavjud.")
        return
    await db.ensure_group(message.chat)
    game = create_game(message.chat.id, mode, message.from_user.id)
    text = texts.LOBBY_TEXT.format(mode_name=MODE_NAMES[mode], players="—", count=0)
    sent = await message.answer(text, reply_markup=kb.lobby_kb(mode))
    game.lobby_msg_id = sent.message_id


def _make_mode_handler(mode: str):
    async def handler(message: Message):
        await _create_lobby(message, mode)
    return handler


for _mode in MODE_NAMES:
    router.message.register(_make_mode_handler(_mode), Command(_mode))


@router.callback_query(F.data.startswith("join:"))
async def on_join(call: CallbackQuery):
    mode = call.data.split(":", 1)[1]
    game = get_game(call.message.chat.id)
    if not game or game.mode != mode or game.state != "lobby":
        await call.answer("⚠️ Lobby topilmadi yoki o'yin allaqachon boshlangan.", show_alert=True)
        return
    await db.ensure_user(call.from_user)
    added = game.add_player(call.from_user.id, call.from_user.full_name)
    if not added:
        await call.answer("Siz allaqachon ro'yxatdan o'tgansiz yoki lobby to'lgan.", show_alert=True)
        return
    players_text = "\n".join(f"{i}. {p.name}" for i, p in enumerate(game.players.values(), 1)) or "—"
    text = texts.LOBBY_TEXT.format(
        mode_name=MODE_NAMES[game.mode], players=players_text, count=len(game.players)
    )
    try:
        await call.message.edit_text(text, reply_markup=kb.lobby_kb(game.mode))
    except Exception:
        pass
    await call.answer("✅ Ro'yxatdan o'tdingiz!")


@router.message(Command("start"), F.chat.type.in_(GROUP_CHAT_TYPES))
async def cmd_start_group(message: Message):
    game = get_game(message.chat.id)
    if not game:
        await message.answer("⚠️ Avval /game (yoki boshqa rejim) buyrug'i bilan lobby oching.")
        return
    if game.state != "lobby":
        await message.answer("⚠️ O'yin allaqachon boshlangan.")
        return
    if len(game.players) < config.MIN_PLAYERS:
        await message.answer(texts.NEED_MORE_PLAYERS.format(min=config.MIN_PLAYERS))
        return
    await message.answer("🚀 O'yin boshlanmoqda...")
    await engine.start_game(message.bot, game)


@router.message(Command("stop"), F.chat.type.in_(GROUP_CHAT_TYPES))
async def cmd_stop(message: Message):
    game = get_game(message.chat.id)
    if not game:
        await message.answer("⚠️ Faol o'yin topilmadi.")
        return
    is_privileged = message.from_user.id in (game.host_id, *config.ADMIN_IDS)
    if not is_privileged:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        is_privileged = member.status in ("administrator", "creator")
    if not is_privileged:
        await message.answer("⛔ Faqat guruh admini yoki o'yin boshlovchisi to'xtata oladi.")
        return
    end_game(message.chat.id)
    await message.answer("🛑 O'yin to'xtatildi.")


@router.message(Command("reload"), F.chat.type.in_(GROUP_CHAT_TYPES))
async def cmd_reload(message: Message):
    await db.ensure_group(message.chat)
    await message.answer("🔄 Guruh ma'lumotlari yangilandi.")
