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
from .types import ExecutorMapping, CommandMapping, JudgerMapping, CommandList
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
CONST_eVersion: str = "eVersion"

fileextToLanguage: Dict[str, str] = {
    "c": "c",
    "cpp": "cpp",
    "cs": "csharp",
    "fs": "fsharp",
    "py": "python",
    "java": "java",
    "pas": "pascal",
    "m": "objective-c",
    "js": "javascript",
    "rb": "ruby",
    "go": "go",
    "php": "php",
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


class WorkItemType(Enum):
    File: int = 0
    Directory: int = 1


class WorkItem:
    def __init__(self, path: str, name: str, types: WorkItemType = WorkItemType.File):
        self.path: str = path
        self.name: str = name
        self.type: WorkItemType = types
        self.run: Optional[CommandList] = None
        self.judge: Optional[CommandList] = None


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


def initializeCodeDirectory(path: str) -> None:
    os.mkdir(ecrpath.getCodeDirDataPath(path))
    config: Dict[str, Optional[List]] = {
        "run": None,
        "judge": None,
    }
    with open(ecrpath.getCodeDirConfigPath(path), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))


def loadCodeDirectory(path: str, name: str)->Optional[WorkItem]:
    try:
        ret = WorkItem(path, name, WorkItemType.Directory)
        with open(ecrpath.getCodeDirConfigPath(path), "r", encoding='utf-8') as f:
            config = yaml.load(f.read())
            ret.judge = config["judge"]
            ret.run = config["run"]
        return ret
    except:
        return None


