import os
import time
from typing import cast
from argparse import Namespace
from watchdog.events import FileSystemEventHandler
from .helper import loadMan, printHead
from .core import manager, WorkManager
from .ui import SwitchState, color
from . import ReturnCode, shared, ui

__all__ = ["init", "new", "now", "pwd", "cd", "clear",
           "getVersion", "shutdown", "run", "clean", "cls", "edit", "debug"]
cmds = ["init", "new", "now", "pwd", "cd", "clear",
        "version", "run", "clean", "cls", "exit", "edit", "debug"]


def printFileModify(file: str)->None:
    ui.console.write(color.useYellow("M"), file)


def printFileCreate(file: str)->None:
    ui.console.write(color.useGreen("+"), file)


def printFileDelete(file: str)->None:
    ui.console.write(color.useRed("-"), file)


def assertInited()->bool:
    if shared.man is None:
        ui.console.error("Not have any ecr directory")
        return False
    return True


def init(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    manager.initialize(cast(str, shared.cwd))
    loadMan()
    printHead()
    return ReturnCode.OK if shared.man else ReturnCode.UNLOADED


def clear(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    if ui.console.confirm("Do you want to clear ALL?",
                          [SwitchState.OK, SwitchState.Cancel]) == SwitchState.OK:
        manager.clear(tman.workingDirectory)
        shared.man = None
    return ReturnCode.OK


def now(args: Namespace)->ReturnCode:
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    tman.currentFile = args.file
    return ReturnCode.OK


def new(args: Namespace)->ReturnCode:
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    file = args.file
    if file is None:
        file = tman.currentFile
    result = tman.newCode(file)
    if result:
        tman.currentFile = file
        printFileCreate(file)
        if args.edit:
            return edit(Namespace(file=file, now=False))
        return ReturnCode.OK
    else:
        ui.console.error(f"Can't create file {file}")
        return ReturnCode.ERROR


def edit(args: Namespace)->ReturnCode:
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    if args.file is None and tman.currentFile is None:
        ui.console.write("Please set file first")
        return ReturnCode.ERROR
    file = args.file
    if file is None:
        file = tman.currentFile
    result = tman.edit(file)
    if result:
        printFileModify(file)
        if args.now:
            return now(Namespace(file=file))
        return ReturnCode.OK
    else:
        ui.console.error(f"Editing file error {file}")
        return ReturnCode.ERROR
    return ReturnCode.OK


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
        if os.path.split(event.src_path)[-1] == self.file:
            self.state = not self.state
            if self.state:  # one modify raise two event
                self.func()


def run(args: Namespace)->ReturnCode:
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    if args.file is None and tman.currentFile is None:
        ui.console.write("Please set file first")
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

    while tman.runner is None:
        pass

    while tman.runner != None and tman.runner.isRunning:
        cmd = ui.console.read()
        if cmd == "kill":
            ui.console.write(cmd)
            tman.runner.terminate()
            new_thread.join()
        elif tman.runner.canInput:
            tman.runner.input(cmd)

    result = ret[0] if len(ret) > 0 else False"""

    if not args.watch:
        result = tman.execute(io=args.io, file=args.file)

        if not result:
            ui.console.error("Running failed")
            return ReturnCode.RUNERR
        return ReturnCode.OK
    else:
        def func():
            ui.console.clear()
            ui.console.info(f"Watching", end=" ")
            printFileModify(file)
            result = tman.execute(io=args.io, file=args.file)
            if not result:
                ui.console.error("Running failed")

        from watchdog.observers import Observer
        file = args.file if args.file else tman.currentFile
        path = tman.workingDirectory
        ui.console.info(f"Watching {file} (press ctrl+c to end)")
        event_handler = RunWatchEventHandler(file, func)
        observer = Observer()
        observer.schedule(event_handler, path, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            ui.console.info("Watching end.")
        observer.join()
        return ReturnCode.OK


def clean(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    if not assertInited():
        return ReturnCode.UNLOADED
    tman: WorkManager = cast(WorkManager, shared.man)
    tman.clean(rmHandler=printFileDelete)
    return ReturnCode.OK


def shutdown(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    return ReturnCode.EXIT


def pwd(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    ui.console.write(shared.cwd)
    return ReturnCode.OK


def getVersion(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    ui.console.write("edl-cr", shared.version)
    ui.console.write("Copyright (C) eXceediDeal")
    ui.console.write(
        "License Apache-2.0, Source https://github.com/eXceediDeaL/edl-coderunner")
    return ReturnCode.OK


def cd(args: Namespace)->ReturnCode:
    if not os.path.exists(args.path):
        ui.console.error("No this directory")
        return ReturnCode.ERROR
    os.chdir(args.path)
    shared.cwd = os.getcwd()
    loadMan()
    printHead()
    return ReturnCode.OK


def cls(args: Namespace)->ReturnCode:  # pylint: disable=W0613
    ui.console.clear()
    return ReturnCode.OK


def debug(args: Namespace) -> ReturnCode:
    import json
    ui.console.write(json.dumps(
        cast(WorkManager, shared.man).__dict__, default=lambda x: str(x), indent=4))

    return ReturnCode.OK
