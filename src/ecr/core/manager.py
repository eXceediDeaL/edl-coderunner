import os
import json
import shutil
import re
import subprocess
import time
import platform
try:
    from .ui import color
except:
    from ui import color

CONST_tempFileFilter = "tempFileFilter"
CONST_importedCommand = "importedCommand"
CONST_defaultShell = "defaultShell"

fileextToLanguage = {
    "c": "c",
    "cpp": "cpp",
    "py": "python",
    "java": "java",
}

languageToFileext = {v: k for k, v in fileextToLanguage.items()}

defaultExecutors = {
    "c": ["gcc {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "cpp": ["g++ {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "java": ["javac {fileName}", "java {fileNameWithoutExt}"],
    "python": ["python -u {fileName}"],
}

defaultTempFileFilter = ["exe", "o", "class"]


defaultImportedCommand = {
    "ls": "ls",
    "cls": "clear"
}

defaultCodeTemplate = {
    "c":
    """#include <stdio.h>
int main()
{
    return 0;
}""",
    "cpp":
    """#include <cstdio>
#include <cstdlib>
#include <iostream>
using namespace std;
int main()
{

    return EXIT_SUCCESS;
}""",
}

TEMPLATE_NAME = "base"


def getMainPath(basepath: str)->str:
    return os.path.join(basepath, ".ecr")


def getConfigPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "config.json")


def getExecutorPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "executor.json")


def getTemplatePath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "templates")


def hasInitialized(basepath: str)->bool:
    return os.path.exists(getMainPath(basepath))


def getFileExt(filename: str) -> str:
    return os.path.splitext(filename)[1][1:]


class WorkManager:
    def __init__(self, path: str):
        self.workingDirectory: str = path
        self.executorMap: dict = {}
        self.tempFileFilter: list = []
        self.currentFile: str = None
        self.importedCommand = {}
        self.defauleShell = None

    def newCode(self, filename):
        lang = fileextToLanguage[getFileExt(filename)]
        dstPath = os.path.join(self.workingDirectory, filename)
        tempPath = os.path.join(getTemplatePath(
            self.workingDirectory), f"{TEMPLATE_NAME}.{languageToFileext[lang]}")
        if os.path.exists(tempPath):
            shutil.copyfile(tempPath, dstPath)
        else:
            open(dstPath, "w").close()
        print(color.useGreen("+"), filename)

    def clean(self):
        for file in os.listdir(self.workingDirectory):
            for pat in self.tempFileFilter:
                try:
                    if pat == getFileExt(os.path.split(file)[-1]):
                        os.remove(file)
                        print(color.useRed("-"), file)
                        break
                except:
                    pass

    def execute(self):
        errf = color.useRed("×")
        passf = color.useGreen("√")
        try:
            fileNameWithoutExt, fileext = os.path.splitext(self.currentFile)

            lang = fileextToLanguage[fileext[1:]]
            cmds = self.executorMap[lang]
            formats = {
                "fileName": self.currentFile,
                "fileNameWithoutExt": fileNameWithoutExt,
                "dir": self.workingDirectory,
            }
            sumStep = len(cmds)
            for ind, cmd in enumerate(cmds):
                _cmd = cmd.format(**formats)
                print(
                    f"({color.useCyan(str(ind+1))}/{sumStep})", _cmd)
                proc = subprocess.Popen(_cmd, cwd=self.workingDirectory)
                bg_time = time.time()
                proc.communicate(timeout=5)
                ed_time = time.time()
                if proc.returncode != 0:
                    print(f"{errf} ({ind+1}/{sumStep})",
                          _cmd, "->", proc.returncode)
                    return False
                print(f"-> {passf} {round((ed_time-bg_time)*1000)/1000}s")
        except Exception:
            return False
        return True


def load(basepath: str) -> WorkManager:
    if not hasInitialized(basepath):
        return None
    ret = WorkManager(basepath)
    with open(getExecutorPath(basepath), "r", encoding='utf-8') as f:
        ret.executorMap = json.loads(f.read())

    with open(getConfigPath(basepath), "r", encoding='utf-8') as f:
        config = json.loads(f.read())
        ret.tempFileFilter = config[CONST_tempFileFilter]
        ret.importedCommand = config[CONST_importedCommand]
        ret.defauleShell = config[CONST_defaultShell]
    return ret


def clear(basepath: str):
    oipath = getMainPath(basepath)
    if hasInitialized(basepath):
        shutil.rmtree(oipath)


def initialize(basepath: str):
    clear(basepath)

    oipath = getMainPath(basepath)
    os.mkdir(oipath)

    templatePath = getTemplatePath(basepath)
    os.mkdir(templatePath)
    for k, v in defaultCodeTemplate.items():
        with open(os.path.join(templatePath, f"{TEMPLATE_NAME}.{languageToFileext[k]}"), "w", encoding='utf-8') as f:
            f.write(v)
    executors = defaultExecutors
    with open(getExecutorPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(executors, indent=4))

    config = {CONST_tempFileFilter: defaultTempFileFilter,
              CONST_importedCommand: defaultImportedCommand,
              CONST_defaultShell : "powershell -c" if platform.system() == "Windows" else None}

    with open(getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(config, indent=4))
