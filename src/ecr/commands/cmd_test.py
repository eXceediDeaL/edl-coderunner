import time
from typing import cast

from .. import shared, ui
from ..core import WorkItem, WorkItemType, WorkManager, defaultData
from ..ui.command import Command, Namespace, ReturnCode
from .cmd_run import RunWatchEventHandler, RunCommand
from .helper import assertInited, getItem, printFileModify


class TestCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if not args.file and not tman.currentFile:
            console.write("Please set file first")
            return ReturnCode.ERROR

        if not args.watch:
            item, file = getItem(tman, args)
            if args.re:
                runResult = RunCommand.default(
                    Namespace(io=defaultData.CIO_FIFO, file=args.file, dir=args.dir, watch=False))
                if runResult != ReturnCode.OK:
                    return runResult

            result = tman.judge(item=item, judger=args.judger)

            if not result:
                console.error("Judging failed")
                return ReturnCode.JUDGEERR
            else:
                console.ok("Judging passed")
                return ReturnCode.OK
        else:
            file = args.file if args.file else cast(
                WorkItem, tman.currentFile).name

            def func():
                item, file = getItem(tman, args)
                console.clear()
                console.info(f"Watching", end=" ")
                printFileModify(file)
                result = tman.judge(reexecute=args.re,
                                    item=item, judger=args.judger)
                if not result:
                    console.error("Judging failed")
                    return ReturnCode.JUDGEERR
                else:
                    console.ok("Judging passed")
                    return ReturnCode.OK

            from watchdog.observers import Observer
            console.info(f"Watching {file} (press ctrl+c to end)")
            path = tman.workingDirectory if item.type == WorkItemType.File else item.path
            event_handler = RunWatchEventHandler(
                file if item.type == WorkItemType.File else None, func)
            observer = Observer()
            observer.schedule(event_handler, path, recursive=False)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                console.info("Watching end.")
            observer.join()
            return ReturnCode.OK

    def __init__(self):
        super().__init__("test", help="Test output data", func=TestCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument(
            "file", nargs="?", default=None, help="File name (only for this command)")
        cmd.add_argument("-j", "--judger",
                         default=None, help="Judger")
        cmd.add_argument("-w", "--watch", action="store_true",
                         default=False, help="Watch the file and judge auto till Ctrl-C")
        cmd.add_argument("-r", "--re", action="store_true",
                         default=False, help="Re-execute before judge")
        cmd.add_argument("-d", "--dir", action="store_true",
                         default=False, help="As directory")
        return cmd
