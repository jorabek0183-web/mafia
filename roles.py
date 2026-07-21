from dataclasses import dataclass


@dataclass
class Role:
    key: str
    name: str
    emoji: str
    team: str  # "town", "mafia", "maniac", "zombie"
    description: str


ROLES = {
    "civilian": Role(
        "civilian", "Tinch aholi", "👤", "town",
        "Kunduzi muhokama va ovoz berish orqali mafiyani aniqlashga harakat qiling.",
    ),
    "mafia": Role(
        "mafia", "Mafiya", "🔪", "mafia",
        "Har kechasi jamoangiz bilan birga bitta o'yinchini yo'q qilasiz.",
    ),
    "don": Role(
        "don", "Don", "😈", "mafia",
        "Mafiya guruhi boshlig'i. Kechalari o'z jamoasiga qurbonni tanlashda bosh bo'ladi.",
    ),
    "doctor": Role(
        "doctor", "Shifokor", "💉", "town",
        "Har kechasi bitta o'yinchini davolab, uni o'limdan qutqarishingiz mumkin.",
    ),
    "detective": Role(
        "detective", "Komissar", "🕵️", "town",
        "Har kechasi bitta o'yinchini tekshirib, uning mafiya ekan-emasligini bilib olasiz.",
    ),
    "maniac": Role(
        "maniac", "Qotil", "🗡", "maniac",
        "Yolg'iz harakat qiluvchi qotil. Har kechasi birovni o'ldirasiz, hech kim bilan ittifoqda emassiz.",
    ),
    "traitor": Role(
        "traitor", "Sotqin", "🥷", "mafia",
        "Tashqi ko'rinishda tinch aholisiz, lekin mafiya g'alaba qozonsa siz ham yutasiz. Mafiya a'zolarini bilmaysiz.",
    ),
    "zombie": Role(
        "zombie", "Zombi", "🧟", "zombie",
        "Har kechasi bitta o'yinchini tishlab, uni ham zombiga aylantirasiz.",
    ),
    "richman": Role(
        "richman", "Boy", "💰", "town",
        "Siz boy o'yinchisiz. Halok bo'lsangiz, yig'gan tangalaringiz umumiy jamg'armaga qo'shiladi.",
    ),
}

MODE_NAMES = {
    "game": "Klassik",
    "vsgame": "Jamoaviy",
    "sgame": "Sotqin",
    "pgame": "Para",
    "p2game": "Para2",
    "zgame": "Zombie",
}


def build_role_list(mode: str, n: int):
    """n ta o'yinchi uchun rol ro'yxatini tuzadi."""
    roles = []
    mafia_count = max(1, n // 4)

    roles.append("don")
    roles += ["mafia"] * (mafia_count - 1)

    if n >= 5:
        roles.append("doctor")
    if n >= 6:
        roles.append("detective")
    if mode in ("game", "vsgame", "pgame", "p2game") and n >= 8:
        roles.append("maniac")
    if mode == "sgame" and n >= 6:
        roles.append("traitor")
    if mode == "zgame":
        roles.append("zombie")
    if mode in ("pgame", "p2game"):
        roles.append("richman")

    while len(roles) < n:
        roles.append("civilian")

    return roles[:n]
