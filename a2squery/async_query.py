import asyncio
import time
from types import TracebackType
from typing import Any, Optional, Tuple, Type, Union, List, Dict

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat
from .query import BaseA2SQuery, QueryResponse

__all__ = ("AsyncA2SQuery",)


class AsyncUDPProtocol(asyncio.DatagramProtocol):

    def __init__(self):
        self.queue: asyncio.Queue[Union[bytes, Exception]] = asyncio.Queue()

    def datagram_received(self, data: bytes, addr: Tuple[Union[str, Any], int]) -> None:
        self.queue.put_nowait(data)

    def error_received(self, exc: Exception) -> None:
        self.queue.put_nowait(exc)


class AsyncA2SQuery(BaseA2SQuery):
    """Asynchronously query various information from game servers implementing Valve's A2S protocol.
    
    It is recommended to use this class as a context manager to automatically release the underlying
    socket back to the OS. However you may also instantiate it normally and use `AsyncA2SQuery.connect()`.
    and `AsyncA2SQuery.close()`

    Args:
        host (str): The IP address or hostname of the game server WITHOUT the port.
        port (Optional[int]): The query port of the server. Usually the same as the
            connection port. Defaults to 27015.
        timeout (Optional[float]): Base time in seconds to wait for a response before
            retrying. Defaults to 1.0.
        retries (Optional[int]): Number of attempts to retry after dropped requests or
            invalid responses using exponential backoff. Defaults to 2.
        challenge_retries (Optional[int]): Number of attempts to retry challenge handshake
            before giving up. Defaults to 3.

    Examples:

        >>> async with A2SQuery("127.0.0.1") as a2s:
        ...     server_info = await a2s.info()
        ...     print(server_info.name)
    """

    def __init__(self, host: str, port: int = 27015, timeout: float = 1, retries: int = 2, challenge_retries: int = 3):
        super().__init__(host, port, timeout, retries, challenge_retries)

        self._transport = None
        self._protocol = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]):
        if exc_val:
            raise exc_val
        await self.close()

    async def _recv(self, timeout: float) -> bytes:
        if self._protocol is None:
            raise SocketClosed("Unable to receive data. Socket is closed.")

        try:
            result = await asyncio.wait_for(self._protocol.queue.get(), timeout)
        except asyncio.TimeoutError:
            raise TimeoutError()  # fix for 3.7 support

        if isinstance(result, bytes):
            return result

        raise result

    async def _receive_batch(self, initial_parser: Parser, end_time: float) -> Parser:
        batch_responses = [self._decode_batch_response(initial_parser)]
        
        while len(batch_responses) < batch_responses[0].total_packets:
            time_left = end_time - time.time()
            if time_left <= 0:
                raise TimeoutError("Timed out receiving expected batch responses.")

            response_data = await self._recv(time_left)
            
            parser = Parser(response_data)

            if ResponseFormat(parser.read_long()) is ResponseFormat.Batch:
                batch_responses.append(self._decode_batch_response(parser))

        return self._assemble_batch(batch_responses)

    async def _request(self, request_type: RequestType, expected_responses: Tuple[ResponseType, ...], body: Optional[str] = None, challenge: Optional[int] = None, _challenge_retries: int = 0) -> QueryResponse:
        if self._transport is None or self._protocol is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        if challenge is None:
            challenge = self._challenge

        request = self._build_request(request_type, body, challenge)

        for attempt in range(self.retries + 1):
            while not self._protocol.queue.empty():
                self._protocol.queue.get_nowait()

            self._transport.sendto(request)
            
            current_timeout = self.timeout * (2 ** attempt)
            end_time = time.time() + current_timeout

            try:
                while True:
                    time_left = end_time - time.time()
                    if time_left <= 0:
                        raise TimeoutError()

                    parser = Parser(await self._recv(time_left))

                    response_format = ResponseFormat(parser.read_long())

                    if response_format is ResponseFormat.Batch:
                        parser = await self._receive_batch(parser, end_time)

                    response_type = ResponseType(parser.read_byte())

                    if response_type is ResponseType.Challenge:
                        if _challenge_retries >= self.challenge_retries:
                            raise InvalidResponse("Server requested too many challenges.")

                        self._challenge = parser.read_long(advance=False)

                        return await self._request(
                            request_type, 
                            expected_responses,
                            body, 
                            challenge=self._challenge, 
                            _challenge_retries=_challenge_retries + 1
                        )

                    if response_type in expected_responses:
                        return QueryResponse(
                            format=response_format,
                            type=response_type,
                            payload=parser.data[parser.index:]
                        )
            except (TimeoutError, OSError):
                pass

        raise TimeoutError(f"Server failed to respond after {self.retries + 1} attempts.")

    async def connect(self) -> None:
        """Starts the connection to the game server.
        Must be closed with `AsyncA2SQuery.close()` when no longer in use."""
        if self._transport is not None:
            return

        loop = asyncio.get_running_loop()
        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: AsyncUDPProtocol(),
            remote_addr=(self.host, self.port)
        )
    
    async def close(self):
        """Closes the connection to the game server"""
        if self._transport:
            self._transport.close()
            self._transport = None
            self._protocol = None

    async def info(self) -> Union[SourceInfo, GoldSourceInfo]:
        """Query general information about the server.
        
        Returns:
            Returns :class:`a2squery.SourceInfo` for Source servers, 
            or :class:`a2squery.GoldSourceInfo` for GoldSource servers.
        """
        response = await self._request(
            RequestType.Info, 
            (ResponseType.InfoSource, ResponseType.InfoGoldSource), 
            "Source Engine Query\x00"
        )

        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.payload)

        return Parser.parse_goldsource_info(response.payload)

    async def players(self) -> List[Player]:
        """Query the server's current players/bots.
        
        This is an alias of A2SQuery.player().

        Returns:
            List of :class:`a2ssquery.Player` objects
        """
        return await self.player()

    async def player(self) -> List[Player]:
        """Query the server's current players/bots.
        
        Returns:
            List of :class:`a2ssquery.Player` objects
        """
        response = await self._request(RequestType.Player, (ResponseType.Player,))
        return Parser.parse_players(response.payload)

    async def rules(self) -> Dict[str, str]:
        """Query the server's rules/configuration variables in key/value pairs.
        
        Includes convars marked with FCVAR_NOTIFY as well as 
        any additional ones listed in the server configuration.

        Returns:
            Key/value dictionary of rules
        """
        response = await self._request(RequestType.Rules, (ResponseType.Rules,))
        return Parser.parse_rules(response.payload)
