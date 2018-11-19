import color
import os
import platform
from prompt_toolkit import prompt, print_formatted_text, HTML, PromptSession
from pygments.lexers.shell import BashLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import ProgressBar
from enum import Enum


class PathCompleter(Completer):
    """
    Complete for Path variables.

    :param get_paths: Callable which returns a list of directories to look into
                      when the user enters a relative path.
    :param file_filter: Callable which takes a filename and returns whether
                        this file should show up in the completion. ``None``
                        when no filtering has to be done.
    :param min_input_len: Don't do autocompletion when the input string is shorter.
    """

    def __init__(self, only_directories=False, get_paths=None, file_filter=None,
                 min_input_len=0, expanduser=False):
        assert get_paths is None or callable(get_paths)
        assert file_filter is None or callable(file_filter)
        assert isinstance(min_input_len, int)
        assert isinstance(expanduser, bool)

        self.only_directories = only_directories
        self.get_paths = get_paths or (lambda: ['.'])
        self.file_filter = file_filter or (lambda _: True)
        self.min_input_len = min_input_len
        self.expanduser = expanduser

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.split()[-1]

        # Complete only when we have at least the minimal input length,
        # otherwise, we can too many results and autocompletion will become too
        # heavy.
        if len(text) < self.min_input_len:
            return

        try:
            # Do tilde expansion.
            if self.expanduser:
                text = os.path.expanduser(text)

            # Directories where to look.
            dirname = os.path.dirname(text)
            if dirname:
                directories = [os.path.dirname(os.path.join(p, text))
                               for p in self.get_paths()]
            else:
                directories = self.get_paths()

            # Start of current file.
            prefix = os.path.basename(text)

            # Get all filenames.
            filenames = []
            for directory in directories:
                # Look for matches in this directory.
                if os.path.isdir(directory):
                    for filename in os.listdir(directory):
                        if filename.startswith(prefix):
                            filenames.append((directory, filename))

            # Sort
            filenames = sorted(filenames, key=lambda k: k[1])

            # Yield them.
            for directory, filename in filenames:
                completion = filename[len(prefix):]
                full_name = os.path.join(directory, filename)

                if os.path.isdir(full_name):
                    # For directories, add a slash to the filename.
                    # (We don't add them to the `completion`. Users can type it
                    # to trigger the autocompletion themselves.)
                    filename += '/'
                elif self.only_directories:
                    continue

                if not self.file_filter(full_name):
                    continue

                yield Completion(completion, 0, display=filename)
        except OSError:
            pass


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
        self.write = print_formatted_text
        self.read = prompt
        self.getProgressBar = ProgressBar
        self.inputCommandSession = inputCommandSession if inputCommandSession != None else defaultInputCommandSession
        self.inputCommand = self.inputCommandSession.prompt

    def clear(self):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

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
        self.write(message, f"({swstr})", end=" ")
        ret = self.read()
        while ret not in confirmStrToSwitch or confirmStrToSwitch[ret] not in choice:
            self.write(
                f"Not an acceptable value. Please input again ({swstr}):", end=" ")
            ret = self.read()
        return confirmStrToSwitch[ret]


console = CLI()
