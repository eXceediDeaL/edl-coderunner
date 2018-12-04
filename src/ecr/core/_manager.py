from typing import Dict, List

from prompt_toolkit.application import run_in_terminal

fileextToLanguage: Dict[str, str] = {
    "c": "c",
    "cpp": "cpp",
    "cs": "csharp",
    "fs": "fsharp",
    "py": "python",
    "java": "java",
    "pas": "pascal",
    "m": "objective-c",
    "js": "javascript",
    "rb": "ruby",
    "go": "go",
    "php": "php",
    "sh": "shellscript",
    "ps1": "powershell",
}

languageToFileext: Dict[str, str] = {
    v: k for k, v in fileextToLanguage.items()}


def getSystemCommand(cmd: str, man=None) -> str:
    if not man or not man.defaultShell:
        return cmd
    else:
        return " ".join([man.defaultShell, f'"{cmd}"'])


def safeOutput(*values: List)->None:
    run_in_terminal(lambda: print(*values, end=""))
