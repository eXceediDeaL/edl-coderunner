from .. import shared, ui
from ..ui.command import Command, Namespace, ReturnCode


class PwdCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        console.write(shared.getCwd())
        return ReturnCode.OK

    def __init__(self):
        super().__init__("pwd", help="Print working directory", func=PwdCommand.default)
