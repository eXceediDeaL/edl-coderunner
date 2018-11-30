from typing import cast
from ..ui import SwitchState
from ..ui.command import ReturnCode, Command, Namespace
from ..core import manager, WorkManager
from .. import shared, ui
from .helper import assertInited


class ClearCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if console.confirm("Do you want to clear ALL?",
                           [SwitchState.OK, SwitchState.Cancel]) == SwitchState.OK:
            manager.clear(tman.workingDirectory)
            shared.setManager(None)
        return ReturnCode.OK

    def __init__(self):
        super().__init__("clear", help="Clear ECR data", func=ClearCommand.default)
