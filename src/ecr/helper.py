import re
from .core import manager
from .ui import color, console
from . import shared


def loadMan():
    try:
        shared.man = manager.load(shared.cwd)
    except:
        shared.man = None


def printHead():
    assert(shared.man is None or shared.man.state !=
           manager.WorkManagerState.Empty)
    if shared.man is None:
        console.write("ECR", end=" ")
    elif shared.man.state == manager.WorkManagerState.Loaded:
        console.write(color.useGreen("ECR"), end=" ")
    elif shared.man.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(shared.cwd)


varFormatRE = re.compile(r'\$(?P<name>[a-zA-Z_]\w*)')


def bashVarToPythonVar(m):
    s = m.groupdict()
    return "{" + s["name"] + "}"


def formatWithVars(oristr, var):
    try:
        tmp = {k: v() for k, v in var.items()}
        oristr = varFormatRE.sub(bashVarToPythonVar, oristr)
        return oristr.format(**tmp)
    except:
        return oristr
