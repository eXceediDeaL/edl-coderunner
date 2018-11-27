import re
from typing import cast
from .core import manager, WorkManager
from .core.types import VariableMapping
from .ui import color
from . import shared, ui


def loadMan()->None:
    try:
        shared.man = manager.load(cast(str, shared.cwd))
        if shared.man and shared.man.eVersion != shared.version:
            ui.console.warning(
                f"The config's version ({shared.man.eVersion}) is not for current ecr ({shared.version}).")
    except:
        shared.man = None


def printHead()->None:
    assert not shared.man or shared.man.state != manager.WorkManagerState.Empty
    tman: WorkManager = cast(WorkManager, shared.man)
    if not shared.man:
        ui.console.write("ECR", end=" ")
    elif tman.state == manager.WorkManagerState.Loaded:
        ui.console.write(color.useGreen("ECR"), end=" ")
    elif tman.state == manager.WorkManagerState.LoadFailed:
        ui.console.write(color.useRed("ECR"), end=" ")
    ui.console.write(shared.cwd)


varFormatRE = re.compile(r'\$(?P<name>[a-zA-Z_]\w*)')


def bashVarToPythonVar(m)->str:
    s = m.groupdict()
    return "'{" + s["name"] + "}'"


def formatWithVars(oristr: str, var: VariableMapping)->str:
    try:
        tmp = {k: v() for k, v in var.items()}
        oristr = varFormatRE.sub(bashVarToPythonVar, oristr)
        return oristr.format(**tmp)
    except:
        return oristr
