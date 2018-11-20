import enum


class ReturnCode(enum.Enum):
    OK = 0
    ERROR = -1
    UNLOADED = 1
    RUNERR = 2
