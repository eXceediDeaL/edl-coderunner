from typing import List, Tuple, Optional, Callable
from enum import Enum
import difflib
import sys
import os


class JudgeResult(Enum):
    Accept = 0
    Wrong = 1
    Error = -1


class DataItem:
    def __init__(self, file: str, data: List[str]):
        self.file: str = file
        self.name = os.path.split(self.file)[-1]
        self.data: List[str] = data


def judged(code: JudgeResult, message: Optional[str] = None):
    if message:
        print(message)
    exit(code.value)


def assertArgv()->None:
    if len(sys.argv) < 3:
        judged(JudgeResult.Error, "Judger Error: Not enough args")


def getFileNames()->Tuple[str, str]:
    return sys.argv[1], sys.argv[2]


def getFileContents() -> Tuple[List[str], List[str]]:
    expectedFile, realFile = getFileNames()
    expectedData: List[str] = []
    realData: List[str] = []
    with open(expectedFile, "r", encoding='utf-8') as f:
        expectedData = f.readlines()
    with open(realFile, "r", encoding='utf-8') as f:
        realData = f.readlines()
    return expectedData, realData


def trimLineEnd(data: List[str]) -> List[str]:
    return [x.rstrip() for x in data]


def judging(func: Callable[[DataItem, DataItem], Tuple[JudgeResult, Optional[str]]]) -> None:
    assertArgv()
    files, data = getFileNames(), getFileContents()
    judged(*func(DataItem(files[0], data[0]), DataItem(files[1], data[1])))
