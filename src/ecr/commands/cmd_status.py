from .. import shared, ui
from ..ui.command import Command, Namespace, ReturnCode


class StatusCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        if args.var:
            vs = shared.getVariables()
            nameLen = 10
            for k, v in vs.items():
                console.info(k.ljust(nameLen), end=" ")
                console.write(v)
        return ReturnCode.OK

    def __init__(self):
        super().__init__("status", help="Get status", func=StatusCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        cmd.add_argument("-v", "--var", action="store_true",
                         default=False, help="Show all variables")
        return cmd
