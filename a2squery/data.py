from dataclasses import dataclass
from typing import Optional

from .enums import Environment, ServerType

__all__ = ("SourceInfo", "GoldSourceInfo", "Player")


@dataclass
class SourceInfo:
    """Represents a Source server's information response

    Attributes:
        protocol (int): The version of the protocol used by the server.
        name (str): The hostname of the server. This is what you see on a server list.
        map (str): The current map.
        folder (str): The name of the folder containing the game files. (ex. Counter-Strike: Global Offensive servers will return "csgo")
        game (str): The full name of the game the server is running.
        app_id (int): The steam App ID of the server. (ex. 730 for Counter-Strike: Global Offensive servers)
        players (int): The number of players on the server. This may include bots.
        max_players (int): The max number of players allowed.
        bots (int): The number of bots on the server.
        server_type (:class:`a2squery.enums.ServerType`): The type of server. Servers can be Dedicated, NonDedicated, or SourceTV.
        environment (:class:`a2squery.enums.Environment`): The operating system the server is running. For Source servers this can be Linux, Mac, or Windows.
        password (bool): Whether of not the server is password locked.
        vac (bool): Indicates whether the server is protected by VAC or not.

        version (str): The version of the game installed on the server.
        extra_data_flag (int): This field specifies what extra data is included in the packet.

        port (int): The server's game port.
        steam_id (int): The server's steam ID.
        spectator_port (int): The spectator port used for SourceTV.
        spectator_name (str): The name of the SourceTV spectator server.
        keywords (str): Tags used to describe the server.
        game_id (int): The server's 64-bit game ID.

        mode (Optional[int]):
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

        witnesses (Optional[int]):
            The number of witnesses necessary to have a player arrested.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        duration (Optional[int]):
            The time before a player is arrested while being witnessed in seconds.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.
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


@dataclass
class GoldSourceInfo:
    """Represents a GoldSource server's info response.

    Attributes:
        address (str): The IP address and port of the server.
        name (str): The hostname of the server. This is what you see on a server list.
        map (str): The current map.
        folder (str): The name of the folder containing the game files. (ex. Counter-Strike: Global Offensive servers will return "csgo")
        game (str): The full name of the game the server is running.
        players (int): The number of players on the server. This may include bots.
        max_players (int): The max number of players allowed.
        protocol (int): The version of the protocol used by the server.
        server_type (:class:`a2squery.enums.ServerType`): The type of server. Servers can be Dedicated, NonDedicated, or SourceTV.
        environment (:class:`a2squery.enums.Environment`): The operating system the server is running. For GoldSource servers this can be Linux or Windows.
        password (bool): Whether of not the server is password locked.
        modded (bool): Indicates if the server is a Half-Life mod or not.
        vac (bool): Indicates whether the server is protected by VAC or not.
        bots (int): The number of bots on the server.

        mod_link (Optional[str]):
            A URL to the mod's website.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_download_link (Optional[str]):
            A URL to download the mod.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_version (Optional[int]):
            The version of the mod running on the server.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_size (Optional[int]):
            The space used by the mod in bytes.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_multiplayer_only (Optional[bool]):
            Indicates whether the mod is multiplayer only or single-player and multiplayer.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.

        mod_uses_custom_dll (Optional[bool]):
            Indicates whether the mod uses its own DLL or the Half-Life DLL.

            .. danger::

                This field is only populated when :py:attr:`a2squery.GoldSourceInfo.modded` is True.
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


@dataclass
class Player:
    """Represents a queried player.

    Attributes:
        index (int): The index of the player's chunk. This is not the player's index in the list of players.
        name (str): The player's name.
        score (int): The player's score. This is unique to the server/game but is usually kills/points.
        duration (float): How long the player has been connected, in seconds.

        deaths (Optional[int]):
            The player's deaths.

            .. warning::

                This field is only populated on servers running
                `The Ship: Murder Party <https://store.steampowered.com/app/2400/The_Ship_Murder_Party/>`_
                where :py:attr:`a2squery.SourceInfo.app_id` == 2400.

        money (Optional[int]):
            The player's money.

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
