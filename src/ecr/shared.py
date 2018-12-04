from typing import Dict, List, Optional, cast

from . import core
from .core import WorkManager, path
from .types import VariableMapping

_cwd: Optional[str] = None

_man: Optional[WorkManager] = None

_variables: VariableMapping = {
    "current": lambda: _man.currentFile.name if _man and _man.currentFile else None,
    "wdir": lambda: _man.workingDirectory if _man else None,
    "edir": lambda: path.getMainPath(_man.getConfigPath()) if _man else None,
    "jdir": lambda: path.getJudgerPath(_man.getConfigPath()) if _man else None,
    "tdir": lambda: path.getTemplatePath(_man.getConfigPath()) if _man else None,
    "config": lambda: path.getConfigPath(_man.getConfigPath()) if _man else None,
    "input": lambda: path.getFileInputPath(_man.getConfigPath()) if _man else None,
    "output": lambda: path.getFileOutputPath(_man.getConfigPath()) if _man else None,
    "globaldir": lambda: path.getMainPath(path.getGlobalBasePath()),
}

_logData: List[str] = []


def getLogData() -> List[str]:
    return _logData


def getManager()->Optional[WorkManager]:
    return _man


def setManager(man: Optional[WorkManager]) -> None:
    global _man
    _man = man


def getCwd() -> str:
    return cast(str, _cwd)


def setCwd(cwd) -> None:
    global _cwd
    _cwd = cwd


def getVersion() -> str:
    return core.__version__


def getVariables() -> Dict[str, Optional[str]]:
    return {k: v() for k, v in _variables.items()}
