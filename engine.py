import asyncio
import random

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError

import config
import database as db
import keyboards as kb
from game_state import Game, get_game, end_game
from roles import ROLES


async def start_game(bot: Bot, game: Game):
    game.state = "starting"
    game.assign_roles()

    if game.mode in ("pgame", "p2game"):
        for uid in list(game.players):
            user = await db.get_user(uid)
            if not user or user["coins"] < game.entry_fee:
                game.remove_player(uid)
                continue
            await db.update_coins(uid, -game.entry_fee)
            game.pot += game.entry_fee

    for player in game.players.values():
        role = ROLES[player.role]
        try:
            await bot.send_message(
                player.user_id,
                f"🎭 Sizning rolingiz: <b>{role.emoji} {role.name}</b>\n\n{role.description}",
            )
        except TelegramForbiddenError:
            pass

    await bot.send_message(
        game.chat_id,
        f"🎬 O'yin boshlandi! Ishtirokchilar soni: {len(game.players)}\n"
        f"Rollaringiz shaxsiy xabarlarga yuborildi (botni shaxsiy chatda ishga tushirganingizga ishonch hosil qiling).\n"
        f"🌙 Tun boshlanmoqda...",
    )
    await asyncio.sleep(3)
    asyncio.create_task(night_phase(bot, game))


async def night_phase(bot: Bot, game: Game):
    game.state = "night"
    game.day_num += 1
    game.night_actions = {"mafia": {}, "doctor": {}, "detective": {}, "maniac": {}, "zombie": {}}

    alive = game.alive_players()
    mafia_team = [p for p in alive if p.role in ("mafia", "don")]
    doctors = [p for p in alive if p.role == "doctor"]
    detectives = [p for p in alive if p.role == "detective"]
    maniacs = [p for p in alive if p.role == "maniac"]
    zombies = [p for p in alive if p.role == "zombie"]

    async def send_action(actor, prefix, choices):
        try:
            await bot.send_message(
                actor.user_id,
                "🌙 Tun. Harakatingizni tanlang:",
                reply_markup=kb.targets_kb(prefix, game.chat_id, choices, exclude=actor.user_id),
            )
        except TelegramForbiddenError:
            pass

    for m in mafia_team:
        await send_action(m, "na_mafia", alive)
    for d in doctors:
        await send_action(d, "na_doctor", alive)
    for det in detectives:
        await send_action(det, "na_detective", alive)
    for man in maniacs:
        await send_action(man, "na_maniac", alive)
    for z in zombies:
        await send_action(z, "na_zombie", alive)

    await bot.send_message(
        game.chat_id,
        f"🌙 {game.day_num}-tun boshlandi. Harakati bo'lganlar shaxsiy xabarlarini tekshirsin.\n"
        f"⏳ {config.NIGHT_TIME} soniya.",
    )
    await asyncio.sleep(config.NIGHT_TIME)

    if get_game(game.chat_id) is not game:
        return
    await resolve_night(bot, game)


def _majority_target(votes: dict):
    if not votes:
        return None
    tally = {}
    for target in votes.values():
        tally[target] = tally.get(target, 0) + 1
    best = max(tally.values())
    top = [t for t, c in tally.items() if c == best]
    return random.choice(top)


