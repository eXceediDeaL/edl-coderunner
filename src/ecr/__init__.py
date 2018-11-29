import enum
from . import core

__version__ = core.__version__


class ReturnCode(enum.Enum):
    OK: int = 0
    ERROR: int = -1
    UNLOADED: int = 1
    RUNERR: int = 2
    JUDGEERR: int = 3
    EXIT: int = 4
