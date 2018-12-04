from typing import cast

from .. import core, shared, ui
from ..core import WorkManager, WorkManagerState, manager
from ..ui import SwitchState
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited
from . import cmd_reload


class ClearCommand(Command):
    @staticmethod
    def default(args: Namespace) -> ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        tman: WorkManager = cast(WorkManager, shared.getManager())

        if args.globals:
            if console.confirm("Do you want to clear ALL for global?",
                               [SwitchState.Yes, SwitchState.No]) == SwitchState.Yes:
                manager.clear(core.path.getGlobalBasePath())
                if tman and tman.state == WorkManagerState.LoadedFromGlobal:
                    cmd_reload.ReloadCommand.default(Namespace())
        else:
            if not assertInited():
                return ReturnCode.UNLOADED

            if console.confirm("Do you want to clear ALL?",
                               [SwitchState.Yes, SwitchState.No]) == SwitchState.Yes:
                manager.clear(tman.workingDirectory)
                cmd_reload.ReloadCommand.default(Namespace())

        return ReturnCode.OK

    def __init__(self):
        super().__init__("clear", help="Clear ECR data", func=ClearCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-g", "--globals", action="store_true",
                         default=False, help="Clear global data")
        return cmd
