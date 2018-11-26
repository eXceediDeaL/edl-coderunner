import enum
from . import shared

__version__ = shared.version


class ReturnCode(enum.Enum):
    OK: int = 0
    ERROR: int = -1
    UNLOADED: int = 1
    RUNERR: int = 2
    JUDGEERR: int = 3
    EXIT: int = 4
