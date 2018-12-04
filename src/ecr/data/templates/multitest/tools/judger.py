import difflib
import os
from typing import Optional, Tuple

from ecr.lib.judger import DataItem, JudgeResult, trimLineEnd, getFileContents, judged
from ecr.lib.console import info, error, write

dataPath = "./data"


def judgeOne(std: DataItem, out: DataItem) -> Tuple[JudgeResult, Optional[str]]:
    diff = difflib.context_diff(trimLineEnd(std.data), trimLineEnd(
        out.data), fromfile=std.name, tofile=out.name, lineterm="")
    ls = list(diff)
    if ls:
        return JudgeResult.Wrong, "\n".join(ls)
    else:
        return JudgeResult.Accept, None


def judge():
    total = 0
    passed = 0
    for item in os.listdir(dataPath):
        inputFile = os.path.join(dataPath, item)
        if not os.path.isfile(inputFile):
            continue
        if not item.startswith("input"):
            continue
        total += 1
        name = os.path.splitext(item)[0].replace("input", "")
        expect = os.path.join(dataPath, item.replace("input", "std"))
        real = os.path.join(dataPath, item.replace("input", "output"))
        info(f"Judging: {name}")
        data = getFileContents(expect, real)
        result, message = judgeOne(
            DataItem(expect, data[0]), DataItem(real, data[1]))
        if result == JudgeResult.Accept:
            passed += 1
        else:
            error(f"Test case {name} failed.")
        if message:
            write(message)
    info(f"Passed {passed} / {total}")
    if total == passed:
        return JudgeResult.Accept, None
    else:
        return JudgeResult.Wrong, None


if __name__ == "__main__":
    judged(*judge())
