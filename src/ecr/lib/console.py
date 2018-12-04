from ..ui import color

from ..ui import getConsole as _internal_gc


def write(*values, **kwargs) -> None:  # pylint: disable=R0201
    _internal_gc().write(*values, **kwargs)


def info(message, end: str = "\n")->None:
    write(color.useCyan(message), end=end)


def warning(message, end: str = "\n")->None:
    write(color.useYellow(message), end=end)


def error(message, end: str = "\n")->None:
    write(color.useRed(message), end=end)


def ok(message, end: str = "\n")->None:
    write(color.useGreen(message), end=end)
