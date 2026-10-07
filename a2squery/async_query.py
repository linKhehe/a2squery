import asyncio
from types import TracebackType
from typing import Any, Optional, Tuple, Type, Union, List, Dict

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat
from .query import BaseA2SQuery, QueryResponse

__all__ = ("AsyncA2SQuery",)


class A2SUDPProtocol(asyncio.DatagramProtocol):

    def __init__(self):
        self.queue: asyncio.Queue[Union[bytes, Exception]] = asyncio.Queue()

    def datagram_received(self, data: bytes, addr: Tuple[Union[str, Any], int]) -> None:
        self.queue.put_nowait(data)

    def error_received(self, exc: Exception) -> None:
        self.queue.put_nowait(exc)


class AsyncA2SQuery(BaseA2SQuery):
    """Asynchronously query various information from running Source/GoldSource game servers.
    
    This class allows you to interface with servers that implement the A2S query protocol.
    Running `AsyncA2SQuery.connect()` opens a socket and connects to the specified server until closed.
    """

    def __init__(self, host: str, port: int = 27015, timeout: float = 10, challenge_retries: int = 3):
        super().__init__(host, port, timeout, challenge_retries)

        self._transport = None
        self._protocol = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]):
        if exc_val:
            raise exc_val
        await self.close()

    async def connect(self) -> None:
        """Starts the connection to the game server.
        Must be closed with `AsyncA2SQuery.close()` when no longer in use.
        """
        loop = asyncio.get_running_loop()
        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: A2SUDPProtocol(),
            remote_addr=(self.host, self.port)
        )

    async def close(self):
        """Closes the connection to the game server"""
        if self._transport:
            self._transport.close()

    async def _recv(self) -> bytes:
        if self._protocol is None:
            raise SocketClosed("Unable to receive data. Socket is closed.")

        result = await asyncio.wait_for(self._protocol.queue.get(), self.timeout)

        if isinstance(result, bytes):
            return result

        raise result

    async def _receive_batch(self, initial_parser: Parser) -> Parser:
        batch_responses = [self._decode_batch_response(initial_parser)]
        
        while len(batch_responses) < batch_responses[0].total_packets:
            response_data = await self._recv()
            
            parser = Parser(response_data)
            if ResponseFormat(parser.read_long()) is not ResponseFormat.Batch:
                raise InvalidResponse("Invalid batch response")
                
            batch_responses.append(self._decode_batch_response(parser))

        return self._assemble_batch(batch_responses)

    async def _request(self, request_type: RequestType, body: Optional[str] = None, challenge: int = -1, _retries: int = 0) -> QueryResponse:
        if self._transport is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        self._transport.sendto(self._build_request(request_type, body, challenge))

        parser = Parser(await self._recv())

        response_format = ResponseFormat(parser.read_long())

        if response_format is ResponseFormat.Batch:
            parser = await self._receive_batch(parser)

        response_type = ResponseType(parser.read_byte())

        if response_type is ResponseType.Unknown:
            raise InvalidResponse("Server responded with an unknown response type. Failed to parse response.")

        if response_type is ResponseType.Challenge:
            if _retries >= self.challenge_retries:
                raise InvalidResponse("Server requested too many challenges.")

            return await self._request(request_type, body, challenge=parser.read_long(advance=False), _retries=_retries + 1)

        return QueryResponse(
            format=response_format,
            type=response_type,
            payload=parser.data[parser.index:]
        )

    async def info(self) -> Union[SourceInfo, GoldSourceInfo]:
        """Query general information about the server.

        Returns:
            :class:`a2squery.SourceInfo` or :class:`a2squery.GoldSourceInfo` depending on server's engine/response.
        """
        response = await self._request(RequestType.Info, "Source Engine Query\x00")

        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.payload)
        if response.type is ResponseType.InfoGoldSource:
            return Parser.parse_goldsource_info(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.InfoSource} or {ResponseType.InfoGoldSource})")

    async def players(self) -> List[Player]:
        """Query the server's current players/bots.

        This is an alias of AsyncA2SQuery.player().

        Returns:
            List of Player objects
        """
        return await self.player()

    async def player(self) -> List[Player]:
        """Query the server's current players/bots.

        Returns:
            List of Player objects
        """
        response = await self._request(RequestType.Player)

        if response.type is ResponseType.Player:
            return Parser.parse_players(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.Player})")

    async def rules(self) -> Dict[str, str]:
        """Query the server's rules/configuration variables in key/value pairs.

        The Console variables included are the ones marked with FCVAR_NOTIFY
        as well as any additional ones listed in the server configuration.

        Returns:
            Key/value dictionary of rules
        """
        response = await self._request(RequestType.Rules)

        if response.type is ResponseType.Rules:
            return Parser.parse_rules(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.Rules})")
