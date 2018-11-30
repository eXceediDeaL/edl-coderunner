from typing import cast
from ..ui import command, SwitchState
from ..ui.command import ReturnCode, Command, Namespace
from ..core import manager, WorkManager
from ..helper import loadMan, printHead
from .. import shared, ui
from .helper import assertInited


class ExitCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        return ReturnCode.EXIT

    def __init__(self):
        super().__init__("exit", help="Exit", func=ExitCommand.default)
