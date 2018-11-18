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
CONST_defaultIO = "defaultIO"
CONST_defaultTimeLimit = "defaultTimeLimit"
CIO_SISO = "ss"
CIO_SIFO = "sf"
CIO_FISO = "fs"
CIO_FIFO = "ff"
CIO_Types = [CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO]

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

defaultIO = CIO_SISO

defaultTimeLimit = 5

defaultExecutors = {
    "c": ["gcc {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "cpp": ["g++ {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "java": ["javac {fileName}", "java {fileNameWithoutExt}"],
    "python": ["python -u {fileName}"],
    "pascal": ["fpc {fileName}", "./{fileNameWithoutExt}"],
    "objective-c": ["gcc -framework Cocoa {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "javascript": ["node {fileName}"],
    "ruby": ["ruby {filename}"],
    "go": ["go run {filename}"],
    "shellscript": ["bash {filename}"],
    "powershell": ["powershell -ExecutionPolicy ByPass -File {filename}"]
}

defaultTempFileFilter = ["exe", "o", "class", "out"]


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
} """,
    "java": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        
    }
}
""",
    "python": """def main():

    return 0

if __name__ == "__main__":
    exit(main())

""",
    "pascal": """program pro(Input, Output);
var

begin
    
end.
""",
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


def getFileInputPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "input.data")


def getFileOutputPath(basepath: str) -> str:
    return os.path.join(getMainPath(basepath), "output.data")


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
        self.defaultShell = None
        self.defaultIO = defaultIO
        self.defaultTimeLimit = defaultTimeLimit

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
            for ind, bcmd in enumerate(cmds):
                cmd, timelimit = None, None
                if not isinstance(bcmd, str):
                    cmd, timelimit = bcmd
                else:
                    cmd, timelimit = bcmd, self.defaultTimeLimit
                _cmd = cmd.format(**formats)
                print(
                    f"({color.useCyan(str(ind+1))}/{sumStep})", _cmd)
                proc = None
                if ind == sumStep - 1:  # last command
                    print("-"*20)
                    proc = subprocess.Popen(_cmd, cwd=self.workingDirectory,
                                            stdin=None if io[0] == "s" else open(
                                                getFileInputPath(self.workingDirectory), "r"),
                                            stdout=None if io[1] == "s" else open(getFileOutputPath(self.workingDirectory), "w"))
                else:
                    proc = subprocess.Popen(_cmd, cwd=self.workingDirectory)

                isTimeout = False
                bg_time = time.time()
                try:
                    proc.communicate(timeout=timelimit)
                except subprocess.TimeoutExpired:
                    isTimeout = True
                    proc.terminate()
                ed_time = time.time()
                if ind == sumStep - 1:  # last command
                    print("-"*20)
                print(
                    f"   -> {passf if proc.returncode == 0 else errf} {round((ed_time-bg_time)*1000)/1000}s")
                if proc.returncode != 0:
                    print(
                        f"({color.useRed(str(ind+1))}/{sumStep}) {_cmd} -> {proc.returncode}", end=" ")
                    if isTimeout:
                        print(color.useRed("Time out"))
                    return False
        except BaseException:
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
        ret.defaultShell = config[CONST_defaultShell]
        ret.defaultIO = config[CONST_defaultIO]
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

    open(getFileInputPath(basepath), "w").close()
    open(getFileOutputPath(basepath), "w").close()

    config = {CONST_tempFileFilter: defaultTempFileFilter,
              CONST_importedCommand: defaultImportedCommand,
              CONST_defaultShell: "powershell -c" if platform.system() == "Windows" else None,
              CONST_defaultIO: defaultIO,
              CONST_defaultTimeLimit: defaultTimeLimit}

    with open(getConfigPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(config, indent=4))
