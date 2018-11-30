from argparse import ArgumentParser, Namespace
import sys
import os
import shlex
from typing import List, NoReturn
import prompt_toolkit
from .core import manager, defaultData, getSystemCommand
from . import helper, shared, commands, ui


itParser: ArgumentParser = ArgumentParser()


class BasicError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class ITParser(ArgumentParser):
    def error(self, message):
        raise BasicError(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)


builtinCmdLists: List[str] = list(commands.commandVerbs)


def getITParser()->ITParser:
    parser = ITParser(
        prog="", description="Code Runner", add_help=True)

    subpars = parser.add_subparsers()

    for cmd in commands.commands:
        cmd.createParser(subpars)

    # cmd_help = subpars.add_parser("help", help="Help")
    # cmd_help.set_defaults(func=gethelp)

    return parser


def doSyscall(cmd, message) -> int:
    console = ui.getConsole()
    console.info(message, end=" ")
    console.write(cmd)
    retCode = os.system(getSystemCommand(cmd, shared.getManager()))
    console.info(f"System command exited:", end=" ")
    if retCode == 0:
        console.write(retCode)
    else:
        console.error(retCode)
    return retCode


defaultPrompt = "> "


def mainInit()->None:
    global itParser
    from prompt_toolkit import PromptSession
    from pygments.lexers.shell import BashLexer
    from prompt_toolkit.lexers import PygmentsLexer
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    itParser = getITParser()
    shared.setCwd(os.getcwd())

    if manager.hasInitialized(shared.getCwd()):
        helper.loadMan()

    cliInputSession = PromptSession(
        message=defaultPrompt,
        lexer=PygmentsLexer(BashLexer),
        auto_suggest=AutoSuggestFromHistory())

    ui.setConsole(ui.CLI(inputCommandSession=cliInputSession))


def executeCommand(oricmd: str) -> int:
    console = ui.getConsole()
    cargs = shlex.split(oricmd)
    if not cargs:
        return 0
    if cargs[0].startswith(">"):
        return doSyscall(oricmd[1:], "Call system command:")
    else:
        try:
            cmd = itParser.parse_args(cargs)
        except BasicError as e:  # when parse failed, parser will call exit()
            man = shared.getManager()
            importedCommand = man.importedCommand if man \
                else defaultData.importedCommand
            if cargs[0] in importedCommand:
                return doSyscall(
                    f"{importedCommand[cargs[0]]} {' '.join(cargs[1:])}", "Imported command:")
            else:
                console.warning("We can't recognize this command:")
                console.write(f"  {e}")
                if console.confirm("Do you mean a system command?",
                                   [ui.SwitchState.Yes, ui.SwitchState.No])\
                        == ui.SwitchState.Yes:
                    return doSyscall(oricmd, "Call system command:")
        else:
            if hasattr(cmd, "func"):
                return cmd.func(cmd).value
    return 0


def getCommandCompleter()->prompt_toolkit.completion.Completer:
    from prompt_toolkit.completion import WordCompleter, merge_completers
    cmdLists = list(builtinCmdLists)
    man = shared.getManager()
    if man:
        cmdLists += man.importedCommand.keys()
    else:
        cmdLists += defaultData.importedCommand
    wc = WordCompleter(cmdLists, ignore_case=True)
    pc = ui.PathCompleter()
    return merge_completers([wc, pc])


def main()->int:  # pragma: no cover
    global itParser

    baseParser = ArgumentParser(
        prog="ecr", description="Code Runner")
    baseParser.add_argument("-v", "--version", default=False, action="store_true",
                            help="Get version")
    baseParser.add_argument("-d", "--dir", default=None,
                            help="Set working directory")
    baseParser.add_argument(
        "-c", "--command", default=None, help="Execute command")
    baseCmd = baseParser.parse_args()
    if baseCmd.version:
        return commands.VersionCommand.default(Namespace()).value
    if baseCmd.dir:
        os.chdir(baseCmd.dir)

    mainInit()

    if baseCmd.command:
        return executeCommand(baseCmd.command)

    helper.printHead()
    while True:
        try:
            curfile = ""
            man = shared.getManager()
            console = ui.getConsole()
            if man and man.currentFile:
                if man.currentFile.type == manager.WorkItemType.File:
                    curfile = man.currentFile.name
                else:
                    curfile = "@" + man.currentFile.name
            oricmd = str(console.inputCommand(
                curfile + defaultPrompt,
                completer=getCommandCompleter(), complete_in_thread=False))
            oricmd = helper.formatWithVars(oricmd, shared.getVariables())
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        if executeCommand(oricmd) == ui.command.ReturnCode.EXIT.value:
            break
    return 0


def outmain() -> NoReturn:  # pragma: no cover
    sys.exit(int(main()))


if __name__ == "__main__":  # pragma: no cover
    outmain()
