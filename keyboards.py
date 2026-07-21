from aiogram.utils.keyboard import InlineKeyboardBuilder

import config


def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Guruhga qo'shish", url=f"https://t.me/{config.BOT_USERNAME}?startgroup=true")
    kb.button(text="🎖 Premium guruhlar", callback_data="premium_groups")
    kb.button(text="🍯 Savollar uchun", url=config.SUPPORT_URL)
    kb.button(text="🕊 Kanal", url=config.CHANNEL_URL)
    kb.adjust(1, 1, 2)
    return kb.as_markup()


def back_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Orqaga", callback_data="back_main")
    return kb.as_markup()


def lobby_kb(mode: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="💡 Qo'shilish", callback_data=f"join:{mode}")
    return kb.as_markup()


def targets_kb(prefix: str, chat_id: int, players, exclude: int | None = None):
    kb = InlineKeyboardBuilder()
    for p in players:
        if exclude is not None and p.user_id == exclude:
            continue
        kb.button(text=p.name, callback_data=f"{prefix}:{chat_id}:{p.user_id}")
    kb.adjust(1)
    return kb.as_markup()
