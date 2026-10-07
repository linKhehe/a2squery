import bz2
import struct
from dataclasses import dataclass
from typing import List

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

    payload: bytes
    packet_number: int
    total_packets: int
    engine: BatchResponseEngine
    compressed: bool


class BaseA2SQuery:

    def __init__(self, host: str, port: int = 27015, timeout: float = 10, challenge_retries: int = 3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.challenge_retries = challenge_retries

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

    @staticmethod
    def _assemble_batch(batch_responses: List[BatchQueryResponse]) -> Parser:
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
    
    @staticmethod
    def _build_request(request_type: RequestType, body: str, challenge: int):
        return struct.pack(f"<lB{len(body)}sl", -1, request_type.value, body.encode(), challenge)
