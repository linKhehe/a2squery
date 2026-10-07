import socket
from types import TracebackType
from typing import Optional, Type, Union, List, Dict

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat
from .query import BaseA2SQuery, QueryResponse

__all__ = ("A2SQuery",)


class A2SQuery(BaseA2SQuery):
    """Query various information from running Source/GoldSource game servers.

    This class allows you to interface with servers that implement the A2S query protocol.
    Each instance of A2SQuery opens a socket and connects to the specified server until closed.
    """

    def __init__(self, host: str, port: int = 27015, timeout: float = 10, challenge_retries: int = 3):
        """Create a new A2SQuery instance connected to the specified server.

        Arguments:
            host: The IP address of the server. Do not include a port here.
            port: The query port of the server. This is the same as the connection port for most games.
            timeout: How long to wait for connection/requests before timing out.
        """
        super().__init__(host, port, timeout, challenge_retries)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))
        self._socket.settimeout(timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]):
        if exc_val:
            raise exc_val
        self.close()

    def close(self) -> None:
        """Close the query socket. All requests after this will fail."""
        if self._socket is None:
            raise SocketClosed("The socket is already closed.")

        self._socket.close()
        self._socket = None

    def _receive_batch(self, initial_parser: Parser) -> Parser:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        batch_responses = [self._decode_batch_response(initial_parser)]
        
        while len(batch_responses) < batch_responses[0].total_packets:
            response_data = self._socket.recv(65536)

            parser = Parser(response_data)

            if ResponseFormat(parser.read_long()) is not ResponseFormat.Batch:
                raise InvalidResponse("First response indicated batching, but other responses were invalid.")

            batch_responses.append(self._decode_batch_response(parser))

        return self._assemble_batch(batch_responses)

    def _request(self, request_type: RequestType, body: Optional[str] = None, challenge: int = -1, _retries: int = 0) -> QueryResponse:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        self._socket.send(self._build_request(request_type, body, challenge))

        parser = Parser(self._socket.recv(65536))

        response_format = ResponseFormat(parser.read_long())

        if response_format is ResponseFormat.Batch:
            parser = self._receive_batch(parser)

        response_type = ResponseType(parser.read_byte())

        if response_type is ResponseType.Unknown:
            raise InvalidResponse("Server responded with an unknown response type. Failed to parse response.")

        if response_type is ResponseType.Challenge:
            if _retries >= self.challenge_retries:
                raise InvalidResponse("Server requested too many challenges.")

            return self._request(request_type, body, challenge=parser.read_long(advance=False), _retries=_retries + 1)

        return QueryResponse(
            format=response_format,
            type=response_type,
            payload=parser.data[parser.index:]
        )

    def info(self) -> Union[SourceInfo, GoldSourceInfo]:
        """Query general information about the server.

        Returns:
            :class:`a2squery.SourceInfo` or :class:`a2squery.GoldSourceInfo` depending on server's engine/response.
        """
        response = self._request(RequestType.Info, "Source Engine Query\x00")

        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.payload)
        if response.type is ResponseType.InfoGoldSource:
            return Parser.parse_goldsource_info(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.InfoSource} or {ResponseType.InfoGoldSource})")

    def players(self) -> List[Player]:
        """Query the server's current players/bots.

        This is an alias of A2SQuery.player().

        Returns:
            List of Player objects
        """
        return self.player()

    def player(self) -> List[Player]:
        """Query the server's current players/bots.

        Returns:
            List of Player objects
        """
        response = self._request(RequestType.Player)

        if response.type is ResponseType.Player:
            return Parser.parse_players(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.Player})")

    def rules(self) -> Dict[str, str]:
        """Query the server's rules/configuration variables in key/value pairs.

        The Console variables included are the ones marked with FCVAR_NOTIFY
        as well as any additional ones listed in the server configuration.

        Returns:
            Key/value dictionary of rules
        """
        response = self._request(RequestType.Rules)

        if response.type is ResponseType.Rules:
            return Parser.parse_rules(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.Rules})")
