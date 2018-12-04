import os
from enum import Enum
from typing import Dict, List, Optional

import yaml

from . import path as ecrpath
from .. import log
from .types import CommandList


class WorkItemType(Enum):
    File: int = 0
    Directory: int = 1


class WorkItem:
    def __init__(self, path: str, name: str, types: WorkItemType = WorkItemType.File):
        self.path: str = path
        self.name: str = name
        self.type: WorkItemType = types
        self.run: Optional[CommandList] = None
        self.test: Optional[CommandList] = None


def initializeCodeDirectory(path: str) -> None:
    config: Dict[str, Optional[List]] = {
        "run": None,
        "test": None,
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
