from typing import cast

from .. import shared
from ..core import WorkManager
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited


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
