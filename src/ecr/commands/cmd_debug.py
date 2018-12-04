from typing import cast

from .. import log, shared, ui
from ..core import WorkManager
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited


class DebugCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        if args.out:
            out = open(args.out, "w")
        else:
            out = console
        try:
            if args.ecr:
                if not assertInited():
                    return ReturnCode.UNLOADED
                console.info("Config loaded for current directory")
                import json
                out.write(json.dumps(
                    cast(WorkManager, shared.getManager()).__dict__, default=str, indent=4))
            if args.current:
                if not assertInited():
                    return ReturnCode.UNLOADED
                console.info("Current work-item")
                import json
                witem = cast(WorkManager, shared.getManager()).currentFile
                if witem:
                    out.write(json.dumps(
                        witem.__dict__, default=str, indent=4))
                else:
                    out.write("None")
            if args.os:
                console.info("Platform information")
                import platform
                lst = []
                lst.append(
                    " ".join(["Machine:", platform.machine(), platform.processor()]))
                lst.append(
                    " ".join(["Platform:", platform.platform()]))
                lst.append(
                    " ".join(["OS:", platform.system(),
                              platform.version()] + list(platform.architecture())))
                lst.append(
                    " ".join(["Python:", platform.python_version(),
                              platform.python_implementation()]))
                if out == console:
                    for msg in lst:
                        out.write(msg)
                else:
                    out.writelines([x+"\n" for x in lst])
            if args.log:
                console.info("Log")
                if out == console:
                    for msg in shared.getLogData():
                        out.write(log.colored(msg))
                else:
                    out.writelines([x+"\n" for x in shared.getLogData()])
        except:
            msg = "Debug log output failed"
            console.error(msg)
            log.errorWithException(msg)
        finally:
            if out != console:
                out.close()
        return ReturnCode.OK

    def __init__(self):
        super().__init__("debug", help="Debug for developing", func=DebugCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-e", "--ecr", action="store_true",
                         default=False, help="Show ECR data")
        cmd.add_argument("-c", "--current", action="store_true",
                         default=False, help="Show current work-item")
        cmd.add_argument("-os", "--os", action="store_true",
                         default=False, help="Show OS data")
        cmd.add_argument("-l", "--log", action="store_true",
                         default=False, help="Show logs")
        cmd.add_argument("-o", "--out", type=str, help="Output to file")
        return cmd
