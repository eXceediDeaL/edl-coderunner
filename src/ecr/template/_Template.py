import os
import shutil
from typing import Optional, Tuple
import yaml
from .. import log
from ..types import CommandList
from .path import getConfigPath, getConfigFile

CONST_rootPath: str = "rootPath"
CONST_after: str = "after"
CONST_subject: str = "subject"


class Template:
    def __init__(self, subject: str, rootpath: str):
        self.subject: str = subject
        self.rootPath: str = rootpath
        self.after: CommandList = []


def load(basepath: str) -> Tuple[Optional[Template], Optional[Exception]]:
    if not os.path.isdir(getConfigPath(basepath)) or not os.path.isfile(getConfigFile(basepath)):
        return Template(os.path.split(basepath)[-1], basepath), None
    ret = Template("", "")
    exp = None
    try:
        with open(getConfigFile(basepath), "r", encoding='utf-8') as f:
            config = yaml.load(f.read())
            ret.subject = config[CONST_subject]
            ret.rootPath = os.path.join(basepath, config[CONST_rootPath])
            ret.after = config[CONST_after]
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

    from ..core.manager import initializeCodeDirectory

    initializeCodeDirectory(basepath)

    oipath = getConfigPath(basepath)
    os.mkdir(oipath)

    config = {CONST_subject: os.path.split(basepath)[-1],
              CONST_rootPath: "",
              CONST_after: [], }

    with open(getConfigFile(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))
