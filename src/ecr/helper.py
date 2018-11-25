import re
from typing import cast
from .core import manager, WorkManager
from .core.types import VariableMapping
from .ui import color, console
from . import shared


def loadMan()->None:
    try:
        shared.man = manager.load(cast(str, shared.cwd))
    except:
        shared.man = None


def printHead()->None:
    assert not shared.man or shared.man.state != manager.WorkManagerState.Empty
    tman: WorkManager = cast(WorkManager, shared.man)
    if not shared.man:
        console.write("ECR", end=" ")
    elif tman.state == manager.WorkManagerState.Loaded:
        console.write(color.useGreen("ECR"), end=" ")
    elif tman.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(shared.cwd)


varFormatRE = re.compile(r'\$(?P<name>[a-zA-Z_]\w*)')


def bashVarToPythonVar(m)->str:
    s = m.groupdict()
    return "{" + s["name"] + "}"


def formatWithVars(oristr: str, var: VariableMapping)->str:
    try:
        tmp = {k: v() for k, v in var.items()}
        oristr = varFormatRE.sub(bashVarToPythonVar, oristr)
        return oristr.format(**tmp)
    except:
        return oristr
