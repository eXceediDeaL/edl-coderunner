from typing import List

from ..ui.command import Command
from .cmd_cd import CdCommand
from .cmd_clean import CleanCommand
from .cmd_clear import ClearCommand
from .cmd_cls import ClsCommand
from .cmd_debug import DebugCommand
from .cmd_edit import EditCommand
from .cmd_exit import ExitCommand
from .cmd_init import InitCommand
from .cmd_new import NewCommand
from .cmd_now import NowCommand
from .cmd_pwd import PwdCommand
from .cmd_reload import ReloadCommand
from .cmd_run import RunCommand
from .cmd_status import StatusCommand
from .cmd_template import TemplateCommand
from .cmd_test import TestCommand
from .cmd_version import VersionCommand

commands: List[Command] = [
    CdCommand(), CleanCommand(), ClearCommand(), ClsCommand(),
    DebugCommand(),
    EditCommand(), ExitCommand(),
    InitCommand(),
    NewCommand(), NowCommand(),
    PwdCommand(),
    ReloadCommand(), RunCommand(),
    StatusCommand(),
    TemplateCommand(), TestCommand(),
    VersionCommand(),
]

commandVerbs: List[str] = [x.verb for x in commands]
