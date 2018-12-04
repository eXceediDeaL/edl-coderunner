from typing import cast
import os
import shutil

from .. import shared, ui, template
from ..core import path as ecrpath
from ..core import WorkManager
from ..ui import SwitchState
from ..ui.command import Command, Namespace, ReturnCode
from .helper import assertInited, printFileCreate, printFileDelete


class TemplateCommand(Command):
    @staticmethod
    def default(args: Namespace) -> ReturnCode:  # pylint: disable=W0613
        if not assertInited():
            return ReturnCode.UNLOADED
        return ReturnCode.OK

    @staticmethod
    def new(args: Namespace) -> ReturnCode:
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        template.initialize(os.path.join(
            ecrpath.getTemplatePath(tman.workingDirectory), args.name))
        printFileCreate(args.name)
        return ReturnCode.OK

    @staticmethod
    def clear(args: Namespace) -> ReturnCode:
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if console.confirm(f"Do you want to clear template config of `{args.name}`?",
                           [SwitchState.Yes, SwitchState.No]) == SwitchState.Yes:
            template.clear(os.path.join(ecrpath.getTemplatePath(
                tman.workingDirectory), args.name))
        return ReturnCode.OK

    @staticmethod
    def remove(args: Namespace) -> ReturnCode:
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if console.confirm(f"Do you want to remove template `{args.name}`?",
                           [SwitchState.Yes, SwitchState.No]) == SwitchState.Yes:
            shutil.rmtree(os.path.join(ecrpath.getTemplatePath(
                tman.workingDirectory), args.name))
            printFileDelete(args.name)
        return ReturnCode.OK

    @staticmethod
    def showTemplate(basepath)->None:
        tem, exp = template.load(basepath)
        console = ui.getConsole()
        if exp:
            console.error(f"Loading template failed: {exp}")
        else:
            import json
            if tem:
                console.write(json.dumps(
                    tem.__dict__, default=str, indent=4))
            else:
                console.write("None")

    @staticmethod
    def show(args: Namespace) -> ReturnCode:
        if not assertInited():
            return ReturnCode.UNLOADED
        tman: WorkManager = cast(WorkManager, shared.getManager())
        console = ui.getConsole()
        if args.name:
            tpath = os.path.join(
                ecrpath.getTemplatePath(tman.workingDirectory), args.name)
            if os.path.isdir(tpath):
                TemplateCommand.showTemplate(tpath)
                return ReturnCode.OK
            else:
                console.write("No this template.")
                return ReturnCode.OK
        else:
            basepath = ecrpath.getTemplatePath(tman.workingDirectory)
            for item in os.listdir(basepath):
                itempath = os.path.join(basepath, item)
                if os.path.isfile(itempath):
                    continue
                console.info(item)
                TemplateCommand.showTemplate(itempath)
            return ReturnCode.OK

    def __init__(self):
        super().__init__("template", help="Tools for templates", func=TemplateCommand.default)

    def createParser(self, parsers):
        cmd = super().createParser(parsers)
        subpars = cmd.add_subparsers()

        cmd_new = subpars.add_parser("new", help="Create new template")
        cmd_new.add_argument("name", type=str, help="Template name")
        cmd_new.set_defaults(func=TemplateCommand.new)

        cmd_clear = subpars.add_parser("clear", help="Clear template config")
        cmd_clear.add_argument("name", type=str, help="Template name")
        cmd_clear.set_defaults(func=TemplateCommand.clear)

        cmd_remove = subpars.add_parser("remove", help="Remove template")
        cmd_remove.add_argument("name", type=str, help="Template name")
        cmd_remove.set_defaults(func=TemplateCommand.remove)

        cmd_show = subpars.add_parser("show", help="Show template config")
        cmd_show.add_argument("name", nargs="?", default=None,
                              type=str, help="Template name (empty to show all)")
        cmd_show.set_defaults(func=TemplateCommand.show)
        return cmd
