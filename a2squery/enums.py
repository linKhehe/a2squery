from typing import Any
from enum import Enum

__all__ = (
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


class _CaseInsensitiveStrEnum(Enum):

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str):
            lower = value.lower()
            if lower != value:
                return cls(lower)
        return getattr(cls, "Unknown")


class ResponseFormat(Enum):

    Simple = -1
    Batch = -2
    Unknown = 0

    @classmethod
    def _missing_(cls, value: object):
        return cls.Unknown


class ServerType(_CaseInsensitiveStrEnum):

    Dedicated = "d"
    NonDedicated = "l"
    SourceTV = "p"
    HLTV = "P"
    Unknown = "unknown"


class Environment(_CaseInsensitiveStrEnum):

    Linux = "l"
    Windows = "w"
    Mac = "m"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value: object):
        if isinstance(value, str) and value.lower() == "o":
            return cls.Mac
        return super()._missing_(value)

