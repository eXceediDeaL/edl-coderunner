import os
import shutil
import subprocess
import time
import platform
from typing import cast, Dict, List, Optional, Tuple, Callable
from enum import Enum
import yaml
import click
from prompt_toolkit.application import run_in_terminal
from .types import ExecutorMapping, CommandMapping, JudgerMapping
from ..ui import color
from . import defaultData
from . import path as ecrpath
from .. import ui

CONST_tempFileFilter: str = "tempFileFilter"
CONST_importedCommand: str = "importedCommand"
CONST_defaultShell: str = "defaultShell"
CONST_defaultIO: str = "defaultIO"
CONST_defaultTimeLimit: str = "defaultTimeLimit"
CONST_defaultEditor: str = "defaultEditor"
CONST_defaultJudger: str = "defaultJudger"

fileextToLanguage: Dict[str, str] = {
    "c": "c",
    "cpp": "cpp",
    "py": "python",
    "java": "java",
    "pas": "pascal",
    "m": "objective-c",
    "js": "javascript",
    "rb": "ruby",
    "go": "go",
    "sh": "shellscript",
    "ps1": "powershell",
}

languageToFileext: Dict[str, str] = {
    v: k for k, v in fileextToLanguage.items()}

TEMPLATE_NAME: str = "base"


def hasInitialized(basepath: str)->bool:
    return os.path.exists(ecrpath.getMainPath(basepath))


def getSystemCommand(cmd: str, man=None) -> str:
    if not man or not man.defaultShell:
        return cmd
    else:
        return " ".join([man.defaultShell, f'"{cmd}"'])


class WorkManagerState(Enum):
    Empty: int = 0
    Loaded: int = 1
    LoadFailed: int = 2


class RunResult(Enum):
    Success: int = 0
    Error: int = 1
    TimeOut: int = 2


def safeOutput(*values: List)->None:
    run_in_terminal(lambda: print(*values, end=""))


class Runner:
    def __init__(self, proc: subprocess.Popen, io: str, timelimit: Optional[int] = None):
        self.proc: subprocess.Popen = proc
        self.timeLimit: Optional[int] = timelimit
        self.communicate = self.proc.communicate
        self.usedTime: float = 0
        self.isRunning: bool = False
        self.io: str = io
        self.canInput: bool = io[0] == "s"

    def terminate(self)->None:
        os.kill(self.proc.pid, 9)
        self.isRunning = False

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


