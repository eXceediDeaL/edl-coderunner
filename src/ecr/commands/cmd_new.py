from typing import cast

from . import cmd_edit
from .. import shared, ui
from ..core import WorkItem, WorkManager
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited, printFileCreate


class NewCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if not args.file and not tman.currentFile:
            console.write("Please set file first")
            return ReturnCode.ERROR
        file = args.file if args.file else cast(
            WorkItem, tman.currentFile).name
        result = tman.newCode(tman.getWorkItem(
            args.file, args.dir, renew=True) if args.file else None, args.template)

        if result:
            tman.currentFile = result
            tman.updateCurrent()
            printFileCreate(file)
            if args.edit:
                return cmd_edit.EditCommand.default(Namespace(file=file, now=False))
            return ReturnCode.OK
        else:
            console.error(f"Can't create file {file}")
            return ReturnCode.ERROR

    def __init__(self):
        super().__init__("new", help="Create new code file", func=NewCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("file", nargs="?", default=None, type=str)
        cmd.add_argument("-e", "--edit", action="store_true",
                         default=False, help="Edit the file")
        cmd.add_argument("-d", "--dir", action="store_true",
                         default=False, help="As directory")
        cmd.add_argument("-t", "--template", type=str,
                         default=None, help="Template name")
        return cmd
