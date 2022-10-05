import struct

from .data import SourceInfo, GoldSourceInfo, Player
from .enums import ServerType, Environment

__all__ = ("Parser",)


class Parser:

    def __init__(self, data: bytes):
        self.index = 0
        self.data = data

    def __enter__(self):
        self.index = 0
        return self

    def __exit__(self, exc_val, exc_type, exc_tb):
        if not exc_val:
            return True
        return False

    def read_byte(self) -> int:
        value = struct.unpack("<B", self.data[self.index: self.index + 1])[0]
        self.index = self.index + 1

        return value

    def read_string(self) -> str:
        end = self.data.index(b"\x00", self.index)

        value = self.data[self.index: end].decode("utf-8")
        self.index = end + 1

        return value

    def read_short(self) -> int:
        value = struct.unpack("<h", self.data[self.index: self.index + 2])[0]
        self.index = self.index + 2

        return value

    def read_char(self) -> str:
        return chr(self.read_byte())

    def read_bool(self) -> bool:
        return bool(self.read_byte())

    def read_long(self) -> int:
        value = struct.unpack("<l", self.data[self.index: self.index + 4])[0]
        self.index = self.index + 4

        return value

    def read_long_long(self) -> int:
        value = struct.unpack("<Q", self.data[self.index: self.index + 8])[0]
        self.index = self.index + 8

        return value

    def read_float(self) -> float:
        value = struct.unpack("<f", self.data[self.index: self.index + 4])[0]
        self.index = self.index + 4

        return value

    @classmethod
    def parse_source_info(cls, data: bytes) -> SourceInfo:
        with cls(data) as parser:
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
            extra_data_flag = parser.read_byte()

            port = None
            steam_id = None
            spectator_port = None
            spectator_name = None
            keywords = None
            game_id = None
    
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
        with cls(data) as parser:
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
    def parse_players(cls, data: bytes) -> list[Player]:
        players = []

        with cls(data) as parser:
            player_count = parser.read_byte()

            while len(players) < player_count:
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

        return players

    @classmethod
    def parse_rules(cls, data: bytes) -> dict[str, str]:
        with cls(data) as parser:
            rule_count = parser.read_short()
            rules = dict((parser.read_string(), parser.read_string()) for _ in range(rule_count))

        return rules
