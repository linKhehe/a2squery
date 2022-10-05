from enum import Enum

__all__ = (
    "RequestType", "ResponseType", "ResponseFormat",
    "ServerType", "Environment"
)


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


class ResponseFormat(Enum):

    Simple = -1
    Batch = -2


class ServerType(Enum):

    Dedicated = "d"
    NonDedicated = "l"
    SourceTV = "p"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value: str):
        if value.lower() != value:
            return cls(value.lower())
        return cls.Unknown


class Environment(Enum):

    Linux = "l"
    Windows = "w"
    Mac = "m"
    Unknown = "unknown"

    @classmethod
    def _missing_(cls, value: str):
        if value == "o":
            return cls.Mac
        if value.lower() != value:
            return cls(value.lower())
        return cls.Unknown
