import os
import sys
from ecr.lib.runner import runCommands, CIO_FIFO
from ecr.lib.console import info, error, write

dataPath = "./data"
timeLimit = 5
command = ""


def runOne(cmd, inputFile, outputFile, timelimit) -> bool:
    return runCommands(CIO_FIFO, [cmd], {}, os.getcwd(),
                       lambda s: s, inputFile, outputFile, timelimit, False)


def run():
    global command, timeLimit

    if len(sys.argv) < 3:
        print("No enough arguments")
        exit(-1)

    command = sys.argv[1]
    timeLimit = int(sys.argv[2])

    total = 0
    passed = 0
    for item in os.listdir(dataPath):
        inputFile = os.path.join(dataPath, item)
        if not os.path.isfile(inputFile):
            continue
        if not item.startswith("input"):
            continue
        total += 1
        name = os.path.splitext(item)[0].replace("input", "")
        outputFile = os.path.join(dataPath, item.replace("input", "output"))
        info(f"Running: {name}")
        result = runOne(command, inputFile, outputFile, timeLimit)
        if result:
            passed += 1
        else:
            error(f"Run case {name} failed.")
    info(f"Finished {passed} / {total}")


if __name__ == "__main__":
    run()
