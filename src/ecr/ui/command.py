from typing import Callable
import enum
from argparse import Namespace


class ReturnCode(enum.Enum):
    OK: int = 0
    ERROR: int = -1
    UNLOADED: int = 1
    RUNERR: int = 2
    JUDGEERR: int = 3
    EXIT: int = 4


class Command:
    def __init__(self, verb: str, help: str, func: Callable[[Namespace], ReturnCode]): # pylint: disable=W0622
        self.verb: str = verb
        self.help: str = help
        self.func: Callable[[Namespace], ReturnCode] = func

    def createParser(self, parsers):
        cmd = parsers.add_parser(self.verb, help=self.help)
        cmd.set_defaults(func=self.func)
        return cmd
