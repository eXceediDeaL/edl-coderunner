import os
import json
import shutil
import re
import subprocess
import time
import platform
from enum import Enum
from ..ui import color
from . import defaultData, path
from .. import ui

CONST_tempFileFilter = "tempFileFilter"
CONST_importedCommand = "importedCommand"
CONST_defaultShell = "defaultShell"
CONST_defaultIO = "defaultIO"
CONST_defaultTimeLimit = "defaultTimeLimit"

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

    def newCode(self, filename):
        ext = path.getFileExt(filename)
        lang = fileextToLanguage[ext] if ext in fileextToLanguage else None
        dstPath = os.path.join(self.workingDirectory, filename)
        tempPath = None if lang == None else os.path.join(path.getTemplatePath(
            self.workingDirectory), f"{TEMPLATE_NAME}.{languageToFileext[lang]}")
        if tempPath != None and os.path.exists(tempPath):
            shutil.copyfile(tempPath, dstPath)
        else:
            open(dstPath, "w").close()
        ui.console.write(color.useGreen("+"), filename)

    def clean(self):
        for file in os.listdir(self.workingDirectory):
            for pat in self.tempFileFilter:
                try:
                    if pat == path.getFileExt(os.path.split(file)[-1]):
                        os.remove(file)
                        ui.console.write(color.useRed("-"), file)
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
        try:
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
                if ind == sumStep - 1:  # last command
                    ui.console.write("-"*20)
                    proc = subprocess.Popen(getSystemCommand(_cmd, self), cwd=self.workingDirectory,
                                            stdin=None if io[0] == "s" else open(
                                                path.getFileInputPath(self.workingDirectory), "r"),
                                            stdout=None if io[1] == "s" else open(path.getFileOutputPath(self.workingDirectory), "w"))
                else:
                    proc = subprocess.Popen(getSystemCommand(
                        _cmd, self), cwd=self.workingDirectory)

                isTimeout = False
                bg_time = time.time()
                try:
                    proc.communicate(timeout=timelimit)
                except subprocess.TimeoutExpired:
                    isTimeout = True
                    proc.terminate()
                ed_time = time.time()
                if ind == sumStep - 1:  # last command
                    ui.console.write("-"*20)
                ui.console.write(
                    "   ->", passf if proc.returncode == 0 else errf, f"{round((ed_time-bg_time)*1000)/1000}s")
                if proc.returncode != 0:
                    ui.console.write(
                        "(", color.useCyan(str(ind+1)), f"/{sumStep}) ", _cmd, " -> ", proc.returncode, split="", end=" ")
                    if isTimeout:
                        ui.console.write(color.useRed("Time out"))
                    else:
                        ui.console.write()
                    return False
        except BaseException:
            return False
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
              CONST_defaultTimeLimit: defaultData.timeLimit}

    with open(path.getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(config, indent=4))
