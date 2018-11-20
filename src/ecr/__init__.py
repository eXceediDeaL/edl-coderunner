import enum
from . import shared

__version__ = shared.version

class ReturnCode(enum.Enum):
    OK = 0
    ERROR = -1
    UNLOADED = 1
    RUNERR = 2
    EXIT = 3
