import argparse
import sys
import io
import os
from colorama import Fore, Back, Style

try:  # for run with module
    from .core import manager
except:
    try:  # for run with only __main__.py
        from core import manager
    except:
        pass


cwd = None

man: manager.WorkManager = None

itParser = None


def printHead():
    print(f"{Fore.GREEN if manager.hasInitialized(cwd) else Style.RESET_ALL}OI{Style.RESET_ALL}",
          cwd, Style.RESET_ALL)


def assertInited()->bool:
    if man == None:
        print("Not have any ecr directory")
        return False
    return True


def init(args):
    global man
    manager.initialize(cwd)
    man = manager.load(cwd)
    printHead()


def now(args):
    if not assertInited():
        return
    man.currentFile = args.path


def run(args):
    if not assertInited():
        return
    if man.currentFile == None:
        print("Please set current file first")
        return
    man.execute()


def shutdown(args):
    exit(0)


def pwd(args):
    print(cwd)


def cd(args):
    global man, cwd
    if not os.path.exists(args.path):
        print("No this directory")
    os.chdir(args.path)
    cwd = os.getcwd()
    printHead()
    if manager.hasInitialized(cwd):
        man = manager.load(cwd)


def gethelp(args):
    itParser.print_help()


def getITParser():
    parser = argparse.ArgumentParser(
        prog="", description="Code Runner", add_help=False,)

    subpars = parser.add_subparsers()

    cmd_init = subpars.add_parser("init", help="Initialize ecr")
    cmd_init.set_defaults(func=init)

    cmd_now = subpars.add_parser("now", help="Change current file")
    cmd_now.add_argument("path")
    cmd_now.set_defaults(func=now)

    cmd_pwd = subpars.add_parser("pwd", help="Print working directory")
    cmd_pwd.set_defaults(func=pwd)

    cmd_cd = subpars.add_parser("cd", help="Change working directory")
    cmd_cd.add_argument("path")
    cmd_cd.set_defaults(func=cd)

    cmd_run = subpars.add_parser("run", help="run current code")
    cmd_run.set_defaults(func=run)

    cmd_help = subpars.add_parser("help", help="Help")
    cmd_help.set_defaults(func=gethelp)

    cmd_exit = subpars.add_parser("exit", help="Exit ecr")
    cmd_exit.set_defaults(func=shutdown)

    return parser


def main():  # pragma: no cover
    global man, cwd, itParser

    if len(sys.argv) > 1:
        os.chdir(sys.argv[-1])

    itParser = getITParser()
    cwd = os.getcwd()

    printHead()
    if manager.hasInitialized(cwd):
        man = manager.load(cwd)

    while True:
        if man.currentFile != None:
            print(man.currentFile, end="")
        cargs = str(input("> ")).split()
        try:
            cmd = itParser.parse_args(cargs)
        except SystemExit:  # when parse failed, parser will call exit()
            pass
        else:
            cmd.func(cmd)


if __name__ == "__main__":  # pragma: no cover
    main()
