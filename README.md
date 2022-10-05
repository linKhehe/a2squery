A2SQuery
====
A2SQuery is a python implementation of [Valve's A2S protocol](https://developer.valvesoftware.com/wiki/Server_queries>).

Docs
----
[View the full A2SQuery documentation here.](https://a2squery.readthedocs.io/en/latest/)

Features
----
A2SQuery can retrieve various information from any game
server that implements the protocol. This includes all Source and GoldSource games.
The library will handle connecting, parsing, and even automatically respond to challenge requests.

> A2SQuery does not support multi-packet responses as they
are impossible parse without knowing information about the server
beforehand.

Installation
----
Install the library via pypi with

    pip install a2squery

Getting Started
----
To start querying servers, we'll need an
instance of `a2squery.A2SQuery`. We can either create one manually,
or use a context manager. For this example, we will be using a context manager.

```python

    >>> from a2squery import A2SQuery

    >>> with A2SQuery("127.0.0.1", 27015) as a2s:

```

Now, with the A2SQuery instance, we can query the game server.

> When using `a2squery.A2SQuery` without a context manager.
Remember to call `a2squery.A2SQuery.close()` when finished.

```python

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
```

Supported Games
----

| App ID | Game                                                                        | Notes                                                                               |
|:------:|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
|  ...   | All Half-Life/Half-Life 2 mods and games                                    |                                                                                     |
|   10   | [Counter-Strike 1.6](https://store.steampowered.com/app/10)                 |                                                                                     |
|  440   | [Team Fortress 2](https://store.steampowered.com/app/440)                   |                                                                                     |
|  550   | [Left For Dead 2](https://store.steampowered.com/app/550)                   |                                                                                     |
|  730   | [Counter-Strike: Global Offensive](https://store.steampowered.com/app/730)  |                                                                                     |
|  1002  | [Rag Doll Kung Fu](https://store.steampowered.com/app/1002)                 |                                                                                     |
|  2400  | [The Ship: Murder Party](https://store.steampowered.com/app/2400)           | This game has various unique fields on `a2squery.SourceInfo` and `a2squery.Player`. |
|  4000  | [Garry's Mod](https://store.steampowered.com/app/4000)                      |                                                                                     |
| 17710  | [Nuclear Dawn](https://store.steampowered.com/app/17710)                    |                                                                                     |
| 70000  | [Dino D-Day](https://store.steampowered.com/app/70000)                      |                                                                                     |
| 107410 | [Arma 3](https://store.steampowered.com/app/107410)                         | The query port is the server port + 1.                                              |
| 115300 | [Call of Duty: Modern Warfare 3](https://store.steampowered.com/app/115300) |                                                                                     |
| 211820 | [Starbound](https://store.steampowered.com/app/211820)                      |                                                                                     |
| 244850 | [Space Engineers](https://store.steampowered.com/app/244850)                | The query port is the server port + 1.                                              |
| 304930 | [Unturned](https://store.steampowered.com/app/304930)                       | The query port is the server port + 1.                                              |
| 251570 | [7 Days To Die](https://store.steampowered.com/app/251570)                  |                                                                                     |
| 252490 | [Rust](https://store.steampowered.com/app/252490)                           |                                                                                     |
| 282440 | [Quake Live](https://store.steampowered.com/app/282440)                     |                                                                                     |
| 346110 | [ARK: Survival Evolved](https://store.steampowered.com/app/346110)          |                                                                                     |
| 108600 | [Project: Zomboid](https://store.steampowered.com/app/108600)               |                                                                                     | 
