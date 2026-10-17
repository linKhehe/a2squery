import socket
import time
from types import TracebackType
from typing import Optional, Type, Union, List, Dict, Tuple

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat
from .query import BaseA2SQuery, QueryResponse

__all__ = ("A2SQuery",)


class A2SQuery(BaseA2SQuery):
    """Synchronously query various information from game servers implementing Valve's A2S protocol.

    It is recommended to use this class as a context manager to automatically release the underlying
    socket back to the OS. However you may also instantiate it normally and use `A2SQuery.close()`.

    Args:
        host (str): The IP address or hostname of the game server WITHOUT the port.
        port (int, optional): The query port of the server. Usually the same as the
            connection port. Defaults to 27015.
        timeout (float, optional): Base time in seconds to wait for a response before
            retrying. Defaults to 1.0.
        retries (int, optional): Number of attempts to retry after dropped requests or
            invalid responses using exponential backoff. Defaults to 2.
        challenge_retries (int, optional): Number of attempts to retry challenge handshake
            before giving up. Defaults to 3.

    Examples:

        >>> with A2SQuery("127.0.0.1") as a2s:
        ...     server_info = a2s.info()
        ...     print(server_info.name)
    """

    def __init__(self, host: str, port: int = 27015, timeout: float = 1, retries: int = 2, challenge_retries: int = 3):
        super().__init__(host, port, timeout, retries, challenge_retries)

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))
        self._socket.settimeout(timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]):
        if exc_val:
            raise exc_val
        self.close()

    def _recv(self, timeout: float) -> bytes:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        self._socket.settimeout(timeout)
        return self._socket.recv(65536)

    def _receive_batch(self, initial_parser: Parser, end_time: float) -> Parser:
        batch_responses = [self._decode_batch_response(initial_parser)]
        
        while len(batch_responses) < batch_responses[0].total_packets:
            time_left = end_time - time.time()
            if time_left <= 0:
                raise TimeoutError("Timed out receiving expected batch packets.")

            parser = Parser(self._recv(time_left))

            if ResponseFormat(parser.read_long()) is ResponseFormat.Batch:
                batch_responses.append(self._decode_batch_response(parser))

        return self._assemble_batch(batch_responses)

    def _flush_socket(self):
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        self._socket.setblocking(False)
        try:
            while True:
                self._socket.recv(65536)
        except OSError:
            pass
        self._socket.setblocking(True)

    def _request(self, request_type: RequestType, expected_responses: Tuple[ResponseType, ...], body: Optional[str] = None, challenge: Optional[int] = None, _challenge_retries: int = 0) -> QueryResponse:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        if challenge is None:
            challenge = self._challenge

        request = self._build_request(request_type, body, challenge)

        for attempt in range(self.retries + 1):
            self._flush_socket()

            self._socket.send(request)

            current_timeout = self.timeout * (2 ** attempt)
            end_time = time.time() + current_timeout

            try:
                while True:
                    time_left = end_time - time.time()
                    if time_left <= 0:
                        raise TimeoutError()

                    parser = Parser(self._recv(time_left))

                    response_format = ResponseFormat(parser.read_long())
                
                    if response_format is ResponseFormat.Batch:
                        parser = self._receive_batch(parser, end_time)

                    response_type = ResponseType(parser.read_byte())

                    if response_type is ResponseType.Challenge:
                        if _challenge_retries >= self.challenge_retries:
                            raise InvalidResponse("Server requested too many challenges.")

                        self._challenge = parser.read_long(advance=False)

                        self._socket.settimeout(self.timeout)
                        return self._request(
                            request_type, 
                            expected_responses,
                            body, 
                            challenge=self._challenge, 
                            _challenge_retries=_challenge_retries + 1
                        )

                    if response_type in expected_responses:
                        self._socket.settimeout(self.timeout)
                        return QueryResponse(
                            format=response_format,
                            type=response_type,
                            payload=parser.data[parser.index:]
                        )
            except TimeoutError, OSError:
                pass

        raise TimeoutError(f"Server failed to respond after {self.retries + 1} attempts.")

    def close(self) -> None:
        """Close the underlying socket. All requests after this will fail."""
        if self._socket is None:
            raise SocketClosed("The socket is already closed.")

        self._socket.close()
        self._socket = None

    def info(self) -> Union[SourceInfo, GoldSourceInfo]:
        """Query general information about the server.

        Returns:
            Returns :class:`a2squery.SourceInfo` for Source servers, 
            or :class:`a2squery.GoldSourceInfo` for GoldSource servers.
        """
        response = self._request(RequestType.Info, (ResponseType.InfoGoldSource, ResponseType.InfoSource), "Source Engine Query\x00")

        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.payload)
        return Parser.parse_goldsource_info(response.payload)

    def players(self) -> List[Player]:
        """Query the server's current players/bots.

        This is an alias of A2SQuery.player().

        Returns:
            List of :class:`a2ssquery.Player` objects
        """
        return self.player()

    def player(self) -> List[Player]:
        """Query the server's current players/bots.

        Returns:
            List of :class:`a2ssquery.Player` objects
        """
        response = self._request(RequestType.Player, (ResponseType.Player,))
        return Parser.parse_players(response.payload)

    def rules(self) -> Dict[str, str]:
        """Query the server's rules/configuration variables in key/value pairs.

        Includes convars marked with FCVAR_NOTIFY as well as 
        any additional ones listed in the server configuration.

        Returns:
            Key/value dictionary of rules
        """
        response = self._request(RequestType.Rules, (ResponseType.Rules,))
        return Parser.parse_rules(response.payload)
