from .. import shared
from ..helper import loadMan, printHead
from ..ui.command import Command, Namespace, ReturnCode


class ReloadCommand(Command):
    @staticmethod
    def default(args: Namespace) -> ReturnCode:  # pylint: disable=W0613
        if args.current:
            man = shared.getManager()
            if man:
                man.updateCurrent()
            return ReturnCode.OK
        else:
            loadMan()
            printHead()
            return ReturnCode.OK if shared.getManager() else ReturnCode.UNLOADED

    def __init__(self):
        super().__init__("reload", help="Reload ECR data", func=ReloadCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-c", "--current", action="store_true",
                         default=False, help="Reload current workitem")
        return cmd
