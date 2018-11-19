CIO_SISO = "ss"
CIO_SIFO = "sf"
CIO_FISO = "fs"
CIO_FIFO = "ff"
CIO_Types = [CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO]

defaultIO = CIO_SISO

defaultTimeLimit = 5

defaultExecutors = {
    "c": ["gcc {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "cpp": ["g++ {fileName} -o {fileNameWithoutExt}", "./{fileNameWithoutExt}"],
    "java": ["javac {fileName}", "java {fileNameWithoutExt}"],
    "python": ["python {fileName}"],
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
    "dir": "dir",
    "cls": "clear",
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
    "gdb": "gdb",
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
