from typing import cast

from . import cmd_now
from .. import shared, ui
from ..core import WorkItem, WorkManager
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited, printFileModify


class EditCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if not args.file and not tman.currentFile:
            console.write("Please set file first")
            return ReturnCode.ERROR
        if not args.file and not tman.currentFile:
            console.write("Please set file first")
            return ReturnCode.ERROR
        file = args.file if args.file else cast(
            WorkItem, tman.currentFile).name
        result = tman.edit(tman.getWorkItem(
            args.file, args.dir) if args.file else None)
        if result:
            printFileModify(file)
            if args.now:
                return cmd_now.NowCommand.default(Namespace(file=file, dir=args.dir))
            return ReturnCode.OK
        else:
            console.error(f"Editing file error {file}")
            return ReturnCode.ERROR

    def __init__(self):
        super().__init__("edit", help="Edit code file", func=EditCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument(
            "file", nargs="?", default=None, help="File name (only for this command)")
        cmd.add_argument("-n", "--now", action="store_true",
                         default=False, help="Set the file as current")
        cmd.add_argument("-d", "--dir", action="store_true",
                         default=False, help="As directory")
        return cmd
