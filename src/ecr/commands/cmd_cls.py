from typing import cast
from ..ui import command, SwitchState
from ..ui.command import ReturnCode, Command, Namespace
from ..core import manager, WorkManager
from ..helper import loadMan, printHead
from .. import shared, ui
from .helper import assertInited


class ClsCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        ui.getConsole().clear()
        return ReturnCode.OK

    def __init__(self):
        super().__init__("cls", help="Clear console", func=ClsCommand.default)
