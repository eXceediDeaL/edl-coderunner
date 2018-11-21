from .core import WorkManager, path
from .ui import CLI

version = "0.0.2"

cwd = None

man: WorkManager = None

variables = {
    "current": lambda: None if man == None else man.currentFile,
    "wdir": lambda: None if man == None else man.workingDirectory,
    "config": lambda: None if man == None else path.getConfigPath(man.workingDirectory),
    "input": lambda: None if man == None else path.getFileInputPath(man.workingDirectory),
    "output": lambda: None if man == None else path.getFileOutputPath(man.workingDirectory),
}
