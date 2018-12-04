import os
import platform
import shutil
import subprocess
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, cast

import click
import yaml

from ._manager import getSystemCommand, fileextToLanguage, languageToFileext
from ._WorkItem import WorkItem, WorkItemType, loadCodeDirectory, initializeCodeDirectory
from ._Runner import Runner, RunResult
from . import defaultData
from . import path as ecrpath
from .. import log, ui
from ..ui import color
from ..types import CommandList, CommandMapping, ExecutorMapping, JudgerMapping, CodeTemplateMapping

CONST_tempFileFilter: str = "tempFileFilter"
CONST_importedCommand: str = "importedCommand"
CONST_defaultShell: str = "defaultShell"
CONST_defaultIO: str = "defaultIO"
CONST_defaultTimeLimit: str = "defaultTimeLimit"
CONST_defaultEditor: str = "defaultEditor"
CONST_defaultJudger: str = "defaultJudger"
CONST_eVersion: str = "eVersion"


def hasInitialized(basepath: str)->bool:
    return os.path.exists(ecrpath.getMainPath(basepath))


class WorkManagerState(Enum):
    Empty: int = 0
    Loaded: int = 1
    LoadedFromGlobal: int = 2
    LoadFailed: int = 3


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
        self.defaultTemplate: CodeTemplateMapping = defaultData.templates
        self.state: WorkManagerState = WorkManagerState.Empty
        self.runner: Optional[Runner] = None
        self.defaultEditor: Optional[str] = None
        from . import __version__
        self.eVersion: str = __version__

    def getConfigPath(self) -> str:
        if self.state == WorkManagerState.LoadedFromGlobal:
            return ecrpath.getGlobalBasePath()
        else:
            return self.workingDirectory

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
            return self.currentFile is not None
        return True

    def updateCurrent(self)->None:
        newCur = None
        if self.currentFile:
            newCur = self.getWorkItem(
                self.currentFile.name, self.currentFile.type == WorkItemType.Directory)
        self.currentFile = newCur

    def newCode(self, item: Optional[WorkItem] = None, template: Optional[str] = None) -> Optional[WorkItem]:
        try:
            if not item:
                item = self.currentFile
            assert item
            dstPath = os.path.join(self.workingDirectory, item.name)
            tempPath = None
            if item.type == WorkItemType.Directory:
                if os.path.isdir(dstPath):
                    shutil.rmtree(dstPath)
                if not template:
                    template = self.defaultTemplate["dir"] if "dir" in self.defaultTemplate else None
                if template:
                    tempPath = os.path.join(ecrpath.getTemplatePath(
                        self.getConfigPath()), f"{template}")
                if tempPath:
                    if os.path.isdir(tempPath):
                        shutil.copytree(tempPath, dstPath)
                    else:
                        log.warning(
                            f"Template directory not found: {tempPath}")
                        os.mkdir(dstPath)
                        initializeCodeDirectory(dstPath)
                else:
                    os.mkdir(dstPath)
                    initializeCodeDirectory(dstPath)
            else:
                ext = ecrpath.getFileExt(item.name)
                lang = fileextToLanguage[ext] if ext in fileextToLanguage else None
                tempPath = None
                if lang:
                    if not template:
                        template = self.defaultTemplate[lang] if lang in self.defaultTemplate else None
                    if template:
                        tempPath = os.path.join(ecrpath.getTemplatePath(
                            self.getConfigPath()), f"{template}.{languageToFileext[lang]}")
                if tempPath:
                    if os.path.isfile(tempPath):
                        shutil.copyfile(tempPath, dstPath)
                    else:
                        log.warning(f"Template file not found: {tempPath}")
                        open(dstPath, "w").close()
                else:
                    open(dstPath, "w").close()
            return item
        except:
            log.errorWithException(
                f"Create workitem({item.type if item else None}) failed: {item.name if item else None}")
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
            log.errorWithException(
                f"Edit workitem({titem.type}) failed: {titem.name}")
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
                    log.warning(f"Clean failed: {pat}", exc_info=True)

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
                rcmd = getSystemCommand(_cmd, self)
                if ind == sumStep - 1:  # last command
                    if io[0] == "s":  # stdin
                        timelimit = None
                    console.write("-"*20)
                    proc = subprocess.Popen(
                        rcmd,
                        cwd=cwd,
                        stdin=None if io[0] == "s"
                        else open(ecrpath.getFileInputPath(self.getConfigPath()), "r"),
                        stdout=None if io[1] == "s"
                        else open(ecrpath.getFileOutputPath(self.getConfigPath()), "w"),
                        stderr=None)
                else:
                    proc = subprocess.Popen(
                        rcmd,
                        cwd=cwd,
                        stdin=None, stdout=None, stderr=None)

                self.runner = Runner(proc=proc, io=io, timelimit=timelimit)
                rresult, retcode = self.runner.run()
            except BaseException:
                log.errorWithException(f"Run command failed: {rcmd}")
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
                defaultData.CMDVAR_FileName: file,
                defaultData.CMDVAR_FileNameWithoutExt: fileNameWithoutExt,
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
                defaultData.CMDVAR_JudgerDir: ecrpath.getJudgerPath(self.getConfigPath()),
                defaultData.CMDVAR_ExpectFile: ecrpath.getFileStdPath(self.getConfigPath()),
                defaultData.CMDVAR_RealFile: ecrpath.getFileOutputPath(self.getConfigPath()),
            }

            console.info(f"Judging {titem.name}")
            return self.__runCommands(defaultData.CIO_SISO, cmds, formats)
        else:  # directory
            cmds = titem.test
            formats = {
                defaultData.CMDVAR_JudgerDir: ecrpath.getJudgerPath(self.getConfigPath()),
                defaultData.CMDVAR_ExpectFile: ecrpath.getFileStdPath(self.getConfigPath()),
                defaultData.CMDVAR_RealFile: ecrpath.getFileOutputPath(self.getConfigPath()),
            }

            console.info(f"Judging {titem.name}")
            if cmds:
                return self.__runCommands(defaultData.CIO_SISO, cmds, formats, wdir=titem.path)
            else:
                return True


