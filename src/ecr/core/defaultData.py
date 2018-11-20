from . import CIO_SISO

io = CIO_SISO
timeLimit = 5
editor = "vim"

executors = {
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

tempFileFilter = ["exe", "o", "class", "out"]

importedCommand = {
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

codeTemplate = {
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
