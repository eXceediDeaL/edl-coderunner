import os
from .shared import version
from .core import manager
from .ui import color, console
from . import ReturnCode, shared


def loadMan():
    try:
        shared.man = manager.load(shared.cwd)
    except:
        shared.man = None


def printHead():
    assert(shared.man == None or shared.man.state != manager.WorkManagerState.Empty)
    if shared.man == None:
        console.write("ECR", end=" ")
    elif shared.man.state == manager.WorkManagerState.Loaded:
        console.write(color.useGreen("ECR"), end=" ")
    elif shared.man.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(shared.cwd)
