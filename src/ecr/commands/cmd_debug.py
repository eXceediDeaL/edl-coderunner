from typing import cast

from .. import log, shared, ui
from ..core import WorkManager
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited


class DebugCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        if args.config:
            if not assertInited():
                return ReturnCode.UNLOADED
            console.info("Config loaded for current directory")
            import json
            console.write(json.dumps(
                cast(WorkManager, shared.getManager()).__dict__, default=str, indent=4))
        if args.os:
            console.info("Platform information")
            import platform
            console.write("Machine:", platform.machine(), platform.processor())
            console.write("Platform:", platform.platform())
            console.write("OS:", platform.system(),
                          platform.version(), *(platform.architecture()))
            console.write("Python:", platform.python_version(),
                          platform.python_implementation())
        if args.log:
            console.info("Log")
            for msg in shared.getLogData():
                console.write(log.colored(msg))
        return ReturnCode.OK

    def __init__(self):
        super().__init__("debug", help="Debug for developing", func=DebugCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-c", "--config", action="store_true",
                         default=False, help="Show config data")
        cmd.add_argument("-os", "--os", action="store_true",
                         default=False, help="Show OS data")
        cmd.add_argument("-l", "--log", action="store_true",
                         default=False, help="Show logs")
        return cmd