class WorkManager:
    def __init__(self, path: str):
        self.workingDirectory: str = path
        self.executorMap: ExecutorMapping = {}
        self.judgerMap: JudgerMapping = {}
        self.tempFileFilter: List[str] = []
        self.currentFile: Optional[str] = None
        self.importedCommand: CommandMapping = {}
        self.defaultShell: Optional[str] = None
        self.defaultIO: str = defaultData.io
        self.defaultTimeLimit: int = defaultData.timeLimit
        self.defaultJudger: str = defaultData.judger
        self.state: WorkManagerState = WorkManagerState.Empty
        self.runner: Optional[Runner] = None
        self.defaultEditor: Optional[str] = None

    def newCode(self, file=None)->bool:
        try:
            if not file:
                file = self.currentFile
            assert file
            ext = ecrpath.getFileExt(file)
            lang = fileextToLanguage[ext] if ext in fileextToLanguage else None
            dstPath = os.path.join(self.workingDirectory, file)
            tempPath = None if not lang else os.path.join(ecrpath.getTemplatePath(
                self.workingDirectory), f"{TEMPLATE_NAME}.{languageToFileext[lang]}")
            if tempPath and os.path.exists(tempPath):
                shutil.copyfile(tempPath, dstPath)
            else:
                open(dstPath, "w").close()
            return True
        except:
            return False

    def edit(self, file: Optional[str] = None)->bool:
        try:
            click.edit(filename=file, editor=self.defaultEditor)
            return True
        except:
            return False

    def clean(self, rmHandler: Optional[Callable[[str], None]] = None)->None:
        for file in os.listdir(self.workingDirectory):
            for pat in self.tempFileFilter:
                try:
                    if pat == ecrpath.getFileExt(os.path.split(file)[-1]):
                        os.remove(os.path.join(self.workingDirectory, file))
                        if rmHandler:
                            rmHandler(file)
                        break
                except:
                    pass

    def execute(self, io: Optional[str] = None, file: Optional[str] = None)->bool:
        if not io:
            io = self.defaultIO
        if not file:
            file = self.currentFile
        errf = color.useRed("×")
        passf = color.useGreen("√")

        fileNameWithoutExt, fileext = cast(
            Tuple[str, str], os.path.splitext(file))
        lang = fileextToLanguage[fileext[1:]]
        cmds = self.executorMap[lang]
        formats = {
            "fileName": file,
            "fileNameWithoutExt": fileNameWithoutExt,
        }
        sumStep = len(cmds)
        ui.console.info(f"Running {file}")

        isSuccess = True

        for ind, bcmd in enumerate(cmds):
            if not isSuccess:
                break
            cmd, timelimit = None, None
            if not isinstance(bcmd, str):
                cmd, timelimit = bcmd
            else:
                cmd, timelimit = bcmd, self.defaultTimeLimit
            _cmd = cmd.format(**formats)
            ui.console.write(
                "(", color.useYellow(str(ind+1)), f"/{sumStep}) ", _cmd, sep="")
            proc = None
            rresult, retcode = None, None
            try:
                if ind == sumStep - 1:  # last command
                    if io[0] == "s":  # stdin
                        timelimit = None
                    ui.console.write("-"*20)
                    proc = subprocess.Popen(
                        getSystemCommand(_cmd, self),
                        cwd=self.workingDirectory,
                        stdin=None if io[0] == "s"
                        else open(ecrpath.getFileInputPath(self.workingDirectory), "r"),
                        stdout=None if io[1] == "s"
                        else open(ecrpath.getFileOutputPath(self.workingDirectory), "w"),
                        stderr=None)
                else:
                    proc = subprocess.Popen(
                        getSystemCommand(_cmd, self),
                        cwd=self.workingDirectory,
                        stdin=None, stdout=None, stderr=None)

                self.runner = Runner(proc=proc, io=io, timelimit=timelimit)
                rresult, retcode = self.runner.run()
            except BaseException:
                self.runner = None
                isSuccess = False
            finally:
                if ind == sumStep - 1:  # last command
                    ui.console.write("-"*20)
                ui.console.write(
                    "   ->",
                    passf if retcode == 0 else errf,
                    f"{round(cast(Runner,self.runner).usedTime*1000)/1000}s")
                if rresult != RunResult.Success:
                    ui.console.write(
                        "(", color.useRed(str(ind + 1)), f"/{sumStep}) ",
                        _cmd, " -> ", retcode, sep="", end=" ")
                    if rresult == RunResult.TimeOut:
                        ui.console.write(color.useRed("Time out"))
                    else:
                        ui.console.write()
                    self.runner = None
                    isSuccess = False
        self.runner = None
        return isSuccess

    def judge(self, file: Optional[str] = None, reexecute: bool = False, judger: Optional[str] = None) -> bool:
        if not file:
            file = self.currentFile
        if not judger:
            judger = self.defaultJudger
        if reexecute:
            if not self.execute(defaultData.CIO_FIFO, file):
                return False

        errf = color.useRed("×")
        passf = color.useGreen("√")

        fileNameWithoutExt, fileext = cast(
            Tuple[str, str], os.path.splitext(file))
        lang = fileextToLanguage[fileext[1:]]
        cmds = self.judgerMap[judger]
        formats = {
            "expectFile": ecrpath.getFileStdPath(self.workingDirectory),
            "realFile": ecrpath.getFileOutputPath(self.workingDirectory),
        }
        sumStep = len(cmds)
        ui.console.info(f"Judging {file}")

        isSuccess = True

        for ind, bcmd in enumerate(cmds):
            if not isSuccess:
                break
            cmd, timelimit = None, None
            if not isinstance(bcmd, str):
                cmd, timelimit = bcmd
            else:
                cmd, timelimit = bcmd, self.defaultTimeLimit
            _cmd = cmd.format(**formats)
            ui.console.write(
                "(", color.useYellow(str(ind+1)), f"/{sumStep}) ", _cmd, sep="")
            proc = None
            rresult, retcode = None, None
            try:
                proc = subprocess.Popen(
                    getSystemCommand(_cmd, self),
                    cwd=self.workingDirectory,
                    stdin=None, stdout=None, stderr=None)

                self.runner = Runner(
                    proc=proc, io=defaultData.CIO_SISO, timelimit=timelimit)
                rresult, retcode = self.runner.run()
            except BaseException:
                self.runner = None
                isSuccess = False
            finally:
                ui.console.write(
                    "   ->",
                    passf if retcode == 0 else errf,
                    f"{round(cast(Runner,self.runner).usedTime*1000)/1000}s")
                if rresult != RunResult.Success:
                    ui.console.write(
                        "(", color.useRed(str(ind + 1)), f"/{sumStep}) ",
                        _cmd, " -> ", retcode, sep="", end=" ")
                    if rresult == RunResult.TimeOut:
                        ui.console.write(color.useRed("Time out"))
                    else:
                        ui.console.write()
                    self.runner = None
                    isSuccess = False
        self.runner = None
        return isSuccess


