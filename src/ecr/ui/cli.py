from enum import Enum
import click
from pygments.lexers.shell import BashLexer
from prompt_toolkit import prompt, print_formatted_text, PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.application import run_in_terminal
from . import color


class SwitchState(Enum):
    Yes = 0
    No = 1
    OK = 2
    Cancel = 3


confirmStrToSwitch = {
    "y": SwitchState.Yes,
    "n": SwitchState.No,
    "o": SwitchState.OK,
    "c": SwitchState.Cancel
}

switchToConfirmStr = {v: k for k, v in confirmStrToSwitch.items()}

defaultInputCommandSession = PromptSession(
    message="> ", lexer=PygmentsLexer(BashLexer), auto_suggest=AutoSuggestFromHistory())


class CLI:
    def __init__(self, inputCommandSession: PromptSession = None):
        self.read = prompt
        self.getProgressBar = ProgressBar
        self.inputCommandSession = inputCommandSession if inputCommandSession \
            else defaultInputCommandSession
        self.inputCommand = self.inputCommandSession.prompt
        self.edit = click.edit
        self.clear = click.clear

    def write(self, *values, **kwargs): # pylint: disable=R0201
        def func():
            print_formatted_text(*values, **kwargs)
        run_in_terminal(func)

    def info(self, message, end="\n"):
        self.write(color.useCyan(message), end=end)

    def warning(self, message, end="\n"):
        self.write(color.useYellow(message), end=end)

    def error(self, message, end="\n"):
        self.write(color.useRed(message), end=end)

    def ok(self, message, end="\n"):
        self.write(color.useGreen(message), end=end)

    def confirm(self, message, choice):  # pragma: no cover
        swstr = ','.join([switchToConfirmStr[x] for x in choice])
        ret = self.read(f"{message} ({swstr}) ")
        while ret not in confirmStrToSwitch or confirmStrToSwitch[ret] not in choice:
            ret = self.read(
                f"Not an acceptable value. Please input again ({swstr}): ")
        return confirmStrToSwitch[ret]
