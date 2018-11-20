import os
from .shared import version
from .helper import loadMan, printHead
from .core import manager
from .ui import SwitchState, console
from . import ReturnCode, shared


def assertInited()->bool:
    if shared.man == None:
        console.error("Not have any ecr directory")
        return False
    return True


def init(args):
    manager.initialize(shared.cwd)
    loadMan()
    printHead()
    return ReturnCode.OK if shared.man != None else ReturnCode.UNLOADED


def now(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.currentFile = args.path
    return ReturnCode.OK


def new(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.newCode(args.filename)
    shared.man.currentFile = args.filename
    return ReturnCode.OK


def run(args):
    if not assertInited():
        return ReturnCode.UNLOADED

    if args.file == None and shared.man.currentFile == None:
        console.write("Please set file first")
        return ReturnCode.ERROR

    result = False

    result = shared.man.execute(io=args.io, file=args.file)

    if not result:
        console.error("Running Failed")
        return ReturnCode.RUNERR
    return ReturnCode.OK


def clean(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    shared.man.clean()
    return ReturnCode.OK


def shutdown(args):
    exit(0)


def pwd(args):
    console.write(shared.cwd)
    return ReturnCode.OK


def getVersion(args):
    console.write("edl-cr", version)
    return ReturnCode.OK


def cd(args):
    if not os.path.exists(args.path):
        console.error("No this directory")
        return ReturnCode.ERROR
    os.chdir(args.path)
    shared.cwd = os.getcwd()
    loadMan()
    printHead()
    return ReturnCode.OK


def clear(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    if console.confirm("Do you want to clear ALL?", [SwitchState.OK, SwitchState.Cancel]) == SwitchState.OK:
        manager.clear(shared.man.workingDirectory)
        shared.man = None
    return ReturnCode.OK
