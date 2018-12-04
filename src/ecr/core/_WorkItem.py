from enum import Enum
from typing import Dict, List, Optional, Callable
import os
import shutil
import yaml

from . import path as ecrpath
from . import defaultData
from .. import log, ui
from ..types import CommandList
from ..template import Template, default_ignore
from ._Runner import runCommands


class WorkItemType(Enum):
    File: int = 0
    Directory: int = 1


class WorkItem:
    def __init__(self, path: str, name: str, types: WorkItemType = WorkItemType.File):
        self.path: str = path
        self.name: str = name
        self.type: WorkItemType = types
        self.run: CommandList = []
        self.test: CommandList = []


def initializeCodeDirectory(path: str) -> None:
    config: Dict[str, Optional[List]] = {
        "run": [],
        "test": [],
    }
    with open(ecrpath.getCodeDirConfigPath(path), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))


def loadCodeDirectory(path: str, name: str)->Optional[WorkItem]:
    try:
        ret = WorkItem(path, name, WorkItemType.Directory)
        with open(ecrpath.getCodeDirConfigPath(path), "r", encoding='utf-8') as f:
            config = yaml.load(f.read())
            ret.test = config["test"]
            ret.run = config["run"]
        return ret
    except:
        log.errorWithException("Load dir-workitem failed")
        return None


def _runcommands(commands: CommandList, variables: Dict[str, str], wdir: str, getSystemCommand: Callable[[str], str], defaultTimeLimit: Optional[int] = None) -> bool:
    return runCommands(io=defaultData.CIO_SISO, commands=commands, variables=variables, wdir=wdir,
                       getSystemCommand=getSystemCommand,
                       inputFile=None,
                       outputFile=None,
                       defaultTimeLimit=defaultTimeLimit)


def initializeCodeDirectoryWithTemplate(man, templ: Template, basepath: str, dstpath: str) -> None:
    console = ui.getConsole()

    formats = {
    }

    console.info(f"Initialize {dstpath} by {templ.subject}")

    if os.path.isdir(dstpath):
        shutil.rmtree(dstpath)

    flag = True
    from ._manager import getSystemCommand

    console.info(f"Copying files")

    if os.path.normpath(templ.rootPath) == os.path.normpath(basepath):
        shutil.copytree(
            templ.rootPath, dstpath, ignore=default_ignore)
    else:
        shutil.copytree(templ.rootPath, dstpath)

    if templ.after:
        console.info(f"After creating")
        flag = flag and _runcommands(commands=templ.after, variables=formats, wdir=dstpath,
                                     getSystemCommand=lambda p: getSystemCommand(p, man), defaultTimeLimit=man.defaultTimeLimit)

    if not flag:
        console.error("Initializing failed.")
        return
