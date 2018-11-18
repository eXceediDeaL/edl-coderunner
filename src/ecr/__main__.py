import argparse
import sys
import io
import os
import platform

try:  # for run with module
    from .core import manager
    from .ui import color, cli
except:
    try:  # for run with only __main__.py
        # from core import manager
        # from ui import color, cli
        pass
    except:
        print("Import failed")


cwd = None

man: manager.WorkManager = None

itParser = None
console = cli.CLI()


def loadMan():
    global man
    try:
        man = manager.load(cwd)
    except:
        man = None
        console.error("ECR Loading Failed")


def printHead():
    if man != None:
        console.write(color.useGreen("ECR "), end="")
    else:
        console.write("ECR ", end="")
    console.write(cwd)


def assertInited()->bool:
    if man == None:
        console.error("Not have any ecr directory")
        return False
    return True


def init(args):
    global man
    manager.initialize(cwd)
    loadMan()
    printHead()


def now(args):
    if not assertInited():
        return
    man.currentFile = args.path


def new(args):
    if not assertInited():
        return
    man.newCode(args.filename)
    man.currentFile = args.filename


def run(args):
    if not assertInited():
        return
    if man.currentFile == None:
        console.write("Please set current file first")
        return
    if not man.execute():
        console.error("Running Failed")


def clean(args):
    if not assertInited():
        return
    man.clean()


def shutdown(args):
    exit(0)


def pwd(args):
    print(cwd)


def cd(args):
    global man, cwd
    if not os.path.exists(args.path):
        console.error("No this directory")
    os.chdir(args.path)
    cwd = os.getcwd()
    printHead()
    if manager.hasInitialized(cwd):
        loadMan()


def clear(args):
    global man
    if not assertInited():
        return
    if console.confirm("Do you want to clear ALL?", [cli.SwitchState.OK, cli.SwitchState.Cancel]) == cli.SwitchState.OK:
        manager.clear(man.workingDirectory)
        man = None


def gethelp(args):
    console.write(itParser.format_help())


class BasicError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ITParser(argparse.ArgumentParser):
    def error(self, message):
        raise BasicError(message)


def getITParser():
    parser = ITParser(
        prog="", description="Code Runner", add_help=False)

    subpars = parser.add_subparsers()

    cmd_init = subpars.add_parser("init", help="Initialize ecr")
    cmd_init.set_defaults(func=init)

    cmd_new = subpars.add_parser("new", help="Create new code file")
    cmd_new.add_argument("filename")
    cmd_new.set_defaults(func=new)

    cmd_now = subpars.add_parser("now", help="Change current file")
    cmd_now.add_argument("path")
    cmd_now.set_defaults(func=now)

    cmd_pwd = subpars.add_parser("pwd", help="Print working directory")
    cmd_pwd.set_defaults(func=pwd)

    cmd_cd = subpars.add_parser("cd", help="Change working directory")
    cmd_cd.add_argument("path")
    cmd_cd.set_defaults(func=cd)

    cmd_clear = subpars.add_parser("clear", help="Clear console")
    cmd_clear.set_defaults(func=clear)

    cmd_run = subpars.add_parser("run", help="run current code")
    cmd_run.set_defaults(func=run)

    cmd_clean = subpars.add_parser("clean", help="clean temp files")
    cmd_clean.set_defaults(func=clean)

    cmd_help = subpars.add_parser("help", help="Help")
    cmd_help.set_defaults(func=gethelp)

    cmd_exit = subpars.add_parser("exit", help="Exit ecr")
    cmd_exit.set_defaults(func=shutdown)

    return parser


def callSysCommand(cmd):
    if man == None or man.defauleShell == None:
        return os.system(cmd)
    else:
        return os.system(" ".join([man.defauleShell, f'"{cmd}"']))


def doSyscall(cmd, message):
    console.info(message, end=" ")
    console.write(cmd)
    retCode = callSysCommand(cmd)
    console.info(f"System command exited:", end=" ")
    if retCode == 0:
        console.write(retCode)
    else:
        console.error(retCode)


def main():  # pragma: no cover
    global man, cwd, itParser

    if len(sys.argv) > 1:
        os.chdir(sys.argv[-1])

    itParser = getITParser()
    cwd = os.getcwd()

    printHead()
    if manager.hasInitialized(cwd):
        loadMan()

    while True:
        if man != None and man.currentFile != None:
            console.write(man.currentFile, end="")
        oricmd = str(console.read("> "))
        cargs = oricmd.split()
        if len(cargs) == 0:
            continue
        if cargs[0].startswith(">"):
            doSyscall(oricmd[1:], "Call system command:")
        else:
            try:
                cmd = itParser.parse_args(cargs)
            except BasicError as e:  # when parse failed, parser will call exit()
                if cargs[0] in man.importedCommand:
                    doSyscall(
                        man.importedCommand[cargs[0]], "Imported command:")
                else:
                    console.warning("We can't recognize this command:")
                    console.write(e)
                    if console.confirm("Do you mean a system command?", [cli.SwitchState.Yes, cli.SwitchState.No]) == cli.SwitchState.Yes:
                        doSyscall(oricmd, "Call system command:")
            else:
                cmd.func(cmd)


if __name__ == "__main__":  # pragma: no cover
    main()
