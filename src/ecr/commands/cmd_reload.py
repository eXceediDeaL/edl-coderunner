from .. import shared
from ..helper import loadMan, printHead
from ..ui.command import Command, Namespace, ReturnCode


class ReloadCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        loadMan()
        printHead()
        return ReturnCode.OK if shared.getManager() else ReturnCode.UNLOADED

    def __init__(self):
        super().__init__("reload", help="Reload ECR data", func=ReloadCommand.default)
