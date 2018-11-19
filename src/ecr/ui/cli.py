import color
import os
import platform
from enum import Enum


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


class CLI:
    def __init__(self):
        self.write = print
        self.read = input

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
