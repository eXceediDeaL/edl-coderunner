from typing import Tuple, cast

from .. import shared, ui
from ..core import WorkItem, WorkItemType, WorkManager
from ..ui import color
from ..ui.command import Namespace


def printFileModify(file: str) -> None:
    console = ui.getConsole()
    console.write(color.useYellow("M"), file)


def printFileCreate(file: str) -> None:
    console = ui.getConsole()
    console.write(color.useGreen("+"), file)


def printFileDelete(file: str) -> None:
    console = ui.getConsole()
    console.write(color.useRed("-"), file)


def assertInited() -> bool:
    console = ui.getConsole()
    if not shared.getManager():
        console.error("Not have any ecr directory")
        return False
    return True


def getItem(tman: WorkManager, args: Namespace)->Tuple[WorkItem, str]:
    if args.file:
        item = tman.getWorkItem(
            args.file, args.dir)
    else:
        item = tman.getWorkItem(
            cast(WorkItem, tman.currentFile).name,
            cast(WorkItem, tman.currentFile).type == WorkItemType.Directory)
        tman.currentFile = item
    file = cast(WorkItem, item).name
    return cast(WorkItem, item), file
