from typing import cast

from .. import log, shared, ui
from ..core import manager, globalData
from ..helper import loadMan, printHead
from ..ui.command import Command, Namespace, ReturnCode


class InitCommand(Command):
    @staticmethod
    def default(args: Namespace) -> ReturnCode:  # pylint: disable=W0613
        if args.globals:
            try:
                globalData.initialize()
                return ReturnCode.OK
            except:
                msg = "Initializing global failed."
                log.errorWithException(msg)
                ui.getConsole().error(msg)
                return ReturnCode.ERROR
        else:
            manager.initialize(cast(str, shared.getCwd()))
            loadMan()
            printHead()
            return ReturnCode.OK if shared.getManager() else ReturnCode.UNLOADED

    def __init__(self):
        super().__init__("init", help="Initialize ECR data", func=InitCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-g", "--globals", action="store_true",
                         default=False, help="Initialize global data")
        return cmd
