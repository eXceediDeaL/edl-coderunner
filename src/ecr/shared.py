from typing import Optional
from .core import WorkManager, path
from .core.types import VariableMapping

version = "0.0.2"

cwd: Optional[str] = None

man: Optional[WorkManager] = None

variables: VariableMapping = {
    "current": lambda: None if man is None else man.currentFile,
    "wdir": lambda: None if man is None else man.workingDirectory,
    "config": lambda: None if man is None else path.getConfigPath(man.workingDirectory),
    "input": lambda: None if man is None else path.getFileInputPath(man.workingDirectory),
    "output": lambda: None if man is None else path.getFileOutputPath(man.workingDirectory),
}