def loadFrom(basepath: str) -> Tuple[Optional[WorkManager], Optional[Exception]]:
    if not hasInitialized(basepath):
        return None, None
    ret = WorkManager(basepath)
    exp = None
    try:
        with open(ecrpath.getExecutorPath(basepath), "r", encoding='utf-8') as f:
            ret.executorMap = yaml.load(f.read())

        with open(ecrpath.getJudgerConfigPath(basepath), "r", encoding='utf-8') as f:
            ret.judgerMap = yaml.load(f.read())

        with open(ecrpath.getTemplateConfigPath(basepath), "r", encoding='utf-8') as f:
            ret.defaultTemplate = yaml.load(f.read())

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
    except Exception as e:
        log.errorWithException(f"Loading ecr data failed from {basepath}")
        ret.state = WorkManagerState.LoadFailed
        exp = e
    return ret, exp


def load(basepath: str) -> Tuple[Optional[WorkManager], Optional[Exception]]:
    if hasInitialized(basepath):
        ret, exp = loadFrom(basepath)
    else:
        log.info("Load from global data")
        ret, exp = loadFrom(ecrpath.getGlobalBasePath())
        if ret:
            if ret.state == WorkManagerState.Loaded:
                ret.state = WorkManagerState.LoadedFromGlobal
            ret.workingDirectory = basepath
    return ret, exp


def clear(basepath: str)->None:
    oipath = ecrpath.getMainPath(basepath)
    if hasInitialized(basepath):
        log.debug(f"Clear ecr data at {basepath}")
        shutil.rmtree(oipath)


def initialize(basepath: str)->None:
    clear(basepath)

    log.debug(f"Initialize ecr data at {basepath}")

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

    templates = defaultData.templates
    with open(ecrpath.getTemplateConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(yaml.dump(templates, indent=4,
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
