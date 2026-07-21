import asyncio
import random
from dataclasses import dataclass, field

import config
from roles import ROLES, build_role_list


@dataclass
class Player:
    user_id: int
    name: str
    role: str = "civilian"
    alive: bool = True


class Game:
    def __init__(self, chat_id: int, mode: str, host_id: int):
        self.chat_id = chat_id
        self.mode = mode
        self.host_id = host_id
        self.state = "lobby"  # lobby -> starting -> night -> day -> voting -> ended
        self.players: dict[int, Player] = {}
        self.lobby_msg_id = None
        self.day_num = 0
        self.night_actions: dict[str, dict[int, int]] = {}
        self.votes: dict[int, int] = {}
        self.pot = 0
        self.entry_fee = 50 if mode in ("pgame", "p2game") else 0

    def add_player(self, user_id: int, name: str) -> bool:
        if user_id in self.players:
            return False
        if len(self.players) >= config.MAX_PLAYERS:
            return False
        self.players[user_id] = Player(user_id, name)
        return True

    def remove_player(self, user_id: int):
        return self.players.pop(user_id, None)

    def get_player(self, user_id: int):
        return self.players.get(user_id)

    def alive_players(self):
        return [p for p in self.players.values() if p.alive]

    def alive_of_team(self, team: str):
        return [p for p in self.alive_players() if ROLES[p.role].team == team]

    def assign_roles(self):
        n = len(self.players)
        role_keys = build_role_list(self.mode, n)
        random.shuffle(role_keys)
        for player, role_key in zip(self.players.values(), role_keys):
            player.role = role_key

    def check_win(self):
        alive = self.alive_players()
        mafia = [p for p in alive if ROLES[p.role].team == "mafia"]
        maniac = [p for p in alive if ROLES[p.role].team == "maniac"]
        zombie = [p for p in alive if ROLES[p.role].team == "zombie"]
        town = [p for p in alive if ROLES[p.role].team == "town"]

        if self.mode == "zgame":
            if not zombie:
                return "town"
            if len(zombie) >= len(alive) - len(zombie):
                return "zombie"
            return None

        if not mafia and not maniac:
            return "town"
        if maniac and not mafia and len(alive) <= 2:
            return "maniac"
        if mafia and len(mafia) >= (len(town) + len(maniac)):
            return "mafia"
        return None


games: dict[int, Game] = {}


def get_game(chat_id: int):
    return games.get(chat_id)


def create_game(chat_id: int, mode: str, host_id: int) -> Game:
    g = Game(chat_id, mode, host_id)
    games[chat_id] = g
    return g


def end_game(chat_id: int):
    games.pop(chat_id, None)
