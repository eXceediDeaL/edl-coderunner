from typing import Dict, List, Callable, Optional
from ..core.defaultData import CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO, CIO_Types


def runCommands(io: str, commands: List[str], variables: Dict[str, str], wdir: str, getSystemCommand: Callable[[str], str], inputFile: str, outputFile: str, defaultTimeLimit: Optional[int] = None, showLog: bool = True) -> bool:
    from ..core.manager import runCommands as internal_rc
    return internal_rc(io, commands, variables, wdir, getSystemCommand,
                       inputFile, outputFile, defaultTimeLimit, showLog)
