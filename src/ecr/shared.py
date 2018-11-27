from typing import Optional
from . import core
from .core import WorkManager, path
from .core.types import VariableMapping

version = core.__version__

cwd: Optional[str] = None

man: Optional[WorkManager] = None

variables: VariableMapping = {
    "current": lambda: man.currentFile.name if man and man.currentFile else None,
    "wdir": lambda: man.workingDirectory if man else None,
    "edir": lambda: path.getMainPath(man.workingDirectory) if man else None,
    "jdir": lambda: path.getJudgerPath(man.workingDirectory) if man else None,
    "tdir": lambda: path.getTemplatePath(man.workingDirectory) if man else None,
    "config": lambda: path.getConfigPath(man.workingDirectory) if man else None,
    "input": lambda: path.getFileInputPath(man.workingDirectory) if man else None,
    "output": lambda: path.getFileOutputPath(man.workingDirectory) if man else None,
}
