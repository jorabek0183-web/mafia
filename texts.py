import config

START_TEXT = (
    "Salom 👋\n"
    "Men mafiya botiman. Do'stlar bilan mafiya o'ynash uchun meni guruhingizga qo'shing "
    f"va {config.MAX_PLAYERS} kishilik o'yindan zavqlaning. Batafsil ma'lumot uchun {config.SUPPORT_URL}\n\n"
    "Meni admin qilib qo'yganingizdan so'ng, o'yinni boshlashingiz mumkin.."
)

NEED_MORE_PLAYERS = "❗ O'yinni boshlash uchun kamida {min} ta ishtirokchi kerak."

LOBBY_TEXT = (
    "🎮 <b>{mode_name}</b> rejimida ro'yxatdan o'tish davom etmoqda!\n\n"
    "Ro'yxatdan o'tganlar:\n{players}\n\n"
    "Jami: {count} ta"
)

ROLES_TEXT_HEADER = "🎭 <b>O'yin rollari</b>\n"

PROFILE_TEXT = (
    "👤 <b>Profil</b>\n\n"
    "Ism: {name}\n"
    "🆔 ID: <code>{uid}</code>\n"
    "💰 Tangalar: {coins}\n"
    "🎮 O'yinlar: {games}\n"
    "🏆 G'alabalar: {wins}\n"
    "💀 Mag'lubiyatlar: {losses}\n"
)

KURS_TEXT = "🪙 2 mg — 💰 {rate}"
