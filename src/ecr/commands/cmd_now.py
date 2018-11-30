from typing import cast
from ..ui import command, SwitchState
from ..ui.command import ReturnCode, Command, Namespace
from ..core import manager, WorkManager, WorkItem
from ..helper import loadMan, printHead
from .. import shared, ui
from .helper import assertInited, printFileModify


class NowCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        tman.setCurrent(args.file, args.dir)
        return ReturnCode.OK

    def __init__(self):
        super().__init__("now", help="Change current file", func=NowCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("file", nargs="?", default=None, type=str,
                             help="Set current file (clear for none)")
        cmd.add_argument("-d", "--dir", action="store_true",
                             default=False, help="As directory")
        return cmd