async def resolve_night(bot: Bot, game: Game):
    killed = []
    mafia_target = _majority_target(game.night_actions.get("mafia", {}))
    doctor_target = _majority_target(game.night_actions.get("doctor", {}))
    maniac_target = _majority_target(game.night_actions.get("maniac", {}))
    zombie_target = _majority_target(game.night_actions.get("zombie", {}))

    if mafia_target and mafia_target != doctor_target:
        p = game.get_player(mafia_target)
        if p and p.alive:
            p.alive = False
            killed.append(p)

    if maniac_target and maniac_target != doctor_target:
        p = game.get_player(maniac_target)
        if p and p.alive:
            p.alive = False
            killed.append(p)

    if zombie_target:
        p = game.get_player(zombie_target)
        if p and p.alive:
            p.role = "zombie"

    for det_id, target_id in game.night_actions.get("detective", {}).items():
        target = game.get_player(target_id)
        if target:
            team = ROLES[target.role].team
            result = "🔴 Mafiya" if team == "mafia" else "🟢 Tinch"
            try:
                await bot.send_message(det_id, f"🕵️ Tekshiruv natijasi: {target.name} — {result}")
            except TelegramForbiddenError:
                pass

    if killed:
        names = ", ".join(f"{p.name} ({ROLES[p.role].emoji} {ROLES[p.role].name})" for p in killed)
        text = f"☀️ Tong yoritildi. Bu kecha halok bo'lganlar: {names}"
    else:
        text = "☀️ Tong yoritildi. Bu kecha hech kim halok bo'lmadi."
    await bot.send_message(game.chat_id, text)

    winner = game.check_win()
    if winner:
        await finish_game(bot, game, winner)
        return

    await day_phase(bot, game)


async def day_phase(bot: Bot, game: Game):
    game.state = "day"
    alive = game.alive_players()
    names = "\n".join(f"• {p.name}" for p in alive)
    await bot.send_message(
        game.chat_id,
        f"💬 Kunduz. Muhokama qiling!\n\nTirik qolganlar:\n{names}\n\n⏳ {config.DAY_TIME} soniya.",
    )
    await asyncio.sleep(config.DAY_TIME)
    if get_game(game.chat_id) is not game:
        return
    await voting_phase(bot, game)


async def voting_phase(bot: Bot, game: Game):
    game.state = "voting"
    game.votes = {}
    alive = game.alive_players()
    await bot.send_message(
        game.chat_id,
        "🗳 Ovoz berish boshlandi! Kimni chetlatmoqchisiz?",
        reply_markup=kb.targets_kb("vote", game.chat_id, alive),
    )
    await asyncio.sleep(config.VOTE_TIME)
    if get_game(game.chat_id) is not game:
        return
    await resolve_vote(bot, game)


async def resolve_vote(bot: Bot, game: Game):
    target_id = _majority_target(game.votes)
    if target_id:
        p = game.get_player(target_id)
        if p and p.alive:
            p.alive = False
            await bot.send_message(
                game.chat_id,
                f"⚖️ Ovoz natijasida <b>{p.name}</b> chetlatildi. Uning rolii: "
                f"{ROLES[p.role].emoji} {ROLES[p.role].name}",
            )
    else:
        await bot.send_message(game.chat_id, "⚖️ Hech kim chetlatilmadi.")

    winner = game.check_win()
    if winner:
        await finish_game(bot, game, winner)
        return
    await asyncio.sleep(3)
    await night_phase(bot, game)


async def finish_game(bot: Bot, game: Game, winner: str):
    game.state = "ended"
    win_names = {"town": "🟢 Tinch aholi", "mafia": "🔴 Mafiya", "maniac": "🗡 Qotil", "zombie": "🧟 Zombilar"}
    lines = ["🏁 <b>O'yin tugadi!</b>", f"G'olib: {win_names.get(winner, winner)}", "", "Barcha rollar:"]
    winners_ids = []

    for p in game.players.values():
        team = ROLES[p.role].team
        won = team == winner
        lines.append(f"{'✅' if won else '❌'} {p.name} — {ROLES[p.role].emoji} {ROLES[p.role].name}")
        await db.add_game_result(p.user_id, won)
        reward = config.WIN_REWARD if won else config.LOSE_REWARD
        await db.update_coins(p.user_id, reward)
        if won:
            winners_ids.append(p.user_id)

    if game.pot and winners_ids:
        share = game.pot // len(winners_ids)
        for uid in winners_ids:
            await db.update_coins(uid, share)
        lines.append(f"\n💰 Jamg'armadan har bir g'olibga: {share} tanga")

    await bot.send_message(game.chat_id, "\n".join(lines))
    end_game(game.chat_id)
