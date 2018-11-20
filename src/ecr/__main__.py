import argparse
import sys
import io
import os
import platform
import shlex
from enum import Enum
from prompt_toolkit.styles import Style
from .core import manager, defaultData, CIO_Types, getSystemCommand
from .ui import color, cli, console
from .command import new, now, shutdown, run, getVersion, init, pwd, cd, clear, clean, cls, edit
from . import helper, shared, command, ReturnCode

itParser = None


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


builtinCmdLists = list(command.cmds)


def getITParser():
    parser = ITParser(
        prog="", description="Code Runner", add_help=True)

    subpars = parser.add_subparsers()

    cmd_init = subpars.add_parser("init", help="Initialize ECR data")
    cmd_init.set_defaults(func=init)

    cmd_clear = subpars.add_parser("clear", help="Clear ECR data")
    cmd_clear.set_defaults(func=clear)

    cmd_new = subpars.add_parser("new", help="Create new code file")
    cmd_new.add_argument("file", nargs="?", default=None, type=str)
    cmd_new.add_argument("-e", "--edit", action="store_true",
                         default=False, help="Edit the file")
    cmd_new.set_defaults(func=new)

    cmd_now = subpars.add_parser("now", help="Change current file")
    cmd_now.add_argument("file", nargs="?", default=None, type=str,
                         help="Set current file (clear for none)")
    cmd_now.set_defaults(func=now)

    cmd_run = subpars.add_parser("run", help="Run code file")
    cmd_run.add_argument("-io", "--io", choices=CIO_Types,
                         default=None, help="Change input and output")
    cmd_run.add_argument(
        "file", nargs="?", default=None, help="File name (only for this command)")
    cmd_run.set_defaults(func=run)

    cmd_edit = subpars.add_parser("edit", help="Edit code file")
    cmd_edit.add_argument(
        "file", nargs="?", default=None, help="File name (only for this command)")
    cmd_edit.add_argument("-n", "--now", action="store_true",
                          default=False, help="Set the file as current")
    cmd_edit.set_defaults(func=edit)

    cmd_clean = subpars.add_parser("clean", help="Clean temp files")
    cmd_clean.set_defaults(func=clean)

    cmd_pwd = subpars.add_parser("pwd", help="Print working directory")
    cmd_pwd.set_defaults(func=pwd)

    cmd_cd = subpars.add_parser("cd", help="Change working directory")
    cmd_cd.add_argument("path")
    cmd_cd.set_defaults(func=cd)

    cmd_version = subpars.add_parser("version", help="Get version")
    cmd_version.set_defaults(func=getVersion)

    # cmd_help = subpars.add_parser("help", help="Help")
    # cmd_help.set_defaults(func=gethelp)

    cmd_cls = subpars.add_parser("cls", help="Clear console")
    cmd_cls.set_defaults(func=cls)

    cmd_exit = subpars.add_parser("exit", help="Exit")
    cmd_exit.set_defaults(func=shutdown)

    return parser


def doSyscall(cmd, message):
    console.info(message, end=" ")
    console.write(cmd)
    retCode = os.system(getSystemCommand(cmd, shared.man))
    console.info(f"System command exited:", end=" ")
    if retCode == 0:
        console.write(retCode)
    else:
        console.error(retCode)
    return retCode


defaultPrompt = "> "


def mainInit():
    global itParser
    from prompt_toolkit import PromptSession
    from pygments.lexers.shell import BashLexer
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    itParser = getITParser()
    shared.cwd = os.getcwd()

    if manager.hasInitialized(shared.cwd):
        helper.loadMan()

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
            importedCommand = shared.man.importedCommand if shared.man != None else defaultData.importedCommand
            if cargs[0] in importedCommand:
                return doSyscall(
                    f"{importedCommand[cargs[0]]} {' '.join(cargs[1:])}", "Imported command:")
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
    cmdLists = list(builtinCmdLists)
    if shared.man != None:
        cmdLists += shared.man.importedCommand.keys()
    else:
        cmdLists += defaultData.importedCommand
    wc = WordCompleter(cmdLists, ignore_case=True)
    pc = cli.PathCompleter()
    return merge_completers([wc, pc])


def main():  # pragma: no cover
    global itParser

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

    helper.printHead()
    while True:
        try:
            oricmd = str(console.inputCommand(
                f'{shared.man.currentFile if shared.man != None and shared.man.currentFile != None else ""}{defaultPrompt}', completer=getCommandCompleter(), complete_in_thread=False))
            oricmd = helper.formatWithVars(oricmd, shared.variables)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        if executeCommand(oricmd) == ReturnCode.EXIT.value:
            break
    
    return 0


def outmain():  # pragma: no cover
    sys.exit(int(main()))


if __name__ == "__main__":  # pragma: no cover
    outmain()
