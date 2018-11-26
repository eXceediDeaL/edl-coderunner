from typing import Optional
from .core import WorkManager, path
from .core.types import VariableMapping

version = "0.0.2"

cwd: Optional[str] = None

man: Optional[WorkManager] = None

variables: VariableMapping = {
    "current": lambda: man.currentFile if man else None,
    "wdir": lambda: man.workingDirectory if man else None,
    "config": lambda: path.getConfigPath(man.workingDirectory) if man else None,
    "input": lambda: path.getFileInputPath(man.workingDirectory) if man else None,
    "output": lambda: path.getFileOutputPath(man.workingDirectory) if man else None,
}
