import os

# ==== Asosiy sozlamalar ====
BOT_TOKEN = os.getenv("BOT_TOKEN", "8972324168:AAGBE34P3Nn1ACoH08tlrnk3Wldu5X6L2Jw")
BOT_USERNAME = "uzzmafbot"  # bot username, @ belgisisiz

ADMIN_IDS = [8476973174]  # bot egalari / super adminlar Telegram ID lari

CHANNEL_URL = "https://t.me/mafiagroupuzz"
SUPPORT_URL = "https://t.me/saidmurodov_109"

DB_PATH = "mafia.db"

# ==== Iqtisodiyot sozlamalari ====
START_BALANCE = 1000
WIN_REWARD = 150
LOSE_REWARD = 30
GOLD_RATE = 3216  # 1 mg oltin narxi (tangada)

# ==== O'yin vaqtlari (soniyalarda) ====
REGISTRATION_TIME = 60
NIGHT_TIME = 45
DAY_TIME = 90
VOTE_TIME = 30
GIVEAWAY_TIME = 120

MIN_PLAYERS = 4
MAX_PLAYERS = 45
