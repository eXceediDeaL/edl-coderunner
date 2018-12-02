from .. import ui
from ..ui.command import Command, Namespace, ReturnCode


class ClsCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        ui.getConsole().clear()
        return ReturnCode.OK

    def __init__(self):
        super().__init__("cls", help="Clear console", func=ClsCommand.default)
