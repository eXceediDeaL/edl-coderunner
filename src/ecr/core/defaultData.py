from typing import List
from .types import ExecutorMapping, CommandMapping, CodeTemplateMapping, JudgerMapping

CIO_SISO: str = "ss"
CIO_SIFO: str = "sf"
CIO_FISO: str = "fs"
CIO_FIFO: str = "ff"
CIO_Types: List[str] = [CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO]

io: str = CIO_SISO
timeLimit: int = 10
editor: str = "vim"
judger: str = "diff"

executors: ExecutorMapping = {
    "c": ["gcc {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "cpp": ["g++ {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "java": ["javac {fileName}", "java {fileNameWithoutExt}"],
    "python": ["python {fileName}"],
    "pascal": ["fpc {fileName}", "./{fileNameWithoutExt}"],
    "objective-c": [
        "gcc -framework Cocoa {fileName} -o {fileNameWithoutExt}",
        "./{fileNameWithoutExt}"
    ],
    "javascript": ["node {fileName}"],
    "ruby": ["ruby {filename}"],
    "go": ["go run {filename}"],
    "shellscript": ["bash {filename}"],
    "powershell": ["powershell -ExecutionPolicy ByPass -File {filename}"]
}

judgers: JudgerMapping = {
    "diff": ["diff {expectFile} {realFile}"],
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

codeTemplate: CodeTemplateMapping = {
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
