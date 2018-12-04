import os
import shutil

TEMPLATE_CONFIG_PATH = ".template"

default_ignore = shutil.ignore_patterns(TEMPLATE_CONFIG_PATH)

def getConfigPath(basepath: str) -> str:
    return os.path.join(basepath, TEMPLATE_CONFIG_PATH)


def getConfigFile(basepath: str) -> str:
    return os.path.join(getConfigPath(basepath), "config.yml")
