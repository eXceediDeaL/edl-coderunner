from .core import WorkManager, path

version = "0.0.2"

cwd = None

man: WorkManager

variables = {
    "current": lambda: None if man is None else man.currentFile,
    "wdir": lambda: None if man is None else man.workingDirectory,
    "config": lambda: None if man is None else path.getConfigPath(man.workingDirectory),
    "input": lambda: None if man is None else path.getFileInputPath(man.workingDirectory),
    "output": lambda: None if man is None else path.getFileOutputPath(man.workingDirectory),
}
