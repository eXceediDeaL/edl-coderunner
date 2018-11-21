import os
import json
import shutil
import re
import subprocess
import time
import platform
import click
import signal
from prompt_toolkit.application import run_in_terminal
from enum import Enum
from ..ui import color
from . import defaultData, path
from .. import ui

CONST_tempFileFilter = "tempFileFilter"
CONST_importedCommand = "importedCommand"
CONST_defaultShell = "defaultShell"
CONST_defaultIO = "defaultIO"
CONST_defaultTimeLimit = "defaultTimeLimit"
CONST_defaultEditor = "defaultEditor"

fileextToLanguage = {
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

languageToFileext = {v: k for k, v in fileextToLanguage.items()}

TEMPLATE_NAME = "base"


def hasInitialized(basepath: str)->bool:
    return os.path.exists(path.getMainPath(basepath))


def getSystemCommand(cmd: str, man=None) -> str:
    if man == None or man.defaultShell == None:
        return cmd
    else:
        return " ".join([man.defaultShell, f'"{cmd}"'])


class WorkManagerState(Enum):
    Empty = 0,
    Loaded = 1,
    LoadFailed = 2,


class RunResult(Enum):
    Success = 0
    Error = 1
    TimeOut = 2


def safeOutput(*values):
    run_in_terminal(lambda: print(*values, end=""))


class Runner:
    def __init__(self, proc: subprocess.Popen, io: str, timelimit=None):
        self.proc = proc
        self.timeLimit = timelimit
        self.communicate = self.proc.communicate
        self.usedTime = 0
        self.isRunning = False
        self.io = io
        self.canInput = io[0] == "s"

    def terminate(self):
        os.kill(self.proc.pid, 9)
        self.isRunning = False

    def input(self, data):
        self.proc.stdin.write(data.encode("utf-8"))
        self.proc.stdin.flush()

    def run(self):
        self.isRunning = True
        isTimeout = False
        bg_time = time.time()
        try:
            # if self.io[1] != "s":  # not stdout
            self.communicate(timeout=self.timeLimit)
            """else:  # stdout for async
                while self.proc.poll() == None and self.isRunning:
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
            elif self.proc.returncode != 0:
                return (RunResult.Error, self.proc.returncode)
            else:
                return (RunResult.Success, self.proc.returncode)


class WorkManager:
    def __init__(self, path: str):
        self.workingDirectory: str = path
        self.executorMap: dict = {}
        self.tempFileFilter: list = []
        self.currentFile: str = None
        self.importedCommand = {}
        self.defaultShell = None
        self.defaultIO = defaultData.io
        self.defaultTimeLimit = defaultData.timeLimit
        self.state = WorkManagerState.Empty
        self.runner: Runner = None
        self.defaultEditor = None

    def newCode(self, file=None):
        try:
            if file == None:
                file = self.currentFile
            assert file != None
            ext = path.getFileExt(file)
            lang = fileextToLanguage[ext] if ext in fileextToLanguage else None
            dstPath = os.path.join(self.workingDirectory, file)
            tempPath = None if lang == None else os.path.join(path.getTemplatePath(
                self.workingDirectory), f"{TEMPLATE_NAME}.{languageToFileext[lang]}")
            if tempPath != None and os.path.exists(tempPath):
                shutil.copyfile(tempPath, dstPath)
            else:
                open(dstPath, "w").close()
            return True
        except:
            return False

    def edit(self, file=None):
        try:
            click.edit(filename=file, editor=self.defaultEditor)
            return True
        except:
            return False

    def clean(self, rmHandler=None):
        for file in os.listdir(self.workingDirectory):
            for pat in self.tempFileFilter:
                try:
                    if pat == path.getFileExt(os.path.split(file)[-1]):
                        os.remove(os.path.join(self.workingDirectory, file))
                        if rmHandler != None:
                            rmHandler(file)
                        break
                except:
                    pass

    def execute(self, io=None, file=None):
        if io == None:
            io = self.defaultIO
        if file == None:
            file = self.currentFile
        errf = color.useRed("×")
        passf = color.useGreen("√")

        fileNameWithoutExt, fileext = os.path.splitext(file)
        lang = fileextToLanguage[fileext[1:]]
        cmds = self.executorMap[lang]
        formats = {
            "fileName": file,
            "fileNameWithoutExt": fileNameWithoutExt,
            "dir": self.workingDirectory,
        }
        sumStep = len(cmds)
        ui.console.info(f"Running {file}")

        for ind, bcmd in enumerate(cmds):
            cmd, timelimit = None, None
            if not isinstance(bcmd, str):
                cmd, timelimit = bcmd
            else:
                cmd, timelimit = bcmd, self.defaultTimeLimit
            _cmd = cmd.format(**formats)
            ui.console.write(
                "(", color.useCyan(str(ind+1)), f"/{sumStep}) ", _cmd, sep="")
            proc = None
            rresult, retcode = None, 0
            try:
                if ind == sumStep - 1:  # last command
                    if io[0] == "s":  # stdin
                        timelimit = None
                    ui.console.write("-"*20)
                    proc = subprocess.Popen(getSystemCommand(_cmd, self), cwd=self.workingDirectory,
                                            stdin=None if io[0] == "s" else open(
                                                path.getFileInputPath(self.workingDirectory), "r"),
                                            stdout=None if io[1] == "s" else open(path.getFileOutputPath(self.workingDirectory), "w"), stderr=None)
                else:
                    proc = subprocess.Popen(getSystemCommand(
                        _cmd, self), cwd=self.workingDirectory, stdin=None, stdout=None, stderr=None)

                self.runner = Runner(proc=proc, io=io, timelimit=timelimit)
                rresult, retcode = self.runner.run()
            except BaseException:
                self.runner = None
                return False
            finally:
                if ind == sumStep - 1:  # last command
                    ui.console.write("-"*20)
                ui.console.write(
                    "   ->", passf if retcode == 0 else errf, f"{round(self.runner.usedTime*1000)/1000}s")
                if rresult != RunResult.Success:
                    ui.console.write(
                        "(", color.useCyan(str(ind+1)), f"/{sumStep}) ", _cmd, " -> ", retcode, sep="", end=" ")
                    if rresult == RunResult.TimeOut:
                        ui.console.write(color.useRed("Time out"))
                    else:
                        ui.console.write()
                    self.runner = None
                    return False
        self.runner = None
        return True


def load(basepath: str) -> WorkManager:
    if not hasInitialized(basepath):
        return None
    ret = WorkManager(basepath)
    try:
        with open(path.getExecutorPath(basepath), "r", encoding='utf-8') as f:
            ret.executorMap = json.loads(f.read())

        with open(path.getConfigPath(basepath), "r", encoding='utf-8') as f:
            config = json.loads(f.read())
            ret.tempFileFilter = config[CONST_tempFileFilter]
            ret.importedCommand = config[CONST_importedCommand]
            ret.defaultShell = config[CONST_defaultShell]
            ret.defaultIO = config[CONST_defaultIO]
            ret.defaultEditor = config[CONST_defaultEditor]
        ret.state = WorkManagerState.Loaded
    except:
        ret.state = WorkManagerState.LoadFailed
    return ret


def clear(basepath: str):
    oipath = path.getMainPath(basepath)
    if hasInitialized(basepath):
        shutil.rmtree(oipath)


def initialize(basepath: str):
    clear(basepath)

    oipath = path.getMainPath(basepath)
    os.mkdir(oipath)

    templatePath = path.getTemplatePath(basepath)
    os.mkdir(templatePath)
    for k, v in defaultData.codeTemplate.items():
        with open(os.path.join(templatePath, f"{TEMPLATE_NAME}.{languageToFileext[k]}"), "w", encoding='utf-8') as f:
            f.write(v)
    executors = defaultData.executors
    with open(path.getExecutorPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(executors, indent=4))

    open(path.getFileInputPath(basepath), "w").close()
    open(path.getFileOutputPath(basepath), "w").close()

    config = {CONST_tempFileFilter: defaultData.tempFileFilter,
              CONST_importedCommand: defaultData.importedCommand,
              CONST_defaultShell: "powershell -c" if platform.system() == "Windows" else None,
              CONST_defaultIO: defaultData.io,
              CONST_defaultTimeLimit: defaultData.timeLimit,
              CONST_defaultEditor: defaultData.editor}

    with open(path.getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(config, indent=4))
