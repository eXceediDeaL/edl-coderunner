import subprocess
import time
from enum import Enum
from typing import Optional, Tuple


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
