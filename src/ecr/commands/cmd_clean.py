from typing import cast
from ..ui.command import ReturnCode, Command, Namespace
from ..core import WorkManager
from .. import shared
from .helper import assertInited, printFileDelete


class CleanCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        tman.clean(rmHandler=printFileDelete)
        return ReturnCode.OK

    def __init__(self):
        super().__init__("clean", help="Clean temp files", func=CleanCommand.default)
