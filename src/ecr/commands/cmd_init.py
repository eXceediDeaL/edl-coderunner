from typing import cast
from ..ui.command import ReturnCode, Command, Namespace
from ..core import manager
from ..helper import loadMan, printHead
from .. import shared


class InitCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        manager.initialize(cast(str, shared.getCwd()))
        loadMan()
        printHead()
        return ReturnCode.OK if shared.getManager() else ReturnCode.UNLOADED

    def __init__(self):
        super().__init__("init", help="Initialize ECR data", func=InitCommand.default)
