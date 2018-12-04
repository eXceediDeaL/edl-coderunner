import os
import shutil
from typing import Optional, Tuple
import yaml
from .. import log
from ..types import CommandList
from .path import getConfigPath, getConfigFile

CONST_rootPath: str = "rootPath"
CONST_beforeCreate: str = "beforeCreate"
CONST_afterCreate: str = "afterCreate"


class Template:
    def __init__(self, rootpath: str):
        self.rootPath: str = rootpath
        self.beforeCreate: CommandList = []
        self.afterCreate: CommandList = []


def load(basepath: str) -> Tuple[Optional[Template], Optional[Exception]]:
    if not os.path.isdir(getConfigPath(basepath)) or not os.path.isfile(getConfigFile(basepath)):
        return Template(basepath), None
    ret = Template("")
    exp = None
    try:
        with open(getConfigFile(basepath), "r", encoding='utf-8') as f:
            config = yaml.load(f.read())
            ret.rootPath = os.path.join(basepath, config[CONST_rootPath])
            ret.beforeCreate = config[CONST_beforeCreate]
            ret.afterCreate = config[CONST_afterCreate]
    except Exception as e:
        log.errorWithException(f"Loading template failed from {basepath}")
        exp = e
    return ret, exp


def clear(basepath: str)->None:
    oipath = getConfigPath(basepath)
    if os.path.isdir(oipath):
        log.debug(f"Clear template data at {basepath}")
        shutil.rmtree(oipath)


def initialize(basepath: str)->None:
    clear(basepath)

    log.debug(f"Initialize template data at {basepath}")

    if not os.path.isdir(basepath):
        os.mkdir(basepath)

    oipath = getConfigPath(basepath)
    os.mkdir(oipath)

    config = {CONST_rootPath: "",
              CONST_beforeCreate: [],
              CONST_afterCreate: [], }

    with open(getConfigFile(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))
