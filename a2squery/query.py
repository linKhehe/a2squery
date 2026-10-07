import bz2
import socket
import struct
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type, Union, List, Dict

from .data import SourceInfo, GoldSourceInfo, Player
from .exceptions import InvalidResponse, SocketClosed
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat, BatchResponseEngine

__all__ = ("QueryResponse", "A2SQuery")


@dataclass
class QueryResponse:

    type: ResponseType
    format: ResponseFormat
    payload: bytes


@dataclass
class BatchQueryResponse:

    payload: bytes
    packet_number: int
    total_packets: int
    engine: BatchResponseEngine
    compressed: bool


class A2SQuery:
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
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((host, port))
        self._socket.settimeout(timeout)

        self.challenge_retries = challenge_retries

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

    @staticmethod
    def _decode_batch_response(parser: Parser) -> BatchQueryResponse:
        compressed = bool(parser.read_long() & 0x80000000)
        index_or_total = parser.read_byte()
        next_byte = parser.read_byte(advance=False)

        upper_packet = index_or_total >> 4
        lower_packet = index_or_total & 0x0F

        if upper_packet > 0 :
            packet_number = upper_packet
            total_packets = lower_packet
            engine = BatchResponseEngine.GoldSource
        else:
            if next_byte == 0xFF:
                packet_number = 0
                total_packets = lower_packet
                engine = BatchResponseEngine.GoldSource
            else:
                total_packets = index_or_total
                packet_number = parser.read_byte()
                engine = BatchResponseEngine.Source

        return BatchQueryResponse(
            payload=parser.data[parser.index:],
            packet_number=packet_number,
            total_packets=total_packets,
            engine=engine,
            compressed=compressed
        )

    def _receive_batch(self, initial_parser: Parser) -> Parser:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        batch_responses = [self._decode_batch_response(initial_parser)]
        
        while len(batch_responses) < batch_responses[0].total_packets:
            response_data = self._socket.recv(65536)

            parser = Parser(response_data)

            if ResponseFormat(parser.read_long()) is not ResponseFormat.Batch:
                raise InvalidResponse("Invalid batch response")

            batch_responses.append(self._decode_batch_response(parser))

        batch_responses.sort(key=lambda r: r.packet_number)
        initial_response = batch_responses[0]

        if initial_response.engine == BatchResponseEngine.Source:
            initial_payload = initial_response.payload
            has_mtu = False

            if initial_response.compressed:
                if initial_payload[8:11] == b"BZh":
                    has_mtu = False
                elif initial_payload[10:13] == b"BZh":
                    has_mtu = True
                else:
                    raise InvalidResponse("Expected bzip header in compressed batch response, but none was found")

                initial_response.payload = initial_response.payload[10 if has_mtu else 8:]
            else:
                if initial_payload.startswith(b"\xFF\xFF\xFF\xFF"):
                    has_mtu = False
                elif initial_payload[2:6] == b"\xFF\xFF\xFF\xFF":
                    has_mtu = True
                elif ResponseType(initial_payload[0]) is not ResponseType.Unknown:
                    has_mtu = False
                elif len(initial_payload) >= 3 and ResponseType(initial_payload[2]) is not ResponseType.Unknown:
                    has_mtu = True

            if has_mtu:
                for response in batch_responses:
                    if initial_response.compressed and response.packet_number == 0:
                        continue # already handled the first compressed packet above

                    response.payload = response.payload[2:]

        parser = Parser(b"".join([response.payload for response in batch_responses]))

        if initial_response.compressed:
            try:
                parser.data = bz2.decompress(parser.data)
            except OSError as e:
                raise InvalidResponse(f"Failed to decompress bzip payload: {e}")

        if parser.data.startswith(b"\xFF\xFF\xFF\xFF"):
            parser.read_long()

        return parser

    def _request(self, request_type: RequestType, body: Optional[str] = None, challenge: int = -1, _retries: int = 0) -> QueryResponse:
        if self._socket is None:
            raise SocketClosed("The socket has been closed. No more requests can be made.")

        if body is None:
            body = ""

        self._socket.send(struct.pack(f"<lB{len(body)}sl", -1, request_type.value, body.encode(), challenge))

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

    def player(self) -> List[Player]:
        """Query the server's current players/bots.

        Returns:
            List of Player objects
        """
        response = self._request(RequestType.Player)

        if response.type is ResponseType.Player:
            return Parser.parse_players(response.payload)

        raise InvalidResponse(f"Invalid server response type (got {response.type}, expected {ResponseType.Player})")

    def players(self) -> List[Player]:
        """Query the server's current players/bots.

        This is an alias of A2SQuery.player().

        Returns:
            List of Player objects
        """
        return self.player()

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
