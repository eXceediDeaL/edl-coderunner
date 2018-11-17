import os
import json
import shutil
import subprocess
from colorama import Fore, Back, Style

fileextToLanguage = {
    "c": "c",
    "cpp": "cpp"
}
defaultExecutors = {
    "c": ["gcc {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "cpp": ["g++ {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"]
}


def getOIPath(basepath: str)->str:
    return os.path.join(basepath, ".oi")


def getExecutorPath(basepath: str) -> str:
    return os.path.join(getOIPath(basepath), "executor.json")


def hasInitialized(basepath: str)->bool:
    return os.path.exists(getOIPath(basepath))


class WorkManager:
    def __init__(self, path: str):
        self.workingDirectory: str = path
        self.executorMap: dict = {}
        self.currentFile: str = None

    def execute(self):
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
            for ind,cmd in enumerate(cmds):
                _cmd = cmd.format(**formats)
                print(f"({ind+1}/{sumStep})", _cmd)
                proc = subprocess.Popen(_cmd, cwd=self.workingDirectory)
                proc.communicate(timeout=5)
                if proc.returncode != 0:
                    print(f"{Fore.RED}Failed{Style.RESET_ALL} ({ind+1}/{sumStep})->", _cmd)
                    return False
        except Exception:
            return False


def load(basepath: str) -> WorkManager:
    if not hasInitialized(basepath):
        return None
    ret = WorkManager(basepath)
    with open(getExecutorPath(basepath), "r", encoding='utf-8') as f:
        ret.executorMap = json.loads(f.read())
    return ret


def initialize(basepath: str):
    oipath = getOIPath(basepath)
    if hasInitialized(basepath):
        shutil.rmtree(oipath)

    os.mkdir(oipath)
    executors = defaultExecutors
    with open(getExecutorPath(basepath), "w", encoding='utf-8') as f:
        f.write(json.dumps(executors, indent=4))
