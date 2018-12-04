import os


def getGlobalBasePath() -> str:
    return os.path.expanduser("~")


def getMainPath(basepath: str)->str:
    return os.path.join(basepath, ".ecr")


def getConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "config.yml")


def getExecutorPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "executor.yml")


def getJudgerConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "judger.yml")


def getTemplateConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "template.yml")


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


def getCodeDirConfigPath(basepath: str) -> str:
    return os.path.join(basepath, "config.yml")


# def getCodeDirDataPath(basepath: str) -> str:
    # return os.path.join(basepath, "data")


def getFileExt(filename: str) -> str:
    return os.path.splitext(filename)[1][1:]


def getCoreJudgerPath() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "judgers")


def getCoreTemplatePath() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "templates")
