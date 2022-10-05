from dataclasses import dataclass
from typing import Optional

from .enums import Environment, ServerType

__all__ = ("SourceInfo", "GoldSourceInfo", "Player")


class Data:

    def __iter__(self):
        for k in self.__slots__:
            yield k, getattr(self, k)

    def __getitem__(self, item):
        if item in self.__slots__:
            return getattr(self, item)
        raise KeyError(item)

    def keys(self):
        return self.__slots__

    def values(self):
        return [getattr(self, k) for k in self.__slots__]

    def items(self):
        return [(k, getattr(self, k)) for k in self.__slots__]

    def get(self, key, default=None):
        return getattr(self, key) or default


@dataclass(slots=True)
class SourceInfo(Data):
    """Represents a Source server's information response
    
    Attributes:
        protocol: The version of the protocol used by the server.
        name: The hostname of the server. This is what you see on a server list.
        map: The current map.
        folder: The name of the folder containing the game files. (ex. Counter-Strike: Global Offensive servers will return "csgo")
        game: The full name of the game the server is running.
        app_id: The steam App ID of the server. (ex. 730 for Counter-Strike: Global Offensive servers)
        players: The number of players on the server. This may include bots.
        max_players: The max number of players allowed.
        bots: The number of bots on the server.
        server_type: The type of server. Servers can be Dedicated, NonDedicated, or SourceTV.
        environment: The operating system the server is running. For Source servers this can be Linux, Mac, or Windows.
        password: Whether of not the server is password locked.
        vac: Indicates whether the server is protected by VAC or not.
    
        version: The version of the game installed on the server.
        extra_data_flag: This field specifies what extra data is included in the packet.
    
        mode:
            The game mode the server is currently running.

            - 0 for Hunt
            - 1 for Elimination
            - 2 for Duel
            - 3 for Deathmatch
            - 4 for VIP Team
            - 5 for Team Elimination

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        witnesses:
            The number of witnesses necessary to have a player arrested.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        duration:
            The time before a player is arrested while being witnessed in seconds.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        port: The server's game port.
        steam_id: The server's steam ID.
        spectator_port: The spectator port used for SourceTV.
        spectator_name: The name of the SourceTV spectator server.
        keywords: Tags used to describe the server.
        game_id: The server's 64-bit game ID.
    """

    protocol: int
    name: str
    map: str
    folder: str
    game: str
    app_id: int
    players: int
    max_players: int
    bots: int
    server_type: ServerType
    environment: Environment
    password: bool
    vac: bool

    version: str
    extra_data_flag: int

    mode: Optional[int] = None
    witnesses: Optional[int] = None
    duration: Optional[int] = None

    port: Optional[int] = None
    steam_id: Optional[int] = None
    spectator_port: Optional[int] = None
    spectator_name: Optional[str] = None
    keywords: Optional[str] = None
    game_id: Optional[int] = None


@dataclass(slots=True)
class GoldSourceInfo(Data):
    """Represents a GoldSource server's info response.

    Attributes:
        address: The IP address and port of the server.
        name: The hostname of the server. This is what you see on a server list.
        map: The current map.
        folder: The name of the folder containing the game files. (ex. Counter-Strike: Global Offensive servers will return "csgo")
        game: The full name of the game the server is running.
        players: The number of players on the server. This may include bots.
        max_players: The max number of players allowed.
        protocol: The version of the protocol used by the server.
        server_type: The type of server. Servers can be Dedicated, NonDedicated, or SourceTV.
        environment: The operating system the server is running. For GoldSource servers this can be Linux or Windows.
        password: Whether of not the server is password locked.
        modded: Indicates if the server is a Half-Life mod or not.

        mod_link:
            A URL to the mod's website.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_download_link:
            A URL to download the mod.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_version:
            The version of the mod running on the server.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_size:
            The space used by the mod in bytes.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_multiplayer_only:
            Indicates whether the mod is multiplayer only or single-player and multiplayer.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_uses_custom_dll:
            Indicates whether the mod uses its own DLL or the Half-Life DLL.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.


        vac: Indicates whether the server is protected by VAC or not.
        bots: The number of bots on the server.
    """

    address: str
    name: str
    map: str
    folder: str
    game: str
    players: int
    max_players: int
    protocol: int
    server_type: ServerType
    environment: Environment
    password: bool
    modded: bool

    vac: bool
    bots: int

    mod_link: Optional[str] = None
    mod_download_link: Optional[str] = None
    mod_version: Optional[int] = None
    mod_size: Optional[int] = None
    mod_multiplayer_only: Optional[bool] = None
    mod_uses_custom_dll: Optional[bool] = None


@dataclass(slots=True)
class Player(Data):
    """Represents a queried player.

    Attributes:
        index: The index of the player's chunk. This is not the player's index in the list of players.
        name: The player's name.
        score: The player's score. This is unique to the server/game but is usually kills/points.
        duration: How long the player has been connected, in seconds.
        deaths:
            The player's deaths.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        money:
            The player's deaths.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.
    """

    index: int
    name: str
    score: int
    duration: float

    deaths: Optional[int] = None
    money: Optional[int] = None
