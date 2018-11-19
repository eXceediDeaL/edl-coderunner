import argparse
import sys
import io
import os
import platform
import codecs
import locale
import subprocess
import shlex
from enum import Enum
from prompt_toolkit.styles import Style
from .core import manager
from .ui import color, cli
from .ui.cli import console

version = "0.0.1.4"


class ReturnCode(Enum):
    OK = 0
    ERROR = -1
    UNLOADED = 1
    RUNERR = 2


cwd = None

man: manager.WorkManager = None

itParser = None


def loadMan():
    global man
    try:
        man = manager.load(cwd)
    except:
        man = None


def printHead():
    assert(man == None or man.state != manager.WorkManagerState.Empty)
    if man == None:
        console.write("ECR", end=" ")
    elif man.state == manager.WorkManagerState.Loaded:
        console.write(color.useGreen("ECR"), end=" ")
    elif man.state == manager.WorkManagerState.LoadFailed:
        console.write(color.useRed("ECR"), end=" ")
    console.write(cwd)


def assertInited()->bool:
    if man == None:
        console.error("Not have any ecr directory")
        return False
    return True


def init(args):
    global man
    manager.initialize(cwd)
    loadMan()
    printHead()
    return ReturnCode.OK if man != None else ReturnCode.UNLOADED


