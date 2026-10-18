import bz2
import struct
from dataclasses import dataclass
from typing import List, Union

from .data import SourceInfo, GoldSourceInfo
from .exceptions import InvalidResponse
from .parser import Parser
from .enums import RequestType, ResponseType, ResponseFormat, BatchResponseEngine


@dataclass
class QueryResponse:

    type: ResponseType
    format: ResponseFormat
    payload: bytes


@dataclass
class BatchQueryResponse:

    response_id: int
    payload: bytes
    packet_number: int
    total_packets: int
    engine: BatchResponseEngine
    compressed: bool


class BaseA2SQuery:

    SIMPLE_HEADER = b'\xFF\xFF\xFF\xFF'

    def __init__(self, host: str, port: int = 27015, timeout: float = 1.0, retries: int = 2, challenge_retries: int = 3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.challenge_retries = challenge_retries
        self._challenge: int = -1

    @staticmethod
    def _decode_batch_response(parser: Parser) -> BatchQueryResponse:
        raw_id = parser.read_long()
        compressed = bool(raw_id & 0x80000000)
        response_id = raw_id & 0x7FFFFFFF
        index_or_total = parser.read_byte()
        next_byte = parser.read_byte(advance=False)

        upper_packet = index_or_total >> 4
        lower_packet = index_or_total & 0x0F

        if upper_packet > 0:
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

        if total_packets <= 0:
            raise InvalidResponse("Batch response reported zero total packets.")

        return BatchQueryResponse(
            response_id=response_id,
            payload=parser.data[parser.index:],
            packet_number=packet_number,
            total_packets=total_packets,
            engine=engine,
            compressed=compressed
        )

    @classmethod
    def _assemble_batch(cls, batch_responses: List[BatchQueryResponse]) -> Parser:
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
                if initial_payload.startswith(cls.SIMPLE_HEADER):
                    has_mtu = False
                elif initial_payload[2:6] == cls.SIMPLE_HEADER:
                    has_mtu = True
                elif len(initial_payload) >= 1 and ResponseType(initial_payload[0]) is not ResponseType.Unknown:
                    has_mtu = False
                elif len(initial_payload) >= 3 and ResponseType(initial_payload[2]) is not ResponseType.Unknown:
                    has_mtu = True

            if has_mtu:
                for response in batch_responses:
                    if initial_response.compressed and response.packet_number == 0:
                        continue  # already handled the first compressed packet above

                    response.payload = response.payload[2:]

        parser = Parser(b"".join([response.payload for response in batch_responses]))

        if initial_response.compressed:
            try:
                parser.data = bz2.decompress(parser.data)
            except (OSError, EOFError) as e:
                raise InvalidResponse(f"Failed to decompress bzip payload: {e}") from e

        if parser.data.startswith(cls.SIMPLE_HEADER):
            parser.read_long()

        return parser

    @staticmethod
    def _build_request(request_type: RequestType, body: str, challenge: int) -> bytes:
        return struct.pack(f"<lB{len(body)}sl", -1, request_type.value, body.encode(), challenge)

    @staticmethod
    def _parse_info_response(response: QueryResponse) -> Union[SourceInfo, GoldSourceInfo]:
        if response.type is ResponseType.InfoSource:
            return Parser.parse_source_info(response.payload)
        return Parser.parse_goldsource_info(response.payload)

