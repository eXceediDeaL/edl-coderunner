CIO_SISO = "ss"
CIO_SIFO = "sf"
CIO_FISO = "fs"
CIO_FIFO = "ff"
CIO_Types = [CIO_SISO, CIO_SIFO, CIO_FISO, CIO_FIFO]

from .manager import WorkManager, WorkManagerState, hasInitialized, getSystemCommand
