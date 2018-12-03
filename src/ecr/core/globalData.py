from . import manager, path
from .. import log


def exists() -> bool:
    return manager.hasInitialized(path.getGlobalBasePath())


def initialize() -> None:
    log.info("Initialize global data.")
    manager.clear(path.getGlobalBasePath())
    manager.initialize(path.getGlobalBasePath())
