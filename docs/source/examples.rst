Examples
====

With context management (Synchronous)
-------------------------------------

.. code-block:: python

    from a2squery import A2SQuery

    with A2SQuery("127.0.0.1", 27015) as a2s:
        info = a2s.info()

        print(info.map)
        print(info.game)

        players = a2s.players()

        print(players[0].name)
        print(players[1].score)

        rules = a2s.rules()

        print(rules.get("sv_cheats"))

Without context management (Synchronous)
----------------------------------------

.. code-block:: python

    from a2squery import A2SQuery

    a2s = A2SQuery("127.0.0.1", 27015)

    info = a2s.info()

    print(info.map)
    print(info.game)

    players = a2s.players()

    print(players[0].name)
    print(players[1].score)

    rules = a2s.rules()

    print(rules.get("sv_cheats"))

    a2s.close()

With context management (Asynchronous)
--------------------------------------

.. code-block:: python

    from a2squery import AsyncA2SQuery

    # ...

    async with AsyncA2SQuery("127.0.0.1", 27015) as a2s:
        info = await a2s.info()

        print(info.map)
        print(info.game)

        players = await a2s.players()

        print(players[0].name)
        print(players[1].score)

        rules = await a2s.rules()

        print(rules.get("sv_cheats"))

Without context management (Asynchronous)
-----------------------------------------

.. code-block:: python

    from a2squery import AsyncA2SQuery

    # ...

    a2s = AsyncA2SQuery("127.0.0.1", 27015)
    await a2s.connect()

    info = await a2s.info()

    print(info.map)
    print(info.game)

    players = await a2s.players()

    print(players[0].name)
    print(players[1].score)

    rules = await a2s.rules()

    print(rules.get("sv_cheats"))

    await a2s.close()
