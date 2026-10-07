import asyncio
import socket
import unittest
import typing
from a2squery import A2SQuery, AsyncA2SQuery, SourceInfo, GoldSourceInfo, Player
import threading

@typing.no_type_check
def async_test(coro): 
    @typing.no_type_check
    def wrapper(self, *args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(self, *args, **kwargs))
        finally:
            loop.close()
    return wrapper


class A2SMockServer:

    def __init__(self, host: str):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(1)
        self._socket.bind((host, 0))
        self._should_exit = False
        self._use_goldsource_info = False
        self._use_compression = False

        self.port = self._socket.getsockname()[1]

    def set_use_goldsource_info(self, v: bool):
        self._use_goldsource_info = v

    def set_use_compression(self, v: bool):
        self._use_compression = v

    def close(self):
        self._should_exit = True
        self._socket.close()

    def recv(self):
        while True:
            if self._should_exit:
                return

            try:
                data, client = self._socket.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError as exception:
                if self._should_exit:
                    return
                raise exception

            if data == b"\xff\xff\xff\xffTSource Engine Query\x00\xff\xff\xff\xff":
                self._socket.sendto(
                    b"\xFF\xFF\xFF\xFF\x41\x0A\x08\x5E\xEA",
                    client
                )
            elif data == b"\xff\xff\xff\xffTSource Engine Query\x00\x0A\x08\x5E\xEA":
                if self._use_goldsource_info:
                    self._socket.sendto(
                        b"\xff\xff\xff\xffmaddress\x00name\x00map\x00valve\x00Half-Life\x00\x14 /dw\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x01",
                        client
                    )
                else:
                    self._socket.sendto(
                        b"\xff\xff\xff\xffI\x11Server Name\x00Map Name\x00Folder\x00Game\x00\x8a\x84'7\x00dw\x00\x001.64.144629\x00\xb1\xfe\x08\x06<\x88\x85\xf1S@\x01keywords\x00\x8a\x84\x00\x00\x00\x00\x00\x00",
                        client
                    )
            elif data == b"\xff\xff\xff\xffU\xff\xff\xff\xff":
                self._socket.sendto(
                    b"\xFF\xFF\xFF\xFF\x41\x0A\x08\x5E\xEA",
                    client
                )
            elif data == b"\xff\xff\xff\xffU\x0A\x08\x5E\xEA":
                self._socket.sendto(
                    b"\xff\xff\xff\xffD\x04\x00Player 0\x00\x03\x00\x00\x00\x00\xa8\xc1E\x00Player 1\x00\x00\x00\x00\x00\x00@8C\x00Player 2\x00\x00\x00\x00\x00f\xc2\xedI\x00Player 3\x00\x00\x00\x00\x00\x00\x00\x0eb",
                    client
                )
            elif data == b"\xff\xff\xff\xff\x56\xff\xff\xff\xff":
                self._socket.sendto(
                    b"\xFF\xFF\xFF\xFF\x41\x0A\x08\x5E\xEA",
                    client
                )
            elif data == b"\xff\xff\xff\xff\x56\x0A\x08\x5E\xEA":
                if self._use_compression:
                    self._socket.sendto(
                        b"\xfe\xff\xff\xff\x01\x00\x00\x80\x01\x00\xb0\x047\x00\x00\x00U\x82\xcblBZh91AY&SY\xd7a-\x82\x00\x00\x1b\xcf\x80\xd0\x00\x10\x00\x02\x00\x00\x00\xae\x0e\xff \x00\x00\xa0\x00Hj\x9e$z\x1a\x8d4zz\x85\x1a2\x06\x8d24*\x7fH{<\xf6\x8aN\x1a\xadt\xa1q\x9c\xc4\xf56\xd4(\x95\x02\xac<\t\xa3L\x13\xc6\xbf\x17rE8P\x90\xd7a-\x82",
                        client
                    )
                else:
                    self._socket.sendto(
                        b"\xff\xff\xff\xffEB\x00a2squery\x00bruh momentum\x00allow_spectators\x001\x00amx_client_languages\x001\x00amx_language\x00en\x00amx_nextmap\x00crossfire\x00amx_timeleft\x0000:00\x00amxmodx_version\x001.8.2\x00br_unlock\x00v1.0\x00coop\x000\x00deathmatch\x001\x00decalfrequency\x0040\x00dp_version\x000.9.548\x00edgefriction\x002\x00hackdetector_version\x000.15.328.lite\x00lambda_ranks\x00enabled\x00lambda_status\x00loaded\x00lambda_version\x000.10g\x00max_queries_sec\x001\x00max_queries_sec_global\x001\x00max_queries_window\x001\x00metamod_version\x001.21p37\x00mp_allowmonsters\x000\x00mp_autocrosshair\x001\x00mp_bunnyhop\x001\x00mp_chattime\x0010\x00mp_consistency\x001\x00mp_falldamage\x000\x00mp_flashlight\x000\x00mp_footsteps\x001\x00mp_forcerespawn\x001\x00mp_fraglimit\x000\x00mp_fragsleft\x000\x00mp_friendlyfire\x000\x00mp_logfile\x001\x00mp_selfgauss\x000\x00mp_teamlist\x00hgrunt;scientist\x00mp_teamplay\x000\x00mp_timeleft\x000\x00mp_timelimit\x000\x00mp_weaponstay\x000\x00mp_welcomecam\x000\x00pausable\x000\x00sv_accelerate\x0010\x00sv_aim\x000\x00sv_airaccelerate\x00100\x00sv_allowupload\x001\x00sv_bounce\x001\x00sv_cheats\x000\x00sv_clienttrace\x003.5\x00sv_contact\x00discord.gg/bNzhcdf\x00sv_friction\x004\x00sv_gravity\x00800\x00sv_logblocks\x000\x00sv_maxrate\x0050000\x00sv_maxspeed\x00320\x00sv_minrate\x000\x00sv_password\x000\x00sv_proxies\x001\x00sv_stepsize\x0018\x00sv_stopspeed\x00100\x00sv_uploadmax\x000.5\x00sv_voiceenable\x001\x00sv_wateraccelerate\x0010\x00sv_waterfriction\x001\x00VTC_Version\x002017RC5\x00whb_version\x001.5.697\x00",
                        client
                    )


