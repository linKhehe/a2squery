from typing import Any
from enum import Enum

__all__ = (
    "BatchResponseEngine","RequestType", "ResponseType", "ResponseFormat",
    "ServerType", "Environment"
)


class BatchResponseEngine(Enum):
    GoldSource = 0
    Source = 1


class RequestType(Enum):

    Info = 0x54
    Player = 0x55
    Rules = 0x56


class ResponseType(Enum):

    Challenge = 0x41
    InfoSource = 0x49
    InfoGoldSource = 0x6D
    Player = 0x44
    Rules = 0x45
    Unknown = 0xFF

    @classmethod
    def _missing_(cls, value: Any):
        return cls.Unknown


class ResponseFormat(Enum):

    Simple = -1
    Batch = -2


class ServerType(Enum):

    Dedicated = "d"
    NonDedicated = "l"
    HLTV = "p"
    SourceTV = "P"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value: object):
        if type(value) is str:
            if value.lower() != value:
                return cls(value.lower())
        return cls.Unknown


class Environment(Enum):

    Linux = "l"
    Windows = "w"
    Mac = "m"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value: object):
        if type(value) is str:
            if value == "o":
                return cls.Mac
            if value.lower() != value:
                return cls(value.lower())
        return cls.Unknown
