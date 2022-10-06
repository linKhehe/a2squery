A2SQuery
====
A2SQuery is a python implementation of `Valve's A2S protocol <https://developer.valvesoftware.com/wiki/Server_queries>`_.

Features
----
A2SQuery can retrieve various information from any game
server that implements the protocol. This includes all Source and GoldSource games.
The library will handle connecting, parsing, and even automatically respond to challenge requests.

.. note::
    A2SQuery does not support multi-packet responses as they
    are impossible parse without knowing information about the server
    beforehand.

Prerequisites
----
- Python >= 3.6

Installation
----
Install the library via pypi with::

    pip install a2squery

Getting Started
----
To start querying servers, we'll need an
instance of :class:`a2squery.A2SQuery`. We can either create one manually,
or use a context manager. For this example, we will be using a context manager.

.. doctest::

    >>> from a2squery import A2SQuery

    >>> with A2SQuery("127.0.0.1", 27015) as a2s:

Now, with a the A2SQuery instance, we can query the game server.

.. tip::

    When using :class:`a2squery.A2SQuery` without a context manager.
    Remember to call :py:meth:`a2squery.A2SQuery.close` when finished.

.. doctest::

    >>> from a2squery import A2SQuery

    >>> with A2SQuery("127.0.0.1", 27015) as a2s:
    >>>     print(a2s.info())

    SourceInfo(
        protocol=17, name="Awp Bhop", map="awp_iceworld",
        folder="csgo", game="Counter-Strike: Global Offensive",
        app_id=730, players=43, max_players=64, bots=0,
        server_type=ServerType.Dedicated, environment=Environment.Linux,
        password=False, vac=True, version="1.38.4.4", extra_data_flag=177,
        mode=None, witnesses=None, duration=None,
        port=27015, steam_id=85568392924437989, spectator_port=None,
        spectator_name=None, keywords="awp,bhop,a2squeryiscool", game_id=730
    )

Reference Pages
-----------------

.. toctree::
    :maxdepth: 2

    Querier <query>
    Responses <data>
    Enums <enums>

Topics
----
.. toctree::
    :maxdepth: 2

    Examples <examples>
    License <license>

Supported Games
----

.. list-table::
    :header-rows: 1
    :widths: 20 40 40

    * - App ID
      - Game
      - Notes
    * - ...
      - All Half-Life/Half-Life 2 mods and games
      -
    * - 10
      - `Counter-Strike 1.6 <https://store.steampowered.com/app/10>`_
      -
    * - 440
      - `Team Fortress 2 <https://store.steampowered.com/app/440>`_
      -
    * - 550
      - `Left For Dead 2 <https://store.steampowered.com/app/550>`_
      -
    * - 730
      - `Counter-Strike: Global Offensive <https://store.steampowered.com/app/730>`_
      -
    * - 1002
      - `Rag Doll Kung Fu <https://store.steampowered.com/app/1002>`_
      -
    * - 2400
      - `The Ship: Murder Party <https://store.steampowered.com/app/2400>`_
      - This game has various unique fields on :py:class:`a2squery.SourceInfo` and :py:class:`a2squery.Player`.
    * - 4000
      - `Garry's Mod <https://store.steampowered.com/app/4000>`_
      -
    * - 17710
      - `Nuclear Dawn <https://store.steampowered.com/app/17710>`_
      -
    * - 70000
      - `Dino D-Day <https://store.steampowered.com/app/70000>`_
      -
    * - 107410
      - `Arma 3 <https://store.steampowered.com/app/107410>`_
      - The query port is the server port + 1.
    * - 115300
      - `Call of Duty: Modern Warfare 3 <https://store.steampowered.com/app/115300>`_
      -
    * - 211820
      - `Starbound <https://store.steampowered.com/app/211820>`_
      -
    * - 244850
      - `Space Engineers <https://store.steampowered.com/app/244850>`_
      - The query port is the server port + 1.
    * - 304930
      - `Unturned <https://store.steampowered.com/app/304930>`_
      - The query port is the server port + 1.
    * - 251570
      - `7 Days To Die <https://store.steampowered.com/app/251570>`_
      -
    * - 252490
      - `Rust <https://store.steampowered.com/app/252490>`_
      -
    * - 282440
      - `Quake Live <https://store.steampowered.com/app/282440>`_
      -
    * - 346110
      - `ARK: Survival Evolved <https://store.steampowered.com/app/346110>`_
      -
    * - 108600
      - `Project: Zomboid <https://store.steampowered.com/app/108600>`_
      -
