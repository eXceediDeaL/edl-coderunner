from .cli import CLI, SwitchState
from .helper import PathCompleter

_console: CLI = CLI()


def getConsole() -> CLI:
    return _console


def setConsole(cli: CLI) -> None:
    global _console
    _console = cli
