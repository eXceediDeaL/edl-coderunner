import os


def getMainPath(basepath: str)->str:
    return os.path.join(basepath, ".ecr")


def getConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "config.yml")


def getExecutorPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "executor.yml")

def getJudgerConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "judger.yml")

def getTemplatePath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "templates")


def getJudgerPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "judgers")

def getFileInputPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "input.data")


def getFileOutputPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "output.data")


def getFileStdPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "std.data")


def getFileExt(filename: str) -> str:
    return os.path.splitext(filename)[1][1:]
