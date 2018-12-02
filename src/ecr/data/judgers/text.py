import difflib
from typing import Optional, Tuple

from ecr.lib.judger import DataItem, JudgeResult, judging, trimLineEnd


def judge(std: DataItem, out: DataItem) -> Tuple[JudgeResult, Optional[str]]:
    diff = difflib.context_diff(trimLineEnd(std.data), trimLineEnd(
        out.data), fromfile=std.name, tofile=out.name, lineterm="")
    ls = list(diff)
    if ls:
        return JudgeResult.Wrong, "\n".join(ls)
    else:
        return JudgeResult.Accept, None


if __name__ == "__main__":
    judging(judge)
