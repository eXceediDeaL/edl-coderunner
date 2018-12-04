import re
from typing import Dict, Optional, cast

from . import log, shared, ui
from .core import WorkManager, manager
from .ui import color


def loadMan()->None:
    try:
        wd = shared.getCwd()
        man, exp = manager.load(wd)
        if exp:
            raise exp
        else:
            shared.setManager(man)
            man = shared.getManager()
            if man and man.eVersion != shared.getVersion():
                msg = f"The config's version ({man.eVersion}) is not for current ecr ({shared.getVersion()})."
                log.warning(msg)
                ui.getConsole().warning(msg)
            else:
                log.debug("ECR data loaded.")
    except Exception as e:
        ui.getConsole().error(f"Loading failed: {e}")
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
    elif tman.state == manager.WorkManagerState.LoadedFromGlobal:
        console.write(color.useYellow("ECR"), end=" ")
    elif tman.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(shared.getCwd())


varFormatRE = re.compile(r'\$(?P<name>[a-zA-Z_]\w*)')


def bashVarToPythonVar(m)->str:
    s = m.groupdict()
    return "'{" + s["name"].lower() + "}'"


def formatWithVars(oristr: str, var: Dict[str, Optional[str]])->str:
    try:
        oristr = varFormatRE.sub(bashVarToPythonVar, oristr)
        return oristr.format(**var)
    except:
        return oristr