def load(basepath: str) -> Optional[WorkManager]:
    if not hasInitialized(basepath):
        return None
    ret = WorkManager(basepath)
    try:
        with open(ecrpath.getExecutorPath(basepath), "r", encoding='utf-8') as f:
            ret.executorMap = yaml.load(f.read())

        with open(ecrpath.getJudgerConfigPath(basepath), "r", encoding='utf-8') as f:
            ret.judgerMap = yaml.load(f.read())

        with open(ecrpath.getConfigPath(basepath), "r", encoding='utf-8') as f:
            config = yaml.load(f.read())
            ret.tempFileFilter = config[CONST_tempFileFilter]
            ret.importedCommand = config[CONST_importedCommand]
            ret.defaultShell = config[CONST_defaultShell]
            ret.defaultIO = config[CONST_defaultIO]
            ret.defaultEditor = config[CONST_defaultEditor]
            ret.defaultJudger = config[CONST_defaultJudger]
        ret.state = WorkManagerState.Loaded
    except:
        ret.state = WorkManagerState.LoadFailed
    return ret


def clear(basepath: str)->None:
    oipath = ecrpath.getMainPath(basepath)
    if hasInitialized(basepath):
        shutil.rmtree(oipath)


def initialize(basepath: str)->None:
    clear(basepath)

    oipath = ecrpath.getMainPath(basepath)
    os.mkdir(oipath)

    templatePath = ecrpath.getTemplatePath(basepath)
    os.mkdir(templatePath)
    os.mkdir(ecrpath.getJudgerPath(basepath))

    for k, v in defaultData.codeTemplate.items():
        with open(os.path.join(templatePath, f"{TEMPLATE_NAME}.{languageToFileext[k]}"),
                  "w", encoding='utf-8') as f:
            f.write(v)

    executors = defaultData.executors
    with open(ecrpath.getExecutorPath(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(executors, indent=4,
                          default_flow_style=False))

    judgers = defaultData.judgers
    with open(ecrpath.getJudgerConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(judgers, indent=4,
                          default_flow_style=False))

    open(ecrpath.getFileInputPath(basepath), "w").close()
    open(ecrpath.getFileOutputPath(basepath), "w").close()
    open(ecrpath.getFileStdPath(basepath), "w").close()

    config = {CONST_tempFileFilter: defaultData.tempFileFilter,
              CONST_importedCommand: defaultData.importedCommand,
              CONST_defaultShell: "powershell -c" if platform.system() == "Windows" else None,
              CONST_defaultIO: defaultData.io,
              CONST_defaultTimeLimit: defaultData.timeLimit,
              CONST_defaultEditor: defaultData.editor,
              CONST_defaultJudger: defaultData.judger}

    with open(ecrpath.getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))
