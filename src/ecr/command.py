import os
import time
from argparse import Namespace
from watchdog.events import FileSystemEventHandler
from .helper import loadMan, printHead
from .core import manager
from .ui import SwitchState, color
from . import ReturnCode, shared, ui

__all__ = ["init", "new", "now", "pwd", "cd", "clear",
           "getVersion", "shutdown", "run", "clean", "cls", "edit"]
cmds = ["init", "new", "now", "pwd", "cd", "clear",
        "version", "run", "clean", "cls", "exit", "edit"]


def printFileModify(file):
    ui.console.write(color.useYellow("M"), file)


def printFileCreate(file):
    ui.console.write(color.useGreen("+"), file)


def printFileDelete(file):
    ui.console.write(color.useRed("-"), file)


def assertInited()->bool:
    if shared.man is None:
        ui.console.error("Not have any ecr directory")
        return False
    return True


def init(args): # pylint: disable=W0613
    manager.initialize(shared.cwd)
    loadMan()
    printHead()
    return ReturnCode.OK if shared.man else ReturnCode.UNLOADED


def clear(args): # pylint: disable=W0613
    if not assertInited():
        return ReturnCode.UNLOADED
    if ui.console.confirm("Do you want to clear ALL?", \
        [SwitchState.OK, SwitchState.Cancel]) == SwitchState.OK:
        manager.clear(shared.man.workingDirectory)
        shared.man = None
    return ReturnCode.OK


def now(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.currentFile = args.file
    return ReturnCode.OK


def new(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    file = args.file
    if file is None:
        file = shared.man.currentFile
    result = shared.man.newCode(file)
    if result:
        shared.man.currentFile = file
        printFileCreate(file)
        if args.edit:
            return edit(Namespace(file=file, now=False))
        return ReturnCode.OK
    else:
        ui.console.error(f"Can't create file {file}")
        return ReturnCode.ERROR


def edit(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    if args.file is None and shared.man.currentFile is None:
        ui.console.write("Please set file first")
        return ReturnCode.ERROR
    file = args.file
    if file is None:
        file = shared.man.currentFile
    result = shared.man.edit(file)
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

    def on_moved(self, event): # pylint: disable=W0235
        super().on_moved(event)
        # self.func()

        # what = 'directory' if event.is_directory else 'file'
        # logging.info("Moved %s: from %s to %s", what, event.src_path,event.dest_path)

    def on_created(self, event): # pylint: disable=W0235
        super().on_created(event)

    def on_deleted(self, event): # pylint: disable=W0235
        super().on_deleted(event)
        # self.func()

    def on_modified(self, event):
        super().on_modified(event)
        if os.path.split(event.src_path)[-1] == self.file:
            self.state = not self.state
            if self.state:  # one modify raise two event
                self.func()


def run(args):
    if not assertInited():
        return ReturnCode.UNLOADED

    if args.file is None and shared.man.currentFile is None:
        ui.console.write("Please set file first")
        return ReturnCode.ERROR

    # pylint: disable=W0105
    """def func(ret): # for async
        try:
            ret.append(shared.man.execute(io=args.io, file=args.file))
        except:
            ret.append(False)

    ret = []

    new_thread = threading.Thread(target=func, args=(ret,))
    new_thread.start()

    while shared.man.runner is None:
        pass

    while shared.man.runner != None and shared.man.runner.isRunning:
        cmd = ui.console.read()
        if cmd == "kill":
            ui.console.write(cmd)
            shared.man.runner.terminate()
            new_thread.join()
        elif shared.man.runner.canInput:
            shared.man.runner.input(cmd)

    result = ret[0] if len(ret) > 0 else False"""

    if not args.watch:
        result = shared.man.execute(io=args.io, file=args.file)

        if not result:
            ui.console.error("Running failed")
            return ReturnCode.RUNERR
        return ReturnCode.OK
    else:
        def func():
            ui.console.clear()
            ui.console.info(f"Watching", end=" ")
            printFileModify(file)
            result = shared.man.execute(io=args.io, file=args.file)
            if not result:
                ui.console.error("Running failed")

        from watchdog.observers import Observer
        file = args.file if args.file else shared.man.currentFile
        path = shared.man.workingDirectory
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


def clean(args):  # pylint: disable=W0613
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.clean(rmHandler=printFileDelete)
    return ReturnCode.OK


def shutdown(args):  # pylint: disable=W0613
    return ReturnCode.EXIT


def pwd(args):  # pylint: disable=W0613
    ui.console.write(shared.cwd)
    return ReturnCode.OK


def getVersion(args):  # pylint: disable=W0613
    ui.console.write("edl-cr", shared.version)
    ui.console.write("Copyright (C) eXceediDeal")
    ui.console.write(
        "License Apache-2.0, Source https://github.com/eXceediDeaL/edl-coderunner")
    return ReturnCode.OK


def cd(args):
    if not os.path.exists(args.path):
        ui.console.error("No this directory")
        return ReturnCode.ERROR
    os.chdir(args.path)
    shared.cwd = os.getcwd()
    loadMan()
    printHead()
    return ReturnCode.OK


def cls(args):  # pylint: disable=W0613
    ui.console.clear()
    return ReturnCode.OK
