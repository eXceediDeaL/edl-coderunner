import subprocess
import time
from enum import Enum
from typing import Dict, Optional, Tuple, Callable

from .. import log, ui
from ..types import CommandList
from ..ui import color


class RunResult(Enum):
    Success: int = 0
    Error: int = 1
    TimeOut: int = 2


class Runner:
    def __init__(self, proc: subprocess.Popen, io: str, timelimit: Optional[int] = None):
        self.proc: subprocess.Popen = proc
        self.timeLimit: Optional[int] = timelimit
        self.communicate = self.proc.communicate
        self.usedTime: float = 0
        self.isRunning: bool = False
        self.io: str = io
        self.canInput: bool = io[0] == "s"

    def terminate(self) -> None:
        self.proc.terminate()
        # os.kill(self.proc.pid, 9)
        self.isRunning = False
        self.proc.wait()

    def input(self, data: str)->None:
        self.proc.stdin.write(data.encode("utf-8"))
        self.proc.stdin.flush()

    def run(self)->Tuple[RunResult, Optional[int]]:
        self.isRunning = True
        isTimeout = False
        bg_time = time.time()
        try:
            # if self.io[1] != "s":  # not stdout
            self.communicate(timeout=self.timeLimit)
            # pylint: disable=W0105
            """else:  # stdout for async
                while not self.proc.poll() and self.isRunning:
                    if self.timeLimit != None and time.time() - bg_time > self.timeLimit:
                        raise subprocess.TimeoutExpired(
                            self.proc.cmd, self.timeLimit)
                    s = self.proc.stdout.readline().decode("utf-8")
                    safeOutput(s)
                if self.proc.poll() != 0 and self.isRunning:  # hit error
                    s = self.proc.stderr.read().decode("utf-8")
                    safeOutput(s)"""
        except subprocess.TimeoutExpired:
            isTimeout = True
            self.terminate()
        except KeyboardInterrupt:
            self.terminate()
        finally:
            ed_time = time.time()
            self.isRunning = False
            self.usedTime = ed_time - bg_time
        if isTimeout:
            return (RunResult.TimeOut, self.proc.returncode)
        if self.proc.returncode != 0:
            return (RunResult.Error, self.proc.returncode)
        return (RunResult.Success, self.proc.returncode)


def runCommands(io: str, commands: CommandList, variables: Dict[str, str], wdir: str, getSystemCommand: Callable[[str], str], inputFile: str, outputFile: str, defaultTimeLimit: Optional[int] = None, showLog: bool = True) -> bool:
    errf = color.useRed("×")
    passf = color.useGreen("√")
    isSuccess = True
    sumStep = len(commands)
    cwd = wdir
    console = ui.getConsole()
    for ind, bcmd in enumerate(commands):
        if not isSuccess:
            break
        cmd, timelimit = None, None
        if not isinstance(bcmd, str):
            cmd, timelimit = bcmd
        else:
            cmd, timelimit = bcmd, defaultTimeLimit
        _cmd = cmd.format(**variables)
        if showLog:
            console.write(
                "(", color.useYellow(str(ind+1)), f"/{sumStep}) ", _cmd, sep="")
        proc = None
        rresult, retcode = None, None
        runner = None
        try:
            rcmd = getSystemCommand(_cmd)
            if ind == sumStep - 1:  # last command
                if io[0] == "s":  # stdin
                    timelimit = None
                if showLog:
                    console.write("-"*20)
                proc = subprocess.Popen(
                    rcmd,
                    cwd=cwd,
                    stdin=None if io[0] == "s"
                    else open(inputFile, "r"),
                    stdout=None if io[1] == "s"
                    else open(outputFile, "w"),
                    stderr=None)
            else:
                proc = subprocess.Popen(
                    rcmd,
                    cwd=cwd,
                    stdin=None, stdout=None, stderr=None)

            runner = Runner(proc=proc, io=io, timelimit=timelimit)
            rresult, retcode = runner.run()
        except BaseException:
            log.errorWithException(f"Run command failed: {rcmd}")
            isSuccess = False
        finally:
            if ind == sumStep - 1:  # last command
                if showLog:
                    console.write("-"*20)
            if showLog:
                console.write(
                    "   ->",
                    passf if retcode == 0 else errf,
                    f"{round(runner.usedTime*1000)/1000}s")
            if rresult != RunResult.Success:
                if showLog:
                    console.write(
                        "(", color.useRed(str(ind + 1)), f"/{sumStep}) ",
                        _cmd, " -> ", color.useRed(str(retcode)), sep="", end=" ")
                    if rresult == RunResult.TimeOut:
                        console.write(color.useRed("Time out"))
                    else:
                        console.write()
                isSuccess = False
    return isSuccess
