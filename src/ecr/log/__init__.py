import logging
from typing import List, Dict
from prompt_toolkit import HTML

LOG_FORMAT = "#%(levelname)s|%(asctime)s|%(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"


class LogListHandler(logging.Handler):
    def __init__(self, data: List[str]):
        super().__init__()
        self.data = data

    def flush(self):
        self.acquire()
        try:
            pass
        finally:
            self.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.data.append(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def initializeLogger(data: List[str], level=logging.INFO)->None:
    logging.basicConfig(level=level,
                        handlers=[LogListHandler(data)], format=LOG_FORMAT)


levelToStyle: Dict[str, str] = {
    "DEBUG": 'fg="ansigreen"',
    "INFO": 'fg="ansicyan"',
    "WARNING": 'fg="ansiyellow"',
    "ERROR": 'fg="ansired"',
    "CRITICAL": 'fg="ansired"',
}


def colored(msg: str) -> HTML:
    if not msg.startswith("#"):
        return HTML(HTML(f'<obj>{msg}</obj>'))
    spl = msg[1:].split('|')
    bg, tme, data = spl[0], spl[1], "|".join(spl[2:])
    output = f'<obj {levelToStyle[bg]}>{bg}</obj> <obj fg="ansiblue">{tme}</obj> <obj>{data}</obj> '
    return HTML(output)


info = logging.info
debug = logging.debug
warning = logging.warning
error = logging.error
critical = logging.critical


def errorWithException(msg, *args):
    error(msg, *args, exc_info=True)
