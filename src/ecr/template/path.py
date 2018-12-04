import os


def getConfigPath(basepath: str) -> str:
    return os.path.join(basepath, ".template")


def getConfigFile(basepath: str) -> str:
    return os.path.join(getConfigPath(basepath), "config.yml")
