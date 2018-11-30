from ..ui.command import ReturnCode, Command, Namespace


class ExitCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        return ReturnCode.EXIT

    def __init__(self):
        super().__init__("exit", help="Exit", func=ExitCommand.default)
