from .. import shared, ui
from ..ui.command import Command, Namespace, ReturnCode


class VersionCommand(Command):
    @staticmethod
    def default(args: Namespace)->ReturnCode:  # pylint: disable=W0613
        console = ui.getConsole()
        console.write("edl-cr", shared.getVersion())
        console.write("Copyright (C) eXceediDeal")
        console.write(
            "License Apache-2.0, Source https://github.com/eXceediDeaL/edl-coderunner")
        return ReturnCode.OK

    def __init__(self):
        super().__init__("version", help="Get version", func=VersionCommand.default)
