__all__ = ["init", "new", "now", "pwd", "cd", "clear",
           "getVersion", "shutdown", "run", "clean", "cls", "edit"]
cmds = ["init", "new", "now", "pwd", "cd", "clear",
        "version", "run", "clean", "cls", "exit", "edit"]

import os
import click
import threading
import time
from argparse import Namespace
from .helper import loadMan, printHead
from .core import manager
from .ui import SwitchState, color
from . import ReturnCode, shared, ui


def assertInited()->bool:
    if shared.man == None:
        ui.console.error("Not have any ecr directory")
        return False
    return True


def init(args):
    manager.initialize(shared.cwd)
    loadMan()
    printHead()
    return ReturnCode.OK if shared.man != None else ReturnCode.UNLOADED


def clear(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    if ui.console.confirm("Do you want to clear ALL?", [SwitchState.OK, SwitchState.Cancel]) == SwitchState.OK:
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
    if file == None:
        file = shared.man.currentFile
    result = shared.man.newCode(file)
    if result:
        shared.man.currentFile = file
        ui.console.write(color.useGreen("+"), file)
        if args.edit:
            return edit(Namespace(file=file, now=False))
        return ReturnCode.OK
    else:
        ui.console.error(f"Can't create file {file}")
        return ReturnCode.ERROR


def edit(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    if args.file == None and shared.man.currentFile == None:
        ui.console.write("Please set file first")
        return ReturnCode.ERROR
    file = args.file
    if file == None:
        file = shared.man.currentFile
    result = shared.man.edit(file)
    if result:
        ui.console.write(color.useYellow("M"), file)
        if args.now:
            return now(Namespace(file=file))
        return ReturnCode.OK
    else:
        ui.console.error(f"Editing file error {file}")
        return ReturnCode.ERROR
    return ReturnCode.OK


def run(args):
    if not assertInited():
        return ReturnCode.UNLOADED

    if args.file == None and shared.man.currentFile == None:
        ui.console.write("Please set file first")
        return ReturnCode.ERROR

    """def func(ret): # for async
        try:
            ret.append(shared.man.execute(io=args.io, file=args.file))
        except:
            ret.append(False)

    ret = []

    new_thread = threading.Thread(target=func, args=(ret,))
    new_thread.start()

    while shared.man.runner == None:
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

    result = shared.man.execute(io=args.io, file=args.file)

    if not result:
        ui.console.error("Running failed")
        return ReturnCode.RUNERR
    return ReturnCode.OK


def clean(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.clean()
    return ReturnCode.OK


def shutdown(args):
    return ReturnCode.EXIT


def pwd(args):
    ui.console.write(shared.cwd)
    return ReturnCode.OK


def getVersion(args):
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


def cls(args):
    ui.console.clear()
    return ReturnCode.OK
