from typing import List

from ..types import CommandMapping, ExecutorMapping, JudgerMapping, CodeTemplateMapping

CIO_SISO: str = "ss"
CIO_SIFO: str = "sf"
CIO_FISO: str = "fs"
CIO_FIFO: str = "ff"
CIO_Types: List[str] = [CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO]

io: str = CIO_SISO
timeLimit: int = 10
editor: str = "vim"
judger: str = "text"

CMDVAR_FileName: str = "fileName"
CMDVAR_FileNameWithoutExt: str = "fileNameWithoutExt"
CMDVAR_JudgerDir: str = "judgerDir"
CMDVAR_ExpectFile: str = "expectFile"
CMDVAR_RealFile: str = "realFile"


executors: ExecutorMapping = {
    "c": [
        f"gcc -O2 -Wall -std=c11 {{{CMDVAR_FileName}}} -o {{{CMDVAR_FileNameWithoutExt}}} -lm",
        f"./{{{CMDVAR_FileNameWithoutExt}}}"
    ],
    "cpp": [
        f"g++ -O2 -Wall -std=c++14 {{{CMDVAR_FileName}}} -o {{{CMDVAR_FileNameWithoutExt}}} -lm",
        f"./{{{CMDVAR_FileNameWithoutExt}}}"
    ],
    "java": [
        f"javac -encoding utf8 {{{CMDVAR_FileName}}}",
        f"java {{{CMDVAR_FileNameWithoutExt}}}"
    ],
    "python": [f"python {{{CMDVAR_FileName}}}"],
    "pascal": [
        f"fpc -O2 {{{CMDVAR_FileName}}} -o {{{CMDVAR_FileNameWithoutExt}}}",
        f"./{{{CMDVAR_FileNameWithoutExt}}}"
    ],
    "objective-c": [
        f"gcc -O2 -Wall -framework Cocoa {{{CMDVAR_FileName}}} -o {{{CMDVAR_FileNameWithoutExt}}}",
        f"./{{{CMDVAR_FileNameWithoutExt}}}"
    ],
    "javascript": [f"node {{{CMDVAR_FileName}}}"],
    "ruby": [f"ruby {{{CMDVAR_FileName}}}"],
    "go": [f"go run {{{CMDVAR_FileName}}}"],
    "php": [f"php {{{CMDVAR_FileName}}}"],
    "shellscript": [f"bash {{{CMDVAR_FileName}}}"],
    "powershell": [f"powershell -ExecutionPolicy ByPass -File {{{CMDVAR_FileName}}}"]
}

judgers: JudgerMapping = {
    "text": [
        f"python -u {{{CMDVAR_JudgerDir}}}/text.py {{{CMDVAR_ExpectFile}}} {{{CMDVAR_RealFile}}}"
    ],
}

templates: CodeTemplateMapping = {
    "c": "base",
    "cpp": "base",
    "csharp": "base",
    "fsharp": "base",
    "go": "base",
    "java": "base",
    "pascal": "base",
    "python": "base",
    "dir": "base",
}

tempFileFilter: List[str] = ["exe", "o", "class", "out"]

importedCommand: CommandMapping = {
    "ls": "ls",
    "dir": "dir",
    "cat": "cat",
    "mkdir": "mkdir",
    "echo": "echo",
    "copy": "copy",
    "cp": "cp",
    "del": "del",
    "diff": "diff",
    "move": "move",
    "mv": "mv",
    "rm": "rm",
    "rmdir": "rmdir",
    "gcc": "gcc",
    "g++": "g++",
    "java": "java",
    "javac": "javac",
    "python": "python",
    "fpc": "fpc",
    "node": "node",
    "ruby": "ruby",
    "go": "go",
    "bash": "bash",
    "powershell": "powershell",
    "git": "git",
    "vim": "vim",
    "vi": "vi",
    "gdb": "gdb",
    "sh": "sh",
    "ps": "ps",
    "kill": "kill",
    "date": "date",
    "man": "man",
    "make": "make",
}