class TestAsyncA2SQuery(unittest.TestCase):

    def setUp(self):
        self.server = A2SMockServer("127.0.0.1")

        self.server_thread = threading.Thread(target=self.server.recv, daemon=True)
        self.server_thread.start()

    @async_test
    async def test_async_source_info(self):
        self.server.set_use_goldsource_info(False)
        async with AsyncA2SQuery("127.0.0.1", self.server.port) as a2s:
            self.assertTrue(isinstance(await a2s.info(), SourceInfo))
            self.assertTrue((await a2s.info()).name == "Server Name")

    @async_test
    async def test_async_goldsource_info(self):
        self.server.set_use_goldsource_info(True)
        async with AsyncA2SQuery("127.0.0.1", self.server.port) as a2s:
            self.assertTrue(isinstance(await a2s.info(), GoldSourceInfo))
            self.assertTrue((await a2s.info()).name == "name")

    @async_test
    async def test_async_players(self):
        async with AsyncA2SQuery("127.0.0.1", self.server.port) as a2s:
            self.assertTrue(isinstance((await a2s.players())[1], Player)) # type: ignore
            self.assertTrue((await a2s.players())[0].name == "Player 0")

    @async_test
    async def test_async_rules(self):
        async with AsyncA2SQuery("127.0.0.1", self.server.port) as a2s:
            self.assertTrue((await a2s.rules()).get("a2squery") == "bruh momentum")

    @async_test
    async def test_async_compression(self):
        async with AsyncA2SQuery("127.0.0.1", self.server.port) as a2s:
            self.server.set_use_compression(True)
            self.assertTrue((await a2s.rules()).get("a2squery") == "compressed_success")

    def tearDown(self):
        self.server.close()


class TestA2SQuery(unittest.TestCase):

    def setUp(self):
        self.server = A2SMockServer("127.0.0.1")
        self.a2s = A2SQuery("127.0.0.1", self.server.port)

        self.server_thread = threading.Thread(target=self.server.recv, daemon=True)
        self.server_thread.start()

    def test_source_info(self):
        self.server.set_use_goldsource_info(False)
        self.assertTrue(isinstance(self.a2s.info(), SourceInfo))
        self.assertTrue(self.a2s.info().name == "Server Name")

    def test_goldsource_info(self):
        self.server.set_use_goldsource_info(True)
        self.assertTrue(isinstance(self.a2s.info(), GoldSourceInfo))
        self.assertTrue(self.a2s.info().name == "name")

    def test_players(self):
        self.assertTrue(isinstance(self.a2s.players()[1], Player)) # type: ignore
        self.assertTrue(self.a2s.players()[0].name == "Player 0")

    def test_rules(self):
        self.assertTrue(self.a2s.rules().get("a2squery") == "bruh momentum")

    def test_compression(self):
        self.server.set_use_compression(True)
        self.assertTrue(self.a2s.rules().get("a2squery") == "compressed_success")

    def tearDown(self):
        self.server.close()
        self.a2s.close()


if __name__ == "__main__":
    unittest.main()