class WorkManager:
    def __init__(self, path: str):
        self.workingDirectory: str = path
        self.executorMap: ExecutorMapping = {}
        self.judgerMap: JudgerMapping = {}
        self.tempFileFilter: List[str] = []
        self.currentFile: Optional[WorkItem] = None
        self.importedCommand: CommandMapping = {}
        self.defaultShell: Optional[str] = None
        self.defaultIO: str = defaultData.io
        self.defaultTimeLimit: int = defaultData.timeLimit
        self.defaultJudger: str = defaultData.judger
        self.state: WorkManagerState = WorkManagerState.Empty
        self.runner: Optional[Runner] = None
        self.defaultEditor: Optional[str] = None
        from . import __version__
        self.eVersion: str = __version__

    def getWorkItem(self, name: str, isdir: bool) -> Optional[WorkItem]:
        path = os.path.join(self.workingDirectory, name)
        if isdir:
            if not os.path.isdir(path):
                return WorkItem(path, name, WorkItemType.Directory)
            else:
                return loadCodeDirectory(path, name)
        else:
            return WorkItem(
                self.workingDirectory, name, WorkItemType.File)

    def setCurrent(self, item: str, isdir: bool) -> bool:
        if item is None:
            self.currentFile = None
        else:
            self.currentFile = self.getWorkItem(item, isdir)
        return True

    def newCode(self, item: Optional[WorkItem] = None)->Optional[WorkItem]:
        try:
            if not item:
                item = self.currentFile
            assert item
            dstPath = os.path.join(self.workingDirectory, item.name)
            if item.type == WorkItemType.Directory:
                os.mkdir(dstPath)
                initializeCodeDirectory(dstPath)
            else:
                ext = ecrpath.getFileExt(item.name)
                lang = fileextToLanguage[ext] if ext in fileextToLanguage else None

                tempPath = None if not lang else os.path.join(ecrpath.getTemplatePath(
                    self.workingDirectory), f"{TEMPLATE_NAME}.{languageToFileext[lang]}")
                if tempPath and os.path.exists(tempPath):
                    shutil.copyfile(tempPath, dstPath)
                else:
                    open(dstPath, "w").close()
            return item
        except:
            return None

    def edit(self, item: Optional[WorkItem] = None)->bool:
        try:
            if not item:
                item = self.currentFile
            titem: WorkItem = cast(WorkItem, item)
            if titem.type == WorkItemType.File:
                click.edit(filename=titem.name, editor=self.defaultEditor)
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

    def __runCommands(self, io: str, commands: CommandList, variables: Dict[str, str], wdir: Optional[str] = None) -> bool:
        errf = color.useRed("×")
        passf = color.useGreen("√")
        isSuccess = True
        sumStep = len(commands)
        cwd = wdir if wdir else self.workingDirectory
        console = ui.getConsole()
        for ind, bcmd in enumerate(commands):
            if not isSuccess:
                break
            cmd, timelimit = None, None
            if not isinstance(bcmd, str):
                cmd, timelimit = bcmd
            else:
                cmd, timelimit = bcmd, self.defaultTimeLimit
            _cmd = cmd.format(**variables)
            console.write(
                "(", color.useYellow(str(ind+1)), f"/{sumStep}) ", _cmd, sep="")
            proc = None
            rresult, retcode = None, None
            try:
                if ind == sumStep - 1:  # last command
                    if io[0] == "s":  # stdin
                        timelimit = None
                    console.write("-"*20)
                    proc = subprocess.Popen(
                        getSystemCommand(_cmd, self),
                        cwd=cwd,
                        stdin=None if io[0] == "s"
                        else open(ecrpath.getFileInputPath(self.workingDirectory), "r"),
                        stdout=None if io[1] == "s"
                        else open(ecrpath.getFileOutputPath(self.workingDirectory), "w"),
                        stderr=None)
                else:
                    proc = subprocess.Popen(
                        getSystemCommand(_cmd, self),
                        cwd=cwd,
                        stdin=None, stdout=None, stderr=None)

                self.runner = Runner(proc=proc, io=io, timelimit=timelimit)
                rresult, retcode = self.runner.run()
            except BaseException:
                isSuccess = False
            finally:
                if ind == sumStep - 1:  # last command
                    console.write("-"*20)
                console.write(
                    "   ->",
                    passf if retcode == 0 else errf,
                    f"{round(cast(Runner,self.runner).usedTime*1000)/1000}s")
                if rresult != RunResult.Success:
                    console.write(
                        "(", color.useRed(str(ind + 1)), f"/{sumStep}) ",
                        _cmd, " -> ", color.useRed(str(retcode)), sep="", end=" ")
                    if rresult == RunResult.TimeOut:
                        console.write(color.useRed("Time out"))
                    else:
                        console.write()
                    self.runner = None
                    isSuccess = False
        self.runner = None
        return isSuccess

    def execute(self, io: Optional[str] = None, item: Optional[WorkItem] = None)->bool:
        if not io:
            io = self.defaultIO
        if not item:
            item = self.currentFile
        titem: WorkItem = cast(WorkItem, item)
        cmds: Optional[CommandList] = None
        console = ui.getConsole()
        if titem.type == WorkItemType.File:
            file = titem.name
            fileNameWithoutExt, fileext = cast(
                Tuple[str, str], os.path.splitext(file))
            lang = fileextToLanguage[fileext[1:]]
            cmds = self.executorMap[lang]
            formats = {
                defaultData.CMDVAR_FileName: file,
                defaultData.CMDVAR_FileNameWithoutExt: fileNameWithoutExt,
            }

            console.info(f"Running {file}")
            return self.__runCommands(io, cmds, formats)
        else:  # directory
            cmds = titem.run
            formats = {
            }

            console.info(f"Running {titem.name}")
            if cmds:
                return self.__runCommands(io, cmds, formats, wdir=titem.path)
            else:
                return True
        return False

    def judge(self, item: Optional[WorkItem] = None,
              reexecute: bool = False, judger: Optional[str] = None) -> bool:
        if not item:
            item = self.currentFile
        if not judger:
            judger = self.defaultJudger
        if reexecute:
            if not self.execute(defaultData.CIO_FIFO, item):
                return False

        console = ui.getConsole()
        titem: WorkItem = cast(WorkItem, item)
        cmds: Optional[CommandList] = None
        if titem.type == WorkItemType.File:
            cmds = self.judgerMap[judger]
            formats = {
                defaultData.CMDVAR_JudgerDir: ecrpath.getJudgerPath(self.workingDirectory),
                defaultData.CMDVAR_ExpectFile: ecrpath.getFileStdPath(self.workingDirectory),
                defaultData.CMDVAR_RealFile: ecrpath.getFileOutputPath(self.workingDirectory),
            }

            console.info(f"Judging {titem.name}")
            return self.__runCommands(defaultData.CIO_SISO, cmds, formats)
        else:  # directory
            cmds = titem.judge
            formats = {
            }

            console.info(f"Judging {titem.name}")
            if cmds:
                return self.__runCommands(defaultData.CIO_SISO, cmds, formats, wdir=titem.path)
            else:
                return True


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
            ret.eVersion = config[CONST_eVersion]
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

    # templatePath = ecrpath.getTemplatePath(basepath)
    # os.mkdir(templatePath)
    # for k, v in defaultData.codeTemplate.items():
    # with open(os.path.join(templatePath, f"{TEMPLATE_NAME}.{languageToFileext[k]}"),
    #   "w", encoding='utf-8') as f:
    # f.write(v)

    # os.mkdir(ecrpath.getJudgerPath(basepath))
    shutil.copytree(ecrpath.getCoreJudgerPath(),
                    ecrpath.getJudgerPath(basepath))
    shutil.copytree(ecrpath.getCoreTemplatePath(),
                    ecrpath.getTemplatePath(basepath))

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

    from . import __version__

    config = {CONST_tempFileFilter: defaultData.tempFileFilter,
              CONST_importedCommand: defaultData.importedCommand,
              CONST_defaultShell: "powershell -c" if platform.system() == "Windows" else None,
              CONST_defaultIO: defaultData.io,
              CONST_defaultTimeLimit: defaultData.timeLimit,
              CONST_defaultEditor: defaultData.editor,
              CONST_defaultJudger: defaultData.judger,
              CONST_eVersion: __version__}

    with open(ecrpath.getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(config, indent=4,
                          default_flow_style=False))