def now(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    man.currentFile = args.path
    return ReturnCode.OK


def new(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    man.newCode(args.filename)
    man.currentFile = args.filename
    return ReturnCode.OK


def run(args):
    if not assertInited():
        return ReturnCode.UNLOADED

    if args.file == None and man.currentFile == None:
        console.write("Please set file first")
        return ReturnCode.ERROR

    result = False

    result = man.execute(io=args.io, file=args.file)

    if not result:
        console.error("Running Failed")
        return ReturnCode.RUNERR
    return ReturnCode.OK


def clean(args):
    if not assertInited():
        return ReturnCode.UNLOADED
    man.clean()
    return ReturnCode.OK


def shutdown(args):
    exit(0)


def pwd(args):
    console.write(cwd)
    return ReturnCode.OK


def getVersion(args):
    console.write("edl-cr", version)
    return ReturnCode.OK


def cd(args):
    global man, cwd
    if not os.path.exists(args.path):
        console.error("No this directory")
        return ReturnCode.ERROR
    os.chdir(args.path)
    cwd = os.getcwd()
    printHead()
    if manager.hasInitialized(cwd):
        loadMan()
    return ReturnCode.OK


def clear(args):
    global man
    if not assertInited():
        return ReturnCode.UNLOADED
    if console.confirm("Do you want to clear ALL?", [cli.SwitchState.OK, cli.SwitchState.Cancel]) == cli.SwitchState.OK:
        manager.clear(man.workingDirectory)
        man = None
    return ReturnCode.OK


class BasicError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ITParser(argparse.ArgumentParser):
    def error(self, message):
        raise BasicError(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)


builtinCmdLists = ["init", "new", "now", "pwd",
                   "cd", "clear", "run", "clean", "version", "exit"]
cmdLists = None


def getITParser():
    parser = ITParser(
        prog="", description="Code Runner", add_help=True)

    subpars = parser.add_subparsers()

    cmd_init = subpars.add_parser("init", help="Initialize ECR data")
    cmd_init.set_defaults(func=init)

    cmd_new = subpars.add_parser("new", help="Create new code file")
    cmd_new.add_argument("filename")
    cmd_new.set_defaults(func=new)

    cmd_now = subpars.add_parser("now", help="Change current file")
    cmd_now.add_argument("path", nargs="?", default=None,
                         help="Set current file (clear for none)")
    cmd_now.set_defaults(func=now)

    cmd_pwd = subpars.add_parser("pwd", help="Print working directory")
    cmd_pwd.set_defaults(func=pwd)

    cmd_cd = subpars.add_parser("cd", help="Change working directory")
    cmd_cd.add_argument("path")
    cmd_cd.set_defaults(func=cd)

    cmd_clear = subpars.add_parser("clear", help="Clear ECR data")
    cmd_clear.set_defaults(func=clear)

    cmd_run = subpars.add_parser("run", help="Run code file")
    cmd_run.add_argument("-io", "--io", choices=manager.CIO_Types,
                         default=None, help="Change input and output")
    cmd_run.add_argument(
        "file", nargs="?", default=None, help="File name (only for this command)")
    cmd_run.set_defaults(func=run)

    cmd_clean = subpars.add_parser("clean", help="Clean temp files")
    cmd_clean.set_defaults(func=clean)

    cmd_version = subpars.add_parser("version", help="Get version")
    cmd_version.set_defaults(func=getVersion)

    # cmd_help = subpars.add_parser("help", help="Help")
    # cmd_help.set_defaults(func=gethelp)

    cmd_exit = subpars.add_parser("exit", help="Exit")
    cmd_exit.set_defaults(func=shutdown)

    return parser


def doSyscall(cmd, message):
    console.info(message, end=" ")
    console.write(cmd)
    retCode = os.system(manager.getSystemCommand(cmd, man))
    console.info(f"System command exited:", end=" ")
    if retCode == 0:
        console.write(retCode)
    else:
        console.error(retCode)
    return retCode


defaultPrompt = "> "


def mainInit():
    global itParser, cmdLists, cwd
    from prompt_toolkit import PromptSession
    from pygments.lexers.shell import BashLexer
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    itParser = getITParser()
    cwd = os.getcwd()

    if manager.hasInitialized(cwd):
        loadMan()

    cmdLists = list(builtinCmdLists)
    if man != None:
        cmdLists += man.importedCommand.keys()

    cliInputSession = PromptSession(
        message=defaultPrompt, lexer=PygmentsLexer(BashLexer), auto_suggest=AutoSuggestFromHistory())
    cli.console = cli.CLI(inputCommandSession=cliInputSession)


def executeCommand(oricmd):
    cargs = shlex.split(oricmd)
    if len(cargs) == 0:
        return
    if cargs[0].startswith(">"):
        return doSyscall(oricmd[1:], "Call system command:")
    else:
        try:
            cmd = itParser.parse_args(cargs)
        except BasicError as e:  # when parse failed, parser will call exit()
            if man != None and cargs[0] in man.importedCommand:
                return doSyscall(
                    f"{man.importedCommand[cargs[0]]} {' '.join(cargs[1:])}", "Imported command:")
            else:
                console.warning("We can't recognize this command:")
                console.write(f"  {e}")
                if console.confirm("Do you mean a system command?", [cli.SwitchState.Yes, cli.SwitchState.No]) == cli.SwitchState.Yes:
                    return doSyscall(oricmd, "Call system command:")
        else:
            if hasattr(cmd, "func"):
                return cmd.func(cmd).value
            else:
                return 0


def getCommandCompleter():
    from prompt_toolkit.completion import WordCompleter, merge_completers
    wc = WordCompleter(cmdLists, ignore_case=True)
    pc = cli.PathCompleter()
    return merge_completers([wc, pc])


def main():  # pragma: no cover
    global man, cwd, itParser

    baseParser = argparse.ArgumentParser(
        prog="ecr", description="Code Runner")
    baseParser.add_argument("-v", "--version", default=False, action="store_true",
                            help="Get version")
    baseParser.add_argument("-w", "--wdir", default=None,
                            help="Set working directory")
    baseParser.add_argument(
        "-c", "--command", default=None,  help="Execute command")
    baseCmd = baseParser.parse_args()
    if baseCmd.version:
        return getVersion(None).value
    if baseCmd.wdir != None:
        os.chdir(baseCmd.wdir)

    mainInit()

    if baseCmd.command != None:
        return executeCommand(baseCmd.command)

    printHead()
    while True:
        try:
            oricmd = str(console.inputCommand(
                f'{man.currentFile if man != None and man.currentFile != None else ""}{defaultPrompt}', completer=getCommandCompleter(), complete_in_thread=True))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        executeCommand(oricmd)

    return 0


def outmain():  # pragma: no cover
    exit(int(main()))


if __name__ == "__main__":  # pragma: no cover
    outmain()
