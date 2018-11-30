import re
from typing import cast, Optional, Dict
from .core import manager, WorkManager
from .ui import color
from . import shared, ui


def loadMan()->None:
    try:
        shared.setManager(manager.load(cast(str, shared.getCwd())))
        man = shared.getManager()
        if man and man.eVersion != shared.getVersion():
            ui.getConsole().warning(
                f"The config's version ({man.eVersion}) is not for current ecr ({shared.getVersion()}).")
    except:
        shared.setManager(None)


def printHead() -> None:
    man = shared.getManager()
    assert not man or man.state != manager.WorkManagerState.Empty
    tman: WorkManager = cast(WorkManager, man)
    console = ui.getConsole()
    if not man:
        console.write("ECR", end=" ")
    elif tman.state == manager.WorkManagerState.Loaded:
        console.write(color.useGreen("ECR"), end=" ")
    elif tman.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(shared.getCwd())


varFormatRE = re.compile(r'\$(?P<name>[a-zA-Z_]\w*)')


def bashVarToPythonVar(m)->str:
    s = m.groupdict()
    return "'{" + s["name"] + "}'"


def formatWithVars(oristr: str, var: Dict[str, Optional[str]])->str:
    try:
        oristr = varFormatRE.sub(bashVarToPythonVar, oristr)
        return oristr.format(**var)
    except:
        return oristr
