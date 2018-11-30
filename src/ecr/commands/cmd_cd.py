import os
from ..ui.command import ReturnCode, Command, Namespace
from ..helper import loadMan, printHead
from .. import shared, ui


class CdCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        if not os.path.exists(args.path):
            console.error("No this directory")
            return ReturnCode.ERROR
        os.chdir(args.path)
        shared.setCwd(os.getcwd())
        loadMan()
        printHead()
        return ReturnCode.OK

    def __init__(self):
        super().__init__("cd", help="Change working directory", func=CdCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("path")
        return cmd
