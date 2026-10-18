import struct
from typing import Any, List, Dict

from .data import SourceInfo, GoldSourceInfo, Player
from .enums import ServerType, Environment
from .exceptions import InvalidResponse

__all__ = ("Parser",)


class Parser:

    def __init__(self, data: bytes):
        self.index = 0
        self.data = data

    def _unpack(self, fmt: str, advance: bool = True) -> Any:
        try:
            value = struct.unpack_from(fmt, self.data, self.index)[0]
        except struct.error as exc:
            raise InvalidResponse(f"Unexpected end of packet while unpacking '{fmt}'.") from exc

        if advance:
            self.index += struct.calcsize(fmt)

        return value

    def read_byte(self, advance: bool = True) -> int:
        try:
            value = self.data[self.index]
        except IndexError as exc:
            raise InvalidResponse("Unexpected end of packet while reading byte.") from exc

        if advance:
            self.index += 1

        return value

    def read_string(self) -> str:
        if self.index >= len(self.data):
            raise InvalidResponse("Unexpected end of packet while reading string.")

        try:
            end = self.data.index(b"\x00", self.index)
        except ValueError:
            end = len(self.data)

        value = self.data[self.index: end].decode("utf-8", errors="replace")
        self.index = end + 1

        return value

    def read_short(self) -> int:
        return self._unpack("<h")

    def read_char(self) -> str:
        return chr(self.read_byte())

    def read_bool(self) -> bool:
        return bool(self.read_byte())

    def read_long(self, advance: bool = True) -> int:
        return self._unpack("<l", advance)

    def read_long_long(self) -> int:
        return self._unpack("<Q")

    def read_float(self) -> float:
        return self._unpack("<f")

    @classmethod
    def parse_source_info(cls, data: bytes) -> SourceInfo:
        parser = cls(data)

        protocol = parser.read_byte()
        name = parser.read_string()
        info_map = parser.read_string()
        folder = parser.read_string()
        game = parser.read_string()
        app_id = parser.read_short()
        players = parser.read_byte()
        max_players = parser.read_byte()
        bots = parser.read_byte()
        server_type = ServerType(parser.read_char())
        environment = Environment(parser.read_char())
        password = parser.read_bool()
        vac = parser.read_bool()

        mode = None
        witnesses = None
        duration = None

        if app_id == 2400:
            mode = parser.read_byte()
            witnesses = parser.read_byte()
            duration = parser.read_byte()

        version = parser.read_string()
        extra_data_flag = 0

        port = None
        steam_id = None
        spectator_port = None
        spectator_name = None
        keywords = None
        game_id = None

        try:
            extra_data_flag = parser.read_byte()

            if extra_data_flag & 0x80:
                port = parser.read_short()

            if extra_data_flag & 0x10:
                steam_id = parser.read_long_long()

            if extra_data_flag & 0x40:
                spectator_port = parser.read_short()
                spectator_name = parser.read_string()

            if extra_data_flag & 0x20:
                keywords = parser.read_string()

            if extra_data_flag & 0x01:
                game_id = parser.read_long_long()
        except InvalidResponse:
            pass

        return SourceInfo(
            protocol=protocol, name=name, map=info_map,
            folder=folder, game=game, app_id=app_id,
            players=players, max_players=max_players, bots=bots,
            server_type=server_type, environment=environment, password=password,
            vac=vac, version=version, extra_data_flag=extra_data_flag,
            mode=mode, witnesses=witnesses, duration=duration,
            port=port, steam_id=steam_id, spectator_port=spectator_port,
            spectator_name=spectator_name, keywords=keywords, game_id=game_id,
        )

    @classmethod
    def parse_goldsource_info(cls, data: bytes) -> GoldSourceInfo:
        parser = cls(data)

        address = parser.read_string()
        name = parser.read_string()
        info_map = parser.read_string()
        folder = parser.read_string()
        game = parser.read_string()
        players = parser.read_byte()
        max_players = parser.read_byte()
        protocol = parser.read_byte()
        server_type = ServerType(parser.read_char())
        environment = Environment(parser.read_char())
        password = parser.read_bool()
        modded = parser.read_bool()

        mod_link = None
        mod_download_link = None
        mod_version = None
        mod_size = None
        mod_multiplayer_only = None
        mod_uses_custom_dll = None

        if modded:
            mod_link = parser.read_string()
            mod_download_link = parser.read_string()
            parser.read_byte()
            mod_version = parser.read_long()
            mod_size = parser.read_long()
            mod_multiplayer_only = parser.read_bool()
            mod_uses_custom_dll = parser.read_bool()

        vac = parser.read_bool()
        bots = parser.read_byte()

        return GoldSourceInfo(
            address=address, name=name, map=info_map,
            folder=folder, game=game, players=players,
            max_players=max_players, protocol=protocol, server_type=server_type,
            environment=environment, password=password, modded=modded,
            mod_link=mod_link, mod_download_link=mod_download_link, mod_version=mod_version,
            mod_size=mod_size, mod_multiplayer_only=mod_multiplayer_only, mod_uses_custom_dll=mod_uses_custom_dll,
            vac=vac, bots=bots
        )

    @classmethod
    def parse_players(cls, data: bytes) -> List[Player]:
        parser = cls(data)

        player_count = parser.read_byte()

        players: List[Player] = []

        try:
            while len(players) < player_count and parser.index < len(data):
                players.append(Player(
                    index=parser.read_byte(),
                    name=parser.read_string(),
                    score=parser.read_long(),
                    duration=parser.read_float()
                ))

            if parser.index < len(data):
                for player in players:
                    player.deaths = parser.read_long()
                    player.money = parser.read_long()
        except InvalidResponse:
            pass

        return players

    @classmethod
    def parse_rules(cls, data: bytes) -> Dict[str, str]:
        parser = cls(data)

        rule_count = parser.read_short()
        rules: Dict[str, str] = {}

        try:
            for _ in range(rule_count):
                if parser.index >= len(data):
                    break
                key = parser.read_string()
                value = parser.read_string()
                rules[key] = value
        except InvalidResponse:
            pass

        return rules

