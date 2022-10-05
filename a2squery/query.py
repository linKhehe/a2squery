import socket
import struct
import typing

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat

__all__ = ("QueryResponse", "A2SQuery")


class QueryResponse:

    def __init__(self, response_type: ResponseType, response_format: ResponseFormat, data: bytes):
        self.type = response_type
        self.format = response_format
        self.data = data


class A2SQuery:
    """Query various information from running Source/GoldSource game servers.

    This class allows you to interface with servers that implement the A2S query protocol.
    Each instance of A2SQuery opens a socket and connects to the specified server until closed.
    A2SQuery will authenticate server challenge requests.
    """

    def __init__(self, host: str, port: int = 27015, timeout: float = 10):
        """Create a new A2SQuery instance connected to the specified server.

        Arguments:
            host: The IP address of the server. Do not include a port here.
            port: The query port of the server. This is the same as the connection port for most games.
            timeout: How long to wait for connection/requests before timing out.
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))
        self._socket.settimeout(timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val
        self.close()

    def close(self) -> None:
        """Close the query socket. All requests after this will fail."""
        self._socket.close()
        self._socket = None

    def _request(self, request_type: RequestType, body: str = None, challenge: int = -1) -> QueryResponse:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        self._socket.send(struct.pack(f"<lB{len(body)}sl", -1, request_type.value, body.encode(), challenge))

        response_data = self._socket.recv(65536)

        parser = Parser(response_data)

        response = QueryResponse(
            response_format=ResponseFormat(parser.read_long()),
            response_type=ResponseType(parser.read_byte()),
            data=response_data[parser.index:]
        )

        if response.type is ResponseType.Challenge:
            if challenge != -1:
                raise InvalidResponse("Server requested too many challenges")

            return self._request(request_type, body, challenge=struct.unpack("<l", response.data)[0])

        return response

    def info(self) -> typing.Union[SourceInfo, GoldSourceInfo]:
        """Query general information about the server.

        Returns:
            :class:`a2squery.SourceInfo` or :class:`a2squery.GoldSourceInfo` depending on server's engine/response.
        """
        response = self._request(RequestType.Info, "Source Engine Query\x00")

        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.data)
        if response.type is ResponseType.InfoGoldSource:
            return Parser.parse_goldsource_info(response.data)

        raise InvalidResponse(
            f"Invalid server response type "
            f"(got {response.type}, expected {ResponseType.InfoSource} or {ResponseType.InfoGoldSource})"
        )

    def player(self) -> list[Player]:
        """Query the server's current players/bots.

        Returns:
            List of Player objects
        """
        response = self._request(RequestType.Player)

        if response.type is ResponseType.Player:
            return Parser.parse_players(response.data)

        raise InvalidResponse(
            f"Invalid server response type "
            f"(got {response.type}, expected {ResponseType.Player})"
        )

    def players(self) -> list[Player]:
        """Query the server's current players/bots.

        This is an alias of A2SQuery.player().

        Returns:
            List of Player objects
        """
        return self.player()

    def rules(self) -> dict[str, str]:
        """Query the server's rules/configuration variables in key/value pairs.

        The Console variables included are the ones marked with FCVAR_NOTIFY
        as well as any additional ones listed in the server configuration.

        Returns:
            Key/value dictionary of rules
        """
        response = self._request(RequestType.Rules)

        if response.type is ResponseType.Rules:
            return Parser.parse_rules(response.data)

        raise InvalidResponse(
            f"Invalid server response type "
            f"(got {response.type}, expected {ResponseType.Rules})"
        )
