import os
import time
from typing import cast

from watchdog.events import FileSystemEventHandler

from .. import shared, ui
from ..core import WorkItem, WorkItemType, WorkManager
from ..core.defaultData import CIO_Types, CIO_SISO
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited, getItem, printFileModify


class RunWatchEventHandler(FileSystemEventHandler):
    def __init__(self, file, func):
        self.func = func
        self.file = file
        self.state = False

    def on_moved(self, event):  # pylint: disable=W0235
        super().on_moved(event)
        # self.func()

        # what = 'directory' if event.is_directory else 'file'
        # logging.info("Moved %s: from %s to %s", what, event.src_path,event.dest_path)

    def on_created(self, event):  # pylint: disable=W0235
        super().on_created(event)

    def on_deleted(self, event):  # pylint: disable=W0235
        super().on_deleted(event)
        # self.func()

    def on_modified(self, event):
        super().on_modified(event)
        if not self.file or os.path.split(event.src_path)[-1] == self.file:
            self.state = not self.state
            if self.state:  # one modify raise two event
                self.func()


class RunCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if not args.file and not tman.currentFile:
            console.write("Please set file first")
            return ReturnCode.ERROR

        # pylint: disable=W0105
        """def func(ret): # for async
            try:
                ret.append(tman.execute(io=args.io, file=args.file))
            except:
                ret.append(False)

        ret = []

        new_thread = threading.Thread(target=func, args=(ret,))
        new_thread.start()

        while not tman.runner:
            pass

        while tman.runner != None and tman.runner.isRunning:
            cmd = ui.console.read()
            if cmd == "kill":
                ui.console.write(cmd)
                tman.runner.terminate()
                new_thread.join()
            elif tman.runner.canInput:
                tman.runner.input(cmd)

        result = ret[0] if len(ret) > 0 else False """

        if not args.watch:
            item, file = getItem(tman, args)
            if item.type == WorkItemType.Directory:
                args.io = CIO_SISO
            result = tman.execute(io=args.io, item=item)

            if not result:
                console.error("Running failed")
                return ReturnCode.RUNERR
            return ReturnCode.OK
        else:
            file = args.file if args.file else cast(
                WorkItem, tman.currentFile).name

            def func():
                item, file = getItem(tman, args)
                if item.type == WorkItemType.Directory:
                    args.io = CIO_SISO
                console.clear()
                console.info(f"Watching", end=" ")
                printFileModify(file)
                result = tman.execute(io=args.io, item=item)
                if not result:
                    console.error("Running failed")

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
        super().__init__("run", help="Run code file", func=RunCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-io", "--io", choices=CIO_Types,
                         default=None, help="Change input and output")
        cmd.add_argument(
            "file", nargs="?", default=None, help="File name (only for this command)")
        cmd.add_argument("-w", "--watch", action="store_true",
                         default=False, help="Watch the file and run auto till Ctrl-C")
        cmd.add_argument("-d", "--dir", action="store_true",
                         default=False, help="As directory")
        return cmd
